"""status.py testleri."""

from __future__ import annotations

import json
from datetime import date

import config


def _set_project(tmp_kit, **overrides):
    p = json.loads(tmp_kit.paths["project_config"].read_text(encoding="utf-8"))
    p.pop("_note", None)
    p["project"]["title"] = "ÖRNEK Başlık"
    p["project"]["keywords"] = ["a", "b", "c"]
    p["team"]["lead"]["name"] = "Ada"
    p["team"]["advisor"]["name"] = "Hoca"
    p["timeline"]["duration_months"] = 9
    p["budget"]["total_tl"] = 10000
    p["budget"]["items"] = {"Makine Teçhizat": 10000, "Hizmet Alımı": 0, "Sarf Malzemesi": 0, "Ulaşım": 0}
    for dotted, value in overrides.items():
        cur = p
        parts = dotted.split(".")
        for part in parts[:-1]:
            cur = cur.setdefault(part, {})
        cur[parts[-1]] = value
    tmp_kit.paths["project_config"].write_text(json.dumps(p, ensure_ascii=False), encoding="utf-8")
    config.project.cache_clear()


def _write_open_questions(tmp_kit, text):
    path = tmp_kit.paths["open_questions"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_days_left_and_open_questions(tmp_kit):
    import status
    _set_project(tmp_kit)
    _write_open_questions(tmp_kit, "# Açık Sorular\n\n- [ ] Birinci\n- [x] Bitti\n- [ ] İkinci\n")
    rep = status.status(today=date(2026, 11, 4))
    assert rep["days_left"] == 7  # rules.timeline.application_deadline = 2026-11-11
    assert rep["open_questions"] == 2  # yalnız işaretsiz kutular
    assert rep["title"] == "ÖRNEK Başlık"


def test_missing_fields_drives_next_step(tmp_kit):
    import status
    _set_project(tmp_kit, **{"project.title": "TBD"})
    rep = status.status(today=date(2026, 11, 1))
    assert "Proje başlığı" in rep["missing_fields"]
    assert "init_project.py" in rep["next_step"]


def test_audit_summary_runs(tmp_kit):
    import status
    _set_project(tmp_kit)
    # belgeler yoksa check_application 'çalıştırılamadı' döndürmeli, patlamamalı.
    rep = status.status(today=date(2026, 11, 1))
    assert "check_application" in rep["audit"]
    assert "check_consistency" in rep["audit"]
    assert "bibkit" in rep["audit"]


def test_open_questions_none_when_file_missing(tmp_kit):
    import status
    _set_project(tmp_kit)
    # open-questions.md yazılmadı → None
    rep = status.status(today=date(2026, 11, 1))
    assert rep["open_questions"] is None
