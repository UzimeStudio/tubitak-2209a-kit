"""pdf_check için testler: A4/boş sayfa/font kontrolleri ve PNG üretimi.

Dış dönüşüm motoruna (Word/LibreOffice) bağlı kalmamak için test PDF'leri `pypdf` ile
bellek içinde üretilir. A4 boyutlu boş bir sayfa; pdf_check 'boş sayfa' sorununu ve
A4 kontrolünü doğrular. Gerçek motor varsa isteğe bağlı bir uçtan uca test eklenir.

Ortak fikstür `tests/conftest.py` `tmp_kit` başka ajana aittir; burada yerel fikstür kullanılır.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import pdf_check

A4_PT = (595.3, 841.9)


def _blank_a4_pdf(path: Path, pages: int = 1, size=A4_PT) -> Path:
    from pypdf import PdfWriter

    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=size[0], height=size[1])
    with path.open("wb") as fh:
        writer.write(fh)
    return path


def test_blank_a4_detected_as_empty(tmp_path):
    pdf = _blank_a4_pdf(tmp_path / "blank.pdf", pages=1)
    rep = pdf_check.check(pdf, headings=[])
    assert rep["page_count"] == 1
    # A4 doğru boyut → A4 sorunu olmamalı; ama boş sayfa sorunu olmalı
    assert not any("A4 değil" in p for p in rep["problems"])
    assert any("boş görünüyor" in p for p in rep["problems"])


def test_wrong_size_flagged(tmp_path):
    # Letter boyutu (612×792 pt) → A4 değil sorunu
    pdf = _blank_a4_pdf(tmp_path / "letter.pdf", pages=1, size=(612.0, 792.0))
    rep = pdf_check.check(pdf, headings=[])
    assert any("A4 değil" in p for p in rep["problems"])


def test_page_pngs_written(tmp_path):
    pdf = _blank_a4_pdf(tmp_path / "doc.pdf", pages=2)
    rep = pdf_check.check(pdf, headings=[])
    assert rep["page_count"] == 2
    outdir = pdf.with_name(pdf.stem + "_pages")
    assert (outdir / "page-01.png").exists()
    assert (outdir / "page-02.png").exists()
    assert len(rep["pages"]) == 2


def test_visual_review_flag(tmp_path):
    pdf = _blank_a4_pdf(tmp_path / "v.pdf", pages=1)
    rep = pdf_check.check(pdf, headings=[])
    assert rep["visual_review_required"] is True


def _soffice_available() -> bool:
    import docx_to_pdf

    return docx_to_pdf._soffice() is not None


@pytest.mark.skipif(not _soffice_available(), reason="LibreOffice yok; uçtan uca dönüşüm testi atlanıyor")
def test_end_to_end_with_libreoffice(tmp_path):
    """Gerçek dönüşüm: Türkçe içerikli DOCX → LibreOffice PDF → pdf_check (CI'da Linux'ta çalışır)."""
    import docx_to_pdf
    from docx import Document

    src = tmp_path / "ornek.docx"
    doc = Document()
    doc.add_heading("Giriş", level=1)
    doc.add_paragraph("Çalışmanın amacı ölçüm doğruluğunu sınamaktır. ĞÜŞİÖÇ ğüşıöç.")
    doc.save(src)
    pdf = tmp_path / "ornek.pdf"
    docx_to_pdf.convert_with_soffice(src, pdf, docx_to_pdf._soffice())
    assert pdf.exists() and pdf.stat().st_size > 0
    rep = pdf_check.check(pdf, headings=[])
    assert rep["page_count"] >= 1
    text = "".join(page.extract_text() or "" for page in __import__("pypdf").PdfReader(str(pdf)).pages)
    assert "Çalışmanın" in text
