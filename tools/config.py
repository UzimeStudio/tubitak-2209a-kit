"""Kitin tek ayar noktası: klasör yolları, proje ayarı (project.json) ve çağrı kuralları (rules/).

Araçlar yolları ve sınırları buradan okur. Hiçbir araçta proje adı, ekip,
tarih, tutar veya çağrı yılı sabit yazılmaz.

Kullanım (başka araçtan):
    from config import PATHS, project, rules
    limit = rules()["abstract"]["max_words"]

Komut satırı:
    uv run python tools/config.py           # ayarları özetler, eksik alanları listeler
    uv run python tools/config.py --json    # birleşik ayarı JSON olarak basar
"""

from __future__ import annotations

import json
import sys
from functools import cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Klasör ve dosya haritası. Yol değişecekse yalnız burası değişir.
PATHS = {
    "root": ROOT,
    "project_config": ROOT / "project.json",
    "project_example": ROOT / "project.example.json",
    "rules_dir": ROOT / "rules",
    "project_dir": ROOT / "project",
    "report_template": ROOT / "project" / "official-report-template.docx",
    "tubitak_sources": ROOT / "project" / "tubitak-sources.md",
    "requirements": ROOT / "project" / "requirements-checklist.md",
    "project_brief": ROOT / "project" / "project-brief.md",
    "sources": ROOT / "sources",
    "references": ROOT / "sources" / "references.json",
    "bib": ROOT / "sources" / "library.bib",
    "matrix_xlsx": ROOT / "sources" / "literature-matrix.xlsx",
    "matrix_rows": ROOT / "sources" / "matrix-rows",
    "verification": ROOT / "sources" / "verification",
    "cache": ROOT / "sources" / "cache",
    "pdf": ROOT / "sources" / "pdf",
    "search_log": ROOT / "sources" / "search-log.md",
    "data_raw": ROOT / "data" / "raw",
    "data_processed": ROOT / "data" / "processed",
    "data_dictionary": ROOT / "data" / "data-dictionary.md",
    "analysis_scripts": ROOT / "analysis" / "scripts",
    "analysis_outputs": ROOT / "analysis" / "outputs",
    "analysis_log": ROOT / "analysis" / "analysis-log.md",
    "figures": ROOT / "figures",
    "tables": ROOT / "tables",
    "report_drafts": ROOT / "report" / "drafts",
    "report_tybs": ROOT / "report" / "tybs",
    "report_final": ROOT / "report" / "final",
    "mock_data": ROOT / "report" / "mock-data.json",
    "logs": ROOT / "logs",
    "ai_use_log": ROOT / "logs" / "ai-use-log.md",
    "decisions": ROOT / "logs" / "decisions.md",
    "open_questions": ROOT / "logs" / "open-questions.md",
    "quality_audit": ROOT / "logs" / "quality-audit.md",
    "templates": ROOT / "templates",
}

# project.json'da doldurulması beklenen alanlar: (nokta yolu, kullanıcıya gösterilen ad)
REQUIRED_FIELDS = [
    ("project.title", "Proje başlığı"),
    ("project.keywords", "Anahtar kelimeler"),
    ("team.lead.name", "Yürütücü adı"),
    ("team.advisor.name", "Danışman adı"),
    ("call.rules_file", "Çağrı kural dosyası"),
    ("budget.total_tl", "Bütçe toplamı"),
    ("timeline.duration_months", "Proje süresi (ay)"),
]

EMPTY = ("", None, [], {}, "TBD")


class ConfigError(RuntimeError):
    """project.json veya rules dosyası okunamadığında."""


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise ConfigError(f"Dosya yok: {path}") from e
    except json.JSONDecodeError as e:
        raise ConfigError(f"JSON bozuk: {path} (satır {e.lineno}): {e.msg}") from e


@cache
def project() -> dict:
    """project.json içeriği."""
    path = PATHS["project_config"]
    if not path.exists():
        raise ConfigError(
            f"{path.name} yok. Önce `uv run python tools/init_project.py` çalıştırın "
            "veya project.example.json dosyasını project.json olarak kopyalayın."
        )
    return _read_json(path)


def latest_rules_file() -> Path:
    files = sorted(PATHS["rules_dir"].glob("2209a-*.json"))
    if not files:
        raise ConfigError("rules/ klasöründe 2209a-*.json yok")
    return files[-1]


@cache
def rules() -> dict:
    """Etkin çağrı kuralları. project.json yoksa en yeni rules dosyası kullanılır."""
    try:
        name = project()["call"]["rules_file"]
    except (ConfigError, KeyError):
        return _read_json(latest_rules_file())
    path = Path(name)
    if not path.is_absolute():
        path = (ROOT / name) if path.parent != Path(".") else PATHS["rules_dir"] / name
    return _read_json(path)


def get(data: dict, dotted: str, default=None):
    """'team.lead.name' gibi bir yolu güvenle okur."""
    value = data
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            return default
        value = value[part]
    return value


def missing_fields() -> list[str]:
    """project.json'da boş veya TBD kalan zorunlu alanlar."""
    p = project()
    return [label for dotted, label in REQUIRED_FIELDS if get(p, dotted) in EMPTY]


def document(key: str) -> Path:
    """project.json 'documents' altındaki göreli yolu mutlak yola çevirir."""
    rel = get(project(), f"documents.{key}")
    if not rel:
        raise ConfigError(f"project.json documents.{key} tanımlı değil")
    return (ROOT / rel).resolve()


def people() -> list[str]:
    """Ekipte adı geçen herkes (yürütücü, ortaklar, danışman); boş olanlar hariç.

    team.members liste değilse (ya da öğeler sözlük değilse) güvenle yok sayılır;
    AttributeError fırlatmaz.
    """
    team = project().get("team", {})
    if not isinstance(team, dict):
        team = {}
    names = [get(team, "lead.name"), get(team, "advisor.name")]
    members = team.get("members")
    if isinstance(members, list):
        names += [m.get("name") for m in members if isinstance(m, dict)]
    return [n for n in names if n not in EMPTY]


def validate_types() -> list[str]:
    """project.json'daki alanların tip beklentilerini denetler; Türkçe ihlal listesi döner.

    Kurallar:
        project.keywords, team.members, ai_tools  -> liste
        budget.items                              -> sözlük
        timeline.duration_months                  -> tam sayı veya null
        checks.* liste alanları (extra_brands, internal_id_patterns) -> liste
        checks.institution_aliases                -> sözlük
    Alanın bulunmaması ihlal sayılmaz; yalnız VAR OLAN ama yanlış tipli değerler bildirilir.
    missing_fields() davranışını DEĞİŞTİRMEZ (ayrı amaç).
    """
    p = project()
    problems: list[str] = []
    _MISSING = object()

    def _check_list(dotted: str, label: str) -> None:
        v = get(p, dotted, _MISSING)
        if v is not _MISSING and v is not None and not isinstance(v, list):
            problems.append(f"{label} ({dotted}) liste olmalı, {type(v).__name__} verilmiş")

    def _check_dict(dotted: str, label: str) -> None:
        v = get(p, dotted, _MISSING)
        if v is not _MISSING and v is not None and not isinstance(v, dict):
            problems.append(f"{label} ({dotted}) sözlük olmalı, {type(v).__name__} verilmiş")

    _check_list("project.keywords", "Anahtar kelimeler")
    _check_list("team.members", "Proje ortakları")
    _check_list("ai_tools", "ÜYZ araçları")
    _check_list("checks.extra_brands", "Ek markalar")
    _check_list("checks.internal_id_patterns", "İç kimlik desenleri")
    _check_dict("budget.items", "Bütçe kalemleri")
    _check_dict("checks.institution_aliases", "Kurum takma adları")

    dm = get(p, "timeline.duration_months", _MISSING)
    if dm is not _MISSING and dm is not None and not (isinstance(dm, int) and not isinstance(dm, bool)):
        problems.append(f"Proje süresi (timeline.duration_months) tam sayı veya null olmalı, "
                        f"{type(dm).__name__} verilmiş")
    return problems


def help_requested(doc: str | None) -> bool:
    """-h/--help verildiyse modül açıklamasını basar ve True döner (araç hiçbir iş yapmaz)."""
    if "-h" in sys.argv[1:] or "--help" in sys.argv[1:]:
        sys.stdout.reconfigure(encoding="utf-8")
        print((doc or "").strip())
        return True
    return False


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if help_requested(__doc__):
        return 0
    try:
        p, r = project(), rules()
    except ConfigError as e:
        print(f"HATA: {e}")
        return 2
    if "--json" in sys.argv:
        print(json.dumps({"project": p, "rules": r}, ensure_ascii=False, indent=2))
        return 0
    print(f"Proje    : {get(p, 'project.title') or '(başlık yok)'}")
    print(f"Çağrı    : {r.get('call_name')} ({r.get('year')}), kontrol {r.get('checked_on')}")
    print(f"Son gün  : {get(r, 'timeline.application_deadline')}")
    missing = missing_fields()
    print("Eksik    : " + (", ".join(missing) if missing else "yok"))
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
