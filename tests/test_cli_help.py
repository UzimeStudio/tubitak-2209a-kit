"""Her komut satırı aracı --help ile iş yapmadan (ağ, dosya yazma, soru sorma yok) 0 ile çıkar."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
CLI = [
    "bibkit",
    "verify_source",
    "matrix",
    "md2docx",
    "docx_to_pdf",
    "pdf_check",
    "check_report",
    "check_application",
    "check_consistency",
    "call_watch",
    "status",
    "init_project",
    "import_draft",
    "sample_report",
    "config",
    "sync_skills",
]


@pytest.mark.parametrize("tool", CLI)
def test_help_exits_cleanly(tool):
    proc = subprocess.run(
        [sys.executable, str(TOOLS / f"{tool}.py"), "--help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        timeout=30,
        stdin=subprocess.DEVNULL,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip(), "yardım metni boş"
    assert "Traceback" not in proc.stderr
