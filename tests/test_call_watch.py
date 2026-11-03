"""call_watch.py testleri. Ağ yerine sahte indirme fonksiyonu kullanır."""

from __future__ import annotations

import hashlib
import json

import config


def _sha16(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16].upper()


SAME = b"ayni-icerik"


def _set_sources(tmp_kit):
    """rules.sources'u kurgusal test kaynaklarıyla değiştirir."""
    r = json.loads((tmp_kit.paths["rules_dir"] / "2209a-2026.json").read_text(encoding="utf-8"))
    r["sources"] = [
        {"id": "T_AYNI", "url": "https://tubitak.gov.tr/a.pdf", "sha256_16": _sha16(SAME)},
        {"id": "T_DEGISTI", "url": "https://tubitak.gov.tr/b.pdf", "sha256_16": "0000000000000000"},
        {"id": "T_YENI", "url": "https://tubitak.gov.tr/c.pdf", "sha256_16": None},
        {"id": "T_DIS", "url": "https://example.com/d.pdf", "sha256_16": None},
    ]
    (tmp_kit.paths["rules_dir"] / "2209a-2026.json").write_text(
        json.dumps(r, ensure_ascii=False), encoding="utf-8"
    )
    config.rules.cache_clear()


def test_status_classification(tmp_kit):
    import call_watch as cw
    _set_sources(tmp_kit)

    def fake_fetch(url: str) -> bytes:
        if url.endswith("a.pdf"):
            return SAME
        if url.endswith("b.pdf"):
            return b"farkli-icerik"
        if url.endswith("c.pdf"):
            return b"yeni-icerik"
        raise AssertionError(f"İzinsiz alan indirilmemeli: {url}")

    rep = cw.watch(fetch=fake_fetch)
    by_id = {r["id"]: r for r in rep["results"]}
    assert by_id["T_AYNI"]["status"] == "AYNI"
    assert by_id["T_DEGISTI"]["status"] == "DEĞİŞTİ"
    assert by_id["T_YENI"]["status"] == "YENİ"
    assert by_id["T_DIS"]["status"] == "ATLANDI"  # tubitak.gov.tr dışı atlanır
    assert rep["changed_count"] == 1


def test_unreachable_recorded(tmp_kit):
    import call_watch as cw
    _set_sources(tmp_kit)

    def failing_fetch(url: str) -> bytes:
        raise TimeoutError("ağ yok")

    rep = cw.watch(fetch=failing_fetch)
    by_id = {r["id"]: r for r in rep["results"]}
    assert by_id["T_AYNI"]["status"] == "ERİŞİLEMEDİ"
    assert by_id["T_DIS"]["status"] == "ATLANDI"


def test_rules_file_not_modified(tmp_kit):
    import call_watch as cw
    _set_sources(tmp_kit)
    rules_path = tmp_kit.paths["rules_dir"] / "2209a-2026.json"
    before = rules_path.read_text(encoding="utf-8")
    cw.watch(fetch=lambda url: b"degisik")
    assert rules_path.read_text(encoding="utf-8") == before


def test_allowed_domain():
    import call_watch as cw
    assert cw.allowed("https://tubitak.gov.tr/x.pdf")
    assert cw.allowed("https://www.tubitak.gov.tr/x.pdf")
    assert not cw.allowed("https://evil-tubitak.gov.tr.attacker.com/x")
    assert not cw.allowed("https://example.com/x.pdf")


def test_cache_written(tmp_kit):
    import call_watch as cw
    _set_sources(tmp_kit)
    cw.watch(fetch=lambda url: SAME if url.endswith("a.pdf") else b"x")
    cached = tmp_kit.paths["cache"] / "tubitak" / "a.pdf"
    assert cached.exists() and cached.read_bytes() == SAME
