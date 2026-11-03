"""md2docx için testler: Markdown → DOCX dönüşümü, başlık/tablo/kaynakça.

md2docx `[[KAYNAKCA]]` için `bibkit` modülünü kullanır; bibkit yoksa bu kısım atlanır.
Test, sahte bir bibkit'i `sys.modules`'a yerleştirerek kaynakça üretimini sınar.

Ortak fikstür `tests/conftest.py` `tmp_kit` başka ajana aittir; burada yerel fikstür kullanılır.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest
from docx import Document

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import md2docx


@pytest.fixture
def fake_bibkit(monkeypatch):
    mod = types.ModuleType("bibkit")
    refs = [{"id": "demir2019", "authors": ["Demir, A."], "year": 2019, "cite_as": None}]

    mod.load = lambda: refs
    mod.cite_key = lambda r: (r["authors"][0].split(",")[0], str(r["year"]))
    mod.format_entry = lambda r: f"{', '.join(r['authors'])} {r['year']}. “Örnek”, Örnek Dergisi."
    mod.sort_key = lambda r: (r["authors"][0].casefold(), str(r["year"]))
    monkeypatch.setitem(sys.modules, "bibkit", mod)
    return mod


def _texts(path: Path) -> list[str]:
    return [p.text for p in Document(str(path)).paragraphs]


def test_parse_front():
    lines = ["---", "title: Örnek", "meta: Satır 1", "meta: Satır 2", "---", "# Başlık"]
    meta, body = md2docx.parse_front(lines)
    assert meta["title"] == "Örnek"
    assert meta["meta"] == ["Satır 1", "Satır 2"]
    assert body == ["# Başlık"]


def test_headings_and_body(tmp_path):
    md = tmp_path / "doc.md"
    md.write_text("# Giriş\n\nBu bir örnek paragraftır.\n\n## Alt başlık\n", encoding="utf-8")
    out = tmp_path / "doc.docx"
    md2docx.build(md, out)
    texts = _texts(out)
    assert "Giriş" in texts
    assert "Alt başlık" in texts
    assert "Bu bir örnek paragraftır." in texts


def test_table_and_caption(tmp_path):
    md = tmp_path / "t.md"
    md.write_text(
        "Tablo: Örnek tablo\n\n| A | B |\n| :- | :- |\n| 1 | 2 |\n",
        encoding="utf-8",
    )
    out = tmp_path / "t.docx"
    md2docx.build(md, out)
    doc = Document(str(out))
    assert len(doc.tables) == 1
    assert doc.tables[0].rows[0].cells[0].text == "A"
    # Caption, SEQ alanıyla "Tablo " ön ekiyle üretilir
    joined = "\n".join(p.text for p in doc.paragraphs)
    assert "Tablo" in joined and "Örnek tablo" in joined


def test_bibliography_with_fake_bibkit(tmp_path, fake_bibkit):
    md = tmp_path / "b.md"
    md.write_text(
        "# Giriş\n\nBir çalışma örnektir (Demir, 2019).\n\n# Kaynaklar\n\n[[KAYNAKCA]]\n",
        encoding="utf-8",
    )
    out = tmp_path / "b.docx"
    md2docx.build(md, out)
    joined = "\n".join(_texts(out))
    assert "Demir, A. 2019" in joined


def test_bibliography_skipped_without_bibkit(tmp_path, monkeypatch):
    # bibkit modülü yoksa [[KAYNAKCA]] atlanır, araç yine çalışır
    monkeypatch.setitem(sys.modules, "bibkit", None)
    md = tmp_path / "nb.md"
    md.write_text("# Giriş\n\nMetin (Demir, 2019).\n\n[[KAYNAKCA]]\n", encoding="utf-8")
    out = tmp_path / "nb.docx"
    md2docx.build(md, out)  # hata atmamalı
    assert out.exists()
