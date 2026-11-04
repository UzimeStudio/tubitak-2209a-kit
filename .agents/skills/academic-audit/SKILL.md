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
0. **İlk kapı — ön inceleme (rules `pre_screening`).** Her şeyden önce başvuru, bilimsel değerlendirmeye bile girmeden eleyecek biçimsel/koşulsal nedenlere karşı denetlenir; biri açıksa bulgu **engelleyici** sayılır ve diğer denetimlere geçmeden kullanıcıya bildirilir:
   - Başvuru koşullarından birini sağlamama (rules `eligibility`).
   - Danışman/kuruluş onayının süresinde tamamlanmaması (rules `timeline`).
   - TÜBİTAK formatına / minimum karakter sınırına uymama (rules `language`, `section_min_chars`; `check_application.py --tybs` ile).
   - Çevrimiçi başvuru dışında e-posta/posta/faks ile belge gönderimi (değerlendirmeye alınmaz, imha edilir) — ekibe hatırlatılır.
   - Yanıltıcı/gerçeğe aykırı bilgi (rules `pre_screening`); iddia–kanıt taramasıyla (adım 2) çapraz kontrol edilir.
1. Otomatik araçlar **ayrı ayrı** çalıştırılır; her komutun **çıkış kodu tek tek okunur** (0 = temiz, 1 = sorun var, 2 = ayar hatası) ve çıktısı kayda eklenir. Komutlar tek satırda `&&`/`;` ile zincirlenmez; biri başarısız olunca diğerleri atlanmasın ve her kodun hangi araçtan geldiği belli olsun. DOCX veya PDF henüz üretilmediyse ilgili adım **atlanır** ve "DOCX/PDF yok — atlandı" diye kaydedilir:
   ```bash
   uv run python tools/status.py
   uv run python tools/bibkit.py lint
   uv run python tools/matrix.py validate
   uv run python tools/check_consistency.py             # belgeler arası tutarsızlık
   uv run python tools/check_application.py --tybs      # başvuru (öneri/TYBS metni)
   uv run python tools/check_writing.py <md> --strict   # belirsiz/kanıtsız ifade + ölçülemeyen başarı ölçütü (--json makine çıktısı)
   uv run python tools/check_report.py <docx>           # sonuç raporu; DOCX varsa (bayraksız = tam belge)
   uv run python tools/pdf_check.py <pdf>               # PDF üretildiyse
   ```
   `check_writing.py` başka bir araç/skill tarafından sağlanır; belirsiz veya kanıtsız ifadeleri ve ölçülemeyen başarı ölçütlerini uyarır. `--json` makine-okunur çıktı, `--strict` uyarıları da hata sayar. Araç henüz yoksa adım "check_writing.py yok — atlandı" diye kaydedilir.
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
- [ ] Ön inceleme (rules `pre_screening`) ilk kapı olarak uygulandı; açık varsa engelleyici işaretlendi.
- [ ] Tüm otomatik denetimler (`check_writing.py` dâhil; yoksa "atlandı") bu belge sürümünde çalıştı.
- [ ] Her bulgu konum (bölüm/sayfa) içeriyor.
- [ ] Denetlenmeyen kısım "denetlenmedi" olarak yazıldı.
