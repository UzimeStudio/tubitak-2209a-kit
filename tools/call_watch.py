"""Resmî çağrı belgelerini indirir ve SHA-256 özetini kayıtlı değerle karşılaştırır.

rules.sources[] listesindeki URL'leri YALNIZ tubitak.gov.tr alanından indirir
(güvenlik: başka alan atlanır), ilk 16 hex karakteri BÜYÜK harf hesaplar ve
kayıtlı sha256_16 ile karşılaştırır: AYNI / DEĞİŞTİ / YENİ / ERİŞİLEMEDİ.
rules dosyasını DEĞİŞTİRMEZ; yeni özeti insanın işlemesi için rapor eder.

İndirilenler PATHS['cache']/tubitak/ altına yazılır.

Kullanım:
    uv run python tools/call_watch.py [--json]
"""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from config import ConfigError, rules

ALLOWED_DOMAIN = "tubitak.gov.tr"
USER_AGENT = "tubitak-2209a-kit/0.1 (call document watch)"


class RedirectBlocked(Exception):
    """Yönlendirme izin verilmeyen bir alana gitmeye çalıştığında."""


def allowed(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return host == ALLOWED_DOMAIN or host.endswith("." + ALLOWED_DOMAIN)


class _StrictRedirectHandler(urllib.request.HTTPRedirectHandler):
    """3xx yönlendirmenin HER adımında hedef alanı allowed() ile denetler.

    Varsayılan urlopen yönlendirmeleri sessizce izler; bu, izin dışı bir alana
    (örn. tubitak.gov.tr -> başka bir CDN) yönlendirerek alan kısıtının
    atlatılmasına yol açabilir. İzin dışı hedef RedirectBlocked ile reddedilir.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not allowed(newurl):
            raise RedirectBlocked(f"{ALLOWED_DOMAIN} dışı alana yönlendirme engellendi: {newurl}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _opener() -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(_StrictRedirectHandler)


def sha16(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16].upper()


def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with _opener().open(req, timeout=30) as r:
        # Yönlendirme zinciri izin verilen alanda kalsa bile son adresi doğrula.
        final = r.geturl()
        if not allowed(final):
            raise RedirectBlocked(f"{ALLOWED_DOMAIN} dışı son adres: {final}")
        return r.read()


def watch(fetch=download) -> dict:
    """fetch: test için enjekte edilebilir (url -> bytes; hata için exception)."""
    r = rules()
    cache = config.PATHS["cache"] / "tubitak"
    results = []
    for src in r.get("sources", []):
        url = src.get("url", "")
        recorded = src.get("sha256_16")
        row = {"id": src.get("id"), "url": url, "recorded": recorded}
        if not allowed(url):
            row["status"] = "ATLANDI"
            row["note"] = f"{ALLOWED_DOMAIN} dışı alan"
            results.append(row)
            continue
        try:
            data = fetch(url)
        except Exception as e:  # noqa: BLE001
            row["status"] = "ERİŞİLEMEDİ"
            row["note"] = str(e)
            results.append(row)
            continue
        computed = sha16(data)
        row["computed"] = computed
        cache.mkdir(parents=True, exist_ok=True)
        name = Path(urlparse(url).path).name or f"{src.get('id')}.bin"
        (cache / name).write_bytes(data)
        if recorded is None:
            row["status"] = "YENİ"
        elif recorded.upper() == computed:
            row["status"] = "AYNI"
        else:
            row["status"] = "DEĞİŞTİ"
        results.append(row)
    changed = sum(1 for s in results if s["status"] == "DEĞİŞTİ")
    return {"results": results, "changed_count": changed}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if config.help_requested(__doc__):
        return 0
    try:
        rep = watch()
    except ConfigError as e:
        print(f"HATA: {e}")
        return 2
    if "--json" in sys.argv:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        for s in rep["results"]:
            line = f"[{s['status']:>11}] {s['id']}"
            if s.get("computed"):
                line += f"  kayıtlı={s.get('recorded')} hesaplanan={s['computed']}"
            if s.get("note"):
                line += f"  ({s['note']})"
            print(line)
        print(f"\nDeğişen belge: {rep['changed_count']}")
    return 1 if rep["changed_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
