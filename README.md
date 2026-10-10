# Universal Modder — extended asset sources and bounded workers

A fork of [rehan-remade/universal-modder](https://github.com/rehan-remade/universal-modder),
with local image/video workflows, direct Vertex image generation, and disposable
vision workers and local log capture. Original MIT license and contributor attribution retained.

## Added features

- **Local FLUX.2 Klein:** `um comfy flux` generates images and sprites through ComfyUI.
- **More workflow sources:** FLUX.1-dev GGUF and MiniMax H3 video/audio API graphs
  are included under `um/workflows/`; use `um comfy run` with your installed models.
- **Vertex images and edits:** `um image vertex`, with optional reference image,
  aspect ratio, and sprite cutout. Uses your locally configured Google ADC.
- **Disposable vision:** `um context inspect` and `generate` keep image payloads
  out of the parent conversation; generation receives a separate visual review.
- **Local log capture:** `um context capture` saves verbose command output without
  starting a model session. Non-image analysis uses ordinary local tools.
- **CC0 materials:** `tools/cc0_materials.py` searches/downloads from ambientCG and
  Poly Haven. See [asset sources](docs/asset-sources.md) for commands and attribution.
- FAL CLI registration, its skill and MCP configuration are disabled in this fork.
  The historical Python module and upstream examples remain for compatibility.

## Install

```bash
uv tool install git+https://github.com/flabanabba8/universal-modder
um --help
```

Or clone this fork and run `./bin/um --help`. Base commands require Python 3.10+;
`um context` requires Python 3.11+ and model work requires an authenticated Codex CLI.
No model weights or credentials are included. ComfyUI and its required custom nodes
and model files must be installed separately. Downloads and paid calls require
explicit user authorization; local generation is preferred.

## Examples

```bash
um comfy status
um comfy flux "a blue potion bottle, game icon" --sprite --name potion
um image vertex "a mossy wall" --out assets/gen/wall.png
um image vertex "same wall in winter" --ref assets/gen/wall.png --out assets/gen/winter.png
um context capture --output outputs/tests.log --compress -- pytest -q tests
um context inspect --backend local --question "Are the edges clean?" --criteria "No halos" sprite.png
um context generate assets/new-potion.png --prompt "A blue potion icon" --criteria "One bottle, no text"
```

Set `GOOGLE_CLOUD_PROJECT` and authenticate locally with Google ADC to use Vertex.
Optional settings: `GOOGLE_CLOUD_LOCATION`, `UM_VERTEX_IMAGE_MODEL`, or private
`~/.config/universal-modder/config.json`. Never commit that file or authentication
material. OpenAI images use the disposable agent tool path, not an API-key fallback.

The existing toolkit also provides engine/game scanning, sprite preparation,
Blender rendering, Windows input/capture, video editing, backups, release lint,
and a shared modding knowledge base. Each group has `--help`. Start with
[AGENTS.md](AGENTS.md), [skills](skills/), and [knowledge](knowledge/README.md).

## Stateless image inspection

Explicit `--backend local` inspection sends only whole-image previews and a short task to an
already-running local vision endpoint, with no agent session, tools, skills or
conversation history. Native image generation uses a fresh isolated Codex session
and independent isolated OpenAI review. Non-image analysis uses local tools;
`um context analyze` is disabled.

```bash
um context check
um context inspect --backend local --question "Are both eyes visible and attached?" --criteria "No missing features; state uncertainty" render.png
um context capture --output outputs/check.log --compress -- pytest -q tests
```

Configure the loopback endpoint/model in private
`~/.config/disposable-vision/local.json`. Optional 9router authentication points
to a separate private key file; credentials never belong in the repository.
The bundled inspection default honors the project’s requested OpenAI provider.
Local inspection fails closed if the endpoint is unavailable. A cloud image-review
escalation must be explicitly selected; there is no silent fallback.
See [the vision guide](docs/disposable-vision.md) and the bundled skill.

## Development

Edit `skills/`, then sync the matching `.agents/skills/` and `.claude/skills/` copies.

```bash
uv run --with pytest pytest -q tests
./bin/um kb check --index
./bin/um publish check .
```

Offline tests cover the added CLI routes and mocked image provider; they do not
prove live provider availability, visual quality, or GPU compatibility. Generation
manifests, logs, credentials and local configuration stay private. Audit history
and artifacts before publishing. See [LICENSE](LICENSE) and [CONTRIBUTING.md](CONTRIBUTING.md).
