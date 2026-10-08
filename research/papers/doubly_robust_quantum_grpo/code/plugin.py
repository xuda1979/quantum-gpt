"""Research-method plugin: doubly_robust_quantum_grpo.

Combines the existing PPO/GRPO update with a DPO-style pairwise loss
on in-group (chosen, rejected) pairs, weighted by a doubly-robust
correction term. See ../paper.md for the full derivation.

The plugin only contributes:

- a reward-shaping extension that tags each candidate with its DR
  pair role (chosen / rejected / null),
- a small prompt suffix that matches the DPO assumption (chosen and
  rejected come from the same prompt),
- a task-weight boost for tasks rich enough to make pair-mining
  informative,
- an `extra_run_config()` block with the DR hyperparameters that the
  trainer reads.

The actual pairwise DPO backward is implemented in
`dr_pair_loss.py` and is invoked by `training/grpo_trainer.py` when
this plugin is enabled.
"""

from __future__ import annotations

from typing import Any

from training.research_plugins import BaseResearchMethod


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return default
    if v != v:  # NaN
        return default
    return v


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# One-line instruction appended to the GRPO prompt. The DPO assumption
# is that chosen and rejected come from the same prompt; the suffix
# biases the student toward producing a single, verifier-likely
# candidate without changing the task semantics.
_DR_PROMPT_SUFFIX = (
    "\n\nAdditional instruction: prefer the implementation most likely "
    "to pass the verifier on the first try; if uncertain, prefer the "
    "simpler, more readable variant. Output only the final Python code."
)


class DoublyRobustQuantumGrpoMethod(BaseResearchMethod):
    method_id = "doubly_robust_quantum_grpo"
    paper_title = "Doubly-Robust GRPO for Quantum Code Generation"

    # Default hyperparameters. Override via the research-methods
    # manifest or by subclassing in a follow-up experiment.
    dr_dpo_beta: float = 0.07
    dr_psi_init: float = 0.5
    # Linear psi warmup: psi ramps 0 -> dr_psi_init over the first
    # `dr_psi_warmup_steps` training steps, then holds at dr_psi_init.
    # 0 = no warmup (constant psi, pre-warmup behavior). Paper suggests
    # tuning psi after step 50; a 10-step linear warmup is a reasonable
    # default to reduce early-step variance.
    dr_psi_warmup_steps: int = 0
    dr_pair_min_reward_gap: float = 0.4
    dr_pair_loss_weight: float = 0.3
    dr_pair_max_per_step: int = 1
    dr_pair_buffer_path: str | None = None

    def augment_grpo_prompt(self, prompt: str, *, task: dict[str, Any], stage: str) -> str:
        if stage != "grpo":
            return prompt
        return prompt + _DR_PROMPT_SUFFIX

    def adjust_task_weight(self, weight: float, *, task: dict[str, Any], stage: str) -> float:
        if stage != "grpo":
            return weight
        # Only boost tasks rich enough to make pair-mining meaningful.
        # A task with <2 behavior hints and <2 required-interface lines
        # is unlikely to produce within-group reward variance beyond
        # pure syntax noise.
        behavior_hints = len(task.get("behavior_hints") or [])
        interface_lines = len(task.get("required_interface") or [])
        if behavior_hints >= 2 or interface_lines >= 2:
            return weight * 1.12
        return weight

    def adjust_reward_breakdown(
        self,
        reward: dict[str, Any],
        *,
        code: str,
        result: dict[str, Any] | None,
        task: dict[str, Any],
        stage: str,
    ) -> dict[str, Any]:
        # Per-candidate reward adjustment is a no-op here. Pair role
        # assignment is a *group-level* operation (it requires
        # comparing candidates within the same group), so it is done
        # in the trainer right after evaluation. We expose the
        # hyperparameters via the reward dict so the trainer can read
        # them off the first candidate's reward without needing a
        # separate config path.
        if stage != "grpo":
            return reward
        merged = dict(reward)
        merged.setdefault("dr_dpo_beta", self.dr_dpo_beta)
        merged.setdefault("dr_psi_init", self.dr_psi_init)
        merged.setdefault("dr_pair_min_reward_gap", self.dr_pair_min_reward_gap)
        merged.setdefault("dr_pair_loss_weight", self.dr_pair_loss_weight)
        merged.setdefault("dr_pair_max_per_step", self.dr_pair_max_per_step)
        # Per-candidate fields (default null / -1; trainer fills them in
        # during group aggregation).
        merged.setdefault("dr_pair_role", None)
        merged.setdefault("dr_pair_partner_idx", -1)
        merged.setdefault("dr_pair_reward_gap", 0.0)
        return merged

    def extra_run_config(self) -> dict[str, Any]:
        return {
            "doubly_robust_quantum_grpo": {
                "enabled": True,
                "dr_dpo_beta": self.dr_dpo_beta,
                "dr_psi_init": self.dr_psi_init,
                "dr_psi_warmup_steps": self.dr_psi_warmup_steps,
                "dr_pair_min_reward_gap": self.dr_pair_min_reward_gap,
                "dr_pair_loss_weight": self.dr_pair_loss_weight,
                "dr_pair_max_per_step": self.dr_pair_max_per_step,
                "dr_pair_buffer_path": self.dr_pair_buffer_path,
            }
        }


def build_method() -> DoublyRobustQuantumGrpoMethod:
    return DoublyRobustQuantumGrpoMethod()
