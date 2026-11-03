---
name: methodology-review
description: Araştırma tasarımı, örneklem, değişkenler, istatistik/analiz yöntemi, geçerlik ve etik kurul ile araştırma soruları/hedefler arasındaki uyumu denetler; her hedefin ölçülebilir başarı ölçütü ve eşik gerekçesi olduğunu kontrol eder. Yöntem bölümü yazılırken veya değiştirilirken, "yöntem tutarlı mı", "örneklem yeterli mi", "hangi test", "başarı ölçütü ne olmalı", "güç analizi", "etik kurul gerekli mi" sorularında kullan. Analizi çalıştırmak data-analysis'in işidir.
---

# methodology-review

## Görev
Yöntemin hedeflere ulaşmaya elverişli olduğunu ve iddiaların yöntemle sınırlı kaldığını göstermek. Her hedefi ölçülebilir bir başarı ölçütüne ve gerekçeli bir eşiğe bağlamak.

## Ne zaman
Yöntem/çalışma takvimi bölümü yazılırken veya değiştirilirken; başarı ölçütü ya da eşik belirlenirken; "yöntem tutarlı mı" sorulduğunda.

## Girdi → Çıktı
- Girdi: yöntem metni (önerinin yöntem bölümü, başvuru §2, araştırma planı, sonuç raporu).
- Çıktı: bulgu listesi (konum, sorun, öneri, öncelik).

## Proje türüne göre tasarım soruları
Önce proje türünü belirle; her tür kendi asgari denetimini getirir. Birden çok tür bir arada olabilir (ör. yazılım + veri analizi).

| Tür | Sorulacaklar |
| --- | --- |
| Yazılım/sistem | Ne ölçülüyor (doğruluk, başarım, kullanılabilirlik)? Karşılaştırma temeli (baseline) var mı? Kör/eşli değerlendirme? Yeniden üretilebilirlik (seed, sürüm, veri)? |
| Deney | Bağımsız/bağımlı değişken, kontrol grubu, rastgele atama, tekrar sayısı, karıştırıcı değişken, körleme |
| Anket | Evren ve örnekleme çerçevesi, örneklem büyüklüğü / güç analizi, ölçek geçerlik-güvenirliği, pilot/ön test, yanıt yanlılığı, **etik kurul / aydınlatılmış onam** |
| Saha | Örneklem temsili, erişim/izin, ölçüm standartlaştırması, gözlemci etkisi, eksik veri planı, **etik kurul gerekliliği** |
| Veri analizi | Veri kaynağı ve kalitesi, birim, eksik veri, uygun test seçimi, çoklu karşılaştırma düzeltmesi, etki büyüklüğü + güven aralığı |
| Tasarım/üretim | Gereksinim–ölçüt eşlemesi, prototip değerlendirme yöntemi, kullanıcı testi, kabul ölçütleri |

## Genel denetim listesi
| Konu | Kontrol |
| --- | --- |
| Hedef ↔ yöntem | Her araştırma sorusu/hedef bir yöntem adımına bağlı mı? Yöntemsiz hedef kalmadı mı? |
| Hedef ↔ başarı ölçütü | Her hedefin **ölçülebilir** bir başarı ölçütü var mı (sayı, oran, eşik + birim)? "İyileştirmek" gibi belirsiz ifade ölçüye çevrildi mi? |
| Eşik gerekçesi | Her eşik neden o değerde? Gerekçe literatüre, pilota veya kabul ölçütüne dayanıyor mu, yoksa keyfi mi? Keyfi eşik bulgu olarak işaretlenir |
| Hipotez ↔ test | Her hipotez uygun bir istatistik/değerlendirme yöntemine (hipotez testi) bağlı mı? Nedensellik dili yalnız tasarım destekliyorsa kullanılıyor mu? |
| Örneklem | Evren → hedef → ulaşılan zinciri; katmanlar, kayıp gerekçeleri, temsil sınırı belirtilmiş mi? |
| Güç/kesinlik | Örneklem büyüklüğü, güç analizi veya kesinlik (yarı genişlik) ile gerekçeli mi? Pilota bırakıldıysa sonuçta yapılıp yapılmadığı yazılacak |
| Çoklu karşılaştırma | Birden çok test varsa düzeltme (ör. Holm) planlandı mı? |
| Ölçülemedi | "Ölçülemedi" ile "gözlenmedi" ayrı mı raporlanıyor? |
| Etik | Proje türü etik kurul / muafiyet değerlendirmesi gerektiriyor mu (insan/hayvan deneği, kişisel veri)? Gereklilik açıkça belirtilmiş mi? Ham veri saklama/anonimleştirme planı var mı? |
| Takvim | Yöntem adımları iş paketlerine bağlı; literatür tarama ve sonuç raporu çalışma takvimi adımı olarak yazılmaz (rules dosyası `work_plan.forbidden_steps`) |

## Prosedür
1. Proje türünü belirle; ilgili tür tablosunu ve genel listeyi birlikte uygula.
2. Metni satır satır oku; her bulgu için kaynak belge ve satır ver.
3. Sayısal iddialar (ör. kesinlik, güç analizi) `tools/stats.py` ile yeniden hesaplanır.
4. Her hedef için başarı ölçütü ve eşik gerekçesini tabloya yaz; eksikse "başarı ölçütü eksik" / "eşik gerekçesiz" bulgusu üret.
5. Yöntem değişikliği öneriliyorsa araştırma planı/gereksinim belgesiyle çelişip çelişmediği belirtilir; belgeler onaysız değiştirilmez (`logs/decisions.md`).

## Hata durumları
- Bir hedefin yöntemi yoksa: "yöntem eksik" bulgusu; hedef silinmez.
- Seyrek hücre: chi-square yerine exact/permütasyon testi önerilir.
- Proje türü belirsizse: önce türü sor, varsayma.

## Kalite kontrol
- [ ] Her hedef bir yönteme ve ölçülebilir başarı ölçütüne bağlandı.
- [ ] Her eşiğin gerekçesi yazılı; keyfi eşik kalmadı.
- [ ] Proje türüne uygun tasarım/etik soruları soruldu.
- [ ] Hiçbir planlanan eşik sonuç gibi yazılmadı; sınırlılıklar gizlenmedi.
