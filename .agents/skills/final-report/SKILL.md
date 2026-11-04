---
name: final-report
description: Proje desteklendikten sonra TÜBİTAK 2209-A resmî sonuç raporunu T07 şablonuyla hazırlar: giriş, rapor dönemi çalışmaları, sonuç, çıktılar, harcama; her hedefi sonuçla eşler, sınırlılıkları korur, danışman onayı ve demirbaş kayıt belgesini hatırlatır, süresinde BİDEB yüklemesini ve ÜYZ beyanını denetler. "Sonuç raporu yaz", "sonuç raporunu hazırla", "proje bitti rapor" isteklerinde kullan. DOCX üretimi docx-engineering, sayı denetimi report-consistency işidir.
---

# final-report

## Görev
Proje **desteklendiyse** dönem sonunda resmî sonuç raporunu doğru ve TÜBİTAK formatında üretmek: planlanan hedeflerin gerçekleşen sonuçlarla dürüst eşlenmesi, harcamanın belgelenmesi, süresinde yüklenmesi.

## Ne zaman
Yalnız proje desteklendikten ve dönem çalışmaları yapıldıktan sonra. Başvuru aşamasında kullanılmaz (o proposal-writing'in işi). Desteklenmediyse skill çalışmaz; kullanıcıya bildirilir.

## Girdi → Çıktı
- Girdi: başvuru/proposal'daki hedefler ve work plan, dönem boyunca üretilen sonuçlar (`analysis/outputs/`), harcama kayıtları, `project.json`, rules dosyası (T07).
- Çıktı: `report/drafts/final-report.docx` → (onayla) `report/final/`.

## T07 bölüm yapısı (şablon bozulmaz)
Şablon `config.PATHS["report_template"]`; bölümler rules `sources[].id` = T07'ye dayanır.
1. **Giriş** — proje konusu hakkında kısa bilgi, amaç ve kapsam.
2. **Rapor dönemlerinde yapılan çalışmalar** — work plan adımlarına karşılık gerçekte yapılanlar; her adım için ne yapıldı, ne zaman, kim.
3. **Sonuç** — bulgular; her hedefin success criterion'u karşılandı mı.
4. **Çıktılar** — yayın, sunum, poster, yazılım vb.
5. **Harcama kalemleri** — rules `budget.items` kalemleri; gerçek harcama, başvuru bütçesiyle tutarlı.
İmza tablosu + "Tarih :".

## Prosedür
1. **Hedef–sonuç eşlemesi.** Başvurudaki her hedefi/çalışma takvimi (iş planı) adımını listele; her birinin karşısına gerçekleşen sonucu yaz. Bir hedef yapılamadıysa gizlenmez: "yapılamadı + gerekçe" yazılır (CLAUDE.md doğruluk ilkesi 6). Bu eşleme methodology-review ve report-consistency ile çapraz kontrol edilir.
2. **Sonuç dürüstlüğü.** Yalnız gerçek ölçüm sonuçları girer; sentetik hiçbir sayı sonuç olmaz. Eşik sağlanmadıysa gerçek değer yazılır. Sınırlılıklar (temsil, tek ölçüm noktası, sınırlar) her sonuçla anılır.
3. **Harcama.** Harcama kalemleri rules'taki bütçe kalemi adlarıyla ve `project.json budget` ile tutarlı; toplam üst sınırı (rules `budget.max_tl`) aşmaz. Rakamlar uydurulmaz; belge yoksa `TBD` + `logs/open-questions.md`.
4. **İzleme kuralları (rules `monitoring`).** Yürürlük sonrası kurallar kontrol listesine alınır:
   - **Demirbaş** (`monitoring.demirbas_envanter`, T02 §6.8): demirbaş (makine/teçhizat) alındıysa üniversiteden alınan envanter kayıt belgesi rapora **ek** olarak eklenir (zorunlu). Belge yoksa açık soru olarak işaretlenir.
   - **Fatura** (`monitoring.invoice_rules`, T02 §6.2): faturalar yürütücü ya da ortak adına; isimsiz fişler geçersiz sayılır ve iade istenir; asıllar istenebilir. Harcama tablosu bununla tutarlı olmalı.
   - **Danışman/ortak değişikliği** (`monitoring.advisor_change`/`partner_change`, T02 §6.3/§6.4): yazılı onayla; ortak sayısı sabit kalır.
   - **Son 3 ay kilidi** (`monitoring.last_3_months_lock`, T02 §6.5): bitişe <3 ay kaldıysa ortak/danışman değişikliği kabul edilmez.
   - **Gecikme yaptırımı** (`monitoring.final_report_delay`, T02 §6.12/§6.13): rapor süresinde yüklenmez veya revizesi kabul edilmezse proje kusura göre yürürlükten kaldırılır/iptal edilir — süre uyarısı bu nedenle önemlidir.
5. **DOCX üretimi ve denetim.** docx-engineering ile şablon doldurulur (`fill_cover`, `fill_general_info` anahtarları: `subject/lead/advisor/dates`, `SectionWriter.at_section` anahtarları: `intro/work/result/outputs/expenses`). Hiçbir şablon etiketi silinmez/yeniden sıralanmaz. Üretim sonrası somut denetim komutları (sonuç raporu tam belge olduğundan **bayraksız**):
   ```bash
   uv run python tools/check_report.py report/drafts/final-report.docx
   uv run python tools/docx_to_pdf.py report/drafts/final-report.docx report/drafts/final-report.pdf
   uv run python tools/pdf_check.py report/drafts/final-report.pdf
   ```
   `check_report.py` çıkış kodu 0 olmalı; `pdf_check.py` bulgusu çözülmeli ve tüm sayfa PNG'leri görsel olarak incelenmelidir.
6. **ÜYZ beyanı.** Raporun hazırlanmasında ÜYZ kullanıldıysa beyan rules `ai_disclosure.content` alanlarını (araç adı+sürümü, aşama/bölüm, kullanımın niteliği) içerir; `logs/ai-use-log.md`'ye yazılır. Not: rules `ai_disclosure.note` beyanın formdaki yerinin BİDEB'e/danışmana sorulması gerektiğini söyler.
7. **Danışman onayı.** Son karar ve bilimsel sorumluluk ekipte + danışmandadır. Rapor danışman kontrolü ve nihai onayı olmadan yüklenmez; skill taslak üretir, onay vermez, sistemden yükleme yapmaz.
8. **Süresinde yükleme.** Rapor proje süresi içinde, harcama tablosuyla birlikte BİDEB Başvuru ve İzleme Sistemine yüklenir. Süresinde yüklenmeyen veya revizyonu kabul edilmeyen proje yürürlükten kaldırılabilir/iptal edilebilir. İlgili tarih rules `timeline`'dan okunur, koda sabit yazılmaz.

## Hata durumları
- Proje henüz desteklenmediyse/sonuç yoksa: skill durur, "sonuç raporu yalnız destek ve dönem çalışması sonrası" uyarısı.
- Bir hedefin sonucu yok: hedef silinmez; "yapılamadı + gerekçe" yazılır.
- Harcama belgesi eksik: `TBD` + açık soru; rakam uydurulmaz.

## Kalite kontrol
- [ ] Her başvuru hedefi/çalışma takvimi adımı sonuçla eşlendi; yapılamayanlar gerekçeli.
- [ ] Hiçbir sentetik/planlanan değer sonuç gibi yazılmadı; sınırlılıklar korundu.
- [ ] Harcama rules `budget` ile tutarlı, üst sınır aşılmadı; demirbaş varsa envanter kayıt belgesi eklendi/hatırlatıldı (rules `monitoring.demirbas_envanter`).
- [ ] İzleme kuralları kontrol edildi: fatura adı/isimsiz fiş, danışman/ortak değişikliği + sayı sabitliği, son 3 ay kilidi, gecikme yaptırımı (rules `monitoring`).
- [ ] Şablon etiketleri korundu (docx-engineering + report-consistency temiz).
- [ ] ÜYZ beyanı ve danışman onayı adımı kullanıcıya hatırlatıldı; süresinde yükleme tarihi rules'tan doğrulandı.
