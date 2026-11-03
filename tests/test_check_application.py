"""check_application.py testleri. Kurgusal (konu-bağımsız) TYBS md'leri kullanır.

Ortak `tmp_kit` fikstürü (tests/conftest.py) gerçek rules/2209a-2026.json + örnek
project.json ile geçici bir KİT kurar. Her test gerektiğinde project.json / belgeleri
kendi kurgusal içeriğiyle üzerine yazar.
"""

from __future__ import annotations

import json

import config

GOOD_TYBS = """# Başvuru

## Başlık

ÖRNEK Proje Başlığı

## Anahtar Kelimeler

bir, iki, üç

## Özet

Bu kurgusal özet, geçerli bir başvurunun alt ve üst kelime sınırları arasında kalmak için
yeterince uzun tutulmuştur; amaç, yöntem, proje yönetimi ve yaygın etki kısaca anılır ve
cümleler konudan bağımsız biçimde yazılmıştır böylece herhangi bir alana uyarlanabilir kalır
ve kelime sayısı yirmi beşin açıkça üzerine çıkar.

## 1.1 Önem

Bu bölüm en az üç yüz elli karakter olmalıdır. Önceki çalışma Soyad (2020) bunu belirtir. {pad}

## 1.2 Amaç

Bu bölüm de en az üç yüz elli karakter olmalıdır. {pad}

## 2. Yöntem

Yöntem bölümü de en az üç yüz elli karakter olmalıdır. {pad}

## 3.1 Çalışma Takvimi

| Proje Süresi (Ay) | Faaliyetler | Kim | Başarı Ölçütü ve Katkısı |
| --- | --- | --- | --- |
| 1-3 | İP1: Tasarım | Ekip | Ölçüt — %50 |
| 4-9 | İP2: Uygulama | Ekip | Ölçüt — %50 |

## 4. Yaygın Etki

Kurgusal yaygın etki metni.

## Kaynakça

1. Soyad, A. 2020. “Kurgusal başlık”, Dergi, 1 (1), 1-10.
""".replace("{pad}", "x" * 360)


def _set_project(tmp_kit, **overrides):
    """Örnek project.json'u denetime uygun kurgusal değerlerle doldurur."""
    p = json.loads(tmp_kit.paths["project_config"].read_text(encoding="utf-8"))
    p.pop("_note", None)
    p["project"]["title"] = "ÖRNEK Proje Başlığı"
    p["project"]["keywords"] = ["bir", "iki", "üç"]
    p["team"]["lead"]["name"] = "Ada Yürütücü"
    p["team"]["advisor"]["name"] = "Danışman Hoca"
    p["timeline"]["duration_months"] = 9
    p["budget"]["total_tl"] = 10000
    p["budget"]["items"] = {"Makine Teçhizat": 6000, "Hizmet Alımı": 4000, "Sarf Malzemesi": 0, "Ulaşım": 0}
    for dotted, value in overrides.items():
        cur = p
        parts = dotted.split(".")
        for part in parts[:-1]:
            cur = cur.setdefault(part, {})
        cur[parts[-1]] = value
    tmp_kit.paths["project_config"].write_text(json.dumps(p, ensure_ascii=False), encoding="utf-8")
    config.project.cache_clear()


def _write_tybs(tmp_kit, text):
    path = tmp_kit.paths["report_tybs"] / "tybs-application.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _set_brands(tmp_kit, brands):
    """rules brand_ban.default_brands'i kurgusal markalarla değiştirir (gerçek markalar değil)."""
    r = json.loads((tmp_kit.paths["rules_dir"] / "2209a-2026.json").read_text(encoding="utf-8"))
    r["brand_ban"]["default_brands"] = brands
    (tmp_kit.paths["rules_dir"] / "2209a-2026.json").write_text(
        json.dumps(r, ensure_ascii=False), encoding="utf-8"
    )
    config.rules.cache_clear()


def test_valid_application_passes(tmp_kit):
    import check_application as ca
    _set_project(tmp_kit)
    path = _write_tybs(tmp_kit, GOOD_TYBS)
    rep = ca.check(path, tybs=True)
    assert rep["problems"] == [], rep["problems"]
    rules_map = {r["rule"].split()[0]: r for r in rep["results"]}
    assert rules_map["Katkı"]["value"] == 100
    assert rules_map["Takvim"]["value"] == 9


def test_short_abstract_fails(tmp_kit):
    import check_application as ca
    _set_project(tmp_kit)
    bad = GOOD_TYBS.replace(
        "Bu kurgusal özet, geçerli bir başvurunun alt ve üst kelime sınırları arasında kalmak için\n"
        "yeterince uzun tutulmuştur; amaç, yöntem, proje yönetimi ve yaygın etki kısaca anılır ve\n"
        "cümleler konudan bağımsız biçimde yazılmıştır böylece herhangi bir alana uyarlanabilir kalır\n"
        "ve kelime sayısı yirmi beşin açıkça üzerine çıkar.",
        "Çok kısa özet.",
    )
    path = _write_tybs(tmp_kit, bad)
    rep = ca.check(path, tybs=True)
    assert any("Özet" in p for p in rep["problems"])


def test_contribution_not_100_fails(tmp_kit):
    import check_application as ca
    _set_project(tmp_kit)
    bad = GOOD_TYBS.replace("Ölçüt — %50 |\n| 4-9", "Ölçüt — %40 |\n| 4-9")
    path = _write_tybs(tmp_kit, bad)
    rep = ca.check(path, tybs=True)
    assert any("Katkı toplamı" in p for p in rep["problems"])


def test_duration_over_limit_fails(tmp_kit):
    import check_application as ca
    _set_project(tmp_kit)
    bad = GOOD_TYBS.replace("| 4-9 |", "| 4-15 |")
    path = _write_tybs(tmp_kit, bad)
    rep = ca.check(path, tybs=True)
    assert any("Takvim" in p for p in rep["problems"])


def test_brand_detected_in_tybs(tmp_kit):
    import check_application as ca
    _set_project(tmp_kit)
    _set_brands(tmp_kit, ["MarkaX", "MarkaY"])
    bad = GOOD_TYBS.replace("Kurgusal yaygın etki metni.", "MarkaX ile geliştirildi.")
    path = _write_tybs(tmp_kit, bad)
    rep = ca.check(path, tybs=True)
    assert any("MarkaX" in p for p in rep["problems"])


def test_extra_brand_from_project(tmp_kit):
    import check_application as ca
    _set_project(tmp_kit, **{"checks.extra_brands": ["ÖzelÜrün"]})
    bad = GOOD_TYBS.replace("Kurgusal yaygın etki metni.", "ÖzelÜrün kullanıldı.")
    path = _write_tybs(tmp_kit, bad)
    rep = ca.check(path, tybs=True)
    assert any("ÖzelÜrün" in p for p in rep["problems"])


def test_forbidden_step_detected(tmp_kit):
    import check_application as ca
    _set_project(tmp_kit)
    bad = GOOD_TYBS.replace("İP2: Uygulama", "İP2: literatür tarama")
    path = _write_tybs(tmp_kit, bad)
    rep = ca.check(path, tybs=True)
    assert any("Ayrı iş adımı" in p for p in rep["problems"])


def test_relative_link_flagged(tmp_kit):
    import check_application as ca
    _set_project(tmp_kit)
    bad = GOOD_TYBS.replace("Kurgusal yaygın etki metni.", "Bak [şuraya](../local/dosya.md).")
    path = _write_tybs(tmp_kit, bad)
    rep = ca.check(path, tybs=True)
    assert any("İç kimlik/bağlantı" in p for p in rep["problems"])


def test_budget_items_mismatch(tmp_kit):
    import check_application as ca
    _set_project(tmp_kit, **{"budget.items": {"Makine Teçhizat": 1000, "Hizmet Alımı": 1000}})
    path = _write_tybs(tmp_kit, GOOD_TYBS)
    rep = ca.check(path, tybs=True)
    assert any("Bütçe kalemleri" in p for p in rep["problems"])


def test_doi_check_without_matching_records(tmp_kit):
    import check_application as ca
    _set_project(tmp_kit)
    # Kaynakça kaydı (references.json) yoksa veya kayıt eşleşmezse DOI sorunu çıkmaz.
    path = _write_tybs(tmp_kit, GOOD_TYBS)
    rep = ca.check(path, tybs=True)
    assert all("DOI'li kaynakta" not in p for p in rep["problems"])
