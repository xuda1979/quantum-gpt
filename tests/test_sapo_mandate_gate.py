"""Unit tests for scripts/sapo_mandate_gate.py (mandates 2026-09-22/23).

M1 dp4-only judge, M2 <=200-line files, M3 changed files need tests.
Each check is tested against synthetic fixtures (no repo-wide state needed).
"""
import importlib.util
import os
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(REPO, "scripts", "sapo_mandate_gate.py")


def _load(tmp_repo):
    """Load the gate with REPO monkeypatched to a temp dir."""
    spec = importlib.util.spec_from_file_location("gate_under_test", GATE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.REPO = tmp_repo
    return mod


def _mk_repo():
    tmp = tempfile.mkdtemp(prefix="mandate_gate_test_")
    os.makedirs(os.path.join(tmp, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(tmp, "harness"), exist_ok=True)
    return tmp


class TestM1Dp4OnlyJudge:
    def test_zhipu_call_in_source_is_flagged(self):
        tmp = _mk_repo()
        with open(os.path.join(tmp, "scripts", "w.py"), "w") as fh:
            fh.write("resp = call_zhipu_fallback(body)\n")
        mod = _load(tmp)
        bad = mod.check_dp4_only_judge()
        assert any("non-dp4 judge" in b for b in bad)

    def test_fail_closed_stub_is_allowed(self):
        tmp = _mk_repo()
        with open(os.path.join(tmp, "scripts", "w.py"), "w") as fh:
            fh.write(
                'return {"error": {"message": "zhipu judge fallback removed: '
                'dp4 is the only judge", "type": "judge_policy"}}\n'
            )
        mod = _load(tmp)
        assert mod.check_dp4_only_judge() == []

    def test_clean_file_passes(self):
        tmp = _mk_repo()
        with open(os.path.join(tmp, "scripts", "w.py"), "w") as fh:
            fh.write("resp = call_dp4(body)\n")
        mod = _load(tmp)
        assert mod.check_dp4_only_judge() == []


class TestM2LineLimit:
    def test_over_limit_flagged(self):
        tmp = _mk_repo()
        with open(os.path.join(tmp, "scripts", "big.py"), "w") as fh:
            fh.write("\n" * 201)
        mod = _load(tmp)
        bad = mod.check_line_limits()
        assert any("big.py" in b and "201" in b for b in bad)

    def test_at_limit_passes(self):
        tmp = _mk_repo()
        with open(os.path.join(tmp, "scripts", "ok.py"), "w") as fh:
            fh.write("\n" * 200)
        mod = _load(tmp)
        assert mod.check_line_limits() == []

    def test_bak_and_pycache_excluded(self):
        tmp = _mk_repo()
        os.makedirs(os.path.join(tmp, "scripts", "__pycache__"), exist_ok=True)
        with open(os.path.join(tmp, "scripts", "__pycache__", "x.py"), "w") as fh:
            fh.write("\n" * 300)
        with open(os.path.join(tmp, "scripts", "x.py.bak-20260101"), "w") as fh:
            fh.write("\n" * 300)
        mod = _load(tmp)
        assert mod.check_line_limits() == []


class TestM3ChangedFilesTested:
    def test_changed_file_without_test_reference_reported(self, tmp_path, monkeypatch):
        tmp = _mk_repo()
        mod = _load(tmp)
        # point git at the real repo but claim a synthetic changed file
        monkeypatch.setattr(mod, "_git",
                            lambda name, *a: type("R", (), {
                                "returncode": 0,
                                "stdout": " M scripts/nonexistent_thing.py\n"})())
        bad = mod.check_changed_files_have_tests()
        assert any("nonexistent_thing.py" in b for b in bad)

    def test_no_changes_is_clean(self, monkeypatch):
        tmp = _mk_repo()
        mod = _load(tmp)
        monkeypatch.setattr(mod, "_git",
                            lambda name, *a: type("R", (), {
                                "returncode": 0, "stdout": ""})())
        assert mod.check_changed_files_have_tests() == []
