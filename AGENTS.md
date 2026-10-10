# universal-modder

A game-modding toolkit and a shared knowledge base for AI coding agents: Claude Code, Codex, Cursor, Gemini
CLI, GitHub Copilot, OpenCode and anything else that reads `AGENTS.md`. When someone opens an agent in this
repo, they almost always want to **mod a game**, or to learn how a game was modded.

## Start here
1. **Read `skills/mod-any-game/SKILL.md` and follow its loop:** intake → recon → route → lab (backups) →
   source of truth → vertical slice → assets → verify in the real game → showcase → publish.
2. **Search the knowledge base first:** `bin/um kb search "<game or engine>"`. Other agents may already have
   written down the exact versions, routes and gotchas (`knowledge/INDEX.md`).
3. **At the end, share what you learned:** write a field note (`bin/um kb new ...`) and, once your human
   agrees, open a PR (`bin/um kb pr <note> --yes`). See `knowledge/README.md` and `CONTRIBUTING.md`.

## Tools
- **`bin/um`** is the Python CLI, and it sets itself up with `uv`.
  - Put it on PATH: `export PATH="$PWD/bin:$PATH"`, or install it anywhere with
    `uv tool install git+https://github.com/flabanabba8/universal-modder`.
  - Every group has `--help`:
    - `scan`: installed games, engine, anti-cheat, loaders, saves, routes
    - `image vertex`: direct Vertex image generation and reference-image edits
    - `comfy`: images from a local ComfyUI server, with no API key
    - `sprite` / `render3d`: art → engine-ready frames
    - `win`: launch, screenshot, input, record on Windows (also from WSL)
    - `video`: contact sheets and EDL showcase edits
    - `backup`: snapshot and restore saves
    - `publish`: pre-release lint
    - `kb`: the knowledge base
- **Assets:** use `um comfy flux` for installed local Flux or `um image vertex` for Vertex with the user’s locally configured Google ADC. See the game-assets skill. No FAL or OpenAI API. Propose any model download in normal chat and wait for user approval.
- **Skills** (`skills/*/SKILL.md`, Agent Skills format) are copied where agents look for them in a clone:
  `.agents/skills` (Codex, Gemini CLI, Copilot, Cursor, OpenCode) and `.claude/skills` (Claude Code). Edit
  `skills/`, then copy it over; a test fails while the copies differ.
- **Engine playbooks:** `skills/mod-any-game/references/engines/`.
- **Worked examples:** `examples/terraria-tmodloader`, `examples/aoe2-de-civ`,
  `examples/minecraft-gta5-passthrough`.

## Rules (full reasoning in `skills/mod-any-game/references/safety.md`)
- **What you can mod:** any game the user owns: single-player, multiplayer, or servers the user hosts.
  - Never touch online clients protected by anti-cheat.
  - Never write cheats against other players (aimbots, ESP, speed hacks).
  - Never bypass anti-cheat, DRM or ownership checks.
- **Saves:** `um backup` saves before modded launches.
- **What you ship:** never commit or publish game files, extracted assets or decompiled code. Keep
  decompiles outside the repo.
- **Processes:** kill by exact PID (`um win kill`), never by name pattern.
- **Ask first** before:
  - driving the user's mouse and keyboard, and never focus a game with an online mode while they're typing;
  - installing loaders into game folders or changing the registry;
  - publishing anything, PRs included.
- **Keep a journal:** a `MODLOG.md` in the mod's working folder. It becomes your field note at the end.

## Working on the toolkit itself
- **Python:** 3.10+, deps Pillow, numpy and PyYAML (`uv` handles them via `bin/um`). Code lives in `um/`,
  one module per CLI group, each with `register(sub)` and a docstring that doubles as `--help`.
- **Windows tools:** `um/ps1/*.ps1` embed C# 5 (Windows PowerShell 5.1's compiler): no string
  interpolation, no `out var`, no expression-bodied members.
- **Tests:** `uv run --with pytest pytest -q tests`. CI also runs `um kb check --index` and
  `um publish check .`.
- **Wording:** keep skills and docs agent-neutral ("the agent", not a product name) except in sections
  about one specific agent.

## Local analysis and image-only disposable sessions

The bundled inspection default honors this project’s requested OpenAI provider.
Explicit `--backend local` uses stateless local vision with no agent session.
Only native generation or explicitly chosen image-review escalation may create
fresh disposable agent sessions. For code, logs, documents, data, research and reviews, use ordinary
local tools and bounded source reads; do not start a text worker or subagent.
`um context capture` runs a local command and saves its output, preserving exit
status; it makes no model request. `um context analyze` is disabled.
Image tasks use disposable-vision (`um context inspect` / `generate`), with a
specific task, selected paths and criteria. Return text/verdicts/paths only.
No parent transcript, resumed worker, recursive delegation or image fallback.


## Disposable agents for every vision task

Use **disposable-vision** automatically for screenshots, sprites, diagrams,
reference images, generated-art inspection, and agent-native image generation. Explicit local inspection is stateless; native
generation uses a fresh agent session. Read `skills/disposable-vision/SKILL.md`; see `docs/disposable-vision.md` for recipes.
Send an isolated image request only the specific task, selected paths and acceptance
criteria. Never pass the parent transcript or resume an image worker. Return only
text findings, verdicts and file paths to the coordinator; keep image payloads,
base64 and previews out of its context. Repair a failed worker path instead of
falling back to coordinator vision.

Use `um context inspect` for images saved by any source, including ComfyUI and
Vertex. Use `um context generate` for native image generation; it launches an
independent review afterward. A FAIL or UNCERTAIN draft is not accepted output.
No verdict authorizes installation, overwriting assets or publication.

Native image viewing/generation are disabled for coordinator sessions in
.codex/config.toml. Workers override those settings in fresh isolated sessions
and execute their narrowly assigned tasks directly, without further delegation.
Never emit image/base64 payloads from shell or MCP to bypass the guard.
