"""Tek ekranda proje durumu: eksikler, son güne kalan, denetim sonuçları, sıradaki adım.

Gösterir:
    - project.json'da eksik (TBD/boş) zorunlu alanlar.
    - Başvuru son gününe kalan gün (bugün ↔ rules.timeline.application_deadline).
    - check_application + check_consistency + bibkit lint sonuç/sorun sayıları
      (ilgili modül yoksa 'çalıştırılamadı').
    - logs/open-questions.md içindeki açık '- [ ]' kutu sayısı.
    - Sıradaki önerilen adım.

Kullanım:
    uv run python tools/status.py [--json]
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from config import ConfigError, document, get, missing_fields, project, rules


def _days_left(r: dict, today: date) -> int | None:
    deadline = get(r, "timeline.application_deadline")
    if not deadline:
        return None
    try:
        dt = datetime.fromisoformat(deadline).date()
    except ValueError:
        try:
            dt = datetime.strptime(deadline[:10], "%Y-%m-%d").date()
        except ValueError:
            return None
    return (dt - today).days


def _open_questions() -> int | None:
    path = config.PATHS["open_questions"]
    if not path.exists():
        return None
    return len(re.findall(r"^\s*[-*]\s*\[ \]", path.read_text(encoding="utf-8"), flags=re.MULTILINE))


class _Skip(Exception):
    """Denetlenecek belge yoksa denetimi atlamak için."""


def _audit_summary() -> dict:
    summary = {}
    # check_application
    try:
        import check_application
        path, tybs = None, False
        for key, is_tybs in (("tybs", True), ("proposal", False)):
            try:
                candidate = document(key)
            except ConfigError:
                continue
            if candidate.exists():
                path, tybs = candidate, is_tybs
                break
        if path is None:
            summary["check_application"] = {"status": "öneri metni henüz yok (templates/proposal.md'den başlayın)"}
            raise _Skip
        rep = check_application.check(path, tybs=tybs)
        summary["check_application"] = {
            "results": len(rep["results"]),
            "failing": sum(1 for r in rep["results"] if not r["ok"]),
            "problems": len(rep["problems"]),
            "manual": len(rep.get("manual_review", [])),
        }
    except _Skip:
        pass
    except Exception as e:  # noqa: BLE001
        summary["check_application"] = {"status": f"çalıştırılamadı: {e}"}
    # check_consistency
    try:
        import check_consistency
        rep = check_consistency.check()
        summary["check_consistency"] = {"problems": len(rep["problems"]), "warnings": len(rep["warnings"])}
    except Exception as e:  # noqa: BLE001
        summary["check_consistency"] = {"status": f"çalıştırılamadı: {e}"}
    # bibkit lint
    try:
        import bibkit
        problems = bibkit.lint(bibkit.load())
        summary["bibkit"] = {"problems": len(problems)}
    except Exception as e:  # noqa: BLE001
        summary["bibkit"] = {"status": f"çalıştırılamadı: {e}"}
    return summary


def _next_step(missing, days_left, audit) -> str:
    if missing:
        return f"project.json eksik alanları doldur: {', '.join(missing)} (init_project.py)"
    ca = audit.get("check_application", {})
    if ca.get("problems"):
        return "check_application.py sorunlarını gider"
    cc = audit.get("check_consistency", {})
    if cc.get("problems"):
        return "check_consistency.py sorunlarını gider"
    if audit.get("bibkit", {}).get("problems"):
        return "kaynakça kayıtlarını düzelt (bibkit lint)"
    if days_left is not None and days_left <= 7:
        return "Son kontrolleri yap ve TYBS'ye yapıştır; danışman onayını al"
    return "Öneri metnini hakem gözüyle gözden geçir"


def status(today: date | None = None) -> dict:
    today = today or date.today()
    try:
        p = project()
        r = rules()
    except ConfigError as e:
        return {"error": str(e)}
    missing = missing_fields()
    days_left = _days_left(r, today)
    audit = _audit_summary()
    return {
        "title": get(p, "project.title"),
        "missing_fields": missing,
        "days_left": days_left,
        "application_deadline": get(r, "timeline.application_deadline"),
        "audit": audit,
        "open_questions": _open_questions(),
        "next_step": _next_step(missing, days_left, audit),
    }


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if config.help_requested(__doc__):
        return 0
    rep = status()
    if "--json" in sys.argv:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
        return 0
    if "error" in rep:
        print(f"HATA: {rep['error']}")
        return 2
    print(f"Proje     : {rep['title'] or '(başlık yok)'}")
    dl = rep["days_left"]
    print(f"Son gün   : {rep['application_deadline']} ({dl} gün kaldı)" if dl is not None else "Son gün   : ?")
    print("Eksik     : " + (", ".join(rep["missing_fields"]) if rep["missing_fields"] else "yok"))
    for name, d in rep["audit"].items():
        if "status" in d:
            print(f"{name:<18}: {d['status']}")
        else:
            print(f"{name:<18}: " + ", ".join(f"{k}={v}" for k, v in d.items()))
    oq = rep["open_questions"]
    print(f"Açık soru : {oq if oq is not None else 'dosya yok'}")
    print(f"Sıradaki  : {rep['next_step']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
