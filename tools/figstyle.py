"""Yayın kalitesinde matplotlib şekilleri için ortak stil ve kayıt.

Her şekil üç dosyayla saklanır:
    figures/<ad>.png   300 dpi, Word'e eklenecek görsel
    figures/<ad>.svg   düzenlenebilir vektör
    figures/<ad>.csv   şeklin çizildiği veri (yeniden üretim)
ve figures/<ad>.json içinde başlık, açıklama, kaynak betik ve veri durumu.

Çıktı klasörü `config.PATHS["figures"]`'ten çağrı anında okunur; böylece testler
geçici klasöre yönlendirebilir.
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import PATHS

# Renk körlüğüne duyarlı Okabe–Ito paleti
PALETTE = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9", "#F0E442", "#000000"]

# Şablon gövdesi Arial; şekil yazıları da Arial.
STYLE = {
    "font.family": "Arial",
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "axes.prop_cycle": matplotlib.cycler(color=PALETTE),
    "figure.dpi": 100,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.formatter.use_locale": False,
}

# A4, 2,5 cm kenar boşluğu: metin genişliği 16 cm
TEXT_WIDTH_IN = 16 / 2.54


def apply() -> None:
    """Ortak şekil stilini matplotlib'e uygular."""
    plt.rcParams.update(STYLE)


def turkish_decimal(ax, axis: str = "y", decimals: int = 2) -> None:
    """Eksen sayılarını Türkçe ondalık virgülle yazar."""
    from matplotlib.ticker import FuncFormatter

    fmt = FuncFormatter(lambda v, _: f"{v:.{decimals}f}".replace(".", ","))
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)


def save(fig, name: str, data: pd.DataFrame, *, caption: str, script: str, synthetic: bool) -> dict:
    """Şekli PNG+SVG, verisini CSV, üst verisini JSON olarak kaydeder.

    Çıktı klasörü çağrı anında `PATHS["figures"]`'ten okunur.
    """
    figures = PATHS["figures"]
    figures.mkdir(parents=True, exist_ok=True)
    png, svg = figures / f"{name}.png", figures / f"{name}.svg"
    fig.savefig(png)
    fig.savefig(svg)
    data.to_csv(figures / f"{name}.csv", index=False, encoding="utf-8")
    meta = {
        "name": name,
        "caption": caption,
        "script": script,
        "synthetic_data": synthetic,
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "files": [png.name, svg.name, f"{name}.csv"],
    }
    (figures / f"{name}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    plt.close(fig)
    return meta
