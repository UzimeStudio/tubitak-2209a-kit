"""Başvuru ve analiz aşamasında sık kullanılan istatistik yöntemleri.

Yöntem ↔ kaynak eşlemesi (künyeler sources/library.bib'e eklenir):
    wilson_ci          Wilson (1927)       oranlar için güven aralığı
    holm               Holm (1979)         çoklu karşılaştırma düzeltmesi
    mcnemar_test       McNemar (1947)      eşli ikili ölçüm değişimi
    cohen_kappa        Cohen (1960)        iki etiketçi uyumu
    prf1               —                   precision, recall, F1
    association_test   Chi-square / Fisher kategorik ilişki; seyrek hücrede exact test

Hesaplar statsmodels/scipy ile yapılır. Elle yazılan formüller testlerde
kütüphane sonucuyla karşılaştırılır. Tüm fonksiyonlar saf girdi alır;
ham veriyi değiştirmez. Belirli bir projeye ya da veri kümesine bağlı değildir.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass

import numpy as np
from scipy import stats
from statsmodels.stats.contingency_tables import mcnemar
from statsmodels.stats.inter_rater import cohens_kappa
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint


@dataclass(frozen=True)
class Proportion:
    """Bir oran tahmini ve güven aralığı."""

    successes: int
    n: int
    estimate: float
    low: float
    high: float
    method: str = "wilson"
    confidence: float = 0.95


def wilson_ci(successes: int, n: int, confidence: float = 0.95) -> Proportion:
    """Oran için Wilson güven aralığı."""
    if n <= 0 or not 0 <= successes <= n:
        raise ValueError("0 <= successes <= n ve n > 0 olmalı")
    low, high = proportion_confint(successes, n, alpha=1 - confidence, method="wilson")
    return Proportion(successes, n, successes / n, float(low), float(high), confidence=confidence)


def worst_case_margin(n: int, confidence: float = 0.95) -> float:
    """p=0,5 için normal yaklaşım yarı genişliği (örneklem büyüklüğü planında kullanılır)."""
    if n <= 0:
        raise ValueError("n > 0 olmalı")
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    return float(z * math.sqrt(0.25 / n))


def holm(pvalues: list[float], alpha: float = 0.05) -> list[dict]:
    """Holm–Bonferroni ile çoklu karşılaştırma düzeltmesi."""
    reject, adjusted, _, _ = multipletests(pvalues, alpha=alpha, method="holm")
    return [
        {"p": p, "p_holm": float(a), "reject": bool(r)}
        for p, a, r in zip(pvalues, adjusted, reject, strict=False)
    ]


def mcnemar_test(both_yes: int, only_old: int, only_new: int, both_no: int) -> dict:
    """Eşli ikili ölçümlerde değişim için McNemar testi (seyrek durumda exact)."""
    table = [[both_yes, only_old], [only_new, both_no]]
    exact = (only_old + only_new) < 25
    res = mcnemar(table, exact=exact, correction=not exact)
    return {"table": table, "exact": exact, "statistic": float(res.statistic), "p": float(res.pvalue)}


def cohen_kappa(labels_a: list, labels_b: list) -> dict:
    """İki etiketçi arasındaki uyum için Cohen's kappa katsayısı."""
    if len(labels_a) != len(labels_b) or not labels_a:
        raise ValueError("Etiket listeleri aynı uzunlukta ve boş olmamalı")
    cats = sorted(set(labels_a) | set(labels_b), key=str)
    idx = {c: i for i, c in enumerate(cats)}
    table = np.zeros((len(cats), len(cats)), dtype=int)
    for a, b in zip(labels_a, labels_b, strict=False):
        table[idx[a], idx[b]] += 1
    res = cohens_kappa(table)
    raw = float(np.trace(table) / table.sum())
    return {
        "categories": cats,
        "table": table.tolist(),
        "raw_agreement": raw,
        "kappa": float(res.kappa),
        "kappa_ci95": (float(res.kappa_low), float(res.kappa_upp)),
        "n": int(table.sum()),
    }


def prf1(tp: int, fp: int, fn: int) -> dict:
    """Precision, recall ve F1 (oranlara Wilson güven aralığı eklenir)."""
    precision = tp / (tp + fp) if tp + fp else float("nan")
    recall = tp / (tp + fn) if tp + fn else float("nan")
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else float("nan")
    out = {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": f1}
    if tp + fp:
        out["precision_ci95"] = asdict(wilson_ci(tp, tp + fp))
    if tp + fn:
        out["recall_ci95"] = asdict(wilson_ci(tp, tp + fn))
    return out


def association_test(table: list[list[int]]) -> dict:
    """r×c çapraz tabloda kategorik ilişki testi.

    Beklenen değeri 5'in altında hücre varsa ve tablo 2×2 ise Fisher exact test kullanılır.
    """
    arr = np.asarray(table)
    chi2, p, dof, expected = stats.chi2_contingency(arr)
    sparse = bool((expected < 5).any())
    if sparse and arr.shape == (2, 2):
        _, p_exact = stats.fisher_exact(arr)
        return {"method": "fisher_exact", "p": float(p_exact), "sparse": True}
    return {
        "method": "chi2",
        "statistic": float(chi2),
        "dof": int(dof),
        "p": float(p),
        "sparse": sparse,
        "note": "Seyrek r×c tabloda exact/permütasyon testi ayrıca planlanmalı" if sparse else "",
    }
