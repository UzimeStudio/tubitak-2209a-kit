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
| T08 | [Proje Yazma Eğitimi Bölüm 1](https://www.tubitak.gov.tr/sites/default/files/proje_yazma_egitimi-1._bolum.pdf) | Genel TÜBİTAK proje yazma rehberi (2209-A'ya özgü değil); https erişilebilir (200, application/pdf) | CFB2CB35621BBFCD | 2026-11-04 |
| T09 | [Proje Yazma Eğitimi Bölüm 2](https://www.tubitak.gov.tr/sites/default/files/proje_yazma_egitimi-2._bolum.pdf) | Genel TÜBİTAK proje yazma rehberi (2209-A'ya özgü değil); https erişilebilir (200, application/pdf) | 8D844CA430D04BB5 | 2026-11-04 |

<!-- URL ve varsayılan SHA değerleri rules dosyasında tutulur; burada yalnız erişim/doğrulama durumu izlenir. T08/T09 genel rehberdir; kural kaynağı olarak değil, yazım desteği olarak kullanılır. -->

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

**Bölüm içerik yükümlülükleri (T03):** Her bölüm (1.1/1.2/2./3.1/3.2/3.3/4.) için istenen içerik maddeleri. 1.1'de konunun kapsamı/sınırları/önemi, literatürdeki eksikliğin nasıl giderileceği (atıfla), araştırma sorusu ve varsa hipotez(ler), varsa 12. Kalkınma Planı/2030 SanTek ilişkisi gerekçesi; 1.2'de açık-ölçülebilir-gerçekçi-ulaşılabilir hedef; 2.'de yöntem (araştırma tasarımı, bağımlı/bağımsız değişken, istatistiksel yöntem), ön çalışma, çalışma takvimiyle ilişki; 3.2'de B Planı (Risk Yönetimi Tablosu) temel hedeften saptırmamalı; 3.3'te mevcut altyapı/ekipman; 4.'te kategorili ve ölçülebilir çıktı. (rules `section_requirements`)

**Ön inceleme ret nedenleri (T02 §5.1.1, §5.1.2, §4.3.1, §4.2.4):** Başvuru koşullarından birini sağlamayan veya süresinde onaylanmayan başvurular bilimsel değerlendirmeye alınmadan elenir; TÜBİTAK formatına/minimum karakter sınırına uymayan başvurular elenir; çevrimiçi başvuru dışında e-posta/posta/faks ile gönderilen belgeler değerlendirmeye alınmaz ve imha edilir; yanıltıcı/gerçeğe aykırı bilgi verenler hukuken sorumludur. (rules `pre_screening`)

**İzleme/sonuçlandırma (T02 §6.2, §6.3, §6.4, §6.5, §6.8, §6.12/§6.13):** Demirbaş alındıysa üniversite envanter kayıt belgesi alınır ve sonuç raporuna eklenmesi zorunludur; faturalar yürütücü ya da ortak adına düzenlenir, isimsiz fişler geçersiz sayılır ve iade istenir; danışman ve ortak değişikliği yazılı onayla yapılır ve ortak sayısı sabit kalır; bitişe 3 aydan az kaldığında ortak/danışman değişiklik talepleri kabul edilmez; sonuç raporu süresinde yüklenmezse veya revizesi kabul edilmezse proje kusura göre yürürlükten kaldırılır veya iptal edilir. (rules `monitoring`)

**TYBS içerik girişi (T03):** Görseller "Resim Yükle", tablolar "Tablo", özel karakterler ve matematiksel semboller "Özel karakter" menüsünden eklenir; denklemler özel karakterle yazılır ya da ekran görüntüsü olarak eklenir; başka ortamdan yapıştırmada biçim bozulabilir; "Proje Önerisini Önizle" ile onay öncesi kontrol edilir. (rules `tybs_input`)

**ÜYZ yükümlülük ve yasakları (T05 §1.3.1, §1.2.1, §1.3.3, §1.1.2, §1.4.4/§1.5.3):** Nihai sorumluluk tamamen başvuru sahibinde; her çıktı (metin/veri/kod/referans) doğrulanır; "önemli ölçüde kullanım" beyan edilir, salt dilbilgisi/yazım denetimi muaftır; ÜYZ ile veri uydurma/çarpıtma/aşırma kesinlikle yasaktır; ÜYZ ile üretilen görseller belirtilir; gizli/kişisel (KVKK) veya yayımlanmamış veriler ÜYZ araçlarına girilmez; ÜYZ taslağı asla nihai metin sayılmaz. (rules `ai_use`)

**Etik genişletme (T02 §5.3.2; T05 §1.3.2/§1.3.3/§1.1.2):** İntihal (Aşırma) AYEK Yönetmeliği Madde 9/1-c; uydurma (Madde 9/1-a, 9/1-b) ve çarpıtma bilimsel yanıltma; ÜYZ'nin ürettiği referanslar sahte olabilir, doğrulanmadan kullanılamaz; destek öncesi benzerlik kontrolü yapılabilir. "Dilimleme" (salami) için 2209-A resmî belgelerinde özel bir madde bulunamadı; en yakın dayanak benzerlik kontrolü ve AYEK'in genel hükümleridir. (rules `ethics`)

**Değerlendirme eşiği (T02 §5.2.3, §5.3.2):** Destek taban (kesme) puanı sayısal olarak yayımlanmaz; taban puan üzerindeki projeler için destek kararı verilir ve kritik/öncelikli alanlara göre taban puan ayrı belirlenebilir. (rules `evaluation.cutoff_note`)

**Genel yazım rehberleri (T08, T09):** "Proje Yazma Eğitimi" Bölüm 1 ve Bölüm 2 genel TÜBİTAK rehberleridir, 2209-A'ya özgü kural kaynağı değildir; yalnız yazım desteği için kullanılır. İkisi de https ile erişilebilir (200, application/pdf).
