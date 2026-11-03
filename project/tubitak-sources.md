# TÜBİTAK 2209-A kaynak kaydı

<!--
Jenerik, projeye özgü olmayan resmî kaynak kaydı. Kimlikler (T01–T07)
`rules/<year>.json` içindeki `sources[]` listesiyle AYNIDIR. Her çağrı yılında
`call-update` skill'iyle her kaydı yeniden doğrulayın (URL, sürüm, SHA-256) ve
erişim tarihini güncelleyin. Erişim tarihi ve SHA değerleri başlangıçta boştur;
doğrulamada doldurulur.
-->

Erişim / son doğrulama tarihi: **2026-11-03** (her doğrulamada güncelleyin). İndirilen dosyaların SHA-256 değeri, sonraki kontrollerde dosyanın değişip değişmediğini görmek içindir. Bu doğrulamada PDF belgelerinde (T02, T03, T05, T07) değişiklik görülmedi; T01 ve T06 HTML sayfadır, SHA tutulmaz.

| ID | Belge | Sürüm / kısım | SHA-256 (ilk 16) | Erişim tarihi |
| --- | --- | --- | --- | --- |
| T01 | [2209-A program sayfası](https://tubitak.gov.tr/tr/burslar/lisans-onlisans/destek-programlari/2209-universite-ogrencileri-arastirma-projeleri-destekleme-programi) | HTML; tarihler, destek/süre üst sınırı, IBAN, bütçe dışı kalemler, bağlı belgeler, sonuç raporu yükümlülükleri | — (HTML) | 2026-11-03 |
| T02 | 2026 Çağrı Duyurusu (rules `sources[].url`) | Çağrı PDF; uygunluk, dil, değerlendirme, etik, geri çekme, logo, sonuç raporu ve ÜYZ bölümleri | BAA725C095DEE354 | 2026-11-03 |
| T03 | Başvuru İçeriği Bilgi Notu | Başvuru biçim kuralları | D5BF5477971B5924 | 2026-11-03 |
| T05 | Üretken Yapay Zekâ Rehberi v04 | ÜYZ beyan ve sorumluluk (§1.2.2, s.12) | FDFE5238DD7C773E | 2026-11-03 |
| T06 | Bibliyografik Verilerin Düzenlenmesi | Kaynakça biçim kuralı | — (HTML) | 2026-11-03 |
| T07 | Sonuç Raporu Formatı | Resmî DOCX şablon yapısı | 8401F2AE6E0E8D08 | 2026-11-03 |

<!-- URL ve varsayılan SHA değerleri rules dosyasında tutulur; burada yalnız erişim/doğrulama durumu izlenir. -->

## Bulgular
<!--
Yalnız RESMÎ ve projeye özgü OLMAYAN bilgiler. Projeye özel sayı, ad, tarih
veya tutar buraya girmez.
-->

**Sonuç raporu yükümlülükleri (T01, T02):**
- Proje süresi içinde, TÜBİTAK formatında, harcama tablosuyla birlikte BİDEB sistemine yüklenir.
- Akademik danışman kontrol eder ve nihai onay verir.
- Demirbaş alındıysa envanter kayıt belgesi rapora eklenir.
- Raporlar dönem sonunda toplu değerlendirilir; uygun bulunmayanlar için düzeltme istenir.
- Süresinde yüklenmeyen veya revizyonu kabul edilmeyen proje kusura göre yürürlükten kaldırılır veya iptal edilir.

**Sonuç raporu şablon yapısı (T07):** Kapakta proje başlığı; GENEL BİLGİLER (konu, yürütücü, danışman, başlangıç–bitiş); ardından 1. Giriş, 2. Rapor dönemlerinde yapılan çalışmalar, 3. Sonuç, 4. Çıktılar (yayınlar, sunumlar vb.), 5. Harcama kalemleri; imza tablosu; tarih. Resmî şablonun kendisi `project/official-report-template.docx` içindedir; yapısına dokunulmaz.

**ÜYZ beyan içeriği (T05 §1.2.2, T02):** Önemli ölçüde kullanım (taslak, kod, analiz, görsel) beyan edilir. Beyanda rules `ai_disclosure.content` alanları yer alır: araç adı ve sürümü, aşama/bölüm, kullanımın niteliği. Tüm çıktıların doğrulanması başvuru sahibinin sorumluluğundadır; danışman da ÜYZ içeriğini kontrol eder ve nihai sorumluluğu üstlenir. ÜYZ Rehberi (T05 §1.2.2, s.12) bu beyanın TÜBİTAK çevrimiçi başvuru sisteminde bu amaçla ayrılmış bölümde yapılmasını ister. 2026 TYBS başvuru ekranında bu amaçla ayrılmış serbest beyan alanı görülmedi (yalnız ÜYZ Kaynakça Taahhütnamesi vardı) — bu bir gözlemdir; alanın yeri rules `ai_disclosure.note` uyarınca BİDEB'e/danışmana sorulur. Rehberin isteği ile ekranda görülen bu ikisi ayrı tutulur.

**Uygunluk koşulları (T02 §4.1):** Aynı dönemde birden fazla başvuru yapılamaz; devam eden 2209-A/2209-B projesinde yürütücü ya da ortak olanlar başvuramaz (§4.1.4). Türkiye'de ön lisans/lisans programına kayıtlı olmak gerekir; Açık Öğretim ve Hazırlık Sınıfı öğrencileri yürütücü ya da ortak olamaz (§4.1.1 ve dipnotu). Yürütücünün ARBİS kaydı ve bilgileri güncel olmalıdır (§4.1.2). Aynı proje için daha önce TÜBİTAK'tan destek alınmamış olmalıdır (§4.1.5). (rules `eligibility`)

**Başvuru dili (T02 §4.2.1, §5.1.2):** Araştırma önerisi TÜBİTAK formatında ve Türkçe hazırlanır; formata/Türkçe'ye uymayan başvurular ön incelemede elenir. (rules `language`)

**Etik kurul (T02 §5.3.1):** Çalışma etik kurul onayına tabi ise, Etik Kurul Onay/Muafiyet Belgesi süresi içinde yüklenmezse proje yürürlüğe girmez. (rules `ethics`)

**Değerlendirme ölçütleri (T02 §5.2.1, §4.2.3, §5.2.6):** Bilimsel nitelik %35, Yöntem %25, Proje yönetimi %20, Yaygın etki %20. Proje ekibinde özel gereksinimli birey beyanı doğrulanırsa toplam puana +1 puan eklenir. (rules `evaluation`)

**Bütçe dışı kalemler ve IBAN (T02 §2.1.2, T01):** Konferans katılım, yayın, patent, konaklama ve gündelik (yeme-içme) giderleri bütçeye dahil edilemez. Başvuruda girilen IBAN proje yürütücüsü öğrenciye ait olmalıdır. (rules `budget.excluded_items`, `budget.iban`)

**Geri çekme (T02 §4.3.5):** Başvuru, çağrı kapanış tarihinden itibaren 1 ay içinde TYBS üzerinden geri çekilebilir. (rules `withdrawal`)

**TÜBİTAK desteği ve logosu (T02 §6.6, T01):** Program çıktılarında ve her türlü duyuru, yayın ve bilimsel etkinlikte TÜBİTAK desteğinin belirtilmesi ve logosunun kullanılması zorunludur. (rules `acknowledgement`)
