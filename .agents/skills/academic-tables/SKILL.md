---
name: academic-tables
description: Analiz çıktılarından düzenlenebilir Word tabloları üretir (başlık üstte, SEQ numaralı, başlık satırı tekrarlı, satır bölünmez, sayılar sağa yaslı, Türkçe ondalık). "Tablo oluştur", "sonuçları tabloya dök", "şekil/tablo ekle" isteklerinde kullan. Belgenin bütün olarak üretimi docx-engineering'in işidir.
---

# academic-tables

## Görev
Tabloyu resim değil, düzenlenebilir Word tablosu olarak ve metin alanına sığacak biçimde üretmek.

## Ne zaman
Sonuçlar, karşılaştırmalar veya özet değerler bir Word tablosuna dökülecekse.

## Girdi → Çıktı
- Girdi: pandas DataFrame (`data/processed/` veya `analysis/outputs/`; yollar `config.PATHS`'ten).
- Çıktı: DOCX içinde tablo; aynı tablonun CSV'si `tables/<ad>.csv`.

## Prosedür
1. Tablo önce CSV olarak kaydedilir: `df.to_csv(Path(config.PATHS["tables"]) / "<ad>.csv", index=False)`. Çıktı klasörü yoksa önce oluşturulur: `Path(config.PATHS["tables"]).mkdir(parents=True, exist_ok=True)`.
2. Sütun adları Türkçe ve birimli ("Oran", "Alt %95", "Süre (s)").
3. Word'e ekleme (import kökten mutlak yolla; çalışma dizinine bağlı `sys.path.insert(0, "tools")` kullanılmaz):
   ```python
   import sys
   from pathlib import Path
   ROOT = Path(__file__).resolve().parents[1]
   sys.path.insert(0, str(ROOT / "tools"))
   from docxkit import SectionWriter

   # SectionWriter.SECTIONS anahtarları: intro | work | result | outputs | expenses
   w = SectionWriter.at_section(doc, "work")
   w.table(df, "Başlık metni", col_widths_cm=[3.2, 1.8, 2.4, 2.6, 3.0])
   ```
   `SectionWriter.table` şunları yapar: başlığı tablonun üstüne yazar (`Tablo N.` SEQ alanı), başlığı tabloya bağlar (keep_with_next), başlık satırını sayfa geçişinde tekrarlar, satırın bölünmesini engeller, ince kenarlık, Arial, sayıları sağa yaslar, ondalığı virgülle yazar.
4. Genişlik toplamı metin alanını (A4, 2,5 cm kenar boşluğu → ~16 cm) aşarsa fonksiyon hata verir. Çözüm: sütun azalt, kısalt veya tabloyu böl. Yatay (landscape) sayfa son çaredir.
5. Metinde "Tablo N" atfı tablodan önce yazılır.
6. Uzun tablo (>1 sayfa) eke alınır; metinde özet tablo kalır.

## Hata durumları
- Birleştirilmiş hücre gerekiyorsa python-docx `cell.merge` kullanılır; sonra PDF'te görsel kontrol yapılır.
- Ondalık basamak sütuna göre farklıysa değerler sütun bazında önceden metne çevrilir.

## Kalite kontrol
- [ ] `tools/check_report.py`: tablo numarası ardışık ve atıflı.
- [ ] PDF sayfasında tablo taşmıyor (`tools/pdf_check.py` + görsel).
- [ ] CSV ile Word tablosu aynı sayıları gösteriyor.
