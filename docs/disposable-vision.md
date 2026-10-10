# Disposable agents for vision tasks

The bundled workers isolate image-heavy work from the coordinator's context.
Use them for every screenshot, sprite, diagram, reference-image and generated-art
review, regardless of which provider created the image. They launch fresh,
ephemeral Codex sessions using the existing local login. No parent conversation
is supplied, and workers are never resumed.

## Check readiness

```bash
um context check
```

Requires Python 3.11+, Pillow and an authenticated, compatible Codex CLI. The check
reports readiness without uploading images or making a model request. Credentials
stay local. Fix a failed prerequisite rather than switching to coordinator vision.

## Inspect existing images

```bash
um context inspect --question "Are the sprite edges clean?" --criteria "No halos, clipped parts or stray marks" sprite.png
um context inspect --question "Does the render preserve the reference design?" --criteria "Matching proportions and color" render.png reference.png
```

Each job accepts one to four image paths and creates whole-image JPEG previews
of at most 50 KB each. Output is a bounded text report: visible findings,
uncertainty and recommended action. Give a specific task and acceptance criteria,
not conversation history. Cache hits reuse an identical review; `--refresh`
requests a fresh opinion. For fine details or alpha edges, prepare a close crop or
checkerboard preview on disk, then pass it to another fresh inspection worker.
Compressed previews do not prove exact alpha values or pixel-perfect quality.

Save game/UI screenshots with the authorized automation tool. Send their paths
to an inspection worker and use its text findings for the next action. The worker
does not drive the desktop. Images produced by `um comfy` and `um image vertex`
use this same inspection path; those providers do not require coordinator vision.

## Generate and independently review

```bash
um context generate assets/gen/new-potion.png --prompt "A blue potion icon, side view" --criteria "One bottle, centered, no text"
um context generate assets/gen/red-potion.png --prompt "Match this potion design, with red liquid" --criteria "Same silhouette, red liquid, no text" --reference assets/gen/new-potion.png
```

The generator invokes the native image tool within its disposable session. A
separate fresh inspector reviews the result against the task and references.
The command returns JSON containing image/review paths and a verdict; read the
review text rather than opening or embedding its image in the coordinator.

- PASS: all stated criteria are visibly satisfied.
- FAIL: at least one criterion has a visible violation; the image is a draft.
- UNCERTAIN: a criterion is unresolved or review failed; obtain better evidence.

Generation takes a new PNG output path. Up to four reference originals are
supported, at most 4 MB each and 8 MB total. Existing assets are not overwritten.
A review verdict does not authorize installation or publication. Do not regenerate
automatically in a loop: use the evidence to choose a focused correction.

## Worker boundaries and failures

Return text findings, review verdicts and artifact paths only. Never copy images,
base64, generated previews or image-heavy transcripts into the coordinator.
Workers perform their narrow assignment directly and do not recursively delegate.
Timeout/authentication failures require repairing the worker path; do not fall
back to the coordinator's image tools. `--model` selects the worker coordinator
model, not the image model. Inspection defaults to 120 seconds and generation to
300 seconds; the CLI exposes `--timeout` for the specific job.

Temporary attachments/transcripts are removed; generated files, bounded reviews
and numeric metrics remain locally. Ephemeral sessions do not guarantee zero
server retention or removal of the native generated-image cache. Audit generated
artifacts and reports before sharing them publicly.
