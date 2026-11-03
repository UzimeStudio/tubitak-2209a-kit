# tubitak-2209a-kit — ajan kuralları

TÜBİTAK 2209-A başvurusu ve (proje desteklenirse) sonuç raporu için çalışma alanı. Claude Code bu dosyayı, Codex `AGENTS.md` üzerinden aynı kuralları okur. İş adımları `.claude/skills/` altındaki skill'lerdedir. Codex aynı skill'leri `.agents/skills/` kopyasından okur. Skill değiştirdiysen `uv run python tools/sync_skills.py` çalıştır.

## İlk açılış

`project.json` yoksa `onboarding` skill'i ile başla. Her oturumda önce `uv run python tools/status.py` çalıştır, sonra `project-context` skill'ini uygula.

## Temel ilkeler

1. **Doğruluk önce gelir.** Hız ve biçim için doğruluktan ödün verilmez.
2. **Doğrulanmamış kaynak kullanılmaz.** Her kaynak `source-verification` skill'inden geçer. Durumu VERIFIED, PARTIAL veya PUBLISHER_PAGE olmayan kaynak metne girmez.
3. **Veri uydurulmaz.** Synthetic veri yalnız altyapı testinde kullanılır, "SENTETİK" diye işaretlenir ve sonuç olarak yazılmaz.
4. **Yapılmamış iş yapılmış gibi yazılmaz.** Hedef, plan ve sonuç ayrı yazılır.
5. **Bilinmeyen bilgi uydurulmaz.** Ad, onay, tarih, tutar bilinmiyorsa `TBD` yazılır, `logs/open-questions.md`'ye eklenir ve kullanıcıya sorulur.
6. **Yöntem ve sonuç tutarlıdır.** Vaat edilen her ölçüt ya raporlanır ya da gerekçesiyle "yapılamadı" yazılır.
7. **Sınırlılıklar gizlenmez.**
8. **Çağrı kuralları koddan değil `rules/` dosyasından okunur.** Sınır, tarih ve tutar ezberden yazılmaz. Yeni çağrı yılında `call-update` skill'i kullanılır.
9. **Resmî şablon korunur.** `project/official-report-template.docx` üzerinde yalnız içerik eklenir (`docx-engineering`).
10. **ÜYZ kullanımı şeffaftır.** Katkı `logs/ai-use-log.md`'ye yazılır (git dışı). Beyan `ai-research-compliance` skill'iyle hazırlanır.
11. **Metin ekibindir.** TYBS taahhüdü önerinin ekip tarafından yazıldığını söyler. Ajan taslak ve düzeltme önerir; son metni ekip kendi sözleriyle sahiplenir. Ajan onay vermez, form göndermez.

## Dil

İçerik akademik Türkçe (`academic-turkish`). Dosya, klasör, kod tanımlayıcısı, CLI komutu ve teknik terimler İngilizce kalır.

## Doğruluk kaynakları

| Konu | Dosya |
| --- | --- |
| Proje bilgisi (başlık, ekip, bütçe, süre) | `project.json` |
| Çağrı kuralları | `rules/2209a-<yıl>.json`, `project/tubitak-sources.md` |
| Gereksinim listesi | `project/requirements-checklist.md` |
| Proje fikri | `project/project-brief.md` |
| Kaynakça | `sources/references.json` (→ `library.bib`) |
| Gerçekleşmiş sonuç | Yalnız `analysis/analysis-log.md` ve `analysis/outputs/` |
| Kararlar / açık sorular | `logs/decisions.md`, `logs/open-questions.md` |

## Komutlar

```bash
uv sync
uv run python tools/status.py                      # durum ve sıradaki adım
uv run python tools/init_project.py                # project.json kurulumu (--set path=value)
uv run python tools/verify_source.py --doi <DOI> --save <id>
uv run python tools/bibkit.py lint|bib|list
uv run python tools/matrix.py validate
uv run python tools/check_application.py report/tybs/tybs-application.md --tybs
uv run python tools/check_consistency.py
uv run python tools/md2docx.py report/drafts/proposal.md report/drafts/proposal.docx
uv run python tools/docx_to_pdf.py <docx>          # Word veya LibreOffice
uv run python tools/pdf_check.py <pdf>
uv run python tools/check_report.py <docx>
uv run python tools/call_watch.py                  # resmî belgeler değişti mi
uv run --group dev pytest                          # kit testleri
```

## Onay gerektirenler

Ücretli API veya abonelik, API anahtarı girişi, sistem geneli kurulum, dış servise proje verisi gönderme, `report/final/` üzerine yazma, commit/push. Kaynak doğrulama sorguları yalnız yayımlanmış künyeleri (başlık/DOI) gönderir.
