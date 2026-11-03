---
name: idea-refinement
description: >-
  Kullanıcının ham fikrini ekiple birlikte düşünerek araştırma sorusu,
  hipotez, özgünlük, yöntem taslağı, ölçülebilir başarı ölçütü ve
  yapılabilirliğe dönüştürür. Tetik: "fikrim var ama netleşmedi", "bunu
  nasıl araştırma sorusuna çeviririm", "hipotezim ne olmalı", "bu özgün mü",
  "proje fikrimi tartışalım", "hangi fikir daha iyi". Claude Code ve Codex'te aynı.
---

# idea-refinement — ortak düşünme

## Görev
Kullanıcının ham fikrini, birlikte düşünerek araştırılabilir ve 2209-A'ya uygun
bir çerçeveye oturt. Fikri sen dayatma; ekibin kendi fikrini netleştirmesine
rehberlik et. Sahiplik ekiptedir.

## Ne zaman
Fikir henüz ham/belirsizken, ya da birkaç fikir arasından seçim gerektiğinde.
Fikir netleşip özgünlük boşluğu kanıtlanacaksa `academic-research`'e geç.

## Girdi → Çıktı
- Girdi: kullanıcının kendi cümleleriyle anlattığı ham fikir(ler).
- Çıktı: `project/project-brief.md` (`config.PATHS["project_brief"]`) — araştırma
  sorusu, hipotez(ler), özgünlük notu, yöntem taslağı, başarı ölçütleri,
  fizibilite, etik/izin ve risk başlıkları doldurulmuş.

## Prosedür
0. **Erken uygunluk kontrolü (rules `eligibility`).** Fikre girmeden önce, onboarding'de
   yapılmadıysa başvuruyu eleyecek koşulları kısaca teyit et (sabit yazma; kuralları
   rules `eligibility`'den oku): aynı dönemde tek başvuru / devam eden 2209-A-B
   projesinde olmama (§4.1.4), ön lisans/lisans öğrencisi olma — Açık Öğretim ve
   Hazırlık hariç (§4.1.1), ARBİS kaydının güncelliği (§4.1.2), aynı proje için önceki
   TÜBİTAK desteği olmaması (§4.1.5). Karşılanmayan koşulu kullanıcıya bildir ve
   `logs/open-questions.md`'ye yaz; uygunluk kararını ekip verir.
1. **Tek seferde 1-3 soru sor.** Kullanıcıyı soru yağmuruna tutma; her turda en
   çok üç soru. Önce neyi merak ettiğini ve kimin için değerli olduğunu anla.
   Eğer ekibin elinde zaten yazılmış bir öneri taslağı varsa (fikir değil, metin),
   fikir üretmeyi bırak ve `draft-revision`'a yönlendir: var olan taslak sıfırdan değil, içe alınıp iyileştirilerek ilerletilir.
2. **Araştırma sorusuna çevir.** Ham fikirden ölçülebilir, sınırlı bir soru
   çıkar. "İyi mi" değil, "ne kadar / hangi koşulda / neye göre" biçiminde.
3. **Hipotez(ler).** Sınanabilir ve yönlü ifade et. Keşifsel olanı ayrıca
   işaretle. Hipotez bir sonuç değil, sınanacak beklentidir.
4. **Özgünlük.** "Kim ne yapmış, boşluk ne?" sorusunu birlikte yanıtla. Henüz
   literatür taranmadıysa boşluğu *aday katkı* diye yaz; kanıtı `academic-research`
   verecek. "Dünyada ilk", "rakipsiz" gibi iddialardan kaçın.
5. **Yöntem taslağı.** Tasarım türü (gözlemsel, deneysel, anket, analiz),
   veri kaynağı, ana değişkenler — kabaca. Ayrıntı `methodology-review` ve
   `proposal-writing`'e kalır.
6. **Ölçülebilir başarı ölçütleri.** Her hedefe sayısal/gözlenebilir bir eşik
   bağla (örnek: "en iyi yöntemde F1 ≥ eşik"). Eşik uydurma; ekibin
   gerekçelendirebileceği değer olsun.
7. **Fizibilite.** rules dosyasındaki süre üst sınırı (`duration.max_months`,
   2026: 12 ay) ve bütçe üst sınırı (`budget.max_tl`, 2026: 12000 TL) içinde
   yapılabilir mi? Ekip/ekipman/zaman gerçekçi mi?
8. **Etik/izin (rules `ethics`, §5.3.1).** Katılımcı, kişisel veri, anket, saha ya da
   canlı sistem var mı? Etik kurul onayı/muafiyeti veya yazılı izin gerekebilecek her
   durumu işaretle; `checks.ethics_required` alanına not düşülmesini öner. Gerekiyorsa
   Etik Kurul Onay/Muafiyet Belgesinin süresi içinde yüklenmesi gerektiğini, aksi hâlde
   projenin yürürlüğe girmeyeceğini hatırlat (rules `ethics`).
9. **Riskler.** En olası 2-4 riski ve kaba B planını birlikte yaz.
10. **Birden çok fikir varsa karşılaştırma tablosu çıkar:**

    | Ölçüt | Fikir A | Fikir B | Fikir C |
    | --- | --- | --- | --- |
    | Araştırma sorusu netliği | | | |
    | Özgünlük (boşluk gücü) | | | |
    | 12 ay + bütçe içinde yapılabilirlik | | | |
    | Veri/izin erişilebilirliği | | | |
    | Ekibin ilgisi ve sahipliği | | | |

    Tabloyu karar aracı olarak sun; kararı ekibe bırak.
11. Netleşen sonucu `project/project-brief.md`'ye yaz. Kullanıcının kendi dilini
    koru; metni ekip sahiplenebilmeli.

## Hata durumları
- Fikir çok geniş → birlikte daraltacak somut bir alt soruya in; tek fikir seçtir.
- Özgünlük belirsiz → "aday katkı" diye yaz, `academic-research`'e yönlendir.
- Kullanıcı eşik veremiyor → `TBD` bırak, `logs/open-questions.md`'ye ekle.

## Kalite kontrol
- [ ] Erken uygunluk (tek başvuru, öğrenci türü, ARBİS, önceki destek) rules `eligibility`'den teyit edildi.
- [ ] Etik kurul gereksinimi rules `ethics`'e göre soruldu ve gerekiyorsa işaretlendi.
- [ ] Her turda en çok 3 soru soruldu.
- [ ] Araştırma sorusu, hipotez, özgünlük, yöntem taslağı, ölçüt, fizibilite,
      etik/izin ve risk başlıklarının hepsi ele alındı.
- [ ] Süre ve bütçe üst sınırları rules dosyasından okundu, sabit yazılmadı.
- [ ] Birden çok fikir varsa karşılaştırma tablosu üretildi.
- [ ] Çıktı `project/project-brief.md`'ye yazıldı; fikir dayatılmadı, sahiplik ekipte.
- [ ] "İlk/rakipsiz" türü abartılı özgünlük iddiası yok.
