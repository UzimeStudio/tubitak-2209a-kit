"""Literatür matrisi (sources/literature-matrix.xlsx) yönetimi.

Kullanım:
    uv run python tools/matrix.py init           # boş, biçimli matris (varsa dokunmaz)
    uv run python tools/matrix.py add row.json   # satır ekler/günceller (Kaynak ID anahtar)
    uv run python tools/matrix.py validate       # sütun, durum ve references.json eşleşmesi

Kurallar:
    - Her satırın Kaynak ID'si sources/references.json içinde olmalıdır.
    - "Doğrulama durumu" references.json'daki durumla aynı olmalıdır.
    - Bulgular ve sınırlılıklar yalnız tam metinden okunmuş bilgiyle yazılır;
      okunmadıysa "TAM METİN OKUNMADI" yazılır, tahmin yazılmaz.

Yollar `config.PATHS`'ten çağrı anında okunur; böylece testler geçici klasöre yönlendirebilir.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bibkit
import config
from config import PATHS

COLUMNS = [
    ("Kaynak ID", 14),
    ("Yazar", 22),
    ("Yıl", 7),
    ("Çalışmanın başlığı", 40),
    ("Araştırma amacı", 40),
    ("Yöntem", 40),
    ("Veri/örneklem", 32),
    ("Temel bulgular", 48),
    ("Sınırlılıklar", 40),
    ("Projeyle ilişkisi", 40),
    ("DOI", 28),
    ("Doğrulama durumu", 16),
    ("Okunan kaynak", 30),
    ("Satırı hazırlayan / tarih", 24),
]
STATUSES = ["VERIFIED", "PARTIAL", "PUBLISHER_PAGE", "CONFLICT", "NOT_FOUND", "UNVERIFIED"]
REQUIRED_TEXT = ("Araştırma amacı", "Yöntem", "Temel bulgular", "Sınırlılıklar", "Projeyle ilişkisi")


def _references() -> dict:
    """references.json'u {id: kayıt} olarak okur.

    bibkit.load() kullanılır: dosya yoksa boş liste, bozuk JSON'da anlaşılır SystemExit
    (traceback yerine). id'si olmayan kayıtlar KeyError yerine sessizce atlanır.
    """
    out: dict = {}
    for r in bibkit.load():
        rid = r.get("id") if isinstance(r, dict) else None
        if rid:
            out[rid] = r
    return out


def init() -> None:
    xlsx = PATHS["matrix_xlsx"]
    if xlsx.exists():
        print(f"Zaten var, değiştirilmedi: {xlsx}")
        return
    xlsx.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "Matris"
    ws.append([c for c, _ in COLUMNS])
    for i, (_, width) in enumerate(COLUMNS, start=1):
        cell = ws.cell(row=1, column=i)
        cell.font = Font(bold=True, color="FFFFFF", name="Arial")
        cell.fill = PatternFill("solid", fgColor="1F4E79")
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        ws.column_dimensions[cell.column_letter].width = width
    ws.freeze_panes = "B2"
    status_col = [c for c, _ in COLUMNS].index("Doğrulama durumu") + 1
    status_letter = ws.cell(row=2, column=status_col).column_letter
    dv = DataValidation(type="list", formula1='"' + ",".join(STATUSES) + '"', allow_blank=False)
    ws.add_data_validation(dv)
    dv.add(f"{status_letter}2:{status_letter}1000")
    notes = wb.create_sheet("Açıklama")
    for line in (__doc__ or "").strip().splitlines():
        notes.append([line])
    wb.save(xlsx)
    print(f"Oluşturuldu: {xlsx}")


def add(row_file: Path) -> None:
    xlsx = PATHS["matrix_xlsx"]
    if not xlsx.exists():
        raise SystemExit(f"Matris yok: {xlsx}. Önce `matrix.py init` çalıştırın.")
    row = json.loads(row_file.read_text(encoding="utf-8"))
    missing = [c for c, _ in COLUMNS if c not in row]
    if missing:
        raise SystemExit(f"Eksik sütunlar: {missing}")
    wb = load_workbook(xlsx)
    ws = wb["Matris"]
    target = None
    for r in range(2, ws.max_row + 1):
        if ws.cell(row=r, column=1).value == row["Kaynak ID"]:
            target = r
    target = target or ws.max_row + 1
    for i, (col, _) in enumerate(COLUMNS, start=1):
        cell = ws.cell(row=target, column=i, value=row[col])
        cell.alignment = Alignment(wrap_text=True, vertical="top")
        cell.font = Font(name="Arial", size=9)
    wb.save(xlsx)
    print(f"Satır {target}: {row['Kaynak ID']}")


def validate() -> int:
    xlsx = PATHS["matrix_xlsx"]
    if not xlsx.exists():
        print(f"Matris yok: {xlsx}. Önce `matrix.py init` çalıştırın.")
        return 1
    refs = _references()
    wb = load_workbook(xlsx)
    ws = wb["Matris"]
    header = [c.value for c in ws[1]]
    problems = []
    if header != [c for c, _ in COLUMNS]:
        problems.append(f"Başlık satırı beklenen sütunlarla aynı değil: {header}")
    for r in range(2, ws.max_row + 1):
        vals = dict(zip(header, [c.value for c in ws[r]], strict=False))
        rid = vals.get("Kaynak ID")
        if not rid:
            continue
        ref = refs.get(rid)
        if not ref:
            problems.append(f"Satır {r}: {rid} references.json'da yok")
            continue
        if vals.get("Doğrulama durumu") != ref["status"]:
            problems.append(
                f"Satır {r}: durum {vals.get('Doğrulama durumu')} ≠ references.json {ref['status']}"
            )
        if (vals.get("DOI") or None) != (ref.get("doi") or None):
            problems.append(f"Satır {r}: DOI references.json ile farklı")
        if str(vals.get("Yıl")) != str(ref["year"]):
            problems.append(f"Satır {r}: yıl farklı")
        for col in REQUIRED_TEXT:
            if not vals.get(col):
                problems.append(f"Satır {r}: '{col}' boş")
    print("\n".join(problems) if problems else f"{ws.max_row - 1} satır: sorun yok")
    return 1 if problems else 0


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if config.help_requested(__doc__):
        return 0
    cmd = sys.argv[1] if len(sys.argv) > 1 else "validate"
    if cmd == "init":
        init()
    elif cmd == "add":
        if len(sys.argv) < 3:
            print("Kullanım: matrix.py add <row.json>")
            return 2
        add(Path(sys.argv[2]))
    elif cmd == "validate":
        return validate()
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
