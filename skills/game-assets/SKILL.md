---
name: game-assets
description: Generate game sprites, icons, concepts and textures using existing local Flux models or Vertex, then prepare them with Universal Modder. Use when a game mod needs generated art.
---

# Game assets

Use existing local Flux on a compatible GPU or Gemini image generation through Vertex.
Never use FAL or the OpenAI API. OpenAI images must go through an available agent image-generation tool using agent authentication. In Codex use its image tool; in Hermes its native image tool is configured for openai-codex OAuth. If Claude Code has no image tool, use Flux or Vertex. Do not invent an OpenAI API fallback.
Never download models without first proposing the model, purpose, size and license in normal chat and receiving explicit approval.

## Existing local Flux

Configure a local ComfyUI installation with compatible Flux models, encoders and VAEs.
Check `um comfy status`. If offline, start your configured backend on loopback. Do not stop other GPU jobs to make room without checking with the user.

```bash
um comfy flux "a blue potion bottle, side view, game icon" --sprite --name potion
um comfy flux "mossy dungeon wall texture" --size 1024x1024 --seed 42 --name wall
```

`flux` uses the existing Flux 2 Klein concept workflow with its installed GGUF model, Qwen encoder and VAE. The upstream `um comfy image` command assumes SD checkpoints; use `flux` here. For reference images, LoRAs, Flux 1, video or 3D, use an existing compatible ComfyUI workflow exported in API format via `um comfy run workflow.json --set NODE.INPUT=value`. An installed model does not guarantee a compatible workflow.

## Vertex with Google application-default credentials

Choose a provider according to the user’s instructions. Native OpenAI image tools use agent authentication; Vertex requires user-configured Google credentials and may incur charges.

```bash
um image vertex "a blue potion bottle, side view, game icon" --sprite --out assets/gen/potion.png
um image vertex "same potion, red liquid" --ref assets/gen/potion.png --out assets/gen/red-potion.png
```

The CLI refreshes user-configured Google ADC with gcloud. Private configuration is `~/.config/universal-modder/config.json`; do not print or commit it. `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `UM_VERTEX_IMAGE_MODEL`, and `--model` can override settings. No pairing secret or broker token is needed. Calls use Vertex directly and may incur the project's normal image-generation charges.

## Output

Review generated art, then use **asset-pipeline** to cut out, fit, pixelate or pack frames. Flux `--sprite` saves both the original and a local cutout; Vertex `--sprite` cuts out the flat background. Inspect alpha edges. Use reference-image editing for consistent variants. For 3D/audio/video, use suitable existing local tools or workflows; these image commands do not replace those capabilities.
Keep generation manifests locally for provenance. Before publication audit manifests as well as source and artifacts for secrets and personal deployment settings. Credit the actual provider and models.
