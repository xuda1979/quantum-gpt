"""Tests for S3 data path — dataset/artifact flow off the browser channel."""

import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def run_py(code: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=15, cwd=str(REPO)
    )


def test_s3_path_module_exists():
    assert (REPO / "harness" / "scripts" / "s3_data_path.py").exists()


def test_versioned_key():
    r = run_py("""
import sys
sys.path.insert(0, 'harness/scripts')
from s3_data_path import versioned_key
k = versioned_key('datasets/train_v9.jsonl', b'hello')
assert k.startswith('artifacts/datasets/train_v9.jsonl-'), k
assert '2cf24dba5fb0a30e' in k, k
print('OK')
""")
    assert r.returncode == 0, r.stderr
    assert "OK" in r.stdout


def test_atomic_plan():
    """Transfer plan uses tmp key + rename. Atomic."""
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        f.write(b"data")
        local = f.name
    try:
        r = run_py(f"""
import sys
sys.path.insert(0, 'harness/scripts')
from s3_data_path import transfer_plan
plan = transfer_plan({local!r}, 'datasets', 'ASI3')
assert plan['local'] == {local!r}
assert plan['remote_tmp'].startswith('artifacts/'), plan['remote_tmp']
assert plan['remote_tmp'].endswith('.tmp'), plan['remote_tmp']
assert plan['remote_final'] != plan['remote_tmp']
assert 'moveto' in str(plan['steps']) or 'rename' in str(plan['steps'])
assert plan['manifest']['name'] == {Path(local).name!r}
print('OK')
""")
        assert r.returncode == 0, r.stderr
        assert "OK" in r.stdout
    finally:
        Path(local).unlink(missing_ok=True)


def test_manifest_roundtrip():
    r = run_py("""
import sys
sys.path.insert(0, 'harness/scripts')
from s3_data_path import build_manifest
m = build_manifest('train_v9.jsonl', b'data', source='local', dest='ASI3')
assert m['name'] == 'train_v9.jsonl'
assert len(m['sha256']) == 64
assert m['size'] == 4
assert m['s3_key'].startswith('artifacts/train_v9.jsonl-')
assert m['source'] == 'local' and m['dest'] == 'ASI3'
print('OK')
""")
    assert r.returncode == 0, r.stderr
    assert "OK" in r.stdout
