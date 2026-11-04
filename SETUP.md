# Kurulum

Gerekenler: Git, [uv](https://docs.astral.sh/uv/) (Python'u kendisi kurar, Python ≥3.11), Claude Code veya Codex. DOCX → PDF için Microsoft Word (Windows) ya da LibreOffice (her sistem).

## Windows (PowerShell)

```powershell
winget install --id Git.Git -e
winget install --id astral-sh.uv -e
# Yeni bir terminal açın
git clone https://github.com/UzimeStudio/tubitak-2209a-kit.git my-2209a
cd my-2209a
uv sync
uv run python tools/init_project.py
uv run python tools/status.py
```

PDF için Word kuruluysa ek bir şey gerekmez. Word yoksa: `winget install --id TheDocumentFoundation.LibreOffice -e`

## macOS

```bash
brew install git uv
brew install --cask libreoffice     # PDF için
git clone https://github.com/UzimeStudio/tubitak-2209a-kit.git my-2209a && cd my-2209a
uv sync
uv run python tools/init_project.py
uv run python tools/status.py
```

## Linux (Debian/Ubuntu)

```bash
sudo apt install git libreoffice-writer
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/UzimeStudio/tubitak-2209a-kit.git my-2209a && cd my-2209a
uv sync
uv run python tools/init_project.py
uv run python tools/status.py
```

## Kurulumu doğrulama

```bash
uv run --group dev pytest -q
```

Testler 1-2 dakika sürebilir. Hepsi geçmeli. LibreOffice yoksa bir test atlanır; bu normaldir.

## Ajanı açma

- **Claude Code:** klasörü açın. `CLAUDE.md` ve `.claude/skills/` otomatik okunur.
- **Codex:** klasörü açın. `AGENTS.md` aynı kurallara yönlendirir. Skill'ler `.agents/skills/` altından otomatik bulunur.

Sonra [prompts/01-onboarding.md](prompts/01-onboarding.md) içeriğini yapıştırın.

## Sorunlar

| Belirti | Çözüm |
| --- | --- |
| `uv` bulunamadı | Kurulumdan sonra yeni terminal açın |
| `project.json yok` | `uv run python tools/init_project.py` |
| PDF dönüşümü çıkış kodu 2 | Word veya LibreOffice kurun |
| Türkçe karakterler bozuk (Windows) | Windows Terminal kullanın veya `chcp 65001` çalıştırın |
