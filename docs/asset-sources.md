# Asset sources in this fork

These routes preserve the customized project's added sources without shipping
its machine configuration, model weights, private wiki archive, or credentials.

| Route | Included integration | Requirements |
| --- | --- | --- |
| FLUX.2 Klein | `um comfy flux`; `um/workflows/flux2-klein.json` | ComfyUI, GGUF loader, compatible local models |
| FLUX.1-dev | `um/workflows/flux1-dev-gguf-api.json` | GGUF loader, matching diffusion model, CLIP/T5 and VAE |
| MiniMax H3 video/audio | `um/workflows/minimax-h3-t2v-gguf-4step-api.json` | Compatible H3 nodes, GGUF models, text encoder and both VAEs |
| Agent-native images | `um context generate` | Authenticated Codex CLI; fresh generation and review workers |
| Vertex Gemini images | `um image vertex` | Explicit cloud project, local ADC, model access and paid-call approval |
| ambientCG / Poly Haven | `tools/cc0_materials.py` | Internet access; fetch only selected materials |

From a clone, run the included API graphs with the existing workflow runner:

```bash
um comfy run um/workflows/flux1-dev-gguf-api.json --set 4.text="a mossy wall" --name wall
um comfy run um/workflows/minimax-h3-t2v-gguf-4step-api.json --name clip
python3 tools/cc0_materials.py ambientcg search "stone" --limit 5
python3 tools/cc0_materials.py polyhaven search "wood" --limit 5
```

Inspect each graph before running. Replace model filename inputs using
`--set NODE.INPUT=value` to match your own installation; node IDs are specific
to each graph. No weights are installed or downloaded automatically. The CLI
saves output media and local provenance manifests. Keep manifests private until
reviewed, since prompts and local paths can contain personal information.

Material source links: [ambientCG](https://ambientcg.com/) and
[Powered by Poly Haven](https://polyhaven.com/). Check source terms, API usage rules,
and model licenses before distributing generated or downloaded assets.

Other researched routes (ACE-Step, ElevenLabs, TRELLIS.2, Hunyuan3D, Tripo,
DiffSynth ControlNet, CHORD, Meshy and rigging tools) are not newly implemented CLI
providers in this fork. Use compatible installed tools/workflows and their own
setup documentation; do not imply their weights or services are bundled.

Use a disposable worker to inspect saved images; do not return image payloads
into the parent session. A successful provider request is not visual acceptance.
