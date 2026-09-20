from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "scripts" / "asi3_launch_grpo_direct.sh"
AI_LAUNCHER = ROOT / "scripts" / "ai_launch_sapo_direct.sh"
PROMOTION_LAUNCHER = ROOT / "scripts" / "run_sapo_three_state_promotion_eval.sh"


def test_asi3_launch_pins_all_eight_npus_and_clears_ambient_resume() -> None:
    source = LAUNCHER.read_text(encoding="utf-8")

    assert 'export NUM_NPU="8"' in source
    assert 'export NPU_DEVICE_MAP="balanced-layers"' in source
    assert 'export ASCEND_RT_VISIBLE_DEVICES="0,1,2,3,4,5,6,7"' in source
    assert 'export ASCEND_VISIBLE_DEVICES="0,1,2,3,4,5,6,7"' in source
    assert 'export RESUME_FROM="${ASI3_SAPO_RESUME_FROM:-}"' in source
    assert 'export ADAPTER_INIT="${ASI3_SAPO_ADAPTER_INIT:-}"' in source
    assert 'export SELF_REPAIR_ROUNDS="0"' in source
    assert "ASI3_SAPO_SELF_REPAIR_ROUNDS" not in source
    assert 'export INNER_EPOCHS="${ASI3_SAPO_INNER_EPOCHS:-1}"' in source
    assert 'export REPAIR_POLL_SECONDS="${ASI3_SAPO_REPAIR_POLL_SECONDS:-60}"' in source
    assert 'export CHECKPOINT_INTERVAL_SECONDS="${ASI3_SAPO_CHECKPOINT_SECONDS:-1800}"' in source
    assert 'export LOGIT_CLIP="${ASI3_SAPO_LOGIT_CLIP:-50.0}"' in source
    assert "evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt}" in source
    assert (
        "ASI3_SAPO_BENCHMARK_FILE:-evals/benchmarks/"
        "quantum_grpo_training_v7_targeted_integrity.txt" not in source
    )
    assert (
        "ASI3_SAPO_BENCHMARK_FILE:-evals/benchmarks/"
        "quantum_grpo_training_v6_runtime30_disjoint.txt" not in source
    )


def test_asi3_launch_pins_paths_and_all_generic_training_knobs() -> None:
    source = LAUNCHER.read_text(encoding="utf-8")
    assert 'LAUNCHER="${ASI3_SAPO_LAUNCHER:-$ROOT_DIR/' in source
    assert "ASI3_SAPO_ROOT:-/root/software/quantum-gpt" in source
    assert "ASI3_SAPO_MODEL_PATH:-$NAS_ROOT/models/Qwen3.6-27B" in source
    assert "$NAS_ROOT/outputs/checkpoints/qwen36_27b_sapo_ai" in source
    assert (
        "/root/work/software/quantum-gpt"
        not in source.split("# ---- fixed ASI3 SAPO settings", 1)[1]
    )
    assert "/root/work/filestorage/Qwen3.6-27B" not in source
    assert '"$NAS_ROOT/evals/runner/candidate_security.py"' in source
    assert '"$NAS_ROOT/evals/runner/single_candidate_eval.py"' in source
    pinned = {
        "NAS_ROOT",
        "MODEL_PATH",
        "CONFIG_FILE",
        "RUN_ID",
        "OUT",
        "NAS_CHECKPOINT_ROOT",
        "LOGDIR",
        "DEVICE",
        "TEMPERATURE",
        "TOP_P",
        "GSPO_CLIP_LOW",
        "GSPO_CLIP_HIGH",
        "ADVANTAGE_MODE",
        "FRONTIER_THRESHOLD",
        "MASTERED_THRESHOLD",
        "MIX_TARGETED",
        "MIX_NEIGHBOR",
        "MIX_REPLAY",
        "NEIGHBOR_WINDOW",
        "CIRCUIT_BREAKER_WINDOW",
        "TRUST_REGION_ON_VIOLATION",
        "TRUST_REGION_MAX_SEQ_KL",
        "TRUST_REGION_MAX_CLIP_FRACTION",
        "CIRCUIT_BREAKER_CLIP_FRACTION_LIMIT",
        "REWARD_MODE",
        "REWARD_PASS_MASS",
        "REWARD_SHAPED_MASS",
        "REWARD_JUDGE_MASS",
        "CURRICULUM_EMA_DECAY",
        "CURRICULUM_MIN_WEIGHT",
        "MIN_REWARD_STD",
        "ADAPTIVE_TEMP_STEP",
        "ADAPTIVE_TEMP_MAX",
    }
    for name in pinned:
        assert re.search(rf"^export {name}=", source, flags=re.MULTILINE), name


def test_asi3_launcher_exposes_loo_advantage_scale_with_shared_mad_default() -> None:
    """2026-08-24 (algorithm analyst): the measured small-drift problem
    (ratio_mean ~1.0003, seq_kl ~2e-4) comes from raw LOO advantages with
    scale 'none'. Dr.GRPO endorses a shared running MAD as the only batch-level
    scaling; the trainer already implements it (--loo-advantage-scale
    shared_mad) but NO launcher passed the flag, so it was dead code. The
    canonical ASI3 SAPO wrapper must default to shared_mad; the generic engine
    stays 'none' for other callers (ASI3 exports override it)."""
    source = LAUNCHER.read_text(encoding="utf-8")
    assert 'export LOO_ADVANTAGE_SCALE="${ASI3_SAPO_LOO_ADVANTAGE_SCALE:-shared_mad}"' in source

    generic = (ROOT / "scripts" / "asi2_launch_grpo_27b_selfeval.sh").read_text(encoding="utf-8")
    assert 'LOO_ADVANTAGE_SCALE="${LOO_ADVANTAGE_SCALE:-none}"' in generic
    assert '--loo-advantage-scale "$LOO_ADVANTAGE_SCALE"' in generic


def test_asi3_launcher_pins_escalated_learning_stack() -> None:
    """2026-09-01 (manager, entropy-blowup fix): RUN-12 at LR 2e-4 caused
    CAPABILITY EROSION — entropy exploded 0.055 -> 1.59 (28x), 16 trust-region
    violation windows, uniform rubric losses vs base (STANDUP #227b deep-cause
    analysis, .sapo-loop/STATUS.md). RUN-13 relaunched at LR 5e-5 (4x lower)
    with the now-working judge signal + entropy floor + recalibrated clips
    (STANDUP #233, verified in launch_config). The launcher DEFAULT must be
    the calibrated 5e-5 so ANY relaunch (box-side resurrector, manual resume)
    without an explicit override gets the safe stack — the 2e-4 default was
    the trap that would silently re-introduce the entropy blowup.
    (History: 2026-08-24/25 escalation raised 5e-5 -> 1e-4 -> 2e-4 for
    movement, but 2e-4 proved destructive at RUN-12; 5e-5 is the proven
    RUN-13 stack with the improved reward signal.)"""
    source = LAUNCHER.read_text(encoding="utf-8")
    assert 'export LR="${ASI3_SAPO_LR:-5e-5}"' in source
    assert 'export LORA_ALPHA="${ASI3_SAPO_LORA_ALPHA:-64}"' in source
    assert 'export LOO_ADVANTAGE_SCALE="${ASI3_SAPO_LOO_ADVANTAGE_SCALE:-shared_mad}"' in source
    # Rollback knob must keep existing.
    assert "ASI3_SAPO_LOO_ADVANTAGE_SCALE=none" in source


def test_asi3_launch_fails_before_side_effects_when_payload_is_incomplete(tmp_path: Path) -> None:
    env = os.environ.copy()
    env.update(
        {
            "ASI3_SAPO_ROOT": str(tmp_path / "missing-project"),
            "ASI3_SAPO_MODEL_PATH": str(tmp_path / "missing-model"),
            "SAPO_RUN_POINTER": str(tmp_path / "run-pointer"),
            "RESUME_FROM": "/stale/metrics.jsonl",
            "ADAPTER_INIT": "/stale/adapter",
            "ASCEND_RT_VISIBLE_DEVICES": "7",
        }
    )
    completed = subprocess.run(
        ["bash", str(LAUNCHER), "launch"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )

    assert completed.returncode != 0
    assert "required launch file missing" in completed.stderr
    assert not (tmp_path / "missing-project").exists()


def _run_launcher_past_preflight(
    tmp_path: Path, *, adapter_init: Path, run_id: str
) -> subprocess.CompletedProcess:
    """Run the launcher with a stub trainer launcher and tmp OUT/LOGDIR.

    The full preflight passes (real repo as NAS_ROOT, v8 manifest contract
    verified against the working tree), so execution reaches the ADAPTER_INIT
    gate — the branch under audit. The stub launcher echoes a sentinel so a
    failed gate is distinguishable from a gate that let launch proceed.
    """
    model_dir = tmp_path / "model"
    model_dir.mkdir(exist_ok=True)
    (model_dir / "config.json").write_text("{}", encoding="utf-8")
    stub = tmp_path / "stub-launcher.sh"
    stub.write_text("#!/usr/bin/env bash\necho LAUNCHER-REACHED\n", encoding="utf-8")
    stub.chmod(0o755)
    env = os.environ.copy()
    env.update(
        {
            "ASI3_SAPO_ROOT": str(ROOT),
            "ASI3_SAPO_MODEL_PATH": str(model_dir),
            "ASI3_SAPO_ADAPTER_INIT": str(adapter_init),
            "ASI3_SAPO_LAUNCHER": str(stub),
            "ASI3_SAPO_OUT": str(tmp_path / "out"),
            "ASI3_SAPO_LOGDIR": str(tmp_path / "logs"),
            "ASI3_SAPO_RUN_ID": run_id,
            "SAPO_RUN_POINTER": str(tmp_path / "run-pointer"),
        }
    )
    return subprocess.run(
        ["bash", str(LAUNCHER), "launch"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )


def test_asi3_launcher_fails_closed_when_adapter_init_config_missing(tmp_path: Path) -> None:
    """An adapter-init dir without adapter_config.json must abort the launch."""
    adapter = tmp_path / "missing-config-adapter"
    adapter.mkdir()

    completed = _run_launcher_past_preflight(
        tmp_path, adapter_init=adapter, run_id="audit-missing-config"
    )

    assert completed.returncode != 0
    assert "adapter init is incomplete" in completed.stderr
    assert "LAUNCHER-REACHED" not in completed.stdout + completed.stderr


def test_asi3_launcher_fails_closed_when_adapter_init_weights_missing(tmp_path: Path) -> None:
    """An adapter-init dir with config but NO weights must abort the launch.

    The trainer's own completeness rule (peft_checkpoint_complete) requires
    adapter_config.json PLUS adapter_model.safetensors/.bin. A config-only dir
    would otherwise pass the gate, boot the full trainer (15-30 min model
    load), and only then crash inside PeftModel.from_pretrained.
    """
    adapter = tmp_path / "config-only-adapter"
    adapter.mkdir()
    (adapter / "adapter_config.json").write_text('{"r": 16, "lora_alpha": 64}\n', encoding="utf-8")

    completed = _run_launcher_past_preflight(
        tmp_path, adapter_init=adapter, run_id="audit-weights-missing"
    )

    assert completed.returncode != 0
    assert "adapter init is incomplete" in completed.stderr
    assert "LAUNCHER-REACHED" not in completed.stdout + completed.stderr


def test_asi3_launcher_rejects_adapter_init_rank_alpha_mismatch(tmp_path: Path) -> None:
    """The gate must reject an adapter whose r/alpha contradicts the launch stack."""
    adapter = tmp_path / "rank-mismatch-adapter"
    adapter.mkdir()
    (adapter / "adapter_config.json").write_text('{"r": 8, "lora_alpha": 32}\n', encoding="utf-8")
    (adapter / "adapter_model.safetensors").write_bytes(b"weights")

    completed = _run_launcher_past_preflight(
        tmp_path, adapter_init=adapter, run_id="audit-rank-mismatch"
    )

    assert completed.returncode != 0
    assert "warm adapter LoRA mismatch" in completed.stderr
    assert "LAUNCHER-REACHED" not in completed.stdout + completed.stderr


def _ids(path: Path) -> set[str]:
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def test_asi3_training_manifest_is_disjoint_from_every_promotion_holdout() -> None:
    manifest = ROOT / "evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt"
    source = manifest.read_text(encoding="utf-8")
    training = _ids(manifest)
    assert "# reference_execution_verified=true runs=3" in source
    assert "# task_contract_sha256=" in source
    assert not [task_id for task_id in training if task_id.startswith("qc-")]
    assert len(training) == 20
    promotion = [
        ROOT / "evals/benchmarks/quantum_generalization_holdout_v1.txt",
        ROOT / "evals/benchmarks/quantum_generalization_holdout_v2_hard.txt",
        ROOT / "evals/benchmarks/quantum_generalization_holdout_v3_multi_framework.txt",
        ROOT / "evals/benchmarks/qwen36_27b_quantum_holdout_v1.txt",
        ROOT / "evals/benchmarks/sapo_promotion_holdout_v1_18.txt",
    ]
    for holdout in promotion:
        assert training.isdisjoint(_ids(holdout)), holdout


def test_next_launch_v9_assets_are_local_and_bundle_member() -> None:
    """2026-09-01 CONFIG-AUDIT (STANDUP #238b/#239, manager decision): the NEXT
    SAPO launch uses BENCHMARK_FILE=v9 (jsonl-derived tasks — 12 in wave 1,
    36 after waves 2-3 landed, contract 143613b9...); the launcher default
    stays v8 (manager-owned). This pin keeps the v9 launch asset chain
    deploy-complete: manifest header invariants, ALL task dirs, disjointness,
    and bundle-member listing — r21 FINAL v2 (180 members) did NOT include v9,
    so a v9 launch would fail-closed on the box ('required launch file
    missing'). The count is asserted dynamically vs the manifest's own
    targeted= header (waves grow it; the header is the source of truth)."""
    manifest = ROOT / "evals/benchmarks/quantum_grpo_training_v9_rl_questions_v2.txt"
    source = manifest.read_text(encoding="utf-8")
    tasks = _ids(manifest)
    targeted = re.search(r"# targeted=(\d+)", source)
    assert targeted is not None
    assert len(tasks) == int(targeted.group(1)) >= 12
    assert "# task_contract_sha256=" in source
    assert "# reference_execution_verified=true runs=3" in source
    assert f"# targeted={len(tasks)} deterministic=0 semantic=0" in source
    assert "# source=quantum_rl_questions_v2.jsonl sha256=" in source
    assert "# required_import_roots=" in source
    assert not {t for t in tasks if t.startswith("qc-")}
    for task_id in tasks:
        task_dir = ROOT / "evals" / "tasks" / "quantum" / task_id
        for name in ("candidate.py", "task.json", "tests.py"):
            assert (task_dir / name).is_file(), f"{task_id}/{name}"
    v8 = _ids(ROOT / "evals/benchmarks/quantum_grpo_training_v8_holdout_adjacent.txt")
    assert tasks.isdisjoint(v8)
    for holdout in (
        ROOT / "evals/benchmarks/quantum_generalization_holdout_v1.txt",
        ROOT / "evals/benchmarks/quantum_generalization_holdout_v2_hard.txt",
        ROOT / "evals/benchmarks/quantum_generalization_holdout_v3_multi_framework.txt",
        ROOT / "evals/benchmarks/qwen36_27b_quantum_holdout_v1.txt",
        ROOT / "evals/benchmarks/sapo_promotion_holdout_v1_18.txt",
    ):
        assert tasks.isdisjoint(_ids(holdout)), holdout
    # Deploy-readiness: the next bundle build must carry all 37 v9 assets
    # (manifest + 12 dirs x 3 files). tmp/r18_members.txt is the member list
    # the bundle builder consumes (.sapo-loop/sapo_bundle_closure_check.py).
    members_file = ROOT / "tmp" / "r18_members.txt"
    assert members_file.is_file(), (
        f"bundle member list missing: {members_file} — deploy lane must "
        "regenerate it before the next launch"
    )
    members = set(members_file.read_text(encoding="utf-8").splitlines())
    expected_members = {str(manifest.relative_to(ROOT))} | {
        f"evals/tasks/quantum/{task_id}/{name}"
        for task_id in tasks
        for name in ("candidate.py", "task.json", "tests.py")
    }
    missing = sorted(expected_members - members)
    assert not missing, f"v9 launch assets not in bundle member list: {missing}"


def test_asi3_launcher_guards_frozen_sapo_promotion_holdout() -> None:
    source = LAUNCHER.read_text(encoding="utf-8")
    holdout = "$NAS_ROOT/evals/benchmarks/sapo_promotion_holdout_v1_18.txt"

    # It must be preflight-required and also checked for task-ID overlap.
    assert source.count(holdout) == 2


def test_asi3_duplicate_guard_checks_pid_identity_not_kill_zero_only() -> None:
    source = LAUNCHER.read_text(encoding="utf-8")

    assert 'ps -p "$existing_pid" -o args=' in source
    assert 'existing_cmd" == *"training/grpo_trainer.py"*' in source
    assert "pgrep -f 'training/[g]rpo_trainer.py'" in source


def test_ai_sapo_entrypoint_pins_canonical_ai_paths_and_preserves_overrides() -> None:
    source = AI_LAUNCHER.read_text(encoding="utf-8")

    assert "/root/software/quantum-gpt" in source
    assert "$AI_ROOT/models/Qwen3.6-27B" in source
    assert "$AI_ROOT/outputs/checkpoints/qwen36_27b_sapo_ai" in source
    assert "$AI_ROOT/outputs/sapo-27b-ai-$AI_RUN_ID" in source
    assert "AI_SAPO_ROOT:-${ASI3_SAPO_ROOT:-" in source
    assert "AI_SAPO_MODEL_PATH:-${ASI3_SAPO_MODEL_PATH:-" in source
    assert "AI_SAPO_ADAPTER_INIT:-${ASI3_SAPO_ADAPTER_INIT:-" in source
    assert "AI_SAPO_RESUME_FROM:-${ASI3_SAPO_RESUME_FROM:-" in source


def test_ai_sapo_entrypoint_forwards_ai_root_before_any_side_effect(tmp_path: Path) -> None:
    missing_root = tmp_path / "ai-project"
    env = os.environ.copy()
    env.update(
        {
            "AI_SAPO_ROOT": str(missing_root),
            "AI_SAPO_MODEL_PATH": str(tmp_path / "ai-model"),
            "SAPO_RUN_POINTER": str(tmp_path / "run-pointer"),
        }
    )
    completed = subprocess.run(
        ["bash", str(AI_LAUNCHER), "launch"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )

    assert completed.returncode != 0
    assert (
        f"required launch file missing: {tmp_path / 'ai-model' / 'config.json'}" in completed.stderr
    )
    assert "/root/work/software/quantum-gpt" not in completed.stderr
    assert not missing_root.exists()


def test_sapo_launchers_fail_closed_for_semantic_stdout_reward() -> None:
    source = LAUNCHER.read_text(encoding="utf-8")

    assert 'composition_fields.get("semantic", "-1")' in source
    assert "semantic-stdout training is circuit-broken" in source


def test_promotion_eval_defaults_to_canonical_ai_model_tree() -> None:
    source = PROMOTION_LAUNCHER.read_text(encoding="utf-8")

    assert 'SAPO_PROMOTION_ROOT="${SAPO_PROMOTION_ROOT:-/root/work/software/quantum-gpt}"' in source
    assert "/root/work/filestorage/Qwen3.8-27B" in source
    assert "Qwen3.6-27B" not in source


ASI2_LAUNCHER = ROOT / "scripts" / "asi2_launch_grpo_27b_selfeval.sh"


def _run_stop(logdir: Path, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["NAS_ROOT"] = str(logdir.parent)
    env["LOGDIR"] = str(logdir)
    env["OUT"] = str(logdir / "out")
    env["NAS_CHECKPOINT_ROOT"] = str(logdir / "nas-checkpoints")
    env.pop("ASI3_SAPO_ROOT", None)
    env.pop("ASI3_SAPO_LOGDIR", None)
    env.pop("ASI3_SAPO_LAUNCHER", None)
    env.update(extra_env or {})
    return subprocess.run(
        ["bash", str(ASI2_LAUNCHER), "stop"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def _fake_trainer(tmp_path: Path, *, ignore_term: bool) -> int:
    """Start a live python process whose argv matches the trainer pattern."""
    code = (
        "import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(600)"
        if ignore_term
        else "import time; time.sleep(600)"
    )
    proc = subprocess.Popen(
        ["python3", "-c", code, "training/grpo_trainer.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return proc.pid


def _alive(pid: int) -> bool:
    """True only for a live (non-zombie) process. kill(pid, 0) alone reports
    True for an unreaped zombie child of the test runner, which would make a
    successfully SIGKILLed fake trainer look still-alive."""
    try:
        out = subprocess.run(
            ["ps", "-p", str(pid), "-o", "stat="], capture_output=True, text=True, timeout=10
        )
    except Exception:
        return False
    stat = out.stdout.strip()
    if not stat:
        return False
    return not stat.startswith("Z")


def test_stop_kills_trainer_even_when_pidfile_is_stale(tmp_path: Path) -> None:
    """2026-08-24 stop-script bug (manager): ``asi3_launch_grpo_direct.sh stop``
    failed to kill the live trainer (PID/pattern mismatch — the pidfile did not
    resolve the real process), which kept training ~30 min until a manual kill.
    The stop path must fall back to resolving the trainer by process pattern
    when the pidfile is stale/wrong instead of silently doing nothing.
    """
    logdir = tmp_path / "logs"
    logdir.mkdir()
    (logdir / "grpo_27b_selfeval.pid").write_text("999999\n", encoding="utf-8")  # stale dead pid
    (logdir / "grpo_27b_checkpoint_sync.pid").write_text("999998\n", encoding="utf-8")
    (logdir / "grpo_27b_repair_sidecar.pid").write_text("999997\n", encoding="utf-8")
    fake_pid = _fake_trainer(tmp_path, ignore_term=False)
    try:
        assert _alive(fake_pid)
        completed = _run_stop(logdir)
        assert completed.returncode == 0, completed.stderr
        assert not _alive(fake_pid), "stale pidfile must not hide the live trainer"
        assert not (logdir / "grpo_27b_selfeval.pid").exists()
    finally:
        if _alive(fake_pid):
            os.kill(fake_pid, 9)


def test_stop_escalates_to_kill_when_trainer_ignores_term(tmp_path: Path) -> None:
    """The second (KILL-escalation) loop of the stop path was dead code: it
    re-read pidfiles that the first loop had already removed, so a trainer that
    ignores SIGTERM survived forever. The escalation must use the originally
    resolved pids and must actually deliver SIGKILL.
    """
    logdir = tmp_path / "logs"
    logdir.mkdir()
    fake_pid = _fake_trainer(tmp_path, ignore_term=True)
    (logdir / "grpo_27b_selfeval.pid").write_text(f"{fake_pid}\n", encoding="utf-8")
    try:
        assert _alive(fake_pid)
        completed = _run_stop(logdir)
        assert completed.returncode == 0, completed.stderr
        assert not _alive(fake_pid), "TERM-ignoring trainer must be SIGKILLed"
    finally:
        if _alive(fake_pid):
            os.kill(fake_pid, 9)


def test_sapo_launchers_use_the_2048_token_budget_and_seq_length_coupling() -> None:
    """Lock the proven generation budget and its max-seq-length coupling.

    The 512/1024 token caps were the run-7 OOM-era stopgap; run 9 and the
    08-23 fence-stop run proved 2048 completions survive the 8-card layout
    (forced layer checkpointing 64/64 + per-candidate backward) and reach 0%
    truncation where the 1024 cap cut solutions mid-code (avg 1019.75 tokens,
    checker fail -> reward 0). The trainer's policy-math path truncates
    prompt+completion at --max-seq-length, so the seq length MUST leave
    headroom above the generation cap or the tail tokens silently drop out of
    the SAPO token gate even when generation succeeds (2026-08-24 audit).
    """
    asi3 = LAUNCHER.read_text(encoding="utf-8")
    assert 'export MAX_NEW_TOKENS="${ASI3_SAPO_MAX_NEW_TOKENS:-2048}"' in asi3
    assert 'export MAX_ADAPTIVE_NEW_TOKENS="${ASI3_SAPO_MAX_ADAPTIVE_NEW_TOKENS:-2048}"' in asi3
    assert 'export MAX_SEQ_LENGTH="${ASI3_SAPO_MAX_SEQ_LENGTH:-3072}"' in asi3
    assert ":-512}" not in asi3
    assert ":-1024}" not in asi3

    generic = (ROOT / "scripts" / "asi2_launch_grpo_27b_selfeval.sh").read_text(encoding="utf-8")
    assert 'INNER_EPOCHS="${INNER_EPOCHS:-1}"' in generic
    assert 'CHECKPOINT_INTERVAL_SECONDS="${CHECKPOINT_INTERVAL_SECONDS:-1800}"' in generic
    assert 'MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-2048}"' in generic
    assert 'MAX_SEQ_LENGTH="${MAX_SEQ_LENGTH:-3072}"' in generic
    assert 'MAX_ADAPTIVE_NEW_TOKENS="${MAX_ADAPTIVE_NEW_TOKENS:-$MAX_NEW_TOKENS}"' in generic


def test_asi3_launcher_pins_repair_converted_jsonl_against_ambient_env() -> None:
    """2026-08-24 bug-hunt: asi2_launch_grpo_27b_selfeval.sh reads
    REPAIR_CONVERTED_JSONL with a default, but asi3_launch_grpo_direct.sh did
    not export it — a persistent-webshell `export REPAIR_CONVERTED_JSONL=...`
    would silently redirect the repair-conversion ledger, making
    count_repair_conversions() see 0 and false-tripping the
    all_fail_without_repair circuit breaker (the 08-19 halt class).
    """
    source = LAUNCHER.read_text(encoding="utf-8")
    assert (
        'export REPAIR_CONVERTED_JSONL="${ASI3_SAPO_REPAIR_CONVERTED_JSONL:-$OUT/repair_stage/repair_converted.jsonl}"'
        in source
    )


def test_asi3_launcher_exports_every_generic_env_the_asi2_launcher_reads() -> None:
    """Ambient-shell pollution lock: every environment variable the generic
    ASI2 launcher reads (outside its own script-internal variables) must be
    explicitly exported by the ASI3 launcher, so a stale persistent-webshell
    export can never silently change a launch."""
    import re as _re

    generic = (ROOT / "scripts" / "asi2_launch_grpo_27b_selfeval.sh").read_text(encoding="utf-8")
    internal = {
        "ADAPTER_DIR",
        "ALL_CHECKPOINTS",
        "CHECKPOINT_PID_FILE",
        "CHECKPOINT_SYNC_SCRIPT",
        "COUNT",
        "CP",
        "EXISTING",
        "INTERVAL",
        "LOGFILE",
        "PID",
        "PID_FILE",
        "REPAIR_PID_FILE",
        "JUDGE_BRIDGE_PID_FILE",
        "RETAIN",
        "SNAPSHOT_DIR",
        "STEP_DIRS",
        "STEP_LABEL",
        "TRAIN_LOG",
        "TZ",
        "BASH_SOURCE",
        "RANDOM",
        "OUT",
        "RUN_ID",
    }
    read_envs = (
        set(_re.findall(r"\$\{([A-Z][A-Z0-9_]+):-", generic))
        | set(_re.findall(r"\$([A-Z][A-Z0-9_]+)", generic))
    ) - internal
    launcher = LAUNCHER.read_text(encoding="utf-8")
    exported = set(_re.findall(r"^export ([A-Z][A-Z0-9_]+)=", launcher, flags=_re.MULTILINE))
    missing = sorted(read_envs - exported)
    assert not missing, f"ambient-pollution vectors not pinned by asi3 launcher: {missing}"


def test_asi3_launcher_wires_r10_preventive_greedy_and_entropy_floor() -> None:
    """Debug-lane F-A 2026-08-26: greedy-rollout-fraction / entropy-floor /
    entropy-floor-weight must be passed EXPLICITLY by the launcher chain so the
    boot echo and launch_config are truthful; ASI3_SAPO_* env overrides tune
    without editing the launcher. Trainer defaults: 0.4 / 1.5 / 0.01."""
    source = LAUNCHER.read_text(encoding="utf-8")
    assert 'export GREEDY_ROLLOUT_FRACTION="${ASI3_SAPO_GREEDY_ROLLOUT_FRACTION:-0.4}"' in source
    assert 'export ENTROPY_FLOOR="${ASI3_SAPO_ENTROPY_FLOOR:-1.5}"' in source
    assert 'export ENTROPY_FLOOR_WEIGHT="${ASI3_SAPO_ENTROPY_FLOOR_WEIGHT:-0.01}"' in source
    assert (
        "GREEDY_ROLLOUT_FRACTION=${GREEDY_ROLLOUT_FRACTION} "
        "ENTROPY_FLOOR=${ENTROPY_FLOOR} ENTROPY_FLOOR_WEIGHT=${ENTROPY_FLOOR_WEIGHT}" in source
    )
    generic = (ROOT / "scripts" / "asi2_launch_grpo_27b_selfeval.sh").read_text(encoding="utf-8")
    assert '--greedy-rollout-fraction "$GREEDY_ROLLOUT_FRACTION"' in generic
    assert '--entropy-floor "$ENTROPY_FLOOR"' in generic
    assert '--entropy-floor-weight "$ENTROPY_FLOOR_WEIGHT"' in generic
    assert 'GREEDY_ROLLOUT_FRACTION="${GREEDY_ROLLOUT_FRACTION:-0.4}"' in generic
    assert 'ENTROPY_FLOOR="${ENTROPY_FLOOR:-1.5}"' in generic
    assert 'ENTROPY_FLOOR_WEIGHT="${ENTROPY_FLOOR_WEIGHT:-0.01}"' in generic


def test_asi3_launcher_wires_run8_oom_fix_entropy_token_cap() -> None:
    """Run-8 OOM fix (2026-08-26): --entropy-token-cap must be passed
    EXPLICITLY by the launcher chain (boot echo truthful), default 256,
    ASI3_SAPO_ENTROPY_TOKEN_CAP override."""
    source = LAUNCHER.read_text(encoding="utf-8")
    assert 'export ENTROPY_TOKEN_CAP="${ASI3_SAPO_ENTROPY_TOKEN_CAP:-256}"' in source
    assert "ENTROPY_TOKEN_CAP=${ENTROPY_TOKEN_CAP}" in source
    generic = (ROOT / "scripts" / "asi2_launch_grpo_27b_selfeval.sh").read_text(encoding="utf-8")
    assert '--entropy-token-cap "$ENTROPY_TOKEN_CAP"' in generic
    assert 'ENTROPY_TOKEN_CAP="${ENTROPY_TOKEN_CAP:-256}"' in generic


def test_asi2_launcher_starts_judge_bridge_only_when_batch_judge_on() -> None:
    """2026-08-27 (JUDGE BRIDGE lane): the box-local judge bridge sidecar must
    launch ONLY when BATCH_COMPARATIVE_JUDGE=1 (inert otherwise) and must be
    stopped by the stop path."""
    generic = (ROOT / "scripts" / "asi2_launch_grpo_27b_selfeval.sh").read_text(encoding="utf-8")
    assert 'JUDGE_BRIDGE_PID_FILE="$LOGDIR/grpo_27b_judge_bridge.pid"' in generic
    assert 'if [[ "$BATCH_COMPARATIVE_JUDGE" == "1" ]]; then' in generic
    assert "sapo_judge_bridge.py" in generic
    assert '--queue-dir "$OUT/judge_bridge"' in generic
    assert '--port "${JUDGE_BRIDGE_PORT:-56237}"' in generic
    assert '"$JUDGE_BRIDGE_PID_FILE"' in generic  # stop list includes the bridge


def test_launcher_chain_pins_dp4_max_tokens_and_bridge_stop() -> None:
    """Critical review C1/H3 (2026-08-27): the launcher must pass a dp4-specific
    token budget (never the frozen-judge 256) and the stop path must pattern-
    fallback + pidfile-clean the judge bridge."""
    generic = (ROOT / "scripts" / "asi2_launch_grpo_27b_selfeval.sh").read_text(encoding="utf-8")
    assert "--judge-dp4-max-tokens" in generic
    assert 'JUDGE_DP4_MAX_TOKENS="${JUDGE_DP4_MAX_TOKENS:-4096}"' in generic
    assert "'sapo_judge_[b]ridge.py'" in generic  # stop pattern fallback
    assert '"$JUDGE_BRIDGE_PID_FILE"' in generic  # stop pidfile cleanup list
    launcher = LAUNCHER.read_text(encoding="utf-8")
    assert 'export JUDGE_DP4_MAX_TOKENS="${ASI3_SAPO_JUDGE_DP4_MAX_TOKENS:-4096}"' in launcher


def test_launch_contract_pins_entropy_floor_weight_and_greedy_fraction() -> None:
    """2026-09-01 (fixer lane): settle the ENTROPY_FLOOR_WEIGHT divergence.

    The launcher exports ENTROPY_FLOOR_WEIGHT=0.01 (the documented RUN-13
    value) and passes it EXPLICITLY to the trainer, so the trainer CLI
    default (0.03, T1c strengthening 2026-08-27) can never silently apply at
    launch. This test pins BOTH sides plus the launchplan.md §3b launch
    command block (GREEDY_ROLLOUT_FRACTION=0.4 / ENTROPY_FLOOR_WEIGHT=0.01)
    so any future drift on either side — launcher default, trainer default,
    or the launch template — fails loudly instead of launching mis-tuned.
    """
    launcher = LAUNCHER.read_text(encoding="utf-8")
    # 1) launcher exports 0.01 = the RUN-13 documented value (wins at launch)
    assert 'export ENTROPY_FLOOR_WEIGHT="${ASI3_SAPO_ENTROPY_FLOOR_WEIGHT:-0.01}"' in launcher
    assert 'export GREEDY_ROLLOUT_FRACTION="${ASI3_SAPO_GREEDY_ROLLOUT_FRACTION:-0.4}"' in launcher
    # 2) trainer CLI default is 0.03 (T1c strengthening) — the divergence from
    #    the launcher's 0.01 is DELIBERATE and pinned here: changing either
    #    side is a loud, reviewed event.
    trainer_src = (ROOT / "training" / "grpo_trainer.py").read_text(encoding="utf-8")
    m = re.search(r'"--entropy-floor-weight"[\s\S]*?default=([0-9.]+)', trainer_src)
    assert m is not None, "--entropy-floor-weight arg default not found in trainer"
    assert m.group(1) == "0.03", f"trainer --entropy-floor-weight default drifted to {m.group(1)}"
    # 3) the generic launcher forwards the exported value explicitly (never
    #    lets the trainer default apply silently)
    generic = (ROOT / "scripts" / "asi2_launch_grpo_27b_selfeval.sh").read_text(encoding="utf-8")
    assert '--entropy-floor-weight "$ENTROPY_FLOOR_WEIGHT"' in generic
    # 4) launchplan.md §3b pins BOTH knobs on the launch command so no future
    #    launch drifts from the documented RUN-13 settings (fixer fix 1).
    plan = (ROOT / ".sapo-loop" / "launchplan.md").read_text(encoding="utf-8")
    assert "AI_SAPO_GREEDY_ROLLOUT_FRACTION=0.4" in plan
    assert "AI_SAPO_ENTROPY_FLOOR_WEIGHT=0.01" in plan


def test_ai_wrapper_aliases_every_launchplan_env_knob() -> None:
    """2026-09-01 (fixer lane): the launchplan section 3b launch command uses
    AI_SAPO_* names — the wrapper must alias EACH of them to ASI3_SAPO_* or
    the knob is SILENTLY DROPPED (the asi3 launcher only reads ASI3_SAPO_*).
    Found live: AI_SAPO_BENCHMARK_FILE was NOT aliased — the v9 benchmark pin
    would have been dropped and the next launch would have trained on
    v8_holdout_adjacent instead. This test parses section 3b itself, so a
    future knob added to the command is enforced automatically.
    """
    wrapper = AI_LAUNCHER.read_text(encoding="utf-8")
    plan = (ROOT / ".sapo-loop" / "launchplan.md").read_text(encoding="utf-8")
    cmd_block = plan.split("### 3b. Launch command", 1)[1].split("```", 2)[1]
    ai_knobs = sorted(set(re.findall(r"AI_SAPO_([A-Z0-9_]+)=", cmd_block)))
    missing = [k for k in ai_knobs if f"AI_SAPO_{k}" not in wrapper]
    assert not missing, (
        f"wrapper does not alias launchplan section 3b knobs: {missing} "
        "(silent drop = wrong benchmark/hyperparams at launch)"
    )
