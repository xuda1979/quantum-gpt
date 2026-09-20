"""C-9079: SDK pin single-source-of-truth (qiskit / cirq / pennylane).

Contract under test (card C-9079):
  1. harness/state/sdk_pin_table.json is the CANONICAL pin table and
     inventories every qiskit/cirq/pennylane pin source in the repo
     (authority requirements file, corpus runnable list, cure package,
     graded-env measurements, box inventory).
  2. Every ACTIVE source's per-package range must be consistent with the
     authority ranges (requirements-cpu-eval.txt) AND must contain every
     graded-env measured version it covers -- a cure/eval pin that
     excludes the graded version (C-9066 V2: qiskit>=1.0,<2.0 vs 2.4.1)
     is a cross-file contradiction.
  3. A graded-env measured version OUTSIDE an authority range
     (C-9066 V1: cirq 1.3.0 vs >=1.4) must be carried fail-closed as a
     declared_violations entry -- never silently reconciled away.
  4. The old C-9066 cure (step2_install in the frozen verdict probe) is
     BLOCKED in the table with a reason naming V2; the REGENERATED cure
     package derives its pins from the table and references the table by
     path so the C-9066 successor consumes the reconciled artifact.

RED first (2026-09-18): no sdk_pin_table module/artifact existed; every
test below failed on the missing feature before implementation.
"""

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "harness"))

from sdk_pin_table import (  # noqa: E402
    AUTHORITY_SPEC,
    CURE_PACKAGE_PATH,
    OLD_CURE_PROBE_PATH,
    TABLE_PATH,
    PinnedSpec,
    graded_env_declarations,
    load_table,
    source_contradictions,
)

AUTHORITY_PATH = ROOT / "requirements-cpu-eval.txt"

SDK_PKGS = {"qiskit", "qiskit-aer", "pennylane", "pennylane-lightning", "cirq"}


def _authority_specs_from_file():
    """Parse the authority file independently of the table (no trusting)."""
    specs = {}
    for line in AUTHORITY_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([A-Za-z0-9_.-]+)\s*(.+)$", line)
        if m and m.group(1).lower() in SDK_PKGS:
            specs[m.group(1).lower()] = m.group(2).replace(" ", "")
    return specs


def _spec_contains_version(spec, version):
    return PinnedSpec(spec).contains(version)


class TestCanonicalTableExists:
    def test_table_file_exists_and_parses(self):
        assert TABLE_PATH.exists(), f"canonical pin table missing: {TABLE_PATH}"
        table = load_table()
        assert table["authority"] == "requirements-cpu-eval.txt"
        assert set(table["authority_pins"]) >= {
            "qiskit",
            "qiskit-aer",
            "pennylane",
            "cirq",
        }

    def test_table_authority_pins_match_authority_file(self):
        table = load_table()
        assert table["authority_pins"] == _authority_specs_from_file()

    def test_every_known_pin_source_is_inventoried(self):
        table = load_table()
        src_paths = {s["path"] for s in table["sources"]}
        for required in [
            "requirements-cpu-eval.txt",
            "data/generated/quantum_dedup_1k_glm52_soft_distill_v3/requirements-runnable.txt",
            "harness/state/probes/c9066_verdict_blocked_20260917T090810Z.json",
            "harness/state/probes/c9066_version_reconciliation_20260917T092121Z.json",
            "harness/state/probes/c9066_asi2_sdk_inventory_20260917T090736Z.json",
        ]:
            assert required in src_paths, f"pin source not inventoried: {required}"


class TestNoCrossFileContradiction:
    def test_no_active_source_contradicts_authority(self):
        """Mechanical contradiction check: every ACTIVE source range must
        intersect the authority range AND contain the graded-env measured
        version for that package (the C-9066 V2 pattern)."""
        table = load_table()
        violations = source_contradictions(table)
        assert violations == [], (
            "ACTIVE pin sources contradict the authority/graded env: "
            + "; ".join(v["detail"] for v in violations)
        )

    def test_qiskit_authority_range_contains_graded_2_4_1(self):
        """C-9066 V2 guard: the scoring authority range must admit the
        graded env's qiskit 2.4.1."""
        assert AUTHORITY_SPEC("qiskit").contains("2.4.1")

    def test_graded_env_cirq_1_3_0_is_declared_fail_closed(self):
        """C-9066 V1 guard: local graded env cirq 1.3.0 sits OUTSIDE the
        authority cirq>=1.4; the table must carry it as a declared
        violation (never silently dropped or reconciled away)."""
        table = load_table()
        declared = graded_env_declarations(table)
        out_of_range = [d for d in declared if d.get("id") == "V1"]
        assert out_of_range, (
            "graded-env cirq 1.3.0 violates authority cirq>=1.4 but the "
            "table declares no V1 violation"
        )
        assert out_of_range[0]["measured"] == "1.3.0"
        assert out_of_range[0]["authority"] == ">=1.4"

    def test_graded_env_versions_inside_authority_or_declared(self):
        table = load_table()
        problems = [
            d
            for d in graded_env_declarations(table)
            if d["state"] not in ("in_range", "declared_violation")
        ]
        assert problems == [], problems


class TestCurePackageReconciliation:
    def test_old_cure_is_blocked_with_v2_reason(self):
        assert OLD_CURE_PROBE_PATH.exists()
        table = load_table()
        old = [
            s for s in table["sources"] if s["path"] == str(OLD_CURE_PROBE_PATH.relative_to(ROOT))
        ]
        assert old and old[0]["status"] == "BLOCKED"
        assert "V2" in old[0]["reason"]
        assert "2.4.1" in old[0]["reason"]

    def test_regenerated_cure_package_exists_and_consumes_table_by_path(self):
        assert CURE_PACKAGE_PATH.exists(), f"regenerated cure package missing: {CURE_PACKAGE_PATH}"
        pkg = json.loads(CURE_PACKAGE_PATH.read_text())
        assert pkg["pin_table"] == str(
            TABLE_PATH.relative_to(ROOT)
        ), "cure package must reference the canonical table by path"
        assert (ROOT / pkg["pin_table"]).exists()

    def test_regenerated_cure_pins_come_from_authority_ranges(self):
        """The successor cure install set must lie INSIDE the authority
        ranges and must admit the graded qiskit 2.4.1 (the V2 fix)."""
        pkg = json.loads(CURE_PACKAGE_PATH.read_text())
        pins = pkg["install_pins"]
        assert _spec_contains_version(
            pins["qiskit"], "2.4.1"
        ), f"regenerated cure qiskit pin {pins['qiskit']} still excludes graded 2.4.1"
        assert _spec_contains_version(
            pins["cirq"], "1.4"
        ), "regenerated cure cirq pin must be >=1.4 per the scorer authority"
        for name, spec in sorted(pins.items()):
            assert AUTHORITY_SPEC(name).intersects(
                spec
            ), f"cure pin {name}={spec} outside authority range {AUTHORITY_SPEC(name).raw}"
