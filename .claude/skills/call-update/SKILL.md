---
name: call-update
description: Yeni bir 2209-A çağrı yılında kuralları resmî TÜBİTAK belgelerinden yeniden doğrulayıp yeni rules dosyası (rules/2209a-<yıl>.json) oluşturur ve projeyi ona bağlar. "Yeni çağrı çıktı", "kuralları güncelle", "çağrı yılını değiştir", "2209-A <yıl> kuralları" isteğinde kullan.
---

# call-update

## Görev
Yeni çağrı yılının biçim kurallarını (kelime/karakter sınırları, süre, bütçe üst sınırı, timeline, yasak adımlar) resmî kaynaktan doğrulayıp yeni bir rules dosyası üretmek. Hiçbir değer eski dosyadan körlemesine taşınmaz.

## Ne zaman
- TÜBİTAK yeni bir 2209-A çağrısı açtığında.
- Resmî belgelerin değişip değişmediği kontrol edilmek istendiğinde.

## Girdi → Çıktı
- Girdi: mevcut `rules/2209a-<eski>.json`, resmî TÜBİTAK belgeleri.
- Çıktı: yeni `rules/2209a-<yıl>.json` (her değer `source` kimliğiyle); güncel `project.json` `call.rules_file`; güncel `project/tubitak-sources.md`.

## Ağ kuralı
Yalnız `tubitak.gov.tr` alan adından belge indirilir/okunur. Başka kaynaktan kural alınmaz.

## Prosedür
1. Resmî belgelerde değişiklik var mı bak: mevcut rules dosyasındaki `sources[].url` ve `sha256_16` ile karşılaştır:
   ```bash
   uv run python tools/call_watch.py
   ```
2. Değişen veya yeni belgeler (çağrı duyurusu, başvuru içeriği bilgi notu, ÜYZ rehberi, program sayfası) okunur.
3. Eski rules dosyası yeni ada kopyalanır: `rules/2209a-<yıl>.json`. İçinde `year`, `checked_on`, `call_name` güncellenir.
4. Her değer tek tek belgeden yeniden doğrulanır (Özet kelime aralığı, başlık karakteri, bölüm alt sınırı, süre, bütçe üst sınırı ve kalemler, timeline tarihleri, yasak adımlar, references karakter sınırı, keywords sayısı). Aşağıdaki bloklar da her yıl aynı şekilde yeniden doğrulanır:
   - `eligibility` — tek başvuru/devam eden proje kısıtı, öğrenci türü (Açık Öğretim/Hazırlık hariç), ARBİS kaydı, önceki destek yasağı (T02 §4.1).
   - `language` — önerinin Türkçe ve TÜBİTAK formatında olması, ön eleme (T02 §4.2.1, §5.1.2).
   - `ethics` — etik kurul onay/muafiyet belgesi yükümlülüğü (T02 §5.3.1).
   - `evaluation` — ölçüt ağırlıkları (`criteria_weights`) ve özel gereksinimli birey +1 puan (T02 §5.2.1, §4.2.3, §5.2.6).
   - `budget.excluded_items` ve `budget.iban` — bütçe dışı kalemler ve IBAN koşulu (T02 §2.1.2, T01).
   - `withdrawal` — başvuru geri çekme süresi (T02 §4.3.5).
   - `acknowledgement` — TÜBİTAK desteği beyanı ve logo zorunluluğu (T02 §6.6, T01).
   TYBS ekranına dayanan ve resmî belgede karşılığı olmayan değerlerin (`title.max_chars`, `keywords`, `references.max_chars`) `source`'u "TYBS ekranı (resmî belgede yok)" olarak kalır. Her alanın `source` değeri doğrulandığı belge kimliğine (ör. `T02 §2.2`) güncellenir. Doğrulanamayan değer taşınmaz; `null` bırakılır ve `logs/open-questions.md`'ye yazılır.
5. `sources[]` listesindeki her belgenin güncel `url` ve `sha256_16` değeri yazılır.
6. Proje yeni dosyaya bağlanır: `project.json` `call.rules_file` = `2209a-<yıl>.json`.
7. `project/tubitak-sources.md` güncel belge sürümleri, erişim tarihi ve SHA değerleriyle güncellenir.
8. Doğrulama:
   ```bash
   uv run python tools/config.py
   uv run python tools/check_application.py --tybs
   ```

## Hata durumları
- İndirme başarısızsa veya belge `tubitak.gov.tr` dışındaysa: durur, kullanıcıya bildirir, eski dosyayı değiştirmez.
- Bir değer resmî belgede bulunamıyorsa: uydurulmaz, `null` + open-question.

## Kalite kontrol
- [ ] Yeni rules dosyasındaki her değerin `source` alanı güncel bir belge kimliğine dayanıyor (TYBS ekranına dayananlar "TYBS ekranı (resmî belgede yok)" olarak işaretli).
- [ ] `eligibility`, `language`, `ethics`, `evaluation`, `budget.excluded_items`/`budget.iban`, `withdrawal`, `acknowledgement` blokları da madde numarasıyla yeniden doğrulandı.
- [ ] Her indirilen belgenin SHA'sı `sources` listesine yazıldı.
- [ ] `project.json` yeni rules dosyasını gösteriyor; `config.py` hatasız okuyor.
- [ ] Yalnız tubitak.gov.tr'den indirildi.
