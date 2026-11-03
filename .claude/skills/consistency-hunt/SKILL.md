---
name: consistency-hunt
description: >-
  Belgeler arası tutarsızlıkları önce araçlarla, sonra makinenin yakalayamadığı
  mantıksal zincirlerle elle avlar; bulguları önem sırasıyla tablolar. Tetik:
  "tutarsızlık var mı", "belgeler çelişiyor mu", "tutarlılık denetimi", "hedef
  yöntem takvim uyuşuyor mu", "iddia kaynak eşleşiyor mu", "son kontrol".
  Claude Code ve Codex'te aynı.
---

# consistency-hunt — belgeler arası tutarsızlık avı

## Görev
Öneri ve TYBS metni ile destekleyici belgeler arasındaki tutarsızlıkları bul.
Önce otomatik araçları çalıştır; sonra araçların göremeyeceği mantıksal
zincirleri elle ara. Araç temizdir demek metin tutarlıdır demek değildir.

## Ne zaman
Öneri yazımı (`proposal-writing`) bitince, `reviewer-simulation`'dan önce veya
onunla birlikte, danışmana teslimden önce.

## Girdi → Çıktı
- Girdi: `report/drafts/proposal.md`, `report/tybs/tybs-application.md`,
  `sources/references.json`, `project.json`.
- Çıktı: önem sırasıyla tutarsızlık tablosu; `logs/quality-audit.md`'ye eklenir.

## Prosedür

### 1. Otomatik denetim (önce)
Komutları **ayrı ayrı** çalıştır; her birinin **çıkış kodunu tek tek oku**
(0 = temiz, 1 = sorun var, 2 = ayar hatası). Tek satırda `&&`/`;` ile zincirleme:
biri başarısız olunca diğerleri atlanmasın ve hangi kodun hangi araçtan geldiği belli olsun.
- `uv run python tools/check_consistency.py` — belgeler arası tutarsızlık.
- `uv run python tools/check_application.py --tybs` — TYBS biçim/sınır denetimi
  (varsayılan `document("tybs")`, yoksa `document("proposal")`).
- `uv run python tools/bibkit.py lint` — kaynakça künye/DOI/atıf denetimi.

Her aracın bulgusunu tabloya al. Araç çıktısını olduğu gibi aktar; süsleme.

### 2. Elle av (makinenin yakalayamadığı)
Araçlar biçimi ve sayıyı görür; mantığı görmez. Şu zincirleri elle izle:

- **Hedef ↔ yöntem ↔ takvim ↔ bütçe ↔ risk zinciri:** Her hedefi yöntem
  karşılıyor mu? Yöntemdeki her iş takvimde var mı ve süre üst sınırına sığıyor
  mu? Takvimdeki iş bütçeyle destekleniyor mu? Her ciddi riskin B planı var mı?
  Zincirde kopan halka tutarsızlıktır.
- **Ekip görev dağılımı:** Her iş paketinde sorumlu belli mi? Bir kişi aynı anda
  çakışan işlerde mi? Bağımsızlık gereken yerde (örn. etiketleme) aynı kişi hem
  üretip hem değerlendiriyor mu?
- **İddia ↔ kaynak eşlemesi:** Metindeki her sayısal/olgusal iddia bir kaynağa
  ya da projenin kendi planına dayanıyor mu? Kaynak söylenen şeyi gerçekten
  söylüyor mu, yoksa abartılmış mı? `references.json`'da olmayan bir kaynağa atıf var mı?
- **Plan/sonuç karışması:** "Yapılacak" ile "yapıldı/bulundu" birbirine karışmış
  mı? Henüz olmayan bir sonuç olmuş gibi mi yazılmış? Özette sonuç iması var mı?
- **Belgeler arası değer tutarlılığı:** Aynı sayı (süre, bütçe, örneklem, eşik)
  öneride ve TYBS'de aynı mı? `project.json`'daki değerle metin uyuşuyor mu?

### 3. Bulguları sırala
Önem sırasıyla (başvuruyu reddettirebilecek > biçimsel) tabloya yaz:

| Önem | Bulgu | Nerede (dosya/bölüm) | Kaynak (araç/elle) | Düzeltme |
| --- | --- | --- | --- | --- |
| Yüksek | | | | |
| Orta | | | | |
| Düşük | | | | |

## Hata durumları
- Araç yoksa/hata veriyorsa → hangi aracın çalışmadığını söyle, elle denetimi
  yine de yap; "çalıştırılamadı" diye işaretle.
- Belge eksikse → eksik belgeyi bildir, o belgeye bağlı denetimi atla.

## Kalite kontrol
- [ ] `check_consistency.py`, `check_application.py --tybs`, `bibkit.py lint`
      çalıştırıldı; çıktılar tabloya alındı.
- [ ] Hedef-yöntem-takvim-bütçe-risk zinciri elle izlendi.
- [ ] Ekip görev dağılımı ve bağımsızlık elle kontrol edildi.
- [ ] İddia-kaynak eşlemesi ve plan/sonuç karışması elle arandı.
- [ ] Bulgular önem sırasıyla tablolandı; `logs/quality-audit.md`'ye yazıldı.
