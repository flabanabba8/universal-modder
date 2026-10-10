---
name: disposable-vision
description: Inspects images and generates GPT-Image art in disposable sessions, returning only text and file paths. Use when reviewing screenshots, sprites, diagrams or visual defects, or creating art with optional image references, while keeping image payloads out of the main conversation.
---

# Disposable image inspection and generation

Project default: use this workflow for all image inspection and generation in main/coordinator sessions without requiring an explicit invocation. Disposable workers execute their assigned task directly and must not recursively invoke this skill.

<what-to-do>

1. Run `python3 SKILL_DIR/scripts/check_environment.py` once in a new environment. It checks prerequisites and CLI support without a model request; readiness is not proof of successful image generation. Locate this skill's directory from the loaded skill path. Use its bundled `scripts/` from any project; do not copy image data into the parent context. All three host agents (Codex, Claude Code, Hermes) run the same disposable **Codex CLI** workers using the existing Codex login. This is not a native Claude/Hermes image-generation API.
2. Select inspection or generation below. Give the worker a specific task, relevant files, and acceptance criteria. Never send the parent transcript or resume a previous image worker. Workers disable host skill discovery to prevent recursive delegation back into this skill.
3. Read only the returned text/JSON and referenced text reviews. Do not open images with the main agent's image-viewing tool, return base64, or render the generated file into the parent conversation. A path is sufficient for subsequent file processing or another disposable inspection.
4. For generation, PASS means the independent reviewer found the criteria visibly satisfied. FAIL and UNCERTAIN are unaccepted drafts; read the review before choosing a targeted correction. Do not automatically regenerate in a loop. A verdict does not authorize installation, publication, or overwriting an existing asset.

## Inspection

Use the Python interpreter with Pillow installed (in this kit, `.venv/bin/python`). Substitute it for `python3` below, and replace `SKILL_DIR` with the actual path to this skill:

```bash
python3 SKILL_DIR/scripts/vision_inspect.py \
  --question 'Are the sprite edges clean?' \
  --criteria 'No visible halos, clipping, or missing limbs' \
  /absolute/path/to/sprite.png
```

- One to four images per job, whole-image JPEG previews of at most 50 KB each. For pixel-level detail or alpha-channel assessment, prepare a crop or suitable checkerboard preview on disk and send it to the worker. Preview images flatten transparency; do not infer exact alpha values from them.
- Returns a bounded text report of findings, uncertainty, and recommended action.
- Reports are cached by ordered image contents/names, question, criteria, model, and worker/preview code. Use `--refresh` for a new opinion. Changing an input invalidates the cache.
- `--model` optionally selects the Codex coordinator; otherwise the user's Codex model is used. `--timeout` defaults to 120 seconds. Do not pass conversation history as a question.

## Generation with optional references

```bash
python3 SKILL_DIR/scripts/image_reference_generate.py /absolute/path/to/new-art.png \
  --prompt 'Create a potion icon matching the supplied reference style' \
  --criteria 'One blue bottle, centered, no lettering' \
  --reference /absolute/path/to/style.png
```

- Omit `--reference` when no reference is needed. Up to four originals, at most 4 MB each and 8 MB combined. Their detail and transparency are preserved. The output must be a new PNG path.
- Uses the native GPT-Image tool through Codex's existing login, not API-key image endpoints. `--model` selects the coordinator, not the underlying image model. Generation timeout defaults to 300 seconds.
- A fresh inspection worker reviews the generated image against the criteria and supplied references. Larger reference sets are reviewed in bounded batches. Review failure produces UNCERTAIN, never automatic acceptance.
- Returns JSON containing `image`, `review`, and `verdict`. The sibling `.review.json` contains the evidence. Generated images remain on disk even if review fails, so the work is not lost.

## Review rubric

- **PASS:** every stated criterion is visibly satisfied by the inspected preview.
- **FAIL:** at least one criterion has a visible violation.
- **UNCERTAIN:** any required detail is unresolved, or the review could not finish. Obtain better evidence before acceptance; a low-resolution preview is not pixel-perfect verification.

</what-to-do>

<supporting-info>

Requires Python 3.11+, Pillow, and a logged-in Codex CLI on PATH. Verified with Codex 0.162.0. If missing, report the missing prerequisite; do not substitute a paid provider or fetch credentials. Worker commands suppress raw transcripts and clean up temporary attachments. `--ephemeral` prevents normal local session persistence; it is not a promise of zero server retention or removal of Codex's generated-image cache.

State defaults to `$XDG_CACHE_HOME/disposable-vision` (or `~/.cache/disposable-vision`). `VISION_WORKER_STATE` overrides it. Reports and numeric metrics persist there; prompts and image payloads are not recorded in metrics. Worker images exist only in temporary directories except for generated artifacts.

```bash
python3 SKILL_DIR/scripts/vision_metrics.py              # recent worker metrics
python3 SKILL_DIR/scripts/vision_metrics.py --seconds 60 # traffic and internet RTT during a slowdown
python3 -m unittest discover -s SKILL_DIR/tests -q       # offline checks
```

Traffic counters include other applications. Attachment bytes are not exact network request sizes; neither metrics nor session-log sizes prove context re-upload or router bufferbloat.

This skill guides tool use; installing it does not disable native image tools globally. The kit routes image work through disposable workers in its shared project instructions. Keep each worker's stdout text-only when invoking from Claude Code or Hermes, just as from Codex.

</supporting-info>
