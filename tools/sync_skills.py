"""Skill'leri Claude Code ve Codex klasörleri arasında eşitler.

Claude Code `.claude/skills/`, Codex `.agents/skills/` klasörünü okur. Tek kaynak
`.claude/skills/`'tir; `.agents/skills/` bu araçla üretilen birebir kopyadır ve elle
düzenlenmez. (Windows'ta git symlink'leri varsayılan olarak düz dosyaya dönüştüğü için
kopya tercih edildi.)

Kullanım:
    uv run python tools/sync_skills.py           # .claude/skills → .agents/skills
    uv run python tools/sync_skills.py --check   # yalnız denetler; fark varsa çıkış 1 (CI)
"""

from __future__ import annotations

import filecmp
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config


def _dirs() -> tuple[Path, Path]:
    root = config.PATHS["root"]
    return root / ".claude" / "skills", root / ".agents" / "skills"


def differences(src: Path, dst: Path) -> list[str]:
    """src ile dst arasındaki farkları göreli yol olarak listeler."""
    out: list[str] = []
    src_files = {p.relative_to(src) for p in src.rglob("*") if p.is_file()}
    dst_files = {p.relative_to(dst) for p in dst.rglob("*") if p.is_file()} if dst.exists() else set()
    for rel in sorted(src_files - dst_files):
        out.append(f"eksik: {rel.as_posix()}")
    for rel in sorted(dst_files - src_files):
        out.append(f"fazla: {rel.as_posix()}")
    for rel in sorted(src_files & dst_files):
        if not filecmp.cmp(src / rel, dst / rel, shallow=False):
            out.append(f"farklı: {rel.as_posix()}")
    return out


def sync(src: Path, dst: Path) -> list[str]:
    changes = differences(src, dst)
    if changes:
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    return changes


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if config.help_requested(__doc__):
        return 0
    src, dst = _dirs()
    if not src.exists():
        print(f"HATA: {src} yok")
        return 2
    if "--check" in sys.argv:
        diff = differences(src, dst)
        if diff:
            print("Skill kopyası güncel değil. `uv run python tools/sync_skills.py` çalıştırın:")
            print("\n".join(f"  {d}" for d in diff))
            return 1
        print(f"Skill kopyası güncel ({len(list(src.iterdir()))} skill).")
        return 0
    changes = sync(src, dst)
    print(f"{len(changes)} değişiklik eşitlendi → {dst}" if changes else "Zaten güncel.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
