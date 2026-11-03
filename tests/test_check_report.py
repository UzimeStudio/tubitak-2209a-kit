"""check_report için testler.

check_report `bibkit` modülünü import eder (başka ajan yazıyor). Bu testler bibkit
henüz yoksa `sys.modules` içine sahte bir bibkit yerleştirir (monkeypatch). Ayrıca mock
değer dosyasını `config.PATHS['mock_data']` üzerinden geçici dosyaya yönlendirir ve kurum
atıf eşlemesini `project.json` yerine doğrudan fonksiyonla sınar.

Ortak fikstür `tests/conftest.py` `tmp_kit` başka ajana aittir; burada yerel fikstür kullanılır.
"""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import check_report
import config
import docxkit


# --------------------------------------------------------------------------- sahte bibkit
def _fake_bibkit():
    mod = types.ModuleType("bibkit")
    refs = [
        {"id": "demir2019", "authors": ["Demir, A."], "year": 2019, "doi": "10.1000/demir",
         "status": "VERIFIED", "cite_as": None},
        {"id": "kaya2021", "authors": ["Kaya, B.", "Yıldız, C."], "year": 2021, "doi": None,
         "status": "PARTIAL", "cite_as": None},
    ]

    def load():
        return refs

    def cite_key(r):
        name = r.get("cite_as") or r["authors"][0].split(",")[0]
        return name, str(r["year"])

    def format_entry(r):
        authors = ", ".join(r["authors"])
        line = f"{authors} {r['year']}. “Örnek başlık”, Örnek Dergisi."
        if r.get("doi"):
            line += f" https://doi.org/{r['doi']}"
        return line

    def sort_key(r):
        return (r["authors"][0].casefold(), str(r["year"]))

    mod.load, mod.cite_key, mod.format_entry, mod.sort_key = load, cite_key, format_entry, sort_key
    mod.USABLE = {"VERIFIED", "PARTIAL", "PUBLISHER_PAGE"}
    mod.STATUSES = {"VERIFIED", "PARTIAL", "PUBLISHER_PAGE", "CONFLICT", "NOT_FOUND", "UNVERIFIED"}
    return mod


@pytest.fixture
def fake_bibkit(monkeypatch):
    mod = _fake_bibkit()
    monkeypatch.setitem(sys.modules, "bibkit", mod)
    return mod


# --------------------------------------------------------------------------- belge kurma
def _doc_with(paras: list[tuple[str, str]], captions: list[tuple[str, int]] | None = None,
              refs: list[str] | None = None) -> object:
    """paras: (stil, metin) çiftleri; refs: Kaynaklar başlığı altına KL Reference satırları."""
    from docx import Document

    doc = Document()
    docxkit.ensure_styles(doc)
    for cap_kind, n in captions or []:
        p = doc.add_paragraph()
        p.style = doc.styles["KL Caption"]
        p.add_run(f"{cap_kind} {n}. Örnek caption")
    for style, text in paras:
        p = doc.add_paragraph()
        p.style = doc.styles[style]
        p.add_run(text)
    if refs is not None:
        h = doc.add_paragraph()
        h.style = doc.styles["Heading 2"]
        h.add_run("Kaynaklar")
        for e in refs:
            p = doc.add_paragraph()
            p.style = doc.styles["KL Reference"]
            p.add_run(e)
    return doc


def test_fold_law_suffix():
    # "Kanunun"/"Kanunu" → "kanun" tabanına indirgenir
    assert check_report.fold("6698 sayılı Kanunun") == check_report.fold("6698 sayılı Kanun")


def test_generic_law_citation_pattern():
    text = "Konu 6698 sayılı Kanun (2016) ile düzenlenmiştir."
    cited = check_report.citations(text)
    assert ("6698 sayili kanun", "2016") in cited


def test_institution_alias_mapping(monkeypatch):
    # institution_aliases() üretimini sına: takma ad → künyenin İLK sözcüğü (fold'lu)
    monkeypatch.setattr(
        config,
        "project",
        lambda: {"checks": {"institution_aliases": {"TÜİK": "Türkiye İstatistik Kurumu"}}},
    )
    aliases = check_report.institution_aliases()
    assert aliases == {check_report.fold("TÜİK"): check_report.fold("Türkiye")}
    # citations() bu eşlemeyle 'TÜİK' atfını künyenin ilk sözcüğüne çevirir
    text = "Bu konu (TÜİK, 2020) tarafından ele alınmıştır."
    cited = check_report.citations(text, aliases)
    assert ("turkiye", "2020") in cited


def test_clean_report_no_problems(fake_bibkit, monkeypatch, tmp_path):
    # mock_data boş bir dosyaya yönlendirilir
    mock = tmp_path / "mock.json"
    mock.write_text(json.dumps({"values": []}), encoding="utf-8")
    monkeypatch.setitem(config.PATHS, "mock_data", mock)
    # project.json olmadan kurum eşlemesi boş döner (ConfigError yakalanır)
    monkeypatch.setattr(config, "project", lambda: (_ for _ in ()).throw(config.ConfigError("yok")))

    doc = _doc_with(
        paras=[
            ("KL Body", "Giriş metni (Demir, 2019) ve ayrıca (Kaya ve Yıldız, 2021) ele alınmıştır."),
            ("KL Body", "Şekil 1 ve Tablo 1 örnektir."),
        ],
        captions=[("Şekil", 1), ("Tablo", 1)],
        refs=[
            "Demir, A. 2019. “Örnek başlık”, Örnek Dergisi. https://doi.org/10.1000/demir",
            "Kaya, B., Yıldız, C. 2021. “Örnek başlık”, Örnek Dergisi.",
        ],
    )
    out = tmp_path / "clean.docx"
    doc.save(str(out))
    rep = check_report.check(out)
    assert rep["problems"] == [], rep["problems"]
    assert rep["mock_warnings"] == []


def test_broken_report_has_problems(fake_bibkit, monkeypatch, tmp_path):
    mock = tmp_path / "mock.json"
    mock.write_text(json.dumps({"values": []}), encoding="utf-8")
    monkeypatch.setitem(config.PATHS, "mock_data", mock)
    monkeypatch.setattr(config, "project", lambda: (_ for _ in ()).throw(config.ConfigError("yok")))

    doc = _doc_with(
        paras=[
            # Tablo 2 atfı var ama caption yok; placeholder kalmış; Şekil 1 caption'ına atıf yok.
            ("KL Body", "Metinde Tablo 2 atfı var ama caption'ı yok. [DOĞRULANMADI]"),
        ],
        captions=[("Şekil", 1)],  # Şekil 1 caption var ama metinde atıf yok
        refs=[
            "Zorlu, X. 2022. “Örnek”, Örnek Dergisi.",  # kaynakçada var, metinde atıf yok
        ],
    )
    out = tmp_path / "broken.docx"
    doc.save(str(out))
    rep = check_report.check(out)
    assert rep["problems"], "bozuk belgede sorun bekleniyordu"
    assert any("[DOĞRULANMADI" in p or "DOĞRULANMADI" in p for p in rep["problems"])


def test_mock_warning_detected(fake_bibkit, monkeypatch, tmp_path):
    mock = tmp_path / "mock.json"
    mock.write_text(
        json.dumps({"values": [{"field": "bütçe", "value": "99.999 TL", "location": "Giriş"}]}),
        encoding="utf-8",
    )
    monkeypatch.setitem(config.PATHS, "mock_data", mock)
    monkeypatch.setattr(config, "project", lambda: (_ for _ in ()).throw(config.ConfigError("yok")))

    doc = _doc_with(paras=[("KL Body", "Bütçe 99.999 TL olarak öngörülmüştür.")])
    out = tmp_path / "withmock.docx"
    doc.save(str(out))
    rep = check_report.check(out)
    assert any("99.999 TL" in w for w in rep["mock_warnings"])
