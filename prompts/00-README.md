# Promptlar — kopyala-yapıştır başvuru akışı

Bu klasördeki promptlar, 2209-A başvurusunu baştan sona yürütmek için
Claude Code veya Codex'e olduğu gibi yapıştırılacak hazır metinlerdir. Her
prompt bir skill'i tetikler; metni değiştirmeden kullanabilirsin.

## Sıra ve ne zaman

| # | Prompt | Ne zaman | Tetiklediği skill |
| --- | --- | --- | --- |
| 01 | `01-onboarding.md` | Kiti ilk açtığında | onboarding |
| 02 | `02-idea-refinement.md` | Fikir ham/belirsizken ya da seçim gerektiğinde | idea-refinement |
| 03 | `03-literature.md` | Fikir netleşince, özgünlük boşluğunu kanıtlamak için | academic-research → literature-review → literature-synthesis |
| 04 | `04-method-budget-timeline.md` | Boşluk netleşince, yöntem/bütçe/takvim kurarken | methodology-review, budget-timeline |
| 05 | `05-proposal-writing.md` | Yöntem oturunca, öneri metnini yazarken | proposal-writing (+ academic-turkish, citation-management) |
| 06 | `06-review.md` | Taslak bitince, danışmana vermeden önce | consistency-hunt, reviewer-simulation |
| 07 | `07-advisor-handoff.md` | Denetim geçince, danışman onayına hazırlarken | academic-audit, tybs-application-check |
| 08 | `08-final-report.md` | Proje desteklenir ve süre bitince (sonuç raporu) | final-report |
| 09 | `09-existing-draft.md` | Elinde hazır bir taslak varsa (01'den sonra 02–05 yerine) | draft-revision |

## Kullanım
1. Sıradaki promptu aç, tümünü kopyala, ajana yapıştır.
2. Ajan senden bilgi isterse kendi cümlelerinle cevapla; ajan fikri dayatmaz.
3. Bilinmeyeni `TBD` bırak; uydurma. Açık sorular `logs/open-questions.md`'de toplanır.
4. Son karar ve bilimsel sorumluluk ekiptedir; ajan taslak üretir, onay vermez.

Not: Promptlar çağrıya bağlı sayı (kelime sınırı, bütçe, süre) içermez; bunlar
`rules/2209a-2026.json`'dan okunur. Yeni çağrıda yalnız rules dosyasını güncelle.
