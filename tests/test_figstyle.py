"""figstyle.py testleri: stil uygulama ve şekil/veri/üstveri kaydı."""

from __future__ import annotations

import json

import figstyle
import matplotlib.pyplot as plt
import pandas as pd


def test_apply_stil():
    figstyle.apply()
    assert plt.rcParams["savefig.dpi"] == 300
    assert plt.rcParams["axes.spines.top"] is False


def test_turkish_decimal_virgul():
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0.5, 1.5])
    figstyle.turkish_decimal(ax, "y", decimals=1)
    fig.canvas.draw()
    fmt = ax.yaxis.get_major_formatter()
    assert fmt(0.5, None) == "0,5"
    plt.close(fig)


def test_save_dosyalari_uretir(tmp_kit):
    figstyle.apply()
    fig, ax = plt.subplots()
    data = pd.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    ax.plot(data["x"], data["y"])
    meta = figstyle.save(
        fig, "ornek-sekil", data, caption="Örnek şekil", script="test_figstyle.py", synthetic=True
    )
    figures = tmp_kit.paths["figures"]
    assert (figures / "ornek-sekil.png").exists()
    assert (figures / "ornek-sekil.svg").exists()
    assert (figures / "ornek-sekil.csv").exists()
    meta_file = figures / "ornek-sekil.json"
    assert meta_file.exists()
    saved = json.loads(meta_file.read_text(encoding="utf-8"))
    assert saved["synthetic_data"] is True
    assert saved["caption"] == "Örnek şekil"
    assert meta["name"] == "ornek-sekil"


def test_save_cagri_aninda_yol_okur(tmp_kit):
    # save, PATHS["figures"]'i çağrı anında okur; tmp_kit yönlendirmesi geçerli olmalı.
    figstyle.apply()
    fig, ax = plt.subplots()
    data = pd.DataFrame({"x": [1], "y": [2]})
    ax.plot(data["x"], data["y"])
    figstyle.save(fig, "ikinci", data, caption="c", script="s", synthetic=False)
    assert (tmp_kit.paths["figures"] / "ikinci.png").exists()
