"""sync_skills: kopya üretimi, fark tespiti ve depodaki kopyanın güncelliği."""

from __future__ import annotations

from pathlib import Path

import sync_skills

ROOT = Path(__file__).resolve().parents[1]


def test_sync_and_check(tmp_path):
    src, dst = tmp_path / "src", tmp_path / "dst"
    (src / "a").mkdir(parents=True)
    (src / "a" / "SKILL.md").write_text("---\nname: a\n---\n", encoding="utf-8")
    assert sync_skills.differences(src, dst) == ["eksik: a/SKILL.md"]
    sync_skills.sync(src, dst)
    assert sync_skills.differences(src, dst) == []
    (dst / "a" / "SKILL.md").write_text("elle düzenlendi", encoding="utf-8")
    (dst / "b.md").write_text("x", encoding="utf-8")
    assert sync_skills.differences(src, dst) == ["fazla: b.md", "farklı: a/SKILL.md"]


def test_repository_copy_is_in_sync():
    """Codex kopyası (.agents/skills) Claude kopyasıyla birebir aynı olmalı."""
    diff = sync_skills.differences(ROOT / ".claude" / "skills", ROOT / ".agents" / "skills")
    assert diff == [], "tools/sync_skills.py çalıştırın: " + ", ".join(diff[:5])
