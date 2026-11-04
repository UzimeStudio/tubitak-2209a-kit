"""2209-A başvuru taslağını çağrı kurallarına göre denetler (konu bağımsız).

KAYNAK tools/check_application.py'nin jenerik hâli: hiçbir sınır, marka veya
desen koda sabit yazılmaz; hepsi rules/<çağrı>.json ve project.json'dan okunur.

Kullanım:
    uv run python tools/check_application.py [md] [--tybs] [--json]

md verilmezse project.json documents.tybs (yoksa documents.proposal) kullanılır.
TYBS'deki sayım yöntemi bilinmediğinden sınıra yakın değerler (%5) "elle kontrol
et" olarak işaretlenir; sınırlı doğrulanabilirlik için uyarı düzeyinde kalır.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from config import ConfigError, get, project, rules

# TYBS'ye yapıştırılamayacak göreli markdown bağlantısı her zaman aranır;
# project.json checks.internal_id_patterns yalnız projeye özgü kimlikleri ekler.
RELATIVE_LINK = r"\]\((?!https?:)[^)]+\)"


def read_md(path: Path) -> str:
    """Markdown dosyasını BOM ve satır sonu farklarından arındırarak okur.

    BOM'lu UTF-8 (``\\ufeff## ...``) dosyalarda başlık regex'leri ilk başlığı
    kaçırıyordu; ``utf-8-sig`` BOM'u yutar. CRLF (``\\r\\n``) satır sonları de LF'e
    çevrilir, böylece ``plain()`` çıktısında ``\\r`` kalmaz ve tüm araçlar aynı
    normalleştirilmiş metni görür. Diğer araçlar da (check_consistency, check_report,
    md2docx) bu yardımcıyı kullanır.
    """
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")


def plain(md: str) -> str:
    """Markdown biçimlendirmesini (bağlantı, kalın, tablo çizgisi) sayımdan önce temizler."""
    md = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)
    md = re.sub(r"^>\s*\[!\w+\]\s*$", "", md, flags=re.MULTILINE)
    md = re.sub(r"^\s*>\s?", "", md, flags=re.MULTILINE)
    md = re.sub(r"[*_`#]", "", md)
    md = re.sub(r"^\s*\|?\s*-{3,}.*$", "", md, flags=re.MULTILINE)
    md = md.replace("|", " ")
    return re.sub(r"[ \t]+", " ", md).strip()


def sections(md: str) -> dict[str, str]:
    """H1–H3 (``#``, ``##``, ``###``) başlıklarını bölüm sözlüğüne ayırır.

    proposal.md ``# Özet``/``## 1.1.`` gibi karışık düzeyler, TYBS ise yalnız
    ``##`` kullanır; her iki şablon da çalışsın diye tüm düzeyler tanınır.
    """
    out, current = {}, None
    for line in md.splitlines():
        m = re.match(r"^#{1,3}\s+(.+?)\s*$", line)
        if m:
            current = m.group(1)
            out[current] = ""
        elif current:
            out[current] += line + "\n"
    return out


def _title_matches(title: str, needle: str) -> bool:
    """Bölüm başlığı, verilen önek ya da başlık adıyla eşleşiyor mu?

    Önek eşleşmesi ('1.1' → '1.1. Konu...') eski davranış; ayrıca numarayı
    atlayıp başlık adıyla da eşleştirir ('Çalışma takvimi' → '5.1. Çalışma
    takvimi (iş paketleri)') — böylece proposal ve TYBS farklı numaralar
    kullansa da aynı bölüm bulunur.
    """
    t, n = title.lower().strip(), needle.lower().strip()
    if t.startswith(n):
        return True
    # Başlıktan öndeki numara/noktalama ('5.1. ', '1.1 ') atılıp ada bakılır.
    stripped = re.sub(r"^\s*#*\s*\d+(?:\.\d+)*\.?\s*", "", title.lower()).strip()
    return stripped.startswith(n)


def find(secs: dict[str, str], prefix: str) -> tuple[str, str] | None:
    for k, v in secs.items():
        if _title_matches(k, prefix):
            return k, v
    return None


def _near(value: float, limit: float, ratio: float = 0.05) -> bool:
    """value sınıra %ratio kadar yakın mı (iki yönlü)?"""
    if limit == 0:
        return value == 0
    return abs(value - limit) <= abs(limit) * ratio


def _institution_aliases() -> dict[str, str]:
    """project.json checks.institution_aliases: {metindeki_ad: kaynakça_anahtarı}."""
    try:
        raw = get(project(), "checks.institution_aliases", {}) or {}
    except ConfigError:
        return {}
    return {str(k).lower(): str(v).lower() for k, v in raw.items()}


def _brands(r: dict) -> list[str]:
    default = get(r, "brand_ban.default_brands", []) or []
    try:
        extra = get(project(), "checks.extra_brands", []) or []
    except ConfigError:
        extra = []
    return list(dict.fromkeys([*default, *extra]))


def _internal_id_patterns() -> list[str]:
    try:
        patterns = get(project(), "checks.internal_id_patterns", []) or []
    except ConfigError:
        patterns = []
    return [*patterns, RELATIVE_LINK]


def tybs_checks(md: str, secs: dict[str, str], r: dict) -> list[str]:
    """TYBS'ye girecek bölümlerde marka, iç kimlik/bağlantı ve atıf–kaynakça eşleşmesi."""
    problems: list[str] = []
    tybs_sections = tuple(r.get("tybs_sections", []))
    body = "\n".join(v for k, v in secs.items() if k.startswith(tybs_sections))

    for b in _brands(r):
        # \b sembolle biten markayı (C++, C#) kaçırıyordu; lookaround sözcük
        # karakteri komşuluğunu dışlar ama marka sonundaki sembole bakmaz.
        if re.search(rf"(?<!\w){re.escape(b)}(?!\w)", body):
            problems.append(f"Marka/ürün adı (marka yasağı): {b}")
    for pat in _internal_id_patterns():
        for m in re.finditer(pat, body):
            problems.append(f"İç kimlik/bağlantı TYBS metninde: {m.group(0)}")

    refs = find(secs, "Kaynakça")
    if not refs:
        return problems + ["Kaynakça bölümü yok"]
    entries = re.findall(r"^\d+\.\s+(.+)$", refs[1], flags=re.MULTILINE)

    keys = set()
    for e in entries:
        y = re.search(r"\.\s(\d{4}|t\.y)\.(?:\s|$)", e) or re.search(r"\((\d{4}|t\.y\.)", e)
        first = re.split(r"[,.(]", e)[0].strip()
        year = y.group(1) if y else ""
        parts = first.split()
        keys.add((parts[0].lower() if parts else "", "t.y." if year == "t.y" else year))

    not_authors = {
        "ocak",
        "şubat",
        "mart",
        "nisan",
        "mayıs",
        "haziran",
        "temmuz",
        "ağustos",
        "eylül",
        "ekim",
        "kasım",
        "aralık",
        "kanun",
        "kanunun",
        "tebliği",
    }
    cited = set()
    # Türkçe iyelik/hal eki: "Yılmaz'ın (2020)", "Cohen'e (1960)", "Landis ve Koch'un (1977)",
    # "Smith vd.'nin (2020)". Ek ilk yazarda, ikinci yazarda veya "vd." sonrasında olabilir;
    # kesme işareti (' veya ') ve sonrası atılır, yalnız ilk soyad (group 1) anahtara girer.
    suffix = r"(?:['’][a-zçğıöşü]+)?"
    # Önce çok sözcüklü kurum/belge adıyla parantez içi atıflar: "(Dünya Sağlık Örgütü, 2018)",
    # "(Türkiye İstatistik Kurumu, 2024; Soyad, 2020)". Anahtar ilk sözcüktür; adın kalan
    # sözcükleri (ör. "Kurumu, 2024") aşağıdaki tek sözcüklü desene ayrıca yakalatılmaz.
    covered: list[tuple[int, int]] = []
    multi = re.compile(
        r"\s*([A-ZÇĞİÖŞÜ][\wçğıöşü]+)(?:\s+[A-ZÇĞİÖŞÜa-zçğıöşü][\wçğıöşü]*){1,3},\s*((?:19|20)\d{2}|t\.y\.)"
    )
    for group in re.finditer(r"\(([^()]*?(?:(?:19|20)\d{2}|t\.y\.)[^()]*)\)", body):
        offset = group.start(1)
        for part in group.group(1).split(";"):
            pm = multi.match(part)
            if pm and pm.group(1).lower() not in not_authors:
                cited.add((pm.group(1).lower(), pm.group(2)))
                covered.append((offset + pm.start(1), offset + pm.end()))
            offset += len(part) + 1
    for m in re.finditer(
        rf"([A-ZÇĞİÖŞÜ][\wçğıöşü]+){suffix}(?: vd\.{suffix}| ve [A-ZÇĞİÖŞÜ]\w+{suffix})?,? \(?((?:19|20)\d{{2}}|t\.y\.)\)?",
        body,
    ):
        if any(a <= m.start() < b for a, b in covered):
            continue
        if m.group(1).lower() not in not_authors:
            cited.add((m.group(1).lower(), m.group(2)))
    for m in re.finditer(r"(\d{4}) sayılı Kanun(?:un)? \((\d{4})\)", body):
        cited.add((m.group(1), m.group(2)))

    aliases = _institution_aliases()
    norm_keys = {(aliases.get(k, k), y) for k, y in keys}
    for k, y in sorted(cited):
        if (aliases.get(k, k), y) not in norm_keys:
            problems.append(f"Metindeki atıf kaynakçada yok: {k} ({y})")
    used = {(aliases.get(k, k), y) for k, y in cited}
    for k, y in sorted(norm_keys - used):
        problems.append(f"Kaynakçada var, metinde atıf yok: {k} ({y})")

    problems += _doi_check(entries, r)
    return problems


def _doi_check(entries: list[str], r: dict) -> list[str]:
    """DOI kuralını bibkit modülünden okur. Modül veya kayıt yoksa atla + uyar."""
    if not get(r, "references.doi_required", False):
        return []
    try:
        import bibkit
    except ImportError:
        return ["UYARI: bibkit modülü bulunamadı; DOI kontrolü atlandı"]
    try:
        records = bibkit.load()
    except Exception as e:  # noqa: BLE001
        return [f"UYARI: bibkit.load() başarısız ({e}); DOI kontrolü atlandı"]
    if not records:
        return ["UYARI: kaynakça kaydı boş; DOI kontrolü atlandı"]
    problems = []
    for rec in records:
        if not rec.get("doi"):
            continue
        line = bibkit.format_entry(rec)
        head = line.split(f"({rec['year']}")[0]
        matched = any(e.startswith(head) and f"({rec['year']}" in e for e in entries)
        if matched and not any(rec["doi"].lower() in e.lower() for e in entries):
            problems.append(f"DOI'li kaynakta DOI yok: {rec['id']} ({rec['doi']})")
    return problems


def _external_source_registry_check(r: dict) -> list[str]:
    """Eski docs/kaynaklar.md tarzı dış kaynak kaydı; yalnız project.json'da doluysa."""
    try:
        rel = get(project(), "documents.external_source_registry")
    except ConfigError:
        return []
    if not rel:
        return []
    path = (config.ROOT / rel).resolve()
    if not path.exists():
        return [f"UYARI: dış kaynak kaydı bulunamadı: {rel}"]
    try:
        import bibkit

        records = bibkit.load()
    except Exception:  # noqa: BLE001
        return []
    reg = path.read_text(encoding="utf-8").lower()
    problems = []
    for rec in records:
        if rec.get("doi") and rec["doi"].lower() not in reg:
            problems.append(f"DOI dış kaynak kaydında yok: {rec['id']} → {rec['doi']} ({rel})")
    return problems


def check(path: Path, tybs: bool = False) -> dict:
    r = rules()
    md = read_md(path)
    secs = sections(md)
    results: list[dict] = []
    problems: list[str] = []
    manual: list[str] = []

    ab_min = get(r, "abstract.min_words", 25)
    ab_max = get(r, "abstract.max_words", 450)
    ab = find(secs, "Özet")
    if ab:
        words = len(plain(ab[1]).split())
        ok = ab_min <= words <= ab_max
        results.append({"rule": f"Özet {ab_min}–{ab_max} kelime", "value": words, "ok": ok})
        if ok and (_near(words, ab_min) or _near(words, ab_max)):
            manual.append(f"Özet kelime sayısı ({words}) sınıra yakın — elle kontrol et")
    else:
        problems.append("Özet bölümü bulunamadı")

    sec_min = get(r, "section_min_chars.min_chars", 350)
    for prefix in get(r, "section_min_chars.sections", ["1.1", "1.2", "2."]):
        s = find(secs, prefix)
        if not s:
            problems.append(f"{prefix} bölümü bulunamadı")
            continue
        chars = len(plain(s[1]))
        ok = chars >= sec_min
        results.append({"rule": f"{s[0]} ≥{sec_min} karakter", "value": chars, "ok": ok})
        if ok and _near(chars, sec_min):
            manual.append(f"{s[0]} karakter sayısı ({chars}) sınıra yakın — elle kontrol et")

    _work_plan(r, secs, results, problems, manual)
    _title_keywords(r, secs, results)
    _references_size(r, secs, results, manual)
    _budget(r, results, problems, manual)

    raw = _external_source_registry_check(r)
    if tybs:
        raw += tybs_checks(md, secs, r)
    # 'UYARI:' ile başlayanlar atlanan kontrollerin bilgilendirmesidir; sorun değil,
    # elle kontrol listesine gider ve çıkış kodunu etkilemez.
    for item in raw:
        (manual if item.startswith("UYARI:") else problems).append(item)

    for res in results:
        if not res["ok"]:
            problems.append(f"Kural sağlanmadı: {res['rule']} (değer {res['value']})")
    return {"file": str(path), "results": results, "problems": problems, "manual_review": manual}


def _work_plan(r, secs, results, problems, manual):
    wp = get(r, "work_plan", {})
    section = wp.get("section", "3.1")
    # Önce çağrı numarasıyla (TYBS'de '3.1'), bulunamazsa başlık adıyla ara
    # (proposal'da '5.1. Çalışma takvimi'); her iki şablon da çalışsın.
    cal = find(secs, section) or find(secs, "Çalışma takvimi")
    if not cal:
        problems.append(f"{section} Çalışma Takvimi bulunamadı")
        return
    rows = [row for row in cal[1].splitlines() if row.startswith("|") and not re.match(r"^\|\s*-", row)]
    header = [c.strip().lower() for c in rows[0].strip("|").split("|")] if rows else []
    col = lambda *keys: next((i for i, h in enumerate(header) if any(key in h for key in keys)), None)
    c_pct, c_month, c_step = col("katkı"), col("ay"), col("iş paketi", "faaliyet")
    forbidden = [s.lower() for s in wp.get("forbidden_steps", [])]
    total, max_month = 0, 0
    for row in rows[1:]:
        cells = [c.strip() for c in row.strip("|").split("|")]
        pcts = re.findall(r"%\s*(\d+)", cells[c_pct]) if c_pct is not None and c_pct < len(cells) else []
        total += int(pcts[-1]) if pcts else 0
        months = (
            [int(x) for x in re.findall(r"\d+", cells[c_month])]
            if c_month is not None and c_month < len(cells)
            else []
        )
        max_month = max([max_month, *months])
        step = cells[c_step].lower() if c_step is not None and c_step < len(cells) else ""
        for bad in forbidden:
            if bad in step:
                problems.append(f"Ayrı iş adımı olmamalı: {step}")
    target = wp.get("contribution_total", 100)
    max_months = get(r, "duration.max_months", 12)
    results.append({"rule": f"Katkı toplamı {target}", "value": total, "ok": total == target})
    results.append(
        {"rule": f"Takvim ≤{max_months} ay", "value": max_month, "ok": 0 < max_month <= max_months}
    )
    if 0 < max_month and _near(max_month, max_months):
        manual.append(f"En büyük ay ({max_month}) üst sınıra yakın — elle kontrol et")


def _title_keywords(r, secs, results):
    title = find(secs, "Başlık")
    title_max = get(r, "title.max_chars")
    if title and title_max:
        text = plain(title[1])
        n = len(text)
        ok = n <= title_max
        results.append({"rule": f"Başlık ≤{title_max} karakter", "value": n, "ok": ok})

    kw = find(secs, "Anahtar")
    kw_min = get(r, "keywords.min")
    kw_max = get(r, "keywords.max")
    sep = get(r, "keywords.separator", ",")
    if kw and kw_min and kw_max:
        line = next((s.strip() for s in plain(kw[1]).splitlines() if s.strip()), "")
        words = [p.strip() for p in line.split(sep) if p.strip()]
        n = len(words)
        ok = kw_min <= n <= kw_max
        results.append({"rule": f"Anahtar kelime {kw_min}–{kw_max}", "value": n, "ok": ok})


def _references_size(r, secs, results, manual):
    maxc = get(r, "references.max_chars")
    refs = find(secs, "Kaynakça")
    if refs and maxc:
        n = len(refs[1].strip())
        ok = n <= maxc
        results.append({"rule": f"Kaynakça ≤{maxc} karakter", "value": n, "ok": ok})
        if ok and _near(n, maxc):
            manual.append(f"Kaynakça karakter sayısı ({n}) üst sınıra yakın — elle kontrol et")


def _budget(r, results, problems, manual):
    maxtl = get(r, "budget.max_tl")
    if not maxtl:
        return
    try:
        total = get(project(), "budget.total_tl")
        items = get(project(), "budget.items", {}) or {}
    except ConfigError:
        return
    if total is not None:
        ok = total <= maxtl
        results.append({"rule": f"Bütçe ≤{maxtl} TL", "value": total, "ok": ok})
        if ok and _near(total, maxtl):
            manual.append(f"Bütçe ({total} TL) üst sınıra yakın — elle kontrol et")
        if isinstance(items, dict) and items:
            items_total = sum(v for v in items.values() if isinstance(v, (int, float)))
            if items_total != total:
                problems.append(
                    f"Bütçe kalemleri toplamı ({items_total} TL) total_tl ({total} TL) ile uyuşmuyor"
                )


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if config.help_requested(__doc__):
        return 0
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    tybs = "--tybs" in sys.argv
    try:
        if args:
            path = Path(args[0])
        else:
            try:
                path = config.document("tybs")
                tybs = True
            except ConfigError:
                path = config.document("proposal")
        rep = check(path, tybs=tybs)
    except ConfigError as e:
        print(f"HATA: {e}")
        return 2
    if "--json" in sys.argv:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print(f"Dosya: {rep['file']}")
        for res in rep["results"]:
            mark = "OK" if res["ok"] else "HATA"
            print(f"  [{mark}] {res['rule']}: {res['value']}")
        for m in rep["manual_review"]:
            print(f"  [ELLE] {m}")
        for p in rep["problems"]:
            print(f"  [SORUN] {p}")
    return 1 if rep["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
