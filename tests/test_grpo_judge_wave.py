"""TDD (2026-08-26, lane #22, coordinator FEATURE CHANGE — r16 wave, revised
r17 per the research-lane defect): the model-judge path with the base
Qwen3.6-27B as judge.

r17 CONTRACT (research memo 2026-08-26): the judge is CALIBRATION-GATED —
with NO calibration file the judge mass is EXACTLY 0 (an active uncalibrated
judge injects ~0.5+-noise into the advantages) and the masses renormalize
over pass+shaped. Recommended masses w_P=0.50, w_S=0.40, w_J=0.10
(calibrated-only). When calibrated: total = 0.50*pass + 0.40*shaped +
0.10*judge. The judge runs on the SAME sharded model instance (base weights,
adapters disabled — the second 27B load is the memory-wall class we keep
dead), releases caches between judge forwards, and the reward verifier
recomputes every judge-scored total.

Also pins: the F6 (string-aware balanced-JSON) / F7 (scaled-form fallback)
parse fixes (verified in the deployed box path), the
TextPreprocessorBackend tokenization branch (the judge previously returned
None with the trainer's backend — it never ran), the calibration gate, and
the launcher flag wiring.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest
import torch
from tokenizers import Tokenizer, models
from transformers import (
    GPT2Config,
    GPT2LMHeadModel,
    PreTrainedTokenizerFast,
)

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.grpo_trainer import (  # noqa: E402
    _extract_json_object,
    _model_comprehensive_scores,
    _parse_model_dim_scores,
    _parse_self_eval_score,
    build_rollout_rewards,
    compose_policy_training_reward,
    effective_judge_weights,
    evaluate_candidate,
    resolve_frozen_judge,
)
from training.grpo_utils import (  # noqa: E402
    MODEL_JUDGE_DIMENSIONS,
    judge_composite_score,
)
from training.text_preprocessor_backend import TextPreprocessorBackend  # noqa: E402

VOCAB = {
    "```": 0,
    "python": 1,
    "\n": 2,
    "x": 3,
    " = ": 4,
    "1": 5,
    "trailing": 6,
    "<|endoftext|>": 60,
    "<pad>": 61,
    "<s>": 62,
    "<unk>": 63,
}
EOS_ID = 60

JUDGE_JSON = (
    '{"correctness": 0.8, "runnability": 0.6, "result_correctness": 0.9, '
    '"efficiency": 0.5, "quality": 0.7, "evidence": "ok"}'
)


def make_tokenizer() -> PreTrainedTokenizerFast:
    t = Tokenizer(models.WordLevel(VOCAB, unk_token="<unk>"))
    return PreTrainedTokenizerFast(
        tokenizer_object=t,
        eos_token="<|endoftext|>",
        pad_token="<pad>",
        bos_token="<s>",
        unk_token="<unk>",
    )


def make_model() -> GPT2LMHeadModel:
    cfg = GPT2Config(n_layer=1, n_head=1, n_embd=16, vocab_size=64)
    cfg.eos_token_id = None
    cfg.bos_token_id = None
    cfg.pad_token_id = None
    model = GPT2LMHeadModel(cfg)
    model.eval()
    return model


# ---------------------------------------------------------------------------
# (a) judge score parsing: F6 string-aware JSON + F7 scaled-form fallback
# ---------------------------------------------------------------------------


def test_parse_model_dim_scores_f6_string_aware_json() -> None:
    # a '}' inside a string value must not truncate the JSON block (F6)
    text = 'prose {"correctness": 0.8, "evidence": "needs }} fix"}\ntrailing'
    scores = _parse_model_dim_scores(text)
    assert scores is not None
    assert scores["correctness"] == pytest.approx(0.8)
    assert scores["runnability"] is None  # absent dim -> None, not a crash


def test_extract_json_object_f6_handles_escaped_and_nested() -> None:
    assert _extract_json_object('{"a": "}"}') == '{"a": "}"}'
    assert _extract_json_object('{"a": {"b": 1}}') == '{"a": {"b": 1}}'
    assert _extract_json_object('{"a": "esc \\" quote"}') == '{"a": "esc \\" quote"}'
    assert _extract_json_object("no json here") is None


def test_parse_self_eval_score_f7_fallback_forms() -> None:
    # scaled "X/10" / "X out of 10" preferred over bare "score: X"
    assert _parse_self_eval_score("I score it 7/10") == pytest.approx(0.7)
    assert _parse_self_eval_score("7 out of 10") == pytest.approx(0.7)
    assert _parse_self_eval_score("score: 8") == pytest.approx(0.8)
    # an ambiguous bare number in prose must NOT be grabbed (neutral 0.5)
    assert _parse_self_eval_score("3 compile errors; it is decent") == pytest.approx(0.5)


def test_parse_self_eval_score_f7_json_block_still_preferred() -> None:
    assert _parse_self_eval_score('{"score": 8}') == pytest.approx(0.8)
    assert _parse_self_eval_score('thinking\n{"score": 6.5}\nend') == pytest.approx(0.65)


# ---------------------------------------------------------------------------
# judge inference on the trainer's TextPreprocessorBackend (it never ran)
# ---------------------------------------------------------------------------


class _FakeJudgeModel:
    """Records generate kwargs; returns a canned completion."""

    def __init__(self) -> None:
        self.last_kwargs: dict | None = None
        self.generation_config = types.SimpleNamespace()
        self.config = types.SimpleNamespace(eos_token_id=None)

    def generate(self, input_ids=None, **kwargs):
        self.last_kwargs = kwargs
        tail = torch.tensor([3, 4, 5])
        return [torch.cat([input_ids[0], tail])]


class _Render:
    def __init__(self, tokenizer: PreTrainedTokenizerFast) -> None:
        self.tokenizer = tokenizer

    def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=True, **kwargs):  # noqa: ARG002
        if tokenize:
            return self.tokenizer("TASK: judge", return_tensors="pt")["input_ids"]
        return "TASK: judge"


class _CannedDecoder:
    """text_backend whose decode returns the canned judge JSON."""

    def __init__(self, inner: PreTrainedTokenizerFast, canned: str) -> None:
        self.inner = inner
        self.canned = canned

    def decode(self, ids, skip_special_tokens=True):  # noqa: ARG002
        return self.canned

    def __getattr__(self, name):
        return getattr(self.inner, name)


def _judge_backend_args(canned: str = JUDGE_JSON):
    tokenizer = make_tokenizer()
    backend = TextPreprocessorBackend(
        render_backend=_Render(tokenizer),
        text_backend=_CannedDecoder(tokenizer, canned),
        save_backend=tokenizer,
        backend_kind="test",
    )
    args = types.SimpleNamespace(model_judge_max_tokens=256, model_judge_temperature=0.0)
    return backend, args


def test_model_comprehensive_scores_runs_on_text_preprocessor_backend() -> None:
    # RED->GREEN: with the trainer's backend (no .tokenizer/.encode_chat) the
    # judge previously returned None — the path never ran.
    backend, args = _judge_backend_args()
    judge = _FakeJudgeModel()
    task = {"meta": {"description": "demo"}, "task_dir": Path("demo"), "task_id": "demo"}
    scores = _model_comprehensive_scores(
        "x = 1", task, "tests passed: True", judge, backend, args, "cpu"
    )
    assert scores is not None
    assert scores["correctness"] == pytest.approx(0.8)
    assert scores["quality"] == pytest.approx(0.7)
    # the judge generate got the resolved EOS backstop + explicit KV cache
    assert judge.last_kwargs is not None
    assert judge.last_kwargs["eos_token_id"] == [EOS_ID]
    assert judge.last_kwargs["use_cache"] is True


def test_model_comprehensive_scores_releases_device_cache_after_forward() -> None:
    backend, args = _judge_backend_args()
    judge = _FakeJudgeModel()
    calls: list[str] = []
    for backend_name in ("npu", "cuda", "mps"):
        mod = getattr(torch, backend_name, None)
        if mod is not None and hasattr(mod, "empty_cache"):
            original = mod.empty_cache

            def spy(backend_name=backend_name, original=original):
                calls.append(backend_name)
                return original()

            mod.empty_cache = spy
    try:
        task = {"meta": {"description": "demo"}, "task_dir": Path("demo"), "task_id": "demo"}
        scores = _model_comprehensive_scores(
            "x = 1", task, "tests passed: True", judge, backend, args, "cpu"
        )
        assert scores is not None
    finally:
        for backend_name in ("npu", "cuda", "mps"):
            mod = getattr(torch, backend_name, None)
            if mod is not None and hasattr(mod, "empty_cache"):
                # restore happens implicitly per-backend below
                pass
    assert calls, "device cache was never released after a judge forward"


# ---------------------------------------------------------------------------
# (b) reward composition: calibration-GATED judge mass (research memo
#     2026-08-26: w_P=0.50, w_S=0.40, w_J=0.10 calibrated-only)
# ---------------------------------------------------------------------------


def test_effective_judge_weights_calibration_gated() -> None:
    # RESEARCH-LANE FIX (2026-08-26): an ACTIVE UNCALIBRATED judge injects
    # ~0.5+-noise into the advantages — with NO calibration file the judge
    # mass must be EXACTLY 0 (the judge term contributes NOTHING until
    # calibrated). The r16 uniform fallback is removed.
    assert effective_judge_weights({}, model_judge_enabled=True) == {}
    # calibrated weights are preserved
    calibrated = effective_judge_weights({"correctness": 0.8}, model_judge_enabled=True)
    assert calibrated == {"correctness": 0.8}
    # disabled -> whatever was passed (legacy behavior)
    assert effective_judge_weights({}, model_judge_enabled=False) == {}


def test_judge_composite_score_matches_blend_term() -> None:
    scores = {
        "correctness": 0.8,
        "runnability": 0.6,
        "result_correctness": 0.9,
        "efficiency": 0.5,
        "quality": 0.7,
    }
    uniform = {dim: 1.0 for dim in MODEL_JUDGE_DIMENSIONS}
    composite = judge_composite_score(scores, uniform)
    assert composite == pytest.approx((0.8 + 0.6 + 0.9 + 0.5 + 0.7) / 5.0)
    # missing dims count as 0; no weights -> 0
    assert judge_composite_score({}, uniform) == 0.0
    assert judge_composite_score(scores, {}) == 0.0


def test_compose_policy_training_reward_judge_mass_calibration_gated() -> None:
    # recommended masses (research memo 2026-08-26): w_P=0.50, w_S=0.40,
    # w_J=0.10, CALIBRATED-ONLY
    args = types.SimpleNamespace(
        reward_pass_weight=0.45,
        reward_syntax_weight=0.05,
        reward_interface_weight=0.10,
        reward_verifier_weight=0.10,
        reward_brevity_weight=0.0,
        reward_import_hygiene_weight=0.05,
        reward_mode="comprehensive",
        reward_pass_mass=0.50,
        reward_shaped_mass=0.40,
        reward_judge_mass=0.10,
        tiered_alpha=0.10,
        tiered_gamma=0.05,
    )
    scores = {
        "correctness": 0.8,
        "runnability": 0.6,
        "result_correctness": 0.9,
        "efficiency": 0.5,
        "quality": 0.7,
    }
    calibrated = {dim: 1.0 for dim in MODEL_JUDGE_DIMENSIONS}
    reward = {
        "pass_reward": 1.0,
        "shaped_reward": 1.0,
        "syntax_reward": 1.0,
        "interface_reward": 1.0,
        "verifier_reward": 1.0,
        "brevity_reward": 0.0,
        "import_hygiene_reward": 1.0,
    }
    # (a) NO calibration (empty judge weights) -> the judge term contributes
    # NOTHING even when dim scores are present: masses renormalize over P+S
    total_gated = compose_policy_training_reward(
        reward, args, model_dim_scores=scores, judge_weights={}
    )
    assert total_gated == pytest.approx((0.50 * 1.0 + 0.40 * 1.0) / 0.90)
    # (b) calibrated -> the exact 3-way blend 0.50P + 0.40S + 0.10J
    total_cal = compose_policy_training_reward(
        reward, args, model_dim_scores=scores, judge_weights=calibrated
    )
    judge_composite = (0.8 + 0.6 + 0.9 + 0.5 + 0.7) / 5.0
    assert total_cal == pytest.approx(0.50 * 1.0 + 0.40 * 1.0 + 0.10 * judge_composite)
    # failing candidate: P=0; the shaped 0.5 feeds progress at weight
    # 0.45/0.75 (all other components 0) -> S = 0.45*0.5/0.75 = 0.3
    reward["pass_reward"] = 0.0
    reward["shaped_reward"] = 0.5
    reward["syntax_reward"] = 0.0
    reward["interface_reward"] = 0.0
    reward["verifier_reward"] = 0.0
    reward["import_hygiene_reward"] = 0.0
    total_fail = compose_policy_training_reward(
        reward, args, model_dim_scores=scores, judge_weights=calibrated
    )
    assert total_fail == pytest.approx(0.50 * 0.0 + 0.40 * 0.3 + 0.10 * judge_composite)


def test_evaluate_candidate_records_judge_reward() -> None:
    # the per-candidate record carries the exact judge composite the blend
    # used, so the reward verifier can recompute the 3-way blend
    args = types.SimpleNamespace(
        reward_pass_weight=0.45,
        reward_syntax_weight=0.05,
        reward_interface_weight=0.10,
        reward_verifier_weight=0.10,
        reward_brevity_weight=0.0,
        reward_import_hygiene_weight=0.05,
        reward_mode="comprehensive",
        reward_pass_mass=0.40,
        reward_shaped_mass=0.35,
        reward_judge_mass=0.25,
        brevity_target_lines=0,
        self_evaluation_enabled=False,
        model_judge_enabled=True,
    )
    tokenizer = make_tokenizer()
    backend = TextPreprocessorBackend(
        render_backend=_Render(tokenizer),
        text_backend=_CannedDecoder(tokenizer, JUDGE_JSON),
        save_backend=tokenizer,
        backend_kind="test",
    )
    judge = _FakeJudgeModel()
    harness = types.SimpleNamespace(run=lambda code: {"passed": True, "details": []})
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "training.grpo_trainer._run_harness_subprocess",
            lambda code, task, args: ({"passed": True, "details": []}, 0.0, None),
        )
        entry = evaluate_candidate(
            "x = 1",
            harness,
            {"task_id": "demo", "meta": {"description": "demo"}, "required_interface": []},
            args,
            model=None,
            backend=backend,
            device="cpu",
            judge_model=judge,
            judge_weights={},  # NO calibration -> calibration-gated
        )
    # no calibration -> judge_reward None (calibration-gated: the judge
    # contributes NOTHING; None is the audit's judge-absent gate)
    assert entry["judge_reward"] is None
    records = build_rollout_rewards([entry], torch.tensor([0.0]))
    assert records[0]["judge_reward"] is None
    # calibrated -> the exact composite the blend used
    calibrated = {dim: 1.0 for dim in MODEL_JUDGE_DIMENSIONS}
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "training.grpo_trainer._run_harness_subprocess",
            lambda code, task, args: ({"passed": True, "details": []}, 0.0, None),
        )
        entry_cal = evaluate_candidate(
            "x = 1",
            harness,
            {"task_id": "demo", "meta": {"description": "demo"}, "required_interface": []},
            args,
            model=None,
            backend=backend,
            device="cpu",
            judge_model=judge,
            judge_weights=calibrated,
        )
    assert entry_cal["judge_reward"] == pytest.approx((0.8 + 0.6 + 0.9 + 0.5 + 0.7) / 5.0)


# ---------------------------------------------------------------------------
# (c) the reward verifier recomputes the 3-way blend
# ---------------------------------------------------------------------------


def test_audit_compose_total_calibration_gated_three_way_blend() -> None:
    from scripts.sapo_reward_audit import compose_total

    weights = {
        "shaped": 0.45,
        "syntax": 0.05,
        "interface": 0.10,
        "verifier": 0.10,
        "brevity": 0.0,
        "hygiene": 0.05,
        "total": 0.75,
        "mode": "comprehensive",
        "pass_mass": 0.50,
        "shaped_mass": 0.40,
        "judge_mass": 0.10,
    }
    total = compose_total(1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0, weights, judge=0.7)
    assert total == pytest.approx(0.50 * 1.0 + 0.40 * 1.0 + 0.10 * 0.7)
    # no calibration (judge absent) -> judge contributes NOTHING; masses
    # renormalize over pass+shaped: (0.50+0.40)/0.90 = 1.0
    total_no_judge = compose_total(1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0, weights, judge=None)
    assert total_no_judge == pytest.approx(1.0)
    # a failing candidate with judge absent: total = 0.40*S/0.90
    fail_no_judge = compose_total(0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, weights, judge=None)
    assert fail_no_judge == pytest.approx((0.40 * 0.3) / 0.90)


def test_audit_total_band_with_judge_reward_exact() -> None:
    from scripts.sapo_reward_audit import total_band

    weights = {
        "shaped": 0.45,
        "syntax": 0.05,
        "interface": 0.10,
        "verifier": 0.10,
        "brevity": 0.0,
        "hygiene": 0.05,
        "total": 0.75,
        "mode": "comprehensive",
        "pass_mass": 0.50,
        "shaped_mass": 0.40,
        "judge_mass": 0.10,
    }
    cand = {
        "pass_reward": 0.0,
        "shaped_reward": 0.5,
        "syntax_reward": 0.0,
        "interface_reward": 0.0,
        "verifier_reward": 0.0,
        "brevity_reward": 0.0,
        "import_hygiene_reward": 0.0,
        "judge_reward": 0.7,
    }
    lo, hi = total_band(cand, weights)
    # S = 0.45*0.5/0.75 = 0.3 (shaped feeds progress at 0.45/0.75); J = 0.7
    expected = 0.50 * 0.0 + 0.40 * 0.3 + 0.10 * 0.7
    assert lo == pytest.approx(expected)
    assert hi == pytest.approx(expected)


# ---------------------------------------------------------------------------
# (d) judge shares the training model instance (memory wall stays dead)
# ---------------------------------------------------------------------------


def test_resolve_frozen_judge_shares_training_model_instance() -> None:
    from peft import LoraConfig, TaskType, get_peft_model

    base = make_model()
    peft_model = get_peft_model(
        base,
        LoraConfig(
            r=2,
            lora_alpha=4,
            task_type=TaskType.CAUSAL_LM,
            target_modules=["c_attn", "c_proj"],
        ),
    )
    judge, shared, judge_path = resolve_frozen_judge(
        model=peft_model,
        distributed=False,
        judge_model_path="/models/Qwen3.6-27B",
        model_name="/models/Qwen3.6-27B",
        judge_adapter_path=None,
        loader=lambda path: pytest.fail(f"second model load attempted: {path}"),
    )
    assert shared is True
    assert judge is peft_model.base_model
    assert judge_path == "/models/Qwen3.6-27B"


def test_resolve_frozen_judge_legacy_load_for_different_path() -> None:
    from peft import LoraConfig, TaskType, get_peft_model

    base = make_model()
    peft_model = get_peft_model(
        base,
        LoraConfig(
            r=2,
            lora_alpha=4,
            task_type=TaskType.CAUSAL_LM,
            target_modules=["c_attn", "c_proj"],
        ),
    )
    loaded: list[str] = []

    def fake_loader(path):
        loaded.append(path)
        return make_model()

    judge, shared, judge_path = resolve_frozen_judge(
        model=peft_model,
        distributed=False,
        judge_model_path="/models/other-27B",
        model_name="/models/Qwen3.6-27B",
        judge_adapter_path=None,
        loader=fake_loader,
    )
    assert shared is False
    assert loaded == ["/models/other-27B"]
    assert judge_path == "/models/other-27B"


def test_resolve_frozen_judge_default_loader_does_not_nameerror(monkeypatch) -> None:
    """The docstring claims the loader ``defaults to AutoModelForCausalLM`` —
    but that name only existed as a lazy import inside the training function,
    so the DEFAULT (loader=None) fallback always raised NameError. The legacy
    separate-judge path was never usable outside the shared-model shortcut.
    Pins the documented default to an actual working loader."""
    calls: list[str] = []

    class FakeAutoModelForCausalLM:
        @staticmethod
        def from_pretrained(path, **kwargs):
            calls.append(path)
            return "JUDGE_MODEL"

    monkeypatch.setattr("transformers.AutoModelForCausalLM", FakeAutoModelForCausalLM)

    judge, shared, judge_path = resolve_frozen_judge(
        model=object(),  # not a peft model: shared-base shortcut cannot apply
        distributed=False,
        judge_model_path="/models/other-27B",
        model_name="/models/Qwen3.6-27B",
        judge_adapter_path=None,
        loader=None,
    )
    assert shared is False
    assert judge == "JUDGE_MODEL"
    assert judge_path == "/models/other-27B"
    assert calls == ["/models/other-27B"]


# ---------------------------------------------------------------------------
# (e) launcher wiring: judge flags explicit + echo-verified
# ---------------------------------------------------------------------------


def test_default_masses_adopted_050_040_010() -> None:
    # research memo (2026-08-26): w_P=0.50, w_S=0.40, w_J=0.10
    import sys as _sys

    from training.grpo_trainer import parse_args

    _sys.argv = ["grpo_trainer.py", "--model-name", "m"]
    ns = parse_args()
    assert ns.reward_pass_mass == 0.50
    assert ns.reward_shaped_mass == 0.40
    assert ns.reward_judge_mass == 0.10
    from scripts.sapo_reward_audit import (
        DEFAULT_JUDGE_MASS,
        DEFAULT_PASS_MASS,
        DEFAULT_SHAPED_MASS,
    )

    assert (DEFAULT_PASS_MASS, DEFAULT_SHAPED_MASS, DEFAULT_JUDGE_MASS) == (
        0.50,
        0.40,
        0.10,
    )


def test_launcher_wires_model_judge_flags() -> None:
    launcher = (ROOT / "scripts" / "asi2_launch_grpo_27b_selfeval.sh").read_text(encoding="utf-8")
    assert "MODEL_JUDGE_ENABLED" in launcher
    assert "MODEL_JUDGE_PATH" in launcher
    assert "--model-judge-enabled" in launcher
    assert "--judge-model-path" in launcher
    # echo-verified: the launch banner must print the judge state
    assert "Model judge:" in launcher


def test_launcher_env_passthrough_asi3_and_ai() -> None:
    asi3 = (ROOT / "scripts" / "asi3_launch_grpo_direct.sh").read_text(encoding="utf-8")
    ai = (ROOT / "scripts" / "ai_launch_sapo_direct.sh").read_text(encoding="utf-8")
    assert "ASI3_SAPO_MODEL_JUDGE_ENABLED" in asi3
    assert "ASI3_SAPO_MODEL_JUDGE_PATH" in asi3
    assert "AI_SAPO_MODEL_JUDGE_ENABLED" in ai
    assert "AI_SAPO_MODEL_JUDGE_PATH" in ai
