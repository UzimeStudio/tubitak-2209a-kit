"""DOCX'i PDF'e çevirir (platforma göre en iyi motoru seçer).

Kullanım:
    uv run python tools/docx_to_pdf.py report/final/test.docx [report/final/test.pdf]

Motor seçimi:
    1. Windows + Microsoft Word kuruluysa: `tools/docx_to_pdf.ps1` (Word COM).
       Field ve TOC güncellenir, yazı tipleri gömülür (PDF/A-1). En doğru çıktı.
    2. Word yoksa / macOS / Linux: LibreOffice `soffice --headless --convert-to pdf`.
       `soffice` veya `libreoffice` PATH'te aranır.
    3. İkisi de yoksa: çıkış kodu 2 ve kurulum ipucu basılır.

Çıkış kodu: 0 başarı, 2 motor yok / dönüşüm hatası.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

SETUP_HINT = (
    "PDF dönüşümü için bir motor gerekli:\n"
    "  - Windows: Microsoft Word kurulu olmalı (tools/docx_to_pdf.ps1 onu kullanır), veya\n"
    "  - LibreOffice kurun ve `soffice`/`libreoffice` komutunu PATH'e ekleyin\n"
    "    (Windows: winget install TheDocumentFoundation.LibreOffice;\n"
    "     macOS: brew install --cask libreoffice;\n"
    "     Linux: apt install libreoffice veya dnf install libreoffice)."
)


def _powershell() -> str | None:
    return shutil.which("pwsh") or shutil.which("powershell")


def _word_available() -> bool:
    """Windows'ta Word COM nesnesi oluşturulabiliyor mu?"""
    if os.name != "nt":
        return False
    ps = _powershell()
    if not ps:
        return False
    probe = (
        "try { $w = New-Object -ComObject Word.Application; "
        "$w.Quit(); 'yes' } catch { 'no' }"
    )
    try:
        out = subprocess.run(
            [ps, "-NoProfile", "-NonInteractive", "-Command", probe],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return out.returncode == 0 and "yes" in out.stdout.lower()


# PATH'te bulunamazsa denenecek platforma özgü LibreOffice adayları.
_SOFFICE_CANDIDATES = {
    "darwin": ["/Applications/LibreOffice.app/Contents/MacOS/soffice"],
    "linux": ["/usr/bin/soffice", "/usr/lib/libreoffice/program/soffice"],
    "win32": [r"C:\Program Files\LibreOffice\program\soffice.exe"],
}


def _soffice() -> str | None:
    found = shutil.which("soffice") or shutil.which("libreoffice")
    if found:
        return found
    for cand in _SOFFICE_CANDIDATES.get(sys.platform, []):
        if Path(cand).exists():
            return cand
    return None


def convert_with_word(docx: Path, pdf: Path) -> Path:
    ps = _powershell()
    if not ps:
        raise RuntimeError("PowerShell bulunamadı")
    script = Path(__file__).resolve().parent / "docx_to_pdf.ps1"
    cmd = [ps, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), str(docx), "-Pdf", str(pdf)]
    res = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Word dönüşümü başarısız: {res.stderr.strip() or res.stdout.strip()}")
    sys.stdout.write(res.stdout)
    return pdf


def convert_with_soffice(docx: Path, pdf: Path, soffice: str) -> Path:
    # LibreOffice çıktı adını seçtirmez; hedef klasöre <stem>.pdf üretir, sonra yeniden adlandırılır.
    cmd = [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(pdf.parent), str(docx)]
    res = subprocess.run(cmd, check=False, capture_output=True, text=True)
    produced = pdf.parent / (docx.stem + ".pdf")
    # soffice bazen 0 döndürüp dosya üretmez (sessiz başarısızlık); bunu da hata say.
    if res.returncode != 0 or not produced.exists():
        detail = res.stderr.strip() or res.stdout.strip() or "soffice çıktı üretmedi"
        raise RuntimeError(f"LibreOffice dönüşümü başarısız: {detail}")
    if produced != pdf:
        if pdf.exists():
            pdf.unlink()
        produced.rename(pdf)
    # LibreOffice PDF/A garantisi VERMEZ; PDF/A gereken resmî çıktı için Word yolu kullanılmalı.
    print(f"PDF: {pdf} (LibreOffice — PDF/A garantisi yok; PDF/A için Windows+Word yolu gerekir)")
    return pdf


def convert(docx: Path, pdf: Path | None = None) -> Path:
    docx = docx.resolve()
    if not docx.exists():
        raise FileNotFoundError(f"DOCX yok: {docx}")
    pdf = (pdf or docx.with_suffix(".pdf")).resolve()
    pdf.parent.mkdir(parents=True, exist_ok=True)
    if _word_available():
        return convert_with_word(docx, pdf)
    soffice = _soffice()
    if soffice:
        return convert_with_soffice(docx, pdf, soffice)
    raise RuntimeError(SETUP_HINT)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if "-h" in sys.argv[1:] or "--help" in sys.argv[1:]:
        print((__doc__ or "").strip())
        return 0
    if len(sys.argv) < 2:
        print("Kullanım: docx_to_pdf.py <docx> [pdf]", file=sys.stderr)
        return 2
    docx = Path(sys.argv[1])
    pdf = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    try:
        convert(docx, pdf)
    except (RuntimeError, FileNotFoundError) as e:
        print(f"HATA: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
