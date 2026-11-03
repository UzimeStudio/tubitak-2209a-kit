---
name: source-verification
description: Bir akademik kaynağın gerçekliğini ve künyesini (başlık, yazar, yıl, venue, DOI) Crossref, OpenAlex, Semantic Scholar, doi.org ve yayıncı sayfasıyla doğrular; uydurma (LLM halüsinasyonu) kaynakları eler ve sonucu sources/references.json'a işler. Kaynakçaya, matrise veya metne yeni kaynak girmeden önce ve "bu kaynak gerçek mi / DOI doğru mu" sorusunda kullan.
---

# source-verification

## Görev
Uydurma veya hatalı künyenin rapora girmesini engellemek. Bibliyografik doğrulama içerik doğrulaması değildir; bir iddia için kaynağın tam metni ayrıca okunur (literature-review).

## Girdi → Çıktı
- Girdi: DOI veya başlık (+ yıl, ilk yazar soyadı).
- Çıktı: `sources/verification/<id>.json` ve `sources/references.json` kaydı (status alanıyla).

## Uydurma kaynak (LLM halüsinasyonu) tespiti
Dil modeli gerçekçi görünen ama var olmayan künyeler üretebilir: doğru biçimli ama çözülmeyen DOI, gerçek dergide var olmayan volume/issue, doğru yazarlara yanlış atfedilen başlık, veya tümüyle uydurma. Metne giren her künye şu adımlardan geçmeden kabul edilmez:
1. **Modelden gelen künyeyi asla doğru varsayma.** LLM'in (veya kendi belleğinin) önerdiği her kaynak "doğrulanmamış" başlar.
2. **DOI doi.org'da resolve etmeli.** Resolve etmeyen DOI = kaynak kullanılmaz (biçimi geçerli olsa bile).
3. **En az iki bağımsız kayıt** (Crossref + OpenAlex) başlık/yıl/yazarda uyuşmalı. Tek kayıt → PARTIAL, yayıncı sayfasından teyit şart.
4. **Hiç kayıt yoksa** DOI'siz USENIX gibi istisnalar dışında kaynak şüphelidir: yayıncı/kurum sayfasında birebir künye aranır; bulunmazsa metne girmez.
5. **Uyarı işaretleri**: çok yuvarlak/tam künye ama hiç resolve etmeyen DOI; yazar+yıl gerçek ama başlık hiçbir yerde yok; "çok uygun" ama hiçbir indekste olmayan kaynak. Bu durumda `sources/verification/<id>.json`'a `rejected_candidates` olarak yazılır, kullanıcıya bildirilir.

## Prosedür
1. Çalıştır:
   ```bash
   uv run python tools/verify_source.py --doi <DOI> --year <yıl> --author <soyad> --save <id>
   uv run python tools/verify_source.py --title "<tam başlık>" --year <yıl> --author <soyad> --no-s2 --save <id>
   ```
   (İstek User-Agent'ı `tubitak-2209a-kit/0.1 (academic source verification)`.)
2. Status'u yorumla:
   | Status | Anlamı | Ne yapılır |
   | --- | --- | --- |
   | VERIFIED | ≥2 bağımsız kayıt başlık/yıl/yazarda uyuşuyor, DOI doi.org'da resolve ediyor | Kullanılabilir |
   | PARTIAL | Tek kayıt | Yayıncı sayfası açılır; künye oradan teyit edilir |
   | PUBLISHER_PAGE | Veri tabanlarında yok, yayıncı sayfasında elle doğrulandı | Kullanılabilir; `verified_by`'a sayfa ve tarih yazılır |
   | CONFLICT | Kayıtlar çelişiyor veya DOI resolve etmiyor | Çözülene kadar kullanılmaz |
   | NOT_FOUND | Hiçbir kayıt yok | Sahte demek değildir ama şüphelidir; yayıncı/kurum sayfası aranır, bulunmazsa elenir |
3. DOI kuralları:
   - DOI'si olan kaynakta DOI yazılır (rules `references.doi_required`).
   - Veri tabanındaki DOI, doi.org'da resolve etmeden yazılmaz.
   - arXiv/preprint DOI'si yayıncı DOI'sinin yerine kullanılmaz; preprint "ön baskı" olarak etiketlenir. Yayımlanmış sürüm varsa yayıncı DOI'si tercih edilir.
4. DOI'siz yayın otomatik geçersiz değildir (bazı konferanslar DOI vermez). Yayıncı sayfası/BibTeX ile doğrulanır.
5. `sources/references.json`'a kayıt eklenir/güncellenir, sonra:
   ```bash
   uv run python tools/bibkit.py lint
   ```

## Hata durumları
- Ağ hatası: sonuç "doğrulanamadı" kalır, status yükseltilmez.
- Başlık eşleşmesi tutmuyor: kısaltılmış yerine tam başlık denenir; benzer başlıklı farklı yıllar `rejected_candidates`'e düşer.
- Kullanıcıdan gelen künye kayıtlarla çelişiyor: iki sürüm birlikte gösterilir.

## Kalite kontrol
- [ ] Ham API yanıtları `sources/cache/`'te (yeniden üretilebilir).
- [ ] references.json'daki her kaydın status'u VERIFIED/PARTIAL/PUBLISHER_PAGE.
- [ ] Her DOI doi.org'da resolve etti; resolve etmeyen hiçbir DOI yazılmadı.
- [ ] Hiçbir künye bellekten veya modelden tamamlanmadı; şüpheli adaylar `rejected_candidates`'te.
- [ ] `bibkit.py lint` temiz.
