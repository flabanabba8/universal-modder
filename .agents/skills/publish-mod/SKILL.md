---
name: publish-mod
description: Package and release a finished game mod. Covers the pre-release lint (no game files, decompiled code or leaked keys), README and install steps, credits and AI disclosure, versioning, where to upload (Nexus Mods, Steam Workshop, Thunderstore, mod.io, GitHub releases), and the post with a video. Use when the user wants to ship, share, upload, release or post a mod.
---

# Publish a mod

## 1. Lint
```bash
um publish check ./MyMod --game "<game install folder>"
```
- **FAIL:** files byte-identical to game files, leaked keys (fal/Anthropic/OpenAI/GitHub/AWS), `.env` files.
- **WARN:** decompiler fingerprints in source (`FUN_`/`DAT_`/`sub_` names, "Decompiled with" headers), large
  engine archives, absolute user paths, a missing README, generated assets without credit.

Fix every FAIL. Resolve each WARN deliberately. For example, AoE2 data mods do ship a modified `.dat`, which
is the platform's norm.

## 2. Package the way the platform expects

| Platform / loader | Package |
|---|---|
| tModLoader | Build → `.tmod`; publish from the in-game Mod Sources menu (Steam Workshop) |
| BepInEx / Thunderstore | zip with `manifest.json`, `icon.png` (256×256), `README.md`, `plugins/<Mod>.dll`; dependency strings like `BepInEx-BepInExPack-5.4.2100` |
| Nexus Mods | zip laid out as it installs (`Data/...` for Bethesda, `BepInEx/plugins/...`, `ue4ss/Mods/...`, `~mods/*.pak`) |
| AoE2 DE | the official mod site (ageofempires.com/mods) or the in-game uploader; data mods include `resources/_common/dat/...` |
| Steam Workshop | the game's own uploader or SDK tool |
| Minecraft | Modrinth / CurseForge jar with `fabric.mod.json` / `neoforge.mods.toml` |
| ROM hacks / GameMaker | patches only (BPS/IPS/xdelta), never the modified game file |

## 3. README (in the zip and on the page)
- What it adds: bullets, a GIF or the showcase video.
- Requirements: game version, the loader and its version, dependencies.
- Install, uninstall and troubleshooting (where the log is).
- Compatibility: multiplayer? Known conflicts?
- Credits:
  - the loader and libraries;
  - references you learned from;
  - **"Art/audio generated using <provider and models>"** (generation manifests list them);
  - honest AI disclosure (which agent and model built it).
- License for your code (MIT/Apache is common). Your assets' terms follow the models' licenses.

## 4. Version and changelog
Use semver in the manifest/build file, name the supported game version, and keep a changelog. When the game
updates, re-run the in-game test scene before bumping.

## 5. The post
- Lead with the video: the showcase-video skill; 20-45 s, gameplay within 2-3 s.
- Post text: the hook, what it is, the "how" credit (which agent and models built it), a link.
- If the video uses anyone else's footage, credit them by handle and ask first.
- Publishing is always the user's call. Draft it, show them, and let them press the button.

## Installed asset-provider preferences
Use existing local Flux via `um comfy flux`, or Vertex via `um image vertex`. For OpenAI images, use an agent image-generation tool with its agent authentication; never use the OpenAI API. Do not use FAL. Never download models without proposing them in normal chat and receiving user approval first. Read **game-assets** for the installed routes.

Before any public push, repository visibility change, release or artifact publication, run a secret scanner AND inspect personal deployment configuration across all exposed source, docs, scripts, defaults, history, branches, tags, generated files, logs, screenshots and package contents. Do not print sensitive values. Keep credentials and private deployment identifiers out of public content; ignore rules are not evidence that history or artifacts are clean. Do not publish until the audit is complete.
