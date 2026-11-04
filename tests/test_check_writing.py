"""check_writing.py testleri. Kurgusal (konu-bağımsız) TYBS md'leri kullanır.

Ortak `tmp_kit` fikstürü (tests/conftest.py) gerçek rules/2209a-2026.json +
rules/writing-lint.json + örnek project.json ile geçici bir KİT kurar.
Her kontrol için olumlu (uyarı çıkar) ve olumsuz (uyarı çıkmaz) durum sınanır.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import config

REPO_ROOT = Path(__file__).resolve().parents[1]

# İçerik açısından TEMİZ bir TYBS: her kontrolü olumsuz (uyarısız) geçmeli.
CLEAN_TYBS = """# Başvuru

## Özet

Bu kurgusal özet, bilimsel nitelik için literatürdeki boşluğa özgün katkıyı anar;
yöntem için ölçüm ve analiz adımlarını kısaca söyler; proje yönetimi için iş paketi
ve takvim düzenini belirtir; yaygın etki için açık kaynak çıktı ve topluma yararı
vurgular. Kelime sayısı yirmi beşin açıkça üzerindedir ve dört kapsam da anılır.

## 1.1 Önem

Bu bölümde önem somut kanıta bağlanır. Önceki çalışma Soyad (2020) ilgili bulguyu
belirtmiştir ve (Başka, 2021) bunu destekler.

## 1.2 Amaç

Amaç, en az 450 başarılı ölçümle doğruluğu %90 eşiğinde sınamaktır. Süre 9 aydır.

## 2. Yöntem

Yöntem olarak bağımsız örneklem t-testi ve %95 güven aralığı kullanılır; her site
üç bağlamda ölçülür.

## 3.1 Çalışma Takvimi

| Proje Süresi (Ay) | Faaliyetler | Kim | Başarı Ölçütü ve Katkısı |
| --- | --- | --- | --- |
| 1-3 | İP1: Tasarım | Ekip | Doğruluk ≥%90 — %50 |
| 4-9 | İP2: Uygulama | Ekip | En az 450 ölçüm — %50 |

## 3.2 Risk

| Risk | B planı |
| --- | --- |
| Erişim gecikmesi | Yedek veri setiyle aynı hedefe ulaşılır |

## 4. Yaygın Etki

Açık kaynak araç ve bilimsel yayın başvurusu beklenir.
"""


def _set_project(tmp_kit, **overrides):
    p = json.loads(tmp_kit.paths["project_config"].read_text(encoding="utf-8"))
    p.pop("_note", None)
    p["project"]["title"] = "ÖRNEK Proje Başlığı"
    p["project"]["keywords"] = ["bir", "iki", "üç"]
    p["team"]["lead"]["name"] = "Ada Yürütücü"
    p["team"]["advisor"]["name"] = "Danışman Hoca"
    p["timeline"]["duration_months"] = 9
    p["budget"]["total_tl"] = 10000
    for dotted, value in overrides.items():
        cur = p
        parts = dotted.split(".")
        for part in parts[:-1]:
            cur = cur.setdefault(part, {})
        cur[parts[-1]] = value
    tmp_kit.paths["project_config"].write_text(json.dumps(p, ensure_ascii=False), encoding="utf-8")
    config.project.cache_clear()


def _copy_writing_rules(tmp_kit):
    """Gerçek writing-lint.json'u geçici köke kopyalar (conftest kopyalamıyor)."""
    src = REPO_ROOT / "rules" / "writing-lint.json"
    dst = tmp_kit.paths["rules_dir"] / "writing-lint.json"
    shutil.copy(src, dst)
    # check_writing modülü WRITING_RULES_FILE'ı import anında bağlar; monkeypatch
    # PATHS'i yerinde güncellediği için modülü yeniden yükleyip yolu tazeleriz.
    import importlib

    import check_writing
    importlib.reload(check_writing)
    return dst


def _write(tmp_kit, text):
    path = tmp_kit.paths["report_tybs"] / "tybs-application.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _ids(rep):
    return {w["id"] for w in rep["warnings"]}


def test_clean_text_passes(tmp_kit):
    import check_writing as cw
    _copy_writing_rules(tmp_kit)
    _set_project(tmp_kit)
    path = _write(tmp_kit, CLEAN_TYBS)
    rep = cw.check(path)
    assert rep["warnings"] == [], [w["id"] for w in rep["warnings"]]


def test_belirsiz_katki_flagged(tmp_kit):
    import check_writing as cw
    _copy_writing_rules(tmp_kit)
    _set_project(tmp_kit)
    bad = CLEAN_TYBS.replace(
        "Açık kaynak araç ve bilimsel yayın başvurusu beklenir.",
        "Bu proje literatüre büyük önem taşımaktadır ve katkı sağlayacaktır.",
    )
    rep = cw.check(_write(tmp_kit, bad))
    assert "belirsiz-katki" in _ids(rep)


def test_belirsiz_yontem_only_in_method(tmp_kit):
    import check_writing as cw
    _copy_writing_rules(tmp_kit)
    _set_project(tmp_kit)
    bad = CLEAN_TYBS.replace(
        "Yöntem olarak bağımsız örneklem t-testi ve %95 güven aralığı kullanılır; her site\nüç bağlamda ölçülür.",
        "Uygun yöntemlerle veriler toplanacak ve gerekli analizler yapılacaktır.",
    )
    rep = cw.check(_write(tmp_kit, bad))
    assert "belirsiz-yontem" in _ids(rep)
    # Yöntem deseni Özet'te geçse bile yalnız '2.' bölümünde sayılır.
    other = CLEAN_TYBS.replace(
        "yöntem için ölçüm ve analiz adımlarını kısaca söyler;",
        "yöntem için uygun yöntemlerle çalışılacaktır;",
    )
    rep2 = cw.check(_write(tmp_kit, other))
    assert "belirsiz-yontem" not in _ids(rep2)


def test_risk_inkari_flagged(tmp_kit):
    import check_writing as cw
    _copy_writing_rules(tmp_kit)
    _set_project(tmp_kit)
    bad = CLEAN_TYBS.replace("Erişim gecikmesi | Yedek veri setiyle aynı hedefe ulaşılır",
                             "Risk | Herhangi bir risk öngörülmemektedir")
    rep = cw.check(_write(tmp_kit, bad))
    assert "risk-inkari" in _ids(rep)


def test_iyimser_vaat_flagged(tmp_kit):
    import check_writing as cw
    _copy_writing_rules(tmp_kit)
    _set_project(tmp_kit)
    bad = CLEAN_TYBS.replace(
        "Açık kaynak araç ve bilimsel yayın başvurusu beklenir.",
        "Proje zamanında ve başarıyla tamamlanacaktır.",
    )
    rep = cw.check(_write(tmp_kit, bad))
    assert "iyimser-vaat" in _ids(rep)


def test_success_metric_missing_flagged(tmp_kit):
    import check_writing as cw
    _copy_writing_rules(tmp_kit)
    _set_project(tmp_kit)
    bad = CLEAN_TYBS.replace("Doğruluk ≥%90 — %50", "Tasarım tamamlanır — %50")
    rep = cw.check(_write(tmp_kit, bad))
    assert "olcusuz-basari" in _ids(rep)


def test_success_metric_present_not_flagged(tmp_kit):
    import check_writing as cw
    _copy_writing_rules(tmp_kit)
    _set_project(tmp_kit)
    rep = cw.check(_write(tmp_kit, CLEAN_TYBS))
    assert "olcusuz-basari" not in _ids(rep)


def test_objectives_measurable_flagged(tmp_kit):
    import check_writing as cw
    _copy_writing_rules(tmp_kit)
    _set_project(tmp_kit)
    bad = CLEAN_TYBS.replace(
        "Amaç, en az 450 başarılı ölçümle doğruluğu %90 eşiğinde sınamaktır. Süre 9 aydır.",
        "Amaç, konuya ilişkin farkındalığı artırmak ve alana genel katkı yapmaktır.",
    )
    rep = cw.check(_write(tmp_kit, bad))
    assert "olcusuz-amac" in _ids(rep)


def test_citation_missing_flagged(tmp_kit):
    import check_writing as cw
    _copy_writing_rules(tmp_kit)
    _set_project(tmp_kit)
    bad = CLEAN_TYBS.replace(
        "Bu bölümde önem somut kanıta bağlanır. Önceki çalışma Soyad (2020) ilgili bulguyu\n"
        "belirtmiştir ve (Başka, 2021) bunu destekler.",
        "Bu bölümde önem anlatılır ancak hiçbir kaynağa atıf verilmemiştir.",
    )
    rep = cw.check(_write(tmp_kit, bad))
    assert "atif-yok" in _ids(rep)


def test_citation_present_not_flagged(tmp_kit):
    import check_writing as cw
    _copy_writing_rules(tmp_kit)
    _set_project(tmp_kit)
    rep = cw.check(_write(tmp_kit, CLEAN_TYBS))
    assert "atif-yok" not in _ids(rep)


def test_long_sentence_flagged(tmp_kit):
    import check_writing as cw
    _copy_writing_rules(tmp_kit)
    _set_project(tmp_kit)
    long_sent = "kelime " * 50 + "son."
    bad = CLEAN_TYBS.replace("Açık kaynak araç ve bilimsel yayın başvurusu beklenir.", long_sent)
    rep = cw.check(_write(tmp_kit, bad))
    assert "uzun-cumle" in _ids(rep)


def test_abstract_scope_missing_flagged(tmp_kit):
    import check_writing as cw
    _copy_writing_rules(tmp_kit)
    _set_project(tmp_kit)
    # Yöntem/etki ipuçlarını kaldır: ozet-kapsam uyarısı çıkmalı.
    bad = CLEAN_TYBS.replace(
        "Bu kurgusal özet, bilimsel nitelik için literatürdeki boşluğa özgün katkıyı anar;\n"
        "yöntem için ölçüm ve analiz adımlarını kısaca söyler; proje yönetimi için iş paketi\n"
        "ve takvim düzenini belirtir; yaygın etki için açık kaynak çıktı ve topluma yararı\n"
        "vurgular. Kelime sayısı yirmi beşin açıkça üzerindedir ve dört kapsam da anılır.",
        "Bu özet yalnız özgün literatür boşluğundan ve bilimsel nitelikten söz eder; başka "
        "bir konu anılmaz ve kelime sayısı yirmi beşin üzerinde tutulmuştur ki sınırı aşsın.",
    )
    rep = cw.check(_write(tmp_kit, bad))
    assert "ozet-kapsam" in _ids(rep)


def test_html_comment_skipped(tmp_kit):
    import check_writing as cw
    _copy_writing_rules(tmp_kit)
    _set_project(tmp_kit)
    # Yorum içindeki 'katkı sağlayacaktır' SAYILMAMALI.
    bad = CLEAN_TYBS.replace(
        "## 4. Yaygın Etki",
        "<!-- bu proje literatüre katkı sağlayacaktır, risk öngörülmemektedir -->\n## 4. Yaygın Etki",
    )
    rep = cw.check(_write(tmp_kit, bad))
    assert "belirsiz-katki" not in _ids(rep)
    assert "risk-inkari" not in _ids(rep)


def test_code_fence_skipped(tmp_kit):
    import check_writing as cw
    _copy_writing_rules(tmp_kit)
    _set_project(tmp_kit)
    bad = CLEAN_TYBS.replace(
        "Açık kaynak araç ve bilimsel yayın başvurusu beklenir.",
        "```\nbu proje katkı sağlayacaktır\n```",
    )
    rep = cw.check(_write(tmp_kit, bad))
    assert "belirsiz-katki" not in _ids(rep)


def test_json_schema(tmp_kit):
    import check_writing as cw
    _copy_writing_rules(tmp_kit)
    _set_project(tmp_kit)
    rep = cw.check(_write(tmp_kit, CLEAN_TYBS))
    assert set(rep) >= {"file", "warnings"}
    assert isinstance(rep["warnings"], list)
    for w in rep["warnings"]:
        assert {"id", "section", "line", "quote", "message", "suggestion"} <= set(w)


def test_missing_file_no_crash(tmp_kit):
    import check_writing as cw
    _copy_writing_rules(tmp_kit)
    _set_project(tmp_kit)
    rep = cw.check(tmp_kit.paths["report_tybs"] / "yok.md")
    assert rep["warnings"] == []


def test_real_templates_do_not_crash(tmp_kit):
    """Gerçek şablonlarla çökmemeli (sayı iddia etmeyiz)."""
    import check_writing as cw
    _copy_writing_rules(tmp_kit)
    _set_project(tmp_kit)
    for name in ("proposal.md", "tybs-application.md"):
        src = REPO_ROOT / "templates" / name
        rep = cw.check(src)
        assert "warnings" in rep
        assert isinstance(rep["warnings"], list)


def test_strict_exit_code(tmp_path):
    """--strict + bulgu → çıkış 1; bulgu yok → 0 (gerçek repo rules ile subprocess)."""
    import subprocess
    import sys

    tool = REPO_ROOT / "tools" / "check_writing.py"
    bad = tmp_path / "bad.md"
    bad.write_text(
        "# X\n\n## 4. Yaygın Etki\n\nBu proje literatüre büyük önem taşımaktadır.\n",
        encoding="utf-8",
    )
    proc = subprocess.run(
        [sys.executable, str(tool), str(bad), "--strict"],
        capture_output=True, text=True, encoding="utf-8", check=False, timeout=60,
        stdin=subprocess.DEVNULL,
    )
    assert proc.returncode == 1, proc.stdout + proc.stderr

    good = tmp_path / "good.md"
    good.write_text("# X\n\n## 4. Yaygın Etki\n\nAçık kaynak araç ve yayın başvurusu.\n", encoding="utf-8")
    proc2 = subprocess.run(
        [sys.executable, str(tool), str(good), "--strict"],
        capture_output=True, text=True, encoding="utf-8", check=False, timeout=60,
        stdin=subprocess.DEVNULL,
    )
    assert proc2.returncode == 0, proc2.stdout + proc2.stderr


def test_json_cli_output(tmp_path):
    """--json geçerli JSON ve beklenen şemayı basar."""
    import json as _json
    import subprocess
    import sys

    tool = REPO_ROOT / "tools" / "check_writing.py"
    md = tmp_path / "x.md"
    md.write_text("# X\n\n## 4. Yaygın Etki\n\nBu proje katkı sağlayacaktır.\n", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(tool), str(md), "--json"],
        capture_output=True, text=True, encoding="utf-8", check=False, timeout=60,
        stdin=subprocess.DEVNULL,
    )
    assert proc.returncode == 0, proc.stderr
    data = _json.loads(proc.stdout)
    assert "warnings" in data and isinstance(data["warnings"], list)
    assert any(w["id"] == "belirsiz-katki" for w in data["warnings"])
