"""import_draft: biçim dönüşümü, özgün kopya, bölüm eşleme ve üzerine yazma koruması."""

from __future__ import annotations

import config
import import_draft
import pytest
from docx import Document

TYBS_LIKE = """\ufeff# Taslak

## Özet
Kısa özet metni.

## 1.1 Konunun Önemi
Önem metni.

## 1.2 Amaç ve Hedefler
Amaç.

## 2. Yöntem
Yöntem.

## 5.1 Çalışma takvimi
| Ay | İş |
| --- | --- |

## Kaynaklar
1. Soyad, A. 2020. "Başlık", Dergi.
"""


def _sections(rep):
    return {m["section"]: m for m in rep["sections"] if "section" in m}


def test_markdown_import_maps_by_number_and_keyword(tmp_kit, tmp_path):
    src = tmp_path / "eski.md"
    src.write_text(TYBS_LIKE.replace("\n", "\r\n"), encoding="utf-8")
    rep = import_draft.run(src, config.PATHS["report_drafts"] / "imported.md", force=False)
    s = _sections(rep)
    assert s["Özet"]["heading"] == "Özet"
    assert s["1.1"]["matched_by"] == "numara + anahtar sözcük" and not s["1.1"]["manual_check"]
    # Takvim farklı numarada; anahtar sözcükle bulunur ve elle kontrol işaretlenir.
    assert s["3.1"]["heading"].startswith("5.1") and s["3.1"]["manual_check"]
    assert s["Kaynakça"]["heading"] == "Kaynaklar"
    assert "3.2" in rep["missing"]
    out = (config.PATHS["report_drafts"] / "imported.md").read_text(encoding="utf-8")
    assert "\r" not in out and not out.startswith("\ufeff")
    assert (config.PATHS["report_drafts"] / "original" / "eski.md").exists()


def test_docx_import_keeps_headings_and_tables(tmp_kit, tmp_path):
    doc = Document()
    doc.add_heading("Özet", level=1)
    doc.add_paragraph("Özet metni.")
    doc.add_heading("2. Yöntem", level=1)
    table = doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text, table.cell(0, 1).text = "Ay", "İş"
    table.cell(1, 0).text, table.cell(1, 1).text = "1-3", "Veri | toplama"
    src = tmp_path / "eski.docx"
    doc.save(src)
    md = import_draft.convert(src)
    assert "# Özet" in md and "# 2. Yöntem" in md
    assert "| Ay | İş |" in md and "Veri / toplama" in md


def test_refuses_overwrite_without_force(tmp_kit, tmp_path):
    src = tmp_path / "eski.md"
    src.write_text(TYBS_LIKE, encoding="utf-8")
    out = config.PATHS["report_drafts"] / "imported.md"
    import_draft.run(src, out, force=False)
    with pytest.raises(config.ConfigError):
        import_draft.run(src, out, force=False)
    import_draft.run(src, out, force=True)


def test_unsupported_format(tmp_kit, tmp_path):
    src = tmp_path / "eski.odt"
    src.write_text("x", encoding="utf-8")
    with pytest.raises(config.ConfigError):
        import_draft.convert(src)
