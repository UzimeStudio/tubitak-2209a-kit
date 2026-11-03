---
name: tybs-application-check
description: 2209-A başvuru metnini TYBS'ye aktarmadan önce çağrının biçim kurallarına göre denetler (Özet kelime sınırı, bölüm karakter alt sınırları, Çalışma Takvimi katkı toplamı, yasak iş adımları, DOI, anahtar kelime sayısı) ve TYBS'ye kopyalama adımlarını verir. Başvuru son günü öncesinde ve başvuru metni her değiştiğinde; "TYBS kontrolü", "başvuru biçim denetimi", "TYBS'ye nasıl kopyalarım" isteğinde kullan.
---

# tybs-application-check

## Görev
Başvurunun biçimsel nedenle sorun yaşamasını önlemek. İçerik kararı vermez.

## Ne zaman
- Başvuru metni TYBS'ye girilmeden önce ve metin her değiştiğinde.

## Girdi → Çıktı
- Girdi: TYBS başvuru metni (`config.document("tybs")`).
- Çıktı: kural-kural uygun/değil tablosu; TYBS'ye kopyalama adımları.

## Kurallar (hepsi rules dosyasından; sabit yazma)
| Kural | rules alanı |
| --- | --- |
| Özet kelime aralığı (2026: 25–450) | `abstract.min_words/max_words`, kapsam `abstract.scope` |
| Başlık karakter üst sınırı (2026: 495) | `title.max_chars` |
| Anahtar kelime sayısı ve separator (2026: 3–5, virgül) | `keywords` |
| Bölüm karakter alt sınırı (2026: ≥350) | `section_min_chars` |
| Çalışma Takvimi: süre, iş adımı sayısı, katkı toplamı (2026: ≤12 ay, ≥1, 100) | `duration`, `work_plan` |
| Yasak iş adımları | `work_plan.forbidden_steps` |
| Kaynakça: karakter üst sınırı, DOI zorunlu, tümüne atıf | `references` |
| Görsel extensions | `images.extensions` |
| Marka/firma öne çıkarma yasağı | `brand_ban` |
| Öneri dili Türkçe + TÜBİTAK formatı (aksi hâlde ön elemede elenir) | `language` |
| ÜYZ beyanının yeri (rehber ayrılmış bölüm ister; ekranda görülmezse BİDEB/danışmana sorulur) | `ai_disclosure.note` |

## Prosedür
1. Biçim denetimi çalıştırılır; sonuç kullanıcıya tablo olarak verilir:
   ```bash
   uv run python tools/check_application.py --tybs
   ```
2. Sınıra yakın değerler (Özet üst sınıra yakınsa, bölüm alt sınıra yakınsa) elle doğrulanır; TYBS'nin sayım yöntemi bilinmiyor.
3. Markdown → TYBS hazırlığı: bağlantılar düz metin atıfa çevrilir (`[Soyad (2023)](https://doi.org/…)` → `Soyad (2023)`); uyarı blokları normal paragraf olur; tablolar TYBS tablo aracıyla yeniden kurulur; 3.1/3.3/4 TYBS'de tablo veya sabit kategori biçimindedir.
4. Kaynakça satırları üretilir ve TYBS Kaynaklar alanına tek tek girilir:
   ```bash
   uv run python tools/bibkit.py list
   ```
   Kaynak kaydında olmayan bir DOI kullanıcıya önce bildirilir.
5. Öneri Türkçe ve TÜBİTAK formatında mı doğrulanır (rules `language`); Türkçe/format dışı metin ön elemede eleneceği için uyarılır.
6. ÜYZ beyanı için `ai-research-compliance`. ÜYZ Rehberi beyanı sistemdeki ayrılmış bölümde ister (rules `ai_disclosure.note`); 2026 ekranında bu alan görülmediyse yeri BİDEB'e/danışmana sorulur, uydurulmaz.
7. Önizleme ("Araştırma Önerisini Önizle") ekip tarafından yapılır; bu skill TYBS'ye giriş yapmaz, form göndermez.

## Hata durumları
- Bölüm başlıkları değişirse betik bölüm bulamaz; başvuru metnindeki başlıklar rules `section_min_chars.sections` ile eşleştirilir.
- Çalışma Takvimi katkı toplamı 0 çıkarsa tablo başlık adları (`work_plan.columns`) kontrol edilir.

## Kalite kontrol
- [ ] Betik çıktısındaki tüm kurallar "uygun".
- [ ] Ekip/danışman bilgisi gerçek bilgiyle girildi (taslakta `TBD` kalmadı).
- [ ] Başvuru önizlemesi ekip tarafından yapıldı.
