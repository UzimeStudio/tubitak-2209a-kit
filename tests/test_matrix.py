"""matrix.py testleri: init/add/validate ve references.json eşleşmesi."""

from __future__ import annotations

import json

import matrix
from openpyxl import load_workbook


def _ref(rid="a", **over):
    base = {
        "id": rid,
        "type": "article",
        "authors": ["Yılmaz, A."],
        "year": 2020,
        "title": "Başlık",
        "venue": "Dergi",
        "doi": "10.1/x",
        "status": "VERIFIED",
    }
    base.update(over)
    return base


def _row(rid="a", **over):
    base = {
        "Kaynak ID": rid,
        "Yazar": "Yılmaz, A.",
        "Yıl": 2020,
        "Çalışmanın başlığı": "Başlık",
        "Araştırma amacı": "amaç",
        "Yöntem": "yöntem",
        "Veri/örneklem": "veri",
        "Temel bulgular": "bulgu",
        "Sınırlılıklar": "sınır",
        "Projeyle ilişkisi": "ilişki",
        "DOI": "10.1/x",
        "Doğrulama durumu": "VERIFIED",
        "Okunan kaynak": "pdf",
        "Satırı hazırlayan / tarih": "A / 2026-11-03",
    }
    base.update(over)
    return base


def test_init_matris_olusturur(tmp_kit):
    matrix.init()
    xlsx = tmp_kit.paths["matrix_xlsx"]
    assert xlsx.exists()
    ws = load_workbook(xlsx)["Matris"]
    assert [c.value for c in ws[1]] == [c for c, _ in matrix.COLUMNS]


def test_init_var_olani_bozmaz(tmp_kit, capsys):
    matrix.init()
    matrix.init()
    assert "Zaten var" in capsys.readouterr().out


def test_add_ve_validate_temiz(tmp_kit):
    tmp_kit.write_references([_ref()])
    matrix.init()
    row_file = tmp_kit.root / "row.json"
    row_file.write_text(json.dumps(_row(), ensure_ascii=False), encoding="utf-8")
    matrix.add(row_file)
    assert matrix.validate() == 0


def test_validate_eksik_kaynak(tmp_kit):
    tmp_kit.write_references([])  # references.json boş
    matrix.init()
    row_file = tmp_kit.root / "row.json"
    row_file.write_text(json.dumps(_row(rid="yok"), ensure_ascii=False), encoding="utf-8")
    matrix.add(row_file)
    assert matrix.validate() == 1


def test_validate_durum_uyusmazligi(tmp_kit):
    tmp_kit.write_references([_ref(status="PARTIAL")])
    matrix.init()
    row_file = tmp_kit.root / "row.json"
    row_file.write_text(
        json.dumps(_row(**{"Doğrulama durumu": "VERIFIED"}), ensure_ascii=False), encoding="utf-8"
    )
    matrix.add(row_file)
    assert matrix.validate() == 1


def test_validate_matris_yoksa_cokmez(tmp_kit, capsys):
    assert matrix.validate() == 1
    assert "Matris yok" in capsys.readouterr().out


def test_add_bos_zorunlu_alan_yakalanir(tmp_kit):
    tmp_kit.write_references([_ref()])
    matrix.init()
    row_file = tmp_kit.root / "row.json"
    row_file.write_text(
        json.dumps(_row(Yöntem=""), ensure_ascii=False), encoding="utf-8"
    )
    matrix.add(row_file)
    assert matrix.validate() == 1
