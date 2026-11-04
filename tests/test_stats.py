"""stats.py testleri: elle/kütüphane sonuçlarının tutarlılığı ve sınır durumlar."""

from __future__ import annotations

import math

import pytest
import stats
from statsmodels.stats.proportion import proportion_confint


def test_wilson_ci_kutuphaneyle_ayni():
    res = stats.wilson_ci(8, 10)
    low, high = proportion_confint(8, 10, alpha=0.05, method="wilson")
    assert res.estimate == pytest.approx(0.8)
    assert res.low == pytest.approx(low)
    assert res.high == pytest.approx(high)


def test_wilson_ci_gecersiz_girdi():
    with pytest.raises(ValueError):
        stats.wilson_ci(11, 10)
    with pytest.raises(ValueError):
        stats.wilson_ci(1, 0)


def test_worst_case_margin():
    # n=100, %95 için ≈ 0,098
    assert stats.worst_case_margin(100) == pytest.approx(1.959963985 * math.sqrt(0.25 / 100), rel=1e-6)
    with pytest.raises(ValueError):
        stats.worst_case_margin(0)


def test_holm_duzeltme():
    out = stats.holm([0.01, 0.04, 0.03])
    assert len(out) == 3
    assert all(o["p_holm"] >= o["p"] for o in out)


def test_mcnemar_test():
    res = stats.mcnemar_test(both_yes=10, only_a=2, only_b=8, both_no=10)
    assert res["table"] == [[10, 2], [8, 10]]
    assert 0.0 <= res["p"] <= 1.0


def test_cohen_kappa_tam_uyum():
    res = stats.cohen_kappa([1, 0, 1, 0], [1, 0, 1, 0])
    assert res["kappa"] == pytest.approx(1.0)
    assert res["raw_agreement"] == pytest.approx(1.0)


def test_cohen_kappa_gecersiz():
    with pytest.raises(ValueError):
        stats.cohen_kappa([1, 0], [1])
    with pytest.raises(ValueError):
        stats.cohen_kappa([], [])


def test_prf1():
    res = stats.prf1(8, 2, 2)
    assert res["precision"] == pytest.approx(0.8)
    assert res["recall"] == pytest.approx(0.8)
    assert res["f1"] == pytest.approx(0.8)
    assert "precision_ci95" in res
    assert "recall_ci95" in res


def test_prf1_sifir_bolme():
    res = stats.prf1(0, 0, 0)
    assert math.isnan(res["precision"])
    assert math.isnan(res["recall"])
    assert math.isnan(res["f1"])


def test_association_test_chi2():
    res = stats.association_test([[30, 10], [20, 40]])
    assert res["method"] == "chi2"
    assert 0.0 <= res["p"] <= 1.0


def test_association_test_fisher_seyrek():
    res = stats.association_test([[1, 0], [0, 1]])
    assert res["method"] == "fisher_exact"
    assert res["sparse"] is True
