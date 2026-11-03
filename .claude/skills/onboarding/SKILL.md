---
name: onboarding
description: >-
  Kitin ilk açılışında ortamı kurar, ekibi tanır ve projeyi doğru başlangıç
  adımına yönlendirir. Tetik: "başlayalım", "ilk kurulum", "projeye nasıl
  başlarım", "2209-A başvurusuna başlıyorum", "kiti ilk kez açtım", "nereden
  başlayayım". Claude Code ve Codex'te aynı çalışır.
---

# onboarding — kitin ilk açılışı

## Görev
Kullanıcı kiti ilk kez açtığında ortamı doğrula, ekibi ve proje durumunu öğren,
`project.json`'u kur ve sonraki doğru adıma yönlendir. Bu bir karşılama değil,
bir yön bulma adımıdır.

## Ne zaman
İlk oturumda, `project.json` yokken veya kullanıcı "nereden başlayayım" dediğinde.
Proje zaten kuruluysa (eksik alan yoksa) buraya dönme; doğrudan ilgili skill'e geç.

## Girdi → Çıktı
- Girdi: temiz veya yarı kurulu bir kit klasörü; kullanıcının ham cevapları.
- Çıktı: çalışan ortam + doldurulmuş `project.json` + kullanıcının ilk adıma
  (idea-refinement veya academic-research) yönlendirilmiş olması.

## Prosedür
1. **Ortam kontrolü.** Sırayla çalıştır ve sonucu kullanıcıya özetle:
   - `uv sync` — bağımlılıkları kurar.
   - `uv run python tools/status.py` — proje durumunu tek ekranda gösterir.
   Komut hata verirse (Python < 3.11, `uv` yok) eksik aracı söyle; uydurma
   kurulum adımı yazma.
2. **Kim ve ekip.** Tek seferde sor: yürütücü kim, proje ortağı var mı (en çok
   rules dosyasındaki `partners.max` kadar), akademik danışman kim. İsimleri sen
   uydurma; bilinmeyeni `TBD` bırak.
3. **Erken uygunluk kontrolü (rules `eligibility`).** Daha fikre girmeden, başvuruyu
   doğrudan eleyecek koşulları sor (sabit yazma; kuralları rules `eligibility`'den oku):
   - **Tek başvuru:** Aynı dönemde başka 2209-A başvurusu veya devam eden 2209-A/2209-B
     projesinde yürütücülük/ortaklık var mı? (varsa başvuramaz, §4.1.4)
   - **Öğrenci türü:** Yürütücü ve ortaklar Türkiye'de ön lisans/lisans programına
     kayıtlı mı? Açık Öğretim veya Hazırlık Sınıfı öğrencisi var mı? (bunlar yürütücü/ortak olamaz, §4.1.1)
   - **ARBİS:** Yürütücünün ARBİS kaydı ve bilgileri güncel mi? (zorunlu, §4.1.2)
   - **Önceki destek:** Aynı proje için daha önce TÜBİTAK desteği alınmış mı? (alındıysa başvuramaz, §4.1.5)
   Bir koşul karşılanmıyorsa kullanıcıyı uyar ve `logs/open-questions.md`'ye yaz; uygunluğu sen onaylama.
4. **Fikir/taslak durumunu ayır.** Net bir soru sor: "Elinizde hazır bir öneri
   taslağı mı var, araştırma fikriniz netleşti mi, yoksa henüz ham bir ilgi alanı mı var?"
   - Hazır **taslak var** (DOCX/PDF/Markdown/TYBS kopyası) → sonraki adım `draft-revision`
     (`prompts/09-existing-draft.md`): taslağı sıfırdan yazmadan içe alır, doğrular ve ekiple tur tur iyileştirir.
   - Fikir **net** → sonraki adım `academic-research` (özgünlük boşluğunu kanıtlamak için).
   - Fikir **yok/ham** → sonraki adım `idea-refinement`.
   Ayrıca projenin etik kurul onayına tabi olup olmadığını erken sor (rules `ethics`,
   §5.3.1): insan/hayvan katılımcı, kişisel veri, anket, saha ya da canlı sistem varsa
   Etik Kurul Onay/Muafiyet Belgesi gerekebilir; gerekiyorsa süresinde yüklenmezse proje
   yürürlüğe girmez. Gereği `idea-refinement`'ta netleştirilir ve `checks.ethics_required`'a işaretlenir.
5. **project.json doldur.** `tools/init_project.py --set` ile öğrendiğin alanları yaz:
   `uv run python tools/init_project.py --set project.title="..." --set team.lead.name="..."`
Liste, sözlük veya çok alan varsa önce bir `values.json` yaz (ör. `{"project": {"keywords": ["..."]}, "team": {"members": [{"name": "..."}]}}`) ve
`uv run python tools/init_project.py --merge values.json` çalıştır. PowerShell'de JSON'u `--set` ile vermek tırnakları bozar.
   Etkileşimli mod: `uv run python tools/init_project.py`. Boş iskelet için
   `--defaults`. Bilinmeyen alana değer uydurma; init_project boşları `TBD` bırakır.
6. **Doğrula.** `uv run python tools/status.py` ile eksik alan listesini göster;
   kalan boşlukları kullanıcıya bildir ama kurulumu bu boşluklar engellemez.
7. **Yönlendir.** 4. adımdaki ayrıma göre kullanıcıyı ilgili skill'e geçir ve
   `prompts/00-README.md`'deki sırayı hatırlat.

## Hata durumları
- `uv` veya Python yok → kurulumu kullanıcıya bırak, adımı atlama ama uydurma.
- `project.json` zaten dolu → kurulumu tekrarlama; eksik alan varsa yalnız onları tamamla.
- Kullanıcı ekip/danışman bilmiyor → `TBD` bırak, `logs/open-questions.md`'ye ekle.

## Kalite kontrol
- [ ] `uv sync` ve `tools/status.py` çalıştırıldı, sonucu kullanıcıya iletildi.
- [ ] Yürütücü/ortak/danışman soruldu; hiçbir ad uydurulmadı.
- [ ] Erken uygunluk kontrolü yapıldı (tek başvuru, öğrenci türü, ARBİS, önceki destek) — rules `eligibility`'den okunarak.
- [ ] Etik kurul gereksinimi erken soruldu (rules `ethics`); gerekiyorsa işaretlendi.
- [ ] Taslak/fikir/ham ayrımı yapıldı ve doğru sonraki skill'e yönlendirildi (taslak → `draft-revision`).
- [ ] `project.json` init_project ile oluşturuldu; eksikler `TBD`.
- [ ] Projeye özel hiçbir değer (tutar, tarih, ad) skill'e sabit yazılmadı.
