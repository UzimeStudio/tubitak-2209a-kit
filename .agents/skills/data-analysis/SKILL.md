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
2. Kitte hazır gelen istatistik fonksiyonları `tools/stats.py`'den alınır (gerçek adlar):
   | Fonksiyon | Kullanım |
   | --- | --- |
   | `wilson_ci(successes, n)` | Oran ve %95 Wilson güven aralığı |
   | `worst_case_margin(n)` | p=0,5 için en kötü durum güven aralığı yarı genişliği (örneklem büyüklüğü planında) |
   | `association_test(table)` | r×c çapraz tabloda kategorik ilişki (ki-kare; seyrek 2×2'de Fisher exact) |
   | `mcnemar_test(both_yes, only_a, only_b, both_no)` | Aynı birimlerde eşli iki koşul/yöntem; az tutarsız çiftte exact |
   | `holm(pvalues)` | Çoklu karşılaştırma (Holm) düzeltmesi |
   | `cohen_kappa(labels_a, labels_b)` | Değerlendirici/kodlayıcı uyumu + ham uyum + %95 aralık |
   | `prf1(tp, fp, fn)` | Precision, recall, F1 + Wilson güven aralıkları |

   Kitte hazır fonksiyonu olmayan yaygın yöntemler doğrudan `scipy.stats` / `statsmodels` ile uygulanır (uydurma fonksiyon adı kullanma; betikte gerçek çağrıyı yaz):
   | Yöntem | Ne zaman | Nasıl |
   | --- | --- | --- |
   | Bağımsız iki grup karşılaştırması | İki ayrı grubun sürekli ölçümü; normallik varsa t-testi, yoksa Mann-Whitney U | `scipy.stats` ile |
   | Eşli iki ölçüm (sürekli) | Aynı birimlerin iki ölçümü | `scipy.stats` ile |
   | İkiden çok grup | Üç ve daha fazla grup; normallik varsa ANOVA, yoksa Kruskal-Wallis | `scipy.stats` / `statsmodels` ile |
   | Ki-kare / Fisher | Kategorik değişkenler arası ilişki | `association_test` (kitte var) |
   | Korelasyon / regresyon | İki sürekli değişken ilişkisi ya da model kurma | `scipy.stats` / `statsmodels` ile |
   | Cronbach alfa | Ölçek/anket iç tutarlılığı | `scipy.stats` / `statsmodels` ile (ya da elle hesapla) |

   Yöntem seçimi veri türü ve varsayımlara (normallik, varyans homojenliği, eşlilik) göre yapılır; seçilen varsayım testi de betikte kayıtlanır.
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
6. Yeni bir yöntem (kitte hazır olmayan) eklenirse, elle hesapla kütüphane sonucunu karşılaştıran bir test yazılır — `tests/test_stats.py`'deki Wilson/kappa testleri örnek alınır.

## Sentetik veri ilkesi
- Sentetik veri yalnız altyapı/akış testinde kullanılır; her satırda bir `synthetic=True` işareti bulunur ve betik bunu `assert` ile doğrular.
- Sentetik veriyle üretilen hiçbir sayı rapora sonuç olarak girmez. JSON çıktısının başına `"UYARI": "SENTETİK VERİ — gerçek ölçüm sonucu değildir"` yazılır.
- Gerçek sonuç gelene kadar rapordaki yer tutucu/sahte değerler ayrı tutulur; bunların listesi `report/mock-data.json` içindedir ve `tools/check_report.py` bu değerlerin son rapora sızmadığını denetler (veri demosu değil, yer tutucu bekçisidir).

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
