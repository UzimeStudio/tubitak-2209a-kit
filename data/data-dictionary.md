# Data dictionary

Bu dosya analiz tablolarının sütunlarını tanımlar. Her yeni değişken (sütun) kullanılmadan önce buraya eklenir: ad, tür, olası değerler, birim ve kısa açıklama. Gerçek veri alan adları projenin kendi veri sözleşmesinden alınır; burada yeniden icat edilmez.

## Kurallar
- `data/raw/` read-only; sütun tanımı değişince bu dosya güncellenir, raw data değil.
- Her değişkenin türü net olmalı: `int`, `float`, `bool`, `category`, `text`, `datetime (UTC)`.
- Kategorik değişkenin bütün olası değerleri listelenir (ör. sonuç sınıfları).
- Unit açıkça yazılır (oran 0–1, süre s, sayı adet).
- `missing`/`ölçülemedi` için kullanılan kodlama belirtilir ("ölçülemedi" ile "gözlenmedi" ayrı).
- Synthetic test verisinde her satırda `synthetic=True` flag'i bulunur ve analiz script'i bunu `assert` ile doğrular.

## Şablon

| Sütun | Tür | Değerler | Unit | Açıklama |
| --- | --- | --- | --- | --- |
| id | text | `ÖRNEK-NNN` | — | Birim tanımlayıcı; gerçek tanımlayıcı veri sözleşmesinden |
| group | category | ÖRNEK (kurgusal): grup-A, grup-B | — | Tabaka/grup değişkeni |
| indicator | int | 0, 1 | — | İlgilenilen ikili gösterge |
| rater_a, rater_b | category | gözlendi, gözlenmedi, belirsiz | — | Bağımsız rater kararları (Cohen's kappa için) |
| measured_at | datetime (UTC) | ISO 8601 | — | Ölçüm zamanı |
| synthetic | bool | True | — | Yalnız synthetic test verisinde; her satırda True |

## ÖRNEK (kurgusal) — synthetic altyapı testi tablosu

Konu-bağımsız örnek; gerçek sonuç üretmez. Gerçek çalışmada bu bölüm projenin kendi değişkenleriyle değiştirilir.

| Sütun | Tür | Değerler | Açıklama |
| --- | --- | --- | --- |
| id | text | `SYN-NNN` | Synthetic kimlik; gerçek değil |
| group | category | grup-A … grup-E | ÖRNEK beş tabaka |
| indicator | int | 0/1 | Synthetic ikili gösterge |
| rater_a, rater_b | category | gözlendi, gözlenmedi, belirsiz | Synthetic rater kararları |
| synthetic | bool | True | Her satırda True |
