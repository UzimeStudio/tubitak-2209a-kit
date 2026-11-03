# 05 — Öneri yazımı ve TYBS aktarımı

> Tetiklediği skill: **proposal-writing** (yanında academic-turkish, citation-management). Yöntem oturunca kullan.

---

Yöntem, bütçe ve takvim hazır. `proposal-writing` skill'ini uygula:

1. `templates/proposal.md` şablonundan başlayarak öneriyi bölüm bölüm yaz
   (`report/drafts/proposal.md`). Her bölümde önce benim madde işaretlerimi/
   taslağımı al, sonra sen düzelt. Uzunluk ve sayı sınırlarını
   `rules/2209a-2026.json`'dan oku, sabit yazma.
2. Dili `academic-turkish` ile akademik ama sade tut; teknik terimler İngilizce kalır.
3. Atıf yalnız `sources/references.json`'daki doğrulanmış kayıtlardan
   (`citation-management`). Uydurma künye yok. Kaynakçayı `tools/bibkit.py bib`
   ile üret, `tools/bibkit.py lint` ile denetle.
4. Çalışma Takvimi katkı toplamı 100 olsun; plan ile sonucu karıştırma.
5. Taslak onaylanınca metni TYBS biçimine aktar
   (`report/tybs/tybs-application.md`) ve
   `uv run python tools/check_application.py report/tybs/tybs-application.md --tybs`
   ile biçimi denetle.

Bittiğinde beni `06-review.md` adımına yönlendir.
