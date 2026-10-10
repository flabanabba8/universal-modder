"""Generate game art with Gemini on Vertex AI (no FAL or OpenAI API).

    um image vertex "a mossy dungeon wall" --out assets/gen/wall.png
    um image vertex "same character, walking" --ref idle.png --out walk.png

Vertex uses GOOGLE_CLOUD_PROJECT,
GOOGLE_CLOUD_LOCATION (default global), and gcloud auth application-default print-access-token.
Default model: gemini-3-pro-image (Nano Banana Pro); gemini-3.1-flash-image (Nano Banana 2) is the cheaper option.
Select a model with --model or UM_VERTEX_IMAGE_MODEL; --aspect sets imageConfig.aspectRatio (e.g. 1:1, 16:9, 9:16).
"""
from __future__ import annotations

import base64
import io
import json
import mimetypes
import os
from pathlib import Path
import re
import subprocess
import urllib.error
import urllib.request

from PIL import Image
from um.common import die


def request(url, token, body, content_type="application/json"):
    data = json.dumps(body).encode() if isinstance(body, dict) else body
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {token}", "Content-Type": content_type,
    })
    try:
        with urllib.request.urlopen(req, timeout=600) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        # Response bodies may echo prompts, private project IDs or credentials.
        die(f"image provider returned HTTP {exc.code}; check authentication, model access and quota")
    except urllib.error.URLError:
        die("cannot reach the image provider; check network access")


def generate(a):
    output = Path(a.out)
    if output.exists():
        die("output already exists; choose another --out path")
    prompt = a.prompt
    if a.sprite:
        prompt += ". Single game sprite, centered, no text, no shadow, on a plain flat white background."
    if a.ref and not Path(a.ref).is_file():
        die("reference image does not exist")
    config_path = Path.home() / ".config/universal-modder/config.json"
    config = json.loads(config_path.read_text()) if config_path.is_file() else {}
    project = os.environ.get("GOOGLE_CLOUD_PROJECT") or config.get("vertex_project")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION") or config.get("vertex_location", "global")
    model = a.model or os.environ.get("UM_VERTEX_IMAGE_MODEL") or config.get("vertex_model", "gemini-3-pro-image")
    if not project:
        die("set GOOGLE_CLOUD_PROJECT locally to use Vertex image generation")
    if not all(re.fullmatch(r"[A-Za-z0-9._-]+", value) for value in (project, location, model)):
        die("invalid project, location or model identifier")
    try:
        auth = subprocess.run(["gcloud", "auth", "application-default", "print-access-token"], capture_output=True, text=True, timeout=60)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        die("install gcloud and authenticate locally for Vertex")
    if auth.returncode or not auth.stdout.strip():
        die("gcloud authentication failed; run gcloud auth application-default login locally")
    host = "aiplatform.googleapis.com" if location == "global" else f"{location}-aiplatform.googleapis.com"
    url = f"https://{host}/v1/projects/{project}/locations/{location}/publishers/google/models/{model}:generateContent"
    parts = [{"text": prompt}]
    if a.ref:
        path = Path(a.ref)
        parts.append({"inlineData": {"mimeType": mimetypes.guess_type(path.name)[0] or "image/png", "data": base64.b64encode(path.read_bytes()).decode()}})
    generation_config = {"responseModalities": ["TEXT", "IMAGE"]}
    if a.aspect:
        if not re.fullmatch(r"\d{1,2}:\d{1,2}", a.aspect):
            die("invalid --aspect; use W:H such as 16:9")
        generation_config["imageConfig"] = {"aspectRatio": a.aspect}
    response = request(url, auth.stdout.strip(), {"contents": [{"role": "user", "parts": parts}], "generationConfig": generation_config})
    encoded = next((part["inlineData"].get("data") for candidate in response.get("candidates", []) for part in candidate.get("content", {}).get("parts", []) if part.get("inlineData", {}).get("mimeType", "").startswith("image/")), None)
    if not encoded:
        die("provider returned no image; the request may have been filtered")
    try:
        im = Image.open(io.BytesIO(base64.b64decode(encoded, validate=True))).convert("RGBA")
        im.load()
    except (ValueError, OSError):
        die("provider returned invalid image data")
    if a.sprite:
        from um.sprite import cutout
        im = cutout(im)
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents accidental overwrites even during concurrent runs.
    with output.open("xb") as fh:
        im.save(fh, format="PNG")
    with (output.parent / "image_manifest.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(dict(provider=a.provider, model=model, prompt=prompt, ref=a.ref, file=str(output))) + "\n")
    print(output)


def register(sub):
    p = sub.add_parser("image", help="Vertex image generation, no FAL or OpenAI API", description=__doc__)
    providers = p.add_subparsers(dest="provider")
    q = providers.add_parser("vertex")
    q.add_argument("prompt")
    q.add_argument("--out", required=True, help="new PNG output path")
    q.add_argument("--model")
    q.add_argument("--ref", help="reference image for edits")
    q.add_argument("--aspect", help="aspect ratio such as 1:1, 16:9, 9:16")
    q.add_argument("--sprite", action="store_true")
    q.set_defaults(func=generate)
