---
name: scientific-visualization
description: Analiz sonuçlarından yayın kalitesinde, Türkçe etiketli, kaynak verisi ve betiğiyle saklanan grafikler üretir (matplotlib, renk körlüğüne uygun palet, 300 dpi PNG + SVG + CSV). Grafik, şekil, güven aralığı çizimi, "grafik çiz", "şekil üret" veya rapor görseli istendiğinde kullan. Sayıların hesaplanması data-analysis'in işidir.
---

# scientific-visualization

## Görev
Veriyi doğru ve okunaklı göstermek; her şekli yeniden üretilebilir tutmak.

## Ne zaman
Rapor/öneri için grafik, güven aralığı çizimi veya karşılaştırma görseli gerektiğinde.

## Girdi → Çıktı
- Girdi: `data/processed/` veya `analysis/outputs/` altındaki tablo (yollar `config.PATHS`'ten).
- Çıktı: `figures/<ad>.png|svg|csv|json` (`tools/figstyle.py` `save` fonksiyonuyla). `save` çıktı klasörünü (`config.PATHS["figures"]`) kendisi `mkdir(parents=True, exist_ok=True)` ile oluşturur.

## Prosedür
1. Şekil türü seçimi:
   | Veri | Tür |
   | --- | --- |
   | Grup oranı + güven aralığı | Nokta + hata çubuğu (sütun grafiği değil) |
   | Kategori × gösterge | Gruplanmış nokta/sütun, kategoriler sabit sırada |
   | Karışıklık/eşleşme matrisi | Isı haritası, hücrede sayı |
   | Dağılım | Kutu/keman + tekil noktalar (n küçükse) |
   | Eşli/zaman karşılaştırması | Eşli çizgi |
   Pasta grafiği ve 3B grafik kullanılmaz.
2. Kod iskeleti (yollar `config.PATHS`'ten; import için çalışma dizinine bağlı `sys.path.insert(0, "tools")` değil, betiğin yerine göre kökten mutlak yol):
   ```python
   import sys
   from pathlib import Path
   ROOT = Path(__file__).resolve().parents[2]   # analysis/scripts/<betik>.py → proje kökü
   sys.path.insert(0, str(ROOT / "tools"))
   import figstyle

   figstyle.apply()
   import matplotlib.pyplot as plt

   fig, ax = plt.subplots(figsize=(figstyle.TEXT_WIDTH_IN * 0.85, 3.2))
   ...
   figstyle.turkish_decimal(ax, "y", 1)
   figstyle.save(fig, "figure_name", df, caption="...", script="analysis/scripts/x.py", synthetic=False)
   ```
3. Zorunlular: eksen adı ve birim ("oran (0–1)", "süre (s)"), hata çubuğunun neyi gösterdiği şekil başlığında ("%95 Wilson güven aralığı"), n değeri, Türkçe ondalık virgül.
4. Sentetik veri varsa şeklin içine "SENTETİK VERİ" yazılır ve `synthetic=True` verilir.
5. Şekil başlığı (caption) cümle düzeninde, sonda nokta yok; `docxkit` başlığa "Şekil N." ekler.
6. Word'e ekleme: `SectionWriter.figure(png, caption, width_cm≤16)`. Düzenlenebilirlik için SVG ve CSV yanında saklanır; Word'de yerel düzenlenebilir grafik gerekiyorsa veri tablosu ayrıca academic-tables ile eklenir.
7. ÜYZ ile üretilen görsel `logs/ai-use-log.md`'ye yazılır (ÜYZ Rehberi şekil üretimini dikkat edilmesi gereken kullanım sayar).

## Hata durumları
- Arial bulunamazsa matplotlib uyarı verir; Windows'ta Arial vardır, başka ortamda `font.family` değiştirilip not düşülür.
- Eksen kırpması (y ekseni 0'dan başlamıyorsa) şekil başlığında belirtilir.

## Kalite kontrol
- [ ] PNG görsel olarak açılıp kontrol edildi (okunur yazı, çakışma yok).
- [ ] CSV'deki sayılar analiz çıktısıyla aynı.
- [ ] Renkler renk körlüğüne uygun paletten.
- [ ] Sentetik veride içeride "SENTETİK VERİ" işareti var.
