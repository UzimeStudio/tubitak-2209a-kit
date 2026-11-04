"""init_project.py testleri. --defaults ve --set modları (etkileşimsiz).

tmp_kit örnek dosyadan bir project.json üretir; init_project testleri bu dosyayı
önce siler çünkü araç onu SIFIRDAN kurmayı test eder.
"""

from __future__ import annotations

import json

import config

REPO_ROOT = config.ROOT  # tmp_kit monkeypatch'inden ÖNCE import edildi; gerçek repo kökü.


def _fresh(tmp_kit):
    """tmp_kit'in hazır project.json'unu kaldır ve örnek dosyayı temp köke koy."""
    tmp_kit.paths["project_config"].unlink(missing_ok=True)
    example = (REPO_ROOT / "project.example.json").read_text(encoding="utf-8")
    tmp_kit.paths["project_example"].parent.mkdir(parents=True, exist_ok=True)
    tmp_kit.paths["project_example"].write_text(example, encoding="utf-8")
    config.project.cache_clear()


def _run(monkeypatch, argv):
    import init_project
    monkeypatch.setattr("sys.argv", ["init_project.py", *argv])
    return init_project.main()


def test_defaults_copies_example(tmp_kit, monkeypatch):
    _fresh(tmp_kit)
    _run(monkeypatch, ["--defaults"])
    data = json.loads(tmp_kit.paths["project_config"].read_text(encoding="utf-8"))
    assert "_note" not in data
    assert data["project"]["title"] == "TBD"
    assert tmp_kit.paths["open_questions"].exists()  # log dosyaları oluştu


def test_set_single_field(tmp_kit, monkeypatch):
    _fresh(tmp_kit)
    _run(monkeypatch, ["--defaults"])
    _run(monkeypatch, ["--set", "project.title=Gerçek Başlık"])
    data = json.loads(tmp_kit.paths["project_config"].read_text(encoding="utf-8"))
    assert data["project"]["title"] == "Gerçek Başlık"


def test_set_json_value(tmp_kit, monkeypatch):
    _fresh(tmp_kit)
    _run(monkeypatch, ["--defaults"])
    _run(monkeypatch, ["--set", 'project.keywords=["bir","iki","üç"]'])
    _run(monkeypatch, ["--set", "timeline.duration_months=9"])
    data = json.loads(tmp_kit.paths["project_config"].read_text(encoding="utf-8"))
    assert data["project"]["keywords"] == ["bir", "iki", "üç"]
    assert data["timeline"]["duration_months"] == 9


def test_existing_not_overwritten_without_force(tmp_kit, monkeypatch):
    _fresh(tmp_kit)
    tmp_kit.paths["project_config"].write_text(
        json.dumps({"project": {"title": "Elle Yazıldı"}}, ensure_ascii=False), encoding="utf-8"
    )
    rc = _run(monkeypatch, ["--defaults"])
    assert rc == 1
    data = json.loads(tmp_kit.paths["project_config"].read_text(encoding="utf-8"))
    assert data["project"]["title"] == "Elle Yazıldı"  # değişmedi


def test_force_overwrites(tmp_kit, monkeypatch):
    _fresh(tmp_kit)
    tmp_kit.paths["project_config"].write_text(
        json.dumps({"project": {"title": "Eski"}}, ensure_ascii=False), encoding="utf-8"
    )
    _run(monkeypatch, ["--defaults", "--force"])
    data = json.loads(tmp_kit.paths["project_config"].read_text(encoding="utf-8"))
    assert data["project"]["title"] == "TBD"


def test_set_on_existing_updates_only_one_field(tmp_kit, monkeypatch):
    _fresh(tmp_kit)
    tmp_kit.paths["project_config"].write_text(
        json.dumps({"project": {"title": "Eski", "short_name": "KORUNSUN"}}, ensure_ascii=False),
        encoding="utf-8",
    )
    _run(monkeypatch, ["--set", "project.title=Yeni"])
    data = json.loads(tmp_kit.paths["project_config"].read_text(encoding="utf-8"))
    assert data["project"]["title"] == "Yeni"
    assert data["project"]["short_name"] == "KORUNSUN"  # diğer alan korunur


def test_templates_logs_used_when_present(tmp_kit, monkeypatch):
    _fresh(tmp_kit)
    tdir = tmp_kit.paths["templates"] / "logs"
    tdir.mkdir(parents=True, exist_ok=True)
    (tdir / "open-questions.md").write_text("# Şablondan\n- [ ] özel\n", encoding="utf-8")
    _run(monkeypatch, ["--defaults"])
    content = tmp_kit.paths["open_questions"].read_text(encoding="utf-8")
    assert "Şablondan" in content


def test_interactive_without_terminal_fails_cleanly(tmp_kit, monkeypatch, capsys):
    """Ajan terminali/pipe: input() EOFError verir; traceback yerine yol gösteren mesaj."""
    _fresh(tmp_kit)

    def _no_tty(*_args, **_kwargs):
        raise EOFError

    monkeypatch.setattr("builtins.input", _no_tty)
    assert _run(monkeypatch, []) == 2
    err = capsys.readouterr().err
    assert "--merge values.json" in err
    assert not tmp_kit.paths["project_config"].exists()  # yarım dosya yazılmadı
