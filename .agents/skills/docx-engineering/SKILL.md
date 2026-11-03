---
name: docx-engineering
description: TÜBİTAK 2209-A resmî sonuç raporu şablonunu (project/official-report-template.docx) bozmadan doldurur, Word veya LibreOffice ile PDF üretir ve sayfa sayfa denetler. Sonuç raporu, "sonuç raporu DOCX", "şablonu doldur", "rapordan PDF üret" veya şablona dayalı herhangi bir Word çıktısı istendiğinde kullan. Genel DOCX okuma/düzenleme için `docx` skill'i (kuruluysa; kitin parçası değildir) kullanılabilir; bu skill şablona özgü kuralları ekler.
---

# docx-engineering

## Görev
Düzenlenebilir DOCX + kontrol edilmiş PDF teslim etmek; şablonun yapısını korumak.

## Ne zaman
Resmî sonuç raporu; öneri gibi şablonsuz Word çıktıları.

## Şablon bilgisi
Yol: `config.PATHS["report_template"]` (official-report-template.docx). Yapı resmî kaynağa dayanır (rules dosyası `sources[].id` = T07, Sonuç Raporu Formatı).
- A4, dört kenar 2,5 cm. Normal stili Times New Roman 12 pt; içerik satırları Arial.
- Sayfa 1: kapak metin kutusu (PROJE BAŞLIĞI koyu, YÜRÜTÜCÜ, DANIŞMAN).
- Sayfa 2: GENEL BİLGİLER tablosu (konu, yürütücü, danışman, başlangıç–bitiş); "Sonuç Raporu Formatı:"; numaralı bölümler: **1. Giriş** ("Proje konusu hakkında kısa bilgi"), **2. Rapor dönemlerinde yapılan çalışmalar**, **3. Sonuç**, **4. Çıktılar** (yayın/sunum vb.), **5. Harcama kalemleri**; imza tablosu; "Tarih :".
- Şablonda kaynakça, şekil/tablo veya yazı tipi boyutu kuralı **yoktur**. Bu skill'in eklediği biçimler (Kaynaklar başlığı, KL stilleri) danışmanla teyit edilecek bir tasarım kararıdır (`logs/decisions.md`).

## Prosedür
1. İçerik önce Markdown/JSON olarak hazırlanır ve report-consistency ile kontrol edilir.
2. Üretim betiği `tools/docxkit.py` API'sini kullanır (`SECTIONS`, `is_label` korunur). Betik kökten mutlak yolla import eder; `sys.path.insert(0, "tools")` gibi çalışma dizinine bağlı yol kullanılmaz:
   ```python
   import sys
   from pathlib import Path
   ROOT = Path(__file__).resolve().parents[1]   # betiğin yerine göre proje kökü
   sys.path.insert(0, str(ROOT / "tools"))
   import config
   from docxkit import open_template, fill_cover, fill_general_info, fill_date, SectionWriter

   doc = open_template()
   fill_cover(doc, title, lead, advisor)          # başlık Türkçe büyük harfe çevrilir, koyu
   # fill_general_info anahtarları docxkit.GENERAL_INFO_ROWS ile aynıdır:
   fill_general_info(doc, {"subject": ..., "lead": ..., "advisor": ..., "dates": ...})
   fill_date(doc, "01.06.2026")
   # SectionWriter.SECTIONS anahtarları: intro | work | result | outputs | expenses
   w = SectionWriter.at_section(doc, "intro")
   w.heading("Alt başlık")
   w.text("Gövde **koyu** *italik*")
   w.table(df, "...")
   w.figure(png, "...")
   SectionWriter.before_signature(doc).references(lines)
   out = Path(config.PATHS["report_drafts"]) / "<ad>.docx"
   out.parent.mkdir(parents=True, exist_ok=True)
   doc.save(str(out))
   ```
   - Şablon etiketleri görünümü değişmeden ana başlık düzeyi (outline level 0) alır (gezinme, PDF yer imi).
   - Alt başlık gerçek `Heading 2`; gövde `KL Body` (Arial, iki yana yaslı).
   - Boşlukla hizalama yapılmaz; girinti stille verilir.
3. PDF üretimi: `uv run python tools/docx_to_pdf.py <docx> [pdf]`. Windows + Microsoft Word kuruluysa `tools/docx_to_pdf.ps1` (Word COM) alanları/İçindekiler'i günceller, yazı tiplerini gömer ve PDF/A üretir — **PDF/A yalnız Word yolunda garanti edilir**. Word yoksa LibreOffice (`soffice --headless --convert-to pdf`) kullanılır; bu yolda PDF/A ve yazı tipi gömme garanti değildir, PDF elle kontrol edilir. İkisi de yoksa çıkış kodu 2.
4. Otomatik sayfa denetimi: `uv run python tools/pdf_check.py <pdf>` — A4, boş sayfa, kenar boşluğu taşması, gömülü olmayan yazı tipi, sayfa sonunda kalan başlık.
5. **Görsel denetim zorunlu:** üretilen sayfa PNG'lerinin her biri açılıp bakılır: taşan tablo, bozuk şekil, yanlış sayfa sonu, boş sayfa, yazı tipi değişimi, yetim başlık, kapakta bozuk Türkçe karakter.
6. Nihai teslim: `config.PATHS["report_final"]` altındaki dosyaların üzerine yalnız kullanıcı onayıyla yazılır.

## Şablonsuz raporlar (öneri, danışman dosyası)
```bash
uv run python tools/md2docx.py report/drafts/proposal.md report/drafts/proposal.docx
```
Kapak, İçindekiler (`[[TOC]]`) alanı, gerçek Heading 1–3, SEQ numaralı şekil/tablo başlıkları, not kutusu, sayfa sonu (`[[PAGEBREAK]]`) ve kaynakça işaretçisi **`[[KAYNAKCA]]`** (metinde atıf yapılan kaynaklar `bibkit` modülünden alfabetik) desteklenir. Tam sözdizimi `tools/md2docx.py` başlığındadır. PDF ve denetim adımları yukarıdakiyle aynıdır.

## Hata durumları
- Başlıklar Calibri/Cambria çıkıyorsa stilde tema yazı tipi özniteliği kalmıştır; temizlenir.
- Word COM hatası: Word açık bir pencerede bekliyor olabilir; kapatılıp yeniden denenir. Word yoksa LibreOffice gerekir (kurulum onay ister).
- "Şablonda bölüm etiketi bulunamadı": resmî şablon değişmiş olabilir; call-update ile tarih kontrol edilir, `SECTIONS` güncellenir.

## Kalite kontrol
- [ ] `tools/check_report.py` temiz.
- [ ] `tools/pdf_check.py` sorun yok ve tüm sayfalar görsel olarak incelendi.
- [ ] Kapak, genel bilgiler, imza ve tarih alanları gerçek bilgiyle dolu.
- [ ] Şablondaki hiçbir etiket silinmedi veya yeniden sıralanmadı.
