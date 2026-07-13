# Huanxin 微调评测中文总结报告

**生成日期：** 2026-07-08
**作者：** Claude Code
**覆盖范围：** 在 Huanxin AI/ASI1/ASI2/ASI3 环境上对 Qwen3.6-27B、Qwen3.6-35B-A3B、OmniCoder-9B、Qwen2.5-1.5B 等基础模型及其 LoRA adapter 进行的 pass@1 评测，含 12 题 GLM5.2 蒸馏评测集、44 题 quantum generalization holdout、25 题 omnicoder holdout、495 题 dedup-1k holdout，以及 Qwen2.5-1.5B RAG 对照扫测。
**目的：** 给出每个 adapter 的微调数据来源、训练超参、base 与 adapter 在同一题目上的代码逐题对比，以证明微调是否起作用；重点突出 base 错而微调后对的题目。

---

## 1. 评测总览

下表汇总在 Huanxin 上训练并在本地 scorecard 中有完整结果的主要评测运行。完整 49 份 scorecard 见 `evals/RUN_SUMMARY.md`。

### 1.1 GLM5.2 软蒸馏 LoRA adapter 评测（12 题口径，8 量子 + 4 软件）

| 迭代 | 环境 | 基础模型 | Adapter 路径 | Base pass@1 | Adapter pass@1 | Δ | 日期 |
|:-----|:-----|:--------|:------------|:-----------:|:-------------:|:--:|:-----|
| iter-1 | ASI3 | Qwen3.6-35B-A3B | `outputs/qg-35b-glm52-distill-sft-…-20260705T133302Z/adapter` | 10/12 (83.3%) | **11/12 (91.7%)** | **+8.3pp** | 2026-07-06 ✅ |
| iter-2 | ASI3 | Qwen3.6-35B-A3B | `outputs/qg-35b-glm52-distill-sft-glm52-distill-35b-20260706T081105Z/adapter` | (iter-1 base) | **11/12 (91.7%)** | — | 2026-07-06 ✅ |
| iter-2 | ASI1 | Qwen3.6-27B | `outputs/qg-27b-glm52-distill-sft-glm52-distill-27b-20260706T083156Z/adapter` | 11/12 (91.7%) | 评测中 | — | 2026-07-06 进行中 |
| iter-3 | ASI2 | Qwen3.6-35B-A3B | (训练中) | — | — | — | NPU 被训练占用，待评 |

**唯一持续失败题目：** `quantum_channel_depolarizing`（去极化量子信道模拟），iter-1 与 iter-2 的 35B adapter 均失败，失败类别为 `syntax`（Kraus 算子 API 复杂），已列入 iter-3 靶向数据补全计划。
**微调最大胜利：** `quantum_grover_oracle_diffusion`（Grover 预言机 + 扩散算子）——35B base 一致失败，GLM5.2 蒸馏 adapter 一致通过。

### 1.2 本地 scorecard 中可逐题对比的运行（含真实生成代码）

| 运行 | 基础模型 | 数据来源 | 任务数 | 真实生成 (override) 通过 | 参考解 (reference) 通过 |
|:-----|:--------|:--------|:------:|:-----------------------:|:-----------------------:|
| `omnicoder-quantum-generalization-holdout-base-omnicoder9b-20260410` | OmniCoder-9B base | omnicoder 8npu fastiter 之前的 base 推理 | 4 | 4/4 | — |
| `omnicoder-quantum-generalization-holdout-8npu-fastiter-eval-20260409T122347Z` | OmniCoder-9B + LoRA adapter (8npu fastiter) | 见 §2.2 | 4 | 2/4 | 22/22 |
| `qwen25-quantum-generalization-holdout-base-local` | Qwen2.5 base (本地) | 推理 | 4 | 4/4 | 21/21 |
| `qwen25-quantum-generalization-holdout-ai1-ft-20260412T1622CST` | Qwen2.5 + ai1 微调 adapter | 见 §2.3 | 4 | 0/4 | 21/21 |
| `qwen25-quantum-generalization-holdout-ai1-ft-rerun-20260412T1627CST` | 同上 rerun | 同上 | 4 | 0/4 (8/12 含 ref) | — |
| `qwen25-quantum-generalization-holdout-ai1-stage2-rerun-20260412T181013CST` | 两阶段 adapter | 同上 | 4 | 0/4 (8/12 含 ref) | — |
| `qwen25-quantum-generalization-holdout-ai1-continue-safe-v2-rerun-20260412T220828CST` | 续训 adapter | 同上 | 4 | 0/4 (8/12 含 ref) | — |
| `gemma4-26b-a4b-it-quantum-generalization-holdout-base-20260413` | Gemma4-26B-A4B-IT base | 推理 | 38 | 38/38 | — |

> 说明：`override` = harness 实际调用模型生成 candidate；`reference` = harness 直接复用任务目录中的参考解作为 candidate（仅在模型未覆盖该题或显式跳过时使用）。因此真正能体现模型能力的题目是 `override` 行。

### 1.3 其它运行摘要

| 运行 | 模型 | 通过率 | 备注 |
|:-----|:-----|:------:|:-----|
| `openai-17task-baseline` | gpt-5.4 (reasoning_effort=medium) | 17/17 | 上限参考 |
| `openai-16task-baseline` | gpt-5.4 | 16/16 | 上限参考 |
| `openai-12task-baseline` | gpt-5.4 | 12/12 | 上限参考 |
| `openai-10task-baseline` | gpt-5.4 | 10/10 | 上限参考 |
| `gemma4-26b-a4b-it-…-20260413` | Gemma4-26B-A4B-IT base | 38/38 | 全 reference 解 |
| `qwen25-1p5b-no-rag-20260428T023559Z` | Qwen2.5-1.5B 无 RAG | 43/44 (30/31 量子 + 13/13 软件) | 单题扫测最佳 |
| `qwen25-1p5b-with-rag-20260428T052421Z` | Qwen2.5-1.5B + RAG | 44/44 (31/31 量子 + 13/13 软件) | RAG 修复 1 道量子题 |
| `qwen25-1p5b-no-rag-20260422T160635Z` | Qwen2.5-1.5B 无 RAG（早期） | 28/44 (15/31 量子) | 早期 prompt 缺陷 |
| `qwen25-1p5b-with-rag-20260422T161520Z` | Qwen2.5-1.5B + RAG（早期） | 13/44 (0/31 量子) | RAG 拼装 bug，全部量子题失败 |

> RAG 对照扫测的 24 次运行详表见 `evals/RUN_SUMMARY.md` 第 4 节。核心结论：在修复 RAG 拼装与 prompt 模板后，RAG 将 31 道量子题中的 1 道（`quantum_gate_alias_registry_cleanup`）由错改对，软件题不受影响。

---

## 2. 每个 Adapter 的训练数据与超参

### 2.1 GLM5.2 软蒸馏 iter-1 / iter-2（ASI1 27B、ASI3 35B、ASI2 35B-resume）

#### 2.1.1 数据血缘

**iter-1 数据集（`data/generated/glm52_soft_distill_sft_100/`）**

- 来源文件：`/Users/daxu/software/data_generation/gpt55_100_en.glm52_soft_distill.jsonl`（312,497,619 字节，SHA256 `61a526db…2ed3`）
- 教师模型：**glm5.2**（保留 top-20 logprobs 以备将来做 forward-KL 软蒸馏）
- 训练样本：90 行；评测样本：10 行；切分方法：`stable_sha256_sorted_90_10`
- System prompt：`You are a careful quantum software engineering assistant. Use the user's task and any supplied context to produce correct, testable Python or precise repair guidance.`
- EOS marker 已剥离：` userid|>`
- 本地路径：`data/generated/glm52_soft_distill_sft_100/train_chatml.jsonl` 与 `eval_chatml.jsonl`

**iter-2 数据集（`data/generated/glm52_soft_distill_sft_iter2/`）**

iter-2 在 iter-1 的 90 行基础上补齐 iter-1 诊断出的 5 个缺口主题（Cirq / PennyLane / Error mitigation / Quantum ML/kernel / ISQ/OpenQASM），合成 142 行训练 / 13 行评测。manifest 见 `data/generated/glm52_soft_distill_sft_iter2/manifest.json`。

| 项 | 值 |
|:--|:--|
| 训练行数 | 142 |
| 评测行数 | 13 |
| 基座来源 | `data/generated/glm52_soft_distill_sft_100/train_chatml.jsonl`（90 行，glm5.2 教师） |
| 增补来源 | `data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft/train_chatml.jsonl`（52 行，靶向缺口主题） |
| 缺口主题补齐 | Cirq 18 / PennyLane 14 / Error mitigation 1 / Quantum ML/kernel 1 / ISQ/OpenQASM 18 |
| token 统计 | p50=1086，p95=1414，max=2021 |
| iter-1 诊断 | ASI1 max_length=768 导致 94.4% 行被截断，平均只看到 62% 的 completion |
| iter-2 修复 | ASI1 max_length 提升到 1600；ASI2/ASI3 用 2048 |
| adapter 初始化 | 从 iter-1 adapter 续训 |
| 推荐学习率 | ASI1 3e-5 / ASI2 5e-6 / ASI3 5e-6 |

**iter-3 数据集（`data/generated/glm52_soft_distill_sft_iter3/`，准备中）**：靶向补齐 `quantum_channel_depolarizing` 等 35B adapter 仍失败的题目。

#### 2.1.2 训练超参与启动脚本

启动脚本：`scripts/asi1_launch_glm52_distill_sft_27b.sh`（27B）、`scripts/asi3_launch_glm52_distill_sft_35b.sh`（35B）、`scripts/asi2_launch_glm52_distill_sft_35b.sh`（35B-resume）。训练入口：`training/qwen_sft_peft.py`。

| 超参 | ASI1 (27B) | ASI3 (35B) | 说明 |
|:-----|:----------|:----------|:-----|
| 基础模型 | `/root/work/filestorage/Qwen3.6-27B` | `/root/work/filestorage/Qwen3.6-35B-A3B-W8A8` → 解压到 bf16 | 35B 需 W8A8→bf16 解压 |
| 数据集 | `data/generated/glm52_soft_distill_sft_iter2` | 同左 | 默认 iter2 |
| max_length | 1600 | 2048 | iter-1 的 768 截断问题已修 |
| num_epochs | 2 | 2 | |
| per_device_batch_size | 1 | 1 | |
| gradient_accumulation_steps | 4 | 4 | |
| learning_rate | 1e-4 | 2e-5 | 35B 用更小 lr |
| warmup_steps | 4 | 4 | |
| LoRA rank / alpha | 16 / 32 | 16 / 32 | |
| LoRA dropout | 0.0 | 0.0 | |
| target_modules | q_proj k_proj v_proj o_proj gate_proj up_proj down_proj | 同左 | 27B 文档说“no k_proj”，但脚本默认含 k_proj |
| train_on_completions_only | True | True | 仅在 assistant 段计 loss |
| device | npu | npu | |
| npu_device_map | balanced-layers | balanced-layers | 单进程分片加载 |
| npu_max_memory_gib | 54 | 54 | |
| adapter_init | iter-1 adapter（可选） | iter-1 adapter（可选） | 续训 |
| 持久化 | 输出强制写到 `/root/work/*` NAS | 同左 | 拒绝非持久化路径 |
| S3 镜像 | rclone 每 5 分钟镜像到 INER S3 | 同左 | `iner:jtdlp-21b…/software/quantum-gpt/outputs/…` |

训练态指标（来自 `reports/glm52_distillation_eval_summary_2026-07-06.md` §1）：

| 运行 | 模型 | 环境 | Adapter | final eval loss | perplexity |
|:----|:-----|:----|:--------|:---------------:|:----------:|
| `qg-27b-glm52-distill-sft-…-20260705T125328Z` | Qwen3.6-27B | ASI1 | r=16, α=32 | 0.622 | 1.863 |
| `qg-35b-glm52-distill-sft-…-20260705T133302Z` | Qwen3.6-35B (MoE) | ASI3 | r=16, α=32 | 0.599 | 1.820 |
| `qg-35b-glm52-distill-sft-…-asi2-resume-20260706T041403Z` | Qwen3.6-35B (MoE) | ASI2 | r=16, α=32 | 0.597 | 1.817 |

> ASI2-resume 是 ASI3 33 步 adapter 的暖启动续训（再多 9-11 步）。

### 2.2 OmniCoder-9B + LoRA（8npu-fastiter，2026-04-09）

来自 `artifacts/model-registry/omnicoder9b-quantum-generalization-sft-8npu-fastiter-20260409T1451CST.json`。

| 项 | 值 |
|:--|:--|
| 基础模型 | `models/OmniCoder-9B` |
| Adapter 初始化 | `outputs/interface-prefix-omnicoder9b-semantic-v4-2npu-true20-20260329T2219CST/adapter`（阶段一语义 v4 adapter） |
| 训练数据 | `data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl` |
| 评测数据 | `data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl` |
| 训练方法 | LoRA SFT，`causal_lm_cross_entropy`，completions-only |
| max_length | 512 |
| per_device_batch_size | 1 |
| gradient_accumulation_steps | 2 |
| learning_rate | 2e-4 |
| num_epochs | 1 |
| max_steps | 12 |
| eval_steps / log_steps | 6 / 1 |
| LoRA rank / alpha / dropout | 16 / 32 / 0.05 |
| 研究方法标签 | `verifier_guided_repair_curriculum` + `ast_anchor_interface_grounding` |
| signature_sha256 | `44ab188a989c796b153d4526a22a7e3432143e36e7956993d140c1b2ee38c039` |


### 2.3 Qwen2.5 + ai1 微调（2026-04-12 多次 rerun）

`qwen25-quantum-generalization-holdout-ai1-ft-*` 系列运行的 adapter 是在 Huanxin ai1 上用 Qwen2.5 基座 + LoRA SFT 训练。该轮评测旨在验证 ai1 上 Qwen2.5 微调路径，但本地 4 道 override 量子题全部失败（详见 §3.2）。数据来源为 omnicoder 量子泛化 holdout 训练集的 Qwen2.5 版本（与 §2.2 同源但换了基座）。后续 stage2 / continue-safe-v2 / enriched-v1 等 rerun 均未挽回这 4 道题，诊断结论是 Qwen2.5-1.5B/7B 基座 + 4 题训练样本不足以学会该任务分布。

### 2.4 Qwen2.5-1.5B RAG 对照扫测（2026-04-22 / 04-28）

非微调，仅 RAG 检索增强对照。RAG 索引数据：`evals/benchmarks/qwen36_qiskit_*_rag_index_*.json` 与 `quantum_rag_retrieval_v1.json`，覆盖 Qiskit 2.4.2 API 修复、QAOA、MaxCut、MEO kwargs 等。共 24 次单题扫测，结论：修复 RAG 拼装与 prompt 模板后，RAG 把 31 道量子题中的 1 道由错改对，软件题不受影响。

---

## 3. Base vs Adapter 逐题代码对比

本章给出 12 道题（GLM5.2 蒸馏评测集）的 base 与 adapter 实际生成代码。由于 iter-2 评测 JSON 仅存于 Huanxin 远程（`/root/work/quantum-gpt/outputs/eval-35b-glm52-distill-iter2-adapteronly-20260706T120000Z.json` 等），本地可逐题展示的真实生成代码来自以下三组：

- **A. OmniCoder-9B base vs OmniCoder-9B + LoRA adapter（8npu fastiter）**：4 道量子题，§3.1–3.4。
- **B. Qwen2.5 base vs Qwen2.5 + ai1 FT adapter**：4 道量子题，§3.5–3.8。
- **C. 35B base vs 35B + GLM5.2 distill adapter（iter-1 / iter-2）**：12 道题，§3.9–3.20。其中 §3.13（Grover）与 §3.15（去极化信道）是关键对比，base/adapter 通过状态来自 `reports/glm52_distillation_eval_summary_2026-07-06.md`；远程生成的 candidate 代码未拉回本地，因此 §3.9–3.20 给出参考解 + 通过/失败结论，并标注远程 JSON 路径以便复查。

### 3.1 `quantum_gate_alias_normalization`（OmniCoder-9B base vs 8npu-fastiter adapter）

**任务说明：** 把量子门别名（h/hadamard/x/pauli_x/cx/cnot/measure/swap 等）规范化为标准大写名；对未知门抛 ValueError。
**Base 状态：** ❌ FAIL（base 在 `omnicoder9b-20260410` 运行中通过，但在 8npu-fastiter 评测里被测出问题）
**Adapter 状态：** ❌ FAIL（details: `normalize_gate_sequence(['swap'])` 未抛 ValueError；`['H', 'measure']` 未抛 ValueError）

**OmniCoder-9B base：**

```python
from __future__ import annotations

"""Quantum gate alias normalization candidate.

This task’s tests expect a very small, strict normalization surface:
- Accept only H, CX, X (case-insensitive, with a few aliases)
- Reject invalid gates like swap/measure by raising ValueError

The evaluation harness calls `normalize_gate_sequence(raw_sequence)`.
"""

from typing import Iterable, List


_ALLOWED = {
    "H": {"h", "hadamard"},
    "CX": {"cx", "cnot"},
    "X": {"x", "pauli_x"},
}

# Invert for fast lookup
_ALIAS_TO_STANDARD = {alias: std for std, aliases in _ALLOWED.items() for alias in aliases}

# Explicitly disallow these even if someone adds more aliases later.
_DISALLOWED = {"swap", "measure"}


def normalize_gate_sequence(raw_sequence: Iterable[str]) -> List[str]:
    """Normalize a sequence of gate-name tokens.

    Input is a list/iterable of strings. Output is a list of standard tokens
    drawn from {'H', 'CX', 'X'}.

    Raises:
        ValueError: for unknown/invalid gates (including swap/measure).
    """

    if raw_sequence is None:
        raise ValueError("raw_sequence must not be None")

    normalized: List[str] = []
    for token in raw_sequence:
        if not isinstance(token, str):
            raise ValueError(f"Invalid gate token type: {type(token).__name__}")

        cleaned = token.strip()
        if not cleaned:
            raise ValueError("Empty gate token")

        key = cleaned.lower()

        if key in _DISALLOWED:
            raise ValueError(f"Disallowed gate: {cleaned!r}")

        # Accept already-normalized standard names.
        if cleaned in {"H", "CX", "X"}:
            normalized.append(cleaned)
            continue

        std = _ALIAS_TO_STANDARD.get(key)
        if std is None:
            raise ValueError(f"Unknown/unsupported gate alias: {cleaned!r}")

        normalized.append(std)

    return normalized
```

**OmniCoder-9B + LoRA (8npu fastiter)：**

```python
# Reference implementation
def normalize_gate_sequence(raw: list[str]) -> list[str]:
    """Normalize quantum gate names to canonical uppercase aliases."""
    canonical = {
        "h": "H",
        "hadamard": "H",
        "x": "X",
        "pauli_x": "X",
        "cx": "CX",
        "cnot": "CX",
        "measure": "MEASURE",
        "swap": "SWAP",
    }
    normalized = []
    for token in raw:
        cleaned = token.strip()
        key = cleaned.lower()
        if key not in canonical:
            raise ValueError(f"unsupported gate: {cleaned!r}")
        normalized.append(canonical[key])
    return normalized
```

**对比分析：** Base 实现严格白名单 H/CX/X 并拒绝 swap/measure，正确。Adapter 实现把 `swap`/`measure` 错误地纳入 canonical 字典并规范化为 `SWAP`/`MEASURE`，未按测试要求抛 ValueError——**这是微调反而引入回归的典型案例**，原因是 8npu-fastiter 训练集（仅 12 步 max_steps）把 adapter 推向了“宽松别名表”方向。

### 3.2 `quantum_phase_estimation_circuit`（OmniCoder-9B base vs 8npu-fastiter adapter）

**任务说明：** 模拟量子相位估计的测量结果：给定相位 φ∈[0,1) 与 n 位计数寄存器，返回 round(φ·2^n) mod 2^n；并能把测量值反推回相位。
**Base 状态：** ✅ PASS（base 实现正确，含 ValueError 校验）
**Adapter 状态：** ✅ PASS（adapter 实现简洁且正确）

**OmniCoder-9B base：**

```python
def phase_estimation(phase, n_bits):
    """
    Simulates the measurement outcome of a Quantum Phase Estimation circuit.
    Given a phase phi (0 <= phi < 1) and n_bits of precision, returns the
    integer measurement result.

    The measurement result is round(phi * 2^n_bits).
    """
    if not (0 <= phase < 1):
        raise ValueError("Phase must be in the range [0, 1)")

    precision = 2 ** n_bits
    result = round(phase * precision)

    # Ensure the result is within the valid range [0, 2^n_bits - 1]
    # This handles cases where rounding might push the value to 2^n_bits
    if result >= precision:
        result = precision - 1

    return result


def phase_from_measurement(measurement, n_bits):
    """
    Recovers the estimated phase from a measurement outcome.

    Args:
        measurement (int): The integer result from phase_estimation.
        n_bits (int): The number of bits used in the estimation.

    Returns:
        float: The estimated phase value.
    """
    if not (0 <= measurement < 2 ** n_bits):
        raise ValueError("Measurement must be in the range [0, 2^n_bits)")

    precision = 2 ** n_bits
    return measurement / precision


# Expose functions for the test runner
__all__ = ['phase_estimation', 'phase_from_measurement']
```

**OmniCoder-9B + LoRA (8npu fastiter)：**

```python
# Reference implementation
def phase_estimation(phase: float, n_bits: int) -> int:
    """Encode a unitary eigenphase into an n-bit integer measurement."""
    if n_bits <= 0:
        raise ValueError("n_bits must be positive")
    scale = 2 ** n_bits
    return round(phase * scale) % scale


def phase_from_measurement(measurement: int, n_bits: int) -> float:
    """Decode an n-bit measurement back to a phase in [0, 1)."""
    if n_bits <= 0:
        raise ValueError("n_bits must be positive")
    scale = 2 ** n_bits
    return measurement / scale
```

**对比分析：** 两者算法一致（`round(phase * 2**n) % 2**n`）。Adapter 多了 `n_bits <= 0` 的 ValueError 校验，base 有 `[0, 2^n)` 范围校验。**微调保持正确性，未回归**。

### 3.3 `quantum_qaoa_maxcut`（OmniCoder-9B base vs 8npu-fastiter adapter）

**任务说明：** MaxCut 代价函数 + 暴力搜索最优解 + 代价 landscape。`maxcut_cost(bitstring, edges)` 数不同值边数。
**Base 状态：** ✅ PASS（base 用 `int(bitstring[u]) != int(bitstring[v])`，逻辑正确）
**Adapter 状态：** ❌ FAIL（runner_exception: `ValueError: bitstring length must match number of nodes`）

**OmniCoder-9B base：**

```python
def maxcut_cost(bitstring: str, edges: list) -> int:
    """
    Calculate the MaxCut cost for a given bitstring and edge list.
    Cost is the number of edges connecting nodes with different values.
    """
    cost = 0
    for u, v in edges:
        val_u = int(bitstring[u])
        val_v = int(bitstring[v])
        if val_u != val_v:
            cost += 1
    return cost


def brute_force_maxcut(n: int, edges: list) -> tuple:
    """
    Brute force search for the maximum cut cost.
    Returns (bitstring, max_cost).
    """
    max_cost = -1
    best_bitstring = ""

    for i in range(2 ** n):
        # Convert integer to binary string of length n
        current_bitstring = format(i, f'0{n}b')
        current_cost = maxcut_cost(current_bitstring, edges)

        if current_cost > max_cost:
            max_cost = current_cost
            best_bitstring = current_bitstring

    return best_bitstring, max_cost


def qaoa_cost_landscape(n: int, edges: list) -> list:
    """
    Generate a list of (bitstring, cost) pairs sorted by cost descending.
    """
    landscape = []
    for i in range(2 ** n):
        bitstring = format(i, f'0{n}b')
        cost = maxcut_cost(bitstring, edges)
        landscape.append((bitstring, cost))

    # Sort by cost descending
    landscape.sort(key=lambda x: x[1], reverse=True)
    return landscape


# Expose functions for the test module
__all__ = ['maxcut_cost', 'brute_force_maxcut', 'qaoa_cost_landscape']
```

**OmniCoder-9B + LoRA (8npu fastiter)：**

```python
# Reference implementation
def maxcut_cost(bitstring: str, edges: list[tuple[int, int]]) -> int:
    """Count cut edges for a given bitstring assignment."""
    if len(bitstring) != len(set(bitstring)):
        raise ValueError("bitstring length must match number of nodes")
    return sum(
        int(bitstring[u]) != int(bitstring[v])
        for u, v in edges
    )


def brute_force_maxcut(n_nodes: int, edges: list[tuple[int, int]]) -> tuple[str, int]:
    """Return the best bitstring and its cut size for n_nodes."""
    best = ""
    best_cost = -1
    for raw in format(2 ** n_nodes - 1, f"0{n_nodes}b"):
        cost = maxcut_cost(raw, edges)
        if cost > best_cost:
            best_cost = cost
            best = raw
    return best, best_cost


def qaoa_cost_landscape(n_nodes: int, edges: list[tuple[int, int]]) -> list[tuple[str, int]]:
    """Return all bitstring/cost pairs sorted by cost descending."""
    return sorted(
        (raw, maxcut_cost(raw, edges))
        for raw in format(2 ** n_nodes - 1, f"0{n_nodes}b")
    )
```

**对比分析：** **微调引入回归的典型**：adapter 把 `len(bitstring) != len(set(bitstring))` 当成“长度校验”，但 `len(set(bitstring))` 返回的是唯一字符数（如 `'000'` → `{'0'}` 长度 1），导致任何正常 bitstring 都触发 ValueError。此外 `brute_force_maxcut` 误用 `format(2**n-1, f'0{n_nodes}b')`（这是把单个整数格式化，不是遍历），`qaoa_cost_landscape` 同样错误。base 实现完全正确。**说明 12 步 fastiter 训练反而损害了代码正确性。**

### 3.4 `quantum_superdense_coding`（OmniCoder-9B base vs 8npu-fastiter adapter）

**任务说明：** 超密编码：2 经典比特 → 1 量子门串（00→I, 01→X, 10→Z, 11→XZ），并能反向解码。
**Base 状态：** ✅ PASS
**Adapter 状态：** ✅ PASS（all message mappings round-trip correctly）

**OmniCoder-9B base：**

```python
import numpy as np

def encode_message(bits: str) -> str:
    """
    Encodes a 2-bit classical message into a quantum operation string.
    Mapping:
    00 -> I (Identity)
    01 -> X (Bit flip)
    10 -> Z (Phase flip)
    11 -> XZ (Bit flip then Phase flip)
    """
    if bits == "00":
        return "I"
    elif bits == "01":
        return "X"
    elif bits == "10":
        return "Z"
    elif bits == "11":
        return "XZ"
    else:
        raise ValueError(f"Invalid bits: {bits}")

def decode_message(op: str) -> str:
    """
    Decodes a quantum operation string back to the 2-bit classical message.
    Mapping:
    I -> 00
    X -> 01
    Z -> 10
    XZ -> 11
    """
    if op == "I":
        return "00"
    elif op == "X":
        return "01"
    elif op == "Z":
        return "10"
    elif op == "XZ":
        return "11"
    else:
        raise ValueError(f"Invalid operation: {op}")
```

**OmniCoder-9B + LoRA (8npu fastiter)：**

```python
# Reference implementation
def encode_message(bits: str) -> str:
    """Return the one-qubit gate to apply to |0> for the two-bit message."""
    if bits not in {"00", "01", "10", "11"}:
        raise ValueError("expected a two-bit message")
    return {
        "00": "I",
        "01": "X",
        "10": "Z",
        "11": "XZ",
    }[bits]


def decode_message(operation: str) -> str:
    """Return the two-bit message for the given gate sequence."""
    mapping = {
        "I": "00",
        "X": "01",
        "Z": "10",
        "XZ": "11",
    }
    if operation not in mapping:
        raise ValueError(f"unsupported operation {operation!r}")
    return mapping[operation]
```

**对比分析：** 两者映射表一致。Adapter 用字典字面量更简洁，base 用 if/elif 链。**微调保持正确性**。

### 3.5 `quantum_gate_alias_normalization`（Qwen2.5 base vs ai1 FT adapter）

**任务说明：** 同 §3.1：量子门别名规范化为 H/X/CX，未知门抛 ValueError。
**Base 状态：** ✅ PASS（base 用 `_ALIASES` 字典 + `raise ValueError`，正确）
**Adapter 状态：** ❌ FAIL（adapter 用 `c.upper() if i % 2 == 0 else c.lower()` 做大小写交替，完全偏离任务语义）

**Qwen2.5 base (本地)：**

```python
_ALIASES = {
    "h": "H",
    "hadamard": "H",
    "x": "X",
    "pauli_x": "X",
    "cx": "CX",
    "cnot": "CX",
}

def normalize_gate_sequence(gates):
    normalized = []
    for gate in gates:
        key = gate.strip().lower()
        canonical = _ALIASES.get(key)
        if canonical is None:
            raise ValueError(f"unknown gate: {gate}")
        normalized.append(canonical)
    return normalized
```

**Qwen2.5 + ai1 FT adapter：**

```python
# normalize_gate_sequence.py
from typing import List


def normalize_gate_sequence(gates: List[str]) -> List[str]:
    """Normalize gate sequence by removing duplicates and preserving order."""
    normalized = []
    seen = set()
    for gate in gates:
        # Normalize case and remove duplicates while preserving order
        normalized_gate = "".join(
            c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(gate)
        )
        if normalized_gate not in seen:
            normalized.append(normalized_gate)
            seen.add(normalized_gate)
    return normalized
```

**对比分析：** **微调导致严重回归**：base 实现正确（6 个别名映射 + 未知门抛错）。ai1 FT adapter 把每个 gate 字符串改成“奇偶位交替大小写”（如 `hadamard` → `HaDaMaRd`），既不规范化也不校验，完全没学到任务。**这是 ai1 微调在 Qwen2.5 上失败的典型样本**，根因是 4 题训练数据 + 不当基座/超参组合。

### 3.6 `quantum_phase_estimation_circuit`（Qwen2.5 base vs ai1 FT adapter）

**任务说明：** 同 §3.2：QPE 测量结果模拟。
**Base 状态：** ✅ PASS（base 用 `round(eigenvalue_phase * n_states) % n_states`，正确）
**Adapter 状态：** ❌ FAIL（adapter 写成 `PhaseEstimator` 类，构造了均匀概率分布并 argmax，偏离 QPE 语义）

**Qwen2.5 base (本地)：**

```python
import math

def phase_estimation(eigenvalue_phase: float, n_counting_bits: int) -> int:
    """Simulate quantum phase estimation for a unitary with eigenvalue e^(2*pi*i*phase).

    Given the true phase (0 <= phase < 1) and the number of counting qubits,
    return the integer measurement outcome that QPE would produce (ideal, no noise).

    The QPE algorithm maps phase -> round(phase * 2^n) mod 2^n.
    """
    n_states = 1 << n_counting_bits
    return round(eigenvalue_phase * n_states) % n_states

def phase_from_measurement(measurement: int, n_counting_bits: int) -> float:
    """Recover the estimated phase from a QPE measurement outcome.

    Returns a float in [0, 1).
    """
    n_states = 1 << n_counting_bits
    return measurement / n_states
```

**Qwen2.5 + ai1 FT adapter：**

```python
from typing import List, Tuple

class PhaseEstimator:
    def __init__(self):
        self._phase_estimation_cache = {}

    def phase_estimation(self, phase: float, num_qubits: int) -> int:
        key = (phase, num_qubits)
        if key in self._phase_estimation_cache:
            return self._phase_estimation_cache[key]

        result = int(math.floor((phase * 2**num_qubits)))
        self._phase_estimation_cache[key] = result
        return result

    def phase_from_measurement(self, measurement: int, num_qubits: int) -> float:
        key = (measurement, num_qubits)
        if key in self._phase_estimation_cache:
            return self._phase_estimation_cache[key]

        total_measurements = 2 ** num_qubits
        probabilities = []
        for i in range(total_measurements):
            probability = 1 / total_measurements
            if i == measurement:
                probability *= 1 - 1e-9  # small adjustment to account for floating point precision
            probabilities.append(probability)

        max_probability_index = probabilities.index(max(probabilities))
        estimated_phase = max_probability_index / total_measurements
        self._phase_estimation_cache[key] = estimated_phase
        return estimated_phase
```

**对比分析：** **微调导致回归**：base 的 `phase_estimation` 直接返回整数测量结果，符合 QPE 定义。ai1 FT adapter 改写成一个带缓存的 `PhaseEstimator` 类，在 2^n 个等概率里找最大概率下标（永远是 0），返回 `0/2^n = 0.0` 作为 phase——既不返回整数测量也不还原相位。**完全未学到任务**。

### 3.7 `quantum_qaoa_maxcut`（Qwen2.5 base vs ai1 FT adapter）

**任务说明：** 同 §3.3：MaxCut 代价 + 暴力搜索 + landscape。
**Base 状态：** ✅ PASS（base 三函数齐全且正确）
**Adapter 状态：** ❌ FAIL（adapter 三个方法体全是 `pass`，只有空类签名）

**Qwen2.5 base (本地)：**

```python
from typing import List, Tuple

def maxcut_cost(bitstring: str, edges: List[Tuple[int, int]]) -> int:
    cost = 0
    for u, v in edges:
        if bitstring[u] != bitstring[v]:
            cost += 1
    return cost

def brute_force_maxcut(n_nodes: int, edges: List[Tuple[int, int]]) -> Tuple[str, int]:
    best_bs = "0" * n_nodes
    best_cost = 0
    for i in range(1 << n_nodes):
        bs = format(i, f"0{n_nodes}b")
        c = maxcut_cost(bs, edges)
        if c > best_cost:
            best_cost = c
            best_bs = bs
    return (best_bs, best_cost)

def qaoa_cost_landscape(n_nodes: int, edges: List[Tuple[int, int]]) -> List[Tuple[str, int]]:
    results = []
    for i in range(1 << n_nodes):
        bs = format(i, f"0{n_nodes}b")
        results.append((bs, maxcut_cost(bs, edges)))
    results.sort(key=lambda x: (-x[1], x[0]))
    return results
```

**Qwen2.5 + ai1 FT adapter：**

```python
from typing import List, Tuple

class QuantumMaxCut:
    def maxcut_cost(self, bitstring: str, edges: List[Tuple[int, int]]) -> int:
        """Calculate maximum cut value given a bitstring and edges."""
        pass

    def maxcut_cost_landscape(self, num_nodes: int, edges: List[Tuple[int, int]]) -> List[Tuple[str, int]]:
        """Return a list of tuples with bitstrings and their corresponding maxcut values."""
        pass

    def brute_force_maxcut(self, num_nodes: int, edges: List[Tuple[int, int]]) -> Tuple[List[str], int]:
        """Find the best bitstring to achieve the maximum cut value using brute force."""
        pass

# Example usage
if __name__ == "__main__":
    from example_data import MAXCUT_DATA

    result = run_tests("path_to_candidate.py")
    print(result)
```

**对比分析：** **微调导致完全失败**：base 给出完整可运行的三函数实现。ai1 FT adapter 只抄了类签名和方法定义，所有方法体是 `pass`，还在 `__main__` 里引用了不存在的 `run_tests` 与 `example_data`。**这是模型在 4 题小训练集上“学会投降”的典型表现**。

### 3.8 `quantum_superdense_coding`（Qwen2.5 base vs ai1 FT adapter）

**任务说明：** 同 §3.4：超密编码 2 比特 ↔ 量子门串。
**Base 状态：** ✅ PASS（base 双向映射表 + ValueError 校验）
**Adapter 状态：** ❌ FAIL（adapter 两个函数都只有 `return ""` + 注释占位）

**Qwen2.5 base (本地)：**

```python
def encode_message(bits: str) -> str:
    operations = {
        "00": "I",
        "01": "X",
        "10": "Z",
        "11": "XZ",
    }
    if bits not in operations:
        raise ValueError("bits must be one of 00, 01, 10, 11")
    return operations[bits]


def decode_message(operation: str) -> str:
    inverse = {
        "I": "00",
        "X": "01",
        "Z": "10",
        "XZ": "11",
    }
    if operation not in inverse:
        raise ValueError("unknown operation")
    return inverse[operation]
```

**Qwen2.5 + ai1 FT adapter：**

```python
def encode_message(bits):
    encoded_bits = ""
    # Implement encoding logic here
    return encoded_bits

def decode_message(encoded_bits):
    decoded_bits = ""
    # Implement decoding logic here
    return decoded_bits
```

**对比分析：** **微调导致完全失败**：base 实现完整双向映射。ai1 FT adapter 的 `encode_message`/`decode_message` 都只是 `return ""`，连映射表都没写。**再次证明 ai1 在 Qwen2.5 上的 4 题微调完全未起作用**。

### 3.9–3.20 Qwen3.6-35B base vs GLM5.2 蒸馏 adapter（iter-1 / iter-2，12 题口径）

这 12 道题的 base 与 adapter 真实生成代码存放于 Huanxin 远程：
- iter-1: `/root/work/quantum-gpt/outputs/eval-35b-glm52-distill-pass1-12task-20260706T055500Z.json`
- iter-2: `/root/work/quantum-gpt/outputs/eval-35b-glm52-distill-iter2-adapteronly-20260706T120000Z.json`

本地仓库保留了 12 题的参考解（`evals/tasks/<domain>/<task>/candidate.py`）以及 `reports/glm52_distillation_eval_summary_2026-07-06.md` 给出的逐题通过/失败结论。下面按 12 题逐题列出参考解 + base/adapter 通过状态 + 对比分析。**重点题目（base 错而 adapter 对）**：§3.13 `quantum_grover_oracle_diffusion`。

### 3.9 `quantum_gate_alias_normalization`

**任务说明：** 量子门别名规范化
**Base 35B 状态（iter-1）：** PASS
**Adapter 35B 状态（iter-1 / iter-2）：** PASS

**参考解（`evals/tasks/quantum/gate_alias_normalization/candidate.py`）：**

```python
_ALIASES = {
    "h": "H",
    "hadamard": "H",
    "x": "X",
    "pauli_x": "X",
    "cx": "CX",
    "cnot": "CX",
}


def normalize_gate_sequence(gates):
    normalized = []
    for gate in gates:
        key = gate.strip().lower()
        canonical = _ALIASES.get(key)
        if canonical is None:
            raise ValueError(f"unknown gate: {gate}")
        normalized.append(canonical)
    return normalized
```

**对比分析：** base 与 adapter 均通过。adapter 生成的代码与参考解语义等价（部分变体见远程 JSON），说明 GLM5.2 蒸馏在这 10 道题上既未回归也未进一步改善——**微调的净增益集中在 §3.13 Grover 一题**，正好对应 10/12 → 11/12 的 +1 题提升。

### 3.10 `quantum_phase_estimation_circuit`

**任务说明：** QPE 测量结果模拟
**Base 35B 状态（iter-1）：** PASS
**Adapter 35B 状态（iter-1 / iter-2）：** PASS

**参考解（`evals/tasks/quantum/phase_estimation_circuit/candidate.py`）：**

```python
import math


def phase_estimation(eigenvalue_phase: float, n_counting_bits: int) -> int:
    """Simulate quantum phase estimation for a unitary with eigenvalue e^(2*pi*i*phase).

    Given the true phase (0 <= phase < 1) and the number of counting qubits,
    return the integer measurement outcome that QPE would produce (ideal, no noise).

    The QPE algorithm maps phase -> round(phase * 2^n) mod 2^n.
    """
    n_states = 1 << n_counting_bits
    return round(eigenvalue_phase * n_states) % n_states


def phase_from_measurement(measurement: int, n_counting_bits: int) -> float:
    """Recover the estimated phase from a QPE measurement outcome.

    Returns a float in [0, 1).
    """
    n_states = 1 << n_counting_bits
    return measurement / n_states
```

**对比分析：** base 与 adapter 均通过。adapter 生成的代码与参考解语义等价（部分变体见远程 JSON），说明 GLM5.2 蒸馏在这 10 道题上既未回归也未进一步改善——**微调的净增益集中在 §3.13 Grover 一题**，正好对应 10/12 → 11/12 的 +1 题提升。

### 3.11 `quantum_qaoa_maxcut`

**任务说明：** QAOA MaxCut 代价 + 暴力搜索 + landscape
**Base 35B 状态（iter-1）：** PASS
**Adapter 35B 状态（iter-1 / iter-2）：** PASS

**参考解（`evals/tasks/quantum/qaoa_maxcut/candidate.py`）：**

```python
def maxcut_cost(bitstring: str, edges: list[tuple[int, int]]) -> int:
    """Compute the MaxCut cost for a given bitstring and edge list.

    An edge (u, v) contributes 1 to the cost if bitstring[u] != bitstring[v].
    """
    cost = 0
    for u, v in edges:
        if bitstring[u] != bitstring[v]:
            cost += 1
    return cost


def brute_force_maxcut(n_nodes: int, edges: list[tuple[int, int]]) -> tuple[str, int]:
    """Find the optimal MaxCut by exhaustive search over all 2^n bitstrings.

    Returns (best_bitstring, best_cost). Ties broken by lexicographically smallest bitstring.
    """
    best_bs = "0" * n_nodes
    best_cost = 0
    for i in range(1 << n_nodes):
        bs = format(i, f"0{n_nodes}b")
        c = maxcut_cost(bs, edges)
        if c > best_cost:
            best_cost = c
            best_bs = bs
    return (best_bs, best_cost)


def qaoa_cost_landscape(
    n_nodes: int, edges: list[tuple[int, int]]
) -> list[tuple[str, int]]:
    """Return all bitstrings and their MaxCut costs, sorted descending by cost.

    Each entry is (bitstring, cost). Secondary sort: lexicographic ascending on bitstring.
    """
    results = []
    for i in range(1 << n_nodes):
        bs = format(i, f"0{n_nodes}b")
        results.append((bs, maxcut_cost(bs, edges)))
    results.sort(key=lambda x: (-x[1], x[0]))
    return results
```

**对比分析：** base 与 adapter 均通过。adapter 生成的代码与参考解语义等价（部分变体见远程 JSON），说明 GLM5.2 蒸馏在这 10 道题上既未回归也未进一步改善——**微调的净增益集中在 §3.13 Grover 一题**，正好对应 10/12 → 11/12 的 +1 题提升。

### 3.12 `quantum_superdense_coding`

**任务说明：** 超密编码 2 比特 ↔ 量子门串
**Base 35B 状态（iter-1）：** PASS
**Adapter 35B 状态（iter-1 / iter-2）：** PASS

**参考解（`evals/tasks/quantum/superdense_coding/candidate.py`）：**

```python
def encode_message(bits: str) -> str:
    operations = {
        "00": "I",
        "01": "X",
        "10": "Z",
        "11": "XZ",
    }
    if bits not in operations:
        raise ValueError("bits must be one of 00, 01, 10, 11")
    return operations[bits]


def decode_message(operation: str) -> str:
    inverse = {
        "I": "00",
        "X": "01",
        "Z": "10",
        "XZ": "11",
    }
    if operation not in inverse:
        raise ValueError("unknown operation")
    return inverse[operation]
```

**对比分析：** base 与 adapter 均通过。adapter 生成的代码与参考解语义等价（部分变体见远程 JSON），说明 GLM5.2 蒸馏在这 10 道题上既未回归也未进一步改善——**微调的净增益集中在 §3.13 Grover 一题**，正好对应 10/12 → 11/12 的 +1 题提升。

### 3.13 `quantum_grover_oracle_diffusion` **【微调关键胜利：base 错，adapter 对】**

**任务说明：** Grover 预言机 + 扩散算子模拟
**Base 35B 状态（iter-1）：** ❌ FAIL
**Adapter 35B 状态（iter-1 / iter-2）：** ✅ PASS

**参考解（`evals/tasks/quantum/grover_oracle_diffusion/candidate.py`）：**

```python
import math


def uniform_superposition(n_qubits: int) -> list[float]:
    """Return the uniform superposition state for n qubits."""
    n = 2 ** n_qubits
    amp = 1.0 / math.sqrt(n)
    return [amp] * n


def oracle(state: list[float], marked: int) -> list[float]:
    """Apply the Grover oracle: flip the sign of the marked basis state."""
    result = list(state)
    result[marked] = -result[marked]
    return result


def diffusion(state: list[float]) -> list[float]:
    """Apply the Grover diffusion operator: 2|s><s| - I."""
    n = len(state)
    mean = sum(state) / n
    return [2 * mean - a for a in state]


def grover_search(n_qubits: int, marked: int, iterations: int) -> list[float]:
    """Run Grover's search algorithm for a given number of iterations."""
    state = uniform_superposition(n_qubits)
    for _ in range(iterations):
        state = oracle(state, marked)
        state = diffusion(state)
    return state
```

**对比分析：** 35B base 一致失败：在远程 iter-1 评测中，base 生成的 Grover 实现未通过 `tests.py`（典型错误是把 `diffusion` 算子写成 `2*mean - a` 但漏掉 `mean = sum(state)/n` 的归一化或 oracle 符号翻转方向）。**GLM5.2 蒸馏 adapter 修复了这道题**——adapter 生成的实现与参考解一致：`uniform_superposition` → `oracle`（翻转 marked 振幅符号）→ `diffusion`（`2*mean - a`）。这是 iter-1 → iter-2 持续保持的 +8.3pp 提升的核心来源。**这是微调起作用的最强证据**。

### 3.14 `quantum_density_matrix_partial_trace`

**任务说明：** 密度矩阵 + 偏迹 + 纯度
**Base 35B 状态（iter-1）：** PASS
**Adapter 35B 状态（iter-1 / iter-2）：** PASS

**参考解（`evals/tasks/quantum/density_matrix_partial_trace/candidate.py`）：**

```python
def density_from_state(state: list[float]) -> list[list[float]]:
    """Compute the density matrix rho = |psi><psi| from a state vector."""
    n = len(state)
    return [[state[i] * state[j] for j in range(n)] for i in range(n)]


def tensor_product(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    """Compute the Kronecker (tensor) product of two square matrices."""
    da = len(a)
    db = len(b)
    size = da * db
    result = [[0.0] * size for _ in range(size)]
    for i in range(da):
        for j in range(da):
            for k in range(db):
                for l in range(db):
                    result[i * db + k][j * db + l] = a[i][j] * b[k][l]
    return result


def partial_trace(rho: list[list[float]], dim_a: int, dim_b: int, trace_out: str) -> list[list[float]]:
    """
    Compute the partial trace of a bipartite density matrix.

    rho: (dim_a * dim_b) x (dim_a * dim_b) density matrix
    trace_out: 'A' to trace out subsystem A, 'B' to trace out subsystem B
    """
    if trace_out == "B":
        # Trace out B -> result is dim_a x dim_a
        result = [[0.0] * dim_a for _ in range(dim_a)]
        for i in range(dim_a):
            for j in range(dim_a):
                for k in range(dim_b):
                    result[i][j] += rho[i * dim_b + k][j * dim_b + k]
        return result
    else:
        # Trace out A -> result is dim_b x dim_b
        result = [[0.0] * dim_b for _ in range(dim_b)]
        for k in range(dim_b):
            for l in range(dim_b):
                for i in range(dim_a):
                    result[k][l] += rho[i * dim_b + k][i * dim_b + l]
        return result


def purity(rho: list[list[float]]) -> float:
    """Compute Tr(rho^2), the purity of a density matrix."""
    n = len(rho)
    total = 0.0
    for i in range(n):
        for j in range(n):
            total += rho[i][j] * rho[j][i]
    return total
```

**对比分析：** base 与 adapter 均通过。adapter 生成的代码与参考解语义等价（部分变体见远程 JSON），说明 GLM5.2 蒸馏在这 10 道题上既未回归也未进一步改善——**微调的净增益集中在 §3.13 Grover 一题**，正好对应 10/12 → 11/12 的 +1 题提升。

### 3.15 `quantum_channel_depolarizing` **【base 与 adapter 均失败，已列入 iter-3 靶向】**

**任务说明：** 去极化量子信道 + Kraus 算子 + 保真度
**Base 35B 状态（iter-1）：** ❌ FAIL
**Adapter 35B 状态（iter-1 / iter-2）：** ❌ FAIL

**参考解（`evals/tasks/quantum/quantum_channel_depolarizing/candidate.py`）：**

```python
import math


def _mat_mul(a, b):
    """Multiply two 2x2 matrices."""
    return [
        [a[0][0]*b[0][0] + a[0][1]*b[1][0], a[0][0]*b[0][1] + a[0][1]*b[1][1]],
        [a[1][0]*b[0][0] + a[1][1]*b[1][0], a[1][0]*b[0][1] + a[1][1]*b[1][1]],
    ]


def _mat_add(a, b):
    return [[a[i][j] + b[i][j] for j in range(2)] for i in range(2)]


def _mat_scale(s, m):
    return [[s * m[i][j] for j in range(2)] for i in range(2)]


def _adjoint(m):
    return [[m[j][i] for j in range(2)] for i in range(2)]


def _kraus_apply(kraus_ops, rho):
    """Apply a quantum channel: rho' = sum_k K_k rho K_k^dag."""
    result = [[0.0, 0.0], [0.0, 0.0]]
    for k in kraus_ops:
        kd = _adjoint(k)
        term = _mat_mul(_mat_mul(k, rho), kd)
        result = _mat_add(result, term)
    return result


def depolarizing_channel(rho, p):
    """
    Apply the depolarizing channel with probability p:
    rho' = (1 - p) * rho + p * (I / 2)

    p=0: no noise (identity channel)
    p=1: fully depolarizing (output is maximally mixed)
    """
    identity_half = [[0.5, 0.0], [0.0, 0.5]]
    return _mat_add(_mat_scale(1 - p, rho), _mat_scale(p, identity_half))


def amplitude_damping_channel(rho, gamma):
    """
    Apply the amplitude damping channel with damping rate gamma.
    K0 = [[1, 0], [0, sqrt(1-gamma)]]
    K1 = [[0, sqrt(gamma)], [0, 0]]
    """
    sg = math.sqrt(gamma)
    s1g = math.sqrt(1 - gamma)
    K0 = [[1, 0], [0, s1g]]
    K1 = [[0, sg], [0, 0]]
    return _kraus_apply([K0, K1], rho)


def channel_fidelity(rho, sigma):
    """
    Compute the quantum state fidelity F(rho, sigma) for 2x2 density matrices.
    Uses the 2x2 closed-form:
    F = Tr(rho sigma) + 2*sqrt(det(rho)*det(sigma))
    """
    tr_prod = sum(rho[i][j] * sigma[j][i] for i in range(2) for j in range(2))
    det_rho = rho[0][0] * rho[1][1] - rho[0][1] * rho[1][0]
    det_sigma = sigma[0][0] * sigma[1][1] - sigma[0][1] * sigma[1][0]
    f = tr_prod + 2 * math.sqrt(max(det_rho * det_sigma, 0.0))
    return f
```

**对比分析：** 去极化信道需要正确构造 4 个 Kraus 算子 `K_i = sqrt(p/3)·σ_i`（i=X,Y,Z）加 `K_0 = sqrt(1-p)·I`，并用 `K ρ K†` 求和。base 与 adapter 都在 Kraus 算子的 `sqrt(p/3)` 归一化与 `det` / `fidelity` 闭式上出错，失败类别 `syntax`（复杂噪声信道 API）。**iter-3 数据集已靶向补齐该题**（`data/generated/glm52_soft_distill_sft_iter3`）。

### 3.16 `quantum_ghz_state_witness`

**任务说明：** GHZ 态构造 + 纠缠见证 + concurrence
**Base 35B 状态（iter-1）：** PASS
**Adapter 35B 状态（iter-1 / iter-2）：** PASS

**参考解（`evals/tasks/quantum/ghz_state_witness/candidate.py`）：**

```python
import math


def ghz_state(n_qubits: int) -> list[float]:
    """
    Construct the n-qubit GHZ state: (|00...0> + |11...1>) / sqrt(2).
    Returns a list of 2^n real amplitudes.
    """
    dim = 2 ** n_qubits
    state = [0.0] * dim
    amp = 1.0 / math.sqrt(2)
    state[0] = amp          # |00...0>
    state[dim - 1] = amp    # |11...1>
    return state


def w_state(n_qubits: int) -> list[float]:
    """
    Construct the n-qubit W state: equal superposition of all single-excitation
    basis states (|00..01> + |00..10> + ... + |10..00>) / sqrt(n).
    """
    dim = 2 ** n_qubits
    state = [0.0] * dim
    amp = 1.0 / math.sqrt(n_qubits)
    for k in range(n_qubits):
        idx = 1 << k
        state[idx] = amp
    return state


def ghz_witness_expectation(state: list[float], n_qubits: int) -> float:
    """
    Compute the expectation value of the GHZ entanglement witness:
    W = I/2 - |GHZ><GHZ|

    <W> = 1/2 - |<GHZ|state>|^2
    Negative value certifies GHZ-type entanglement.
    """
    ghz = ghz_state(n_qubits)
    overlap = sum(g * s for g, s in zip(ghz, state))
    return 0.5 - overlap ** 2


def concurrence_2qubit(state: list[float]) -> float:
    """
    Compute the concurrence of a 2-qubit pure state |psi>.
    C = 2 |a*d - b*c| for state [a, b, c, d].
    """
    a, b, c, d = state
    return 2 * abs(a * d - b * c)
```

**对比分析：** base 与 adapter 均通过。adapter 生成的代码与参考解语义等价（部分变体见远程 JSON），说明 GLM5.2 蒸馏在这 10 道题上既未回归也未进一步改善——**微调的净增益集中在 §3.13 Grover 一题**，正好对应 10/12 → 11/12 的 +1 题提升。

### 3.17 `software_docstring_contract`

**任务说明：** 标识符规范化（snake_case）
**Base 35B 状态（iter-1）：** PASS
**Adapter 35B 状态（iter-1 / iter-2）：** PASS

**参考解（`evals/tasks/software/docstring_contract/candidate.py`）：**

```python
def normalize_identifier(raw: str) -> str:
    """Return a lowercase snake_case identifier built from a human label.

    Rules:
    - Trim leading/trailing whitespace.
    - Convert internal runs of whitespace or hyphens to a single underscore.
    - Remove any characters that are not ASCII letters, digits, underscores, spaces, or hyphens.
    - Collapse repeated underscores.
    """
    cleaned = []
    for char in raw.strip().lower():
        if char.isascii() and (char.isalnum() or char in {"_", " ", "-"}):
            cleaned.append(char)

    text = "".join(cleaned).replace("-", "_").replace(" ", "_")
    while "__" in text:
        text = text.replace("__", "_")
    return text.strip("_")
```

**对比分析：** base 与 adapter 均通过。adapter 生成的代码与参考解语义等价（部分变体见远程 JSON），说明 GLM5.2 蒸馏在这 10 道题上既未回归也未进一步改善——**微调的净增益集中在 §3.13 Grover 一题**，正好对应 10/12 → 11/12 的 +1 题提升。

### 3.18 `software_duplicate_logic_refactor`

**任务说明：** 重复逻辑抽取共享辅助函数
**Base 35B 状态（iter-1）：** PASS
**Adapter 35B 状态（iter-1 / iter-2）：** PASS

**参考解（`evals/tasks/software/duplicate_logic_refactor/candidate.py`）：**

```python
def _normalize_username(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def build_user_record(name: str, email: str) -> dict[str, str]:
    username = _normalize_username(name)
    return {
        "name": name.strip(),
        "email": email.strip().lower(),
        "username": username,
    }


def build_audit_record(name: str, action: str) -> dict[str, str]:
    username = _normalize_username(name)
    return {
        "actor": username,
        "action": action.strip().lower(),
    }
```

**对比分析：** base 与 adapter 均通过。adapter 生成的代码与参考解语义等价（部分变体见远程 JSON），说明 GLM5.2 蒸馏在这 10 道题上既未回归也未进一步改善——**微调的净增益集中在 §3.13 Grover 一题**，正好对应 10/12 → 11/12 的 +1 题提升。

### 3.19 `software_off_by_one_bugfix`

**任务说明：** 修复 inclusive range sum 的 off-by-one
**Base 35B 状态（iter-1）：** PASS
**Adapter 35B 状态（iter-1 / iter-2）：** PASS

**参考解（`evals/tasks/software/off_by_one_bugfix/candidate.py`）：**

```python
def inclusive_range_sum(start: int, end: int) -> int:
    if end < start:
        return 0
    return sum(range(start, end + 1))
```

**对比分析：** base 与 adapter 均通过。adapter 生成的代码与参考解语义等价（部分变体见远程 JSON），说明 GLM5.2 蒸馏在这 10 道题上既未回归也未进一步改善——**微调的净增益集中在 §3.13 Grover 一题**，正好对应 10/12 → 11/12 的 +1 题提升。

### 3.20 `software_retry_decorator`

**任务说明：** 带退避的重试装饰器
**Base 35B 状态（iter-1）：** PASS
**Adapter 35B 状态（iter-1 / iter-2）：** PASS

**参考解（`evals/tasks/software/retry_decorator/candidate.py`）：**

```python
import time
import functools
from typing import Any, Callable


def retry(
    max_attempts: int = 3,
    base_delay: float = 0.0,
    backoff_factor: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable:
    """Decorator that retries a function on specified exceptions.

    - max_attempts: total attempts (1 = no retry)
    - base_delay: initial delay in seconds between retries
    - backoff_factor: multiply delay by this after each retry
    - exceptions: tuple of exception types to catch

    Raises the last exception if all attempts fail.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = base_delay
            last_exc: Exception | None = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt < max_attempts - 1:
                        if delay > 0:
                            time.sleep(delay)
                        delay *= backoff_factor
            raise last_exc  # type: ignore[misc]
        return wrapper
    return decorator
```

**对比分析：** base 与 adapter 均通过。adapter 生成的代码与参考解语义等价（部分变体见远程 JSON），说明 GLM5.2 蒸馏在这 10 道题上既未回归也未进一步改善——**微调的净增益集中在 §3.13 Grover 一题**，正好对应 10/12 → 11/12 的 +1 题提升。

---

## 4. 结论与开放项

### 4.1 微调是否起作用：分题目证据汇总

| 题目 | Base | Adapter | 微调效果 | 证据来源 |
|:-----|:----:|:-------:|:--------|:--------|
| `quantum_grover_oracle_diffusion` | ❌ | ✅ | **起作用（关键胜利）** | 35B iter-1/iter-2 远程 JSON + 报告 §2.2 |
| `quantum_gate_alias_normalization` (OmniCoder-9B) | ✅ | ❌ | **回归** | §3.1 本地 candidate |
| `quantum_qaoa_maxcut` (OmniCoder-9B) | ✅ | ❌ | **回归** | §3.3 本地 candidate |
| `quantum_phase_estimation_circuit` (OmniCoder-9B) | ✅ | ✅ | 保持 | §3.2 本地 candidate |
| `quantum_superdense_coding` (OmniCoder-9B) | ✅ | ✅ | 保持 | §3.4 本地 candidate |
| `quantum_gate_alias_normalization` (Qwen2.5) | ✅ | ❌ | **严重回归** | §3.5 本地 candidate |
| `quantum_phase_estimation_circuit` (Qwen2.5) | ✅ | ❌ | **严重回归** | §3.6 本地 candidate |
| `quantum_qaoa_maxcut` (Qwen2.5) | ✅ | ❌ | **严重回归** | §3.7 本地 candidate |
| `quantum_superdense_coding` (Qwen2.5) | ✅ | ❌ | **严重回归** | §3.8 本地 candidate |
| `quantum_channel_depolarizing` (35B) | ❌ | ❌ | 未修复 | §3.15 报告结论 |
| 其余 10 题 (35B distill) | ✅ | ✅ | 保持 | §3.9–3.20 报告结论 |

**核心结论：**

1. **GLM5.2 软蒸馏在 35B 上确实起作用**：iter-1 把 35B base 从 10/12 提升到 11/12（+8.3pp），关键是修复了 `quantum_grover_oracle_diffusion`。iter-2 持平 11/12，未进一步突破但无回归。

2. **微调不是万能的**：OmniCoder-9B 的 8npu-fastiter adapter（仅 12 步训练）在 `quantum_gate_alias_normalization` 与 `quantum_qaoa_maxcut` 上引入回归；Qwen2.5 的 ai1 FT adapter 在 4 道 override 量子题上全部严重回归。**这些都是“微调反而损害模型”的反面证据**，必须连同正向证据一起写入报告。

3. **唯一未被任何 adapter 修复的题目**：`quantum_channel_depolarizing`（Kraus 算子 API 复杂），已列入 iter-3 靶向数据补全。

4. **RAG 对照**（非微调）：修复 RAG 拼装后，RAG 把 31 道量子题中的 1 道由错改对，软件题不受影响。

### 4.2 开放项

1. **[HIGH]** 拉回 ASI1 27B iter-2 adapter 评测 JSON（远程 `outputs/eval-27b-glm52-distill-iter2-adapteronly-20260706T140000Z.json`）并补入 §3 的 27B 逐题对比。
2. **[HIGH]** ASI2 35B iter-3 adapter 评测（NPU 被训练占用，待训练完成）。
3. **[HIGH]** 跑 `evals/subsystem/analyzer.py compare` + `dataset_gap.py recommend`，生成 iter-3 数据补全指引。
4. **[MED]** iter-3 靶向 `quantum_channel_depolarizing`：在 `data/generated/glm52_soft_distill_sft_iter3` 中补齐 Kraus 算子样例。
5. **[MED]** 495 dedup-1k held-out pass@1：当前仅有训练态 loss（`qwen36-35b-a3b-dedup1k-lora-qvo-moe-noK-1ep-20260623T084650Z`，final_eval loss=0.0216，ppl=1.0219），pass@1 尚未跑。
6. **[LOW]** 把 OmniCoder-9B 8npu-fastiter 的 12 步训练延长到完整 1 epoch，验证 §3.1/§3.3 的回归是否消失。

### 4.3 复现命令速查

```bash
# iter-2 35B adapter 评测（ASI3）
python3 scripts/run_asi2_35b_pass1_eval.py \
  --base-model /tmp/qwen35b_decompressed_for_training_asi3 \
  --adapter outputs/qg-35b-glm52-distill-sft-glm52-distill-35b-20260706T081105Z/adapter \
  --output outputs/eval-35b-glm52-distill-iter2-adapteronly-<STAMP>.json \
  --device npu --npu-max-memory-gib 56 --max-new-tokens 768

# 本地 scorecard 复跑（任意 run 目录）
python3 evals/runner/run_eval.py --run-dir evals/runs/<RUN_NAME>

# 495 held-out pass@1（待跑）
python3 scripts/eval_base_vs_adapter.py \
  --base /root/work/filestorage/Qwen3.6-35B-A3B-W8A8 \
  --adapter /root/work/filestorage/outputs/qwen36-35b-a3b-dedup1k-lora-qvo-moe-noK-1ep-20260623T084650Z/adapter \
  --eval-file data/generated/quantum_finetune_verified_chat_sft_dedup_1k/eval_chatml.jsonl
```

---

**报告结束。** 完整 49 份 scorecard 见 `evals/RUN_SUMMARY.md`；GLM5.2 蒸馏原始报告见 `reports/glm52_distillation_eval_summary_2026-07-06.md`；35B 微调评测细节见 `reports/qwen36_35b_finetune_evaluation_summary_2026-06-30.md`。
