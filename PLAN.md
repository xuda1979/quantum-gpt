# PLAN.md

## 核心任务总览与估时（2026-07-08 更新，对齐两阶段路线）

| 任务 (Task) | 做什么 (What) | 怎么做 (How) | 优先级 | 状态 | 风险 (Risk) | 价值 (Value) | 估时 (Time) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. 模型与Prompt基线建立** | 锁定 Qwen3.6-27B（ASI1）与 Qwen3.6-35B-A3B（ASI2/ASI3）作为目标模型，建立 base-vs-adapter baseline prompt 与评测对照。 | 已在 `research/model-target.md` 与 `reports/qwen36_35b_finetune_evaluation_summary_2026-06-30.md` 记录基线；GLM5.2 作为教师。 | 高 | ✅ 完成 | 模型因尺寸/上下文导致量子语法幻觉。 | 为后续 LoRA 蒸馏提供可对照的冻结基线。 | 已交付 |
| **2. 双领域高质数据集构建** | 构建 GLM5.2 软蒸馏 SFT 数据集（量子代码 + 通用软工），含教师 top-logprobs 以支持后续 KL 蒸馏。 | `data/generated/glm52_soft_distill_sft_100`（90 训练/10 评测）已生成；iter-2 数据已用于训练；iter-3 数据脚手架 `scripts/prepare_iter3_distill_sft.py` 就绪，等 iter-2 eval gap report 填充。 | 高 | 进行中（iter-2 已训练，iter-3 待 gap report） | 量子数据多样性不足，`quantum_channel_depolarizing` 等噪声信道任务持续失败。 | 丰富微调样本，保证模型兼具专业量子编程与通用软工规范。 | 持续迭代 |
| **3. 评测子系统与本地沙盒** | 维护 `evals/subsystem/` 多维度评测基础设施（harness/analyzer/dataset_gap/reporter/tracker）+ ~44 任务黄金集 + 495 holdout。 | 2026-07-08 修复 v1 scorecard 解析 bug（analyzer/dataset_gap/reporter），新增 6 个回归测试；NPU 上 harness.py 运行 pass@1。 | 高 | ✅ 框架稳定，持续填充任务 | v1/v2 scorecard 格式兼容、远程 eval JSON 拉取延迟。 | 在 NPU 预算投入前快速评估、防护退化，自动生成 iter-N+1 数据缺口。 | 持续维护 |
| **4. 远程微调与强化对齐** | 在 Huanxin `AI`（ASI1/ASI2/ASI3）上对 Qwen3.6-27B/35B 执行 GLM5.2 软蒸馏 LoRA SFT，后续接 RL+软蒸馏迭代（`docs/rl-distill-iteration-process-2026-07.md`）。 | iter-1/iter-2 LoRA SFT 已在 ASI1(27B)/ASI3(35B) 完成；iter-2 adapter eval 进行中；RL+软蒸馏 pipeline 设计完成。 | 高 | 进行中（iter-2 eval 阶段） | NPU OOM、W8A8 解压耗时、Huanxin 会话保活、分布式框架兼容。 | 突破基模型上限，获得兼具量子编程与通用软工的大模型。 | 持续迭代（每轮 ~1.5 天） |
| **5. 阶段二：1000 篇论文科学能力** | 选择 1000 篇重要量子计算论文，生成循序渐进 QA + 代码实现任务，做蒸馏 SFT + 混合 RL。 | manifest schema 与验证脚本已就绪（`docs/stage2-science-corpus-manifest-schema-2026-07-07.md`）；paper-card 生成、QA 生成、验证工具待阶段一稳定后启动。 | 中 | 规划中（spec-only） | 论文版权/获取、QA 知觉正确性、与阶段一代码能力相互稀释。 | 赋予模型论文级科学推理与前沿研究感知能力。 | 阶段一稳定后启动 |

**当前迭代节奏：** 每轮 SFT ~1.5 天（含 W8A8 解压、训练、评测、诊断、数据生成、质量校验）。详见 `docs/glm52-distillation-rd-iteration-process-2026-07.md`。

## 2026-06-30 两阶段训练优先级

当前研发工作明确分为两个阶段：

1. **阶段一（现阶段）：代码能力训练。** 先把模型训练成可靠的量子代码与通用软件工程模型，重点是可运行代码、API 准确性、调试修复、单测、RAG 辅助查文档和执行反馈闭环。训练仍以高质量 SFT、轨迹克隆和可执行任务上的 GRPO/RLVR 为主，不能因为后续科学能力目标而稀释当前代码能力训练。
2. **阶段二（后续）：量子计算科学能力训练。** 在代码能力稳定后，选择 1000 篇重要和经典量子计算论文，生成循序渐进的论文理解问答，包括技术细节、方法、结论、公式推导、代码实现任务、局限性和进一步可行研究方向。先做蒸馏训练，再做强化学习与蒸馏的混合训练。

详细落地路线见 [docs/two-stage-training-roadmap-2026-06-30.md](docs/two-stage-training-roadmap-2026-06-30.md)。

## Goals
- Build a compact, fine-tunable quantum coding LLM centered on the smallest practical Qwen 3.5 instruct model.
- Improve two capabilities together: quantum algorithm reasoning/code generation and general software-engineering behavior.
- Produce a CPU-first research pipeline that can curate data, run lightweight evaluation, and de-risk later fine-tuning before any GPU spend.
- Create artifacts that compound: datasets, eval sets, prompting baselines, tooling, and documented decisions.

## Constraints
- Local CPU only for now: no dependence on GPU training, large-scale distributed infra, or expensive online services in the critical path.
- Prefer small, inspectable experiments over broad but shallow automation.
- Optimize for the smallest model that is still plausibly useful after targeted fine-tuning.
- Focus on reproducible data prep, task design, and eval harnesses that can be exercised locally.
- Treat software-engineering skill as first-class: correctness, editing, debugging, tests, and repo navigation matter alongside quantum knowledge.

## Workstreams
1. **Base-model selection and prompting**
   - Lock the exact smallest practical Qwen 3.5 candidate, context limits, tokenizer assumptions, and baseline prompting recipes.
2. **Quantum task/data program**
   - Curate a compact corpus around circuits, simulation, Hamiltonians, variational methods, error mitigation, and library-specific coding tasks.
   - Emphasize executable tasks in Qiskit, Cirq, PennyLane, and small NumPy-based simulators.
3. **Software-engineering task/data program**
   - Build code-edit, bug-fix, test-writing, refactor, and small feature tasks from clean local repos and synthetic micro-projects.
4. **Local evaluation harness**
   - Create CPU-friendly evals for exact-match, test-pass rate, edit success, and rubric-scored reasoning quality.
5. **Fine-tuning readiness**
   - Prepare conversation/task schemas, filtering rules, train/val/test splits, and parameter-efficient training configs for later execution.
6. **Research memory and iteration loop**
   - Log decisions, failures, dataset gaps, and next actions so each autonomous cycle advances one concrete artifact.

## First 10 Tasks
1. Identify and record the exact Qwen 3.5 small-model target and why it is the best CPU-first starting point.
2. Create a model card note capturing parameter count, context length, license, tokenizer, and likely fine-tuning options.
3. Draft a task taxonomy covering quantum explanation, quantum code generation, code repair, testing, repo edits, and debugging.
4. Define a minimal JSONL schema for supervised examples, edit tasks, and eval items.
5. Build a seed list of 25-50 quantum coding tasks that are executable on CPU with small inputs.
6. Build a seed list of 25-50 software-engineering tasks focused on local code editing and tests.
7. Implement a tiny local eval harness that can run unit tests, compare outputs, and summarize pass/fail per task.
8. Create a baseline prompt pack for the target model: direct answer, plan-then-code, and repair-focused prompts.
9. Assemble a small gold eval set (about 20 quantum + 20 software tasks) reserved from training data.
10. Write fine-tuning readiness notes: preferred PEFT approach, sequence packing assumptions, and dataset size targets for the first training run.

## Evaluation Strategy
- **Quantum capability**
  - Measure correctness on small CPU-runnable tasks: circuit construction, statevector expectations, simple VQE/QAOA scaffolds, simulator debugging, and concept-to-code translation.
  - Score with unit tests, numerical tolerances, and compact rubric checks for explanation quality.
- **Software-engineering capability**
  - Measure bug fixing, test generation, small feature implementation, refactoring, and repository edits.
  - Use pass@1 on unit-test tasks, edit-application success, lint/test outcomes, and concise human review on a small sample.
- **Baseline discipline**
  - Keep a frozen baseline prompt/eval report for the untouched base model before any tuning.
  - Compare every dataset or prompt change against the same held-out eval set.
- **CPU realism**
  - Prefer tiny but representative tasks that run in seconds to a few minutes locally.
  - Defer large-scale benchmarking until the local harness and task design are stable.

## Immediate Next Step
Create `research/model-target.md` that selects the exact smallest practical Qwen 3.5 model candidate, states the selection criteria, and lists the first CPU-friendly baseline prompts and eval assumptions.
