"""project.json kurulumu: etkileşimli Türkçe sorular, örnekten kopyalama, alan güncelleme.

Modlar:
    uv run python tools/init_project.py                  # etkileşimli Türkçe sorular; Enter = TBD
    uv run python tools/init_project.py --defaults        # project.example.json'u olduğu gibi kopyalar
    uv run python tools/init_project.py --set path=value  # tek alanı günceller (tekrarlanabilir)
    uv run python tools/init_project.py --set-json path=dosya.json   # değeri dosyadan okur (tırnaksız)
    uv run python tools/init_project.py --merge values.json          # birçok alanı tek dosyadan yazar
    uv run python tools/init_project.py --force           # var olan project.json'u yeniden kurar

--set değeri önce JSON olarak çözülür ("[\"a\",\"b\"]", "12000", "true"); çözülemezse
düz metin kabul edilir. ANCAK liste/sözlük beklenen alanlarda (project.keywords,
team.members, ai_tools, budget.items ve checks.* liste/sözlük alanları) JSON çözülemezse
araç sessizce metin YAZMAZ; hata verir (çıkış 2) ve PowerShell tırnak ipucu gösterir:
    uv run python tools/init_project.py --set 'project.keywords=[\"a\",\"b\"]'
Kolaylık: project.keywords için virgülle ayrılmış düz metin ('a, b, c') kabul edilir ve
listeye çevrilir.

Tırnak sorununu tümden aşmak için değeri bir dosyadan okuyun:
    uv run python tools/init_project.py --set-json team.members=members.json
(members.json içeriği geçerli JSON olmalı; aksi halde çıkış 2.)

Birden çok alanı tek dosyadan yazmak için (ajanlar için önerilen yol):
    uv run python tools/init_project.py --merge values.json
values.json project.json ile aynı biçimde kısmi bir nesnedir, ör.
{"project": {"title": "..."}, "team": {"lead": {"name": "..."}}}. Yalnız dosyada
olan alanlar değişir; her alan --set ile aynı tip denetiminden geçer.

Var olan project.json --force olmadan BÜTÜN olarak değiştirilmez; yalnız --set/--set-json
ile tek alan güncellemesine izin verilir.
Eksik logs/*.md dosyaları templates/logs/ varsa oradan, yoksa kısa başlıklarla
oluşturulur. Sonda config.missing_fields() ve config.validate_types() listeleri basılır.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from config import ConfigError

# (nokta yolu, Türkçe soru). Liste/sözlük alanları ayrıca sorulur.
QUESTIONS = [
    ("project.title", "Proje başlığı"),
    ("project.short_name", "Kısa ad (opsiyonel)"),
    (
        "project.project_type",
        "Proje türü (software/experiment/field-study/survey/data-analysis/design/other)",
    ),
    ("project.scientific_field", "Bilimsel ve teknolojik alan"),
    ("team.lead.name", "Yürütücü adı"),
    ("team.advisor.name", "Danışman adı"),
    ("timeline.duration_months", "Proje süresi (ay, sayı)"),
    ("budget.total_tl", "Bütçe toplamı (TL, sayı)"),
]

NUMERIC_FIELDS = {"timeline.duration_months", "budget.total_tl"}

# Liste bekleyen alanlar: JSON çözülemezse metin yazma yerine hata ver.
LIST_FIELDS = {
    "project.keywords",
    "team.members",
    "ai_tools",
    "checks.extra_brands",
    "checks.internal_id_patterns",
}
# Sözlük bekleyen alanlar.
DICT_FIELDS = {
    "budget.items",
    "checks.institution_aliases",
}
# Virgülle ayrılmış düz metni listeye çevirmeye izin verilen alanlar (kolaylık).
CSV_LIST_FIELDS = {"project.keywords", "ai_tools"}

QUOTE_HINT = (
    "PowerShell JSON tırnaklarını yutabilir. Tek tırnak içine alın "
    '(örn. --set \'project.keywords=["a","b"]\') veya --set-json ile dosyadan okutun '
    "(örn. --set-json project.keywords=keywords.json)."
)

LOG_FILES = {
    "ai-use-log.md": "# ÜYZ Kullanım Günlüğü\n\nAraç, sürüm, aşama ve kullanım niteliği buraya yazılır.\n",
    "decisions.md": "# Kararlar\n\nProje boyunca alınan bilinçli kararlar ve gerekçeleri.\n",
    "open-questions.md": "# Açık Sorular\n\n- [ ] İlk açık soru buraya.\n",
    "quality-audit.md": "# Kalite Denetimi\n\nDenetim çalıştırmaları ve sonuçları.\n",
}


def _parse(value: str):
    """--set değerini JSON olarak dener, olmazsa düz metin (serbest alanlar için)."""
    try:
        return json.loads(value)
    except (json.JSONDecodeError, ValueError):
        return value


def _resolve_value(dotted: str, raw: str) -> object:
    """Alanın tipine göre --set değerini çözer; liste/sözlük alanında hatalıysa ConfigError.

    - Liste/sözlük beklenen alanda JSON çözülemezse (ve CSV kolaylığı uygulanamazsa)
      ConfigError fırlatılır; sessizce metin YAZILMAZ.
    - CSV_LIST_FIELDS alanlarında virgüllü düz metin ('a, b, c') listeye çevrilir.
    - Diğer alanlarda eski davranış: JSON dene, olmazsa düz metin.
    """
    if dotted in LIST_FIELDS or dotted in DICT_FIELDS:
        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, ValueError) as e:
            if dotted in CSV_LIST_FIELDS and "," in raw:
                return [p.strip() for p in raw.split(",") if p.strip()]
            expected = "liste" if dotted in LIST_FIELDS else "sözlük"
            raise ConfigError(
                f"'{dotted}' için {expected} bekleniyor ama değer JSON değil: {e}. {QUOTE_HINT}"
            ) from e
        want_list = dotted in LIST_FIELDS
        if want_list and not isinstance(parsed, list):
            # CSV kolaylığı: düz metin JSON olarak string'e çözülmüşse virgülle böl.
            if dotted in CSV_LIST_FIELDS and isinstance(parsed, str):
                return [p.strip() for p in parsed.split(",") if p.strip()]
            raise ConfigError(f"'{dotted}' bir liste olmalı, {type(parsed).__name__} verilmiş. {QUOTE_HINT}")
        if not want_list and not isinstance(parsed, dict):
            raise ConfigError(f"'{dotted}' bir sözlük olmalı, {type(parsed).__name__} verilmiş. {QUOTE_HINT}")
        return parsed
    return _parse(raw)


def _set_in(data: dict, dotted: str, value) -> None:
    parts = dotted.split(".")
    d = data
    for p in parts[:-1]:
        d = d.setdefault(p, {})
        if not isinstance(d, dict):
            raise ConfigError(f"'{dotted}' yolu bir sözlük değil")
    d[parts[-1]] = value


def _example() -> dict:
    return json.loads(config.PATHS["project_example"].read_text(encoding="utf-8"))


def _write(data: dict) -> None:
    config.PATHS["project_config"].write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _collect_set_args(argv: list[str]) -> list[tuple[str, str, bool]]:
    """--set ve --set-json çiftlerini sırayla toplar.

    Döner: (dotted, raw_or_path, from_file) üçlüleri. --set-json'da raw_or_path
    bir dosya yoludur ve içeriği JSON olarak okunur.
    """
    out: list[tuple[str, str, bool]] = []
    i = 0
    while i < len(argv):
        if argv[i] == "--set" and i + 1 < len(argv):
            out.append((*_split_pair(argv[i + 1]), False))
            i += 2
        elif argv[i] == "--set-json" and i + 1 < len(argv):
            out.append((*_split_pair(argv[i + 1]), True))
            i += 2
        elif argv[i] == "--merge" and i + 1 < len(argv):
            # Dosyadaki iç içe nesne yaprak alanlara açılır; her yaprak --set gibi doğrulanır.
            out.extend(
                (dotted, json.dumps(value, ensure_ascii=False), False)
                for dotted, value in _flatten(_read_json_file(argv[i + 1]))
            )
            i += 2
        else:
            i += 1
    return out


def _read_json_file(raw: str) -> object:
    path = Path(raw)
    if not path.exists():
        raise ConfigError(f"JSON dosyası bulunamadı: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, ValueError) as e:
        raise ConfigError(f"Dosya geçerli JSON değil: {path} ({e})") from e


def _flatten(data: object, prefix: str = "") -> list[tuple[str, object]]:
    """{'team': {'lead': {'name': 'A'}}} → [('team.lead.name', 'A')]. Listeler yapraktır."""
    if not isinstance(data, dict):
        if not prefix:
            raise ConfigError("--merge dosyası bir JSON nesnesi olmalı ({...})")
        return [(prefix, data)]
    out: list[tuple[str, object]] = []
    for key, value in data.items():
        if key.startswith("_"):
            continue
        dotted = f"{prefix}.{key}" if prefix else key
        out += _flatten(value, dotted) if isinstance(value, dict) and value else [(dotted, value)]
    return out


def _split_pair(pair: str) -> tuple[str, str]:
    dotted, sep, value = pair.partition("=")
    if not sep:
        raise ConfigError(f"--set '{pair}' 'path=value' biçiminde değil")
    return dotted.strip(), value


def _value_for(dotted: str, raw: str, from_file: bool) -> object:
    """Bir --set/--set-json çiftinin nihai değerini çözer."""
    if from_file:
        return _read_json_file(raw)
    return _resolve_value(dotted, raw)


def _create_log_files() -> list[str]:
    created = []
    target = config.PATHS["logs"]
    target.mkdir(parents=True, exist_ok=True)
    template_dir = config.PATHS["templates"] / "logs"
    for name, default in LOG_FILES.items():
        path = target / name
        if path.exists():
            continue
        template = template_dir / name
        path.write_text(
            template.read_text(encoding="utf-8") if template.exists() else default,
            encoding="utf-8",
        )
        created.append(str(path.relative_to(config.ROOT)))
    # Taslak belgeler yoksa şablondan başlatılır; var olan taslağa dokunulmaz.
    for template_name, target_path in (
        ("proposal.md", config.PATHS["report_drafts"] / "proposal.md"),
        ("tybs-application.md", config.PATHS["report_tybs"] / "tybs-application.md"),
    ):
        template = config.PATHS["templates"] / template_name
        if template.exists() and not target_path.exists():
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
            created.append(str(target_path.relative_to(config.ROOT)))
    return created


def _interactive(base: dict) -> dict:
    print("project.json kurulumu — bilinmeyen değer için Enter (TBD).\n")
    for dotted, question in QUESTIONS:
        answer = input(f"{question}: ").strip()
        if not answer:
            is_name = dotted.endswith(".name") or dotted == "project.title"
            _set_in(base, dotted, "TBD" if is_name else None)
            continue
        if dotted in NUMERIC_FIELDS:
            try:
                _set_in(base, dotted, int(answer))
            except ValueError:
                print("  (sayı değil, metin olarak yazıldı)")
                _set_in(base, dotted, answer)
        else:
            _set_in(base, dotted, answer)
    kw = input("Anahtar kelimeler (virgülle, en az 3): ").strip()
    if kw:
        _set_in(base, "project.keywords", [p.strip() for p in kw.split(",") if p.strip()])
    members = input("Proje ortakları (virgülle, yoksa boş): ").strip()
    if members:
        _set_in(base, "team.members", [{"name": a.strip()} for a in members.split(",") if a.strip()])
    ai = input("ÜYZ araçları (virgülle, yoksa boş): ").strip()
    if ai:
        _set_in(base, "ai_tools", [a.strip() for a in ai.split(",") if a.strip()])
    print("Bütçe kalemleri (TL; Enter = 0):")
    items = base.get("budget", {}).get("items", {})
    for item in list(items.keys()):
        v = input(f"  {item}: ").strip()
        if v:
            try:
                items[item] = int(v)
            except ValueError:
                pass
    return base


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if config.help_requested(__doc__):
        return 0
    argv = sys.argv[1:]
    force = "--force" in argv
    defaults = "--defaults" in argv
    try:
        set_args = _collect_set_args(argv)
    except ConfigError as e:
        print(f"HATA: {e}", file=sys.stderr)
        return 2

    target = config.PATHS["project_config"]
    exists = target.exists()

    def _apply(base: dict) -> None:
        for dotted, raw, from_file in set_args:
            _set_in(base, dotted, _value_for(dotted, raw, from_file))

    # Yalnızca --set/--set-json: var olan dosyada (ya da örnekten) tek alan güncelle.
    if set_args and not defaults and not force:
        base = json.loads(target.read_text(encoding="utf-8")) if exists else _example()
        try:
            _apply(base)
        except ConfigError as e:
            print(f"HATA: {e}", file=sys.stderr)
            return 2
        _write(base)
        return _final_report(set_args)

    if exists and not force:
        print(f"{target.name} zaten var. Tümünü kurmak için --force, tek alan için --set kullanın.")
        return 1

    base = _example()
    base.pop("_note", None)
    if not defaults:
        base = _interactive(base)
    try:
        _apply(base)
    except ConfigError as e:
        print(f"HATA: {e}", file=sys.stderr)
        return 2
    _write(base)
    return _final_report(set_args)


def _final_report(set_args) -> int:
    created = _create_log_files()
    config.project.cache_clear()
    print(f"\nproject.json yazıldı: {config.PATHS['project_config']}")
    if set_args:
        print("Güncellenen alan(lar): " + ", ".join(dotted for dotted, _, _ in set_args))
    if created:
        print("Oluşturulan dosyalar: " + ", ".join(created))
    try:
        missing = config.missing_fields()
    except ConfigError as e:
        print(f"Eksik alanlar hesaplanamadı: {e}")
        return 1
    print("Eksik alanlar: " + (", ".join(missing) if missing else "yok"))
    try:
        type_problems = config.validate_types()
    except ConfigError as e:
        print(f"Tip denetimi yapılamadı: {e}")
        return 1
    if type_problems:
        print("Tip uyarıları:\n  - " + "\n  - ".join(type_problems))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
