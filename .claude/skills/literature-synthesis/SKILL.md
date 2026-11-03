---
name: literature-synthesis
description: literature-matrix'teki birden çok kaynağı tema, yöntem ve bulguya göre karşılaştırıp araştırma boşluğunu ve projenin konumunu yazar (başvuru 1.1, sonuç raporu Giriş). "Literatür özeti yaz", "boşluk ne", "öncüllerle farkımız" isteklerinde kullan. Tek kaynak okuma literature-review'un işidir.
---

# literature-synthesis

## Görev
Kaynakları tek tek özetlemek yerine karşılaştırmalı anlatı kurmak ve projenin katkısını abartmadan konumlandırmak.

## Girdi → Çıktı
- Girdi: `sources/literature-matrix.xlsx` (yalnız doğrulanmış satırlar), `sources/search-log.md`.
- Çıktı: `report/drafts/` altında Markdown bölüm taslağı + kullanılan kaynak id listesi.

## Prosedür
1. Matrix pandas ile okunur; satırlar tema ve yönteme göre gruplanır:
   ```bash
   uv run python -c "import pandas as pd; df=pd.read_excel('sources/literature-matrix.xlsx'); print(df[['Kaynak ID','Yöntem','Veri/örneklem','Doğrulama durumu']])"
   ```
2. **Tema iskeleti** konuya göre kurulur: ilgili alt sorunun her biri bir tema, her tema altında onu çalışan öncüller. İskelet matristen çıkar; buraya örnek yazar/kaynak gömülmez.
3. Her tema için: ne ölçüldü/incelendi, nasıl, hangi bağlamda, hangi sınırla. Sonra proje bu sınırların hangisine dokunuyor.
4. **Boşluk ifadesi koşullu** yazılır: "taranan kaynaklarda (bkz. search-log, <tarih>) … bulunmamıştır". search-log yoksa boşluk "aday" olarak kalır (academic-research).
5. Her cümledeki iddia bir matrix satırına bağlanır; atıf yazar–yıl biçimindedir (academic-turkish).
6. Taslak report-consistency ve academic-turkish ile kontrol edilir.

## Yasak ifadeler
"ilk", "tek", "literatürde hiç yok", "kanıtlanmıştır" (kaynak öyle demiyorsa), preprint'i hakemli yayın gibi sunmak.

## Hata durumları
- Bir tema tek kaynağa dayanıyorsa bu açıkça yazılır.
- Kaynaklar çelişiyorsa çelişki saklanmaz; yöntem/örneklem farkıyla açıklanır.

## Kalite kontrol
- [ ] Her atıf matrix'te VERIFIED/PARTIAL/PUBLISHER_PAGE satırına karşılık geliyor.
- [ ] Bağlam farkı (bölge, hukuk düzeni, örneklem) her karşılaştırmada belirtildi.
- [ ] Katkı abartılmadı; boşluk search-log'a koşullu yazıldı.
