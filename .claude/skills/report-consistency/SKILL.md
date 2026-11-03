---
name: report-consistency
description: Rapor içindeki şekil/tablo numaralarını ve atıflarını, metin içi atıfları ile kaynakçayı, yer tutucuları (placeholder), boş bölümleri ve kaynak belgelerle sayı tutarlılığını denetler. Her DOCX üretiminden sonra ve teslimden önce, "rapor tutarlı mı", "atıflar eşleşiyor mu", "şekil tablo numaraları doğru mu" istendiğinde kullan. Dil düzeltmesi academic-turkish'in, bilimsel içerik denetimi academic-audit'in işidir.
---

# report-consistency

## Görev
Belgenin kendi içinde ve kaynak belgelerle tutarlı olduğunu makineyle ve gözle doğrulamak.

## Ne zaman
Her DOCX üretiminden sonra ve teslimden önce.

## Prosedür
1. Otomatik iç denetim:
   ```bash
   # Sonuç raporu (bayraksız; tam/son belge):
   uv run python tools/check_report.py report/final/<ad>.docx
   ```
   | Kontrol | Örnek bulgu |
   | --- | --- |
   | Şekil/Tablo numaraları ardışık | `Tablo numaraları ardışık değil: [1, 3]` |
   | Her atfın başlığı, her başlığın atfı | `Metinde Tablo 2 atfı var ama caption'ı yok` |
   | Metin içi atıf ↔ kaynakça | `Metin içi atıf kaynakçada yok: Yılmaz (2021)` |
   | DOI zorunluluğu | `DOI eksik: <id>` |
   | Yer tutucu (placeholder) | `[DOĞRULANMADI]`, `TODO`, `koyu harflerle yazılacak` |
   | Boş şablon bölümü | `Bölüm boş: Sonuç:` |
2. Öneri taslağı için:
   ```bash
   uv run python tools/check_application.py
   ```
   Özet kelime sayısı, bölüm asgari karakter, çalışma takvimi katkı toplamı, süre üst sınırı, yasaklı iş adımları, DOI'lerin dış kaynak kaydında olması — hepsi rules dosyasındaki (`rules/2209a-2026.json`) değerlere göre. Eşik değerleri koda sabit yazılmaz; `config.rules()`'tan okunur.
   - **Dış kaynak kaydı DOI kontrolü yalnız `project.json documents.external_source_registry` doluysa çalışır** (`_external_source_registry_check`). Alan tanımlı değilse bu kontrol atlanır, bu bir sorun değildir.
3. Elle sayı tutarlılığı: rapordaki her sayı (örneklem, eşik, sonuç) kaynağına karşı kontrol edilir: `analysis/outputs/*.json` (sonuç), öneri/başvuru metni (hedef). Aynı sayı birden çok yerde geçiyorsa hepsi aynı mı?
4. Yöntem–sonuç uyumu: sonuçta raporlanan her ölçüt yöntemde tanımlı mı; yöntemde vaat edilen her ölçüt sonuçta ya raporlandı ya da "yapılamadı + gerekçe" yazıldı mı?

## Hata durumları
- Atıf deseni tanınmıyorsa (ör. kurum adı yazar: "Kurum (2025)"), kaynakça girdisi aynı ilk sözcükle başlatılır veya bulgu elle kapatılıp `logs/quality-audit.md`'ye yazılır.
- Negatif test: denetçi bilerek bozuk bir belgede (`tools/sample_report.py --broken`) bütün hataları yakalamalıdır.

## Kalite kontrol
- [ ] `tools/check_report.py` çıkış kodu 0.
- [ ] `tools/check_application.py` sorunları kullanıcıya iletildi.
- [ ] Hedef ↔ sonuç ayrımı her tabloda açık.
