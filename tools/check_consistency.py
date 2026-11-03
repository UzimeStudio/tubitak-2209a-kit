"""Belgeler arası tutarsızlık avcısı: project.json ↔ proposal md ↔ TYBS md.

Kontrol edilenler:
    - Başlık, ekip adları, süre (takvimdeki en büyük ay ↔ timeline.duration_months),
      bütçe toplamı ve kalemler, anahtar kelimeler project.json ile belgeler arasında.
    - İki md arasında aynı bölümdeki sayısal değerlerin (yüzde, eşik, örneklem, TL)
      farklılaşması.
    - Kalan yer tutucular (TBD, TODO, XXX, [KAYNAK, ???).
    - Başvuru aşamasında olmayan sonuç dili (geçmiş zaman bulgu ifadeleri; uyarı).
    - Metinde geçen ama tanımı olmayan hipotez/araştırma sorusu kimlikleri (H1, AS1).

Kullanım:
    uv run python tools/check_consistency.py [--json]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from check_application import read_md
from config import EMPTY, ConfigError, get, people, project

PLACEHOLDERS = ["TBD", "TODO", "XXX", "[KAYNAK", "???"]
RESULT_LANGUAGE = ["bulunmuştur", "gösterilmiştir", "tespit edilmiştir", "elde edilmiştir"]


def _read(path: Path) -> str:
    return read_md(path)


def _sections(md: str) -> dict[str, str]:
    """H1–H3 başlıklarını bölüm sözlüğüne ayırır (proposal karışık düzey kullanır)."""
    out, current = {}, None
    for line in md.splitlines():
        m = re.match(r"^#{1,3}\s+(.+?)\s*$", line)
        if m:
            current = m.group(1)
            out[current] = ""
        elif current:
            out[current] += line + "\n"
    return out


def _section_key(title: str) -> str:
    """'1.1 Konunun Önemi' → '1.1'; 'Özet' → 'özet'. Karşılaştırma için normalize."""
    m = re.match(r"^(\d+(?:\.\d+)?\.?)", title.strip())
    return m.group(1) if m else title.strip().lower()


def _numbers(text: str) -> set[str]:
    """Metindeki yüzde / eşik / örneklem / TL benzeri sayısal değerleri çıkarır."""
    found = set()
    for m in re.finditer(r"%\s*\d+(?:[.,]\d+)?", text):
        found.add(m.group(0).replace(" ", ""))
    for m in re.finditer(r"\d+(?:[.,]\d+)?\s*(?:TL|puan|site|sitede|kuruluş)", text):
        found.add(re.sub(r"\s+", " ", m.group(0)))
    for m in re.finditer(r"\b0[.,]\d+\b", text):  # eşik (kappa, F1, precision)
        found.add(m.group(0).replace(",", "."))
    return found


def _id_defined(text: str, ident: str) -> bool:
    """Kimliğin tanımı var mı?

    Tanım biçimleri: 'H1 (…):', 'H1:', '- H1:' satırı; ayrıca tablo hücresi
    başındaki kimlik ('| AS1: ... |', '| H1 | ...') de tanım sayılır.
    """
    i = re.escape(ident)
    return bool(
        re.search(rf"(?:^|\n)\s*[-*]?\s*{i}\s*[:(]", text)
        or re.search(rf"{i}\s*\([^)]*\)\s*:", text)
        # Tablo hücresi: '|' hemen ardından (boşluklarla) kimlik; sonrasında
        # ':' tanım ya da '|' ile bir sonraki hücre.
        or re.search(rf"\|\s*{i}\s*[:|]", text)
    )


def _max_month(md: str) -> int | None:
    secs = _sections(md)
    # TYBS'de takvim '3.1', proposal'da '5.1. Çalışma takvimi'. Numara anahtarına
    # bağlı kalmadan başlık adıyla da bul; böylece iki şablon da çalışır.
    cal = next((v for k, v in secs.items() if _section_key(k) in ("3.1", "3.1.")), None)
    if cal is None:
        cal = next((v for k, v in secs.items() if "çalışma takvimi" in k.lower()), None)
    if cal is None:
        return None
    months = []
    for row in cal.splitlines():
        if row.startswith("|") and not re.match(r"^\|\s*-", row):
            cells = [c.strip() for c in row.strip("|").split("|")]
            if cells and re.search(r"\d", cells[0]):
                months += [int(x) for x in re.findall(r"\d+", cells[0])]
    return max(months) if months else None


def check() -> dict:
    problems: list[str] = []
    warnings: list[str] = []

    try:
        p = project()
    except ConfigError as e:
        return {"problems": [f"project.json okunamadı: {e}"], "warnings": []}

    try:
        proposal_path = config.document("proposal")
    except ConfigError:
        proposal_path = Path()
    try:
        tybs_path = config.document("tybs")
    except ConfigError:
        tybs_path = Path()
    proposal = _read(proposal_path)
    tybs = _read(tybs_path)
    docs = [("proposal", proposal), ("TYBS", tybs)]

    # 1) başlık
    title = get(p, "project.title")
    if title and title not in EMPTY:
        for name, text in docs:
            if text and title not in text:
                warnings.append(f"project.json başlığı {name} metninde birebir geçmiyor: '{title[:60]}'")

    # 2) ekip adları
    for person in people():
        for name, text in docs:
            if text and person not in text:
                warnings.append(f"Ekip üyesi '{person}' {name} metninde geçmiyor")

    # 3) süre
    duration = get(p, "timeline.duration_months")
    for name, text in docs:
        if not text:
            continue
        mm = _max_month(text)
        if duration and mm and mm != duration:
            problems.append(
                f"Süre uyuşmazlığı: project.json duration_months={duration}, {name} en büyük ay={mm}"
            )

    # 4) bütçe toplamı ve kalemler
    total = get(p, "budget.total_tl")
    items = get(p, "budget.items", {}) or {}
    if isinstance(items, dict) and items and total is not None:
        items_total = sum(v for v in items.values() if isinstance(v, (int, float)))
        if items_total != total:
            problems.append(f"Bütçe: kalemler toplamı {items_total} TL ≠ total_tl {total} TL")

    # 5) anahtar kelimeler
    for kw in get(p, "project.keywords", []) or []:
        for name, text in docs:
            if text and kw and kw not in text:
                warnings.append(f"Anahtar kelime '{kw}' {name} metninde geçmiyor")

    # 6) iki md arası aynı bölümdeki sayısal farklar
    if proposal and tybs:
        pm = {_section_key(k): v for k, v in _sections(proposal).items()}
        tm = {_section_key(k): v for k, v in _sections(tybs).items()}
        for key in sorted(set(pm) & set(tm)):
            pf, tf = _numbers(pm[key]), _numbers(tm[key])
            only_p, only_t = pf - tf, tf - pf
            if only_p or only_t:
                warnings.append(
                    f"Bölüm {key}: sayısal değerler farklı "
                    f"(yalnız proposal: {sorted(only_p) or '-'}; yalnız TYBS: {sorted(only_t) or '-'})"
                )

    # 7) yer tutucular
    for name, text in docs:
        # Şablonun meşru '[[KAYNAKCA]]' yönergesi '[KAYNAK' desenini tetikler;
        # yanlış pozitifi önlemek için o yönergeyi sayımdan çıkar.
        scan = text.replace("[[KAYNAKCA]]", "")
        for ph in PLACEHOLDERS:
            if ph in scan:
                problems.append(f"Yer tutucu kaldı ({name}): {ph}")

    # 8) sonuç dili (uyarı)
    for name, text in docs:
        for phrase in RESULT_LANGUAGE:
            m = re.search(rf"[^.\n]*\b{re.escape(phrase)}\b[^.\n]*", text)
            if m:
                warnings.append(f"Sonuç dili ({name}): …{m.group(0).strip()[-70:]}")

    # 9) tanımsız H*/AS* kimlikleri
    for name, text in docs:
        seen = set()
        for m in re.finditer(r"\b((?:H|AS)\d+)\b", text):
            ident = m.group(1)
            if ident in seen:
                continue
            seen.add(ident)
            if not _id_defined(text, ident):
                problems.append(f"Tanımsız kimlik ({name}): {ident} geçiyor ama tanımı yok")

    problems = list(dict.fromkeys(problems))
    warnings = list(dict.fromkeys(warnings))
    return {"problems": problems, "warnings": warnings}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if config.help_requested(__doc__):
        return 0
    rep = check()
    if "--json" in sys.argv:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        if not rep["problems"] and not rep["warnings"]:
            print("Tutarsızlık bulunamadı.")
        for s in rep["problems"]:
            print(f"[SORUN]  {s}")
        for w in rep["warnings"]:
            print(f"[UYARI]  {w}")
    return 1 if rep["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
