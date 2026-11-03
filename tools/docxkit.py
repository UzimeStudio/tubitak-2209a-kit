"""Resmî TÜBİTAK 2209-A sonuç raporu şablonunu bozmadan doldurmak için yardımcılar.

Şablon (`PATHS['report_template']`) yapısı:
    1. sayfa  VML text box'ında kapak: PROJE BAŞLIĞI, YÜRÜTÜCÜ, DANIŞMAN
    2. sayfa  GENEL BİLGİLER tablosu (4×2), numaralı bölüm etiketleri,
              harcama paragrafı, imza tablosu ve "Tarih :" satırı

İlkeler:
    - Şablondaki metin, numaralandırma, kenar boşluğu ve tablolar korunur.
    - İçerik ilgili bölüm etiketinin hemen altına eklenir.
    - Şablon etiketlerine görünümü değiştirmeden ana başlık düzeyi (outlineLvl 0) verilir.
    - Alt başlıklar gerçek "Heading 2" stilini kullanır.
    - Şekil/Tablo caption'ları Word SEQ field'ıdır; numara önbelleği yazılır.
    - Tablo caption'ı tablonun üstünde, şekil caption'ı şeklin altındadır.

Şablon yolu `config.PATHS['report_template']`'dan ÇAĞRI ANINDA okunur; böylece testler
`monkeypatch.setitem(config.PATHS, "report_template", ...)` ile geçici şablona yönlenebilir.

API: `SECTIONS`, `is_label`, `open_template`, `fill_cover`, `fill_general_info`,
`fill_date`, `section_anchor`, `signature_table`, `SectionWriter`, `ensure_styles`,
`tr_upper`, `FONT`, `TEXT_WIDTH_CM`.
"""

from __future__ import annotations

import copy
import re
import sys
from pathlib import Path
from typing import ClassVar

import pandas as pd
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from docx.table import Table
from docx.text.paragraph import Paragraph

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import PATHS

FONT = "Arial"
TEXT_WIDTH_CM = 16.0


def template_path() -> Path:
    """Resmî şablon yolu; çağrı anında `config.PATHS`'ten okunur (test için yönlendirilebilir)."""
    return Path(PATHS["report_template"])


# İçeriğin ekleneceği şablon satırları (metnin başlangıcı) — sıra korunur.
# "Proje konusu hakkında kısa bilgi" ayrı bölüm değil, "1. Giriş"in içerik açıklamasıdır;
# giriş metni bu açıklama satırının altına yazılır, açıklama satırı korunur.
SECTIONS = {
    "intro": "Proje konusu hakkında kısa bilgi",
    "work": "Rapor dönemlerinde yapılan çalışmalar",
    "result": "Sonuç",
    "outputs": "Çıktılar",
    "expenses": "Proje ile ilgili harcama kalemleri",
}
# Görünümü değişmeden ana başlık düzeyi (outlineLvl 0) verilen şablon etiketleri.
HEADING_LABELS = [
    "Giriş",
    "Rapor dönemlerinde yapılan çalışmalar",
    "Sonuç",
    "Çıktılar",
    "Proje ile ilgili harcama kalemleri",
]

GENERAL_INFO_ROWS = ["subject", "lead", "advisor", "dates"]
PLACEHOLDER = "(koyu harflerle yazılacak)"


def tr_upper(text: str) -> str:
    """Türkçe büyük harf: i→İ, ı→I. str.upper() 'i'yi 'I' yapar."""
    return text.replace("i", "İ").replace("ı", "I").upper()


# --------------------------------------------------------------------------- styles
def ensure_styles(doc) -> None:
    styles = doc.styles
    names = {s.name for s in styles}
    if "KL Body" not in names:
        st = styles.add_style("KL Body", WD_STYLE_TYPE.PARAGRAPH)
        st.base_style = styles["Normal"]
        st.font.name, st.font.size = FONT, Pt(11)
        pf = st.paragraph_format
        pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pf.space_after, pf.line_spacing = Pt(6), 1.15
        pf.widow_control = True
    if "Heading 2" not in names:
        st = styles.add_style("Heading 2", WD_STYLE_TYPE.PARAGRAPH)
        st.base_style = styles["Normal"]
        st.font.name, st.font.size, st.font.bold = FONT, Pt(11), True
        pf = st.paragraph_format
        pf.space_before, pf.space_after = Pt(10), Pt(4)
        pf.keep_with_next = True
        _set_outline(st.element.get_or_add_pPr(), 1)
    if "KL Caption" not in names:
        st = styles.add_style("KL Caption", WD_STYLE_TYPE.PARAGRAPH)
        st.base_style = styles["Normal"]
        st.font.name, st.font.size = FONT, Pt(10)
        pf = st.paragraph_format
        pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pf.space_before, pf.space_after = Pt(4), Pt(8)
    if "KL Reference" not in names:
        st = styles.add_style("KL Reference", WD_STYLE_TYPE.PARAGRAPH)
        st.base_style = styles["Normal"]
        st.font.name, st.font.size = FONT, Pt(10)
        pf = st.paragraph_format
        pf.left_indent, pf.first_line_indent = Cm(1.0), Cm(-1.0)
        pf.space_after = Pt(4)
    for s in styles:
        if s.type == WD_STYLE_TYPE.PARAGRAPH and s.name in (
            "KL Body",
            "Heading 2",
            "KL Caption",
            "KL Reference",
        ):
            rfonts = s.element.get_or_add_rPr().get_or_add_rFonts()
            for attr in ("w:ascii", "w:hAnsi", "w:cs"):
                rfonts.set(qn(attr), FONT)


def _set_outline(ppr, level: int) -> None:
    for old in ppr.findall(qn("w:outlineLvl")):
        ppr.remove(old)
    el = OxmlElement("w:outlineLvl")
    el.set(qn("w:val"), str(level))
    ppr.append(el)


# --------------------------------------------------------------------------- template
def open_template(path: Path | None = None):
    doc = Document(str(path or template_path()))
    ensure_styles(doc)
    for p in doc.paragraphs:
        if any(is_label(p.text, lb) for lb in HEADING_LABELS):
            _set_outline(p._p.get_or_add_pPr(), 0)
    return doc


def fill_cover(doc, title: str, lead_name: str, advisor: str) -> None:
    """Kapaktaki text box'a başlık ve adları yazar; placeholder'ı kaldırır."""
    body = doc.element.body
    paras = body.findall(".//" + qn("w:txbxContent") + "//" + qn("w:p"))
    for p in paras:
        text = "".join(t.text or "" for t in p.iter(qn("w:t")))
        if "BAŞLIĞI" in text:
            for t in p.iter(qn("w:t")):
                if PLACEHOLDER in (t.text or ""):
                    t.text = t.text.replace(PLACEHOLDER, "")
            _append_run(p, " " + tr_upper(title), bold=True)
        elif "YÜRÜTÜCÜSÜNÜN" in text:
            _append_run(p, " " + lead_name)
        elif "DANIŞMANININ" in text:
            _append_run(p, " " + advisor)


def _append_run(p, text: str, bold: bool = False) -> None:
    runs = p.findall(qn("w:r"))
    new = copy.deepcopy(runs[-1]) if runs else OxmlElement("w:r")
    for child in list(new):
        if child.tag != qn("w:rPr"):
            new.remove(child)
    rpr = new.find(qn("w:rPr"))
    if bold and rpr is not None and rpr.find(qn("w:b")) is None:
        rpr.append(OxmlElement("w:b"))
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = text
    new.append(t)
    p.append(new)


def fill_general_info(doc, values: dict[str, str]) -> None:
    table = doc.tables[0]
    for row, key in zip(table.rows, GENERAL_INFO_ROWS, strict=False):
        if key in values:
            cell = row.cells[1]
            para = cell.paragraphs[-1]
            run = para.add_run(values[key])
            run.font.name = FONT


def fill_date(doc, date_text: str) -> None:
    for p in doc.paragraphs:
        if p.text.strip().startswith("Tarih"):
            p.add_run(" " + date_text).font.name = FONT
            return


def is_label(text: str, label: str) -> bool:
    """'Sonuç' etiketi 'Sonuç Raporu Formatı:' satırıyla karışmasın diye kalan kısım denetlenir."""
    text = text.strip()
    if not text.startswith(label):
        return False
    rest = text[len(label) :].strip()
    return rest == "" or rest[0] in ":(" or len(label) > 15


def section_anchor(doc, key: str) -> Paragraph:
    label = SECTIONS[key]
    for p in doc.paragraphs:
        if is_label(p.text, label):
            return p
    raise KeyError(f"Şablonda bölüm etiketi bulunamadı: {label!r}")


def signature_table(doc) -> Table:
    for t in doc.tables:
        if "İMZA" in t.rows[0].cells[0].text:
            return t
    raise KeyError("İmza tablosu bulunamadı")


# --------------------------------------------------------------------------- writer
class SectionWriter:
    """Bir bölüm etiketinin altına sırayla içerik ekler."""

    counters: ClassVar[dict[str, int]] = {"Şekil": 0, "Tablo": 0}

    def __init__(self, doc, anchor_element):
        self.doc = doc
        self.cursor = anchor_element

    @classmethod
    def at_section(cls, doc, key: str) -> SectionWriter:
        return cls(doc, section_anchor(doc, key)._p)

    @classmethod
    def before_signature(cls, doc) -> SectionWriter:
        tbl = signature_table(doc)._tbl
        prev = tbl.getprevious()
        # İmza tablosundan önceki boş paragraflar korunur; içerik onların önüne girer.
        while prev is not None and prev.tag == qn("w:p") and not "".join(prev.itertext()).strip():
            prev = prev.getprevious()
        return cls(doc, prev)

    def _place(self, element) -> None:
        self.cursor.addnext(element)
        self.cursor = element

    def _para(self, style: str) -> Paragraph:
        p = OxmlElement("w:p")
        self._place(p)
        para = Paragraph(p, self.doc._body)
        para.style = self.doc.styles[style]
        return para

    def heading(self, text: str) -> Paragraph:
        para = self._para("Heading 2")
        para.add_run(text)
        return para

    def text(self, text: str) -> Paragraph:
        """**kalın** ve *italik* işaretlerini destekleyen gövde paragrafı."""
        para = self._para("KL Body")
        for part in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", text):
            if not part:
                continue
            if part.startswith("**"):
                para.add_run(part[2:-2]).bold = True
            elif part.startswith("*"):
                para.add_run(part[1:-1]).italic = True
            else:
                para.add_run(part)
        return para

    def bullets(self, items: list[str]) -> None:
        for item in items:
            para = self.text("•\t" + item)
            para.paragraph_format.left_indent = Cm(0.75)
            para.paragraph_format.first_line_indent = Cm(-0.5)
            para.paragraph_format.space_after = Pt(2)

    def caption(self, kind: str, text: str) -> Paragraph:
        SectionWriter.counters[kind] += 1
        n = SectionWriter.counters[kind]
        para = self._para("KL Caption")
        if kind == "Tablo":
            para.paragraph_format.keep_with_next = True
        para.add_run(f"{kind} ").bold = True
        _seq_field(para, kind, n)
        para.add_run(". ").bold = True
        para.add_run(text)
        return para

    def table(
        self,
        df: pd.DataFrame,
        caption: str,
        col_widths_cm: list[float] | None = None,
        number_format: str = "{:.2f}",
    ) -> Table:
        self.caption("Tablo", caption)
        rows, cols = df.shape
        tbl = self.doc.add_table(rows=rows + 1, cols=cols)
        self._place(tbl._tbl)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        _table_borders(tbl)
        widths = col_widths_cm or [TEXT_WIDTH_CM / cols] * cols
        if sum(widths) > TEXT_WIDTH_CM + 0.01:
            raise ValueError(f"Tablo genişliği {sum(widths):.1f} cm > {TEXT_WIDTH_CM} cm metin alanı")
        for j, name in enumerate(df.columns):
            _cell_text(tbl.cell(0, j), str(name), bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        _repeat_header(tbl.rows[0])
        for i, (_, row) in enumerate(df.iterrows(), start=1):
            for j, val in enumerate(row):
                numeric = isinstance(val, (int, float)) and not isinstance(val, bool)
                shown = number_format.format(val).replace(".", ",") if isinstance(val, float) else str(val)
                _cell_text(
                    tbl.cell(i, j),
                    shown,
                    align=WD_ALIGN_PARAGRAPH.RIGHT if numeric else WD_ALIGN_PARAGRAPH.LEFT,
                )
        keep_together = len(tbl.rows) <= 15  # kısa tablo sayfa arasında bölünmesin
        for r_i, row in enumerate(tbl.rows):
            _cant_split(row)
            for j, cell in enumerate(row.cells):
                cell.width = Cm(widths[j])
                if keep_together and r_i < len(tbl.rows) - 1:
                    for para in cell.paragraphs:
                        para.paragraph_format.keep_with_next = True
        # Tablodan sonra boşluk
        self._para("KL Body").paragraph_format.space_after = Pt(2)
        return tbl

    def figure(self, image: Path, caption: str, width_cm: float = 14.0) -> None:
        if width_cm > TEXT_WIDTH_CM:
            raise ValueError("Şekil metin alanından geniş")
        para = self._para("KL Caption")
        para.paragraph_format.keep_with_next = True
        para.add_run().add_picture(str(image), width=Cm(width_cm))
        self.caption("Şekil", caption)

    def references(self, entries: list[str], title: str = "Kaynaklar") -> None:
        self.heading(title)
        for e in entries:
            para = self._para("KL Reference")
            para.add_run(e)

    def page_break(self) -> None:
        self._para("KL Body").add_run().add_break(WD_BREAK.PAGE)


# --------------------------------------------------------------------------- XML ayrıntıları
def _seq_field(para: Paragraph, kind: str, cached: int) -> None:
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), f" SEQ {kind} \\* ARABIC ")
    r = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    rpr.append(OxmlElement("w:b"))
    r.append(rpr)
    t = OxmlElement("w:t")
    t.text = str(cached)
    r.append(t)
    fld.append(r)
    para._p.append(fld)


def _cell_text(cell, text: str, bold: bool = False, align=WD_ALIGN_PARAGRAPH.LEFT) -> None:
    para = cell.paragraphs[0]
    para.alignment = align
    para.paragraph_format.space_after = Pt(0)
    run = para.add_run(text)
    run.font.name, run.font.size, run.bold = FONT, Pt(9.5), bold


def _table_borders(tbl: Table) -> None:
    tblpr = tbl._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), "000000")
        borders.append(el)
    tblpr.append(borders)


def _repeat_header(row) -> None:
    trpr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    trpr.append(el)


def _cant_split(row) -> None:
    trpr = row._tr.get_or_add_trPr()
    trpr.append(OxmlElement("w:cantSplit"))
