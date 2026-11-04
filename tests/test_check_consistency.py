"""check_consistency.py testleri. Kurgusal proposal/TYBS md'leri kullanır."""

from __future__ import annotations

import json

import config

REPO_ROOT = config.ROOT  # tmp_kit monkeypatch'inden ÖNCE okunur; gerçek repo kökü.

CONSISTENT = """# Belge

## Başlık

ÖRNEK Başlık

## 1.1 Önem

anahtar1 ve anahtar2 burada geçer. Ada Yürütücü ve Danışman Hoca ekiptedir.
Örneklem %30 düzeyindedir.

## 3.1 Çalışma Takvimi

| Proje Süresi (Ay) | Faaliyetler | Kim | Katkı |
| --- | --- | --- | --- |
| 1-9 | İP1 | Ada Yürütücü | %100 |

## Hipotezler

- H1 (keşifsel): Bir örnek hipotez tanımı.
"""


def _set_project(tmp_kit, **overrides):
    p = json.loads(tmp_kit.paths["project_config"].read_text(encoding="utf-8"))
    p.pop("_note", None)
    p["project"]["title"] = "ÖRNEK Başlık"
    p["project"]["keywords"] = ["anahtar1", "anahtar2"]
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


def _write(tmp_kit, proposal_text, tybs_text):
    pr = tmp_kit.paths["report_drafts"] / "proposal.md"
    tb = tmp_kit.paths["report_tybs"] / "tybs-application.md"
    pr.parent.mkdir(parents=True, exist_ok=True)
    tb.parent.mkdir(parents=True, exist_ok=True)
    pr.write_text(proposal_text, encoding="utf-8")
    tb.write_text(tybs_text, encoding="utf-8")


def test_consistent_docs_no_problems(tmp_kit):
    import check_consistency as cc
    _set_project(tmp_kit)
    _write(tmp_kit, CONSISTENT, CONSISTENT)
    rep = cc.check()
    assert rep["problems"] == [], rep["problems"]


def test_duration_mismatch_detected(tmp_kit):
    import check_consistency as cc
    _set_project(tmp_kit)
    bad_tybs = CONSISTENT.replace("| 1-9 |", "| 1-12 |")
    _write(tmp_kit, CONSISTENT, bad_tybs)
    rep = cc.check()
    assert any("Süre uyuşmazlığı" in p for p in rep["problems"])


def test_budget_items_mismatch_detected(tmp_kit):
    import check_consistency as cc
    _set_project(tmp_kit, **{"budget.items": {"Makine Teçhizat": 1000, "Hizmet Alımı": 1000}})
    _write(tmp_kit, CONSISTENT, CONSISTENT)
    rep = cc.check()
    assert any("kalemler toplamı" in p for p in rep["problems"])


def test_placeholder_detected(tmp_kit):
    import check_consistency as cc
    _set_project(tmp_kit)
    bad = CONSISTENT.replace("Bir örnek hipotez tanımı.", "TODO: doldurulacak.")
    _write(tmp_kit, bad, CONSISTENT)
    rep = cc.check()
    assert any("Yer tutucu" in p and "TODO" in p for p in rep["problems"])


def test_undefined_identifier_detected(tmp_kit):
    import check_consistency as cc
    _set_project(tmp_kit)
    bad = CONSISTENT.replace("- H1 (keşifsel): Bir örnek hipotez tanımı.", "H1 sonucu burada tartışılır.")
    _write(tmp_kit, bad, CONSISTENT)
    rep = cc.check()
    assert any("Tanımsız kimlik" in p and "H1" in p for p in rep["problems"])


def test_numeric_diff_between_docs_warns(tmp_kit):
    import check_consistency as cc
    _set_project(tmp_kit)
    bad_tybs = CONSISTENT.replace("Örneklem %30 düzeyindedir.", "Örneklem %40 düzeyindedir.")
    _write(tmp_kit, CONSISTENT, bad_tybs)
    rep = cc.check()
    assert any("sayısal değerler farklı" in w for w in rep["warnings"])


def test_result_language_warns(tmp_kit):
    import check_consistency as cc
    _set_project(tmp_kit)
    bad = CONSISTENT.replace("Örneklem %30 düzeyindedir.", "Etki tespit edilmiştir.")
    _write(tmp_kit, bad, CONSISTENT)
    rep = cc.check()
    assert any("Sonuç dili" in w for w in rep["warnings"])


def test_untouched_template_gives_one_note_not_warning_flood(tmp_kit):
    """Şablondan yeni açılmış taslak: başlık/ekip/anahtar kelime uyarısı yerine tek not."""
    import check_consistency as cc
    _set_project(tmp_kit)
    for name in ("proposal.md", "tybs-application.md"):
        src = (REPO_ROOT / "templates" / name).read_text(encoding="utf-8")
        (tmp_kit.paths["templates"] / name).write_text(src, encoding="utf-8")
    _write(
        tmp_kit,
        (tmp_kit.paths["templates"] / "proposal.md").read_text(encoding="utf-8"),
        (tmp_kit.paths["templates"] / "tybs-application.md").read_text(encoding="utf-8"),
    )
    rep = cc.check()
    assert any("hâlâ boş şablon" in w for w in rep["warnings"])
    assert not any("geçmiyor" in w for w in rep["warnings"]), rep["warnings"]


def test_long_title_truncation_is_marked(tmp_kit):
    import check_consistency as cc
    long_title = "Uzun başlık " * 10
    _set_project(tmp_kit, **{"project.title": long_title.strip()})
    _write(tmp_kit, CONSISTENT, CONSISTENT)
    rep = cc.check()
    assert any("…'" in w for w in rep["warnings"] if "başlığı" in w)
