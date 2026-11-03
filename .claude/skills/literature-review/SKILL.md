---
name: literature-review
description: Doğrulanmış bir kaynağın tam metnini (PDF) okuyup amaç, yöntem, örneklem, bulgu ve sınırlılıklarını çıkarır, literature-matrix'e (sources/literature-matrix.xlsx) bir satır yazar. "Bu makaleyi özetle", "matrise ekle", "makalenin yöntemi ne" isteklerinde kullan. Birden çok kaynağı karşılaştırıp sentez yazmak literature-synthesis'in işidir.
---

# literature-review

## Görev
Tek bir kaynağın içeriğini, yalnız metinde yazanla ve kendi cümlelerimizle kayda geçirmek.

## Girdi → Çıktı
- Girdi: `sources/references.json`'da VERIFIED/PARTIAL/PUBLISHER_PAGE status'lu kaynak + tam metin.
- Çıktı: `sources/matrix-rows/<id>.json` → matrix aracı → `sources/literature-matrix.xlsx` satırı.

## Prosedür
1. Kaynağın status'u kontrol edilir; doğrulanmamışsa önce source-verification.
2. Tam metin yasal açık erişim kopyasından (yayıncı, arXiv, yazar sayfası) `sources/pdf/<id>_<kaynak>.pdf` olarak alınır. PDF'ler `.gitignore` ile repo dışında tutulur; telifli metin paylaşılmaz.
3. Metin çıkarılır:
   ```bash
   uv run python -c "from pypdf import PdfReader; r=PdfReader('sources/pdf/X.pdf'); print(len(r.pages)); open('analysis/outputs/.X.txt','w',encoding='utf-8').write(''.join(p.extract_text() or '' for p in r.pages))"
   ```
   Tablo/şekil veya taranmış sayfa varsa: OCR bu kitin parçası **değildir**. Sistemde `pdf` skill'i kuruluysa görüntü/metin çıkarma için o kullanılır; kurulu değilse sayfa görüntüsü üretilip **elle** okunur. Taranmış (metin katmanı olmayan) PDF'te `extract_text()` boş döner; bu durumda içerik elle aktarılır.
4. En az şu bölümler okunur: Özet, katkılar/giriş sonu, yöntem ve veri seçimi, bulgular, **sınırlılıklar**, tartışma. Okunan bölümler "Okunan kaynak" sütununa yazılır.
5. Satır JSON'u matrix sütunlarıyla doldurulur:
   - Sayılar metindeki gibi aktarılır; yuvarlanmaz, yorumlanmaz.
   - Yazarların nitelemesi korunur (ör. "şüpheli" niteleme "kesin" yapılmaz).
   - Okunmayan alan için "TAM METİN OKUNMADI" yazılır.
   - "Projeyle ilişkisi" sütununda kaynağın projenin hangi alt sorusu/bileşeniyle bağlandığı yazılır; bölge/hukuk/bağlam farkı belirtilir ve yerel bağlama genellenmez.
   - "Satırı hazırlayan / tarih" sütununa ÜYZ katkısı yazılır.
6. Matrix aracıyla satır eklenir ve doğrulanır:
   ```bash
   uv run python tools/matrix.py add sources/matrix-rows/<id>.json
   uv run python tools/matrix.py validate
   ```
7. Geçici metin dosyası (`analysis/outputs/.X.txt`) iş bitince silinir.

## Özet yazım kuralları
- Doğrudan alıntı yerine özgün Türkçe özet; alıntı gerekirse tırnak + sayfa.
- Özet kaynağın yerine geçecek uzunlukta olmaz.
- Bulgu başka bölge/hukuktaysa yerel bağlama genellenmez.

## Hata durumları
- PDF erişimi yok: satır "TAM METİN OKUNMADI" ile açılabilir ama bulgu/sınırlılık sütunları özetten doldurulmaz.
- Metin çıkarma bozuk (iki sütun, bitişik kelimeler): sayfa görüntüsüyle kontrol edilir.

## Kalite kontrol
- [ ] `matrix.py validate` temiz.
- [ ] Her sayı PDF'te aranarak bulundu.
- [ ] Sınırlılıklar sütunu yazarların kendi sınırlılık bölümünden.
