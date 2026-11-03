"""DOCX rapor iç tutarlılık denetimi.

Varsayılan mod sonuç raporu için tam denetimdir; taslakta ``--draft`` ile
"caption var ama metinde atıf yok" bulguları uyarıya düşürülür (metin henüz
tabloları bağlamamış olabilir).

Kullanım:
    uv run python tools/check_report.py report/final/test.docx [--json] [--draft]

Kontroller:
    1. Şekil/Tablo caption numaraları 1'den başlayıp ardışık mı?
    2. Metindeki her "Şekil N"/"Tablo N" atfının caption'ı var mı; her caption'a atıf var mı?
    3. Metin içi yazar–yıl atıfları "Kaynaklar" listesinde var mı; listede atıfsız kaynak var mı?
    4. DOI'li kaynaklarda DOI yazılmış mı (references kaydında DOI varsa)?
    5. Kalan placeholder / doğrulanmamış işaret var mı?
    6. Şablon bölüm etiketlerinden içeriği boş kalan var mı?
    7. Mock değerler belgede kalmış mı (`PATHS['mock_data']`, biçim:
       {"values": [{"field", "value", "location"}]})?
Çıkış kodu: sorun varsa 1, ayar hatası 2.

Kaynakça kardeş `bibkit` modülünden okunur (API: load(), cite_key(r), format_entry(r), USABLE).
Modül yoksa kaynak atıf eşleştirmesi biçime dayalı yapılır (3–4 kısmen çalışır).

Kurum/mevzuat atıfları:
    - Genel Türk mevzuatı deseni: "<sayı> sayılı Kanun(un/u)" (ör. "6698 sayılı Kanun").
    - `project.json` `checks.institution_aliases` (takma ad → references künyesinin ilk
      sözcüğü) ile metinde kurum kısaltmasıyla ("TÜİK" vb.) yapılan atıf künyeye eşlenir.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config
from docxkit import SECTIONS, is_label

PLACEHOLDERS = [
    r"\bTODO\b",
    r"\bXXX\b",
    r"\[KAYNAK",
    r"\[DOĞRULANMADI",
    r"\[ATIF",
    r"koyu harflerle yazılacak",
    r"\?\?\?",
    r"Lorem ipsum",
]
SURNAME = r"[A-ZÇĞİÖŞÜ][a-zçğıöşüA-ZÇĞİÖŞÜ'’\-]+"
YEAR = r"(?:1[89]|20)\d{2}[a-z]?|t\.y\."
# Kişi soyadı, kurum kısaltması (büyük harfli; project.json ile eşlenebilir) ve
# genel Türk mevzuatı atfı "<sayı> sayılı Kanun(un/u)".
NAME = rf"\d+ sayılı Kanun(?:un|u)?|{SURNAME}"
# (Soyad, 2020) (Soyad ve Soyad, 2020) (Soyad vd., 2020; TÜİK, t.y.) ve Soyad vd. (2020)
PAREN = re.compile(rf"\(([^()]*?(?:{YEAR}))\)")
NARRATIVE = re.compile(rf"({NAME})(?:\s+(?:vd\.|ve\s+{SURNAME}))?\s+\(({YEAR})\)")


def fold(s: str) -> str:
    # Türkçe iyelik/hal eki: kesme işareti (' veya ') ve sonrası atılır, böylece
    # "Yılmaz'ın", "Cohen'e", "Wilson'ın" atfı kaynakçadaki soyadla eşleşir.
    # Mevzuat atfı ("6698 sayılı Kanun") kesme işareti içermediğinden etkilenmez.
    s = re.sub(r"['’].*$", "", s.strip())
    s = unicodedata.normalize("NFKD", s.replace("ı", "i").replace("İ", "I"))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"(kanun)(un|u)$", r"\1", s)


def institution_aliases() -> dict[str, str]:
    """project.json `checks.institution_aliases`: {takma_ad: references künyesinin ilk sözcüğü}.

    Metinde takma adla (ör. 'TÜİK') yapılan atıf, references künyesinin ilk sözcüğüne
    (ör. 'Türkiye') eşlenir; böylece atıf–kaynakça karşılaştırması tutar.
    project.json yoksa boş döner (araç yine çalışır).
    """
    try:
        mapping = config.get(config.project(), "checks.institution_aliases") or {}
    except config.ConfigError:
        return {}
    return {fold(k): fold(str(v).split()[0]) for k, v in mapping.items() if v}


def paragraphs_with_kind(doc):
    """Gövde, tablo hücresi ve text box paragraflarını sırayla verir."""
    for p in doc.element.body.iter(qn("w:p")):
        text = "".join(t.text or "" for t in p.iter(qn("w:t")))
        style_el = p.find(qn("w:pPr") + "/" + qn("w:pStyle"))
        style_id = style_el.get(qn("w:val")) if style_el is not None else ""
        yield text, style_id


def citations(text: str, aliases: dict[str, str] | None = None) -> set[tuple[str, str]]:
    """Metin içi (soyad/kurum, yıl) atıflarını çıkarır; kurum takma adlarını eşler."""
    aliases = aliases or {}

    def norm(name: str) -> str:
        f = fold(name)
        return aliases.get(f, f)

    found: set[tuple[str, str]] = set()
    for m in NARRATIVE.finditer(text):
        found.add((norm(m.group(1)), m.group(2)[:4] if m.group(2)[0].isdigit() else m.group(2)))
    for m in PAREN.finditer(text):
        for part in m.group(1).split(";"):
            mm = re.match(rf"\s*({NAME}).*?({YEAR})", part)
            if mm:
                y = mm.group(2)
                found.add((norm(mm.group(1)), y[:4] if y[0].isdigit() else y))
    return found


def reference_keys() -> dict[str, tuple[tuple[str, str], dict]]:
    """Biçimli kaynakça satırı → (atıf anahtarı, kayıt).

    bibkit modülü yoksa boş döner; çağıran biçime dayalı eşleştirmeye düşer.
    """
    try:
        import bibkit
    except ImportError:
        return {}
    out = {}
    for r in bibkit.load():
        name, year = bibkit.cite_key(r)
        out[bibkit.format_entry(r)] = ((fold(name), str(year)), r)
    return out


def _usable_set() -> set[str]:
    try:
        import bibkit

        return set(getattr(bibkit, "USABLE", {"VERIFIED", "PARTIAL", "PUBLISHER_PAGE"}))
    except ImportError:
        return {"VERIFIED", "PARTIAL", "PUBLISHER_PAGE"}


def check(path: Path, draft: bool = False) -> dict:
    doc = Document(str(path))
    style_names = {s.style_id: s.name for s in doc.styles}
    paras = [(t, style_names.get(sid, sid)) for t, sid in paragraphs_with_kind(doc)]
    problems: list[str] = []
    warnings: list[str] = []
    aliases = institution_aliases()

    captions = {"Şekil": [], "Tablo": []}
    body_text, ref_entries, in_refs = [], [], False
    for text, style in paras:
        if style == "KL Caption":
            m = re.match(r"(Şekil|Tablo) (\d+)\.", text)
            if m:
                captions[m.group(1)].append(int(m.group(2)))
            continue
        if style.startswith("Heading") and text.strip() in ("Kaynaklar", "Kaynakça"):
            in_refs = True
            continue
        if style.startswith("Heading"):
            in_refs = False
        if in_refs and style == "KL Reference":
            ref_entries.append(text)
        else:
            body_text.append(text)
    full_body = "\n".join(body_text)

    # 1–2 numaralandırma ve atıflar
    for kind, nums in captions.items():
        if nums != list(range(1, len(nums) + 1)):
            problems.append(f"{kind} numaraları ardışık değil: {nums}")
        mentioned = {int(n) for n in re.findall(rf"{kind} (\d+)", full_body)}
        for n in sorted(mentioned - set(nums)):
            problems.append(f"Metinde {kind} {n} atfı var ama caption'ı yok")
        for n in sorted(set(nums) - mentioned):
            msg = f"{kind} {n} caption'ı var ama metinde atıf yok"
            # Taslakta metin henüz tabloları/şekilleri bağlamamış olabilir;
            # bu başlık–atıf eşleşmesini uyarıya düşür (sonuç raporunda sorun).
            (warnings if draft else problems).append(msg)

    # 3–4 kaynak atıfları
    cited = citations(full_body, aliases)
    known = reference_keys()
    usable = _usable_set()
    listed = {}
    for e in ref_entries:
        if e in known:
            listed[known[e][0]] = e
            continue
        m = re.match(rf"\s*({SURNAME})", e)
        # APA "(2020)." veya TÜBİTAK "Soyad, A. 2020." biçimi
        y = re.search(rf"\(({YEAR})", e) or re.search(rf"\s({YEAR})\.\s", e)
        if m and y:
            listed[(fold(m.group(1)), y.group(1)[:4])] = e
        else:
            problems.append(f"Kaynak girdisi biçimi tanınmadı: {e[:60]}")
    for key in sorted(cited - set(listed)):
        problems.append(f"Metin içi atıf kaynakçada yok: {key[0].title()} ({key[1]})")
    for key in sorted(set(listed) - cited):
        problems.append(f"Kaynakçada var, metinde atıf yok: {key[0].title()} ({key[1]})")
    for key, r in known.values():
        if key in listed and r.get("doi") and r["doi"].lower() not in listed[key].lower():
            problems.append(f"DOI eksik: {r['id']} ({r['doi']}) — TÜBİTAK DOI'li kaynakta DOI ister")
        if key in listed and r.get("status") and r.get("status") not in usable:
            problems.append(f"Doğrulanmamış kaynak kaynakçada: {r['id']} ({r.get('status')})")

    # 5 placeholder'lar
    all_text = "\n".join(t for t, _ in paras)
    for pat in PLACEHOLDERS:
        # Harf duyarlı: "TODO" işareti ile kaynak başlığındaki "Todo" karışmasın.
        for m in re.finditer(pat, all_text):
            problems.append(f"Placeholder/işaret kalmış: '{all_text[max(0, m.start() - 20) : m.end() + 20]}'")

    # 6 boş bölümler
    labels = list(SECTIONS.values())
    texts = [t.strip() for t, _ in paras]
    for i, t in enumerate(texts):
        if any(is_label(t, lb) for lb in labels):
            nxt = next((x for x in texts[i + 1 :] if x), "")
            if any(is_label(nxt, lb) for lb in labels) or nxt.startswith(
                ("PROJE YÜRÜTÜCÜSÜNÜN", "Kaynaklar")
            ):
                problems.append(f"Bölüm boş: {t[:50]}")

    # 7 mock değerler: belgede işaretlenmez, yalnız burada uyarı olarak görünür
    mock_warnings = []
    mock_file = Path(config.PATHS["mock_data"])
    if mock_file.exists():
        try:
            data = json.loads(mock_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        # Biçim: {"values": [{"field", "value", "location"}]}
        for item in data.get("values", []):
            value = item.get("value")
            # Naif alt dizgi yanlış pozitif üretir ('42' her yerde geçer); 3
            # karakterden kısa değerleri atla ve sözcük sınırıyla eşleştir.
            if not value or len(str(value)) < 3:
                continue
            if re.search(rf"(?<!\w){re.escape(str(value))}(?!\w)", all_text):
                mock_warnings.append(
                    f"{item.get('field', '?')}: '{value}' ({item.get('location', '?')})"
                )

    return {
        "docx": str(path),
        "captions": captions,
        "citations": sorted(cited),
        "reference_entries": len(ref_entries),
        "problems": problems,
        "warnings": warnings,
        "mock_warnings": mock_warnings,
    }


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("docx", type=Path)
    ap.add_argument("--json", action="store_true")
    ap.add_argument(
        "--draft",
        action="store_true",
        help="Taslak modu: 'başlık var, metinde atıf yok' sorunu uyarıya düşer.",
    )
    args = ap.parse_args()
    rep = check(args.docx, draft=args.draft)
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print(f"Belge: {rep['docx']}")
        print(f"Şekil: {rep['captions']['Şekil']}  Tablo: {rep['captions']['Tablo']}")
        print(f"Kaynakça girdisi: {rep['reference_entries']}")
        if rep["mock_warnings"]:
            print("Mock değer uyarıları:")
            for u in rep["mock_warnings"]:
                print(f"  - {u}")
        if rep["warnings"]:
            print(f"UYARI ({len(rep['warnings'])}):")
            for w in rep["warnings"]:
                print(f"  - {w}")
        if rep["problems"]:
            print(f"SORUN ({len(rep['problems'])}):")
            for p in rep["problems"]:
                print(f"  - {p}")
        else:
            print("Sorun yok.")
    return 1 if rep["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
