"""Düzeltilen hatalar için regresyon testleri.

Her test, kapatılan bir güvenlik/sağlamlık açığını kilitler. Hepsi AĞSIZ ve
yan etkisizdir (geçici klasör / sahte fonksiyon kullanır).
"""

from __future__ import annotations

import json

import config
import pytest

# --- 1) call_watch.py: yönlendirme alan kısıtını atlatamaz ------------------


def test_call_watch_redirect_disalli_alana_reddedilir(tmp_kit, monkeypatch):
    """İzin verilen alandan izin DIŞI alana 3xx yönlendirme reddedilmeli; önbelleğe yazılmamalı."""
    import call_watch as cw

    # rules.sources: izin verilen bir tubitak.gov.tr kaynağı.
    r = json.loads((tmp_kit.paths["rules_dir"] / "2209a-2026.json").read_text(encoding="utf-8"))
    r["sources"] = [{"id": "T_RDR", "url": "https://tubitak.gov.tr/a.pdf", "sha256_16": None}]
    (tmp_kit.paths["rules_dir"] / "2209a-2026.json").write_text(
        json.dumps(r, ensure_ascii=False), encoding="utf-8"
    )
    config.rules.cache_clear()

    # Gerçek download() yolunu kullan; opener'ın redirect_request'ini sahte bir
    # yönlendirmeyle tetikle (ağsız). İzin dışı hedef RedirectBlocked fırlatmalı.
    handler = cw._StrictRedirectHandler()

    class _FakeReq:
        def get_full_url(self):
            return "https://tubitak.gov.tr/a.pdf"

    with pytest.raises(cw.RedirectBlocked):
        handler.redirect_request(
            _FakeReq(), None, 302, "Found", {}, "https://evil.example.com/steal.pdf"
        )

    # Aynı alan içindeki yönlendirme engellenmez (super().redirect_request çağrılır).
    # (Burada yalnız izin kontrolünün geçtiğini doğruluyoruz; gerçek Request kullanırız.)
    import urllib.request

    req = urllib.request.Request("https://tubitak.gov.tr/a.pdf")
    out = handler.redirect_request(req, None, 302, "Found", {}, "https://www.tubitak.gov.tr/b.pdf")
    assert out is not None


def test_call_watch_reddedilen_yonlendirme_onbellege_yazilmaz(tmp_kit):
    """fetch RedirectBlocked fırlatınca durum ERİŞİLEMEDİ olmalı ve dosya önbelleğe yazılmamalı."""
    import call_watch as cw

    r = json.loads((tmp_kit.paths["rules_dir"] / "2209a-2026.json").read_text(encoding="utf-8"))
    r["sources"] = [{"id": "T_RDR", "url": "https://tubitak.gov.tr/a.pdf", "sha256_16": None}]
    (tmp_kit.paths["rules_dir"] / "2209a-2026.json").write_text(
        json.dumps(r, ensure_ascii=False), encoding="utf-8"
    )
    config.rules.cache_clear()

    def blocked_fetch(url: str) -> bytes:
        raise cw.RedirectBlocked("izin dışı alana yönlendirme")

    rep = cw.watch(fetch=blocked_fetch)
    row = rep["results"][0]
    assert row["status"] == "ERİŞİLEMEDİ"
    cached = tmp_kit.paths["cache"] / "tubitak" / "a.pdf"
    assert not cached.exists()


def test_call_watch_download_son_adres_denetlenir():
    """download(), yönlendirme son adresini de allowed() ile denetler (geturl kontrolü)."""
    import call_watch as cw

    class _Resp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def geturl(self):
            return "https://evil.example.com/final.pdf"

        def read(self):  # çağrılmamalı; önce son adres reddedilir
            raise AssertionError("son adres reddedilmeden read çağrıldı")

    class _Opener:
        def open(self, req, timeout=None):
            return _Resp()

    from unittest import mock

    with mock.patch.object(cw, "_opener", lambda: _Opener()), pytest.raises(cw.RedirectBlocked):
        cw.download("https://tubitak.gov.tr/a.pdf")


# --- 2) verify_source.py: yazar tam token eşleşmesi + Türkçe normalizasyon --


def test_verify_author_alt_dizgi_eslesmez():
    """'And' soyadı 'Andrew'e alt dizgi olarak eşleşmemeli (tam token eşleşmesi)."""
    import verify_source as vs

    assert not vs._author_matches("And", ["Andrew"])
    assert vs._author_matches("Andrew", ["Andrew"])
    assert vs._author_matches("Yılmaz", ["Ahmet Yılmaz", "Can Demir"])


def test_verify_norm_turkce_harfler():
    """_norm Türkçe harfleri ASCII karşılığına indirger, boşluğa değil."""
    import verify_source as vs

    assert vs._norm("çalışması") == "calismasi"
    assert vs._norm("İSTANBUL") == "istanbul"
    assert vs._norm("Şişli Güvenç Öz") == "sisli guvenc oz"


def test_verify_author_tam_token_difits(monkeypatch):
    """verify(): yazarı alt dizgi eşleşen sahte kayıt artık kabul edilmemeli."""
    import verify_source as vs

    t = "Örnek başlık uzun yeterli olacak şekilde yazıldı"

    def rec(src, authors):
        return {
            "source": src,
            "title": t,
            "year": 2020,
            "authors": authors,
            "venue": "D",
            "doi": None,
            "url": None,
        }

    # Kayıtlarda 'Andrew' var; sorgu 'And' -> eşleşmemeli, kayıt elenmeli -> NOT_FOUND.
    monkeypatch.setattr(vs, "crossref", lambda doi, title: [rec("crossref", ["Andrew"])])
    monkeypatch.setattr(vs, "openalex", lambda doi, title: [rec("openalex", ["Andrew"])])
    monkeypatch.setattr(vs, "semantic_scholar", lambda doi, title: [])
    monkeypatch.setattr(vs, "doi_resolves", lambda doi: True)
    res = vs.verify(None, t, 2020, "And", use_s2=False)
    assert res["status"] == "NOT_FOUND"


# --- 3) bibkit.py: boş yazar listesi çökmesin -------------------------------


def test_bibkit_bos_yazar_cite_ve_sort_key():
    import bibkit

    r = {"id": "x", "type": "article", "authors": [], "year": 2020, "title": "B", "status": "VERIFIED"}
    # IndexError fırlatmamalı.
    assert bibkit.cite_key(r) == ("", "2020")
    assert isinstance(bibkit.sort_key(r), tuple)
    # cite_as varsa onu kullanır.
    r2 = dict(r, cite_as="TÜİK")
    assert bibkit.cite_key(r2)[0] == "TÜİK"


def test_bibkit_bos_yazar_format_entry_cokmez():
    import bibkit

    r = {
        "id": "x",
        "type": "web",
        "authors": [],
        "cite_as": "TÜİK",
        "year": 2021,
        "title": "Rapor",
        "venue": "Site",
        "url": "https://e.example",
        "status": "VERIFIED",
    }
    out = bibkit.format_entry(r)
    assert "TÜİK" in out


def test_bibkit_list_bos_yazarla_cokmez(tmp_kit):
    """`list` komutu boş yazarlı kayıtta çökmemeli (sort_key/format_entry güvenli)."""
    import bibkit

    tmp_kit.write_references(
        [{"id": "x", "type": "web", "authors": [], "cite_as": "TÜİK", "year": 2021,
          "title": "Rapor", "venue": "Site", "url": "https://e.example", "status": "VERIFIED"}]
    )
    refs = bibkit.load()
    # Sıralama ve biçimleme hata vermemeli.
    out = [bibkit.format_entry(r) for r in sorted(refs, key=bibkit.sort_key)]
    assert out and "TÜİK" in out[0]


def test_bibkit_lint_authors_eksik_der():
    import bibkit

    r = {"id": "x", "type": "article", "authors": [], "year": 2020, "title": "B",
         "venue": "D", "status": "VERIFIED", "doi": "10.1/x"}
    problems = bibkit.lint([r])
    assert any("'authors' eksik" in p for p in problems)


# --- 4) matrix.py: id'siz / bozuk references.json ---------------------------


def test_matrix_references_idsiz_atlanir(tmp_kit):
    import matrix

    tmp_kit.write_references(
        [{"id": "a", "status": "VERIFIED"}, {"status": "VERIFIED"}, {"id": "b", "status": "PARTIAL"}]
    )
    refs = matrix._references()
    assert set(refs.keys()) == {"a", "b"}  # id'siz kayıt atlandı, KeyError yok


def test_matrix_references_bozuk_json_anlasili_hata(tmp_kit):
    import matrix

    tmp_kit.paths["references"].write_text("{bozuk json", encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        matrix._references()
    assert "bozuk JSON" in str(e.value)


def test_matrix_references_dosya_yoksa_bos(tmp_kit):
    import matrix

    tmp_kit.paths["references"].unlink(missing_ok=True)
    assert matrix._references() == {}


# --- 5) config.py: tip güvenli people() + validate_types() ------------------


def test_config_people_bozuk_members_cokmez(tmp_kit):
    cfg = json.loads(tmp_kit.paths["project_config"].read_text(encoding="utf-8"))
    cfg["team"]["lead"]["name"] = "Yürütücü"
    cfg["team"]["members"] = "bir metin"  # liste değil
    tmp_kit.paths["project_config"].write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
    config.project.cache_clear()
    assert config.people() == ["Yürütücü"]  # AttributeError yok


def test_config_people_sozluk_olmayan_uye_atlanir(tmp_kit):
    cfg = json.loads(tmp_kit.paths["project_config"].read_text(encoding="utf-8"))
    cfg["team"]["lead"]["name"] = "Lider"
    cfg["team"]["members"] = [{"name": "Ortak A"}, "düz metin", {"name": "Ortak B"}]
    tmp_kit.paths["project_config"].write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
    config.project.cache_clear()
    assert config.people() == ["Lider", "Ortak A", "Ortak B"]


def test_config_validate_types_ihlalleri_bulur(tmp_kit):
    cfg = json.loads(tmp_kit.paths["project_config"].read_text(encoding="utf-8"))
    cfg["project"]["keywords"] = "a,b"  # liste olmalı
    cfg["team"]["members"] = {}  # liste olmalı
    cfg["budget"]["items"] = []  # sözlük olmalı
    cfg["timeline"]["duration_months"] = "9"  # int/null olmalı
    tmp_kit.paths["project_config"].write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
    config.project.cache_clear()
    problems = config.validate_types()
    joined = " ".join(problems)
    assert "keywords" in joined
    assert "members" in joined
    assert "budget.items" in joined
    assert "duration_months" in joined


def test_config_validate_types_temiz(tmp_kit):
    cfg = json.loads(tmp_kit.paths["project_config"].read_text(encoding="utf-8"))
    cfg["project"]["keywords"] = ["a", "b", "c"]
    cfg["team"]["members"] = [{"name": "X"}]
    cfg["ai_tools"] = []
    cfg["budget"]["items"] = {"Ulaşım": 0}
    cfg["timeline"]["duration_months"] = 12
    tmp_kit.paths["project_config"].write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
    config.project.cache_clear()
    assert config.validate_types() == []


def test_config_validate_types_duration_null_sorunsuz(tmp_kit):
    cfg = json.loads(tmp_kit.paths["project_config"].read_text(encoding="utf-8"))
    cfg["timeline"]["duration_months"] = None
    tmp_kit.paths["project_config"].write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
    config.project.cache_clear()
    assert all("duration_months" not in p for p in config.validate_types())


# --- 6) init_project.py: --set liste/sözlük JSON hatası + kolaylıklar -------


def _run_init(monkeypatch, argv):
    import init_project

    monkeypatch.setattr("sys.argv", ["init_project.py", *argv])
    return init_project.main()


def _fresh_example(tmp_kit):
    # tmp_kit zaten project.json'u örnekten üretti; örnek dosya da temp köke gerekli.
    src = json.loads((_REPO_ROOT / "project.example.json").read_text(encoding="utf-8"))
    tmp_kit.paths["project_example"].parent.mkdir(parents=True, exist_ok=True)
    tmp_kit.paths["project_example"].write_text(json.dumps(src, ensure_ascii=False), encoding="utf-8")
    config.project.cache_clear()


_REPO_ROOT = config.ROOT  # tmp_kit monkeypatch'inden önce: gerçek repo kökü.


def test_init_set_liste_alanina_metin_hata(tmp_kit, monkeypatch, capsys):
    """project.keywords JSON değilse ve virgül yoksa: sessiz metin yazma yok, çıkış 2."""
    _fresh_example(tmp_kit)
    rc = _run_init(monkeypatch, ["--set", "project.keywords=tekkelime"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "liste" in err
    # project.json değişmemeli (yazılmamalı): başlangıç değeri korunur.
    data = json.loads(tmp_kit.paths["project_config"].read_text(encoding="utf-8"))
    assert data["project"]["keywords"] != "tekkelime"


def test_init_set_keywords_virgullu_metin_listeye(tmp_kit, monkeypatch):
    """Kolaylık: 'a, b, c' düz metni keywords listesine çevrilir."""
    _fresh_example(tmp_kit)
    rc = _run_init(monkeypatch, ["--set", "project.keywords=yapay zeka, toprak nemi, sensör"])
    assert rc == 0
    data = json.loads(tmp_kit.paths["project_config"].read_text(encoding="utf-8"))
    assert data["project"]["keywords"] == ["yapay zeka", "toprak nemi", "sensör"]


def test_init_set_keywords_json_liste(tmp_kit, monkeypatch):
    _fresh_example(tmp_kit)
    rc = _run_init(monkeypatch, ["--set", 'project.keywords=["a","b"]'])
    assert rc == 0
    data = json.loads(tmp_kit.paths["project_config"].read_text(encoding="utf-8"))
    assert data["project"]["keywords"] == ["a", "b"]


def test_init_set_json_dosyadan(tmp_kit, monkeypatch):
    """--set-json alanı bir dosyadan okur (PowerShell tırnak sorunu olmadan)."""
    _fresh_example(tmp_kit)
    f = tmp_kit.root / "members.json"
    f.write_text(json.dumps([{"name": "Ortak A"}, {"name": "Ortak B"}]), encoding="utf-8")
    rc = _run_init(monkeypatch, ["--set-json", f"team.members={f}"])
    assert rc == 0
    data = json.loads(tmp_kit.paths["project_config"].read_text(encoding="utf-8"))
    assert data["team"]["members"] == [{"name": "Ortak A"}, {"name": "Ortak B"}]


def test_init_set_json_bozuk_dosya_hata(tmp_kit, monkeypatch, capsys):
    _fresh_example(tmp_kit)
    f = tmp_kit.root / "bad.json"
    f.write_text("{bozuk", encoding="utf-8")
    rc = _run_init(monkeypatch, ["--set-json", f"team.members={f}"])
    assert rc == 2
    assert "JSON" in capsys.readouterr().err


def test_init_set_sozluk_alanina_liste_hata(tmp_kit, monkeypatch, capsys):
    _fresh_example(tmp_kit)
    rc = _run_init(monkeypatch, ["--set", 'budget.items=["a","b"]'])
    assert rc == 2
    assert "sözlük" in capsys.readouterr().err


def test_init_validate_types_uyarilari_basilir(tmp_kit, monkeypatch, capsys):
    """Yazdıktan sonra tip uyarıları (duration_months metin) basılmalı."""
    _fresh_example(tmp_kit)
    # duration_months serbest alan değil; _parse "9x" -> metin kalır, validate_types uyarır.
    rc = _run_init(monkeypatch, ["--set", "timeline.duration_months=9ay"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Tip uyarıları" in out
    assert "duration_months" in out


# --- 7) docx_to_pdf.py: soffice 0 dönüp dosya üretmezse hata ----------------


def test_docx_to_pdf_soffice_dosya_uretmezse_hata(tmp_path, monkeypatch):
    import docx_to_pdf as dp

    docx = tmp_path / "a.docx"
    docx.write_bytes(b"dummy")
    pdf = tmp_path / "a.pdf"

    class _Res:
        returncode = 0
        stderr = ""
        stdout = "Dönüştürüldü ama dosya yok"

    monkeypatch.setattr(dp.subprocess, "run", lambda *a, **k: _Res())
    # produced (a.pdf) oluşturulmaz -> RuntimeError beklenir.
    with pytest.raises(RuntimeError) as e:
        dp.convert_with_soffice(docx, pdf, "soffice")
    assert "başarısız" in str(e.value)


def test_docx_to_pdf_soffice_adaylari_platforma_gore(monkeypatch):
    from pathlib import Path as _P

    import docx_to_pdf as dp

    # PATH'te yok; linux adayı mevcutmuş gibi davran. _soffice adayı dize olarak döndürür.
    expected = dp._SOFFICE_CANDIDATES["linux"][0]  # "/usr/bin/soffice"
    assert expected == "/usr/bin/soffice"
    monkeypatch.setattr(dp.shutil, "which", lambda name: None)
    monkeypatch.setattr(dp.sys, "platform", "linux")
    # exists() yalnız ilk linux adayı için True; karşılaştırma Path kimliğiyle yapılır
    # (Windows'ta str(Path) ters taksim verebildiği için doğrudan Path eşitliği kullanılır).
    want = _P(expected)
    monkeypatch.setattr(dp.Path, "exists", lambda self: self == want)
    assert dp._soffice() == expected


def test_init_merge_writes_nested_fields(tmp_kit, monkeypatch, tmp_path):
    """--merge kısmi nesneyi yaprak alanlara açar; yalnız dosyadaki alanlar değişir."""
    _fresh_example(tmp_kit)
    values = tmp_path / "values.json"
    values.write_text(
        json.dumps(
            {
                "_note": "yok sayılır",
                "project": {"title": "ÖRNEK başlık", "keywords": ["toprak nemi", "sensör", "doğruluk"]},
                "team": {"lead": {"name": "Ayşe Yılmaz"}, "members": [{"name": "Mehmet Demir"}]},
                "budget": {"items": {"Sarf Malzemesi": 9000}},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8-sig",
    )
    assert _run_init(monkeypatch, ["--merge", str(values)]) == 0
    data = json.loads(tmp_kit.paths["project_config"].read_text(encoding="utf-8"))
    assert data["project"]["title"] == "ÖRNEK başlık"
    assert data["project"]["keywords"] == ["toprak nemi", "sensör", "doğruluk"]
    assert data["team"]["lead"]["name"] == "Ayşe Yılmaz"
    assert data["team"]["members"] == [{"name": "Mehmet Demir"}]
    assert data["budget"]["items"]["Sarf Malzemesi"] == 9000
    assert data["budget"]["items"]["Ulaşım"] == 0  # dokunulmayan kalem korunur
    assert "project" not in data["project"]


def test_init_merge_rejects_non_object(tmp_kit, monkeypatch, tmp_path):
    _fresh_example(tmp_kit)
    values = tmp_path / "values.json"
    values.write_text("[1, 2]", encoding="utf-8")
    assert _run_init(monkeypatch, ["--merge", str(values)]) == 2
