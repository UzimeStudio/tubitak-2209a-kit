"""verify_source.py testleri: AĞSIZ. Künye servisleri sahte yanıtlarla taklit edilir."""

from __future__ import annotations

import verify_source


def _rec(source, title, year, authors, doi=None):
    return {
        "source": source,
        "title": title,
        "year": year,
        "authors": authors,
        "venue": "Örnek Dergi",
        "doi": doi,
        "url": None,
    }


def _patch_providers(monkeypatch, crossref=None, openalex=None, s2=None, resolves=True):
    """Ağ çağrısı yapan tüm fonksiyonları sahte yanıtlarla değiştirir."""
    monkeypatch.setattr(verify_source, "crossref", lambda doi, title: list(crossref or []))
    monkeypatch.setattr(verify_source, "openalex", lambda doi, title: list(openalex or []))
    monkeypatch.setattr(verify_source, "semantic_scholar", lambda doi, title: list(s2 or []))
    monkeypatch.setattr(verify_source, "doi_resolves", lambda doi: resolves)


def test_similarity_altbaslik():
    uzun = "Bir calisma hakkinda detayli bir inceleme ve sonuclar"
    kisa = "Bir calisma hakkinda detayli bir inceleme"
    assert verify_source.similarity(kisa, uzun) >= 0.90


def test_verified_iki_kaynak_uyusur(monkeypatch):
    t = "Örnek başlık uzun yeterli olacak şekilde yazıldı"
    _patch_providers(
        monkeypatch,
        crossref=[_rec("crossref", t, 2020, ["Yılmaz"])],
        openalex=[_rec("openalex", t, 2020, ["Yılmaz"])],
    )
    res = verify_source.verify(None, t, 2020, "Yılmaz", use_s2=False)
    assert res["status"] == "VERIFIED"
    assert set(res["agreeing_sources"]) == {"crossref", "openalex"}


def test_partial_tek_kaynak(monkeypatch):
    t = "Örnek başlık uzun yeterli olacak şekilde yazıldı"
    _patch_providers(monkeypatch, crossref=[_rec("crossref", t, 2020, ["Yılmaz"])])
    res = verify_source.verify(None, t, 2020, "Yılmaz", use_s2=False)
    assert res["status"] == "PARTIAL"


def test_not_found(monkeypatch):
    _patch_providers(monkeypatch)
    res = verify_source.verify(None, "Hiçbir yerde olmayan başlık metni uzun", 2020, None, use_s2=False)
    assert res["status"] == "NOT_FOUND"


def test_conflict_yil_celisir(monkeypatch):
    # DOI sorgusunda kayıt title ile elenmez; yıl çelişkisi CONFLICT olarak raporlanır.
    t = "Örnek başlık uzun yeterli olacak şekilde yazıldı"
    _patch_providers(
        monkeypatch,
        crossref=[_rec("crossref", t, 2010, ["Yılmaz"], doi="10.1/x")],
        openalex=[_rec("openalex", t, 2010, ["Yılmaz"], doi="10.1/x")],
    )
    res = verify_source.verify("10.1/x", t, 2020, "Yılmaz", use_s2=False)
    assert res["status"] == "CONFLICT"
    assert any("yıl" in i for i in res["issues"])


def test_doi_cozumlenmezse_sorun(monkeypatch):
    t = "Örnek başlık uzun yeterli olacak şekilde yazıldı"
    _patch_providers(
        monkeypatch,
        crossref=[_rec("crossref", t, 2020, ["Yılmaz"], doi="10.1/x")],
        openalex=[_rec("openalex", t, 2020, ["Yılmaz"], doi="10.1/x")],
        resolves=False,
    )
    res = verify_source.verify(None, t, 2020, "Yılmaz", use_s2=False)
    assert res["status"] == "CONFLICT"
    assert any("çözümlenmiyor" in i for i in res["issues"])


def test_get_ag_yapmaz(monkeypatch, tmp_kit):
    # _get önbellekte varsa ağ açmaz; sahte önbellek girdisi koyup kontrol ederiz.
    import hashlib
    import json

    url = "https://api.crossref.org/works/test"
    cache = tmp_kit.paths["cache"]
    cache.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode()).hexdigest()[:24]
    (cache / f"{key}.json").write_text(
        json.dumps({"url": url, "body": {"ok": True}}), encoding="utf-8"
    )

    def _patla(*a, **k):
        raise AssertionError("ağ erişimi denendi")

    monkeypatch.setattr(verify_source.urllib.request, "urlopen", _patla)
    assert verify_source._get(url) == {"ok": True}
