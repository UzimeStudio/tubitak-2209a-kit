"""Sınırlı Markdown'dan akademik Word belgesi üretir (şablonsuz raporlar için).

Kullanım:
    uv run python tools/md2docx.py report/drafts/proposal.md report/drafts/proposal.docx

Desteklenen sözdizimi:
    ---              (ilk satırda) YAML benzeri kapak alanları: title, subtitle, meta (birden çok satır)
    # / ## / ###     Heading 1–3 (gerçek Word başlık stilleri; İçindekiler bunlardan üretilir)
    [[TOC]]          İçindekiler field'ı (PDF dönüşümünde Word günceller)
    [[PAGEBREAK]]    Sayfa sonu
    [[KAYNAKCA]]     Metinde atıf yapılan kaynakları bibkit modülünden alfabetik ekler
    Tablo: başlık    Hemen ardından gelen pipe tablosunun caption'ı (tablonun üstünde)
    ![başlık](yol){width=14}   Şekil; caption altında. Yol Markdown dosyasına göredir
    - madde / 1. madde, > not kutusu, **kalın**, *italik*
Şekil/Tablo numaraları SEQ field'ıdır; metinde "Şekil 1", "Tablo 2" diye atıf yapılır.

Kaynakça, kardeş `bibkit` modülünden okunur (API: load(), cite_key(r), format_entry(r)).
Modül yoksa [[KAYNAKCA]] atlanır ve uyarı basılır (araç yine çalışır).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_application import read_md
from check_report import citations, fold
from docxkit import FONT, SectionWriter, _set_outline, ensure_styles

INLINE = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*)")


def _field(paragraph, instr: str, placeholder: str = "") -> None:
    """Karmaşık field (TOC, PAGE) ekler."""
    run = paragraph.add_run()
    for kind, text in (
        ("begin", None),
        ("instr", instr),
        ("separate", None),
        ("text", placeholder),
        ("end", None),
    ):
        if kind == "instr":
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = text
            run._r.append(el)
        elif kind == "text":
            t = OxmlElement("w:t")
            t.text = text
            run._r.append(t)
        else:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), kind)
            run._r.append(el)


def _inline(paragraph, text: str) -> None:
    for part in INLINE.split(text):
        if not part:
            continue
        if part.startswith("**"):
            paragraph.add_run(part[2:-2]).bold = True
        elif part.startswith("*"):
            paragraph.add_run(part[1:-1]).italic = True
        else:
            paragraph.add_run(part)


def setup(doc) -> None:
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    for side in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
        setattr(sec, side, Cm(2.5))
    normal = doc.styles["Normal"]
    normal.font.name, normal.font.size = FONT, Pt(11)
    normal.element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), FONT)
    ensure_styles(doc)
    sizes = {"Heading 1": 14, "Heading 2": 12, "Heading 3": 11}
    for name, size in sizes.items():
        st = doc.styles[name]
        st.font.name, st.font.size, st.font.bold = FONT, Pt(size), True
        st.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)
        rf = st.element.get_or_add_rPr().get_or_add_rFonts()
        for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rf.set(qn(a), FONT)
        pf = st.paragraph_format
        pf.space_before, pf.space_after, pf.keep_with_next = (
            Pt(14 if name == "Heading 1" else 10),
            Pt(6),
            True,
        )
    for name in ("List Bullet", "List Number"):
        st = doc.styles[name]
        st.font.name, st.font.size = FONT, Pt(11)
        st.paragraph_format.space_after = Pt(3)
    if "KL Note" not in {s.name for s in doc.styles}:
        from docx.enum.style import WD_STYLE_TYPE

        st = doc.styles.add_style("KL Note", WD_STYLE_TYPE.PARAGRAPH)
        st.base_style = doc.styles["KL Body"]
        st.font.size = Pt(10)
        pf = st.paragraph_format
        pf.left_indent, pf.right_indent = Cm(0.4), Cm(0.4)
        pf.space_before, pf.space_after = Pt(6), Pt(8)
        ppr = st.element.get_or_add_pPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:fill"), "EEF3F8")
        ppr.append(shd)
        bdr = OxmlElement("w:pBdr")
        left = OxmlElement("w:left")
        for k, v in (("w:val", "single"), ("w:sz", "18"), ("w:color", "1F3A5F"), ("w:space", "6")):
            left.set(qn(k), v)
        bdr.append(left)
        ppr.append(bdr)
    # Tema yazı tipi öznitelikleri (asciiTheme vb.) açık yazı tipini ezer; başlıklar Calibri/Cambria çıkar.
    styles_root = doc.styles.element
    for rf in styles_root.iter(qn("w:rFonts")):
        for attr in list(rf.attrib):
            if "Theme" in attr or "theme" in attr:
                del rf.attrib[attr]
        for a in ("w:ascii", "w:hAnsi", "w:cs"):
            if rf.get(qn(a)) is None:
                rf.set(qn(a), FONT)
    footer = sec.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _field(footer, " PAGE ", "1")


def cover(doc, meta: dict) -> None:
    for _ in range(6):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(meta.get("title", ""))
    r.bold, r.font.size = True, Pt(18)
    r.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)
    if meta.get("subtitle"):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(12)
        p.add_run(meta["subtitle"]).font.size = Pt(13)
    for _ in range(8):
        doc.add_paragraph()
    for line in meta.get("meta", []):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(2)
        _inline(p, line)
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def parse_front(lines: list[str]) -> tuple[dict, list[str]]:
    if not lines or lines[0].strip() != "---":
        return {}, lines
    meta: dict = {"meta": []}
    i = 1
    while i < len(lines) and lines[i].strip() != "---":
        key, _, val = lines[i].partition(":")
        if key.strip() == "meta":
            meta["meta"].append(val.strip())
        else:
            meta[key.strip()] = val.strip()
        i += 1
    return meta, lines[i + 1 :]


def table_from(lines: list[str]) -> pd.DataFrame:
    rows = [
        [c.strip() for c in ln.strip().strip("|").split("|")]
        for ln in lines
        if not re.match(r"^\|\s*:?-", ln)
    ]
    return pd.DataFrame(rows[1:], columns=rows[0])


def references_for(text: str) -> list[str]:
    """Metinde atıf yapılan kaynakları bibkit modülünden biçimli satır olarak döndürür.

    Modül yoksa boş liste döner ve çağıran uyarı basar.
    """
    try:
        import bibkit
    except ImportError:
        return []
    cited = citations(text)
    out = []
    for r in bibkit.load():
        name, year = bibkit.cite_key(r)
        if (fold(name), str(year)) in cited:
            out.append(r)
    sort_key = getattr(bibkit, "sort_key", lambda r: (r["authors"][0].casefold(), str(r["year"])))
    out.sort(key=sort_key)
    return [bibkit.format_entry(r) for r in out]


def _bibkit_missing() -> bool:
    import importlib.util

    return importlib.util.find_spec("bibkit") is None


def build(md_path: Path, out: Path) -> Path:
    raw = read_md(md_path)  # BOM + CRLF normalizasyonu: kapak alanı/başlık kaçmasın
    meta, lines = parse_front(raw.splitlines())
    body_text = "\n".join(lines)
    doc = Document()
    setup(doc)
    SectionWriter.counters = {"Şekil": 0, "Tablo": 0}
    if meta:
        cover(doc, meta)
    if not doc.paragraphs:  # kapak bilgisi olmayan dosya (ör. TYBS metni)
        doc.add_paragraph()
    w = SectionWriter(doc, doc.paragraphs[-1]._p)

    # [[PAGEBREAK]] hemen ardından başlık gelirse ayrı sayfa sonu yerine başlığa
    # "önce sayfa sonu" verilir; önceki sayfa tam dolduğunda boş sayfa oluşmaz.
    break_next = False

    def heading(level: int, text: str):
        nonlocal break_next
        para = w._para(f"Heading {level}")
        para.add_run(text)
        if break_next:
            para.paragraph_format.page_break_before = True
            break_next = False
        _set_outline(para._p.get_or_add_pPr(), level - 1)

    pending_caption = None
    para_buf: list[str] = []

    def flush():
        if para_buf:
            p = w._para("KL Body")
            _inline(p, " ".join(s.strip() for s in para_buf))
            para_buf.clear()

    i = 0
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s:
            flush()
        elif s == "[[TOC]]":
            flush()
            t = w._para("KL Body")
            t.paragraph_format.space_after = Pt(12)
            r = t.add_run("İçindekiler")
            r.bold, r.font.size = True, Pt(14)
            r.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)
            p = w._para("KL Body")
            _field(p, ' TOC \\o "1-3" \\h \\z \\u ', "İçindekiler PDF dönüşümünde güncellenir.")
        elif s == "[[PAGEBREAK]]":
            flush()
            nxt = next((x.strip() for x in lines[i + 1 :] if x.strip()), "")
            if nxt.startswith("#"):
                break_next = True
            else:
                w.page_break()
        elif s == "[[KAYNAKCA]]":
            flush()
            entries = references_for(body_text)
            if not entries and _bibkit_missing():
                print("UYARI: bibkit modülü bulunamadı; [[KAYNAKCA]] atlandı.", file=sys.stderr)
            for e in entries:
                w._para("KL Reference").add_run(e)
        elif m := re.match(r"^(#{1,3})\s+(.*)$", s):
            flush()
            heading(len(m.group(1)), m.group(2))
        elif s.startswith("Tablo:"):
            flush()
            pending_caption = s[len("Tablo:") :].strip()
        elif s.startswith("|"):
            flush()
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            df = table_from(block)
            widths = _widths(df)
            w.table(df, pending_caption or "", col_widths_cm=widths)
            pending_caption = None
            continue
        elif m := re.match(r"^!\[(.+)\]\((.+?)\)(\{width=([\d.]+)\})?$", s):
            flush()
            # Yol Markdown dosyasına göre çözülür (GitHub önizlemesiyle aynı).
            img = (md_path.parent / m.group(2)).resolve()
            w.figure(img, m.group(1), width_cm=float(m.group(4) or 15))
        elif m := re.match(r"^[-*]\s+(.*)$", s):
            flush()
            _inline(w._para("List Bullet"), m.group(1))
        elif m := re.match(r"^(\d+)\.\s+(.*)$", s):
            flush()
            # Numara metinden alınır: Word'ün ortak liste sayacı listeler arasında numarayı sürdürür.
            p = w._para("KL Body")
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            pf = p.paragraph_format
            pf.left_indent, pf.first_line_indent, pf.space_after = Cm(0.75), Cm(-0.5), Pt(3)
            pf.tab_stops.add_tab_stop(Cm(0.75))
            _inline(p, f"{m.group(1)}.\t{m.group(2)}")
        elif s.startswith(">"):
            flush()
            _inline(w._para("KL Note"), s.lstrip("> ").strip())
        else:
            para_buf.append(s)
        i += 1
    flush()
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out))
    return out


def _widths(df: pd.DataFrame, total: float = 16.0) -> list[float]:
    """Sütun genişliğini içerik uzunluğuna göre paylaştırır (en az 1,6 cm)."""
    lens = [max([len(str(c))] + [len(str(v)) for v in df[c]]) for c in df.columns]
    lens = [min(max(n, 6), 60) for n in lens]
    raw = [total * n / sum(lens) for n in lens]
    raw = [max(r, 1.6) for r in raw]
    k = total / sum(raw)
    return [int(r * k * 100) / 100 for r in raw]  # aşağı yuvarlama: toplam 16 cm'yi aşmaz


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    if "-h" in sys.argv[1:] or "--help" in sys.argv[1:]:
        print((__doc__ or '').strip())
        raise SystemExit(0)
    if len(sys.argv) != 3:
        print("Kullanım: uv run python tools/md2docx.py <md> <docx>", file=sys.stderr)
        raise SystemExit(2)
    print(build(Path(sys.argv[1]), Path(sys.argv[2])))
