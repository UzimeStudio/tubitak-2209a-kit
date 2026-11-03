"""Regresyon testleri: check_application / check_consistency / check_report / md2docx
araçlarında düzeltilen 9 kusur için birer koruma testi.

Her test, ilgili kusur geri gelirse kırılır. `tmp_kit` fikstürü tests/conftest.py'den
gelir (gerçek repoya dokunmadan geçici KİT kökü kurar). Şablon yapısı (madde 7) gerçek
templates/proposal.md ve templates/tybs-application.md ile sınanır.
"""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import config

REPO_ROOT = Path(__file__).resolve().parents[1]


# --------------------------------------------------------------------- yardımcılar
def _set_project(tmp_kit, **overrides):
    p = json.loads(tmp_kit.paths["project_config"].read_text(encoding="utf-8"))
    p.pop("_note", None)
    p["project"]["title"] = "ÖRNEK Başlık"
    p["project"]["keywords"] = ["anahtar1", "anahtar2"]
    p["team"]["lead"]["name"] = "Ada Yürütücü"
    p["team"]["advisor"]["name"] = "Danışman Hoca"
    p["timeline"]["duration_months"] = 9
    p["budget"]["total_tl"] = 10000
    p["budget"]["items"] = {"Makine Teçhizat": 6000, "Hizmet Alımı": 4000, "Sarf Malzemesi": 0, "Ulaşım": 0}
    for dotted, value in overrides.items():
        cur = p
        parts = dotted.split(".")
        for part in parts[:-1]:
            cur = cur.setdefault(part, {})
        cur[parts[-1]] = value
    tmp_kit.paths["project_config"].write_text(json.dumps(p, ensure_ascii=False), encoding="utf-8")
    config.project.cache_clear()


def _fake_bibkit():
    mod = types.ModuleType("bibkit")

    def load():
        return []

    mod.load = load
    mod.cite_key = lambda r: (r["authors"][0].split(",")[0], str(r["year"]))
    mod.format_entry = lambda r: ", ".join(r["authors"])
    mod.sort_key = lambda r: (r["authors"][0].casefold(), str(r["year"]))
    mod.USABLE = {"VERIFIED", "PARTIAL", "PUBLISHER_PAGE"}
    return mod


# =========================================================== 1) BOM'lu UTF-8 okuma
def test_bom_utf8_heading_not_missed(tmp_path):
    """BOM'lu dosyada read_md BOM'u yutar; ilk başlık (`## Başlık`) kaçmaz."""
    import check_application as ca

    f = tmp_path / "bom.md"
    f.write_bytes("\ufeff## Başlık\n\nİçerik satırı.\n\n## Özet\n\nİkinci bölüm.\n".encode())
    secs = ca.sections(ca.read_md(f))
    assert "Başlık" in secs, secs.keys()
    assert ca.find(secs, "Özet") is not None


def test_read_md_strips_bom_and_crlf(tmp_path):
    import check_application as ca

    f = tmp_path / "bom.md"
    f.write_bytes("\ufeff## X\r\nsatır\r\n".encode())
    text = ca.read_md(f)
    assert not text.startswith("\ufeff")
    assert "\r" not in text
    assert text.startswith("## X")


# ======================================================= 2) CRLF plain() çıktısında
def test_plain_output_has_no_cr(tmp_path):
    """read_md CRLF'i LF'e çevirdiği için plain() çıktısında `\\r` kalmaz."""
    import check_application as ca

    f = tmp_path / "crlf.md"
    f.write_bytes("## 1.1 Önem\r\nBir satır\r\nİkinci satır\r\n".encode())
    md = ca.read_md(f)
    secs = ca.sections(md)
    sec = ca.find(secs, "1.1")
    assert sec is not None
    assert "\r" not in ca.plain(sec[1])


# ============================================= 3) Türkçe iyelik/hal eki (check_report)
def test_turkish_possessive_suffix_citation_matches():
    import check_report as cr

    assert cr.fold("Yılmaz'ın") == cr.fold("Yılmaz")
    assert cr.fold("Cohen'e") == cr.fold("Cohen")
    assert cr.fold("Wilson'ın") == cr.fold("Wilson")
    cited = cr.citations("Bu yaklaşım Yılmaz'ın (2020) çalışmasına dayanır.")
    assert (cr.fold("Yılmaz"), "2020") in cited


def test_apostrophe_suffix_in_check_application(tmp_kit):
    """check_application atıf regex'i de kesme işareti ekini atmalı (metin↔kaynakça)."""
    import check_application as ca

    _set_project(tmp_kit)
    body = "\n".join(
        [
            "## Özet",
            "x " * 30,
            "## 1.1 Önem",
            "Yılmaz'ın (2020) çalışması temel alınır. " + "x" * 360,
            "## 1.2 Amaç",
            "x" * 360,
            "## 2. Yöntem",
            "x" * 360,
            "## 3.1 Çalışma Takvimi",
            "| Proje Süresi (Ay) | Faaliyetler | Kim | Katkı |",
            "| --- | --- | --- | --- |",
            "| 1-9 | İP1 | Ekip | Ölçüt — %100 |",
            "## 4. Yaygın Etki",
            "Kurgusal metin.",
            "## Kaynakça",
            "1. Yılmaz, A. 2020. “Başlık”, Dergi, 1 (1), 1-10.",
        ]
    )
    path = tmp_kit.paths["report_tybs"] / "tybs.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    rep = ca.check(path, tybs=True)
    # 'Yılmaz'ın' atfı 'Yılmaz, 2020' künyesiyle eşleşmeli: eksik-atıf sorunu çıkmamalı.
    assert not any("Yılmaz" in p and "kaynakçada yok" in p.lower() for p in rep["problems"]), rep["problems"]
    assert not any("metinde atıf yok" in p for p in rep["problems"]), rep["problems"]


# ================================================= 4) Marka yasağı sembolle biten ad
def test_brand_ban_catches_symbol_ending_brand(tmp_kit):
    import check_application as ca

    _set_project(tmp_kit)
    r = json.loads((tmp_kit.paths["rules_dir"] / "2209a-2026.json").read_text(encoding="utf-8"))
    r["brand_ban"]["default_brands"] = ["C++", "C#"]
    (tmp_kit.paths["rules_dir"] / "2209a-2026.json").write_text(
        json.dumps(r, ensure_ascii=False), encoding="utf-8"
    )
    config.rules.cache_clear()

    secs = ca.sections("## 2. Yöntem\n\nSistem C++ ile yazıldı.\n")
    problems = ca.tybs_checks("", secs, config.rules())
    assert any("C++" in p for p in problems), problems


def test_brand_ban_no_false_positive_substring(tmp_kit):
    """Lookaround sözcük içi alt dizgiyi yakalamamalı ('Metamorfoz' → 'Meta' değil)."""
    import check_application as ca

    _set_project(tmp_kit)
    r = json.loads((tmp_kit.paths["rules_dir"] / "2209a-2026.json").read_text(encoding="utf-8"))
    r["brand_ban"]["default_brands"] = ["Meta"]
    (tmp_kit.paths["rules_dir"] / "2209a-2026.json").write_text(
        json.dumps(r, ensure_ascii=False), encoding="utf-8"
    )
    config.rules.cache_clear()

    secs = ca.sections("## 2. Yöntem\n\nMetamorfoz süreci incelendi.\n")
    problems = ca.tybs_checks("", secs, config.rules())
    assert not any("Meta" in p for p in problems), problems


# ===================================== 5) PLACEHOLDERS [KAYNAK ↔ [[KAYNAKCA]] yanlış poz.
def test_kaynakca_directive_not_flagged_as_placeholder(tmp_kit):
    import check_consistency as cc

    _set_project(tmp_kit)
    doc = (
        "# Özet\n\nÖRNEK Başlık burada. anahtar1 anahtar2 Ada Yürütücü Danışman Hoca.\n\n"
        "# Kaynakça\n\n[[KAYNAKCA]]\n"
    )
    pr = tmp_kit.paths["report_drafts"] / "proposal.md"
    tb = tmp_kit.paths["report_tybs"] / "tybs.md"
    pr.parent.mkdir(parents=True, exist_ok=True)
    tb.parent.mkdir(parents=True, exist_ok=True)
    pr.write_text(doc, encoding="utf-8")
    tb.write_text(doc, encoding="utf-8")
    p = json.loads(tmp_kit.paths["project_config"].read_text(encoding="utf-8"))
    p["documents"] = {"proposal": "report/drafts/proposal.md", "tybs": "report/tybs/tybs.md"}
    tmp_kit.paths["project_config"].write_text(json.dumps(p, ensure_ascii=False), encoding="utf-8")
    config.project.cache_clear()

    rep = cc.check()
    assert not any("[KAYNAK" in s for s in rep["problems"]), rep["problems"]


def test_real_placeholder_still_flagged(tmp_kit):
    import check_consistency as cc

    _set_project(tmp_kit)
    doc = "# Özet\n\n[KAYNAK eksik] burada.\n"
    pr = tmp_kit.paths["report_drafts"] / "proposal.md"
    tb = tmp_kit.paths["report_tybs"] / "tybs.md"
    pr.parent.mkdir(parents=True, exist_ok=True)
    tb.parent.mkdir(parents=True, exist_ok=True)
    pr.write_text(doc, encoding="utf-8")
    tb.write_text(doc, encoding="utf-8")
    p = json.loads(tmp_kit.paths["project_config"].read_text(encoding="utf-8"))
    p["documents"] = {"proposal": "report/drafts/proposal.md", "tybs": "report/tybs/tybs.md"}
    tmp_kit.paths["project_config"].write_text(json.dumps(p, ensure_ascii=False), encoding="utf-8")
    config.project.cache_clear()

    rep = cc.check()
    assert any("[KAYNAK" in s for s in rep["problems"]), rep["problems"]


# ======================================= 6) _id_defined tablo hücresindeki tanım
def test_id_defined_in_table_cell():
    import check_consistency as cc

    table = "| Hedef | Eşik |\n| --- | --- |\n| AS1: amaç tanımı | %90 |\n| H1 | Bir hipotez açıklaması |\n"
    assert cc._id_defined(table, "AS1")
    assert cc._id_defined(table, "H1")


def test_undefined_id_still_detected():
    import check_consistency as cc

    text = "Metinde H2 sonucu tartışılır ama hiçbir yerde tanımlanmaz.\n"
    assert not cc._id_defined(text, "H2")


# ================================= 7) Şablon başlık düzeyleri + bölüm bulma (gerçek şablonlar)
def test_real_proposal_template_sections_found():
    """proposal.md: `# Özet` (H1), `## 5.1. Çalışma takvimi`, `# Kaynakça` bulunmalı."""
    import check_application as ca

    md = ca.read_md(REPO_ROOT / "templates" / "proposal.md")
    secs = ca.sections(md)
    assert ca.find(secs, "Özet") is not None
    assert ca.find(secs, "1.1") is not None
    assert ca.find(secs, "Çalışma takvimi") is not None
    assert ca.find(secs, "Kaynakça") is not None


def test_real_tybs_template_sections_found():
    import check_application as ca

    md = ca.read_md(REPO_ROOT / "templates" / "tybs-application.md")
    secs = ca.sections(md)
    assert ca.find(secs, "Özet") is not None
    assert ca.find(secs, "3.1") is not None
    assert ca.find(secs, "Kaynakça") is not None


def test_work_plan_found_in_both_templates(tmp_kit, monkeypatch):
    """_work_plan proposal (5.1) ve TYBS (3.1) takvimini de bulmalı."""
    import check_application as ca

    _set_project(tmp_kit)
    monkeypatch.setitem(sys.modules, "bibkit", _fake_bibkit())
    for tpl in ("proposal.md", "tybs-application.md"):
        md = ca.read_md(REPO_ROOT / "templates" / tpl)
        secs = ca.sections(md)
        results, problems, manual = [], [], []
        ca._work_plan(config.rules(), secs, results, problems, manual)
        assert not any("Çalışma Takvimi bulunamadı" in p for p in problems), (tpl, problems)


def test_consistency_max_month_proposal_calendar():
    """check_consistency proposal'ın '5.1' takvimini de okumalı (en büyük ay)."""
    import check_consistency as cc

    md = "# Özet\n\nx\n\n## 5.1. Çalışma takvimi\n| Ay | Faaliyet |\n| --- | --- |\n| 1-9 | İP1 |\n"
    assert cc._max_month(md) == 9


# ===================================== 8) check_report mock değer sözcük sınırı / kısa değer
def test_mock_value_word_boundary(fake_mock_report):
    check_report, make_doc = fake_mock_report
    # '42' kısa (3'ten az) → atlanır; '99.999 TL' sözcük sınırıyla eşleşir.
    mock = {
        "values": [
            {"field": "a", "value": "42", "location": "x"},
            {"field": "b", "value": "99.999 TL", "location": "y"},
        ]
    }
    out = make_doc(["Örneklem 420 kişidir ve bütçe 99.999 TL olarak öngörülmüştür."], mock)
    rep = check_report.check(out)
    joined = " ".join(rep["mock_warnings"])
    assert "99.999 TL" in joined
    assert "'42'" not in joined, rep["mock_warnings"]


# ===================================== 9) check_report --draft bayrağı
def test_draft_flag_demotes_caption_citation(fake_mock_report):
    check_report, make_doc = fake_mock_report
    # Caption var ama metinde atıf yok → tam denetimde SORUN, taslakta UYARI.
    out = make_doc(["Giriş metni."], {"values": []}, captions=[("Tablo", 1)])
    full = check_report.check(out)
    assert any("atıf yok" in p for p in full["problems"]), full["problems"]
    draft = check_report.check(out, draft=True)
    assert not any("atıf yok" in p for p in draft["problems"]), draft["problems"]
    assert any("atıf yok" in w for w in draft["warnings"]), draft["warnings"]


# --------------------------------------------------------------------- fikstür (8–9)
@pytest.fixture
def fake_mock_report(monkeypatch, tmp_path):
    sys.path.insert(0, str(REPO_ROOT / "tools"))
    import check_report
    import docxkit
    from docx import Document

    monkeypatch.setitem(sys.modules, "bibkit", _fake_bibkit())
    monkeypatch.setattr(config, "project", lambda: (_ for _ in ()).throw(config.ConfigError("yok")))

    def make_doc(body_lines, mock, captions=None):
        mock_file = tmp_path / "mock.json"
        mock_file.write_text(json.dumps(mock), encoding="utf-8")
        monkeypatch.setitem(config.PATHS, "mock_data", mock_file)
        doc = Document()
        docxkit.ensure_styles(doc)
        for kind, n in captions or []:
            p = doc.add_paragraph()
            p.style = doc.styles["KL Caption"]
            p.add_run(f"{kind} {n}. Örnek caption")
        for line in body_lines:
            p = doc.add_paragraph()
            p.style = doc.styles["KL Body"]
            p.add_run(line)
        out = tmp_path / "doc.docx"
        doc.save(str(out))
        return out

    return check_report, make_doc


@pytest.mark.parametrize(
    "phrase",
    ["Landis ve Koch'un (1977)", "Landis ve Koch’a (1977)", "Landis vd.'nin (1977)", "Landis'in (1977)"],
)
def test_suffix_on_second_author_or_vd_is_matched(tmp_kit, phrase):
    """Ek ikinci yazarda veya 'vd.' sonrasında olsa da atıf ilk soyadla eşlenir."""
    import check_application

    md = (
        "## Özet\n"
        + ("kelime " * 30)
        + "\n\n## 1.1 Önem\n"
        + f"Bu ölçek {phrase} önerilmiştir. " * 20
        + "\n\n## Kaynakça\n1. Landis, J. R., Koch, G. G. 1977. “Başlık”, Biometrics, 33 (1), 159–174.\n"
    )
    path = tmp_kit.root / "t.md"
    path.write_text(md, encoding="utf-8")
    rep = check_application.check(path, tybs=True)
    assert not any("landis" in p.lower() for p in rep["problems"]), rep["problems"]


def test_multiword_institution_parenthetical_citation(tmp_kit):
    """'(Türkiye İstatistik Kurumu, 2024; Soyad, 2020)' her iki atfı da tanır."""
    import check_application

    md = (
        "## Özet\n"
        + ("kelime " * 30)
        + "\n\n## 1.1 Önem\n"
        + "Oran artmıştır (Türkiye İstatistik Kurumu, 2024; Soyad, 2020). " * 10
        + "\n\n## Kaynakça\n1. Soyad, A. 2020. “Başlık”, Dergi.\n"
        + "2. Türkiye İstatistik Kurumu. 2024. “Bülten”. https://data.tuik.gov.tr, Son erişim tarihi: 1 Ekim 2026.\n"
    )
    path = tmp_kit.root / "t.md"
    path.write_text(md, encoding="utf-8")
    rep = check_application.check(path, tybs=True)
    atif = [p for p in rep["problems"] if "atıf" in p]
    assert not atif, atif
