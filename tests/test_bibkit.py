"""bibkit.py testleri: biçimleme, sıralama, lint ve boş/eksik dosya davranışı."""

from __future__ import annotations

import json

import bibkit


def _article(**over) -> dict:
    base = {
        "id": "ornek1",
        "type": "article",
        "authors": ["Yılmaz, A."],
        "year": 2020,
        "title": "Örnek bir çalışma başlığı",
        "venue": "Örnek Dergi",
        "volume": "12",
        "issue": "3",
        "pages": "45-60",
        "doi": "10.1234/ornek.2020",
        "status": "VERIFIED",
    }
    base.update(over)
    return base


def test_load_bos_dosya_cokmez(tmp_kit):
    # references.json hiç yoksa boş liste döner, hata fırlatmaz.
    assert bibkit.load() == []


def test_load_gecersiz_liste_degil(tmp_kit):
    tmp_kit.paths["references"].write_text('{"id": "x"}', encoding="utf-8")
    try:
        bibkit.load()
    except SystemExit as e:
        assert "kayıt listesi" in str(e)
    else:
        raise AssertionError("liste olmayan JSON için SystemExit beklenir")


def test_cite_key_ve_sort_key():
    r = _article(authors=["Çeker, B.", "Ada, C."])
    assert bibkit.cite_key(r) == ("Çeker", "2020")
    # Tek yazarlı aynı soyadta çok yazarlıdan önce gelir.
    tek = _article(authors=["Ada, D."])
    cok = _article(authors=["Ada, D.", "Be, E."])
    assert bibkit.sort_key(tek) < bibkit.sort_key(cok)


def test_format_entry_article_doi():
    out = bibkit.format_entry(_article())
    assert "“Örnek bir çalışma başlığı”" in out
    assert "Örnek Dergi, 12 (3)" in out
    assert out.endswith("https://doi.org/10.1234/ornek.2020")


def test_format_entry_book_turu():
    book = {
        "id": "k1",
        "type": "book",
        "authors": ["Demir, E."],
        "year": 2019,
        "title": "Bir kitap başlığı",
        "venue": "Örnek Yayınevi",
        "pages": "10-20",
        "status": "VERIFIED",
    }
    out = bibkit.format_entry(book)
    assert "Örnek Yayınevi" in out
    assert "10–20" in out


def test_format_entry_web_turu():
    web = {
        "id": "w1",
        "type": "web",
        "authors": ["Örnek Kurum"],
        "year": 2021,
        "title": "Bir web sayfası",
        "venue": "Örnek Site",
        "url": "https://ornek.example/sayfa",
        "accessed": "3 Kasım 2026",
        "status": "VERIFIED",
    }
    out = bibkit.format_entry(web)
    assert "https://ornek.example/sayfa" in out
    assert "Son erişim tarihi: 3 Kasım 2026" in out


def test_lint_temiz_kayit():
    assert bibkit.lint([_article()]) == []


def test_lint_sorunlari_bulur():
    kotu = _article(id="kotu", doi="gecersiz-doi", status="NOT_FOUND")
    problems = bibkit.lint([kotu])
    assert any("DOI biçimi geçersiz" in p for p in problems)
    assert any("raporda kullanılamaz" in p for p in problems)


def test_bib_uretir(tmp_kit):
    tmp_kit.write_references([_article()])
    refs = bibkit.load()
    bib = tmp_kit.paths["bib"]
    bib.parent.mkdir(parents=True, exist_ok=True)
    bib.write_text(bibkit.to_bibtex(refs[0]), encoding="utf-8")
    content = bib.read_text(encoding="utf-8")
    assert "@article{ornek1" in content
    assert "journal = {Örnek Dergi}" in content


def test_to_bibtex_book_publisher():
    book = {
        "id": "k2",
        "type": "book",
        "authors": ["Demir, E."],
        "year": 2019,
        "title": "Kitap",
        "venue": "Yayınevi",
        "status": "VERIFIED",
    }
    assert "publisher = {Yayınevi}" in bibkit.to_bibtex(book)


def test_load_gercek_dosyadan(tmp_kit):
    path = tmp_kit.write_references([_article(id="a"), _article(id="b")])
    assert json.loads(path.read_text(encoding="utf-8"))
    assert len(bibkit.load()) == 2
