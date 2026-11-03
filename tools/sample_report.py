"""Altyapı testi: resmî 2209-A sonuç raporu şablonu üzerinde kurgusal ÖRNEK DOCX üretir.

Bu belge gerçek bir sonuç raporu DEĞİLDİR. İçeriği konu-bağımsız, tamamen kurgusal
('ÖRNEK') metindir; yalnız şablon/biçim/atıf/numara altyapısını test eder.
Ad ve tarih alanları boş bırakılmaz, 'ÖRNEK' yazılır.

    uv run python tools/sample_report.py                      # geçerli örnek belge
    uv run python tools/sample_report.py --broken             # bilerek hatalı (negatif test)
    uv run python tools/sample_report.py --out <yol.docx>     # çıktı yolu (varsayılan: PATHS['report_final'])

check_report.py karşılığı: geçerli belgede 0 sorun, --broken belgesinde >0 sorun bulunmalı.
Kaynakça satırları kurguseldir ve belgenin içinde üretilir (bibkit'e veya references.json'a
bağlı değildir); böylece araç paralel geliştirmeden bağımsız çalışır.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config
from docxkit import SectionWriter, fill_cover, fill_date, fill_general_info, open_template

TITLE = "ÖRNEK (kurgusal): Akademik Rapor Biçim ve Atıf Altyapısının Sınanması"

# Kurgusal kaynakça satırları (ÖRNEK). Metinde (Soyad, Yıl) biçiminde atıf yapılır;
# check_report.py biçime dayalı eşleştirmeyle bunları tanır.
REFERENCES = [
    "Demir, A. 2019. “Örnek yöntem üzerine bir inceleme”, Örnek Dergisi, 12 (3), 45–60.",
    "Kaya, B., Yıldız, C. 2021. “Kurgusal ölçüm yaklaşımı”, Örnek Konferans Bildirileri, 101–110.",
    "Yılmaz, D. 2023. “Örnek veri analizi”, Örnek Bilim Dergisi, 5 (1), 7–20.",
]
# Metinde atıf yapılacak (soyad, yıl) çiftleri — REFERENCES ile birebir eşleşir.
CITATIONS = [("Demir", "2019"), ("Kaya", "2021"), ("Yılmaz", "2023")]


def _summary_table() -> pd.DataFrame:
    """Sabit, kurgusal özet tablo (dış dosyaya bağlı değil)."""
    return pd.DataFrame(
        {
            "Grup": ["Grup A", "Grup B", "Grup C"],
            "n": [30, 28, 31],
            "Oran": [0.62, 0.55, 0.71],
            "Alt sınır": [0.44, 0.37, 0.53],
            "Üst sınır": [0.77, 0.72, 0.84],
        }
    )


def build(broken: bool, out: Path | None = None) -> Path:
    SectionWriter.counters = {"Şekil": 0, "Tablo": 0}
    doc = open_template()
    fill_cover(doc, TITLE, "ÖRNEK", "ÖRNEK")
    fill_general_info(
        doc,
        {
            "subject": "Kurgusal örnek konu (altyapı testi)",
            "lead": "ÖRNEK",
            "advisor": "ÖRNEK",
            "dates": "Proje başlamadı — örnek belge",
        },
    )
    fill_date(doc, "01.01.2026 (örnek)")

    w = SectionWriter.at_section(doc, "intro")
    w.text(
        "**Bu belge kurgusal bir ÖRNEK ve altyapı testidir; gerçek proje sonucu içermez.** "
        "Tablo ve şekildeki değerler tamamen kurgusaldır."
    )
    w.text(
        "Benzer bir yaklaşım daha önce örnek bir çalışmada ele alınmıştır (Demir, 2019). "
        "Ölçüm yöntemi için kurgusal bir öneri de bulunmaktadır (Kaya ve Yıldız, 2021)."
    )

    w = SectionWriter.at_section(doc, "work")
    w.heading("Kurgusal veriyle biçim testi")
    w.text("Gruplara göre kurgusal oranlar Tablo 1'de, aynı değerler Şekil 1'de özetlenmiştir.")
    w.table(
        _summary_table(),
        "ÖRNEK (kurgusal): gruplara göre oran ve %95 güven aralığı",
        col_widths_cm=[3.0, 2.0, 3.0, 3.0, 3.0],
    )
    _add_dummy_figure(w)
    w.text("Analiz ayrıntıları önceki örnek çalışmayla tutarlıdır (Yılmaz, 2023).")
    if broken:
        # Negatif test: atıfı olmayan Şekil/Tablo + kaynakçasız atıf + placeholder.
        w.text("Ek ayrıntılar Tablo 2'de yer almaktadır (Öztürk, 2020). [DOĞRULANMADI]")

    w = SectionWriter.at_section(doc, "result")
    w.text(
        "Örnek belgede şablon bölümleri, gerçek başlık düzeyleri, SEQ alanlı şekil/tablo "
        "caption'ları ve kaynakça birlikte üretilmiştir."
    )
    w = SectionWriter.at_section(doc, "outputs")
    w.bullets(["Yayın, sunum veya başka çıktı yoktur (örnek belge)."])
    w = SectionWriter.at_section(doc, "expenses")
    w.text("Harcama yoktur (örnek belge).")

    SectionWriter.before_signature(doc).references(REFERENCES)

    out = out or (Path(config.PATHS["report_final"]) / ("sample-report-broken.docx" if broken else "sample-report.docx"))
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out))
    return out


def _add_dummy_figure(w: SectionWriter) -> None:
    """Küçük, kurgusal bir PNG üretir (matplotlib) ve şekil olarak ekler.

    Yalnız SEQ/caption altyapısını sınamak için; içerik kurgusaldır.
    """
    import os
    import tempfile

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(4, 2.4), dpi=100)
    df = _summary_table()
    ax.bar(df["Grup"], df["Oran"], color="#1F3A5F")
    ax.set_ylabel("Oran")
    ax.set_title("ÖRNEK (kurgusal)")
    fig.tight_layout()
    fd, name = tempfile.mkstemp(prefix="kit_sample_figure_", suffix=".png")
    os.close(fd)
    fig.savefig(name)
    plt.close(fig)
    w.figure(Path(name), "ÖRNEK (kurgusal) şekil", width_cm=9.0)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--broken", action="store_true")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    print(build(args.broken, args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
