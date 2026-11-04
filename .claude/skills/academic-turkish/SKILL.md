---
name: academic-turkish
description: Rapor ve başvuru metnini akademik Türkçe yazım kurallarına, proje terminolojisine ve kesinlik düzeyine göre düzenler; 2209-A hakemlerinin olumsuz karşıladığı abartı ve belirsizlik kalıplarını temizler. Metin taslağı tamamlandığında, "dili düzelt", "akademik hale getir", "hakeme uygun yaz" isteklerinde kullan. İçerik eklemez; bilgi, sayı veya iddia değiştirmez.
---

# academic-turkish

## Görev
Anlamı koruyarak dili netleştirmek: kısa cümle, tek fikir, edilgen-etken dengesi, tutarlı terim ve hakemin güvenini sarsmayan ölçülü bir ton.

## Girdi → Çıktı
- Girdi: Markdown veya DOCX taslak.
- Çıktı: düzeltilmiş metin + değişiklik listesi (eski → yeni, gerekçe).

## Kurallar
1. **Kesinlik dili.** İddia düzeyi, elde kanıt neyse o olur:
   | Kullanma | Kullan |
   | --- | --- |
   | kanıtlandı / ispatlandı | (yalnız ölçülmüşse) gösterildi / gözlendi |
   | kesinlikle / hiç şüphesiz / mutlaka | — (kaldırılır) |
   | başarılı oldu (henüz yapılmamış iş için) | hedeflenmektedir / planlanmaktadır |
   | çözecektir / sağlayacaktır (kesin vaat) | sağlaması beklenmektedir / amaçlanmaktadır |
2. **Gelecek iş geçmiş zamanla yazılmaz.** Başvuruda "yapılacaktır", sonuç raporunda yalnız yapılanlar "yapılmıştır".
3. Teknik terimler kodda ve araçta geçtiği gibi İngilizce kalır (CLI, API, DOI, BibTeX ...); zorla Türkçe karşılık üretilmez. İlk geçişte açıklama verilir.
4. Sayı biçimi: ondalık virgül (0,90), binlik boşluk (28 257), yüzde işareti önde (%95).
5. Atıf biçimi: (Soyad, Yıl), (Soyad ve Soyad, Yıl), Soyad vd. (Yıl).
6. Kısaltmalar ilk geçişte açılır.
7. Büyük harf: Türkçe kural (i→İ).
8. Yazım: TDK. Sık hatalar: "herşey"→"her şey", "birşey"→"bir şey", "-de/-da" ayrı/bitişik, "ki" bağlacı.
9. Bir cümle okunurluk eşiğini (yaklaşık 25 kelime) geçiyorsa bölünür.

## 2209-A hakeminin sevmediği kalıplar
Hakem, somut yöntemi ve ölçülebilir çıktısı olan başvuruyu arar; pazarlama dili ve içi boş büyük sözler güveni düşürür. Şunlar temizlenir:
- **Abartı / süperlatif**: "devrim niteliğinde", "dünyada ilk", "benzersiz", "en iyi", "çığır açan", "mükemmel", "tamamen yeni". Yerine ölçülebilir fark ve koşullu boşluk ifadesi (literature-synthesis).
- **Belirsiz nicelik**: "birçok", "pek çok", "oldukça fazla", "yeterince", "kısa sürede", "çeşitli çalışmalar". Yerine sayı, aralık veya "taranan kaynaklarda (bkz. search-log)".
- **Dayanaksız kesinlik**: "kesinlikle sağlayacaktır", "mutlaka çözecektir". Yöntemle desteklenmeyen vaat kaldırılır.
- **Klişe gerekçe**: "günümüzde teknolojinin hızla gelişmesiyle…" gibi içeriksiz açılışlar. Doğrudan probleme girilir.
- **Yöntemsiz hedef**: "yapay zekâ ile analiz edilecektir" gibi hangi yöntem/ölçüt olduğu belirsiz cümleler somutlaştırılır (başarı ölçütü verilir).

## Boş vaat kalıpları

Bu kalıplar hakemin "kanıt yok" diye işaretlediği cümlelerdir. Yerine somut bilgi koy. Tam liste ve örnekler: `project/writing-guide.md`, otomatik tarama: `uv run python tools/check_writing.py <md>`.

| Zayıf | Güçlü yön |
| --- | --- |
| "…alana katkı sağlayacaktır." | Kimin, neyi, ne kadar kazanacağını yaz. |
| "Uygun yöntemler kullanılarak…" | Yöntemin adını, aracını ve neden seçildiğini yaz. |
| "Herhangi bir risk öngörülmemektedir." | En olası 2–3 riski ve B planını yaz. |
| "Proje zamanında ve başarıyla tamamlanacaktır." | İş paketi başına sayısal başarı ölçütü yaz. |
| "Literatürde ilk kez…" | Taramayı ve boşluğu kaynakla göster ya da iddiayı yumuşat. |

## TYBS taahhüdü — öneri metni ekibin kendi sözleri olmalı
TYBS başvurusunda öğrenci, öneri metninin kendi ürünü olduğunu taahhüt eder. ÜYZ yalnız taslak/öneri üretir; son metin ekibin kendi cümleleriyle, kendi anlayarak yeniden yazılır. Bu skill metni cilalar ama ekibin yerine yazmaz: ÜYZ kaynaklı büyük yeniden yazımda ekibe "bu paragrafı kendi cümlenizle onaylayın/yeniden yazın" denir ve ÜYZ katkısı ai-research-compliance kaydına işlenir. Son karar ve bilimsel sorumluluk ekiptedir.

## Prosedür
1. Metin okunur, yalnız dil düzeyinde değişiklik önerilir.
2. Her değişiklik anlam kontrolünden geçer: sayı, ad, kimlik, bağlantı ve iddia düzeyi aynı mı?
3. Belirsiz bir anlam varsa düzeltme yapılmaz, kullanıcıya sorulur.
4. Değişiklik listesi kullanıcıya sunulur; büyük yeniden yazımda ÜYZ kaydı (ai-research-compliance) güncellenir.

## Kalite kontrol
- [ ] Hiçbir sayı, kimlik, kaynak veya bağlantı değişmedi.
- [ ] Kesinlik düzeyi yükseltilmedi; abartı ve belirsiz nicelik temizlendi.
- [ ] Özet, rules dosyasındaki kelime aralığında (2026: 25–450 kelime) kaldı.
- [ ] Öneri metni ekibin kendi sözleri olarak işaretlendi; ÜYZ katkısı kaydedildi.
