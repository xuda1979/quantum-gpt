# Frontier-Verifier GSPO for Quantum Code

**Status:** proposed algorithm and ablation plan, not yet implemented or remotely launched
**Target models:** Qwen3.6-27B and Qwen3.6-35B-A3B adapters
**Primary objective:** improve executable quantum-code and software-engineering pass@1 without wasting rollout compute on mastered or currently unlearnable tasks

## Decision

Use a GRPO-family algorithm called **Frontier-Verifier GSPO (FV-GSPO)**. It combines:

1. sequence-level policy optimization from GSPO for stable dense and MoE updates;
2. leave-one-out centered verifier rewards from Dr.GRPO, without per-question reward-standard-deviation scaling;
3. DAPO-style dynamic sampling, extended into a three-way task router;
4. execution-grounded repair-data generation for all-fail tasks;
5. replay and held-out regression gates to preserve general coding ability.

This is not a request to generate arbitrary difficult questions. The current adapter defines the learning frontier through fresh rollouts and executable verifier outcomes.

## Why Vanilla GRPO Does Not Fit

The current trainer samples tasks with weight approximately proportional to `1 - ema_reward`, so lower-reward tasks receive more rollouts. It then skips a group when total and component reward dispersion is below `min_reward_std`. This creates a costly failure mode:

- mastered tasks produce all-pass groups and zero advantages;
- tasks beyond the adapter's current capability produce all-fail groups and zero or noisy advantages;
- the curriculum gives the latter *more* probability before discovering that the group cannot train the policy;
- response-normalized token objectives can bias length;
- token-level importance ratios are especially unstable for MoE expert routing.

The useful GRPO region is the **frontier**: prompts for which the current policy produces meaningfully different outcomes.

The repository's current update is not textbook token-level GRPO. It sums completion token log-probabilities, divides by completion token count, and passes one scalar per response to `stable_grpo_loss`. This already approximates GSPO's length-normalized sequence ratio. However, `stable_grpo_loss` only clamps the log-ratio for numerical safety; it does not implement the clipped proximal minimum in the GSPO objective. The implementation therefore needs a precise sequence-clipped objective and calibrated sequence clip ranges, not a token-to-sequence rewrite.

## Research Basis

- **GRPO / DeepSeekMath** removes the critic and uses a group baseline, making verifiable-reward RL memory-efficient.
- **DeepSeek-R1** demonstrates that outcome-verifiable RL can improve mathematics and code reasoning, but does not resolve sparse-group efficiency.
- **Dr.GRPO** identifies response-length and question-difficulty biases caused by response-length and within-group standard-deviation normalization. It removes both terms and relates the centered group estimator to REINFORCE leave-one-out.
- **DAPO** adds asymmetric clipping, dynamic removal of all-pass and all-fail groups, token-level loss aggregation, and soft handling of truncated responses. Its dynamic sampling directly addresses zero-gradient groups.
- **GSPO** aligns the importance-sampling unit with sequence-level rewards. It reports better stability and efficiency than token-ratio GRPO and specifically addresses MoE expert-routing volatility.
- **ProRL** argues that prolonged RL benefits from diverse tasks, KL control, and periodic reference-policy reset rather than unconstrained drift.
- **Entropy Mechanism / Clip-Cov** shows that entropy collapse limits continued exploration and motivates explicit entropy monitoring and selective update control.
- **CISPO / MiniMax-M1** provides further evidence that clipping importance weights, rather than suppressing token updates through PPO's minimum objective, can improve long-horizon RL efficiency.

Primary sources are listed at the end of this document.

## Algorithm

### 1. Probe and route tasks

For each candidate training task `x`, sample `G` programs from the current adapter and run the deterministic test harness. Compute:

- `p_pass`: fraction passing all tests;
- `v_rule = 4 * p_pass * (1 - p_pass)`, binary frontier variance in `[0, 1]`;
- `v_shape`: normalized dispersion across syntax, interface, clause, import, and execution rewards;
- `learnability = max(v_rule, v_shape)`;
- `coverage_need`: weight from the training-only skill/failure inventory;
- `staleness`: bonus for tasks not probed recently.

Route the task:

| Route | Condition | Action |
|---|---|---|
| `frontier_rl` | `learnability >= tau_frontier` | Use the group for FV-GSPO |
| `mastered_replay` | `p_pass >= tau_mastered` and low shaped dispersion | Downweight; retain a small replay quota |
| `repair_sft` | `p_pass == 0` and low shaped dispersion | Generate a verified correction curriculum, then re-probe |
| `partial_repair_rl` | no full pass but meaningful shaped dispersion | Keep for RL with partial verifier reward and optionally mine preference pairs |
| `invalid_or_noisy` | verifier disagreement, flaky tests, or nondeterminism | Quarantine; do not train |

The task sampling score is:

$$
w_x = c_x\left[\lambda_f L_x + \lambda_n\sqrt{\frac{\log(1+N)}{1+n_x}} + \lambda_s S_x\right],
$$

where $L_x$ is learnability, $c_x$ is coverage need, $S_x$ is staleness, $n_x$ is the number of recent probes, and $N$ is the total number of probes. Unlike inverse-reward sampling, this score favors informative uncertainty rather than maximum failure.

### 2. Build a verifier-first reward

The executable harness is authoritative. Self-evaluation and teacher judgments are diagnostics or routing inputs; they cannot override execution.

For candidate `y` on task `x`, define:

$$
R(x,y) = P + (1-P)\left(0.10S + 0.15I + 0.55C + 0.10H + 0.10E\right) - T,
$$

where:

- $P \in \{0,1\}$ is full test pass;
- $S$ is syntax validity;
- $I$ is required-interface satisfaction;
- $C$ is passed verifier-clause fraction;
- $H$ is import/API hygiene;
- $E$ is execution progress without timeout or crash;
- $T$ is a bounded truncation or pathological-length penalty.

Clamp failing rewards below `0.95`, so every passing candidate outranks every failing candidate. Do not give the current adapter's self-judge a direct reward weight until its agreement with executable labels is calibrated on held-out rollouts; if later enabled, cap it at `0.05` and subtract that mass from shaped terms, not from $P$.

### 3. Estimate an unbiased group advantage

For group size $G`, use a leave-one-out baseline:

$$
A_i = R_i - \frac{1}{G-1}\sum_{j\ne i}R_j.
$$

Do not divide by the group's reward standard deviation. Batch-level robust scaling by a fixed running MAD is allowed for numerical stability, but it must be shared across tasks rather than reweighting each question by its own variance.

### 4. Optimize at sequence level

For response $y_i$ with completion length $|y_i|`, define the GSPO sequence ratio:

$$
s_i(\theta) = \exp\left(\frac{1}{|y_i|}\sum_t
\log\frac{\pi_\theta(y_{i,t}\mid x,y_{i,<t})}
{\pi_{\mathrm{old}}(y_{i,t}\mid x,y_{i,<t})}\right).
$$

The policy objective is:

$$
J_{FV} = \frac{1}{B}\sum_{i=1}^{B}
\min\left(s_i A_i,
\operatorname{clip}(s_i,1-\epsilon_{low},1+\epsilon_{high})A_i\right)
- \beta D_{KL}(\pi_\theta\Vert\pi_{anchor}).
$$

Use one optimizer epoch per fresh rollout batch initially. This keeps the policy close to on-policy and makes clipping a guardrail rather than the main learning mechanism. For Qwen3.6-35B-A3B, sequence-level clipping is the default because it is less sensitive to expert-routing changes than token-level ratios.

The anchor policy is the accepted SFT/adapter checkpoint at the start of a training phase. Reset the anchor only after a checkpoint passes held-out regression gates. KL is adaptive: increase `beta` when replay performance or sequence KL drifts beyond target; decrease it when learning stalls while regression gates remain green.

### 5. Convert all-fail groups into learnable data

An all-fail group with no shaped-reward variation is not an RL batch. It enters the repair lane:

1. choose the current adapter candidate with the most verifier clauses passed;
2. retain its exact test failures, traceback, interface mismatch, and import errors;
3. ask the trusted teacher or verified repair system for the smallest correction;
4. execute the correction against the same training-task harness;
5. reject it unless all tests pass;
6. generate nearby variants that preserve the failed skill while changing constants, APIs, topology, or specification wording;
7. verify every emitted target;
8. train with correction SFT and, when a verified chosen/rejected pair exists, DPO;
9. re-probe the task family with the updated adapter before returning it to `frontier_rl`.

This is the mechanism by which generated samples teach the current adapter to fix its current issues. The current adapter supplies the failure; a verifier and stronger teacher supply the trustworthy learning target.

### 6. Prevent evaluation leakage and forgetting

- Held-out eval tasks never become training prompts, targets, tests, or direct paraphrases.
- Eval failures may update only a coarse training taxonomy such as `qaoa parameter binding` or `Kraus operator shape`.
- New repair tasks must come from the disjoint training inventory or independently generated analogues checked for task, prompt-family, and source overlap.
- Start each update batch with `50% frontier/repair`, `25% neighboring generalization`, and `25% broad quantum + software replay`.
- Adjust the mixture from measured regressions, never from training reward alone.

## End-to-End Loop

```text
evaluate current adapter on train-probe pool
classify failures and update skill coverage

while budget remains:
    probe candidate tasks with G rollouts
    route each group

    if route == frontier_rl or partial_repair_rl:
        execute and score candidates
        compute leave-one-out advantages
        apply sequence-level clipped update

    if route == repair_sft:
        create execution-grounded correction + nearby variants
        verify targets
        queue SFT/DPO micro-batch

    mix targeted data with neighbor and replay data
    periodically train queued correction micro-batches
    run fixed disjoint eval gate

    if eval improves without regression:
        accept checkpoint and optionally reset anchor
    elif regression or instability persists:
        roll back, raise replay/KL, and quarantine noisy rewards
```

## Initial Hyperparameters

These are starting points for ablation, not universal constants.

| Parameter | 27B start | 35B-A3B start | Reason |
|---|---:|---:|---|
| group size `G` | 8 | 8 | enough pass/fail resolution without excessive rollout cost |
| rollout temperature | 0.8 | 0.8 | current setting; adapt only after entropy evidence |
| `tau_frontier` | 0.10 | 0.10 | exclude nearly flat groups |
| `tau_mastered` | 0.95 | 0.95 | retain occasional replay but stop dominant sampling |
| GSPO `epsilon_low` | sweep `1e-4, 3e-4, 1e-3` | start `3e-4` | GSPO ratios differ by orders of magnitude from token PPO ratios |
| GSPO `epsilon_high` | `1.3 * epsilon_low` | `4e-4` | asymmetric exploration, following GSPO/DAPO direction |
| optimizer epochs | 1 | 1 | minimize off-policy drift |
| learning rate | `1e-6` to `3e-6` LoRA | `5e-7` to `2e-6` LoRA | current `1e-5` is aggressive for prolonged verifier RL |
| initial KL `beta` | `0.005` | `0.005` | capability preservation; adapt from measured KL/regression |
| correction mix | 50/25/25 | 50/25/25 | targeted / neighbor / replay |
| self-judge reward | 0 | 0 | enable only after executable-label calibration |

Do not copy DAPO's token-ratio clip values (`0.2/0.28`) into GSPO. The GSPO paper used approximately `3e-4/4e-4` for Qwen3-30B-A3B because sequence ratios operate on a different scale.

## Monitoring and Circuit Breakers

Record per step and per task family:

- all-pass, all-fail, frontier, repair, and quarantined group fractions;
- effective-gradient groups per 1,000 generated tokens;
- pass@1 and pass@G on train-probe and held-out sets;
- clause pass rates and failure-category transitions;
- sequence KL, GSPO ratio, low/high clip fractions, gradient norm;
- generation entropy, correct/incorrect response lengths, truncation rate;
- replay pass@1 and domain-specific regressions;
- repair acceptance rate and verified-target count.

Stop or roll back when any condition persists for two evaluation windows:

- held-out pass@1 drops by more than 3 percentage points;
- broad software replay drops by more than 3 percentage points;
- non-finite loss or gradient occurs;
- entropy collapses while frontier yield decreases;
- clip fraction exceeds 50% after learning-rate reduction;
- all-fail rollout share exceeds 40% without repair conversion;
- verifier disagreement or flaky-test rate exceeds 2%;
- training reward rises while held-out pass@1 is flat or falling.

## Implementation Order and Ablations

Implement the smallest discriminating sequence, using the same adapter, task pool, seeds, rollout budget, and eval protocol:

1. **Baseline:** current GRPO and current curriculum.
2. **Router only:** frontier routing plus all-fail repair queue; unchanged policy loss.
3. **Dr advantage:** leave-one-out centering without group standard-deviation scaling.
4. **FV-GSPO:** sequence ratio and sequence clipping.
5. **Repair loop:** verified correction SFT/DPO with 50/25/25 replay mixture.
6. **Adaptive anchor:** KL controller and accepted-checkpoint reference resets.
7. **Optional research plugins:** DR pair/correction terms only after the core design wins.

The primary efficiency metric is:

$$
\text{frontier efficiency} =
\frac{\Delta\text{held-out pass@1}}
{\text{generated NPU-token-hours}}.
$$

Secondary metrics are final pass@1, regression count, repair conversion rate, and run-to-run variance. A method that improves training reward but not held-out executable pass@1 fails.

## Repository Integration Map

- Replace inverse-difficulty-only sampling in `training/grpo_utils.py::TaskCurriculum` with the frontier router state.
- Batch multiple prompt groups in `training/grpo_trainer.py`; dynamic sampling is ineffective when the loop handles only one prompt per optimizer step.
- Refactor `stable_grpo_loss` into an explicit GSPO proximal objective using the sequence-mean log-ratios the trainer already computes; retain the old unclipped sequence-ratio loss for controlled ablations.
- Replace `ratio_clip_log_delta=8.0` as the policy trust-region control. Keep a wide log clamp only for finite exponentiation, and introduce separate calibrated `gspo_clip_low` / `gspo_clip_high` parameters for the actual proximal objective.
- Extend `grpo_step_metrics.jsonl` with route, sequence ratio, clip status, entropy, token cost, and failure transition.
- Feed `evals/subsystem/dataset_gap.py` recommendations into the coarse skill taxonomy, not direct eval-task replay.
- Reuse `scripts/rl_distill_pipeline.py::WeaknessReport` for training-only weakness cells, but extend cells with executable failure categories and repair conversion status.
- Reuse existing verified DPO builders and execution sandbox for the repair lane.

## Non-Goals and Cautions

- Do not use the current adapter as its own source of correctness.
- Do not reward self-critique language, long reasoning, or confidence unless it improves executable outcomes.
- Do not assume every hard failure is learnable by RL.
- Do not stack every published stabilization technique in the first run.
- Do not claim the existing doubly-robust plugin is beneficial until its terms win a controlled ablation. It cannot recover a truly equal-reward group without a verified preference gap.
- Do not launch a long run before the router produces a healthy frontier yield on a short probe.

## Primary Sources

1. Shao et al., **DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models**, arXiv:2402.03300.
2. DeepSeek-AI, **DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning**, arXiv:2501.12948.
3. Yu et al., **DAPO: An Open-Source LLM Reinforcement Learning System at Scale**, arXiv:2503.14476.
4. Liu et al., **Understanding R1-Zero-Like Training: A Critical Perspective** (Dr.GRPO), arXiv:2503.20783.
5. Zheng et al., **Group Sequence Policy Optimization**, arXiv:2507.18071.
6. Liu et al., **ProRL: Prolonged Reinforcement Learning Expands Reasoning Boundaries in Large Language Models**, arXiv:2505.24864.
7. Cui et al., **The Entropy Mechanism of Reinforcement Learning for Reasoning Language Models**, arXiv:2505.22617.
8. MiniMax, **MiniMax-M1: Scaling Test-Time Compute Efficiently with Lightning Attention**, arXiv:2506.13585.
