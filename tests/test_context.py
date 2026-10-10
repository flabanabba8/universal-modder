from argparse import Namespace
import gzip
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch
import pytest
from um import context


def test_local_capture_preserves_log_and_exit_status(tmp_path, capsys):
    out = tmp_path / "check.log"
    command = [sys.executable, "-c", "import sys; print('local-output'); sys.exit(3)"]
    with pytest.raises(SystemExit) as error:
        context.execute(Namespace(context_action="capture", arguments=["--output",str(out),"--compress","--",*command]))
    assert error.value.code == 3
    report = json.loads(capsys.readouterr().out)
    assert report["exit_code"] == 3
    assert gzip.open(report["log"], "rt").read() == "local-output\n"


def test_capture_refuses_to_overwrite_existing_log(tmp_path):
    out=tmp_path/"existing.log";out.write_text("preserve")
    with patch.object(context.subprocess,"run") as run:
        with pytest.raises(SystemExit,match="new log path"):
            context.execute(Namespace(context_action="capture",arguments=["--output",str(out),"--","false"]))
        run.assert_not_called()
    assert out.read_text()=="preserve"


def test_nonvision_analysis_never_launches_a_worker():
    with patch.object(context.subprocess,"run") as run:
        with pytest.raises(SystemExit,match="Non-vision disposable workers are disabled"):
            context.execute(Namespace(context_action="analyze",arguments=["--kind","code","--question","Review"]))
        run.assert_not_called()


@pytest.mark.parametrize("action,script",[("inspect","vision_inspect.py"),("generate","image_reference_generate.py"),("check","check_environment.py")])
def test_only_image_actions_reach_bundled_scripts(action,script):
    with patch.object(context.subprocess,"run",return_value=subprocess.CompletedProcess([],0)) as run:
        with pytest.raises(SystemExit):
            context.execute(Namespace(context_action=action,arguments=["--help"]))
    assert Path(run.call_args.args[0][1]).name==script
    assert Path(run.call_args.args[0][1]).exists()
