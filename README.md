# tubitak-2209a-kit

[![CI](https://github.com/UzimeStudio/tubitak-2209a-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/UzimeStudio/tubitak-2209a-kit/actions/workflows/ci.yml)

TÜBİTAK 2209-A Üniversite Öğrencileri Araştırma Projeleri başvurusu için Claude Code / Codex çalışma kiti. Fikri netleştirmekten kaynak doğrulamaya, öneri metninden TYBS biçim denetimine ve (proje desteklenirse) sonuç raporuna kadar adım adım ilerler.

> **Önce bunu okuyun.** Bu kiti kendi başvurum için hazırladım; işe yaradığı için olduğu gibi paylaşıyorum. TÜBİTAK ile bir bağı yoktur. Kurallar her yıl değişebilir: çağrı belgelerini kendiniz okuyun, başvurunun son hâlini kendiniz kontrol edin. Kitin çıktılarından doğacak sonuçlar için sorumluluk kabul etmiyorum. Yapay zekâ taslak üretir; metin, kaynaklar ve kararlar sizindir.

## Ne sağlar

- **25 skill**: ajan hangi işte ne yapacağını ve çıtanın nerede olduğunu buradan okur. Claude Code `.claude/skills/`, Codex `.agents/skills/` klasörünü kendiliğinden bulur. İkincisi birincinin kopyasıdır (`tools/sync_skills.py`).
- **12 çalıştırılabilir araç + ortak kütüphaneler** (`tools/`): komut satırından çalışan araçlar (kaynak doğrulama, kaynakça, biçim denetimi, belgeler arası tutarsızlık, var olan taslağı içe alma, DOCX/PDF üretimi) ve bunların paylaştığı kütüphaneler (`config`, `bibkit`, `docxkit`, `stats`, `figstyle`).
- **Hazır promptlar** (`prompts/`): sırayla kopyala-yapıştır.
- **Çağrı kuralları ayrı dosyada** (`rules/2209a-2026.json`): kelime sınırı, bütçe üst sınırı, tarihler. Her değer resmî belgeye bağlı. Yeni yılda yalnız bu dosya yenilenir.
- **Şablonlar** (`templates/`): öneri raporu, TYBS'ye yapıştırılacak metin, izin/onam belgeleri.

## Hızlı başlangıç

Kurulum ayrıntıları: [SETUP.md](SETUP.md).

```bash
git clone <bu-repo> my-2209a && cd my-2209a
uv sync
uv run python tools/init_project.py     # project.json'u sorularla kurar
uv run python tools/status.py           # durum ve sıradaki adım
```

Sonra klasörü Claude Code veya Codex ile açın ve [prompts/01-onboarding.md](prompts/01-onboarding.md) içeriğini yapıştırın.

## Akış

| Adım | Prompt | Skill'ler | Çıktı |
| --- | --- | --- | --- |
| 1. Başlangıç | `01-onboarding.md` | onboarding | `project.json` |
| Hazır taslak varsa | `09-existing-draft.md` | draft-revision | `logs/revision-plan.md` (1. adımdan sonra 2–5 yerine) |
| 2. Fikir | `02-idea-refinement.md` | idea-refinement | `project/project-brief.md` |
| 3. Literatür | `03-literature.md` | academic-research, source-verification, literature-review, literature-synthesis | `sources/references.json`, matris |
| 4. Yöntem, bütçe, takvim | `04-method-budget-timeline.md` | methodology-review, budget-timeline | iş paketleri, bütçe gerekçesi |
| 5. Öneri yazımı | `05-proposal-writing.md` | proposal-writing, academic-turkish, citation-management | `report/drafts/proposal.md`, `report/tybs/tybs-application.md` |
| 6. Denetim | `06-review.md` | consistency-hunt, reviewer-simulation | bulgu tablosu |
| 7. Danışmana teslim | `07-advisor-handoff.md` | academic-audit, tybs-application-check, ai-research-compliance | temiz denetim, ÜYZ beyanı |
| 8. Sonuç raporu | `08-final-report.md` | final-report, docx-engineering, report-consistency | resmî şablonla DOCX/PDF |

## Klasörler

| Klasör | İçerik |
| --- | --- |
| `project/` | Resmî sonuç raporu şablonu, TÜBİTAK kaynak kaydı, gereksinim listesi, TYBS ekran rehberi, proje özeti |
| `rules/` | Çağrı yılına göre kural dosyaları |
| `sources/` | `references.json`, `library.bib`, literatür matrisi, doğrulama kayıtları |
| `data/`, `analysis/` | Ham/işlenmiş veri, analiz betikleri ve çıktıları |
| `figures/`, `tables/` | Şekil ve tablolar |
| `report/` | Taslaklar, TYBS metni, son rapor |
| `logs/` | Kararlar, açık sorular, kalite denetimi, ÜYZ kaydı |
| `templates/`, `prompts/` | Şablonlar ve hazır promptlar |
| `tools/`, `tests/` | Araçlar ve testleri |

## Yeni çağrı yılı

`call-update` skill'ini çalıştırın. `tools/call_watch.py` resmî belgeleri indirip değişeni bulur. Değişiklikler yeni bir `rules/2209a-<yıl>.json` dosyasına kaynak kimliğiyle yazılır.

## Katkı

Hata veya eskimiş kural görürseniz issue açın. Kural değişikliği önerirken resmî belgenin bağlantısını ve madde numarasını yazın.

Değişiklik yaparken:

```bash
uv run --group dev ruff check .
uv run --group dev pytest -q
uv run python tools/sync_skills.py      # skill değiştiyse
```

GitHub Actions bu üç denetimi Windows, macOS ve Linux'ta çalıştırır. Linux'ta LibreOffice ile PDF dönüşümü de sınanır.

## Lisans

[MIT](LICENSE) © 2026 Bilal Abiç
