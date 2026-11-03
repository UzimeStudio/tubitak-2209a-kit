---
name: data-analysis
description: Ölçüm/etiket/anket verisini yeniden üretilebilir Python betikleriyle analiz eder (Wilson güven aralığı, chi-square/Fisher, McNemar, Holm, Cohen's kappa, precision/recall/F1 vb.). Veri temizleme, özet istatistik, hipotez testi veya sonuç tablosu üretmek, "veriyi analiz et", "güven aralığı hesapla", "hangi test" istendiğinde kullan. Sentetik veri daima "SENTETİK" işaretlenir ve rapora sonuç olarak girmez. Grafik çizimi scientific-visualization'ın işidir.
---

# data-analysis

## Görev
Ham veriye dokunmadan, her adımı betik ve kayıtla izlenebilir analiz yapmak.

## Ne zaman
Veri temizlenirken, özet istatistik/hipotez testi gerektiğinde, sonuç tablosu üretilirken.

## Veri düzeni
Yollar `tools/config.py` içindeki `PATHS`'ten okunur.

| PATHS anahtarı | İçerik | Kural |
| --- | --- | --- |
| `data/raw/` | Kaynaktan gelen veri | Salt okunur; asla değiştirilmez |
| `data/processed/` | Betikle türetilen veri | Betik yeniden çalışınca aynı sonuç |
| `analysis/scripts/` | Analiz betikleri | Seed sabit, girdi/çıktı yolu başlıkta |
| `analysis/outputs/` | JSON/CSV sonuçlar | Betik adıyla eşleşir |
| `data/data-dictionary.md` | Değişken tanımları | Her yeni değişken buraya |
| `analysis/analysis-log.md` | Analiz kaydı | Her çalıştırma bir satır |

## Prosedür
1. Değişkenler `data/data-dictionary.md`'de tanımlıdır; yoksa önce tanımlanır.
2. İstatistik fonksiyonları `tools/stats.py`'den alınır (gerçek adlar):
   | Fonksiyon | Kullanım |
   | --- | --- |
   | `wilson_ci(successes, n)` | Oran ve %95 Wilson güven aralığı |
   | `worst_case_margin(n)` | p=0,5 için en kötü durum güven aralığı yarı genişliği (örneklem büyüklüğü planında) |
   | `association_test(table)` | r×c çapraz tabloda kategorik ilişki testi (chi-square; seyrek 2×2'de Fisher exact) |
   | `mcnemar_test(both_yes, only_old, only_new, both_no)` | Eşli ikili ölçüm değişimi; az tutarsız çiftte exact |
   | `holm(pvalues)` | Çoklu karşılaştırma (Holm) düzeltmesi |
   | `cohen_kappa(labels_a, labels_b)` | Etiketçi uyumu + ham uyum + %95 aralık |
   | `prf1(tp, fp, fn)` | Precision, recall, F1 + Wilson güven aralıkları |
3. Betik `uv run python analysis/scripts/<betik>.py` ile çalıştırılır; yollar `config.PATHS`'ten alınır. Import için çalışma dizinine bağlı `sys.path.insert(0, "tools")` değil, betiğin yerine göre kökten mutlak yol kullanılır:
   ```python
   import sys
   from pathlib import Path
   ROOT = Path(__file__).resolve().parents[2]   # analysis/scripts/<betik>.py → proje kökü
   sys.path.insert(0, str(ROOT / "tools"))
   import config, stats
   ```
4. Çıktı klasörü yazmadan önce oluşturulur: `Path(config.PATHS["analysis_outputs"]).mkdir(parents=True, exist_ok=True)` (ilgili PATHS anahtarıyla).
5. `analysis/analysis-log.md`'ye tarih, betik, girdi, çıktı, sonuç özeti ve **veri türü (sentetik/gerçek)** yazılır.
6. Yeni bir yöntem eklenirse elle hesapla karşılaştırma testi yazılır (örnek betikteki `manual_wilson`, `manual_kappa` gibi).

## Sentetik veri ilkesi
- Sentetik veri yalnız altyapı testinde kullanılır; her satırda bir `synthetic=True` işareti bulunur ve betik bunu `assert` ile doğrular.
- Sentetik veriyle üretilen hiçbir sayı rapora sonuç olarak girmez. JSON çıktısının başına `"UYARI": "SENTETİK VERİ — gerçek ölçüm sonucu değildir"` yazılır.
- Örnek, konu-bağımsız sentetik betik `templates/` altına konur; gerçek değer üretmez. Örnek sahte değerler `report/mock-data.json` içindedir (yalnız şablon testi).

## Raporlama kuralları
- p değeri tek başına verilmez; etki büyüklüğü/oran ve güven aralığı birlikte.
- "Ölçülemedi" sayısı ayrı satırda.
- Eşik sağlanmadıysa gerçek değer yazılır, hedef yazılmaz.

## Hata durumları
- Ham veri değişmiş görünüyorsa analiz durur; kullanıcıya bildirilir.
- Beklenen hücre <5: yöntem notu (exact test) sonuçta görünür (`association_test` `note` alanına yazar).

## Kalite kontrol
- [ ] Betik iki kez çalıştırıldı, sonuç aynı.
- [ ] Ham veri karması (hash) değişmedi.
- [ ] Analiz kaydı ve veri türü işareti güncel.
- [ ] Sentetik hiçbir sayı sonuç olarak rapora girmedi.
