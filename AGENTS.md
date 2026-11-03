# tubitak-2209a-kit — Codex rehberi

Kurallar [CLAUDE.md](CLAUDE.md) dosyasındadır; Codex de onları uygular.

Skill'ler `.agents/skills/` altındadır ve Codex onları kendiliğinden bulur (`$` ile adını yazarak da çağırabilirsin). Bu klasör `.claude/skills/`'in birebir kopyasıdır. Skill'i düzenlerken `.claude/skills/` altını değiştir, sonra `uv run python tools/sync_skills.py` çalıştır.

İlk açılışta `project.json` yoksa `onboarding` skill'i ile başla. Hazır promptlar `prompts/` klasöründedir.
