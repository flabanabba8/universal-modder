# Isolated image operations

Only image operations may use disposable AI work. Code, logs, data, documents,
research and reviews use ordinary local tools. `um context capture` saves local
command output and exit status; `um context analyze` is disabled.

## Inspect

```bash
um context inspect --backend local --question "Are the features visible and attached?" --criteria "No missing parts; state limitations" render.png
```

The explicit local backend is a stateless request to a warm local vision endpoint: two messages,
no tools/skills/history and a bounded output. Supply one to four whole images,
not a parent transcript. Exact alpha, dimensions, masks, hashes and pixel equality
are measured locally; JPEG previews cannot prove them. Validate representative
evidence before scaling a task. Re-review only when relevant inputs change.

The private endpoint/model configuration lives outside the repo in
~/.config/disposable-vision/local.json. A 9router key, when needed, is read from
its separate private file and sent only to the configured loopback endpoint.
Unavailable service, truncation or invalid verdict fails closed; no remote
fallback. Report-cache hits skip inference. The bundled project default is Codex to honor
its requested OpenAI provider; choose `--backend local` for permitted local tasks.
Codex has agent startup overhead and is never an automatic local failure fallback.

## Generate

```bash
um context generate assets/gen/new-art.png --prompt "Specific image task" --criteria "Visible requirements" --reference reference.png
```

Native generation launches a fresh isolated Codex session using the existing
login, then independent isolated OpenAI image review. PASS requires all stated criteria; FAIL and
UNCERTAIN remain drafts. No verdict authorizes overwriting, installing or
publishing assets. Start with one representative transformation, not a large
family of unvalidated drafts.

Keep image payloads/base64/previews out of the coordinator. Return only text,
verdicts and paths. Temporary data is removed; local cache and numeric metrics
remain private. Ephemeral agents do not guarantee zero server retention.

## Measure

Metrics record reported input/cache/output usage when supplied, elapsed time,
image counts and cache status. Counts from different tokenizers are not a bill.
Agent-session input includes harness/context; local requests use a short prompt.
Do not infer token savings from isolation alone or exact request bytes from
host-wide traffic counters. A narrow OCR benchmark does not prove equivalence
on complex rigging judgments.
