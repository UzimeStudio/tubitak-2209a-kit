---
name: proposal-writing
description: >-
  Öneri raporunu şablondan bölüm bölüm yazar; her bölüm için hakemin aradığını,
  uzunluk kuralını ve yaygın hatayı gözetir, sonra TYBS biçimine aktarır. Tetik:
  "öneriyi yazalım", "özet bölümünü yaz", "giriş nasıl olmalı", "yöntem bölümü",
  "TYBS'ye aktar", "başvuru metnini hazırla". Claude Code ve Codex'te aynı.
---

# proposal-writing — öneri raporunun yazımı

## Görev
`templates/proposal.md` şablonundan başlayarak öneri raporunu bölüm bölüm yaz;
sonra metni TYBS başvuru biçimine aktar. Model düzeltir ve çıtayı korur; içerik
ekibin fikrine dayanır.

## Ne zaman
Fikir netleşip (`idea-refinement`) ve özgünlük boşluğu kanıtlanınca
(`academic-research`). Yazım bitince denetim için `consistency-hunt` ve
`reviewer-simulation`'a geç.

## Girdi → Çıktı
- Girdi: `project/project-brief.md`, doğrulanmış kaynaklar
  (`sources/references.json`), şablon `templates/proposal.md`.
- Çıktı: `report/drafts/proposal.md` (`config.document("proposal")`) ve ardından
  `report/tybs/tybs-application.md` (`config.document("tybs")`).

## Bölüm bölüm yaz
Her bölümde önce ekibin taslağını/madde işaretlerini al, sonra sen düzelt. Uzunluk
kuralları `config.rules()` üzerinden okunur; aşağıdaki değerler 2026 örneğidir.

- **Özet** — Hakem: bilimsel nitelik, yöntem, proje yönetimi ve yaygın etkiyi
  tek paragrafta görmek ister (`rules()["abstract"]["scope"]`). Uzunluk:
  `abstract.min_words`–`max_words` (2026: 25-450 kelime). Yaygın hata: sonuç
  varmış gibi yazmak; plan ve sonuç ayrı kalır.
- **1.1 Problem ve önemi** — Hakem: neden önemli, kime değerli. Alt sınır
  `section_min_chars.min_chars` (2026: 350 karakter). Yaygın hata: genel geçer
  giriş; somut boşluğa inmemek.
- **1.2 Literatür / çerçeve** — Hakem: alanı tanıyor musun, boşluk gerçek mi.
  Yaygın hata: atıfsız iddia; doğrulanmamış kaynak.
- **2. Özgün değer / amaç-soru-hipotez** — Hakem: katkı net ve sınanabilir mi.
  Alt sınır `section_min_chars` (2026: 350 karakter). Yaygın hata: "ilk/rakipsiz"
  iddiası; sınanamayan hipotez.
- **Yöntem** — Hakem: tasarım, değişken, analiz, örneklem tutarlı mı. Zengin
  metin, alt sınır rules dosyasından. Yaygın hata: yöntemde vaat edilen ölçütün
  sonuçta karşılığının olmaması.
- **3.1 Çalışma Takvimi** — Hakem: iş adımları, kim yapıyor, başarı ölçütü ve
  katkı payı. Kurallar: `work_plan.columns`, katkı toplamı `contribution_total`
  (100), `forbidden_steps` (literatür tarama / sonuç rapor / sonuçların paylaşım
  / malzeme alım iş adımı olarak yazılmaz). Yaygın hata: katkı toplamının 100
  olmaması; yasak adımı iş paketi yapmak.
- **3.2 Riskler / B planı · 3.3 Olanaklar** — Hakem: gerçekçi risk ve mevcut
  altyapı. Yaygın hata: "risk yok" demek.
- **4. Yaygın Etki** — `impact_categories` (Bilimsel/Akademik;
  Ekonomik/Ticari/Sosyal; Yeni Proje). Yaygın hata: abartılı ticari vaat.
- **Kaynakça** — `references.max_chars` (2026: 32000), `references.doi_required`,
  metindeki her kaynağa atıf (`references.all_cited`). Yaygın hata: atıfsız
  kaynak ya da kaynaksız atıf.

## Hakemin baktığı yer

Her bölümü yazmadan önce iki kaynağa bak:
- rules dosyasındaki `section_requirements.<bölüm>`: TÜBİTAK'ın o bölümde istediği içerik (resmî).
- `project/writing-guide.md`: o bölümde hakemin aradığı, sık hata, zayıf → güçlü cümle örneği.

Yazdıktan sonra `uv run python tools/check_writing.py <md>` çalıştır. Uyarıları tek tek değerlendir: her uyarı hata değildir, ama gerekçesiz bırakma.

## Atıf kuralı
Atıf **yalnız** `sources/references.json`'daki doğrulanmış kayıtlardan yapılır:
status `bibkit.USABLE` kümesinde (VERIFIED, PARTIAL, PUBLISHER_PAGE) olanlar.
Künye uydurma. BibTeX üretmek/denetlemek için:
`uv run python tools/bibkit.py bib` ve `uv run python tools/bibkit.py lint`.

## TYBS'ye aktarım
Taslak onaylanınca metni TYBS biçimine `report/tybs/tybs-application.md`'ye aktar:
- Başlık `title.max_chars` (2026: 495), anahtar kelime `keywords.min`-`max`
  `keywords.separator` ile (2026: 3-5, virgül).
- 3.1 / 3.3 / 4 bölümleri TYBS'de tablo veya sabit kategori biçimindedir
  (`tybs_sections`); düz metni bu yapıya böl.
- Görsel uzantıları `images.extensions` (.jpg/.jpeg/.png).
- Marka yasağı: başlık ve öneride kurum/firma/ürün öne çıkarılmaz (`brand_ban`);
  kaynakça künyesindeki yayın yeri adları hariç.
- Biçim denetimi: `uv run python tools/check_application.py report/tybs/tybs-application.md --tybs`.

## Hata durumları
- Şablon yoksa → kullanıcıya `templates/proposal.md`'nin eksik olduğunu söyle; uydurma.
- Doğrulanmış kaynak yetersiz → `academic-research`/`source-verification`'a dön; atıf ekleme.
- Uzunluk aşımı → bölümü kısalt; kuralı esnetme.

## Kalite kontrol
- [ ] Her bölüm şablondan, ekibin taslağı üzerinden yazıldı; model düzeltici rolde.
- [ ] Uzunluk/sayı sınırları `config.rules()`'dan okundu, sabit yazılmadı.
- [ ] Atıfların tümü `references.json`'daki USABLE kayıtlardan; uydurma künye yok.
- [ ] Çalışma Takvimi katkı toplamı 100; yasak iş adımı yok.
- [ ] Plan ve sonuç ayrı; "ilk/rakipsiz" iddiası yok.
- [ ] TYBS aktarımı yapıldı; `check_application.py --tybs` çalıştırıldı.
