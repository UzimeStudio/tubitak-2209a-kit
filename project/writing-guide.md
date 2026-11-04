# 2209-A öneri yazım rehberi — bölüm bölüm hakem bakışı

Bu rehber, TÜBİTAK 2209-A öneri metnini bölüm bölüm ele alır: her bölümde
**hakemin ne aradığı**, **en sık yapılan hata** ve **zayıf cümlenin güçlüye
dönüşmüş kurgusal örneği** verilir. Örnekler konu-bağımsız ve kurgusaldır;
kendi projenize uyarlayın. Son sütun, maddenin dayandığı **kaynak kimliğidir**
(aşağıdaki "Kaynaklar" bölümüne bakın).

İki tür kuralı ayrı işaretliyoruz:

- **Resmî** — TÜBİTAK çağrı belgelerinden veya resmî eğitim/başvuru notundan
  gelen, uyulması beklenen kural.
- **Öneri** — resmî metinde zorunlu kılınmayan, iyi uygulama niteliğinde
  tavsiye. Resmî olmayan kaynaklardan gelenler ayrıca "genel rehber" diye
  işaretlenir.

Sayısal sınırlar (kelime, karakter, ay, tutar) bu rehberde **sabit yazılmaz**;
her çağrıda değişebildikleri için `rules/<yıl>.json` dosyasından okunur. Rehber
kuralın *mantığını* anlatır, değerini değil.

Kaynakta açıkça bulunmayan hiçbir kural bu rehbere eklenmemiştir. Alıntılar
kısadır (hiçbir yerde 30 kelimeden uzun birebir aktarım yoktur); içerik yeniden
ifade edilmiştir.

---

## Başlık

| Hakemin aradığı | Sık hata | Zayıf → güçlü (kurgusal) | Kaynak |
| --- | --- | --- | --- |
| **Resmî:** Konuyu ve özgün yönü yansıtan, kurum/firma/ürün/marka öne çıkarmayan başlık. | Modaya uygun ama konuyla ilgisiz etiket ("yapay zekâ", "nano") eklemek; başlık ile içeriğin uyuşmaması. | "Yeni Nesil Akıllı Sistem" → "X Yönteminin Y Koşulunda Ölçüm Güvenilirliğinin Değerlendirilmesi" | T08/T09, T02 (marka yasağı) |
| **Öneri:** Başlık okunduğunda ne, nerede, neye göre ölçüldüğü sezilmeli. | Aşırı uzun, iç içe tamlamalı başlık. | "… ve Bununla İlişkili Tüm Etkenlerin Kapsamlı İncelenmesi" → "… İki Grup Arasındaki Farkın İncelenmesi" | genel rehber (NSF, Horizon) |
| **Öneri:** Başlıkta kısaltma ve alan jargonu olmamalı; hakem başlığı ilk okuyuşta çözebilmeli. | Yalnız ekibin bildiği kısaltma ("XYZ-Net ile …"). | "ABC-Ölçer ile DKS Tespiti" → "Düşük Maliyetli Sensörle Toprak Nemi Ölçümünün Doğruluğu" | genel rehber (NSF) |

---

## Özet ve Anahtar Kelimeler

| Hakemin aradığı | Sık hata | Zayıf → güçlü (kurgusal) | Kaynak |
| --- | --- | --- | --- |
| **Resmî:** Önem, amaç, yöntem, beklenen sonuç ve etkiyi tek akışta eksiksiz veren özet; dört ekseni (bilimsel nitelik, yöntem, proje yönetimi, yaygın etki) kapsar. | Sonuç varmış gibi yazmak; dört eksenden birini atlamak; sınır dışı uzunluk. | "Bu çok önemli ve yenilikçi bir projedir." → "Bu proje, X yönteminin Y koşulundaki güvenilirliğini nicel olarak sınayarak literatürdeki Z boşluğunu kapatmayı amaçlar." | T03, T08/T09 |
| **Öneri:** İngilizce özet, Türkçe özetin birebir ve dilbilgisel karşılığı olmalı. Sayılar, eşikler ve yöntem adları iki dilde aynı olmalı; cümle cümle karşılaştırın. | "Çeviri kokan", Türkçeden sapan İngilizce özet; Türkçede "%90", İngilizcede "85%". | Makine çevirisi cümle → ekip tarafından yeniden kurulmuş akıcı cümle | genel rehber (Horizon, Innovate UK) |
| **Öneri:** Anahtar kelimeler konuyu tarayıcıda bulunur kılmalı. | Çok genel ("araştırma", "analiz") sözcükler. | "bilim, teknoloji, veri" → "ölçek geçerliği, iç tutarlılık, Y koşulu" | genel rehber |

---

## 1.1 Konunun önemi ve bilimsel niteliği (özgün değer)

| Hakemin aradığı | Sık hata | Zayıf → güçlü (kurgusal) | Kaynak |
| --- | --- | --- | --- |
| **Resmî:** Özgünlüğü oluşturan unsurların, hangi literatür boşluğunu nasıl kapatacağının **ilgili literatüre atıfla** açıklanması; araştırma sorusu ve varsa hipotez. Önerinin en önemli bölümü sayılır. | Boşluğun gerekçesiz "yeterince çalışılmamış" diye geçilmesi; önerilen işin bir kısmının daha önce yapılmış olması. | "Bu konu literatürde yeterince çalışılmamıştır." → "Mevcut çalışmalar A yöntemini yalnız laboratuvar koşulunda sınamış; saha koşulundaki geçerliği bilinmiyor — bu proje bu boşluğu doldurur." | T03, T08/T09 |
| **Resmî:** Ulusal önceliklerle (ör. ilgili kalkınma planı/strateji alanı) ilişkiliyse, ilişkinin ve sağlayacağı yararın açıklanması. | Öncelikli alan bağının hiç kurulmaması veya zorlama kurulması. | "Projemiz de önemlidir." → "Proje çıktısı, [öncelikli alan]'daki ölçüm standardı eksikliğine doğrudan katkı sunar." | T03 |
| **Öneri:** Katkının somut ve sınanabilir olması; "ilk/rakipsiz" söyleminden kaçınma. | "Dünyada ilk", "benzersiz" iddiaları. | "Dünyada ilk kez …" → "Bilgimiz dahilinde A ile B'yi aynı tasarımda karşılaştıran çalışma bulunmamaktadır." | genel rehber (NSF, Horizon) |

---

## 1.2 Amaç ve hedefler

| Hakemin aradığı | Sık hata | Zayıf → güçlü (kurgusal) | Kaynak |
| --- | --- | --- | --- |
| **Resmî:** Açık, ölçülebilir, gerçekçi ve ulaşılabilir amaç ve hedefler; amacın proje çıktılarıyla ilişkilendirilmesi. | Belirsiz, ölçülemeyen hedef; genel hedefle proje hedefinin bağlanmaması; aşırı iyimser beklenti. | "Bu alanda farkındalık yaratmak." → "On iki ay sonunda, ilgili ölçeğin iç tutarlılığını N≥[hedef] katılımcıda belirlemek." | T03, T08/T09 |
| **Öneri:** Hedefler SMART (özgül, ölçülebilir, ulaşılabilir, gerçekçi, zaman sınırlı) olmalı. | Temenni cümlesi hedef gibi yazılır. | "Topluma katkı sağlamak." → "[süre] içinde [sayısal eşik]'e ulaşmak." | genel rehber + T08/T09 |

---

## 2 Yöntem

| Hakemin aradığı | Sık hata | Zayıf → güçlü (kurgusal) | Kaynak |
| --- | --- | --- | --- |
| **Resmî:** Amaç-hedefe uygun, **literatüre atıfla** gerekçelendirilmiş yöntem; araştırma tasarımı, bağımlı/bağımsız değişkenler, istatistiksel yöntemler gibi unsurların bulunması; yöntemin iş-zaman çizelgesiyle ilişkilendirilmesi. | Yöntemin yeterince ayrıntılı verilmemesi **veya** gereksiz ayrıntıya boğulması; ölçüt/kayıt adımının atlanması. | "Uygun yöntemler kullanılarak veriler toplanıp analiz edilecektir." → "İP2'de X cihazıyla her örnekte üç tekrar ölçüm alınır; grup farkı bağımsız örneklem t-testiyle sınanır." | T03, T08/T09 |
| **Resmî:** Yapıldıysa ön çalışma/fizibilite sonucunun sunulması. | Ön çalışmanın sonucu "doğruluk kanıtı" gibi sunulur. | "Ön denemede yöntem çalıştı." → "Ön denemede [n] örnekte yöntem uygulanabildi; kesin doğruluk iddiası asıl ölçüme bırakılmıştır." | T03 |
| **Öneri:** Yeniden üretilebilirlik (araç sürümü, veri, rastgelelik tohumu) ve veri en aza indirme açıkça yazılmalı. | Protokol anlatılıp kayıt/sürüm bilgisi atlanır. | "Sistem test edildi." → "Değerlendirme, sabit tohum ve belirtilen sürümle tekrarlanabilir biçimde yapılır." | genel rehber |

---

## 3.1 Çalışma takvimi (iş paketleri ve başarı ölçütleri)

| Hakemin aradığı | Sık hata | Zayıf → güçlü (kurgusal) | Kaynak |
| --- | --- | --- | --- |
| **Resmî:** Gerçekçi iş paketleri; her işin ne ölçüde yapılırsa başarılı sayılacağını belirten **başarı ölçütü** ve bu ölçütlerin katkı payı/ağırlığı; süre üst sınırını aşmayan çizelge. | Başarı ölçütünün tanımlanmaması; katkı toplamının hedeflenen değere ulaşmaması; gerçekçi olmayan takvim. | "Proje zamanında ve başarıyla tamamlanacaktır." → "İP2 başarı ölçütü: hedef doğruluğun ≥[eşik] olması (katkı %[ağırlık])." | T03, T08/T09 |
| **Resmî:** Literatür tarama, rapor yazımı, sonuç paylaşımı ve malzeme alımı tek başına iş paketi olamaz. | Bu adımların ayrı iş paketi yapılması. | İP: "Literatür taraması" → yöntem adımlarının içine gömülü, çıktısı somut iş paketleri | T03 (rules `work_plan.forbidden_steps`) |
| **Öneri:** Her iş paketinde sorumlu kişi(ler) belli, bir kişi çakışan işlerde değil. | Sorumsuz iş paketi; bir kişiye çakışan yük. | "Ekip yapar." → "İP2'den [ad] sorumludur; eş zamanlı İP3 [ad]'e verilmiştir." | genel rehber |
| **Öneri:** Her iş paketi elle tutulur bir ara çıktıyla bitmeli (veri seti, çalışan modül, analiz tablosu); başarı ölçütü bu çıktıya bağlanmalı. Hangi iş paketinin hangisinin çıktısını beklediği yazılmalı. | İş paketi "devam eden çalışma" gibi biter; bağımlılık görünmez, gecikme zinciri fark edilmez. | "İP2: Veri toplama (2-5. ay)." → "İP2 (2-5. ay) çıktısı: temizlenmiş [n] kayıtlık veri seti. İP3 bu veri setine bağlıdır." | genel rehber (1002-A form yapısı) |
| **Öneri:** Takvimi ay ay gösteren basit bir çubuk çizelge (Gantt) ekleyin; çakışan işler ve toplam süre tek bakışta görünür. | Takvimin yalnız düz metinle anlatılması. | Paragrafla anlatılan takvim → iş paketi × ay tablosu ya da `tools/figstyle.py` stiliyle çizilmiş çizelge | genel rehber |

---

## 3.2 Risk ve B planı

| Hakemin aradığı | Sık hata | Zayıf → güçlü (kurgusal) | Kaynak |
| --- | --- | --- | --- |
| **Resmî:** Öngörülemeyen gelişmelerde devreye girecek, tercihen aynı hedefe başka yoldan ulaştıran bir B planı; B planı temel hedeflerden sapmaya yol açmamalı. | B planının hiç verilmemesi; risklerin yok sayılması. | "Herhangi bir risk öngörülmemektedir." → "Saha erişimi gecikirse İP3, kamuya açık X veri setiyle yürütülerek aynı hedef korunur." | T03, T08/T09 |
| **Öneri:** Her ciddi riske karşılık somut, uygulanabilir bir tedbir. | Genel "gerekli önlemler alınacaktır" ifadesi. | "Önlem alınacaktır." → "Cihaz arızasında [yedek cihaz/kurum] ile ölçüm sürdürülür." | genel rehber |

---

## 3.3 Araştırma olanakları

| Hakemin aradığı | Sık hata | Zayıf → güçlü (kurgusal) | Kaynak |
| --- | --- | --- | --- |
| **Resmî:** Kurumda var olan ve projede kullanılacak altyapı/ekipmanın ve projedeki kullanım amacının belirtilmesi; konu-ekip-altyapı örtüşmesi. | Belgeyle doğrulanmamış olanağın kesin yazılması; pahalı cihaz satın alma talebinin gerekçesiz olması. | "Gerekli cihazlar satın alınacaktır." → "İP2'nin gerektirdiği X cihazı bölüm laboratuvarımızda mevcuttur (bkz. Şekil 3)." | T03, T08/T09 |
| **Öneri:** Kurum olanağı kullanılmıyorsa bunu açıkça belirtmek. | Boş bırakmak. | (boş) → "Projede kurum altyapısı kullanılmayacaktır; tüm ölçümler [yöntem] ile yapılır." | genel rehber |

---

## 4 Yaygın etki

| Hakemin aradığı | Sık hata | Zayıf → güçlü (kurgusal) | Kaynak |
| --- | --- | --- | --- |
| **Resmî:** Öngörülen çıktıların kategorilere ayrılarak (bilimsel/akademik, ekonomik/ticari/sosyal, yeni proje), ölçülebilir ve gerçekçi hedeflere dayandırılarak verilmesi. | Etkinin açıkça ifade edilmemesi; sona iliştirilen bir paragrafa sıkıştırılması; yayın kabulünün garanti edilmesi. | "Proje topluma ve bilime katkı sağlayacaktır." → "Çıktılar, X alanındaki ölçüm maliyetini düşürebilir; veri seti açık erişime açılacaktır." | T03, T08/T09 |
| **Öneri:** Sonuçtan kimin nasıl yararlanacağının somut yazılması. | Soyut "fayda" iddiası. | "Faydalı olacaktır." → "[paydaş], çıktıyı [somut kullanım] için kullanabilir." | genel rehber (NSF broader impacts) |
| **Öneri:** Etkiyi zamana göre ayırın: proje süresince, proje bitince (kısa vade) ve sonrasında (uzun vade). Her birine ölçülebilir bir gösterge bağlayın. | Bütün etkilerin tek, zamansız bir listede durması. | "Yayın ve yeni proje beklenmektedir." → "Süresince: açık veri seti. Bitince: 1 ulusal bildiri başvurusu. Sonra: sonuçlara dayanan yeni proje önerisi." | genel rehber (NSF broader impacts) |

---

## Bütçe

| Hakemin aradığı | Sık hata | Zayıf → güçlü (kurgusal) | Kaynak |
| --- | --- | --- | --- |
| **Resmî:** Her kalemin proje faaliyetiyle (iş paketiyle) ilişkilendirilmesi ve gerekçelendirilmesi; üst sınırın aşılmaması; yalnız izinli kalemlerin kullanılması. | Gerekçesiz kalem; kalemin hangi iş paketi için gerektiğinin yazılmaması; üst sınırı aşma. | "Sarf malzemesi: [tutar]." → "İP2'deki [sayı] ölçüm için X kiti gereklidir (birim fiyat [tutar], KDV dahil)." | T03, T08/T09 |
| **Öneri:** Fiyatların KDV dahil ve kur değişimini hesaba katan, proforma/teklife dayanan değerler olması. | Yuvarlak dolgu tutar, teklifsiz rakam. | "Yaklaşık [tutar]." → "Proforma Ek-2'ye göre [tutar] (KDV dahil)." | genel rehber + T08/T09 |
| **Öneri:** Öğrenci bursu/maaşı (PTİ) talebi izlenimi vermemek. | Bütçe dışı kalemi dolaylı istemek. | "Öğrenciye ödeme." → (yalnız izinli kalemler; burs/maaş yazılmaz) | T02 (bütçe dışı), T08/T09 |
| **Öneri:** Üst sınıra dayanmayın; kur ve fiyat artışı için küçük bir pay bırakın. Teklifin tarihini ve geçerlilik süresini not edin. | Bütçenin üst sınıra kuruşu kuruşuna eşit kurulması; bir fiyat artışında kalem kesmek zorunda kalmak. | "Toplam: [üst sınır] TL." → "Toplam: [üst sınırın biraz altı] TL; teklif tarihi [gün], geçerlilik 30 gün." | genel rehber (Horizon) |

---

## Kaynakça

| Hakemin aradığı | Sık hata | Zayıf → güçlü (kurgusal) | Kaynak |
| --- | --- | --- | --- |
| **Resmî:** Güncel, metinde atıfla ilişkilendirilmiş kaynaklar; projede anılan her çalışmanın listede yer alması ve listenin yalnız atıf verilenleri içermesi; DOI'li kaynakta DOI. | Eski kaynaklar; metinle bağ kurulmayan ham liste; eksik/fazla künye. | Peş peşe özetlenen, projeyle bağ kurulmayan liste → "Smith (2023) A'yı gösterdi; B koşulu test edilmedi — bu, projemizin çıkış noktasıdır." | T03, T06, T08/T09 |
| **Resmî:** ÜYZ uydurma kaynak üretebilir; her künye doğrulanmadan kullanılamaz. **Öneri:** Son metin düzenlemesinden sonra atıf-kaynakça eşlemesini bir kez daha çalıştırın; düzenleme sırasında atıf düşer ya da eklenir. | Kaynakçanın yalnız ilk taslakta denetlenmesi. | Son gün eklenen paragraftaki atıf listede yok → `tools/check_application.py` ve `tools/verify_source.py` son kez çalıştırıldı | T05 (rules `ethics.fake_references`), T06 |

---

## Ekip / Danışman

| Hakemin aradığı | Sık hata | Zayıf → güçlü (kurgusal) | Kaynak |
| --- | --- | --- | --- |
| **Resmî:** Gerekli bilimsel yetkinliğe sahip, projeye katkı verecek ekip; danışmanın alanının konuyla örtüşmesi. | Gereksiz kalabalık veya konuyla ilgisiz ekip; deneyimsizlik algısı. | "Danışmanımız tecrübelidir." → "Danışman, bu ölçüm yönteminde [sayı] yayını olan [alan] uzmanıdır." | T08/T09 |
| **Öneri:** Konuya dair ön çalışma/ders/deneyimin belirtilmesi. | Deneyimin hiç anılmaması. | (boş) → "Ekip, [ders/ön çalışma] kapsamında bu yöntemi daha önce uygulamıştır." | genel rehber |

---

## Proje türüne göre notlar

Proje türünü önce belirleyin; birden çok tür bir arada olabilir (ör. yazılım +
veri analizi). Her türün kendi asgari denetimi vardır.

- **Anket / ölçek çalışması:** İnsandan veri toplayan çalışmalar **etik kurul
  onayı/muafiyeti** gerektirebilir; örneklem büyüklüğü ve seçim yöntemi
  (olasılıklı mı?) gerekçelendirilmeli; ölçeğin geçerlik-güvenirliği (ör. iç
  tutarlılık) başarı ölçütü olarak tanımlanmalı. Bazı üniversitelerde lisans
  öğrencileri için ayrı öğrenci araştırmaları etik değerlendirme kurulu vardır.
  (T03, genel rehber)
- **Laboratuvar deneyi:** Kontrol grubu, rastgele atama, tekrar sayısı ve
  karıştırıcı değişkenler yöntemde netleştirilmeli; mevcut cihaz altyapısı
  gerekçeyle/kanıtla gösterilmeli; varsa ön deneme sonucu sunulmalı. (T08/T09)
- **Yazılım / prototip:** Her iş paketi somut bir çıktıya (modül, test,
  doğrulama) bağlanmalı; değerlendirme temeli (baseline), test/doğrulama ve
  yeniden üretilebilirlik (sürüm, tohum) belirtilmeli; başlığa konuyla ilgisiz
  moda etiketi eklenmemeli. (T08/T09, genel rehber)
- **Saha çalışması:** Erişim/izin riski ve B planı mutlaka yazılmalı; ölçüm
  standartlaştırması, gözlemci etkisi ve eksik veri planı ele alınmalı. (T03,
  T08/T09)
- **Sosyal bilim:** Doğru destek grubuna yazılmalı; yaygın etki ve planlama ayrı
  başlıklar olarak ciddiye alınmalı. (T08/T09, genel rehber)

---

## Konu seçimi ve kapsam

- **Lisans düzeyine uygunluk:** Konuyu, lisans süresi ve kaynaklarıyla
  bitirilebilir bir kapsama daraltın. Ekibin/altyapının kaldıramayacağı
  vaatlerden kaçının. (T08/T09)
- **Süre ve bütçe gerçekçiliği:** Süre ve bütçe üst sınırları (değerleri
  `rules/<yıl>.json`'dan) içinde yapılabilir bir iş seçin; süreyi gereğinden
  uzun tutmayın. İlk projede küçük/kısa kapsam önerilir. (T08/T09)
- **Hazırlık süresi:** İyi bir öneri hazırlık ister; metni başvurudan **önce**
  bitirip birkaç kez okuyun, mümkünse danışman dışı bir okuyucuya da okutun.
  (T08/T09)
- **Çifte fonlama:** Konunun başka bir kaynaktan (üniversite/AB vb.) fonlanmak
  için yazılmadığından ve literatüre gerçekten katkı yapacağından emin olun.
  Bitirme projesi ya da BAP projesiyle aynı işse bunu baştan danışmanla
  konuşun. (T08/T09; rules `eligibility.no_prior_support`, `eligibility.single_application`)
- **Yeşil ekonomi finansmanı:** Proje çevre dostu, sürdürülebilir ya da iklim
  nötr bir teknolojik çözüme odaklanıyor ve yürütücü kadın ya da uluslararası
  öğrenciyse, TÜBİTAK-UNIDO iş birliğiyle finanse edilebilir. (Resmî — rules
  `evaluation.green_economy_financing`, T02 §5.2.5)

---

## Başvuru süreci ve son kontrol

| Hakemin / sistemin aradığı | Sık hata | Ne yapılmalı | Kaynak |
| --- | --- | --- | --- |
| **Resmî:** Başvuru ve akademik danışman onayı aynı kapanış saatine kadar tamamlanır; tamamlanmayan başvuru ön incelemede elenir. | Öğrenci onayını son gün vermek; danışmana onay için zaman kalmaması. | Kendi iç son gününüzü resmî tarihten birkaç iş günü önceye koyun. Tarihler rules `timeline`'da. | T02 §4.3.1, rules `pre_screening` |
| **Resmî:** Biçime uymayan ya da en az karakter sayısını tutmayan başvuru elenir. | Bir zorunlu alanın boş ya da çok kısa kalması. | Onaydan önce `tools/check_application.py --tybs` çalıştırın; her alanın dolu olduğunu görün. | T02 §5.1.2, rules `section_min_chars` |
| **Resmî:** Metin "Proje Önerisini Önizle" ile kontrol edilip öyle onaylanır. | Başka yerden yapıştırılan metinde tablo kayması, bozuk özel karakter. | Önizlemeyi baştan sona okuyun; tablo ve şekilleri tek tek kontrol edin. | T03, rules `tybs_input` |
| **Öneri:** Metni konuya yabancı birine okutun. | Ekip içinde anlaşılan ama hakeme kapalı anlatım. | Başka bölümden bir arkadaş özgün değeri ve yöntemi bir cümleyle anlatabiliyorsa metin hazırdır. | genel rehber (Innovate UK) |

---

## En sık 15 kural (önem sırasıyla)

1. **Özgün değeri önerinin kalbi yapın;** boşluğu somut kanıtla gösterin.
   (Resmî — T03, T08/T09)
2. **Hedefleri açık, ölçülebilir, gerçekçi ve zaman sınırlı yazın.** (Resmî —
   T03)
3. **Başarı ölçütlerini ve katkı paylarını açıkça tanımlayın.** (Resmî — T03)
4. **B planını mutlaka yazın;** tercihen aynı hedefe başka yoldan ulaştıran.
   (Resmî — T03, T08/T09)
5. **İş paketlerini gerçekçi ve somut tutun;** literatür tarama/rapor yazımını
   iş paketi saymayın. (Resmî — T03)
6. **Yöntemi yeterince ayrıntılı ama gereksiz detaysız,** literatüre atıfla
   verin. (Resmî — T03)
7. **Yaygın etkiyi açık ve spesifik yazın;** sona iliştirilmiş bir paragraf
   olmasın. (Resmî — T03; genel rehber NSF)
8. **Bütçeyi gerçekçi, kalem kalem gerekçeli ve üst sınır içinde** hazırlayın.
   (Resmî — T03)
9. **Güncel, metinle ilişkilendirilmiş kaynaklar** kullanın; ham liste olmasın.
   (Resmî — T03, T06)
10. **Kendinizi hakemin yerine koyun** ve değerlendirme ölçütlerini okuyun.
    (Öneri — T08/T09)
11. **Akıcı, doğru Türkçe;** çeviri kokmayan İngilizce özet. (Öneri — T08/T09;
    genel rehber)
12. **Görsellerle (şekil/tablo) destekleyin;** biçime de içeriğe gösterdiğiniz
    özeni verin. (Öneri — genel rehber)
13. **Ekip-konu-altyapı örtüşmesini kanıtlayın;** kalabalık/ilgisiz ekipten
    kaçının. (Öneri — T08/T09)
14. **Etik kurul/izin gerektiren çalışmalarda başvuruyu geciktirmeyin** (anket,
    insan verisi, saha). (Resmî — rules `ethics`; genel rehber)
15. **Küçük/kısa projeyle başlayın, erken bitirip birkaç kez okuyun;**
    reddedilirse hakem raporuna göre revize edip yeniden gönderin. (Öneri —
    T08/T09)

---

## Kaynaklar

Yalnız aşağıdaki kaynaklar kullanılmıştır. Resmî olmayan kaynaklar "genel
rehber" diye işaretlenmiştir; kural kaynağı olarak yalnız resmî metni ve
tanınmış fon kurumlarının yayımlanmış ölçütlerini esas alın.

Resmî (TÜBİTAK):

- T01 — [2209-A program sayfası](https://tubitak.gov.tr/tr/burslar/lisans-onlisans/destek-programlari/2209-universite-ogrencileri-arastirma-projeleri-destekleme-programi)
- T02 — 2026 Çağrı Duyurusu (rules `sources` T02)
- T03 — Başvuru İçeriği Bilgi Notu (rules `sources` T03)
- T06 — [Bibliyografik Verilerin Düzenlenmesi](https://tubitak.gov.tr/tr/duyuru/bibliyografik-verilerin-duzenlenmesi)
- T08/T09 — TÜBİTAK Proje Yazma Eğitimi, Bölüm 1 ve Bölüm 2 (resmî eğitim
  sunumu). 2209-A'ya özgü olmayan süreç ayrıntıları (ör. yurtdışı araştırmacı)
  bu programda geçerli olmayabilir; özgün değer/yöntem/başarı ölçütü/B
  planı/yaygın etki mantığı aynı değerlendirme kültüründen gelir.

Genel rehber (resmî değil — çapraz doğrulama için):

- [NSF Merit Review genel bakış](http://www.nsf.gov/bfa/dias/policy/merit_review/overview.pdf)
- [Horizon Europe'da sık proje hataları](https://moose-pelican-xee8.squarespace.com/blog/common-mistakes-in-horizon-europe-proposals)
- [Innovate UK — değerlendiriciden sık hatalar](https://iuk-business-connect.org.uk/wp-content/uploads/2025/02/Evalutors-tips-feb-12th-2025-with-text-boxes.pdf)
- [TÜBİTAK 1002-A başvuru formu yapısı (topluluk şablonu)](https://tr.overleaf.com/latex/templates/tubitak-1002-a-basvuru-formu/zdkqbvmbdfrj)
