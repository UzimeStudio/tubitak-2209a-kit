"""2209-A başvuru/öneri metnini hakemlerin sık şikayet ettiği yazım sorunları için denetler.

Desenler ve sözcük listeleri rules/writing-lint.json'dan okunur; koda hiçbir
desen sabit yazılmaz. Bütün bulgular UYARI düzeyindedir: metin bağlama göre yine
de doğru olabilir. Çıkış kodu yalnız --strict verildiğinde ve bulgu varsa 1 olur;
ayar/okuma hatasında 2.

Her bulgu bölüm + satır + kısa alıntı + öneri içerir. Kod blokları (```...```)
ve HTML yorumları (<!-- ... -->) sayımdan önce atılır; yanlış pozitif düşük
tutulur.

Kullanım:
    uv run python tools/check_writing.py [md] [--json] [--strict]

md verilmezse project.json documents.tybs (yoksa documents.proposal) kullanılır.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from check_application import find, plain, read_md, sections
from config import ConfigError, get, rules

WRITING_RULES_FILE = config.PATHS["rules_dir"] / "writing-lint.json"


def _load_writing_rules() -> dict:
    """rules/writing-lint.json içeriği. Yoksa/bozuksa ConfigError."""
    if not WRITING_RULES_FILE.exists():
        raise ConfigError(f"Dosya yok: {WRITING_RULES_FILE}")
    try:
        return json.loads(WRITING_RULES_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ConfigError(f"JSON bozuk: {WRITING_RULES_FILE} (satır {e.lineno}): {e.msg}") from e


# --- Kod bloğu ve HTML yorumlarını atma -------------------------------------

_FENCE = re.compile(r"```.*?```", re.DOTALL)
_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def strip_noise(md: str) -> str:
    """Kod bloklarını ve HTML yorumlarını SATIR SAYISINI koruyarak boşa çevirir.

    Satır numaralarının bozulmaması için her atılan parçanın içindeki satır
    sonları korunur; yalnız içerik boşaltılır. Böylece bulgulardaki satır
    numaraları özgün dosyayla eşleşir.
    """

    def _blank(m: re.Match) -> str:
        return "\n" * m.group(0).count("\n")

    md = _FENCE.sub(_blank, md)
    md = _COMMENT.sub(_blank, md)
    return md


def _line_index(md: str) -> list[int]:
    """Her karakter ofseti için 1 tabanlı satır numarası tablosunu kurar."""
    idx, line = [], 1
    for ch in md:
        idx.append(line)
        if ch == "\n":
            line += 1
    idx.append(line)
    return idx


def _section_of(line_no: int, section_lines: list[tuple[int, str]]) -> str:
    """Verilen satır numarasının ait olduğu bölüm başlığını döndürür."""
    current = "(başlıksız)"
    for start, title in section_lines:
        if start <= line_no:
            current = title
        else:
            break
    return current


def _quote(md: str, start: int, end: int, width: int = 60) -> str:
    """Eşleşme çevresinden kısa, tek satırlık bir alıntı çıkarır."""
    lo = md.rfind("\n", 0, start) + 1
    hi = md.find("\n", end)
    if hi == -1:
        hi = len(md)
    snippet = md[lo:hi].strip()
    snippet = re.sub(r"\s+", " ", snippet)
    if len(snippet) > width:
        rel = start - lo
        half = width // 2
        a = max(0, rel - half)
        snippet = ("…" if a > 0 else "") + snippet[a : a + width] + "…"
    return snippet


# --- Denetimler --------------------------------------------------------------


def _warn(section: str, line: int, quote: str, check_id: str, message: str, suggestion: str) -> dict:
    return {
        "id": check_id,
        "section": section,
        "line": line,
        "quote": quote,
        "message": message,
        "suggestion": suggestion,
    }


def _pattern_checks(md: str, secs: dict[str, str], wr: dict, section_lines, line_idx) -> list[dict]:
    """rules writing-lint.json patterns[] listesini uygular (bölüm filtreli)."""
    out: list[dict] = []
    for pat in wr.get("patterns", []):
        try:
            rx = re.compile(pat["pattern"], re.IGNORECASE)
        except re.error:
            continue
        secs_filter = pat.get("sections") or []
        for m in rx.finditer(md):
            ln = line_idx[m.start()] if m.start() < len(line_idx) else line_idx[-1]
            sec_title = _section_of(ln, section_lines)
            if secs_filter and not any(_title_has_prefix(sec_title, p) for p in secs_filter):
                continue
            out.append(
                _warn(sec_title, ln, _quote(md, m.start(), m.end()), pat["id"], pat["message"], pat["suggestion"])
            )
    return out


def _title_has_prefix(title: str, prefix: str) -> bool:
    """Bölüm başlığı önekle (ya da ad ile) eşleşiyor mu? find() ile aynı mantık."""
    t, n = title.lower().strip(), prefix.lower().strip()
    if t.startswith(n):
        return True
    stripped = re.sub(r"^\s*#*\s*\d+(?:\.\d+)*\.?\s*", "", title.lower()).strip()
    return stripped.startswith(n)


def _section_bounds(section_lines, md: str) -> dict[str, tuple[int, int]]:
    """Her bölüm başlığının (satır → sonraki başlığa kadar) satır aralığı."""
    total = md.count("\n") + 1
    out = {}
    for i, (start, title) in enumerate(section_lines):
        end = section_lines[i + 1][0] - 1 if i + 1 < len(section_lines) else total
        out[title] = (start, end)
    return out


def _abstract_scope(secs, wr, r, section_lines) -> list[dict]:
    """Özet'te rules abstract.scope kapsamlarının içerik ipucu bulunmayanları için uyarı."""
    out: list[dict] = []
    ab = find(secs, "Özet")
    if not ab:
        return out
    scope = get(r, "abstract.scope", []) or []
    hints = wr.get("abstract_scope_hints", {})
    text = plain(ab[1]).lower()
    ln = _title_line(section_lines, ab[0])
    for cat in scope:
        words = [w.lower() for w in hints.get(cat, [])]
        if words and not any(w in text for w in words):
            out.append(
                _warn(
                    ab[0],
                    ln,
                    f"Özet: '{cat}' kapsamı",
                    "ozet-kapsam",
                    f"Özette '{cat}' kapsamına dair içerik ipucu görülmedi.",
                    f"Özete '{cat}' kapsamını anlatan bir cümle ekleyin (rules abstract.scope).",
                )
            )
    return out


def _objectives_measurable(secs, wr, section_lines) -> list[dict]:
    """1.2'de hiç ölçülebilir öğe yoksa uyarı."""
    s = find(secs, "1.2")
    if not s:
        return []
    pat = wr.get("objectives_measurable", {}).get("pattern")
    if not pat:
        return []
    text = plain(s[1])
    if re.search(pat, text, re.IGNORECASE):
        return []
    return [
        _warn(
            s[0],
            _title_line(section_lines, s[0]),
            "1.2 bölümünde sayısal eşik yok",
            "olcusuz-amac",
            "Amaç/hedef bölümünde ölçülebilir bir öğe (sayı, ay, eşik, %) görülmedi.",
            "En az bir hedefe sayısal eşik koyun (ör. 'N≥450', '12 ay', 'F1 ≥0,80').",
        )
    ]


def _citation(secs, wr, section_lines) -> list[dict]:
    """1.1'de hiç atıf yoksa 'literatüre atıf yok' uyarısı."""
    s = find(secs, "1.1")
    if not s:
        return []
    pat = wr.get("citation", {}).get("pattern")
    if not pat:
        return []
    if re.search(pat, s[1]):
        return []
    return [
        _warn(
            s[0],
            _title_line(section_lines, s[0]),
            "1.1 bölümünde atıf bulunamadı",
            "atif-yok",
            "Konunun önemi bölümünde literatüre atıf (Soyad, 2020 / Soyad vd.) görülmedi.",
            "İddiaları güncel kaynaklarla destekleyin ve metin içi atıf verin.",
        )
    ]


def _long_sentences(secs, wr, section_lines) -> list[dict]:
    """Bölüm başına, max_words üzeri cümle sayısını raporlar."""
    max_words = get(wr, "long_sentence_words.max_words", 40)
    out: list[dict] = []
    for title, body in secs.items():
        # Tablo satırlarını (| ... |) ele: hücreler cümle değildir, yoksa uzun
        # bir tablo satırı yanlışlıkla 'uzun cümle' sayılır.
        prose = "\n".join(ln for ln in body.splitlines() if not ln.lstrip().startswith("|"))
        text = plain(prose)
        count = 0
        for sent in re.split(r"(?<=[.!?])\s+|\n{2,}", text):
            if len(sent.split()) > max_words:
                count += 1
        if count:
            out.append(
                _warn(
                    title,
                    _title_line(section_lines, title),
                    f"{count} cümle {max_words}+ kelime",
                    "uzun-cumle",
                    f"Bu bölümde {count} cümle {max_words} kelimeyi aşıyor; okunabilirliği düşürür.",
                    "Uzun cümleleri bölün; her cümle tek bir fikir taşısın.",
                )
            )
    return out


# --- 3.1 başarı ölçütü: katkı yüzdesi dışında ölçü var mı? -------------------


def _work_plan_metrics(secs, wr, r, section_lines) -> list[dict]:
    """3.1 tablosunda başarı ölçütü hücresinde katkı yüzdesi dışında ölçü yoksa uyarı.

    Sütunu check_application'ın 'katkı' sütununu bulma yoluyla bulur. TYBS'de
    başarı ölçütü ve katkı aynı hücrede olabilir: son '%N' katkı payıdır,
    ondan önceki metin başarı ölçütüdür. Kalan metinde sayısal/eşik öğe yoksa
    'ölçülemeyen başarı ölçütü' uyarısı verilir.
    """
    out: list[dict] = []
    section = get(r, "work_plan.section", "3.1")
    cal = find(secs, section) or find(secs, "Çalışma takvimi")
    if not cal:
        return out
    pat = wr.get("success_metric_number", {}).get("pattern")
    if not pat:
        return out
    rows = [row for row in cal[1].splitlines() if row.lstrip().startswith("|") and not re.match(r"^\s*\|\s*-", row)]
    if len(rows) < 2:
        return out
    header = [c.strip().lower() for c in rows[0].strip().strip("|").split("|")]

    def col(*keys):
        return next((i for i, h in enumerate(header) if any(k in h for k in keys)), None)

    # 'başarı ölçütü ... katkısı' hücresi check_application'da 'katkı' ile bulunur.
    c_metric = col("başarı ölçütü", "katkı", "ölçüt")
    if c_metric is None:
        return out
    base_line = _title_line(section_lines, cal[0])
    for ri, row in enumerate(rows[1:], start=1):
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if c_metric >= len(cells):
            continue
        cell = cells[c_metric]
        # Son '%N' katkı payıdır; başarı ölçütü metni için onu çıkar.
        metric_text = re.sub(r"%\s*\d+[.,]?\d*\s*$", "", cell).strip(" —-–")
        metric_text = re.sub(r"[—–-]\s*$", "", metric_text).strip()
        if not metric_text:
            metric_text = cell
        if not re.search(pat, metric_text, re.IGNORECASE):
            out.append(
                _warn(
                    cal[0],
                    base_line,
                    _shorten(cell),
                    "olcusuz-basari",
                    "Başarı ölçütü hücresinde katkı yüzdesi dışında ölçülebilir öğe yok.",
                    "Ölçüte sayısal eşik ekleyin (ör. 'doğruluk ≥%90', 'N≥450 ölçüm', 'kappa ≥0,70').",
                )
            )
    return out


def _shorten(text: str, width: int = 60) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= width else text[: width - 1] + "…"


def _title_line(section_lines, title: str) -> int:
    for start, t in section_lines:
        if t == title:
            return start
    return 1


def _section_line_map(md: str) -> list[tuple[int, str]]:
    """(satır_no, başlık) listesi — H1–H3 başlıkları, dosya sırasıyla."""
    out = []
    for i, line in enumerate(md.splitlines(), start=1):
        m = re.match(r"^#{1,3}\s+(.+?)\s*$", line)
        if m:
            out.append((i, m.group(1)))
    return out


def check(path: Path) -> dict:
    """Verilen markdown dosyasını denetler; UYARI listesi döndürür."""
    r = rules()
    wr = _load_writing_rules()
    raw = read_md(path)
    if not raw:
        return {"file": str(path), "warnings": [], "note": "dosya bulunamadı veya boş"}
    md = strip_noise(raw)
    secs = sections(md)
    section_lines = _section_line_map(md)
    line_idx = _line_index(md)

    warnings: list[dict] = []
    warnings += _pattern_checks(md, secs, wr, section_lines, line_idx)
    warnings += _work_plan_metrics(secs, wr, r, section_lines)
    warnings += _objectives_measurable(secs, wr, section_lines)
    warnings += _citation(secs, wr, section_lines)
    warnings += _long_sentences(secs, wr, section_lines)
    warnings += _abstract_scope(secs, wr, r, section_lines)

    warnings.sort(key=lambda w: (w["line"], w["id"]))
    return {"file": str(path), "warnings": warnings}


def _resolve_path(args: list[str]) -> Path:
    if args:
        return Path(args[0])
    try:
        return config.document("tybs")
    except ConfigError:
        return config.document("proposal")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if config.help_requested(__doc__):
        return 0
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    strict = "--strict" in sys.argv
    try:
        path = _resolve_path(args)
        rep = check(path)
    except ConfigError as e:
        print(f"HATA: {e}")
        return 2
    if "--json" in sys.argv:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print(f"Dosya: {rep['file']}")
        if rep.get("note"):
            print(f"  {rep['note']}")
        for w in rep["warnings"]:
            print(f"  [UYARI] {w['section']} (satır {w['line']}): {w['message']}")
            print(f"          alıntı: {w['quote']}")
            print(f"          öneri : {w['suggestion']}")
        print(f"Toplam uyarı: {len(rep['warnings'])}")
    if strict and rep["warnings"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
