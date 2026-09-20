import importlib.util
import json
from pathlib import Path

# C-0002 acceptance: verdict_<step>.json carries "per-task pass + composite".
# RED 2026-09-17: tmp/c0002_collect_verdict.py emitted pass_adapter/pass_base
# and per-task maps but NO composite fields, and its beats_base was a bare
# pass-count compare that silently disagrees with the pinned metric
# (harness/beats_base.py, card C-0013 pin: composite tiebreak, never
# re-implement). The collector must use the pinned composite
# (scripts/verdict_holdout.composite) and the pinned beats_base comparison.

COLLECTOR = Path(__file__).resolve().parents[2] / "tmp" / "c0002_collect_verdict.py"

TASKS = [
    "quantum_gate_alias_normalization",
    "quantum_phase_estimation_circuit",
    "quantum_qaoa_maxcut",
    "quantum_superdense_coding",
    "quantum_grover_oracle_diffusion",
    "quantum_density_matrix_partial_trace",
    "quantum_error_correction_shor_9qubit",
    "quantum_trotterized_hamiltonian_evolution",
    "quantum_channel_depolarizing",
    "quantum_ghz_state_witness",
    "quantum_pennylane_vqe_h2",
    "quantum_cirq_qaoa_line",
    "quantum_braket_bell_state",
    "quantum_qiskit_qft_entangled",
    "quantum_qiskit_stabilizer_5qubit_code",
    "quantum_pennylane_qml_iris_classification",
    "quantum_phase_register_roundtrip",
    "quantum_binary_measurement_decoder",
]


def _load():
    spec = importlib.util.spec_from_file_location("c0002_collect_verdict", COLLECTOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _slice(start, a_overall, a_pass, b_overall, b_pass):
    ids = TASKS[start : start + 6]
    recs = []
    for _i, tid in enumerate(ids):
        recs.append(
            dict(model="adapter", task_id=tid, passed=bool(a_pass), scores=dict(overall=a_overall))
        )
        recs.append(
            dict(model="base", task_id=tid, passed=bool(b_pass), scores=dict(overall=b_overall))
        )
    return dict(task_ids=ids, records=recs)


def _run(slices):
    mod = _load()
    payloads = iter(slices)

    def fake_fetch(port, remote, local):  # offline: write the next slice
        Path(local).write_text(json.dumps(next(payloads)), encoding="utf-8")

    mod.fetch_file = fake_fetch

    def fake_exec(port, cmd, timeout=120):
        if "md5sum" in cmd:
            return "\n".join(
                "aa%d  adapter/%s.py" % (i, t) + "\n" + "bb%d  base/%s.py" % (i, t)
                for i, t in enumerate(TASKS[:3])
            )
        if "cat" in cmd:
            return (
                "LEG_FAILCLOSED adapter-applied adapter-probe-differs "
                "stage=adapter_applied stage=adapter_probe_differs"
            )
        return json.dumps(next(payloads))

    mod.exec_cmd = fake_exec
    mod.sys.argv = [
        "c0002_collect_verdict.py",
        "--step",
        "900",
        "--leg-log",
        "/tmp/leg_c0002_step900.log",
        "--adapter",
        "/x/outputs/run/step_000100_adapter",
    ]
    out = Path(tempfile.mkdtemp(prefix="c0002_t_")) / "verdict_step900.json"
    (out.parent / "outputs").mkdir()  # repo layout: ROOT/outputs/
    saved_root = mod.ROOT
    mod.ROOT = out.parent
    try:
        rc = mod.main()
    finally:
        mod.ROOT = saved_root
    assert rc == 0
    written = out.parent / "outputs" / "verdict_step900.json"
    return json.loads(written.read_text(encoding="utf-8"))


import tempfile


def test_verdict_carries_pinned_composites_and_beats_rule():
    verdict = _run(
        [
            _slice(0, 0.9, True, 0.5, False),
            _slice(6, 0.8, True, 0.5, False),
            _slice(12, 0.7, True, 0.5, False),
        ]
    )
    assert verdict["pass_adapter"] == "18/18"
    assert verdict["pass_base"] == "0/18"
    # composite = 0.70*mean(overall) + 0.30*pass@1 fraction
    assert abs(verdict["composite_adapter"] - (0.7 * 0.8 + 0.3 * 1.0)) < 1e-9
    assert abs(verdict["composite_base"] - (0.7 * 0.5 + 0.3 * 0.0)) < 1e-9
    assert verdict["beats_base"] is True
    assert verdict["beats_rule"] == "pass-count"
    assert verdict["adapter_applied_marker"] is True
    assert len(verdict["per_task_adapter"]) == 18
    # C-0040 class: verdicts must pin the frozen bench + scorer chain or
    # goal_done rejects them (the s97 verdicts died on exactly this)
    assert len(verdict["holdout_sha256"]) == 64
    assert verdict["scorer_shas"], "scorer chain pins missing"


def test_equal_pass_count_uses_composite_tiebreak():
    # 9/18 vs 9/18 on pass; identical pass pattern; adapter rubric higher ->
    # the pinned metric must decide via composite-tiebreak, not pass-count
    s = []
    for start in (0, 6, 12):
        ids = TASKS[start : start + 6]
        recs = []
        for j, tid in enumerate(ids):
            gidx = start + j
            a_pass = gidx % 2 == 0
            recs.append(
                dict(
                    model="adapter",
                    task_id=tid,
                    passed=a_pass,
                    scores=dict(overall=0.9 if a_pass else 0.2),
                )
            )
            recs.append(dict(model="base", task_id=tid, passed=a_pass, scores=dict(overall=0.5)))
        s.append(dict(task_ids=ids, records=recs))
    verdict = _run(s)
    assert verdict["pass_adapter"] == "9/18"
    assert verdict["pass_base"] == "9/18"
    assert verdict["beats_rule"] == "composite-tiebreak"
    assert verdict["beats_base"] is True
