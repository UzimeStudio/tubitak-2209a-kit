"""docxkit için testler: şablonu bozmadan doldurma, SECTIONS/is_label API'si, SectionWriter.

Ortak fikstür `tests/conftest.py` içindeki `tmp_kit` başka bir ajana aittir; bu dosya
ona yazmaz. Burada gereken yerel fikstürler (gerçek resmî şablona yönlendirme) kendi
içinde tanımlanır; conftest varsa onu ezmeden çalışır.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from docx import Document

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import config
import docxkit

REAL_TEMPLATE = Path(config.PATHS["report_template"])
SKIP_NO_TEMPLATE = pytest.mark.skipif(
    not REAL_TEMPLATE.exists(), reason="resmî şablon (project/official-report-template.docx) yok"
)


def test_is_label_basic():
    assert docxkit.is_label("Sonuç: ", "Sonuç")
    assert docxkit.is_label("Sonuç", "Sonuç")
    # "Sonuç Raporu Formatı:" satırı "Sonuç" etiketiyle karışmamalı
    assert not docxkit.is_label("Sonuç Raporu Formatı:", "Sonuç")
    # Uzun etiket (>15 karakter) ön ek eşleşmesiyle kabul edilir
    assert docxkit.is_label("Proje ile ilgili harcama kalemleri hakkında", "Proje ile ilgili harcama kalemleri")


def test_tr_upper():
    assert docxkit.tr_upper("ileri ışık") == "İLERİ IŞIK"


def test_sections_keys_and_labels():
    assert set(docxkit.SECTIONS) == {"intro", "work", "result", "outputs", "expenses"}
    assert docxkit.SECTIONS["result"] == "Sonuç"


def test_template_path_reads_paths_at_call_time(monkeypatch, tmp_path):
    fake = tmp_path / "fake-template.docx"
    monkeypatch.setitem(config.PATHS, "report_template", fake)
    assert docxkit.template_path() == fake


@SKIP_NO_TEMPLATE
def test_open_template_and_fill(tmp_path):
    doc = docxkit.open_template()
    docxkit.fill_cover(doc, "örnek başlık", "Ada Yürütücü", "Danışman Hoca")
    docxkit.fill_general_info(
        doc,
        {"subject": "konu", "lead": "Ada Yürütücü", "advisor": "Danışman Hoca", "dates": "2026"},
    )
    docxkit.fill_date(doc, "01.01.2026")
    out = tmp_path / "filled.docx"
    doc.save(str(out))

    reopened = Document(str(out))
    full = "\n".join(p.text for p in reopened.paragraphs)
    # Kapaktaki başlık Türkçe büyük harfle yazılır
    body_xml = reopened.element.body.xml
    assert "ÖRNEK BAŞLIĞI" not in full  # placeholder metni gitmemeli diye değil; aşağıdaki asıl kontrol
    assert "ÖRNEK BAŞLIK" in body_xml
    assert "Ada Yürütücü" in body_xml
    assert "Danışman Hoca" in body_xml
    # Genel bilgiler tablosu dolu
    assert "konu" in reopened.tables[0].rows[0].cells[1].text


@SKIP_NO_TEMPLATE
def test_section_writer_adds_content(tmp_path):
    docxkit.SectionWriter.counters = {"Şekil": 0, "Tablo": 0}
    doc = docxkit.open_template()
    w = docxkit.SectionWriter.at_section(doc, "intro")
    w.text("Giriş metni örnektir.")
    w.heading("Alt başlık")
    out = tmp_path / "sw.docx"
    doc.save(str(out))
    reopened = Document(str(out))
    texts = [p.text for p in reopened.paragraphs]
    assert "Giriş metni örnektir." in texts
    assert "Alt başlık" in texts


@SKIP_NO_TEMPLATE
def test_section_anchor_unknown_key_raises():
    doc = docxkit.open_template()
    with pytest.raises(KeyError):
        docxkit.section_anchor(doc, "yok")


@SKIP_NO_TEMPLATE
def test_signature_table_found():
    doc = docxkit.open_template()
    tbl = docxkit.signature_table(doc)
    assert "İMZA" in tbl.rows[0].cells[0].text
