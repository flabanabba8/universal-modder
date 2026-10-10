"""Local log capture and image-only disposable workers.

  um context capture --output outputs/test.log --compress -- pytest -q
  um context inspect --question "Any clipping?" screenshot.jpg
  um context generate new.png --prompt "A potion icon" --criteria "One bottle"

Code, logs, documents and data use local tools; non-vision workers are disabled.
"""
import argparse
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time


def capture(arguments):
    parser = argparse.ArgumentParser(prog="um context capture")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--compress", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(arguments)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("Pass a local command after --")
    output = Path(str(args.output) + ".gz") if args.compress else args.output
    if output.exists():
        raise SystemExit("Choose a new log path")
    output.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    with tempfile.TemporaryFile() as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
        original_bytes = log.tell()
        log.seek(0)
        with (gzip.open(output, "xb") if args.compress else output.open("xb")) as saved:
            shutil.copyfileobj(log, saved)
    print(json.dumps({"exit_code": result.returncode, "log": str(output),
                      "original_bytes": original_bytes, "stored_bytes": output.stat().st_size,
                      "elapsed_seconds": round(time.monotonic()-start, 3)}))
    raise SystemExit(result.returncode)


def execute(args):
    action = args.context_action
    if action == "capture":
        capture(args.arguments)
    if action == "analyze":
        raise SystemExit("Non-vision disposable workers are disabled; use local tools for code, logs, documents and data")
    scripts = {"inspect": "vision_inspect.py", "generate": "image_reference_generate.py",
               "check": "check_environment.py"}
    if action not in scripts:
        raise SystemExit("Unknown context action")
    if sys.version_info < (3, 11):
        raise SystemExit("Image workers require Python 3.11+")
    local = Path(__file__).resolve().parents[1] / "skills/disposable-vision"
    root = local if local.exists() else Path(__file__).parent / "bundled_skills/disposable-vision"
    command = [sys.executable, str(root / "scripts" / scripts[action]), *args.arguments]
    raise SystemExit(subprocess.run(command).returncode)


def register(sub):
    parser = sub.add_parser("context", description=__doc__)
    parser.add_argument("context_action", choices=["capture", "inspect", "generate", "check", "analyze"],
                        help="analyze is retained only to explain that non-vision workers are disabled")
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    parser.set_defaults(func=execute)
