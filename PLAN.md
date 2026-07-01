# PLAN.md

## 核心任务总览与估时
| 任务 (Task) | 做什么 (What) | 怎么做 (How) | 优先级 | 状态 | 风险 (Risk) | 价值 (Value) | 估时 (Time) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. 模型与Prompt基线建立** | 选定本地适合CPU开发的Qwen3.5小模型，设计并建立 baseline 及 3 大 Prompt 配方。 | 基于参数量/Tokenizer/上下文分析锁定小模型，生成 `model-target.md` 规范。 | 高 | 进行中 | 模型因尺寸过小导致量子逻辑语法在初期幻觉严重。 | 无 GPU 开销完成本地低门槛探索，对齐后续微调的标准。 | 1 - 2 天 |
| **2. 双领域高质数据集构建** | 收集量子算法设计与经典软件工程（Code edit/Fix/单测）的高质量指示数据集。 | 整合 Qiskit 样板、经典 Python edit 任务，设计 JSONL schema 自动过滤生成。 | 高 | 拟启动 | 自动化清洗不够干净或量子数据多样性不足，产生不精确写法。 | 丰富微调样本，保证模型兼具专业量子编程与极佳通用软质规范。 | 3 - 5 天 |
| **3. 本地自动化评测沙盒** | 建立秒级执行的本地执行沙盒，包含约40个黄金任务评测集（量+软）。 | 编写 `run_eval.py` 等轻量脚本，执行并比对输出与数值误差以计算 Pass@1。 | 高 | 框架已定，任务填充中 | 本地代码执行存在死循环或指令干扰，判定存在少许数值摆动。 | 在 GPU 预算投入前快速进行模型表现评估、防护退化，实现自动化测试熔断。 | 2 - 3 天 |
| **4. 远程微调与强化对齐** | 在远程 Huanxin `AI` 环境执行 Qwen3.6-27B 上的 LoRA/QLoRA 监督微调和 GRPO/RLvr 强化对齐。 | 通过 INER S3 同步无误代码与模型，使用 `ai_shell.sh` 远程拉起多卡微调。 | 中 | 路线连通，等待数据 | 显存 OOM、NPU 分布式框架不匹配或配额被非用户任务侵占。 | 突破小模型智力上限，获得兼具经典软工实力和高纯度量子编程的大模型。 | 4 - 7 天 |

**项目总体时间跨度估计：约 10 - 17 天**

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
