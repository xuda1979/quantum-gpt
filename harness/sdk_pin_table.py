"""C-9079: canonical SDK pin table (qiskit / cirq / pennylane).

Single source of truth for quantum-SDK version pins. The authority is
requirements-cpu-eval.txt (its header states the pins exist so the local
pass/fail signal matches the NPU-side verifier evals/subsystem/harness.py).

Consumers: the C-9066 successor cure package (by path, see
harness/state/cure-packages/C-9066-sdk-pin-cure-package.json) and
harness/tests/test_c9079_sdk_pin_table.py, which mechanically fails on any
cross-file contradiction (C-9066 V1/V2 patterns).
"""

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
TABLE_PATH = ROOT / "harness" / "state" / "sdk_pin_table.json"
CURE_PACKAGE_PATH = (
    ROOT / "harness" / "state" / "cure-packages" / "C-9066-sdk-pin-cure-package.json"
)
OLD_CURE_PROBE_PATH = (
    ROOT / "harness" / "state" / "probes" / "c9066_verdict_blocked_20260917T090810Z.json"
)


def load_table():
    return json.loads(TABLE_PATH.read_text())


def _vtuple(version):
    nums = re.findall(r"[0-9]+", str(version))
    return tuple(int(n) for n in nums) if nums else (0,)


def _cmp(a, b):
    la, lb = len(a), len(b)
    a = a + (0,) * (lb - la)
    b = b + (0,) * (la - lb)
    return (a > b) - (a < b)


class PinnedSpec:
    """A requirement-style version spec: examples >=1.2,<3.0 / >=0.14 / ==2.4.1."""

    _OP_RE = re.compile(r"^(>=|<=|==|!=|~=|>|<)?([0-9][0-9A-Za-z.]*)$")

    def __init__(self, raw):
        self.raw = str(raw).replace(" ", "")
        self._ops = []
        for part in self.raw.split(","):
            m = self._OP_RE.match(part)
            if not m:
                raise ValueError("unparseable version spec: " + repr(raw))
            self._ops.append((m.group(1) or "==", m.group(2)))

    def contains(self, version):
        v = _vtuple(version)
        for op, bound in self._ops:
            c = _cmp(v, _vtuple(bound))
            ok = {
                ">=": c >= 0,
                ">": c > 0,
                "<=": c <= 0,
                "<": c < 0,
                "==": c == 0,
                "!=": c != 0,
            }.get(op)
            if ok is None:  # tilde-equals unsupported in this table's specs
                raise ValueError("unsupported comparator in " + repr(self.raw))
            if not ok:
                return False
        return True

    def _bounds(self):
        lo = hi = None
        lo_strict = hi_strict = False
        for op, bound in self._ops:
            t = _vtuple(bound)
            if op in (">=", ">"):
                if lo is None or t > lo:
                    lo, lo_strict = t, op == ">"
            elif op in ("<=", "<"):
                if hi is None or t < hi:
                    hi, hi_strict = t, op == "<"
            elif op == "==":
                lo = hi = t
                lo_strict = hi_strict = False
        return lo, lo_strict, hi, hi_strict

    def intersects(self, other):
        if isinstance(other, str):
            other = PinnedSpec(other)
        alo, als, ahi, ahs = self._bounds()
        blo, bls, bhi, bhs = other._bounds()
        if ahi is not None and blo is not None:
            c = _cmp(ahi, blo)
            if c < 0 or (c == 0 and (ahs or bls)):
                return False
        if bhi is not None and alo is not None:
            c = _cmp(bhi, alo)
            if c < 0 or (c == 0 and (bhs or als)):
                return False
        return True


def _auth_spec(name, table):
    spec = table["authority_pins"].get(name)
    if spec is None:
        spec = table.get("derived_pins", dict()).get(name)
    if spec is None:
        raise KeyError("no authority/derived pin for " + repr(name))
    return PinnedSpec(spec)


def AUTHORITY_SPEC(name):
    return _auth_spec(name, load_table())


def _source_pins(src):
    pins = dict(src.get("pins", dict()))
    if src.get("live_pins_file"):
        live = json.loads((ROOT / src["path"]).read_text())
        pins.update(live["install_pins"])
    return pins


def source_contradictions(table=None):
    """Fail-closed contradiction scan over every ACTIVE pin source.

    A source contradicts when (a) any of its package ranges is disjoint
    from the authority range, or (b) it excludes a graded-env measured
    version that the AUTHORITY range itself admits (the C-9066 V2
    pattern: cure qiskit>=1.0,<2.0 vs graded 2.4.1). Versions the
    authority also rejects are V1 territory (declared_violations), not
    source contradictions.
    """
    table = table or load_table()
    measured = table.get("graded_env", dict()).get("measured", dict())
    out = []
    for src in table.get("sources", []):
        if src.get("status") != "ACTIVE":
            continue
        pins = _source_pins(src)
        for pkg in sorted(pins):
            spec = pins[pkg]
            try:
                auth = _auth_spec(pkg, table)
            except KeyError:
                out.append(
                    dict(source=src["path"], package=pkg, detail="no authority pin for " + pkg)
                )
                continue
            ps = PinnedSpec(spec)
            if not auth.intersects(ps):
                out.append(
                    dict(
                        source=src["path"],
                        package=pkg,
                        detail=spec + " disjoint from authority " + auth.raw,
                    )
                )
            for mpkg in sorted(measured):
                if mpkg != pkg:
                    continue
                ver = measured[mpkg]
                if auth.contains(ver) and not ps.contains(ver):
                    out.append(
                        dict(
                            source=src["path"],
                            package=pkg,
                            detail=spec
                            + " excludes graded "
                            + mpkg
                            + "=="
                            + ver
                            + " (V2 pattern; authority "
                            + auth.raw
                            + " admits it)",
                        )
                    )
    return out


def graded_env_declarations(table=None):
    """Classify every graded-env measurement against the authority pins.

    States: in_range, declared_violation (carried in the table, fail
    closed), undeclared_violation, no_authority_pin.
    """
    table = table or load_table()
    aliases = table.get("graded_env", dict()).get("aliases", dict())
    declared = set((d["package"], d["measured"]) for d in table.get("declared_violations", []))
    out = []
    measured = table.get("graded_env", dict()).get("measured", dict())
    for pkg in sorted(measured):
        ver = measured[pkg]
        base = aliases.get(pkg, pkg)
        entry = dict(package=pkg, measured=ver)
        try:
            auth = _auth_spec(base, table)
        except KeyError:
            entry.update(state="no_authority_pin")
            out.append(entry)
            continue
        entry["authority"] = auth.raw
        if auth.contains(ver):
            entry.update(state="in_range")
        elif (pkg, ver) in declared or (base, ver) in declared:
            d = None
            for cand in table["declared_violations"]:
                if cand["measured"] == ver and cand["package"] in (pkg, base):
                    d = cand
                    break
            entry.update(
                state="declared_violation", id=d["id"], disposition=d.get("disposition", "")
            )
        else:
            entry.update(state="undeclared_violation")
        out.append(entry)
    return out
