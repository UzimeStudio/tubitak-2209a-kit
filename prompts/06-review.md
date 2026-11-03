# 06 — Denetim ve hakem simülasyonu

> Tetiklediği skill'ler: **consistency-hunt**, **reviewer-simulation**. Taslak bitince, danışmana vermeden önce kullan.

---

Öneri taslağı hazır (`report/drafts/proposal.md`,
`report/tybs/tybs-application.md`). Başvuruyu göndermeden önce iki aşamalı
denetim yap:

1. `consistency-hunt`:
   - Önce araçları çalıştır: `tools/check_consistency.py`,
     `tools/check_application.py --tybs`, `tools/bibkit.py lint`.
   - Sonra makinenin yakalayamadığını elle ara: hedef↔yöntem↔takvim↔bütçe↔risk
     zinciri, ekip görev dağılımı ve bağımsızlık, iddia↔kaynak eşlemesi,
     plan/sonuç karışması, belgeler arası değer tutarlılığı.
   - Bulguları önem sırasıyla tablo yap; `logs/quality-audit.md`'ye yaz.

2. `reviewer-simulation`:
   - Öneriyi sert ve bağımsız bir TÜBİTAK hakemi gibi değerlendir. Mümkünse
     yazımı görmemiş ayrı bir oturum/alt ajan kullan.
   - Dört eksende (bilimsel nitelik/özgün değer, yöntem, proje yönetimi, yaygın
     etki) puan + gerekçe + somut düzeltme ver.
   - "Reddedilme nedeni olabilecek ilk 5 sorunu" önem sırasıyla listele.

Çıktıları bana özetle; düzeltmeleri uygulamadan önce onayımı al. Hazır olunca
beni `07-advisor-handoff.md` adımına yönlendir.
