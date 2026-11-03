"""Ortak test fikstürleri. Tüm araç testleri burayı paylaşır.

`tmp_kit` fikstürü, gerçek repoya dokunmadan geçici bir KİT kökü kurar:
    - tmp_path altına PATHS'teki tüm klasörleri (ve dosya yollarının üst klasörlerini) açar,
    - rules/2209a-2026.json dosyasını kopyalar,
    - project.example.json'dan project.json üretir,
    - config.PATHS'i geçici köke yönlendirir ve project()/rules() önbelleğini temizler.

Araçlar PATHS'i çağrı anında okuduğu için bu yönlendirme bütün araçları kapsar.
Fikstür, kurduğu geçici kökü (TmpKit) döndürür; testler ek dosya yazmak için kullanır.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

import config
import pytest

# Gerçek repo kökü: bu dosya tests/ altında, repo kökü bir üst klasör.
REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class TmpKit:
    """Geçici KİT kökü ve sık kullanılan yollar."""

    root: Path
    paths: dict

    def write_references(self, records: list[dict]) -> Path:
        """sources/references.json dosyasını verilen kayıtlarla yazar."""
        path = self.paths["references"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        return path


def _is_dir_key(name: str, path: Path) -> bool:
    """PATHS girdisi klasör mü dosya mı? Uzantısı olanları dosya sayarız."""
    return path.suffix == ""


@pytest.fixture
def tmp_kit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TmpKit:
    new_root = tmp_path / "kit"
    new_root.mkdir()

    # PATHS girdilerini YERİNDE değiştir (setitem): araçlar `from config import PATHS`
    # ile aynı sözlük nesnesine bağlı; nesneyi değiştirmek yerine içeriğini güncelleriz.
    new_paths: dict = {}
    for key, original in config.PATHS.items():
        if key == "root":
            target = new_root
        else:
            rel = Path(original).relative_to(REPO_ROOT)
            target = new_root / rel
            # Klasör yolları doğrudan, dosya yolları üst klasörleriyle açılır.
            (target if _is_dir_key(key, target) else target.parent).mkdir(parents=True, exist_ok=True)
        new_paths[key] = target
        monkeypatch.setitem(config.PATHS, key, target)

    monkeypatch.setattr(config, "ROOT", new_root)

    # rules dosyasını kopyala.
    shutil.copy(REPO_ROOT / "rules" / "2209a-2026.json", new_paths["rules_dir"] / "2209a-2026.json")

    # project.example.json'dan project.json üret.
    example = json.loads((REPO_ROOT / "project.example.json").read_text(encoding="utf-8"))
    new_paths["project_config"].write_text(
        json.dumps(example, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    config.project.cache_clear()
    config.rules.cache_clear()
    yield TmpKit(root=new_root, paths=new_paths)
    config.project.cache_clear()
    config.rules.cache_clear()
