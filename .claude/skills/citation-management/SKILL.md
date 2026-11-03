---
name: citation-management
description: sources/references.json kaynak listesini yönetir; library.bib ile APA 7 benzeri Türkçe kaynakça satırlarını üretir, DOI ve künye alanlarını denetler. Kaynakça oluşturma, atıf biçimi, BibTeX veya TYBS kaynakça alanı için kullan. Kaynağın gerçekliği source-verification'ın işidir.
---

# citation-management

## Görev
Tek doğruluk kaynağından (references.json) tutarlı kaynakça üretmek.

## Dosyalar
| Dosya | Rol |
| --- | --- |
| `sources/references.json` | Elle bakılan ana liste (status, doğrulayan kayıtlar, notlar) |
| `sources/library.bib` | Türetilir (`bibkit.py bib`), elle düzenlenmez; Zotero vb. içe alabilir |

## Prosedür
1. Yeni kaynak yalnız source-verification sonrası eklenir.
2. Denetim ve üretim:
   ```bash
   uv run python tools/bibkit.py lint
   uv run python tools/bibkit.py bib
   uv run python tools/bibkit.py list <id1> <id2>   # rapor satırları
   ```
   (API: `load()`, `cite_key(r)`, `sort_key(r)`, `format_entry(r)`, `format_entry_apa(r)`, `lint(refs)`, `USABLE`, `STATUSES`.)
3. Biçim: Türkçe APA 7 benzeri; "ve", "vd.", "ss."; DOI `https://doi.org/...` biçiminde. 2209-A sonuç raporu şablonu kaynakça biçimini belirtmez; başvuru için TÜBİTAK "Bibliyografik Verilerin Düzenlenmesi" sayfası esastır (TYBS'de kaynaklar tek tek girilir). Kaynakça karakter sınırı ve DOI zorunluluğu rules dosyasından (`references`) okunur (2026: max_chars 32000, doi_required, all_cited).
4. Metin içi atıf: (Soyad, Yıl); iki yazar "ve"; üç+ yazar "vd.". Aynı yazar-yıl çakışırsa 2020a/2020b.
5. Preprint venue'sunde "ön baskı" yazmalı; lint bunu arar.

## Hata durumları
- Lint "status ... raporda kullanılamaz": kaynak kaynakçadan çıkarılır veya doğrulanır.
- DOI'li kaynakta DOI eksik: eklenir; resolve etmeyen DOI yazılmaz (source-verification).

## Kalite kontrol
- [ ] `bibkit.py lint` temiz.
- [ ] DOI'li her kaynakta DOI var (rules: doi_required).
- [ ] Kaynakçadaki her giriş metinde atıflı, her atıf kaynakçada (rules: all_cited).
