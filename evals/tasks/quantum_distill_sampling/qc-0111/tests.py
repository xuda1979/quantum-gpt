# Auto-generated semantic checker for qc-0111 (stabilizer).
# run_tests(candidate_path) -> {"passed": bool, "details": [str]}
# Executes the candidate as a standalone script and asserts SEMANTIC
# properties (distribution / energy / phase / fidelity / decoded stats)
# instead of stdout equality — the reference output is nondeterministic
# (random sampling).
import sys

#!/usr/bin/env python3
"""stageb_common.py — shared stdout parsers + semantic checkers for stage-B
(distillation sampling rows -> RL tasks with semantic tests).

This module's source is INLINED into each generated tests.py (they must be
self-contained, executed in a fresh subprocess by the harness). Only stdlib
imports are allowed here.

Checker contract: check_*(stdout: str, details: list, **params) -> bool.
params are derived at BUILD time from the problem statement and/or reference
runs, so the generated tests.py is self-contained and never runs the reference.

Parsing philosophy: reference stdout formats are diverse (dict reprs, '00: 123',
'|00> : 123', tuples, tables...). We parse defensively with multiple regexes and
report parse failures as assertion failures with the raw text head.
"""
import math
import re
import subprocess
import sys

# ---------------------------------------------------------------- parsers

_COUNTS_RES = [
    # order matters: spaced keys ('001 01': N) must be tried before the plain
    # patterns can mis-split them, and plain bitstrings must win over single
    # bits / labels. Counts always use ':' (never '=') — 'shots = 500' style
    # prose must not match — and a key must not be preceded by another digit.
    re.compile(r"['\"]?(?<!\d)([01](?:\s+[01])+)['\"]?\s*:\s*(\d+)"),  # '0 1': 123
    re.compile(r"['\"]?(?<!\d)([01]{2,})['\"]?\s*:\s*(\d+)"),          # '00': 123 / 000: 123
    re.compile(r"\|([01]{2,})>\s*:\s*(\d+)"),                          # |00>: 123
    re.compile(r"^([01]{2,})\s+(\d+)\s*$", re.M),                      # 00  123
    re.compile(r"^([01]{2,})\s*:\s*(\d+)\s*\(", re.M),                 # 1101: 483 (0.483)
    re.compile(r"^Shot\s+\d+\s*:\s*([01]{2,})\s*$", re.M),             # Shot 1: 1111
    re.compile(r"^\s*\[([01](?:,\s*[01])+)\]\s*$", re.M),              # [1, 1, 1, 1, 1]
    re.compile(r"^\s*\[?\[?\s*((?:True|False)(?:\s+(?:True|False)){1,})\s*\]?\]?\s*$", re.M),  # [False False False]
    re.compile(r"['\"]?(?<!\d)([01])['\"]?\s*:\s*(\d+)"),             # 0: 1964 / '1': 2055
    re.compile(r"(ZeroZero|OneOne)\s*:\s*(\d+)"),                      # Q# Bell labels
]

# 'True/False' shot rows map to 1/0
_BOOL_SHOT = {"True": "1", "False": "0"}

# single-bit / spaced / labelled keys must be normalized back to bitstrings
_SPECIAL_KEY = {
    "ZeroZero": "00",
    "OneOne": "11",
}

# Q# style: "(Zero, One, One, One): 243" — bits are printed MSB-first, so we
# REVERSE them to match the bitstring convention ('0111').
_TUPLE_RES = [
    re.compile(r"\(\s*(Zero|One)(?:\s*,\s*(Zero|One))+\s*\)\s*:\s*(\d+)"),
]

# Cirq np.int8 tuples: "(np.int8(0), np.int8(1)): 123" (qubit order kept)
_INT8_RES = [
    re.compile(r"\(\s*np\.int8\(([01])\)(?:\s*,\s*np\.int8\(([01])\))+\)\s*:\s*(\d+)"),
]

ENERGY_RES = [
    re.compile(r"(?:energy|E)\s*[:=]?\s*([-+]?\d*\.?\d+)", re.I),
    re.compile(r"final\s+energy[^\d-]*([-+]?\d+\.\d+)", re.I),
]

FIDELITY_RES = [
    re.compile(r"fidelity[^\d.]*([-+]?\d*\.?\d+)", re.I),
    re.compile(r"overlap[^\d.]*([-+]?\d*\.?\d+)", re.I),
]

PHASE_RES = [
    re.compile(r"phase[^\d.]*([-+]?\d*\.?\d+)", re.I),
    re.compile(r"theta_est[^\d.]*([-+]?\d*\.?\d+)", re.I),
]

CUT_RES = [
    re.compile(r"(?:best\s+)?cut\s*(?:value)?[^\d.]*(\d+)", re.I),
    re.compile(r"max(?:imum)?\s*cut[^\d.]*(\d+)", re.I),
    re.compile(r"cut\s*=\s*(\d+)", re.I),
    re.compile(r"maxcut\s+value[^\d.]*(\d+)", re.I),
]

COUNT_RES = [
    re.compile(r"(?:counts?|samples?|shots?)\s*[:=]?\s*(\d+)", re.I),
]


def parse_counts(stdout: str) -> dict:
    """Merge all bitstring-count pairs found in stdout. Returns {} if none.

    Handles: "{'00': 123, '11': 234}", "00: 123", "|00>: 123", "00 123",
    "1101: 483 (0.483)", Q# "(Zero, One, One, One): 243" (reversed),
    Cirq "(np.int8(0), np.int8(1)): 123", and Cirq-style
    "Counter({0: 519, 7: 481})" (int keys -> bitstrings of width =
    max_key.bit_length(), clamped to a sane bound)."""
    out = {}
    # Cirq-style int-key counters must win over single-bit prose matches
    m = re.search(r"Counter\((\{[^}]*\})\)", stdout)
    if m:
        pairs = re.findall(r"(\d+)\s*:\s*(\d+)", m.group(1))
        if pairs:
            maxk = max(int(k) for k, _ in pairs)
            width = max(1, maxk.bit_length())
            if width <= 64:  # sanity: never widen into garbage
                for k, v in pairs:
                    key = format(int(k), f"0{width}b")
                    out[key] = out.get(key, 0) + int(v)
                return out
    for rx in _COUNTS_RES:
        for m in rx.finditer(stdout):
            k = m.group(1)
            if len(m.groups()) == 1:
                v = 1  # per-shot row formats ("Shot 1: 1111", "[1, 1, 1]")
            else:
                v = int(m.group(2))
            if v <= 0:
                continue  # 'P(|s>) = 0.000' style floats must not count
            if k in _SPECIAL_KEY:
                k = _SPECIAL_KEY[k]
            elif set(k) <= {"T", "F"} or "True" in k or "False" in k:
                k = "".join(_BOOL_SHOT.get(w, "0") for w in k.split())
            else:
                k = k.replace(" ", "").replace(",", "")
            out[k] = out.get(k, 0) + v
        if out:
            return out
    for rx in _TUPLE_RES:
        for m in rx.finditer(stdout):
            seg = m.group(0)
            bits = re.findall(r"\b(Zero|One)\b", seg)
            bits = ["1" if b == "One" else "0" for b in bits]
            cm = re.search(r":\s*(\d+)", seg)
            k = "".join(reversed(bits))
            out[k] = out.get(k, 0) + int(cm.group(1))
        if out:
            return out
    for rx in _INT8_RES:
        for m in rx.finditer(stdout):
            seg = m.group(0)
            bits = re.findall(r"np\.int8\(([01])\)", seg)
            cm = re.search(r":\s*(\d+)", seg)
            k = "".join(bits)
            out[k] = out.get(k, 0) + int(cm.group(1))
        if out:
            return out
    return out


def parse_first_floats(stdout: str, res_list) -> list:
    out = []
    for rx in res_list:
        for m in rx.finditer(stdout):
            try:
                out.append(float(m.group(1)))
            except ValueError:
                continue
        if out:
            break
    return out


def parse_energies(stdout: str) -> list:
    return parse_first_floats(stdout, ENERGY_RES)


def parse_fidelities(stdout: str) -> list:
    return parse_first_floats(stdout, FIDELITY_RES)


def parse_phases(stdout: str) -> list:
    return parse_first_floats(stdout, PHASE_RES)


def parse_cuts(stdout: str) -> list:
    return [int(v) for v in parse_first_floats(stdout, CUT_RES)]


def parse_count(stdout: str):
    """Total shot count if the program reports one."""
    vals = parse_first_floats(stdout, COUNT_RES)
    return int(vals[0]) if vals else None


def parse_factors(stdout: str):
    """QPE-factoring: factors printed like '3, 5', '3 and 5',
    'Factors of 15: 3 and 5', or 'Factors found: 3 and 5'."""
    m = re.search(
        r"factor(?!ing)(?:s)?[^:\n]*?[:=]\s*([\d,\s]*\d+(?:\s*and\s*\d+)?)",
        stdout, re.I)
    if not m:
        return []
    nums = [int(x) for x in re.findall(r"\d+", m.group(1))]
    return nums


def parse_period(stdout: str):
    m = re.search(r"period[^\d]*(\d+)", stdout, re.I)
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------- assertions

def assert_true(cond: bool, detail: str, details: list) -> bool:
    ok = bool(cond)
    details.append(("PASS " if ok else "FAIL ") + detail)
    return ok


def run_candidate(candidate_path: str, timeout: int = 180):
    """Run candidate as standalone script; return (rc, stdout, stderr)."""
    try:
        p = subprocess.run(
            [sys.executable, candidate_path],
            capture_output=True, text=True, timeout=timeout,
        )
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"


# ---------------------------------------------------------------- checkers

def check_concentration(stdout, details, p_lo, label="counts", total_min=0.6):
    """Bell/GHZ counts: P('0'*n)>=p_lo and P('1'*n)>=p_lo and sum>=total_min.
    n is inferred from the parsed bitstring width, so no per-row config."""
    counts = parse_counts(stdout)
    if not counts:
        return assert_true(False, f"{label}: no bitstring counts parsed "
                                  f"(head {stdout[:120]!r})", details)
    n = len(next(iter(counts)))
    a, b = "0" * n, "1" * n
    total = sum(counts.values())
    if total < 10:
        return assert_true(False, f"{label}: only {total} shots parsed", details)
    pa, pb = counts.get(a, 0) / total, counts.get(b, 0) / total
    need_sum = 0.8 if total < 50 else total_min
    details.append(f"{label}: P({a})={pa:.4f} P({b})={pb:.4f} "
                   f"(n={n}, total={total})")
    ok = pa >= p_lo and pb >= p_lo and (pa + pb) >= need_sum
    return assert_true(ok, f"{label}: need P({a})>={p_lo} and P({b})>={p_lo} "
                           f"and sum>={need_sum}", details)


def check_z_expectation(stdout, details, z_min=0.85):
    """GHZ verification via <Z...Z>: the n-qubit GHZ is a +1 eigenstate of
    Z^(x)n, so a correct preparation reports <Z...Z> ~ 1 (qulacs/braket
    observable checks)."""
    vals = []
    for line in stdout.splitlines():
        m = re.search(r"<Z[^>]*>\s*[:=]\s*(-?[\d.]+)", line, re.I)
        if m:
            vals.append(float(m.group(1)))
    if not vals:
        return assert_true(False, f"zexp: no <Z...Z> expectation parsed "
                                  f"(head {stdout[:120]!r})", details)
    z = max(vals)
    details.append(f"zexp: <Z...Z>={z:.4f} need>={z_min}")
    return assert_true(z >= z_min, f"zexp: <Z...Z> {z:.4f} < {z_min} "
                                   f"(GHZ not verified)", details)


def check_stabilizer(stdout, details, frac_min=0.98):
    """GHZ stabilizer verification: the X^(x)n stabilizer measurement via an
    ancilla must be deterministic +1 (a GHZ state is a +1 eigenstate)."""
    fracs = []
    for line in stdout.splitlines():
        m = re.search(r"(?<!-)\+1\s+outcome[^\(\n]*\(([\d.]+)", line)
        if m:
            f = float(m.group(1))
            fracs.append(f / 100.0 if f > 1.0 else f)
            continue
        m = re.search(r"(?<!-)\+1\s+outcome\s+fraction[:\s]*([\d.]+)",
                      line, re.I)
        if m:
            fracs.append(float(m.group(1)))
            continue
        m = re.search(r"outcome\s+False[^\n]*\([^)]*([\d.]+)\)", line, re.I)
        if m:
            fracs.append(float(m.group(1)))
            continue
        m = re.search(r"(?<!-)\+1\s+fraction[:\s]*([\d.]+)", line)
        if m:
            fracs.append(float(m.group(1)))
    ok = True
    if fracs:
        f = max(fracs)
        details.append(f"stabilizer: +1 fraction={f:.4f} need>={frac_min}")
        ok = assert_true(f >= frac_min, f"stabilizer: +1 fraction {f:.4f} "
                                        f"< {frac_min}", details)
    m = re.search(r"Deterministic\s+\+1\s*:\s*(True|False)", stdout, re.I)
    if m and m.group(1).lower() == "false":
        ok = assert_true(False, "stabilizer: Deterministic +1 = False",
                         details) and ok
    if not fracs and not m:
        return assert_true(False, f"stabilizer: no +1 statistics parsed "
                                  f"(head {stdout[:120]!r})", details)
    return ok


def check_statevector(stdout, details, fid_min=0.99):
    """GHZ statevector: fidelity (|a_0|+|a_last|)^2/2 to the n-qubit GHZ must
    be >= fid_min. Falls back to sampled-counts concentration if no
    statevector line is found."""
    m = re.search(r"\[\s*([^\]]*\+[0-9.]+j[^\]]*)\]", stdout)
    if m:
        pairs = re.findall(r"([-+]?\d+(?:\.\d*)?)\s*([+-]\d+(?:\.\d*)?j)",
                           m.group(1))
        amps = [complex(float(p[0]), float(p[1].rstrip("j"))) for p in pairs]
        if not amps:
            return assert_true(False, "statevector: no complex amplitudes parsed",
                               details)
        fid = (abs(amps[0]) + abs(amps[-1])) ** 2 / 2
        details.append(f"statevector: GHZ fidelity={fid:.5f} "
                       f"({len(amps)} amps, n={len(amps).bit_length() - 1})")
        return assert_true(fid >= fid_min, f"statevector: fidelity {fid:.5f} "
                                           f"< {fid_min}", details)
    m = re.search(r"\|([01]+)>\s*:\s*\(([^)]+)\)", stdout)
    if m:
        # Braket-style: "|0000> : (0.7071067811865475+0j)" lines
        amps = {}
        for m2 in re.finditer(r"\|([01]+)>\s*:\s*\(([^)]+)\)", stdout):
            amp = m2.group(2).replace(" ", "")
            try:
                amps[m2.group(1)] = complex(amp)
            except ValueError:
                continue
        if amps:
            n = len(next(iter(amps)))
            a0 = amps.get("0" * n, 0j)
            a1 = amps.get("1" * n, 0j)
            fid = (abs(a0) + abs(a1)) ** 2 / 2
            details.append(f"statevector: GHZ fidelity={fid:.5f} "
                           f"from {len(amps)} basis amplitudes (n={n})")
            return assert_true(fid >= fid_min, f"statevector: fidelity "
                               f"{fid:.5f} < {fid_min}", details)
    counts = parse_counts(stdout)
    if counts:
        n = len(next(iter(counts)))
        total = sum(counts.values())
        pa, pb = counts.get("0" * n, 0) / total, counts.get("1" * n, 0) / total
        details.append(f"statevector: counts P({'0' * n})={pa:.4f} "
                       f"P({'1' * n})={pb:.4f}")
        return assert_true(pa + pb >= 0.8 and min(pa, pb) >= 0.15,
                           "statevector: GHZ counts not concentrated", details)
    return assert_true(False, f"statevector: no amplitudes/counts parsed "
                              f"(head {stdout[:120]!r})", details)


def check_chsh(stdout, details, s_min=2.0):
    """CHSH: |S| must violate the classical bound (S in (2, 2*sqrt(2)]).
    Computes S from the four printed correlators, or from a printed S value."""
    corrs = [float(x) for x in re.findall(r"E\([^)]*\)\s*=\s*([-+]?\d+\.\d+)",
                                          stdout)]
    s_val = None
    if len(corrs) >= 4:
        c = corrs[:4]
        s_val = abs(c[0] - c[1] + c[2] + c[3])
        details.append(f"chsh: correlators={[f'{x:.4f}' for x in c]} "
                       f"|S|={s_val:.4f} need>{s_min}")
        return assert_true(s_val > s_min, f"chsh: |S|={s_val:.4f} "
                                          f"<= classical bound {s_min}", details)
    m = re.search(r"(?:S value|S\s*=|^[ \t]*=)\s*([-+]?\d+\.\d+)", stdout, re.M)
    if m:
        s_val = abs(float(m.group(1)))
        details.append(f"chsh: printed |S|={s_val:.4f} need>{s_min}")
        return assert_true(s_val > s_min, f"chsh: |S|={s_val:.4f} "
                                          f"<= classical bound {s_min}", details)
    return assert_true(False, f"chsh: no correlators / S value parsed "
                              f"(head {stdout[:120]!r})", details)


def check_zne(stdout, details, err_max):
    """Zero-noise extrapolation: extrapolated <ZZ> must be close to the ideal
    (1.0 for a Bell state)."""
    m = re.search(r"(?:Zero-noise extrapolated|ZNE extrapolated|"
                  r"Zero-noise estimate|Extrapolated \(linear fit\)|"
                  r"Extrapolated <ZZ>|extrapolated <ZZ>)[^\d.]*([\d.]+)",
                  stdout, re.I)
    if not m:
        return assert_true(False, f"zne: no extrapolated value parsed "
                                  f"(head {stdout[:120]!r})", details)
    ext = float(m.group(1))
    m2 = re.search(r"Ideal(?:\s*<ZZ>\s*(?:value)?|\s+value)?\s*[:=]?\s*"
                   r"([\d.]+)", stdout, re.I)
    ideal = float(m2.group(1)) if m2 else 1.0
    err = abs(ext - ideal)
    details.append(f"zne: extrapolated={ext:.4f} ideal={ideal:.4f} "
                   f"err={err:.4f} need<={err_max}")
    return assert_true(err <= err_max, f"zne: extrapolation error {err:.4f} "
                                       f"> {err_max}", details)


def check_maxcut(stdout, details, edges, n_nodes):
    """MaxCut: the printed best cut must equal the brute-force optimum of the
    problem-statement graph. The test recomputes opt itself."""
    opt = 0
    for mask in range(1 << n_nodes):
        cut = 0
        for u, v in edges:
            if ((mask >> u) & 1) != ((mask >> v) & 1):
                cut += 1
        opt = max(opt, cut)
    cuts = parse_cuts(stdout)
    if not cuts:
        return assert_true(False, f"maxcut: no cut value parsed "
                                  f"(head {stdout[:120]!r})", details)
    best = max(cuts)
    details.append(f"maxcut: best={best} brute-force opt={opt} "
                   f"({len(edges)} edges)")
    return assert_true(best == opt, f"maxcut: best cut {best} != optimum {opt}",
                       details)


def check_vqe(stdout, details, e_max, exact_slack=0.6):
    """VQE: the VQE-labeled energy must be <= e_max (derived from reference
    runs) and within exact_slack of the printed exact ground energy."""
    vqe_es = re.findall(
        r"(?:VQE|vqe)[^:\n]*?(?:energy|Energy)\s*[:=]\s*(-?\d+\.?\d*)", stdout)
    exact_es = re.findall(
        r"(?:Exact|exact)[^:\n]*?(?:energy|Energy)\s*[:=]\s*(-?\d+\.?\d*)",
        stdout)
    es = parse_energies(stdout)
    if not es and not vqe_es:
        return assert_true(False, f"vqe: no energy parsed (head {stdout[:120]!r})",
                           details)
    e_vqe = float(vqe_es[0]) if vqe_es else es[0]
    ok = assert_true(e_vqe <= e_max, f"vqe: energy {e_vqe:.5f} > threshold "
                                     f"{e_max}", details)
    if exact_es:
        e_exact = float(exact_es[0])
        ok = assert_true(e_vqe <= e_exact + exact_slack,
                         f"vqe: energy {e_vqe:.5f} too far above exact "
                         f"{e_exact:.5f} (slack {exact_slack})", details) and ok
        details.append(f"vqe: energy={e_vqe:.5f} exact={e_exact:.5f} "
                       f"need<={e_max}")
    else:
        details.append(f"vqe: energy={e_vqe:.5f} need<={e_max}")
    return ok


def check_qpe_phase(stdout, details, expected, tol=0.1):
    """QPE: |estimated_phase - expected| <= tol. expected comes from the
    problem statement. Lines that restate the target ('Target phase',
    'True phase') are excluded — only the ESTIMATED phase counts."""
    filtered = "\n".join(l for l in stdout.splitlines()
                         if "target" not in l.lower() and
                         "true" not in l.lower())
    phases = parse_phases(filtered)
    if not phases:
        return assert_true(False, f"qpe: no phase parsed (head {stdout[:120]!r})",
                           details)
    err = min(abs(p - expected) for p in phases)
    details.append(f"qpe: est={phases[-1]:.6f} expected={expected} "
                   f"err={err:.6f} tol={tol}")
    return assert_true(err <= tol, f"qpe: phase error {err:.5f} > tol {tol}",
                       details)


def check_shor(stdout, details, N, expected_factors=None):
    """Order finding / Shor: printed factors must (a) be nontrivial divisors,
    (b) multiply to N, and (c) include the expected factors if given."""
    factors = parse_factors(stdout)
    if not factors:
        return assert_true(False, f"shor: no factors parsed (head {stdout[:120]!r})",
                           details)
    fset = {f for f in factors if 1 < f < N}
    ok = True
    if expected_factors:
        missing = [f for f in expected_factors if f not in fset]
        ok = assert_true(not missing, f"shor: missing factors {missing}, "
                                       f"got {sorted(fset)}", details)
    prod_ok = any(f1 * f2 == N for f1 in fset for f2 in fset)
    ok = assert_true(prod_ok, f"shor: factors {sorted(fset)} don't multiply "
                              f"to {N}", details) and ok
    details.append(f"shor: factors={sorted(fset)} N={N}")
    return ok


def check_hhl(stdout, details, err_max):
    """HHL: max absolute error of the normalized solution vs numpy must be
    <= err_max (derived from reference runs)."""
    m = re.search(r"Absolute\s+error\s*:\s*\[([^\]]*)\]", stdout, re.I)
    if m:
        errs = [float(x) for x in re.findall(r"[-+]?\d+\.?\d*", m.group(1))]
    else:
        m2 = re.search(r"Absolute\s+error\s*:\s*([-+]?\d+\.?\d*)", stdout, re.I)
        errs = [float(m2.group(1))] if m2 else []
    if not errs:
        return assert_true(False, f"hhl: no absolute error parsed "
                                  f"(head {stdout[:120]!r})", details)
    err = max(errs)
    details.append(f"hhl: max abs error={err:.4f} need<={err_max}")
    return assert_true(err <= err_max, f"hhl: abs error {err:.4f} > {err_max}",
                       details)


def check_qae(stdout, details, theta, m=None, amp_tol=0.04):
    """Canonical amplitude estimation: estimated amplitude must match
    sin^2(theta/2) from the problem statement. The questions always place
    theta exactly on the QPE grid, so a correct implementation has error ~ 0
    and amp_tol=0.04 cleanly separates broken estimates."""
    a_est = None
    m2 = re.search(r"(?:Estimated amplitude|estimated amplitude)\s*[:=]?\s*"
                   r"([\d.]+)", stdout)
    if m2:
        a_est = float(m2.group(1))
    a_th = math.sin(theta / 2) ** 2
    if a_est is None:
        m3 = re.search(r"(?:Estimated theta|estimated theta)\s*[:=]?\s*"
                       r"([\d.]+)", stdout)
        if m3:
            th_est = float(m3.group(1))
            a_est = math.sin(th_est / 2) ** 2
    if a_est is None:
        return assert_true(False, f"qae: no estimated amplitude/theta parsed "
                                  f"(head {stdout[:120]!r})", details)
    err = abs(a_est - a_th)
    details.append(f"qae: est amplitude={a_est:.4f} true={a_th:.4f} "
                   f"err={err:.4f} tol={amp_tol}" +
                   (f" (m={m})" if m else ""))
    return assert_true(err <= amp_tol, f"qae: amplitude error {err:.4f} "
                                       f"> {amp_tol}", details)


def check_swap_test(stdout, details, theta_psi, theta_phi, tol=0.06):
    """SWAP test: estimated and analytic |<psi|phi>|^2 must both match
    cos^2((theta_psi - theta_phi)/2) computed from the problem-statement
    rotation angles."""
    theory = math.cos((theta_psi - theta_phi) / 2) ** 2
    m1 = re.search(r"Estimated\s+[^:\n]*\|<psi\|phi>\|\^2\s*[:=]\s*"
                   r"([-+]?[\d.]+)", stdout, re.I)
    m2 = re.search(r"Analytic\s+[^:\n]*\|<psi\|phi>\|\^2\s*[:=]\s*"
                   r"([-+]?[\d.]+)", stdout, re.I)
    est = float(m1.group(1)) if m1 else None
    ana = float(m2.group(1)) if m2 else None
    if est is None and ana is None:
        return assert_true(False, f"swap: no |<psi|phi>|^2 parsed "
                                  f"(head {stdout[:120]!r})", details)
    ok = True
    if est is not None:
        ok = assert_true(abs(est - theory) <= tol,
                         f"swap: estimated {est:.4f} vs theory {theory:.4f}",
                         details) and ok
    if ana is not None:
        ok = assert_true(abs(ana - theory) <= tol,
                         f"swap: analytic {ana:.4f} vs theory {theory:.4f}",
                         details) and ok
    details.append(f"swap: theory={theory:.4f} est={est} ana={ana}")
    return ok


def check_simon(stdout, details, expected_s):
    """Simon: the recovered hidden period must equal the one stated in the
    problem statement."""
    m = re.search(r"Recovered\s+(?:period|hidden\s+string)[^\n]*?s?\s*[:=]?\s*"
                  r"([01]{3,})", stdout, re.I)
    if not m:
        return assert_true(False, f"simon: no recovered period parsed "
                                  f"(head {stdout[:120]!r})", details)
    got = m.group(1)
    details.append(f"simon: recovered={got} expected={expected_s}")
    ok = assert_true(got == expected_s,
                     f"simon: recovered {got} != expected {expected_s}", details)
    return ok


# teleport: regexes that only ever match MEASURED receiver statistics
_TELEPORT_P1_RES = [
    re.compile(r"Observed\s+P\(\|1>\)[:\s]+(\d+\.\d+)"),                       # Q#
    re.compile(r"Measured\s+probability\s+of\s+1[:\s]*(\d+\.\d+)"),            # qc-0064
    re.compile(r"P\(receiver=1\)\s+empirical[:\s]*(\d+\.\d+)"),                # Cirq
    re.compile(r"P\(receiver=1\)[:\s]*empirical\s*=\s*(\d+\.\d+)"),            # Cirq =
    re.compile(r"P\(receiver=1\)\s*=\s*(\d+\.\d+)\s*\(expected"),              # qc-0624
    re.compile(r"P\(\|1>\)\s*=\s*(\d+\.\d+)\s*\(expected"),                    # qc-0821...
    re.compile(r"P\(1\)\s*=\s*(\d+\.\d+)\s*\(expected"),
    re.compile(r"Measured\s+P\(m2=1\)\s*=\s*(\d+\.\d+)"),                      # qc-0720
    re.compile(r"Receiver\s+qubit\s+measured\s+1\s*:\s*(\d+)\s+times\s*\(\s*(\d+\.\d+)"),  # qc-0779
    re.compile(r"f\(\|1>\)\s*=\s*(\d+\.\d+)"),                                 # qc-0626
    re.compile(r"Actual\s+P\(\|1>\)\s*=\s*(\d+\.\d+)"),                        # qc-0561
    re.compile(r"P\(\|1>\)\s*=\s*(\d+\.\d+)\s*\(count"),                       # qc-0522
    re.compile(r"P\(1\)\s+simulated\s*=\s*(\d+\.\d+)"),                        # Cirq
    re.compile(r"\|1> count:\s*\d+\s*\((\d+\.\d+)\)"),                         # qc-0475
]
_TELEPORT_PLAIN = [
    re.compile(r"P\(1\)\s*=\s*(\d+\.\d+)"),
    re.compile(r"P\(\|1>\)\s*=\s*(\d+\.\d+)"),
    re.compile(r"P\(m2=1\)\s*=\s*(\d+\.\d+)"),
]


def _teleport_measured_p1(stdout: str) -> list:
    vals = []
    for rx in _TELEPORT_P1_RES:
        for m in rx.finditer(stdout):
            g = m.groups()[-1]
            vals.append(float(g))
    for line in stdout.splitlines():
        low = line.lower()
        if "expected" in low or "theory" in low or "theoretical" in low:
            continue
        for rx in _TELEPORT_PLAIN:
            m = rx.search(line)
            if m:
                vals.append(float(m.group(1)))
    return vals


def check_teleport(stdout, details, angle, tol=0.06, p_val_min=0.001):
    """Teleportation: measured receiver P(|1>) must match sin^2(angle/2)
    (the teleported state). angle comes from the problem statement. Every
    measured P(1) candidate must agree (a broken row may print both a
    correct-looking theory line and a wrong measured line)."""
    m = re.search(r"All outcomes teleport correctly:\s*(True|False)", stdout,
                  re.I)
    if m:
        ok = m.group(1).lower() == "true"
        details.append(f"teleport: all-outcomes-correct={m.group(1)}")
        return assert_true(ok, "teleport: some outcome failed to teleport",
                           details)
    p1s = _teleport_measured_p1(stdout)
    if not p1s:
        return assert_true(False, f"teleport: no measured P(|1>) parsed "
                                  f"(head {stdout[:120]!r})", details)
    p_th = math.sin(angle / 2) ** 2
    ok = True
    for p in p1s:
        err = abs(p - p_th)
        ok = assert_true(err <= tol, f"teleport: |P(1)={p:.4f} - "
                                     f"sin^2({angle}/2)={p_th:.4f}| = "
                                     f"{err:.4f} > tol {tol}", details) and ok
    m2 = re.search(r"P-value[:\s]+([\d\.]+)", stdout, re.I)
    if m2:
        pv = float(m2.group(1))
        ok = assert_true(pv >= p_val_min, f"teleport: chi2 p-value {pv:.4f} "
                                          f"< {p_val_min}", details) and ok
    return ok


def check_grover(stdout, details, target, p_min=0.6):
    """Grover: the probability of the QUESTION-stated marked state must be
    >= p_min. Checks counts, every target-specific printed probability, and
    the generic success-rate (min over parsed values). Checking the stated
    target — not the candidate's own max — catches wrong-oracle
    implementations that concentrate on another state."""
    ok = True
    counts = parse_counts(stdout)
    if counts:
        total = sum(counts.values())
        p = counts.get(target, 0) / total
        details.append(f"grover: counts P({target})={p:.4f} need>={p_min} "
                       f"({total} shots)")
        ok = assert_true(p >= p_min, f"grover: P({target})={p:.4f} < {p_min}",
                         details) and ok
    # target-specific probabilities: every parsed one must be >= p_min
    target_probs = []
    for line in stdout.splitlines():
        low = line.lower()
        if not any(k in low for k in ("probab", "frequenc", "success")):
            continue
        bits = re.findall(r"[01]{3,}", line)
        if len(bits) != 1:
            continue
        idx = line.find(bits[0])
        nums = [float(x) for x in re.findall(r"(\d+\.\d+)", line[idx:])]
        if not nums:
            continue
        target_probs.append((bits[0], nums[0]))
    for b, p in target_probs:
        details.append(f"grover: printed P({b})={p:.4f} need>={p_min}")
        if b == target:
            ok = assert_true(p >= p_min, f"grover: P({target})={p:.4f} < "
                                         f"{p_min}", details) and ok
    # generic success rates ("399/500 = 79.80%" and "0.7400" forms)
    gen = []
    frac = re.findall(r"Success\s+rate[^\d]*(\d+)/(\d+)\s*=\s*([\d.]+)\s*%",
                      stdout, re.I)
    if frac:
        gen += [float(a) / float(b) for a, b, _ in frac]
        gen += [float(p) / 100.0 for _, _, p in frac]
    else:
        gen += [float(x) for x in re.findall(
            r"Success\s+rate[^\d]*(\d+\.\d+)", stdout, re.I)]
    gen += [float(x) for x in re.findall(
        r"Success\s+probability[^\d]*(\d+\.\d+)", stdout, re.I)]
    gen = [g / 100.0 if g > 2.0 else g for g in gen]
    for g in gen:
        ok = assert_true(g >= p_min, f"grover: success rate {g:.4f} < {p_min}",
                         details) and ok
    m = re.search(r"Most\s+probable\s+outcome:\s*([01]{3,})", stdout, re.I)
    if m and m.group(1) != target:
        ok = assert_true(False, f"grover: most probable outcome {m.group(1)} "
                                f"!= target {target}", details) and ok
    if not counts and not target_probs and not gen:
        return assert_true(False, f"grover: no probability/counts parsed "
                                  f"(head {stdout[:120]!r})", details)
    return ok


def check_walk(stdout, details, support_min, spread_min,
               require_mixed_parity=True):
    """Quantum walk: final position distribution must cover >= support_min
    nodes, span >= spread_min positions, and (default) hit both parities —
    i.e., a real coin-driven walk, not a stationary/no-coin output.
    Handles 'Node 0: 0.4547' (prob) and 'Node 0: 1013' (count) formats."""
    m = re.findall(r"(?:Node|Position)\s+(\d+):\s*([\d.]+)", stdout, re.I)
    if not m:
        return assert_true(False, f"walk: no Node/Position lines parsed "
                                  f"(head {stdout[:120]!r})", details)
    raw = {int(k): float(v) for k, v in m}
    total = sum(raw.values())
    probs = {k: v / total for k, v in raw.items()}
    support = sum(1 for v in probs.values() if v > 1e-9)
    spread = max(probs) - min(probs)
    parities = {p % 2 for p in probs}
    details.append(f"walk: nodes={sorted(probs)} support={support} "
                   f"spread={spread} parities={parities}")
    ok = assert_true(support >= support_min, f"walk: support {support} "
                                             f"< {support_min}", details)
    ok = assert_true(spread >= spread_min, f"walk: spread {spread} < "
                                           f"{spread_min}", details) and ok
    if require_mixed_parity:
        ok = assert_true(len(parities) > 1, f"walk: only parity {parities} "
                                            f"(no coin mixing?)", details) and ok
    return ok


def check_knapsack(stdout, details, values, weights, capacity):
    """0/1 knapsack: printed total value must equal the DP-computed optimum
    (recomputed from the problem statement) and the solution feasible."""
    dp = [0] * (capacity + 1)
    for v, w in zip(values, weights):
        for c in range(capacity, w - 1, -1):
            dp[c] = max(dp[c], dp[c - w] + v)
    opt = max(dp)
    m = re.search(r"Total value[:\s]+(\d+)", stdout)
    if not m:
        return assert_true(False, f"knapsack: no 'Total value' parsed "
                                  f"(head {stdout[:120]!r})", details)
    best = int(m.group(1))
    ok = assert_true(best == opt, f"knapsack: value {best} != DP opt {opt}",
                     details)
    m2 = re.search(r"Feasible[:\s]+(True|False)", stdout, re.I)
    if m2:
        ok = assert_true(m2.group(1).lower() == "true",
                         f"knapsack: printed Feasible={m2.group(1)} "
                         f"(weight>cap)", details) and ok
    details.append(f"knapsack: value={best} DP-opt={opt}")
    return ok


def check_xeb(stdout, details, fid_min=0.5):
    """Linear cross-entropy benchmarking: XEB fidelity of a noiseless random
    circuit must be close to 1; broken samplers drop it toward 0."""
    m = re.search(r"(?:XEB|Linear XEB)\s*fidelity[:\s]*([\d.]+)", stdout, re.I)
    if not m:
        return assert_true(False, f"xeb: no XEB fidelity parsed "
                                  f"(head {stdout[:120]!r})", details)
    fid = float(m.group(1))
    details.append(f"xeb: fidelity={fid:.4f} need>={fid_min}")
    return assert_true(fid >= fid_min, f"xeb: fidelity {fid:.4f} < {fid_min}",
                       details)


def check_surface_code(stdout, details, max_rate=0.5):
    """Surface/repetition code memory: logical error rates must be in
    (0, max_rate] and, when several distances are reported, the higher
    distance must show a lower rate (error suppression). Also flags
    'errors > shots' arithmetic failures."""
    cur_d = None
    pairs = []   # (distance, rate)
    rates = []   # rate without a distance label
    bad_arith = None
    for line in stdout.splitlines():
        m = re.search(r"Distance\s+(\d+)", line)
        if m:
            cur_d = int(m.group(1))
        m2 = re.search(r"Logical\s+errors?\s*=\s*(\d+)\s*/\s*(\d+)\s*=\s*"
                       r"([\d.]+)", line, re.I)
        if m2:
            e, s, r = int(m2.group(1)), int(m2.group(2)), float(m2.group(3))
            if e > s:
                bad_arith = (e, s)
            if cur_d is not None:
                pairs.append((cur_d, r))
            else:
                rates.append(r)
        m3 = re.search(r"logical\s+error\s+rate\s*[:=]?\s*([\d.]+)", line, re.I)
        if m3:
            r = float(m3.group(1))
            if cur_d is not None:
                pairs.append((cur_d, r))
            else:
                rates.append(r)
    if not pairs and not rates:
        return assert_true(False, f"surface: no logical error rate parsed "
                                  f"(head {stdout[:120]!r})", details)
    ok = True
    for d, r in pairs:
        ok = assert_true(0.0 < r <= max_rate, f"surface: rate={r:.5f} "
                                              f"(d={d}) out of (0, {max_rate}]",
                         details) and ok
    for r in rates:
        ok = assert_true(0.0 < r <= max_rate, f"surface: rate={r:.5f} out of "
                                              f"(0, {max_rate}]", details) and ok
    if bad_arith:
        ok = assert_true(False, f"surface: errors {bad_arith[0]} > shots "
                                f"{bad_arith[1]}", details) and ok
    if len(pairs) >= 2:
        by_d = {}
        for d, r in pairs:
            by_d[d] = min(by_d.get(d, 1.0), r)
        lo, hi = min(by_d), max(by_d)
        ok = assert_true(by_d[hi] < by_d[lo],
                         f"surface: no error suppression d={lo} "
                         f"({by_d[lo]:.5f}) vs d={hi} ({by_d[hi]:.5f})",
                         details) and ok
    return ok


def check_qasm3(stdout, details):
    """OpenQASM 3 mid-circuit reset: the printed program must contain a QASM3
    header, an if statement and a mid-circuit measurement, and the final
    measurement counts must show a ~50/50 coin-flip distribution (both
    outcomes present, none dominant)."""
    has_qasm3 = "OPENQASM 3.0" in stdout or "OPENQASM 3" in stdout or \
        "QASM 3" in stdout
    ok = assert_true(has_qasm3, "qasm3: no OPENQASM 3.0 source printed", details)
    has_if = bool(re.search(r"\bif\s*\([^)]*\)", stdout))
    ok = assert_true(has_if, "qasm3: no if statement in printed source",
                     details) and ok
    has_mid = bool(re.search(r"measure\s*q\[\d+\]", stdout, re.I))
    ok = assert_true(has_mid, "qasm3: no mid-circuit measure q[...] found",
                     details) and ok
    counts = parse_counts(stdout)
    if not counts:
        return assert_true(False, f"qasm3: no final counts parsed "
                                  f"(head {stdout[:120]!r})", details) and ok
    total = sum(counts.values())
    p_max = max(counts.values()) / total
    ok = assert_true(total >= 100, f"qasm3: only {total} shots parsed",
                     details) and ok
    ok = assert_true(len(counts) >= 2,
                     f"qasm3: single outcome {dict(counts)} (no coin flip?)",
                     details) and ok
    ok = assert_true(p_max <= 0.9, f"qasm3: dominant outcome P={p_max:.4f} "
                                   f"(reset failed?)", details) and ok
    details.append(f"qasm3: counts={dict(list(counts.items())[:6])} "
                   f"max P={p_max:.4f} (n={total})")
    return ok


def check_povm(stdout, details, wrong_max=0.05, correct_min=0.1):
    """Unambiguous state discrimination of |0> vs |+>: misidentification must
    be ~0 (a POVM element that identifies |0> never fires on |+> and vice
    versa) and the correct identification rate must be meaningful."""
    blocks = re.split(r"Input\s+(?:state\s*:?\s*)?\|?(zero|plus|\|0>|\|\+>)",
                      stdout, flags=re.I)
    # blocks: [pre, tag, body, tag, body, ...]
    ok = True
    found = 0
    for i in range(1, len(blocks), 2):
        tag = blocks[i].lower().strip("| >")
        body = blocks[i + 1] if i + 1 < len(blocks) else ""
        if tag.startswith("zero") or tag == "0":
            wrong_label = "|+>"
        else:
            wrong_label = "|0>"
        wrong_fracs = []
        for line in body.splitlines():
            if "conclusive" not in line.lower():
                continue
            if wrong_label not in line:
                continue
            fracs = re.findall(r"\(([\d.]+)\s*%?\)", line)
            if fracs:
                f = float(fracs[0])
                wrong_fracs.append(f / 100.0 if f > 1.0 else f)
        if not wrong_fracs:
            continue
        found += 1
        w = max(wrong_fracs)
        ok = assert_true(w <= wrong_max, f"povm: input |{tag}> misidentified "
                                         f"as {wrong_label}: {w:.4f} > "
                                         f"{wrong_max}", details) and ok
    if found == 0:
        return assert_true(False, f"povm: no conclusive statistics parsed "
                                  f"(head {stdout[:120]!r})", details)
    return ok


def check_qrng(stdout, details, count, range_max, mean_lo=0.15, mean_hi=0.85):
    """QRNG: printed integers must be exactly `count` values, each in
    [0, range_max), not all identical, and roughly uniformly spread."""
    m = re.search(r"\[\s*(\d+(?:\s*,\s*\d+)*)\s*\]", stdout)
    if not m:
        return assert_true(False, f"qrng: no integer list parsed "
                                  f"(head {stdout[:120]!r})", details)
    nums = [int(x) for x in re.findall(r"\d+", m.group(1))]
    ok = assert_true(len(nums) == count, f"qrng: {len(nums)} numbers, "
                                         f"expected {count}", details)
    ok = assert_true(all(0 <= x < range_max for x in nums),
                     f"qrng: value out of [0, {range_max}): "
                     f"{sorted(set(x for x in nums if not 0 <= x < range_max))}",
                     details) and ok
    ok = assert_true(len(set(nums)) >= 2, f"qrng: all values identical "
                                          f"({nums[:5]}...)", details) and ok
    mean = sum(nums) / len(nums) if nums else 0
    ok = assert_true(mean_lo * range_max <= mean <= mean_hi * range_max,
                     f"qrng: mean {mean:.1f} outside "
                     f"[{mean_lo * range_max:.0f}, {mean_hi * range_max:.0f}]",
                     details) and ok
    details.append(f"qrng: {len(nums)} ints, mean={mean:.1f}, "
                   f"range=[0,{range_max})")
    return ok


def check_random_benchmark(stdout, details, epc_max=0.1, monotone_tol=0.05):
    """Single-qubit randomized benchmarking: survival probabilities must decay
    monotonically (within sampling tolerance) and the fitted error per
    Clifford must be small (a nonsense fit fails)."""
    pairs = []
    for line in stdout.splitlines():
        m = re.search(r"(?:Length|L=)\s*(\d+)\s*:?\s*(?:survival\s*=\s*)?"
                      r"([\d.]+)", line, re.I)
        if m:
            pairs.append((int(m.group(1)), float(m.group(2))))
            continue
        m = re.match(r"^\s*(\d+)\s+([\d.]+)\s*$", line)
        if m:
            pairs.append((int(m.group(1)), float(m.group(2))))
    if not pairs:
        return assert_true(False, f"rb: no survival probabilities parsed "
                                  f"(head {stdout[:120]!r})", details)
    pairs.sort()
    surv = [p for _, p in pairs]
    ok = True
    for i in range(1, len(surv)):
        if surv[i] > surv[i - 1] + monotone_tol:
            ok = assert_true(False, f"rb: survival increases "
                                    f"{surv[i - 1]:.4f} -> {surv[i]:.4f} "
                                    f"(len {pairs[i - 1][0]} -> {pairs[i][0]})",
                             details) and ok
    epc = None
    m = re.search(r"Error\s+per\s+Clifford\s*\(EPC\)\s*=\s*1\s*-\s*p\s*=\s*"
                  r"([\d.]+)", stdout, re.I)
    if m:
        epc = float(m.group(1))
    if epc is None:
        m = re.search(r"Error\s+per\s+Clifford[^\d]*([\d.]+)", stdout, re.I)
        if m:
            epc = float(m.group(1))
    if epc is not None:
        ok = assert_true(epc <= epc_max, f"rb: error per Clifford {epc:.4f} "
                                         f"> {epc_max}", details) and ok
    details.append(f"rb: survivals={[f'{s:.3f}' for s in surv]} "
                   f"epc={epc}")
    return ok


def check_loschmidt(stdout, details, echo_min=0.9, decay_gap=0.003):
    """Loschmidt echo: U U^dagger must return to |0...0> with probability
    ~1, and a perturbation must cause a (small) decay."""
    m1 = re.search(r"(?:Unperturbed[^\n]*|Echo probability[^\n]*)[:\s]+"
                   r"([\d.]+)", stdout, re.I)
    m2 = re.search(r"Perturbed[^\n]*[:\s]+([\d.]+)", stdout, re.I)
    if not m1 or not m2:
        return assert_true(False, f"loschmidt: echo probabilities not parsed "
                                  f"(head {stdout[:120]!r})", details)
    echo = float(m1.group(1))
    pert = float(m2.group(1))
    ok = assert_true(echo >= echo_min, f"loschmidt: echo {echo:.4f} < "
                                       f"{echo_min} (U^dagger U != I?)",
                     details)
    ok = assert_true(pert < echo - decay_gap, f"loschmidt: perturbed {pert:.4f}"
                     f" not below echo {echo:.4f} (no decay)", details) and ok
    details.append(f"loschmidt: echo={echo:.4f} perturbed={pert:.4f} "
                   f"decay={echo - pert:.4f}")
    return ok


def check_ising(stdout, details, n, J, h0, etol=1e-3):
    """Ising chain: the best sampled state must be fully aligned (all spins
    equal — ferromagnetic) and its energy must match the analytic ground
    energy E* = -J*(n-1) - |h0| of the problem-statement model."""
    m = re.search(r"\{[^{}]*np\.int8\([-01]+\)[^{}]*\}", stdout)
    if not m:
        return assert_true(False, f"ising: no np.int8 spin dict parsed "
                                  f"(head {stdout[:120]!r})", details)
    vals = [int(x) for x in re.findall(r"np\.int8\(([-01]+)\)", m.group(0))]
    ok = assert_true(len(vals) == n, f"ising: {len(vals)} spins, expected {n}",
                     details)
    ok = assert_true(all(v == vals[0] for v in vals), f"ising: spins not fully "
                     f"aligned: {vals[:8]}{'...' if len(vals) > 8 else ''}",
                     details) and ok
    e_star = -J * (n - 1) - abs(h0)
    energies = []
    for line in stdout.splitlines():
        if "expected" in line.lower():
            continue
        m2 = re.search(r"(?:Ground state energy|Best energy|Min energy found|"
                       r"^Energy)[:\s]*(-?[\d.]+)", line, re.I)
        if m2:
            energies.append(float(m2.group(1)))
    if not energies:
        return assert_true(False, f"ising: no ground state energy parsed "
                                  f"(head {stdout[:120]!r})", details) and ok
    e_min = min(energies)
    ok = assert_true(abs(e_min - e_star) <= etol, f"ising: energy {e_min:.6f}"
                     f" != analytic {e_star:.6f} (n={n}, J={J}, h0={h0})",
                     details) and ok
    details.append(f"ising: spins={vals[:6]}{'...' if len(vals) > 6 else ''} "
                   f"aligned, E={e_min:.6f} vs {e_star:.6f}")
    return ok


def check_xxz(stdout, details, err_max):
    """XXZ Trotter evolution: |Trotter - exact| <Z_0>(t) must be small."""
    m = re.search(r"(?:Absolute difference|absolute difference|Absolute "
                  r"error)[:\s]*([\d.]+)", stdout)
    if not m:
        return assert_true(False, f"xxz: no absolute difference parsed "
                                  f"(head {stdout[:120]!r})", details)
    err = float(m.group(1))
    details.append(f"xxz: |trotter-exact|={err:.5f} need<={err_max}")
    return assert_true(err <= err_max, f"xxz: error {err:.5f} > {err_max}",
                       details)


def check_hubbard(stdout, details, e_max):
    """Fermi-Hubbard: printed ground state energy must be <= e_max (derived
    from reference runs of the fixed problem Hamiltonian)."""
    m = re.search(r"Ground state energy\s*:\s*(-?[\d.]+)", stdout)
    if not m:
        return assert_true(False, f"hubbard: no ground state energy parsed "
                                  f"(head {stdout[:120]!r})", details)
    e = float(m.group(1))
    details.append(f"hubbard: E0={e:.6f} need<={e_max}")
    return assert_true(e <= e_max, f"hubbard: E0 {e:.6f} > {e_max}", details)


def check_transpile(stdout, details):
    """Transpilation: depth and CX count must not increase with optimization
    level, and the highest level must strictly improve on level 0."""
    pairs = re.findall(
        r"(?:Level|Optimization level)\s+(\d+)\s*:?\s*(?:depth|Depth)\s*=\s*"
        r"(\d+)\s*,?\s*(?:cx|CX)\s*(?:count)?\s*=\s*(\d+)", stdout)
    if not pairs:
        return assert_true(False, f"transpile: no level/depth/cx lines parsed "
                                  f"(head {stdout[:120]!r})", details)
    by_level = {int(l): (int(d), int(c)) for l, d, c in pairs}
    levels = sorted(by_level)
    ok = True
    prev_d, prev_c = by_level[levels[0]]
    for lv in levels[1:]:
        d, c = by_level[lv]
        ok = assert_true(d <= prev_d, f"transpile: depth {d} > {prev_d} at "
                                      f"level {lv}", details) and ok
        ok = assert_true(c <= prev_c, f"transpile: cx {c} > {prev_c} at "
                                      f"level {lv}", details) and ok
        prev_d, prev_c = d, c
    d0, c0 = by_level[levels[0]]
    dl, cl = by_level[levels[-1]]
    ok = assert_true(dl < d0 or cl < c0, f"transpile: no improvement from "
                     f"level {levels[0]} ({d0} depth, {c0} cx) to "
                     f"{levels[-1]} ({dl} depth, {cl} cx)", details) and ok
    details.append(f"transpile: levels={levels} "
                   f"{[(l, by_level[l]) for l in levels]}")
    return ok


def check_ite(stdout, details, err_max, overlap_min=0.999):
    """Imaginary-time evolution: the ITE energy must match the exact ground
    energy, and the overlap must be ~1."""
    m = re.search(r"(?:Energy error|Energy difference|energy error|energy "
                  r"difference)[:\s]*([\d.eE+-]+)", stdout)
    if not m:
        return assert_true(False, f"ite: no energy error parsed "
                                  f"(head {stdout[:120]!r})", details)
    err = float(m.group(1))
    ok = assert_true(err <= err_max, f"ite: energy error {err:.3e} > "
                                     f"{err_max:.3e}", details)
    m2 = re.search(r"(?:Overlap|overlap)\s*\|[^|]*\|\s*:\s*([\d.]+)", stdout)
    if m2:
        ov = float(m2.group(1))
        ok = assert_true(ov >= overlap_min, f"ite: overlap {ov:.6f} < "
                                            f"{overlap_min}", details) and ok
    details.append(f"ite: energy error={err:.3e}")
    return ok


def check_bitflip(stdout, details, theta, tol=0.08):
    """3-qubit bit-flip code: the decoded logical P(|0>) must match
    cos^2(theta/2) of the state encoded per the problem statement."""
    p0 = None
    total = None
    m = re.search(r"Measured\s+P\(0\)\s*=\s*([\d.]+)", stdout)
    if m:
        p0 = float(m.group(1))
    if p0 is None:
        m = re.search(r"P\(\|0_L>\)\s*=\s*([\d.]+)", stdout)
        if m:
            p0 = float(m.group(1))
    if p0 is None:
        m = re.search(r"Logical\s+\|0>\s*:\s*(\d+)", stdout)
        if m:
            p0 = int(m.group(1))
            total = _parse_shots(stdout)
    if p0 is None:
        m = re.search(r"Decoded logical statistics[:\s]*0:\s*(\d+)[\s\S]*?"
                      r"1:\s*(\d+)", stdout)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            p0 = a / (a + b)
    if p0 is None:
        m = re.search(r"Decoded logical statistics[:\s]*0:\s*(\d+)", stdout)
        if m:
            p0 = int(m.group(1))
            total = _parse_shots(stdout)
    if p0 is None:
        m = re.search(r"^\s*\|0>\s*:\s*(\d+)\s+shots", stdout, re.M)
        if m:
            p0 = int(m.group(1))
            total = _parse_shots(stdout)
    if p0 is None:
        # raw counts fallback: keys like '001 01' -> data bits = first 3
        counts = parse_counts(stdout)
        if counts:
            n = len(next(iter(counts)))
            if n >= 3:
                z = sum(v for k, v in counts.items()
                        if k[:3].count("0") >= 2)
                p0 = z / sum(counts.values())
    if p0 is None:
        return assert_true(False, f"bitflip: no decoded P(0) parsed "
                                  f"(head {stdout[:120]!r})", details)
    if total:
        p0 = p0 / total
    p_th = math.cos(theta / 2) ** 2
    err = abs(p0 - p_th)
    details.append(f"bitflip: decoded P(0)={p0:.4f} theory={p_th:.4f} "
                   f"err={err:.4f} tol={tol}")
    return assert_true(err <= tol, f"bitflip: decoded P(0) {p0:.4f} != "
                                   f"theory {p_th:.4f}", details)


def _parse_shots(stdout):
    m = re.search(r"Shots:\s*(\d+)", stdout)
    if m:
        return int(m.group(1))
    m = re.search(r"shots\s*=\s*(\d+)", stdout, re.I)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)\s+shots\b", stdout, re.I)
    if m:
        return int(m.group(1))
    return None


def check_counts_concentration(stdout, basis_a, basis_b, p_min, details,
                               label, tolerance=0.0):
    """Assert P(basis_a)+P(basis_b) >= p_min (within tolerance accounting for
    finite sampling: tolerance ~ 5 sigma of binomial)."""
    counts = parse_counts(stdout)
    if not counts:
        return assert_true(False, f"{label}: no bitstring counts found in stdout "
                                  f"(head: {stdout[:120]!r})", details)
    total = sum(counts.values())
    if total < 50:
        return assert_true(False, f"{label}: only {total} shots parsed", details)
    pa = counts.get(basis_a, 0) / total
    pb = counts.get(basis_b, 0) / total
    ok = pa + pb + tolerance >= p_min
    details.append(f"  {label}: P({basis_a})={pa:.4f} P({basis_b})={pb:.4f} "
                   f"(sum {pa + pb:.4f}, tol {tolerance:.3f}, need >= {p_min})")
    return ok


# ------------------------------------------------------------------ main



CHECKER_NAME = 'stabilizer'
CHECKER_PARAMS = {'frac_min': 0.98}


def run_tests(candidate_path: str) -> dict:
    rc, stdout, stderr = run_candidate(candidate_path, timeout=180)
    if rc != 0:
        return {
            "passed": False,
            "details": ["exit code {r}" .format(r=rc) + ": " + stderr.strip()[:500]],
        }
    details = []
    fn = globals()["check_" + CHECKER_NAME]
    passed = fn(stdout, details, **CHECKER_PARAMS)
    return {"passed": bool(passed), "details": details}
