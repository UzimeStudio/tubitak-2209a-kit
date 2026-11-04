---
name: budget-timeline
description: 2209-A bütçesini ve Çalışma Takvimini (iş paketleri) çağrı kurallarına uygun, uydurmasız ve yöntemle bağlı kurar ve denetler. "Bütçe hazırla", "iş paketi / çalışma takvimi yaz", "gider kalemleri uygun mu", "bütçe-takvim kontrolü" isteğinde kullan.
---

# budget-timeline

## Görev
Bütçe kalemlerini ve Çalışma Takvimini çağrının izin verdiği biçimde, her tutarı gerçek bir kaynağa, her iş adımını yönteme bağlayarak kurmak. Tutar uydurmaz, iş adımı şişirmez.

## Ne zaman
- Bütçe veya Çalışma Takvimi (3.1) yazılırken ya da denetlenirken.

## Girdi → Çıktı
- Girdi: proje yöntemi, team, timeline; call rules.
- Çıktı: uygun gider kalemleri + gerekçeli tutarlar; iş paketi tablosu; uygun/değil denetim tablosu.

## Bütçe kuralları (rules dosyasından; sabit yazma)
- İzinli kalemler: `budget.items` (2026: Makine Teçhizat, Hizmet Alımı, Sarf Malzemesi, Ulaşım). Başka kalem adı eklenmez.
- Bütçe dışı kalemler: `budget.excluded_items` (2026: konferans katılım, yayın, patent, konaklama, gündelik) bütçeye yazılmaz.
- IBAN: `budget.iban` — başvuruda girilen IBAN proje yürütücüsü öğrenciye ait olmalıdır; bu banka bilgisi ekip tarafından girilir, uydurulmaz.
- Üst sınır: `budget.max_tl` (2026: 12000). Toplam sıfır da kaydedilebilir ("Destek İstemiyorum").
- Her tutar gerçek bir fiyat teklifine (quote) veya belgelenebilir kaynağa dayanır; teklif yoksa tutar `TBD` kalır ve `logs/open-questions.md`'ye yazılır.
- Her kalemin gerekçesi yöntemdeki bir ihtiyaca bağlanır (hangi iş adımı için, ne işe yarar). Yöntemle bağı kurulamayan kalem yazılmaz.
- Şişirme, yuvarlak dolgu tutar, uydurma teklif yasaktır.
- Gider kalemleri yalnız TYBS bütçe ekranında girilir; başvuru kapandıktan sonra değişmez (`budget.note`).

## Çalışma Takvimi kuralları (`work_plan`)
- Süre `duration.max_months`'u (2026: 12) aşmaz; en az `work_plan.min_steps` iş adımı.
- Tablo sütunları `work_plan.columns`: Proje Süresi (Ay) · Faaliyetler · Kim(ler) Tarafından Gerçekleştirileceği · Başarı Ölçütü ve Katkısı.
- Her iş adımı: ay aralığı, sorumlu kişi(ler), ölçülebilir başarı ölçütü taşır. Başarı ölçütü katkıları toplamı `work_plan.contribution_total` (2026: 100) olur.
- Yasak iş adımları (`work_plan.forbidden_steps`): literatür tarama, sonuç raporu, sonuçların paylaşımı, malzeme alımı ayrı iş adımı olamaz.

## Hakemin bütçe ve takvimde aradığı (`project/writing-guide.md`)

- Her kalem bir iş paketine bağlı ve gerekçeli. "Sarf: 5.000 TL" yetmez; neyin, kaç adet, hangi iş paketi için alındığı yazılır.
- Fiyatlar KDV dahil, gerçek teklif veya proformaya dayalı. Döviz bağlı alımda kur artışı payı düşünülür.
- Burs, maaş veya ücret izlenimi veren kalem yoktur. Bütçe dışı kalemler rules `budget.excluded_items`'tadır.
- Demirbaş alınacaksa proje sonunda envantere kaydedilir (rules `monitoring`).
- Her iş paketinin başarı ölçütü sayısaldır (adet, oran, eşik, tarih) ve katkı ağırlığı vardır. `tools/check_writing.py` ölçülemeyen ölçütü uyarır.
- Takvim ekibin ve altyapının kaldırabileceği kadardır; süre gereğinden uzun tutulmaz.

## Prosedür
1. Yöntem okunur; her bütçe kalemi bir iş adımına ve ihtiyaca bağlanır. Fiyat teklifi yoksa tutar `TBD`.
2. İş paketleri ay aralığı, sorumlu, ölçülebilir başarı ölçütü ve katkı payıyla yazılır; katkı toplamı kontrol edilir.
3. Biçim ve toplam denetimi çalıştırılır:
   ```bash
   uv run python tools/check_application.py --tybs
   ```
   Katkı toplamı, süre, iş adımı sayısı ve yasak adımlar bu çıktıdan doğrulanır.
4. Belgeler arası (bütçe toplamı ↔ `project.json` `budget.total_tl`, takvim süresi ↔ `timeline.duration_months`) tutarlılık:
   ```bash
   uv run python tools/check_consistency.py
   ```
5. Bulunan boşluklar `logs/open-questions.md`'ye, verilen kararlar `logs/decisions.md`'ye yazılır.

## Hata durumları
- Kalem adı rules `budget.items` listesinde yoksa ya da `budget.excluded_items`'ta ise: yazılmaz, kullanıcıya bildirilir.
- Katkı toplamı 100 değilse: eksik/fazla iş adımı payı kullanıcıya gösterilir.
- Fiyat teklifi yoksa: tutar uydurulmaz, `TBD` kalır.

## Kalite kontrol
- [ ] Her kalem izinli listede (`budget.items`), hiçbiri `budget.excluded_items`'ta değil ve bir iş adımına/yönteme bağlı.
- [ ] IBAN'ın yürütücü öğrenciye ait olması gerektiği (`budget.iban`) ekibe hatırlatıldı.
- [ ] Her tutar gerçek teklife dayanıyor veya `TBD`.
- [ ] Her iş adımı: ay aralığı + sorumlu + ölçülebilir başarı ölçütü.
- [ ] Katkı toplamı rules değerine eşit; yasak adım yok.
- [ ] `check_consistency.py` bütçe/süre için tutarsızlık bildirmiyor.
