"""Bounded context helpers: capture, analyze, inspect, generate, and check.

Examples:
  um context capture --output outputs/test.log --compress -- pytest -q
  um context analyze --kind logs --question "What failed?" outputs/test.log.gz
  um context analyze --kind code --root . --pattern "load_save" --question "Trace save loading"
  um context inspect --question "Any clipping?" screenshot.jpg

Large outputs stay on disk. Model work uses a fresh authenticated Codex session.
"""
from pathlib import Path
import subprocess
import sys


def execute(args):
    if sys.version_info < (3, 11):
        raise SystemExit('um context requires Python 3.11+; other um commands still support 3.10')
    local = Path(__file__).resolve().parents[1] / 'skills'
    root = local if (local / 'disposable-tasks').exists() else Path(__file__).parent / 'bundled_skills'
    action = args.context_action
    scripts = {'inspect': ('disposable-vision', 'vision_inspect.py'),
               'generate': ('disposable-vision', 'image_reference_generate.py'),
               'check': ('disposable-vision', 'check_environment.py')}
    name, script = scripts.get(action, ('disposable-tasks', 'task.py'))
    command = [sys.executable, str(root / name / 'scripts' / script)]
    if action not in scripts: command.append(action)
    command.extend(args.arguments)
    raise SystemExit(subprocess.run(command).returncode)


def register(sub):
    parser = sub.add_parser('context', description=__doc__)
    parser.add_argument('context_action', choices=['capture', 'analyze', 'inspect', 'generate', 'check'])
    parser.add_argument('arguments', nargs='...')
    parser.set_defaults(func=execute)
