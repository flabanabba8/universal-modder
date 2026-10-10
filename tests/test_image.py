"""Offline checks for the direct Vertex route; no cloud calls or credentials."""
import base64
import io
import json
from types import SimpleNamespace

import pytest
from PIL import Image
from um import image


def test_vertex_edit_saves_png_without_logging_auth(tmp_path, monkeypatch):
    buf = io.BytesIO()
    Image.new('RGB', (8, 8), 'blue').save(buf, format='JPEG')
    reference = tmp_path / 'ref.png'
    Image.new('RGB', (8, 8), 'white').save(reference)
    monkeypatch.setenv('GOOGLE_CLOUD_PROJECT', 'test-project')
    monkeypatch.setattr(image.subprocess, 'run', lambda cmd, **kw: SimpleNamespace(returncode=0, stdout='test-access-token'))
    requests = []
    def fake_request(url, token, body):
        requests.append((url, token, body))
        return {'candidates': [{'content': {'parts': [{'inlineData': {'mimeType': 'image/jpeg', 'data': base64.b64encode(buf.getvalue()).decode()}}]}}]}
    monkeypatch.setattr(image, 'request', fake_request)
    output = tmp_path / 'result.png'
    args = SimpleNamespace(out=str(output), prompt='potion', sprite=False, ref=str(reference), model='test-model', provider='vertex', aspect=None)
    image.generate(args)
    assert Image.open(output).format == 'PNG'
    assert Image.open(output).mode == 'RGBA'
    assert requests[0][2]['contents'][0]['parts'][1]['inlineData']['mimeType'] == 'image/png'
    manifest = (tmp_path / 'image_manifest.jsonl').read_text()
    assert 'test-access-token' not in manifest and 'test-project' not in manifest
    assert json.loads(manifest)['model'] == 'test-model'
    with pytest.raises(SystemExit):
        image.generate(args)
    assert len(requests) == 1  # never pay for a request that would overwrite an existing output


def test_vertex_filtered_response_creates_no_output(tmp_path, monkeypatch):
    monkeypatch.setenv('GOOGLE_CLOUD_PROJECT', 'test-project')
    monkeypatch.setattr(image.subprocess, 'run', lambda *a, **kw: SimpleNamespace(returncode=0, stdout='test-access-token'))
    monkeypatch.setattr(image, 'request', lambda *a: {'candidates': []})
    output = tmp_path / 'result.png'
    with pytest.raises(SystemExit):
        image.generate(SimpleNamespace(out=str(output), prompt='potion', sprite=False, ref=None, model="test-model", provider="vertex", aspect=None))
    assert not output.exists()
