"""Var olan bir öneri taslağını (DOCX, PDF, Markdown, TXT) kite alır ve TYBS bölümlerine eşler.

Kullanım:
    uv run python tools/import_draft.py <dosya> [--out report/drafts/imported.md] [--force] [--json]

Ne yapar:
    1. Özgün dosyayı değiştirmeden `report/drafts/original/` altına kopyalar.
    2. Metni Markdown'a çevirir: DOCX başlık stilleri `#` düzeyine, tablolar Markdown
       tablosuna dönüşür; PDF'te numaralı satırlar ("2.", "3.1") başlık sayılır.
    3. Her TYBS bölümünü (rules `tybs_sections` + Başlık, Anahtar Kelimeler, Kaynakça)
       taslaktaki başlıklarla eşler; uzunluğu ve bulunamayanları raporlar.

Var olan çıktının üzerine yazmaz (`--force` hariç). Eşleme önek ve anahtar sözcükle yapılır;
emin olunamayan eşlemeler "elle kontrol" diye işaretlenir. Çıkış: 0 (eşleme tam),
1 (eksik bölüm var), 2 (dosya/ayar hatası).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config

# TYBS bölümü → taslak başlığında aranacak önekler ve anahtar sözcükler (küçük harf, katlanmış).
# Önek, numaralı başlıkta (ör. "1.1") kesin eşleme; anahtar sözcük, numarasız/farklı
# numaralı taslaklarda (ör. "5.1 Çalışma takvimi") yardımcı eşleme.
SECTION_HINTS: dict[str, list[str]] = {
    "Başlık": ["baslik", "proje basligi"],
    "Anahtar Kelimeler": ["anahtar kelime"],
    "Özet": ["ozet"],
    "1.1": ["konunun onemi", "problem", "bilimsel nitelik", "onemi"],
    "1.2": ["amac", "hedef"],
    "2.": ["yontem"],
    "3.1": ["calisma takvimi", "is paket", "is-zaman"],
    "3.2": ["risk"],
    "3.3": ["olanak", "altyapi"],
    "4.": ["yaygin etki", "beklenen cikti"],
    "5.": ["diger konular", "belirtmek istediginiz"],
    "6.": ["ekler"],
    "Kaynakça": ["kaynakca", "kaynaklar", "references"],
}
NUMBERED = re.compile(r"^\s*((?:\d+\.)+\d*|\d+\.)\s+\S")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def fold(text: str) -> str:
    table = str.maketrans("çğıöşüÇĞİÖŞÜâîû", "cgiosucgiosuaiu")
    return text.translate(table).lower()


# ---------- dönüştürücüler ----------


def _docx_to_md(path: Path) -> str:
    from docx import Document
    from docx.oxml.ns import qn

    doc = Document(str(path))
    out: list[str] = []
    body = doc.element.body
    tables = {t._tbl: t for t in doc.tables}
    paragraphs = {p._p: p for p in doc.paragraphs}
    for child in body.iterchildren():
        if child.tag == qn("w:p") and child in paragraphs:
            p = paragraphs[child]
            text = p.text.strip()
            if not text:
                continue
            style = (p.style.name or "").lower() if p.style is not None else ""
            level = None
            m = re.search(r"(heading|başlık|baslik)\s*(\d)", style)
            if m:
                level = int(m.group(2))
            elif style in ("title", "konu başlığı"):
                level = 1
            if level:
                out.append(f"{'#' * min(level, 6)} {text}")
            elif "list" in style or "liste" in style:
                out.append(f"- {text}")
            else:
                out.append(text)
            out.append("")
        elif child.tag == qn("w:tbl") and child in tables:
            rows = [[c.text.strip().replace("\n", " ").replace("|", "/") for c in r.cells] for r in tables[child].rows]
            if not rows:
                continue
            width = max(len(r) for r in rows)
            rows = [r + [""] * (width - len(r)) for r in rows]
            out.append("| " + " | ".join(rows[0]) + " |")
            out.append("|" + " --- |" * width)
            out.extend("| " + " | ".join(r) + " |" for r in rows[1:])
            out.append("")
    return "\n".join(out)


def _pdf_heading(line: str) -> bool:
    m = NUMBERED.match(line)
    if not m or len(line) > 70 or line.endswith((".", ",", ";", ":")):
        return False
    first = int(m.group(1).split(".")[0])
    rest = line[m.end(1) :].strip()
    return first <= 20 and len(rest.split()) <= 9 and rest[:1].isupper() and "http" not in rest


def _pdf_to_md(path: Path) -> str:
    from pypdf import PdfReader

    lines: list[str] = []
    for page in PdfReader(str(path)).pages:
        for raw in (page.extract_text() or "").splitlines():
            line = raw.strip()
            if not line:
                continue
            # Numaralı, kısa ve cümle olmayan satırlar başlık adayıdır ("2. Yöntem", "3.1 Çalışma Takvimi").
            # Gövdedeki numaralı maddeler (uzun, noktayla biten) ve kaynakça numaraları elenir.
            if _pdf_heading(line):
                depth = line.split()[0].strip(".").count(".") + 1
                lines += ["", f"{'#' * min(depth + 1, 6)} {line}", ""]
            elif fold(line) in ("ozet", "kaynakca", "kaynaklar"):
                lines += ["", f"## {line}", ""]
            else:
                lines.append(line)
    if not any(lines):
        raise config.ConfigError(
            f"{path.name}: PDF'ten metin çıkmadı (taranmış olabilir). Metni DOCX/Markdown olarak verin."
        )
    return "\n".join(lines)


def convert(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".docx":
        text = _docx_to_md(path)
    elif suffix == ".pdf":
        text = _pdf_to_md(path)
    elif suffix in (".md", ".markdown", ".txt"):
        text = path.read_text(encoding="utf-8-sig")
    else:
        raise config.ConfigError(f"Desteklenmeyen biçim: {suffix} (DOCX, PDF, MD, TXT)")
    return text.replace("\r\n", "\n").replace("\r", "\n")


# ---------- eşleme ----------


def headings(md: str) -> list[tuple[int, str, int]]:
    """(satır no, başlık metni, düzey) listesi."""
    out = []
    for i, line in enumerate(md.splitlines()):
        m = HEADING.match(line)
        if m:
            out.append((i, m.group(2).strip(), len(m.group(1))))
    return out


def section_text(md: str, line_no: int, level: int) -> str:
    lines = md.splitlines()
    body = []
    for line in lines[line_no + 1 :]:
        m = HEADING.match(line)
        if m and len(m.group(1)) <= level:
            break
        body.append(line)
    return "\n".join(body).strip()


def _prefix_match(title: str, prefix: str) -> bool:
    if not prefix[0].isdigit():
        return False
    num = re.match(r"^((?:\d+\.)*\d+)\.?", title.strip())
    return bool(num) and num.group(1).rstrip(".") == prefix.rstrip(".")


def map_sections(md: str) -> list[dict]:
    try:
        wanted = list(config.rules().get("tybs_sections", []))
    except config.ConfigError:
        wanted = []
    order = ["Başlık", "Anahtar Kelimeler", *wanted, "Kaynakça"]
    order = list(dict.fromkeys(s for s in order if s in SECTION_HINTS))
    found = headings(md)
    used: set[int] = set()
    result = []
    for key in order:
        # Anahtar sözcük zorunlu: serbest taslakta "2. Literatür" TYBS "2. Yöntem" değildir.
        # Numara yalnız adaylar arasında öncelik verir ve eşlemeyi kesinleştirir.
        candidates = [
            (n, t, lv) for n, t, lv in found if n not in used and any(h in fold(t) for h in SECTION_HINTS[key])
        ]
        numbered = [c for c in candidates if _prefix_match(c[1], key)]
        match = (numbered or candidates or [None])[0]
        how = "numara + anahtar sözcük" if numbered else "anahtar sözcük"
        if match:
            used.add(match[0])
            text = section_text(md, match[0], match[2])
            result.append(
                {
                    "section": key,
                    "heading": match[1],
                    "line": match[0] + 1,
                    "matched_by": how,
                    "chars": len(text),
                    "words": len(text.split()),
                    # Numaralı TYBS bölümü farklı numarada bulunduysa ekip eşlemeyi doğrulamalı.
                    "manual_check": key[0].isdigit() and not numbered,
                }
            )
        else:
            result.append({"section": key, "heading": None, "line": None, "matched_by": None})
    unmapped = [t for n, t, _ in found if n not in used]
    return result + [{"unmapped_headings": unmapped}]


# ---------- komut ----------


def run(src: Path, out: Path, force: bool) -> dict:
    if not src.exists():
        raise config.ConfigError(f"Dosya yok: {src}")
    if out.exists() and not force:
        raise config.ConfigError(f"{out} zaten var. Üzerine yazmak için --force kullanın.")
    md = convert(src)
    original_dir = config.PATHS["report_drafts"] / "original"
    original_dir.mkdir(parents=True, exist_ok=True)
    keep = original_dir / src.name
    if src.resolve() != keep.resolve() and not keep.exists():
        shutil.copy2(src, keep)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    mapping = map_sections(md)
    missing = [m["section"] for m in mapping if "section" in m and m["heading"] is None]
    return {"source": str(src), "original_copy": str(keep), "output": str(out), "sections": mapping, "missing": missing}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Var olan öneri taslağını içe alır ve TYBS bölümlerine eşler.")
    ap.add_argument("file", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    out = args.out or (config.PATHS["report_drafts"] / "imported.md")
    try:
        rep = run(args.file, out, args.force)
    except config.ConfigError as e:
        print(f"HATA: {e}")
        return 2
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
        return 1 if rep["missing"] else 0
    print(f"Özgün kopya : {rep['original_copy']}")
    print(f"Markdown    : {rep['output']}")
    print()
    for m in rep["sections"]:
        if "section" not in m:
            if m["unmapped_headings"]:
                print("\nEşlenmeyen başlıklar: " + " · ".join(m["unmapped_headings"]))
            continue
        if m["heading"] is None:
            print(f"  [YOK ] {m['section']}")
        else:
            flag = "ELLE" if m["manual_check"] else "OK  "
            print(f"  [{flag}] {m['section']:<18} ← {m['heading']} (satır {m['line']}, {m['words']} kelime)")
    return 1 if rep["missing"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
