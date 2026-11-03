"""PDF sayfa düzeni denetimi ve sayfa görüntüleri.

Kullanım:
    uv run python tools/pdf_check.py report/final/test.pdf [--headings "Giriş" "Sonuç" ...]

Üretir: <pdf_adı>_pages/page-NN.png (110 dpi) ve stdout'a JSON rapor.
Otomatik kontroller:
    - A4 boyutu
    - boş sayfa (ink oranı < %0,2)
    - gömülü olmayan font
    - sayfanın son satırında kalan başlık (yetim başlık)
    - sağ/sol kenar boşluğuna taşan içerik (ink kenar şeridinde)
Otomatik kontrol görsel incelemenin yerine geçmez; PNG'ler tek tek açılıp bakılmalıdır.

Çıkış kodu: sorun varsa 1.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pypdfium2 as pdfium
from pypdf import PdfReader

A4_PT = (595.3, 841.9)
DPI = 110


def fonts(reader: PdfReader) -> list[dict]:
    seen: dict[str, bool] = {}
    for page in reader.pages:
        res = page.get("/Resources") or {}
        for f in (res.get("/Font") or {}).values():
            f = f.get_object()
            name = str(f.get("/BaseFont", "?"))
            desc = f.get("/FontDescriptor")
            if desc is None and "/DescendantFonts" in f:
                desc = f["/DescendantFonts"][0].get_object().get("/FontDescriptor")
            embedded = bool(desc) and any(
                k in desc.get_object() for k in ("/FontFile", "/FontFile2", "/FontFile3")
            )
            seen[name] = seen.get(name, False) or embedded
    return [{"font": k, "embedded": v} for k, v in sorted(seen.items())]


def check(pdf: Path, headings: list[str]) -> dict:
    reader = PdfReader(str(pdf))
    doc = pdfium.PdfDocument(str(pdf))
    outdir = pdf.with_name(pdf.stem + "_pages")
    outdir.mkdir(exist_ok=True)
    pages, problems = [], []
    for i, page in enumerate(doc, start=1):
        w, h = page.get_size()
        img = page.render(scale=DPI / 72).to_pil()
        png = outdir / f"page-{i:02d}.png"
        img.save(png)
        gray = np.asarray(img.convert("L"))
        ink = gray < 200
        ink_ratio = float(ink.mean())
        margin_px = int(1.5 / 2.54 * DPI)  # 1,5 cm şerit (2,5 cm kenar boşluğunun içinde)
        edge_ink = float(ink[:, :margin_px].mean() + ink[:, -margin_px:].mean())
        text = (reader.pages[i - 1].extract_text() or "").strip()
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        last = lines[-1] if lines else ""
        info = {
            "page": i,
            "size_pt": [round(w, 1), round(h, 1)],
            "ink_ratio": round(ink_ratio, 4),
            "edge_ink": round(edge_ink, 4),
            "png": str(png),
        }
        if abs(w - A4_PT[0]) > 2 or abs(h - A4_PT[1]) > 2:
            problems.append(f"s.{i}: A4 değil ({w:.0f}×{h:.0f} pt)")
        if ink_ratio < 0.002:
            problems.append(f"s.{i}: boş görünüyor")
        if edge_ink > 0.002:
            problems.append(f"s.{i}: kenar boşluğunda içerik var (taşma olabilir)")
        for hd in headings:
            if last and (last == hd or last.endswith(hd)) and i < len(doc):
                problems.append(f"s.{i}: '{hd}' başlığı sayfa sonunda tek kalmış olabilir")
        pages.append(info)
    font_list = fonts(reader)
    for f in font_list:
        if not f["embedded"]:
            problems.append(f"Gömülü olmayan font: {f['font']}")
    return {
        "pdf": str(pdf),
        "page_count": len(doc),
        "fonts": font_list,
        "pages": pages,
        "problems": problems,
        "visual_review_required": True,
    }


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--headings", nargs="*", default=[])
    args = ap.parse_args()
    report = check(args.pdf, args.headings)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
