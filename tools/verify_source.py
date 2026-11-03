"""Akademik kaynağı bağımsız bibliyografik kayıtlarla doğrular.

Kullanım:
    uv run python tools/verify_source.py --doi 10.1177/001316446002000104
    uv run python tools/verify_source.py --title "..." --year 2020 --author Soyad

Çıktı: stdout'a JSON. --save verilirse PATHS["verification"]/<id>.json dosyasına da yazar.
Ham API yanıtları PATHS["cache"] altında saklanır (yeniden üretilebilirlik).

Ağ erişimi: yalnız herkese açık künye servislerine, yalnız başlık/DOI gönderilerek.
    Crossref, OpenAlex, (isteğe bağlı) Semantic Scholar ve doi.org resolver.
Hiçbir proje verisi, kişi bilgisi veya tam metin dışarı gönderilmez.

Durumlar:
    VERIFIED   En az iki bağımsız kayıt başlık, yıl ve ilk yazar soyadında uyuşuyor.
    PARTIAL    Yalnız bir kayıt bulundu veya bir alan eksik; insan kontrolü gerekir.
    CONFLICT   Kayıtlar birbiriyle veya verilen künyeyle çelişiyor.
    NOT_FOUND  Hiçbir kayıtta bulunamadı. Bu, kaynağın sahte olduğunu kanıtlamaz.

Ortam değişkenleri (isteğe bağlı, kaynak koduna yazılmaz):
    CROSSREF_MAILTO   Crossref "polite pool" için iletişim adresi.
    OPENALEX_API_KEY  OpenAlex anahtarı.
    S2_API_KEY        Semantic Scholar anahtarı.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import PATHS

UA = "tubitak-2209a-kit/0.1 (academic source verification)"
TITLE_MATCH = 0.90


# Türkçe harfler NFKD ile yanlış ayrışır (ı->'', ş->s+birleşik imge): önce ASCII'ye
# eşle, sonra NFKD uygula. Böylece 'çalışması' -> 'calismasi' olur ('cal smas' değil).
_TR_MAP = str.maketrans({"ı": "i", "İ": "I", "ş": "s", "Ş": "S", "ğ": "g", "Ğ": "G",
                         "ç": "c", "Ç": "C", "ö": "o", "Ö": "O", "ü": "u", "Ü": "U"})


def _norm(text: str | None) -> str:
    if not text:
        return ""
    text = text.translate(_TR_MAP)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _author_matches(author: str | None, record_authors: list) -> bool:
    """Yazar soyadı, kayıttaki yazar adlarından biriyle TAM TOKEN olarak eşleşmeli.

    Alt dizgi eşleşmesi yanlış pozitif üretir ('And' -> 'Andrew' doğru sayılırdı);
    bu yüzden normalize edilmiş token kümesinde tam eşleşme aranır.
    """
    if not author:
        return True
    needle = _norm(author)
    if not needle:
        return True
    needle_tokens = needle.split()
    for name in record_authors:
        name_tokens = _norm(name or "").split()
        # Soyad tek token ise tam token eşleşmesi; çok tokenli ise alt dizi olarak aranır.
        if len(needle_tokens) == 1:
            if needle_tokens[0] in name_tokens:
                return True
        elif needle_tokens and _is_subsequence(needle_tokens, name_tokens):
            return True
    return False


def _is_subsequence(needle: list[str], tokens: list[str]) -> bool:
    """needle token dizisi, tokens içinde ardışık olarak geçiyor mu (tam token eşleşmesi)."""
    n = len(needle)
    if n == 0 or n > len(tokens):
        return False
    for i in range(len(tokens) - n + 1):
        if tokens[i : i + n] == needle:
            return True
    return False


def similarity(a: str | None, b: str | None) -> float:
    na, nb = _norm(a), _norm(b)
    # Alt başlıklı uzun başlıklarda kısaltılmış sorgu tam başlığın içinde geçebilir.
    short, long_ = sorted((na, nb), key=len)
    if len(short) >= 30 and short in long_:
        return 0.95
    return difflib.SequenceMatcher(None, na, nb).ratio()


def _get(url: str, headers: dict[str, str] | None = None, retries: int = 3) -> dict | None:
    """Künye servisinden JSON çeker; yanıtı önbelleğe yazar. Yollar çağrı anında okunur."""
    cache = PATHS["cache"]
    cache.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(url.encode()).hexdigest()[:24]
    cached = cache / f"{key}.json"
    if cached.exists():
        return json.loads(cached.read_text(encoding="utf-8"))["body"]
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            cached.write_text(
                json.dumps(
                    {"url": url, "fetched_utc": datetime.now(UTC).isoformat(), "body": body},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            return body
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            if exc.code == 429 and attempt < retries - 1:
                time.sleep(3 * (attempt + 1))
                continue
            print(f"[uyarı] {url} -> HTTP {exc.code}", file=sys.stderr)
            return None
        except (urllib.error.URLError, TimeoutError) as exc:
            print(f"[uyarı] {url} -> {exc}", file=sys.stderr)
            return None
    return None


def _record(source: str, title, year, authors, venue, doi, url) -> dict:
    return {
        "source": source,
        "title": title,
        "year": year,
        "authors": authors,
        "venue": venue,
        "doi": (doi or "").lower().removeprefix("https://doi.org/") or None,
        "url": url,
    }


def crossref(doi: str | None, title: str | None) -> list[dict]:
    mailto = os.environ.get("CROSSREF_MAILTO")
    suffix = f"?mailto={urllib.parse.quote(mailto)}" if mailto else ""
    if doi:
        data = _get(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}{suffix}")
        items = [data["message"]] if data else []
    else:
        q = urllib.parse.urlencode(
            {"query.bibliographic": title, "rows": 5, **({"mailto": mailto} if mailto else {})}
        )
        data = _get(f"https://api.crossref.org/works?{q}")
        items = data["message"]["items"] if data else []
    out = []
    for it in items:
        year = None
        for k in ("published-print", "published-online", "issued", "created"):
            parts = it.get(k, {}).get("date-parts", [[None]])
            if parts and parts[0] and parts[0][0]:
                year = parts[0][0]
                break
        authors = [a.get("family") or a.get("name") for a in it.get("author", [])]
        out.append(
            _record(
                "crossref",
                (it.get("title") or [None])[0],
                year,
                authors,
                (it.get("container-title") or [None])[0],
                it.get("DOI"),
                it.get("URL"),
            )
        )
    return out


def openalex(doi: str | None, title: str | None) -> list[dict]:
    key = os.environ.get("OPENALEX_API_KEY")
    extra = f"api_key={urllib.parse.quote(key)}" if key else ""
    if doi:
        data = _get(
            f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}" + (f"?{extra}" if extra else "")
        )
        items = [data] if data else []
    else:
        q = urllib.parse.urlencode({"search": title, "per-page": 5})
        data = _get(f"https://api.openalex.org/works?{q}" + (f"&{extra}" if extra else ""))
        items = data.get("results", []) if data else []
    out = []
    for it in items:
        authors = [
            (a.get("author") or {}).get("display_name", "").split(" ")[-1] for a in it.get("authorships", [])
        ]
        venue = ((it.get("primary_location") or {}).get("source") or {}).get("display_name")
        out.append(
            _record(
                "openalex",
                it.get("title"),
                it.get("publication_year"),
                authors,
                venue,
                it.get("doi"),
                it.get("id"),
            )
        )
    return out


def semantic_scholar(doi: str | None, title: str | None) -> list[dict]:
    key = os.environ.get("S2_API_KEY")
    headers = {"x-api-key": key} if key else None
    fields = "title,year,authors,venue,externalIds,url"
    if doi:
        data = _get(
            f"https://api.semanticscholar.org/graph/v1/paper/DOI:{urllib.parse.quote(doi)}?fields={fields}",
            headers,
        )
        items = [data] if data else []
    else:
        q = urllib.parse.urlencode({"query": title, "limit": 5, "fields": fields})
        data = _get(f"https://api.semanticscholar.org/graph/v1/paper/search?{q}", headers)
        items = data.get("data", []) if data else []
    out = []
    for it in items:
        authors = [(a.get("name") or "").split(" ")[-1] for a in it.get("authors", [])]
        doi_found = (it.get("externalIds") or {}).get("DOI")
        out.append(
            _record(
                "semanticscholar",
                it.get("title"),
                it.get("year"),
                authors,
                it.get("venue"),
                doi_found,
                it.get("url"),
            )
        )
    return out


def doi_resolves(doi: str) -> bool | None:
    """doi.org handle kaydını sorgular. Veri tabanındaki DOI alanı tek başına yeterli değildir."""
    data = _get(f"https://doi.org/api/handles/{urllib.parse.quote(doi)}")
    if data is None:
        return False
    return data.get("responseCode") == 1


def _fits(rec: dict, year: int | None, author: str | None) -> bool:
    if year and rec["year"] and abs(int(rec["year"]) - year) > 1:
        return False
    return not (author and rec["authors"] and not _author_matches(author, rec["authors"]))


def _best(
    records: list[dict], title: str | None, year: int | None, author: str | None, rejected: list[str]
) -> dict | None:
    if not records:
        return None
    if not title:
        return records[0]
    close = [r for r in records if similarity(r["title"], title) >= TITLE_MATCH]
    fitting = [r for r in close if _fits(r, year, author)]
    for r in close:
        if r not in fitting:
            rejected.append(f"{r['source']}: benzer başlıklı farklı kayıt elendi ({r['year']}, {r['title']})")
    if not fitting:
        return None
    return max(fitting, key=lambda r: similarity(r["title"], title))


def verify(doi: str | None, title: str | None, year: int | None, author: str | None, use_s2: bool) -> dict:
    """Künyeyi (yalnız başlık/DOI/yıl/yazar) servislerle karşılaştırır, durum döndürür."""
    doi = doi.lower().removeprefix("https://doi.org/") if doi else None
    providers = [crossref, openalex] + ([semantic_scholar] if use_s2 else [])
    found: list[dict] = []
    rejected: list[str] = []
    for prov in providers:
        # DOI sorgusunda kayıt elenmez; çelişki aşağıda raporlanır.
        rec = _best(prov(doi, title), None if doi else title, year, author, rejected)
        if rec:
            found.append(rec)
    issues: list[str] = []
    ref_title = title or (found[0]["title"] if found else None)
    agreeing = []
    for rec in found:
        ok = similarity(rec["title"], ref_title) >= TITLE_MATCH
        if year and rec["year"] and abs(int(rec["year"]) - year) > 1:
            issues.append(f"{rec['source']}: yıl {rec['year']} ≠ {year}")
            ok = False
        if author and rec["authors"] and not _author_matches(author, rec["authors"]):
            issues.append(f"{rec['source']}: '{author}' yazar listesinde yok")
            ok = False
        if doi and rec["doi"] and rec["doi"] != doi:
            issues.append(f"{rec['source']}: DOI {rec['doi']} ≠ {doi}")
            ok = False
        if rec["doi"]:
            rec["doi_resolves"] = doi_resolves(rec["doi"])
            if rec["doi_resolves"] is False:
                issues.append(f"{rec['source']}: DOI {rec['doi']} doi.org'da çözümlenmiyor; kullanılmamalı")
                ok = False
        if ok:
            agreeing.append(rec["source"])
    if not found:
        status = "NOT_FOUND"
    elif issues:
        status = "CONFLICT"
    elif len(agreeing) >= 2:
        status = "VERIFIED"
    else:
        status = "PARTIAL"
    return {
        "query": {"doi": doi, "title": title, "year": year, "author": author},
        "status": status,
        "agreeing_sources": agreeing,
        "issues": issues,
        "rejected_candidates": rejected,
        "records": found,
        "checked_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "note": "Bibliyografik doğrulama içerik doğrulaması değildir; iddia için tam metin okunmalıdır.",
    }


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--doi")
    ap.add_argument("--title")
    ap.add_argument("--year", type=int)
    ap.add_argument("--author", help="İlk yazarın soyadı")
    ap.add_argument("--no-s2", action="store_true", help="Semantic Scholar'ı atla (anahtarsız hız sınırı)")
    ap.add_argument("--save", metavar="ID", help="Sonucu PATHS['verification']/<ID>.json olarak kaydet")
    args = ap.parse_args()
    if not (args.doi or args.title):
        ap.error("--doi veya --title gerekli")
    result = verify(args.doi, args.title, args.year, args.author, not args.no_s2)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.save:
        out = PATHS["verification"]
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{args.save}.json").write_text(text, encoding="utf-8")
    print(text)
    return 0 if result["status"] in ("VERIFIED", "PARTIAL") else 1


if __name__ == "__main__":
    raise SystemExit(main())
