# Analysis log

Her analiz run'ı burada bir satırla kayıt altına alınır. Amaç: hangi script'in, hangi input'tan, hangi output'u, ne zaman, hangi sonuçla ve **hangi veri türüyle (synthetic/real)** ürettiğini izlenebilir tutmak. data-analysis skill'i her çalıştırmada bu dosyaya yazar.

## Kurallar
- Her satır bir run'dır; en yeni üstte.
- `Veri türü` zorunlu: `synthetic` veya `real`. Synthetic run'ların sonucu rapora sonuç olarak girmez.
- Script seed sabit; aynı input aynı output vermeli (iki kez çalıştır, karşılaştır).
- Raw data hash'i değiştiyse not düşülür ve analiz durdurulur.
- Sonuç özeti kısa: p value tek başına değil, effect size/oran ve confidence interval birlikte.

## Kayıtlar

| Tarih (UTC) | Script | Input | Output | Veri türü | Sonuç özeti |
| --- | --- | --- | --- | --- | --- |
| ÖRNEK (kurgusal) YYYY-AA-GG | `analysis/scripts/<script>.py` | `data/processed/<file>.csv` | `analysis/outputs/<file>.json` | synthetic | ÖRNEK: Wilson interval ve Cohen's kappa manual hesapla karşılaştırıldı, uyumlu |
