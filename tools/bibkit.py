"""sources/references.json → library.bib ve biçimli kaynakça satırları.

Kullanım:
    uv run python tools/bibkit.py bib             # sources/library.bib üretir
    uv run python tools/bibkit.py list [id ...]   # rapor kaynakça satırları (TÜBİTAK biçimi)
    uv run python tools/bibkit.py lint            # zorunlu alan, DOI ve durum kontrolü

references.json tek doğruluk kaynağıdır; library.bib ondan türetilir, elle düzenlenmez.
Yollar `config.PATHS`'ten çağrı anında okunur; böylece testler geçici klasöre yönlendirebilir.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from config import PATHS

# Doğrulama durumları: verify_source.py ve matrix.py ile aynı küme.
STATUSES = {"VERIFIED", "PARTIAL", "PUBLISHER_PAGE", "CONFLICT", "NOT_FOUND", "UNVERIFIED"}
USABLE = {"VERIFIED", "PARTIAL", "PUBLISHER_PAGE"}


def load() -> list[dict]:
    """references.json içeriğini okur. Dosya yoksa boş liste döndürür (çökmez)."""
    path = PATHS["references"]
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SystemExit(f"HATA: {path} bozuk JSON (satır {e.lineno}): {e.msg}")
    if not isinstance(data, list):
        raise SystemExit(f"HATA: {path} bir kayıt listesi olmalı (en dış köşeli parantez)")
    return data


def _authors_apa(authors: list[str]) -> str:
    if len(authors) == 1:
        return authors[0]
    if len(authors) <= 20:
        return ", ".join(authors[:-1]) + " ve " + authors[-1]
    return ", ".join(authors[:19]) + ", ... " + authors[-1]


def _authors_of(r: dict) -> list[str]:
    """Kaydın yazar listesini güvenle döndürür (boş/eksik -> boş liste)."""
    authors = r.get("authors")
    return authors if isinstance(authors, list) else []


def cite_key(r: dict) -> tuple[str, str]:
    """Metin içi atıf anahtarı: (ilk yazar soyadı veya cite_as, yıl).

    Yazar listesi boşsa cite_as (yoksa boş dize) kullanılır; IndexError fırlatmaz.
    """
    authors = _authors_of(r)
    name = r.get("cite_as") or (authors[0].split(",")[0] if authors else "")
    return name, str(r.get("year", ""))


def sort_key(r: dict) -> tuple:
    """Kaynakça sırası: ilk yazar soyadı (alfabetik), tek yazarlılar önce, sonra yıl.

    TÜBİTAK sayfası soyada göre alfabetik, aynı yazarda kronolojik sıra ister.
    Yazar listesi boşsa cite_as (yoksa boş dize) ilk anahtar olarak kullanılır.
    """
    authors = _authors_of(r)
    first = (authors[0] if authors else (r.get("cite_as") or "")).replace("ı", "i").replace("İ", "I").casefold()
    return (first, len(authors) > 1, [a.casefold() for a in authors[1:]], str(r.get("year", "")))


def _quoted(title: str) -> str:
    """Başlığı TÜBİTAK biçimi için “…” içine alır; iç tırnaklar tek tırnağa çevrilir."""
    t = title.rstrip(".").replace("“", "‘").replace("”", "’")
    t = re.sub(r'"([^"]*)"', r"‘\1’", t)
    return f"“{t}”"


def _date_dmy(date_text: str) -> str:
    """'2016, 7 Nisan' → '7 Nisan 2016'."""
    year, _, rest = date_text.partition(", ")
    return f"{rest} {year}" if rest else date_text


def format_entry(r: dict) -> str:
    """TÜBİTAK 'Bibliyografik Verilerin Düzenlenmesi' biçimi.

    Süreli yayın: Soyad, A., Soyad, B. Yıl. “Başlık”, Dergi, Cilt (Sayı), Sayfa. DOI
    İnternet metni: Kurum. Yıl. “Başlık”, Yayın yeri. Adres, Son erişim tarihi: Gün Ay Yıl.
    Kitap: Soyad, A. Yıl. “Başlık”, Yayınevi, Sayfa.
    DOI varsa kaynağın sonuna https://doi.org/ biçiminde eklenir (zorunlu).
    """
    author_list = _authors_of(r)
    # Yazar yoksa cite_as (yoksa boş) kullan; IndexError/çökme yerine güvenli varsayılan.
    authors = ", ".join(author_list) if author_list else (r.get("cite_as") or "")
    first_author = author_list[0] if author_list else authors
    year = str(r.get("year", "")).rstrip(".")
    pages = (r.get("pages") or "").replace("-", "–")
    if r["type"] == "legal":
        if first_author == r["title"]:
            out = f"{r['title']}. {year}. {r['venue']}, {_date_dmy(r.get('date_text', ''))}."
        elif r.get("venue") and r["venue"] != first_author:
            out = f"{authors}. {year}. {_quoted(r['title'])}, {r['venue']}."
        else:
            out = f"{authors}. {year}. {_quoted(r['title'])}."
        if r.get("url"):
            out += f" {r['url']}"
        if r.get("accessed"):
            out += f", Son erişim tarihi: {r['accessed']}."
        return out
    if r["type"] == "web":
        out = f"{authors} {year}. {_quoted(r['title'])}"
        if r.get("venue"):
            out += f", {r['venue']}"
        out += "."
        if r.get("url"):
            out += f" {r['url']}"
        if r.get("accessed"):
            out += f", Son erişim tarihi: {r['accessed']}."
        return out
    if r["type"] == "book":
        out = f"{authors} {year}. {_quoted(r['title'])}"
        if r.get("venue"):
            out += f", {r['venue']}"
        if pages:
            out += f", {pages}"
        out += "."
        if r.get("doi"):
            out += f" https://doi.org/{r['doi']}"
        elif r.get("url"):
            out += f" {r['url']}"
        return out
    head = f"{authors} {year}. {_quoted(r['title'])}, {r.get('venue') or ''}"
    if r["type"] == "article":
        vol = r.get("volume") or ""
        iss = r.get("issue")
        if vol:
            head += f", {vol}" + (f" ({iss})" if iss else "")
        elif iss:
            head += f", Sayı {iss}"
    elif r["type"] == "thesis":
        return f"{head}. YÖK Ulusal Tez Merkezi."
    if pages:
        head += f", {pages}"
    head += "."
    if r.get("doi"):
        return f"{head} https://doi.org/{r['doi']}"
    if r.get("url"):
        return f"{head} {r['url']}"
    return head


def format_entry_apa(r: dict) -> str:
    """Türkçe APA 7 benzeri satır (dergi başvuruları için saklanır)."""
    if r["type"] == "legal":
        author = r["authors"][0]
        if author == r["title"]:
            return f"{author}. ({r.get('date_text', r['year'])}). {r['venue']}. {r.get('url', '')}".rstrip()
        return (
            f"{author}. ({r.get('date_text', r['year'])}). {r['title']}. "
            f"{r['venue']}. {r.get('url', '')}"
        ).rstrip()
    title = r["title"] if r["title"][-1] in ".?!…" or r["title"].endswith(("”", '"')) else r["title"] + "."
    parts = [f"{_authors_apa(r['authors'])} ({r['year']}). {title}"]
    venue = r.get("venue") or ""
    if r["type"] == "article":
        vol = r.get("volume") or ""
        iss = f"({r['issue']})" if r.get("issue") else ""
        volume_part = f", {vol}{iss}" if vol else (f", Sayı {r['issue']}" if r.get("issue") else "")
        pages = f", {r['pages'].replace('-', '–')}" if r.get("pages") else ""
        parts.append(f"{venue}{volume_part}{pages}.")
    elif r["type"] == "thesis":
        parts[-1] = parts[-1].rstrip(".")
        parts.append(f"[{venue}]. YÖK Ulusal Tez Merkezi.")
        return " ".join(parts)
    elif r["type"] == "inproceedings":
        pages = f" (ss. {r['pages'].replace('-', '–')})" if r.get("pages") else ""
        parts.append(f"{venue}{pages}.")
    elif r["type"] in ("book", "web"):
        parts.append(f"{venue}." if venue else "")
    else:
        parts.append(f"{venue}.")
    if r.get("doi"):
        parts.append(f"https://doi.org/{r['doi']}")
    elif r.get("url"):
        parts.append(r["url"])
    return " ".join(p for p in parts if p)


def _bib_escape(s: str) -> str:
    return s.replace("&", r"\&").replace("%", r"\%")


def to_bibtex(r: dict) -> str:
    kind = {
        "article": "article",
        "inproceedings": "inproceedings",
        "preprint": "misc",
        "legal": "misc",
        "thesis": "misc",
        "book": "book",
        "web": "misc",
    }.get(r["type"], "misc")
    if kind == "article":
        venue_field = "journal"
    elif kind == "inproceedings":
        venue_field = "booktitle"
    elif kind == "book":
        venue_field = "publisher"
    else:
        venue_field = "howpublished"
    fields = {
        "author": " and ".join(a.rstrip(".") for a in _authors_of(r)) or None,
        "title": "{" + r["title"] + "}",
        "year": str(r["year"]),
        venue_field: r.get("venue"),
        "volume": r.get("volume"),
        "number": r.get("issue"),
        "pages": (r.get("pages") or "").replace("-", "--") or None,
        "doi": r.get("doi"),
        "url": r.get("url"),
        "note": f"Doğrulama: {r.get('status', 'UNVERIFIED')}",
    }
    body = ",\n".join(f"  {k} = {{{_bib_escape(v)}}}" for k, v in fields.items() if v)
    return f"@{kind}{{{r['id']},\n{body}\n}}\n"


def lint(refs: list[dict]) -> list[str]:
    problems = []
    ids = set()
    for r in refs:
        rid = r.get("id", "?")
        if rid in ids:
            problems.append(f"{rid}: yinelenen kimlik")
        ids.add(rid)
        for f in ("id", "type", "authors", "year", "title", "venue", "status"):
            if not r.get(f):
                problems.append(f"{rid}: '{f}' eksik")
        if r.get("status") not in STATUSES:
            problems.append(f"{rid}: bilinmeyen durum {r.get('status')}")
        if r.get("status") not in USABLE:
            problems.append(f"{rid}: durum {r.get('status')} — raporda kullanılamaz")
        if r.get("doi") and not re.match(r"^10\.\d{4,9}/\S+$", r["doi"]):
            problems.append(f"{rid}: DOI biçimi geçersiz")
        if not r.get("doi") and not r.get("url"):
            problems.append(f"{rid}: DOI de URL de yok")
        if r.get("type") == "preprint" and "ön baskı" not in (r.get("venue") or "").lower():
            problems.append(f"{rid}: ön baskı olduğu yayın yerinde belirtilmeli")
    return problems


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if config.help_requested(__doc__):
        return 0
    cmd = sys.argv[1] if len(sys.argv) > 1 else "lint"
    refs = load()
    if cmd == "bib":
        bib = PATHS["bib"]
        bib.parent.mkdir(parents=True, exist_ok=True)
        bib.write_text(
            "% Bu dosya tools/bibkit.py ile references.json'dan üretilir. Elle düzenlemeyin.\n\n"
            + "\n".join(to_bibtex(r) for r in refs),
            encoding="utf-8",
        )
        print(f"{len(refs)} kayıt -> {bib}")
    elif cmd == "list":
        if not refs:
            print("Kaynak kaydı yok. Önce sources/references.json dosyasına kayıt ekleyin.")
            return 0
        wanted = set(sys.argv[2:])
        for r in sorted(refs, key=sort_key):
            if not wanted or r["id"] in wanted:
                print(format_entry(r))
    elif cmd == "lint":
        if not refs:
            print("Kaynak kaydı yok (sources/references.json boş veya yok); denetlenecek bir şey yok.")
            return 0
        problems = lint(refs)
        print("\n".join(problems) if problems else f"{len(refs)} kayıt: sorun yok")
        return 1 if problems else 0
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
