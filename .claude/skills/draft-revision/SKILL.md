---
name: draft-revision
description: >-
  Ekibin elinde zaten var olan bir öneri taslağını (DOCX, PDF, Markdown, TYBS kopyası)
  kite alır, doğrular, sorunları önem sırasıyla bir revizyon planına yazar ve taslağı
  ekiple tur tur ilerletir. Taslağı baştan yazmaz; ekibin metnini korur. Tetik:
  "elimde bir taslak var", "raporumu iyileştir", "mevcut başvuruyu kontrol et",
  "geçen yılki öneriyi güncelle", "danışman düzeltme istedi", "bu metin nerede eksik".
---

# draft-revision — var olan taslağı doğrula, iyileştir, ilerlet

## Görev

Hazır bir taslağı sıfırdan yazmadan teslim edilebilir hâle getirmek. Önce neyin doğru, neyin eksik, neyin uydurma olduğunu kanıtla bulur. Sonra ekibin onayıyla küçük adımlarla düzeltir. Taslağı sıfırdan yazmak `proposal-writing`'in işidir.

## Ne zaman

- Ekip kitle değil kendi başına yazmaya başlamışsa.
- Geçen yıl reddedilen veya gönderilmeyen bir öneri yeniden kullanılacaksa.
- Danışman veya hakem geri bildirimi geldiyse.
- `onboarding` sırasında "taslağım var" denirse.

## Girdi → Çıktı

- Girdi: taslak dosyası; varsa danışman/hakem notları.
- Çıktı: `report/drafts/imported.md` (ilk kopya) · `report/drafts/proposal.md` (çalışılan metin) · `logs/revision-plan.md` (bulgu ve karar tablosu) · güncel `project.json`, `sources/references.json` · `logs/decisions.md` kayıtları.

## İlkeler

- **Özgün dosyaya dokunulmaz.** `tools/import_draft.py` onu `report/drafts/original/` altına kopyalar.
- **Ekibin sesi korunur.** Taahhütnameye göre metni ekip yazmıştır. Paragrafı yeniden yazmak yerine en küçük düzeltme önerilir. Her değişiklik önce gösterilir, onaydan sonra uygulanır.
- **Doğrulanamayan silinmez, işaretlenir.** Kaynağı bulunamayan iddia, uydurma şüphesi olan kaynak, belgesiz ad/tutar/tarih `TBD` olur ve `logs/open-questions.md`'ye eklenir. Yerine yeni bilgi uydurulmaz.
- **Plan ve sonuç ayrılır.** "Yapılmıştır, bulunmuştur" gibi ifadelerin arkasında gerçek kayıt yoksa plan diline çevrilir.
- **Sırayla gidilir.** Eleyici sorun çözülmeden dil cilası yapılmaz.

## Prosedür

### 1. İçe al

```bash
uv run python tools/import_draft.py <taslak.docx|pdf|md>
uv run python tools/status.py
```

Eşleme tablosunda `[YOK]` bölüm eksik demektir. `[ELLE]` ise bölüm başka numarada bulundu demektir (ör. takvim 5.1'de). Eşlemeyi ekiple kısaca teyit et. `report/drafts/proposal.md` yoksa `imported.md`'yi oraya kopyala. Artık çalışılan metin budur. PDF'ten içe alınan metinde tablo ve başlık bozulabilir. Mümkünse DOCX veya Markdown iste.

### 2. Gerçekleri çıkar

Taslaktan başlık, ekip, danışman, süre, bütçe kalemleri ve anahtar kelimeleri oku. Bunları geçici bir `values.json` dosyasına yaz (project.json ile aynı biçimde, yalnız bulduğun alanlar) ve `uv run python tools/init_project.py --merge values.json` ile aktar. Bu yol kabuk tırnak sorunlarından etkilenmez. Yalnız metinde açıkça yazanı al. Taslak kendi içinde çelişiyorsa iki değeri de `logs/open-questions.md`'ye yaz ve sor.

Sonra uygunluğu kontrol et (`rules` dosyasındaki `eligibility`, `language`, `ethics` blokları). Örnekler: aynı anda tek başvuru, öğrenci türü, etik kurul gereksinimi. Burada çıkan sorun ELEYİCİ'dir.

### 3. Kaynakları doğrula

Kaynakçadaki her satır için DOI'yi veya başlığı al:

```bash
uv run python tools/verify_source.py --doi <DOI> --save <id>
uv run python tools/verify_source.py --title "<başlık>" --year <yıl> --author <soyad> --save <id>
```

Kaydı `sources/references.json`'a ekle (`source-verification`). NOT_FOUND veya CONFLICT çıkan kaynak uydurma şüphesidir: ELEYİCİ. Ardından metindeki en güçlü 5–10 iddiayı seç. Atıf verilen kaynağın o iddiayı gerçekten söyleyip söylemediğini oku (`literature-review`). Desteklemiyorsa YÜKSEK.

```bash
uv run python tools/bibkit.py lint
```

### 4. Makine denetimi

```bash
uv run python tools/check_application.py report/drafts/proposal.md
uv run python tools/check_consistency.py
```

TYBS kopyası varsa `--tybs` ile o da denetlenir. Her komutu ayrı çalıştır ve çıkış kodunu ayrı oku.

### 5. İçerik denetimi

Sırayla şu skill'leri uygula:
- `methodology-review`: hedef, yöntem ve ölçüt uyumu.
- `budget-timeline`: takvim, katkı toplamı, bütçe gerekçesi.
- `consistency-hunt`: belgeler arası çelişki.
- `reviewer-simulation`: yazımı görmemiş ayrı bir alt ajanla, rules dosyasındaki değerlendirme ağırlıklarıyla puan.

Danışman veya hakem notu varsa her notu ayrı bulgu yap.

### 6. Revizyon planı

Bulguları `logs/revision-plan.md`'ye bu tabloyla yaz (dosya yoksa oluştur):

| ID | Önem | Tür | Bulgu | Kanıt | Öneri | Karar | Durum |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R01 | ELEYİCİ | doğruluk | Kaynak bulunamadı: … | `verify_source` NOT_FOUND | Kaynağı çıkar veya gerçeğini bul | ekip | açık |

- **Önem:** ELEYİCİ (ön elemede düşürür veya kural ihlali), YÜKSEK (puanı ciddi düşürür), ORTA, DÜŞÜK.
- **Tür:** uygunluk, doğruluk, biçim, yöntem, yönetim, yaygın etki, dil.
- **Kanıt:** araç çıktısı veya `dosya:satır`. Kanıtsız bulgu yazılmaz.

Planı ekibe göster. Ekip her bulgu için kabul, ret veya erteleme kararı verir. Ret gerekçesi `logs/decisions.md`'ye yazılır.

### 7. Tur tur düzelt

Sıra: ELEYİCİ → doğruluk → biçim sınırları → hedef-yöntem-takvim-bütçe zinciri → hakemin en düşük puan verdiği ölçüt → dil (`academic-turkish`).

Her turda tek bir bulgu kümesini ele al:
1. Önerilen değişikliği diff veya önce/sonra olarak göster.
2. Onay gelince uygula.
3. Adım 4'ü yeniden çalıştır.
4. Plan tablosunda durumu güncelle.

Bir turda bütün metin yeniden yazılmaz. ÜYZ katkısını `logs/ai-use-log.md`'ye yaz (`ai-research-compliance`).

### 8. İlerlet

Plan temizlenince taslağın nerede olduğuna bak:

| Durum | Sıradaki skill |
| --- | --- |
| Literatür ince, boşluk kanıtsız | `academic-research` → `literature-synthesis` |
| Yöntem veya ölçüt belirsiz | `methodology-review` |
| Bölüm eksik | `proposal-writing` (yalnız eksik bölüm) |
| Metin tamam, TYBS kopyası yok | `proposal-writing` TYBS aktarımı |
| Her şey temiz | `academic-audit` → danışmana teslim |

## Durma ölçütü

- ELEYİCİ ve YÜKSEK bulgu kalmadı ya da ekip gerekçesiyle kabul etti.
- `check_application` ve `check_consistency` sorunsuz çıkıyor.
- `reviewer-simulation` puanı her ölçütte ekibin kabul ettiği düzeyde.

## Hata durumları

- PDF'ten metin çıkmıyorsa dosya taranmış olabilir. Ekipten DOCX veya metin iste.
- Taslak eski çağrı yılına göre yazılmışsa sınırlar değişmiş olabilir. `rules` dosyasıyla karşılaştır. Gerekiyorsa önce `call-update` çalıştır.
- Ekip bir bulguyu kabul etmezse uygulama. Kararı kaydet ve devam et.

## Kalite kontrol

- [ ] Özgün dosya `report/drafts/original/` altında ve değişmedi.
- [ ] Her bulgunun kanıtı var; her kararın sahibi ekip.
- [ ] Doğrulanmamış kaynak metinde kalmadı.
- [ ] Yeni eklenen her sayı, ad ve tarih bir dosyaya veya ekibe dayanıyor.
- [ ] Plan dilinde yazılması gereken hiçbir cümle sonuç gibi durmuyor.
- [ ] Değişiklikler küçük ve gösterilerek yapıldı; ekibin anlatımı korundu.
