# 2209-A gereksinim listesi

<!--
Konu-bağımsız gereksinim listesi. Sınır değerleri buraya SABİT yazılmaz;
`rules/<year>.json` atfı + parantez içinde o yılın değeri verilir. "Durum"
sütunu BOŞ bırakılır (ekip doldurur). "Denetim" sütunu, maddeyi kontrol eden
araç/skill ile DOLU gelir. Kaynaklar: [tubitak-sources.md](tubitak-sources.md).
-->

> Kuralların resmî belgelerle son doğrulama tarihi: **2026-11-03** (rules `checked_on`).

## A. Başvuru (son gün: rules `timeline.application_deadline`; 2026: 11 Kasım 2026, 17.30)

| # | Gereksinim | Kaynak / sınır | Denetim (araç/skill) | Durum |
| --- | --- | --- | --- | --- |
| A1 | Özet kelime aralığında; bilimsel nitelik, yöntem, yönetim, yaygın etki | T03 / rules `abstract` (2026: 25–450 kelime) | `tools/check_application.py` | |
| A2 | 1.1, 1.2, 2. bölümleri asgari karakter | T03 / rules `section_min_chars` (2026: 350) | `tools/check_application.py` | |
| A3 | 1.1'de araştırma sorusu ve hipotezler | T03 | `tybs-application-check` skill | |
| A4 | Takvim süre sınırı, ≥1 iş adımı, katkı toplamı 100 | T03 / rules `duration`, `work_plan` (2026: ≤12 ay, toplam 100) | `tools/check_application.py` | |
| A5 | Yasak adımlar ayrı iş adımı değil | T03 / rules `work_plan.forbidden_steps` | `tools/check_application.py` | |
| A6 | Risk tablosu ve B planları | T03 | `reviewer-simulation` skill | |
| A7 | Araştırma olanakları | T03 | `tybs-application-check` skill | |
| A8 | Kaynakça adımında, tümüne atıf, DOI'li kaynakta DOI | T03, T06 / rules `references` | `tools/bibkit.py lint`, `tools/check_consistency.py` | |
| A9 | Görseller uygun uzantı, tablolar TYBS aracıyla, önizleme | T03 / rules `images` | `academic-tables`, `scientific-visualization` skill | |
| A10 | ÜYZ kullanım beyanı (araç/sürüm, bölüm, nitelik) | T05, T02 / rules `ai_disclosure.content` | `ai-research-compliance` skill | |
| A11 | Danışman onayı (süresinde) | T01 / rules `timeline.advisor_approval_deadline` | — (ekip/danışman) | |
| A12 | Kuruluş e-imzası | T01 / rules `timeline.institution_esign` | — (kurum) | |
| A13 | Bütçe üst sınır, uygun kalemler; kapanıştan sonra değişmez | T01, T02 / rules `budget` (2026: ≤12.000 TL, dört kalem) | `budget-timeline` skill | |
| A14 | Başlık/öneride kurum/firma/ürün/marka öne çıkarılmaz | T02 / rules `brand_ban` | `tools/check_application.py` | |
| A15 | Anahtar kelime sayısı; bilimsel/teknolojik alan seçimi | TYBS / rules `keywords` (2026: 3–5) | `tools/check_application.py` | |
| A16 | Önerinin ekip tarafından yazıldığı taahhüdü; ÜYZ beyanının yeri (rehber ayrılmış bölüm ister; ekranda görülmezse BİDEB/danışmana sorulur) | TYBS Taahhütname, T05 §1.2.2 / rules `ai_disclosure.note` | `ai-research-compliance` skill | |
| A17 | Danışman koşulları; proje sayısı üst sınırı | T02 / rules `advisor` (2026: ≤5 proje) | — (ekip/danışman) | |
| A18 | Uygunluk: tek başvuru / devam eden 2209-A-B projesinde olmama; ön lisans/lisans öğrencisi (Açık Öğretim, Hazırlık hariç); ARBİS kaydı güncel; aynı proje için önceki TÜBİTAK desteği yok | T02 §4.1.1, §4.1.2, §4.1.4, §4.1.5 / rules `eligibility` | `onboarding`, `idea-refinement` skill | |
| A19 | Araştırma önerisi Türkçe ve TÜBİTAK formatında; aksi hâlde ön elemede elenir | T02 §4.2.1, §5.1.2 / rules `language` | `tybs-application-check` skill | |
| A20 | Etik kurul onayına tabiyse Etik Kurul Onay/Muafiyet Belgesi süresinde yüklenir (yoksa proje yürürlüğe girmez) | T02 §5.3.1 / rules `ethics` | `idea-refinement`, `onboarding` skill | |
| A21 | Değerlendirme ölçüt ağırlıkları (2026: bilimsel nitelik %35, yöntem %25, proje yönetimi %20, yaygın etki %20); özel gereksinimli birey +1 puan | T02 §5.2.1, §4.2.3, §5.2.6 / rules `evaluation` | `reviewer-simulation` skill | |
| A22 | Bütçe dışı kalemler (konferans katılım, yayın, patent, konaklama, gündelik) bütçeye girmez | T02 §2.1.2, T01 / rules `budget.excluded_items` | `budget-timeline` skill | |
| A23 | Başvuruda girilen IBAN proje yürütücüsü öğrenciye ait | T01 / rules `budget.iban` | `budget-timeline` skill | |
| A24 | Başvuru çağrı kapanışından itibaren 1 ay içinde geri çekilebilir | T02 §4.3.5 / rules `withdrawal` | — (ekip) | |
| A25 | Çıktılarda TÜBİTAK desteğinin belirtilmesi ve logo kullanımı zorunlu | T02 §6.6, T01 / rules `acknowledgement` | — (ekip) | |
| A26 | Bölüm içerik yükümlülükleri: 1.1 kapsam/sınır/önem + literatür eksikliği + araştırma sorusu/hipotez (+ varsa 12. Kalkınma Planı/2030 SanTek ilişkisi); 1.2 açık-ölçülebilir-gerçekçi-ulaşılabilir hedef; 2. yöntem (tasarım/değişken/istatistik, ön çalışma, takvim ilişkisi); 3.2 B Planı temel hedeften saptırmamalı; 3.3 mevcut altyapı/ekipman; 4. kategorili ve ölçülebilir çıktı | T03 / rules `section_requirements` | `tybs-application-check`, `reviewer-simulation` skill | |
| A27 | Ön inceleme ret nedenleri: koşul ihlali, süresinde onaylanmama, format/min karakter, e-posta/posta/faks ile gönderim (imha), yanıltıcı bilgi | T02 §5.1.1, §5.1.2, §4.3.1, §4.2.4 / rules `pre_screening` | `academic-audit` skill (ilk kapı) | |
| A28 | TYBS giriş araçları: Resim Yükle / Tablo / Özel karakter butonları, denklem, yapıştırmada biçim bozulması, "Proje Önerisini Önizle" | T03 / rules `tybs_input` | `tybs-application-check` skill | |
| A29 | ÜYZ kullanımı: nihai sorumluluk + doğrulama yükümlülüğü, beyan eşiği ("önemli ölçüde kullanım"; salt dil denetimi muaf), yasak kullanımlar (fabrikasyon/falsifikasyon/aşırma), ÜYZ görselinin belirtilmesi, gizli/kişisel bilginin ÜYZ'ye girilmemesi, taslağın nihai metin sayılmaması | T05 §1.3.1, §1.2.1, §1.3.3, §1.1.2, §1.4.4/§1.5.3 / rules `ai_use` | `ai-research-compliance` skill | |
| A30 | Etik genişletme: intihal tanımı (AYEK Md. 9/1-c), uydurma/çarpıtma, sahte kaynak riski, destek öncesi benzerlik kontrolü; dilimleme için resmî madde bulunamadı | T02 §5.3.2, T05 §1.3.2/§1.3.3/§1.1.2 / rules `ethics` | `academic-audit`, `ai-research-compliance` skill | |
| A31 | Değerlendirme eşik notu: taban puan yayımlanmaz, kritik/öncelikli alanlara göre ayrı belirlenebilir | T02 §5.2.3, §5.3.2 / rules `evaluation.cutoff_note` | `reviewer-simulation` skill | |

## B. Sonuç raporu (proje desteklenirse)

| # | Gereksinim | Kaynak | Denetim (araç/skill) | Durum |
| --- | --- | --- | --- | --- |
| B1 | TÜBİTAK formatı (resmî DOCX) | T01, T07 | `docx-engineering` skill, `tools/docxkit.py` | |
| B2 | Bilimsel ve teknik tüm gelişmeler | T02 / sonuç raporu | `report-consistency` skill, `tools/check_report.py` | |
| B3 | Harcama tablosu sistemde | T02 | — (sistem formu) | |
| B4 | Demirbaş envanter belgesi eki | T02 | `academic-audit` skill | |
| B5 | Danışman kontrolü ve onayı | T02 | — (danışman) | |
| B6 | Proje süresi içinde yükleme | T02 | — (ekip, takvim hatırlatması) | |
| B7 | ÜYZ ilke ve beyanlarına uyum | T02 / rules `ai_disclosure` | `ai-research-compliance` skill | |
| B8 | Yayın/sunum çıktıları | T07 | `citation-management` skill | |
| B9 | İzleme kuralları: demirbaş envanter belgesi (sonuç raporuna zorunlu ek), fatura yürütücü/ortak adına + isimsiz fiş geçersiz/iade, danışman değişikliği yazılı onay, ortak değişikliği + sayı sabitliği, bitişe <3 ay değişiklik kilidi, sonuç raporu gecikmesi yaptırımı | T02 §6.2, §6.8, §6.3, §6.4, §6.5, §6.12/§6.13 / rules `monitoring` | `final-report`, `academic-audit` skill | |
