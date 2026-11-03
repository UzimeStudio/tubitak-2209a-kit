---
name: ai-research-compliance
description: TÜBİTAK Üretken Yapay Zekâ (ÜYZ) Rehberi ve 2209-A çağrısına göre yapay zekâ kullanımını kaydeder, beyan metni taslağı çıkarır ve yasak kullanımları engeller. ÜYZ ile metin, kod, analiz veya görsel üretildiğinde; "yapay zekâ beyanı", "ÜYZ kaydı", "yapay zekâyı nasıl beyan ederim" isteğinde kullan.
---

# ai-research-compliance

## Görev
ÜYZ kullanımını şeffaf, gerçeğe uygun ve doğrulanmış tutmak. Son karar ve bilimsel sorumluluk ekiptedir; danışman da ÜYZ içeriğinin doğruluğundan sorumludur.

## Ne zaman
- Her ÜYZ ile içerik (taslak, kod, analiz, görsel) üretilen oturumdan sonra.
- Çağrının ÜYZ beyan alanı doldurulurken.

## Girdi → Çıktı
- Girdi: ÜYZ oturumunun ne ürettiği.
- Çıktı: `logs/ai-use-log.md`'ye satır (git dışı); istenirse beyan metni taslağı.

## Kaynak kurallar (`project/tubitak-sources.md`'den doğrula)
- **Beyan zorunlu**: bölüm taslağı, analiz kodu, veri analizi, görsel, ana argümanı destekleyen içerik üretimi önemli ölçüde kullanımdır.
- **Beyan içeriği** (rules `ai_disclosure.content`): araç adı + sürüm; aşama/bölüm; kullanımın niteliği.
- **Sorumluluk**: her çıktı (metin, veri, kod, reference) doğrulanır; uydurma/çarpıtma/aşırma akademik etik ihlalidir.
- **Beyanın yeri**: ÜYZ Rehberi (T05 §1.2.2) beyanın TÜBİTAK çevrimiçi başvuru sisteminde bu amaçla ayrılmış bölümde yapılmasını ister. rules `ai_disclosure.note`, 2026 TYBS ekranında böyle bir serbest beyan alanının görülmediğini (yalnız ÜYZ Kaynakça Taahhütnamesi) bir gözlem olarak kaydeder. Bu iki şeyi ayrı tut: rehberin istediği beyan yükümlülüğü ile ekranda fiilen görülen alan aynı değildir; alanın yeri netleşmiyorsa BİDEB'e veya danışmana sorulur, uydurulmaz.

## Prosedür
1. Her ÜYZ oturumundan sonra `logs/ai-use-log.md`'ye satır eklenir: tarih · araç/sürüm · aşama/bölüm · nitelik · çıktı dosyası · insan doğrulaması (kim/ne zaman). Araç sürümü bilinmiyorsa "sürüm kaydedilmedi" yazılır, uydurulmaz.
2. Yasaklar (her istekten önce kontrol):
   - Veri, ölçüm, deney sonucu veya kaynak uydurmak.
   - Yapılmamış işi yapılmış göstermek; hedefi sonuç gibi yazmak.
   - Danışman/uzman incelemesi yapılmış gibi yazmak.
   - Gizli proje verisini veya kişisel veriyi dış servise göndermek.
3. ÜYZ'nin ürettiği her künye `source-verification`'dan, her sayı kaynağından, her kod testten geçer.
4. Beyan taslağı istendiğinde yalnız `logs/ai-use-log.md`'de gerçekten kayıtlı kullanımlardan derlenir; ekip ve danışman onayına sunulur, sisteme ekip girer.
5. Metinde ÜYZ'den doğrudan alınan ifade varsa alıntı gibi işaretlenir.

## Beyan taslağı iskeleti (doldurulmadan kullanılmaz)
> Kullanılan araç(lar): <ad, sürüm>. Kullanıldığı bölümler: <…>. Kullanımın niteliği: <ilk taslak / dil düzeltme / kod / analiz / görsel>. Tüm çıktılar ekip tarafından <yöntem> ile doğrulanmıştır.

## Hata durumları
- Geçmiş oturumların araç/sürüm kaydı yoksa: beyanda uydurulmaz, "sürüm kaydedilmedi" veya boşluk `logs/open-questions.md`'ye yazılır.

## Kalite kontrol
- [ ] ÜYZ kaydı bu oturumu içeriyor.
- [ ] Beyandaki her satırın kayıtta karşılığı olan gerçek bir kullanım var.
- [ ] İnsan doğrulaması boş olan çıktı teslim edilmedi.
