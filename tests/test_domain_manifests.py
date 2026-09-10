"""TDD: every domain-monitor manifest must reference REAL, existing task ids
(goldens: the id must exist in evals/tasks/* OR a benchmarks txt), so the
industrial-standard monitor never measures hallucinated benchmarks."""
import json, glob, os
from pathlib import Path
import pytest

DOMAINS = ["math", "coding", "physics"]
MANIFEST_DIR = Path("evals/domain_monitor/domains")


@pytest.fixture(scope="module")
def real_tasks():
    ids = set()
    for d in glob.glob("evals/tasks/*"):
        for t in os.listdir(d):
            if os.path.isdir(os.path.join(d, t)):
                ids.add(t)
    for f in glob.glob("evals/benchmarks/*.txt"):
        for line in open(f):
            line = line.strip()
            if line and not line.startswith("#"):
                ids.add(line.split("\t")[0].split(" ")[0].strip())
    return ids


def test_each_domain_manifest_has_tasks():
    for dom in DOMAINS:
        p = MANIFEST_DIR / dom / "manifest.json"
        assert p.exists(), f"missing {p}"
        m = json.loads(p.read_text())
        assert isinstance(m["task_ids"], list) and len(m["task_ids"]) >= 5, dom


def test_all_manifest_ids_are_grounded(real_tasks):
    for dom in DOMAINS:
        m = json.loads((MANIFEST_DIR / dom / "manifest.json").read_text())
        missing = [t for t in m["task_ids"] if t not in real_tasks]
        assert not missing, f"{dom}: ungrounded ids {missing}"


def test_manifests_non_identical():
    """Three domains should target meaningfully different task sets."""
    sets = []
    for dom in DOMAINS:
        m = json.loads((MANIFEST_DIR / dom / "manifest.json").read_text())
        sets.append(set(m["task_ids"]))
    # not all three identical
    assert not (sets[0] == sets[1] == sets[2])
