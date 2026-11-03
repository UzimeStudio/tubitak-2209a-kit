---
name: academic-audit
description: Danışmana gitmeden önceki son kapı: bilimsel doğruluk, iddia-kanıt eşleşmesi, sınırlılıkların görünürlüğü, hedef/sonuç ayrımı, etik ve ÜYZ beyanı, gereksinim listesi. Başvuru veya sonuç raporu danışmana sunulmadan önce; "son kontrol", "teslim denetimi", "danışmana hazır mı", "denetle" isteğinde kullan. Diğer skill'lerin çıktısını denetler, yeniden yapmaz.
---

# academic-audit

## Görev
Belgeyi bağımsız bir reviewer gözüyle okuyup teslime engel sorunları bulmak ve `logs/quality-audit.md`'ye kaydetmek. Bu skill teslim onayı vermez; onay ekip ve danışmanındır.

## Ne zaman
- Başvuru veya sonuç raporu danışmana gönderilmeden önce.
- Metinde büyük değişiklik sonrası.

## Girdi → Çıktı
- Girdi: denetlenecek belge (başvuru veya rapor).
- Çıktı: bulgu kaydı (`logs/quality-audit.md`): tarih, belge, bulgu, önem (engelleyici/önemli/küçük), öneri, durum.

## Prosedür
1. Otomatik araçlar **ayrı ayrı** çalıştırılır; her komutun **çıkış kodu tek tek okunur** (0 = temiz, 1 = sorun var, 2 = ayar hatası) ve çıktısı kayda eklenir. Komutlar tek satırda `&&`/`;` ile zincirlenmez; biri başarısız olunca diğerleri atlanmasın ve her kodun hangi araçtan geldiği belli olsun. DOCX veya PDF henüz üretilmediyse ilgili adım **atlanır** ve "DOCX/PDF yok — atlandı" diye kaydedilir:
   ```bash
   uv run python tools/status.py
   uv run python tools/bibkit.py lint
   uv run python tools/matrix.py validate
   uv run python tools/check_consistency.py             # belgeler arası tutarsızlık
   uv run python tools/check_application.py --tybs      # başvuru (öneri/TYBS metni)
   uv run python tools/check_report.py <docx>           # sonuç raporu; DOCX varsa (bayraksız = tam belge)
   uv run python tools/pdf_check.py <pdf>               # PDF üretildiyse
   ```
   `check_report.py` bir **öneri taslağı** DOCX'ine uygulanıyorsa, taslaklarda tablo–atıf gürültüsünü uyarıya düşüren `--draft` bayrağıyla çağrılır (`check_report.py <docx> --draft`); sonuç raporu gibi tam/son belgelerde bayrak kullanılmaz.
2. İddia–kanıt taraması: her olgusal cümle bir sınıfa konur; kanıtı olmayan cümle bulgudur:
   | Sınıf | Kanıt |
   | --- | --- |
   | Literatür | `sources/references.json` VERIFIED/PARTIAL/PUBLISHER_PAGE + matrix satırı |
   | Proje sonucu | `analysis/outputs` + `analysis/analysis-log.md` (gerçek veri) |
   | Plan/hedef | başvuru taslağı; dili gelecek zaman |
3. Kırmızı bayraklar: "ilk/tek/kanıtlandı/uyumlu/ihlal" gibi aşırı iddialar, hedef sayının sonuç gibi yazılması, mock sayının rapora girmesi, ad/onay/tarih/tutar boşluğunun uydurmayla doldurulması, sınırlılık bölümünün kısaltılması.
4. `project/requirements-checklist.md` satır satır işaretlenir.
5. Bütçe-takvim için `budget-timeline`, ÜYZ için `ai-research-compliance` kalite listeleri uygulanır.
6. Derin inceleme gereken yerlerde `consistency-hunt` ve `reviewer-simulation` skill'lerine yönlendirilir.
7. Bulgular `logs/quality-audit.md`'ye yazılır.

## Karar
- Engelleyici bulgu varsa "teslime hazır değil" denir. Onay ekip ve danışmanındır.

## Kalite kontrol
- [ ] Tüm otomatik denetimler bu belge sürümünde çalıştı.
- [ ] Her bulgu konum (bölüm/sayfa) içeriyor.
- [ ] Denetlenmeyen kısım "denetlenmedi" olarak yazıldı.
