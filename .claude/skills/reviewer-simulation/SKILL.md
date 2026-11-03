---
name: reviewer-simulation
description: >-
  Öneriyi bağımsız ve sert bir hakem gibi değerlendirir; ölçüt başına puan,
  gerekçe ve somut düzeltme verir, reddedilme riski en yüksek ilk beş sorunu
  sıralar. Tetik: "hakem gözüyle bak", "bu öneri kabul alır mı", "sert
  değerlendir", "zayıf yanları ne", "panelde ne sorarlar", "reddedilir miyim".
  Claude Code ve Codex'te aynı.
---

# reviewer-simulation — bağımsız sert değerlendirme

## Görev
Öneriyi, yazanı memnun etme kaygısı olmayan bir TÜBİTAK hakemi gibi değerlendir.
Amaç övgü değil; zayıf noktaları başvuru gönderilmeden bulmak.

## Ne zaman
Öneri taslağı (`proposal-writing`) ve tutarlılık denetimi (`consistency-hunt`)
tamamlandıktan sonra, danışmana teslimden önce.

## Girdi → Çıktı
- Girdi: `report/drafts/proposal.md` ve/veya `report/tybs/tybs-application.md`,
  `config.rules()` ölçüt çerçevesi.
- Çıktı: ölçüt başına puanlı değerlendirme + ilk beş reddedilme riski;
  `logs/quality-audit.md`'ye (`config.PATHS["quality_audit"]`) yazılır.

## Bağımsızlık
Mümkünse değerlendirmeyi, yazımı **görmemiş** ayrı bir alt ajan ya da ayrı bir
oturumla yaptır: yalnız son metni oku, yazım gerekçelerini önden alma. Bu
mümkün değilse rolünü bilinçli ayır — "yazar" şapkasını çıkar, metinde yazılana
bak, niyete değil. Ekibin savunmasını değil, metnin kendini kanıtlayıp
kanıtlamadığını değerlendir.

## Değerlendirme ölçütleri
Dört eksen (2209-A paneli). Ağırlıkları `config.rules()["evaluation"]["criteria_weights"]`
dosyasından oku, SABİT yazma (2026 örneği: bilimsel nitelik %35 / yöntem %25 /
proje yönetimi %20 / yaygın etki %20). Eksen adları `evaluation.criteria_weights`
anahtarlarıyla, içerikleri `abstract.scope` ile hizalıdır:

1. **Bilimsel nitelik / özgün değer** (`bilimsel_nitelik`) — Soru net, sınanabilir
   mi? Boşluk gerçek ve kanıtlı mı? Katkı somut mu, "ilk/rakipsiz" söylemi var mı?
2. **Yöntem** (`yöntem`) — Tasarım soruyu yanıtlıyor mu? Değişken, örneklem,
   analiz tutarlı mı? Vaat edilen her ölçütün karşılığı var mı?
3. **Proje yönetimi** (`proje_yönetimi`) — Takvim süre üst sınırı içinde gerçekçi
   mi? İş paketleri, kim-yapar ve katkı payları (toplam 100) tutarlı mı? Risk ve B
   planı inandırıcı mı?
4. **Yaygın etki** (`yaygın_etki`) — `impact_categories` kategorilerinde etki
   somut ve ölçülü mü, yoksa abartılı mı?

Her eksen için ver:
- **Ağırlık** — o yılın `evaluation.criteria_weights` değeri (dosyadan).
- **Puan** (örn. 1-5 veya zayıf/orta/güçlü) — ölçeği başta tanımla. Ağırlıklarla
  bir toplam puan vereceksen hesabı ağırlıklardan türet; eksen ağırlıklarını
  metne sabit yazma.
- **Gerekçe** — metinden somut kanıt/eksik.
- **Somut düzeltme** — "şunu şöyle yap" düzeyinde, uygulanabilir.

Özel gereksinimli birey beyanı doğrulanmışsa, çağrının öngördüğü +1 puan katkısını
(`evaluation.special_needs_bonus`) not düş; bunu puanlama kurgusuna dahil ederken
kaynağını belirt.

| Eksen | Ağırlık (rules) | Puan | Gerekçe (metinden) | Somut düzeltme |
| --- | --- | --- | --- | --- |
| Bilimsel nitelik / özgün değer | | | | |
| Yöntem | | | | |
| Proje yönetimi | | | | |
| Yaygın etki | | | | |

## Reddedilme nedeni olabilecek ilk 5 sorun
Önem sırasıyla, her biri için: sorun · neden reddettirir · nasıl giderilir.
Bunları metindeki gerçek kanıta dayandır; genel tavsiye verme.

## Hata durumları
- Metin eksik/yarım → neyin eksik olduğunu söyle, eksik bölümü puanlama.
- Ayrı ajan/oturum kurulamıyor → "yazar şapkası çıkarıldı" notuyla tek oturumda
  yap; bağımsızlık sınırını açıkça belirt.

## Kalite kontrol
- [ ] Dört eksenin her biri ağırlık + puan + gerekçe + somut düzeltme ile değerlendirildi.
- [ ] Eksen ağırlıkları rules `evaluation.criteria_weights`'ten okundu, sabit yazılmadı.
- [ ] Puan ölçeği baştan tanımlandı.
- [ ] İlk beş reddedilme riski önem sırasıyla, metinden kanıtla verildi.
- [ ] Değerlendirme sert ve bağımsız; ekibin niyetini değil metni esas aldı.
- [ ] Sonuç `logs/quality-audit.md`'ye yazıldı.
