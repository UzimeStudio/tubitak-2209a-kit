---
name: academic-research
description: Araştırma sorusundan tekrarlanabilir bir arama stratejisi üretir; Türkçe (DergiPark, YÖK Ulusal Tez Merkezi) ve uluslararası (Crossref, OpenAlex, Semantic Scholar, Google Scholar, yayıncı sayfaları) kaynaklarda tarar, search-log tutar ve "konuyu kapatan en küçük kaynak seti" ilkesiyle durur. "Literatür tara", "bu konuda çalışma var mı", "anahtar kelime üret", "boşluğu kanıtla" isteklerinde kullan. Bulunan adayın doğrulanması source-verification'ın işidir.
---

# academic-research

## Görev
Araştırma sorularına uygun aday kaynakları sistematik ve tekrarlanabilir biçimde bulmak. Bulmak ≠ doğrulamak ≠ okumak. Hedef, çok kaynak değil **konuyu kapatan en küçük set**: öncülleri, karşıt bulguları ve Türkçe bağlamı temsil eden yeter sayıda kaynak. 2209-A için sabit bir sayı yoktur; rules dosyasındaki `references.max_chars` (2026: 32000) kaynakçanın pratik üst sınırını belirler.

## Ne zaman
- Literatür boşluğu / özgünlük iddiası yazılmadan önce. Taslak "boşluk aday katkıdır" der; search-log olmadan kesinleştirilmez.
- Yeni yöntem, karşıt bulgu veya Türkçe kaynak arandığında.

## Girdi → Çıktı
- Girdi: araştırma sorusu veya konu.
- Çıktı: `sources/search-log.md` girdisi + aday listesi (henüz doğrulanmamış). Adaylar source-verification'a gider.

## Prosedür
1. **Kavram tablosu** kur: her kavram için TR + EN terimler ve eş anlamlılar (konunun temel olgusu, yöntemi, bağlamı, karşılaştırma ekseni). Eş anlamlıları tam yazmak recall'ı belirler.
2. **Query** dizeleri üret (Boolean): `(terimA OR eşanlamlıA) AND (terimB OR eşanlamlıB) AND (bağlam)`. Aynı query hem TR hem EN terimlerle kurulur.
3. **Veri tabanı seçimi** — Türkçe ve uluslararası birlikte taranır:
   | Kaynak | Erişim | Not |
   | --- | --- | --- |
   | DergiPark | web arayüzü | Türkçe hakemli literatür; API yok, elle arama + log. Bot doğrulaması çıkarsa site-kısıtlı web araması yedektir, arayüzün yerine geçmez |
   | YÖK Ulusal Tez Merkezi | web arayüzü | Türkçe tez; bitişik ifade araması, uzun listeler kısmen okunur |
   | OpenAlex API | anahtarsız (tools/verify_source.py aynı endpoint'i kullanır) | geniş kapsam |
   | Crossref API | anahtarsız | DOI'li yayınlar |
   | Semantic Scholar API | anahtarsız, düşük rate limit (429) | API key isteğe bağlı, kullanıcı onayıyla |
   | Google Scholar | web arayüzü | otomatik kazıma yapılmaz; elle tamamlayıcı, atıf zinciri izlemek için |
   | Alan yayıncıları (konferans/dergi) | yayıncı sayfası | DOI'siz veya veri tabanında eksik yayınlar |
4. OpenAlex hızlı arama: `curl -s "https://api.openalex.org/works?search=<query>&filter=from_publication_date:<yıl>-01-01&per-page=25"`; sonuç sayısı ve tarih log'a yazılır.
5. **İleri/geri citation chain** (en küçük set için en güçlü yol): çekirdek bir kaynaktan, atıf verdiği öncüller (geri) ve ona atıf verenler (ileri) izlenir. Bu, körlemesine anahtar kelime taramasından daha hızlı doyuma ulaştırır.
6. **Log** (`sources/search-log.md`): her satırda tarih, veri tabanı, query dizesi, filtre, sonuç sayısı, taranan sayı, dahil/dışlama gerekçesi.
7. **Doyum / durma ölçütü** ("en küçük set"): yeni aramalar yalnız zaten elde olan kaynakları döndürmeye başladığında ve her alt tema (öncül yöntem, karşıt/sınır bulgu, Türkçe bağlam) en az bir doğrulanabilir kaynakla temsil edildiğinde durulur. Durma gerekçesi log'a yazılır.
8. **Özgünlük/boşluk kanıtı**: boşluk ancak taranan kaynaklara koşullu yazılır — "taranan kaynaklarda (bkz. search-log, <tarih>) … bulunmamıştır". "İlk/tek çalışma" yazılmaz; yokluk, literatürde yokluk kanıtı değildir.

## Hata durumları
- API 429: bekle/yeniden dene; Semantic Scholar'ı atla, log'a yaz.
- Hiç sonuç yok: bu "literatürde yok" kanıtı değildir; log'a "bulunamadı" yazılır.
- DergiPark arayüzü bot doğrulaması istiyor: yedek web araması kullanılır, log'da arayüzün kullanılamadığı belirtilir.

## Kalite kontrol
- [ ] Her arama search-log'da tarih ve query ile var.
- [ ] Hem Türkçe (DergiPark/YÖK) hem uluslararası veri tabanı tarandı.
- [ ] Durma, doyum ölçütüyle gerekçelendirildi; set konuyu kapatacak en küçük boyutta.
- [ ] Adaylar doğrulanmadan kaynakçaya eklenmedi.
- [ ] "İlk/tek/literatürde hiç yok" ifadesi kullanılmadı.
