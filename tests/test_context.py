from argparse import Namespace
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch
import pytest
from um import context


def test_cli_forwards_capture_arguments_and_exit_status():
    with patch.object(context.subprocess, 'run', return_value=subprocess.CompletedProcess([], 3)) as run:
        with pytest.raises(SystemExit) as exc:
            context.execute(Namespace(context_action='capture', arguments=['--output','test.log','--','false']))
    assert exc.value.code == 3
    command = run.call_args.args[0]
    assert command[0] == sys.executable and Path(command[1]).exists()
    assert command[2:] == ['capture','--output','test.log','--','false']


def test_cli_routes_inspection_to_vision_worker():
    with patch.object(context.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)) as run:
        with pytest.raises(SystemExit):
            context.execute(Namespace(context_action='inspect', arguments=['--question','Check','image.png']))
    assert Path(run.call_args.args[0][1]).name == 'vision_inspect.py'
