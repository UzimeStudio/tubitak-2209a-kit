# TYBS başvuru ekranı rehberi

<!--
Konu-bağımsız TYBS ekran rehberi: adımlar, alanlar, kurallar ve önemli
taahhüt maddeleri. Başvuru numarası, kişisel durum bilgisi ve projeye özgü
değer İÇERMEZ. Çağrıya bağlı sınırlar `rules/<year>.json`'dan; parantez içi
2026 örneğidir.
-->

## Adımlar ve alanlar

| Adım | Alanlar ve kurallar |
| --- | --- |
| Kişisel Bilgiler | Kimlik ve iletişim ARBİS/YÖK'ten gelir. Fotoğraf yükleme alanı olabilir |
| Danışman Bilgileri | Danışman TC kimlik no ile "Kişi Getir"; bilgiler ARBİS/YÖK'ten alınır, güncel olmalı (rules `advisor`) |
| Proje Ortağı Öğrenci Bilgileri | İsteğe bağlı; en çok N ortak (rules `partners`; 2026: 4); T.C. kimlik no / YKN / Mavi Kart; ARBİS kaydı zorunlu; ortak yoksa boş bırakıp Kaydet |
| Bütçe | Dört kalem, her biri tek tutar (rules `budget.items`; 2026: Makine Teçhizat, Hizmet Alımı, Sarf Malzemesi, Ulaşım). "Destek İstemiyorum" kutusu. Gider kalemleri yalnız bu ekranda belirtilir; toplam sıfır kaydedilebilir |
| Araştırma Projesi Bilgileri | Proje Başlığı ≤ rules `title.max_chars` (2026: 495); Proje Özeti rules `abstract` aralığı (2026: 25–450 kelime); Anahtar Kelimeler rules `keywords` (2026: 3–5, virgülle); Bilimsel ve Teknolojik Faaliyet Alanı (dış danışmanlar buna göre seçilir); Öncelikli Alanlar Evet/Hayır |
| Araştırma Önerisi | 1.1, 1.2, Yöntem: zengin metin, rules `section_min_chars` (2026: ≥350). 3.1 Çalışma Takvimi satır tablosu (rules `work_plan.columns`). 3.2 Risk tablosu: Riskler, Tedbirler (B Planı). 3.3 Olanaklar tablosu: Altyapı/Ekipman Türü-Modeli, Kullanım Amacı. 4. Yaygın Etki üç sabit kategori (rules `impact_categories`). 5. Diğer konular zengin metin. 6. Ekler |
| Kaynaklar | Tek metin alanı, rules `references.max_chars` (2026: 32.000); "Kaynakçayı Numaralandır", "Araştırma Önerisini Önizle" |
| İçerik girişi (tüm zengin metin alanları) | Görsel "Resim Yükle", tablo "Tablo", özel karakter/matematiksel sembol "Özel karakter" menüsünden; denklem özel karakterle ya da ekran görüntüsü olarak; başka ortamdan yapıştırmada biçim bozulabilir; tablo genişlikleri "tablo/hücre özellikleri"nden ayarlanır (rules `tybs_input`) |
| Üretken Yapay Zekâ (ÜYZ) | ÜYZ Kaynakça Taahhütnamesi: atıf↔kaynakça tam eşleşme; tüm kaynakların doğrulandığı, uydurma kaynak olmadığı; AYEK yaptırımı onayları. Serbest beyan alanının yeri rules `ai_disclosure.note`'a göre netleştirilir |
| Başvuru Ek Belgeleri | Etik Kurul Onay Belgesi (zorunlu olmayabilir; gerekiyorsa destek sonrası da yüklenebilir) |
| Başvuru Sahibi Banka Bilgileri | Kişisel finansal veri |
| Taahhütname | Tek onay. Öne çıkan maddeler aşağıda |
| Danışman Onay | Yürütücü onayından sonra aktifleşir |

## Önemli taahhüt maddeleri

- Projenin destek kararından itibaren süre sınırı içinde tamamlanması (rules `duration`).
- Destek kalemlerinde danışmanın yazılı uygun görüşü olmadan değişiklik yapılmaması.
- Proje önerisinin tamamen yürütücü ve (varsa) ortakları tarafından yazıldığı ve AYEK hükümlerine uyulduğu.
- ÜYZ Rehberine tam uyum ve ÜYZ kullanımına ilişkin bilgilerin eksiksiz ve gerçeğe uygun olması.
- Fatura, bilet, makbuz, etik kurul belgesi gibi asılların belirli süre saklanması.
- Kişisel verilerin korunması ve veri güvenliği mevzuatına uyum; veri, yazılım ve içerik için gerekli izinler.

## Notlar
- ÜYZ Rehberi beyanın "sistemdeki ayrılmış bölümde" yapılmasını isteyebilir; formda serbest beyan alanı görülmezse yerin BİDEB'e veya danışmana sorulması gerekir (rules `ai_disclosure.note`).
- Onay öncesi tüm zengin metin alanları "Proje Önerisini Önizle" butonuyla kontrol edilmeli; eksik/hatalı içerik olmadığından emin olunduktan sonra onaylanmalıdır (rules `tybs_input`). Metin başka ortamdan yapıştırıldığında biçim bozulabileceğinden görsel/tablo/özel karakter TYBS araçlarıyla yeniden kurulmalıdır.
- "Tamamen şahsım tarafından yazıldığı" taahhüdü nedeniyle metnin son hâli ekip tarafından kendi sözleriyle sahiplenilmelidir.
- 3.1, 3.3 ve 4. bölümleri TYBS'de tablo/sabit kategori biçimindedir; `templates/tybs-application.md` buna göre düzenlenmiştir.
