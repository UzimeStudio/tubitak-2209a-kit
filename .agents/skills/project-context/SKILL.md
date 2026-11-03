---
name: project-context
description: 2209-A çalışma alanının güncel durumunu, doğruluk kaynaklarını ve bilgi boşluklarını tek yerden yükler. Herhangi bir araştırma, yazım, analiz, bütçe veya rapor işine başlamadan önce; "proje ne durumda", "hangi belge esas", "bu sayı/tarih nereden", "neyi biliyoruz neyi bilmiyoruz" sorularında kullan. İçerik üretmez; bağlamı kurar.
---

# project-context

## Görev
Diğer skill'lerin ortak bağlamını kurmak: neyin bilindiği, neyin bilinmediği, hangi belgenin esas olduğu. İçerik üretmez.

## Ne zaman
- Oturumun ilk araştırma/yazım/rapor işinden önce.
- Bir sayı, hedef, tarih, ad veya tutar yazılmadan önce.
- Belgeler arasında çelişki görüldüğünde.

## Girdi → Çıktı
- Girdi: kullanıcı isteği.
- Çıktı: kısa bağlam notu (proje durumu, ilgili esas belge, açık bilgi boşlukları). Gerekiyorsa `logs/decisions.md`'ye kayıt.

## Prosedür
1. Proje ayarı ve call rules okunur:
   ```bash
   uv run python tools/status.py
   ```
   Eksik alanlar listelenir; bir istek eksik alana dayanıyorsa uydurulmaz, kullanıcıya sorulur ve `logs/open-questions.md`'ye `- [ ]` olarak eklenir.
2. Proje bilgisi `project.json`'dan (`config.project()`), call sınırları etkin rules dosyasından (`config.rules()`) okunur. Hiçbir sayı/tarih skill metnine sabit yazılmaz.
3. Doğruluk kaynağı sırası (üstteki esas alınır):
   | Konu | Esas |
   | --- | --- |
   | Proje adı, team, budget, timeline | `project.json` |
   | Call sınırları (kelime, karakter, süre, tutar üst sınırı) | etkin `rules/2209a-<year>.json` |
   | TÜBİTAK resmî kaynakları | `project/tubitak-sources.md` |
   | Gereksinim listesi | `project/requirements-checklist.md` |
   | Kaynakça | `sources/references.json` |
   | Açık sorular / kararlar | `logs/open-questions.md`, `logs/decisions.md` |
4. Proje bir dış repoya dayanıyorsa kaydı `project.json` `documents.external_source_registry` yolundan okunur; bu alan boşsa dış kaynak varsayılmaz.

## Hata durumları
- `project.json` yoksa: `uv run python tools/init_project.py` ile kurulması söylenir; uydurma değerle devam edilmez.
- Belgeler çelişiyorsa: üst sıradaki belge esas alınır, çelişki `logs/decisions.md`'ye yazılır.
- Bilgi hiçbir belgede yoksa: `TBD` yazılır ve kullanıcıya sorulur.

## Kalite kontrol
- [ ] Kullanılan her sayı/tarih bir dosya yoluna (project.json veya rules dosyası) dayanıyor.
- [ ] Hedefler sonuç gibi yazılmadı.
- [ ] Ad, onay, tarih, tutar uydurulmadı; bilinmeyen `TBD`.
