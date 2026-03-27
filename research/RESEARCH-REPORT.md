# Quantum Coding LLM 研究报告

**项目名称：** 面向量子算法编程与通用软件工程能力的小型代码模型研发  
**基础模型：** `Qwen2.5-1.5B-Instruct`  
**工作区：** `quantum-gpt`  
**报告语言：** 中文  
**最新更新时间：** 2026-03-27（中午）  

---

## 1. 先说结论

如果只看一句话，项目现在的状态是：

**主流程已经跑通，当前最好的路线是 `semantic-v4` 监督微调；`mix75` 混合数据已经跑通但暂时没有赢；强化学习还只是原型；现在最关键的工作是把定量结果和定性输出对上。**

更具体一点：

1. 本地研发闭环已经成立：改代码 -> 跑本地回归 -> 远端训练/评测 -> 回收结果 -> 更新数据和脚本。
2. 当前最好的训练结果来自：
   - `outputs/interface-prefix-semantic-v4-8npu-true20-e2-20260326T1627CST`
   - `final_eval.loss = 0.6986174695193768`
   - `final_eval.perplexity = 2.0109705566192857`
3. 新的混合数据实验 `mix75` 已经完成真实训练，但还没有超过纯 `semantic-v4`：
   - `outputs/codefirst-semantic-mix75-8npu-true20-e2-20260326T2118CST`
   - `final_eval.loss = 0.735347468405962`
   - `final_eval.perplexity = 2.086206757517806`
4. RL 训练器虽然已经有原型代码，但当前真正跑通、真正带来提升的仍然是 **数据工程 + LoRA SFT + 可执行评测** 这条线。
5. 当前主要基础设施问题不是“训练跑不起来”，而是：
   - `Huanxin -> S3` 写回大文件/整目录不稳定
   - 但小文件已经可以通过 `scripts/huanxin_fetch_small_file.sh` 直接回收，所以结果分析本身已经不再完全被卡死
6. 当前仍在进行中的两个远端任务：
   - `ai2`：`semantic-v4` 的固定切片定性评测仍在跑，目标报告还未落盘
   - `ai1`：`mix75` 的同切片定性评测已经启动过，但当前没有 fresh readback，所以最新状态仍待确认

---

## 2. 先解释几个最容易混淆的词

为了避免“每个字都认识，但连起来看不懂”，这里先把最常出现的术语用通俗话解释清楚。

1. `SFT`
   - 就是监督微调。
   - 可以理解成：拿一批“题目 + 参考答案”去教模型。

2. `LoRA`
   - 不是重新训练整个大模型，而是只训练一小部分附加参数。
   - 好处是更快、更省资源，适合反复试数据和超参。

3. `eval loss`
   - 就是模型在评估集上的平均错误程度。
   - 一般来说越低越好，但它不等于“人看起来就一定更好”。

4. `perplexity`
   - 是把 loss 换一种常见形式表达。
   - 也是越低越好，通常和 loss 一起看。

5. `定量评测`
   - 指自动跑测试、看通过率、看 loss、看 ppl。
   - 这是“分数层面”的判断。

6. `定性评测`
   - 指抽固定几条题目，直接看 base 和 adapter 各自写出了什么代码。
   - 这是“人类审稿层面”的判断。

7. `semantic-v4`
   - 是当前最强的一套语义增强训练数据。
   - 它不是模型名，而是一条数据设计路线。

8. `mix75`
   - 是把 `semantic-v4` 和 `codefirst` 混在一起的一个实验版本。
   - 75 的意思是：大约 75% 走 semantic 样本，25% 走 codefirst 样本。

9. `true20-e2`
   - 这不是随便起的名字。
   - `true20` 表示真的跑满 20 个 optimizer steps。
   - `e2` 表示训练时用了 `num_epochs = 2`，否则当前数据规模下实际只会跑到 10 步。

10. `base vs adapter`
    - `base` 是基础模型原始输出。
    - `adapter` 是 LoRA 微调后的输出。
    - 这个对比是为了看训练到底有没有让模型写出更像样的代码。

---

## 3. 这份报告怎么读

这不是论文，也不是 PR 描述，而是一份给研发自己用的“持续更新的实验档案”。

它要回答 7 个问题：

1. 项目到底想做什么？
2. 现在整条研发流水线长什么样？
3. 数据是从哪里来的，怎么一步步变成现在的训练集？
4. 训练算法是什么，loss 到底怎么算？
5. 评测是怎么做的，定量和定性各看什么？
6. 到目前为止做过哪些关键实验，结果如何？
7. 现在真正的阻塞和下一步是什么？

如果你不熟悉项目，建议先看：

1. 第 1 节“先说结论”
2. 第 3 节“项目目标与研发方法”
3. 第 4 节“整条研发流水线”
4. 第 8 节“当前结果”
5. 第 11 节“当前阻塞与真实风险”

---

## 4. 项目目标与研发方法

### 4.1 项目目标

项目目标不是训练一个“泛泛会写 Python”的小模型，而是训练一个在两类任务上都更强的小模型：

1. 量子算法/量子编程任务
2. 通用软件工程任务

这里的“更强”必须满足三个条件：

1. 能用自动测试验证
2. 能复现实验过程
3. 能和历史版本直接比较

### 4.2 当前研发方法

目前采用的是“工程化小步快跑”的方法，不是一次性大训练。

核心思想是：

1. 从可执行任务出发构造监督数据
2. 用 LoRA 做快速 SFT 迭代
3. 每轮实验都强制经过本地回归闸门
4. 远端训练完成后，不只看 loss，还要看固定切片上的真实输出
5. 根据结果继续改数据，而不是盲目加步数或加模型规模

### 4.3 当前主线判断

到今天为止，真正有效的主线是：

**更强语义约束的数据设计**

而不是：

- 更大的训练步数本身
- 更复杂的 RL 名字
- 更花哨的远端调度包装

---

## 5. 整条研发流水线

### 5.1 全流程

当前可运行的流程是：

1. 本地修改数据脚本、训练脚本、评测脚本
2. 本地跑回归评测
3. 回归全绿后，把代码和数据同步到远端
4. 在 Huanxin 环境运行训练或评测
5. 把结果同步或直拉回本地
6. 做定量分析和定性审查
7. 再决定下一轮实验

如果用一张最简流程图来表示，就是：

```text
本地改数据/脚本
  -> 本地回归闸门 `python3 evals/runner/run_eval.py`
  -> `scripts/push_to_s3.sh`
  -> 远端 `scripts/ai2_sync_from_s3.sh`
  -> Huanxin 训练或定性评测
  -> 正常路径：`ai2_push_results_to_s3.sh` -> `pull_from_s3.sh`
  -> 应急路径：`huanxin_fetch_small_file.sh` 直接拉小文件
  -> 本地做定量/定性分析
  -> 决定下一轮数据或评测改动
```

### 5.2 本地闸门

主闸门命令：

```bash
python3 evals/runner/run_eval.py
```

当前状态：

- 总任务数：`25`
- 通过数：`25/25`
- 领域分布：
  - quantum：`12`
  - software：`13`

只要这个闸门没过，就不应该发起新的远端训练。

### 5.3 远端执行环境

远端是 Huanxin train-dev。

现实执行上，目前有两个环境都在用：

1. `ai2`
   - 默认主训练/主评测环境
2. `ai1`
   - 用户明确允许并行使用后，被用来加速混合数据实验与定性评测

注意：

- 工作区默认约束原本倾向只用 `ai2`
- 但当前真实研发过程里，用户已经明确授权 `ai1 + ai2` 并行
- 所以报告记录的必须是“真实发生了什么”，不是静态约束文本本身

### 5.4 代码与结果传输

当前采用三段式传输：

**本地 <-> S3 <-> Huanxin**

核心脚本：

- 本地推送到 S3：
  - `scripts/push_to_s3.sh`
- 远端从 S3 拉取：
  - `scripts/ai2_sync_from_s3.sh`
- 远端结果回推 S3：
  - `scripts/ai2_push_results_to_s3.sh`
- 本地从 S3 拉回：
  - `scripts/pull_from_s3.sh`

### 5.5 小文件应急回收

由于 `Huanxin -> S3` 大文件回传不稳定，后来新增了一个应急路径：

- `scripts/huanxin_fetch_small_file.sh`

它用于直接通过浏览器 Shell 把小文件拉回本地，例如：

- `metrics.json`
- `run_config.json`
- 小型 JSON 报告

这件事很重要，因为它把当前阻塞从：

- “结果完全回不来”

缩小成了：

- “大目录或大文件难以批量同步”

也就是说，分析已经能继续做，不需要等基础设施完美。

---

## 6. 数据体系：从任务到训练集

### 6.1 上游数据源：`evals/tasks`

整个项目最上游的数据源不是网页抓取语料，而是本仓库里的可执行任务。

任务位于：

- `evals/tasks/quantum/*`
- `evals/tasks/software/*`

每个任务通常包含：

- `task.json`
- `tests.py`
- `candidate.py`，或者多文件 candidate

这些任务的价值在于：

1. 有明确任务描述
2. 有标准参考实现
3. 有可执行测试
4. 可以同时作为：
   - 监督数据来源
   - 本地回归评测来源
   - 将来 RL reward 来源

### 6.2 当前评测任务分布

当前一共 `25` 个任务。

量子侧 `12` 个：

- `quantum_bell_pair_construction`
- `quantum_circuit_depth_optimization`
- `quantum_circuit_phase_repair`
- `quantum_gate_alias_normalization`
- `quantum_measurement_bug_repair`
- `quantum_phase_estimation_circuit`
- `quantum_qaoa_maxcut`
- `quantum_qft_phase_pattern`
- `quantum_stabilizer_tableau_update_repair`
- `quantum_superdense_coding`
- `quantum_teleportation_corrections`
- `quantum_vqe_energy_minimization`

软件侧 `13` 个：

- `software_config_merge`
- `software_docstring_contract`
- `software_duplicate_logic_refactor`
- `software_multifile_patch_conflict_repair`
- `software_off_by_one_bugfix`
- `software_parser_regression_tests`
- `software_patch_application_conflict_resolver`
- `software_retry_decorator`
- `software_session_event_log`
- `software_session_window_summary`
- `software_tree_serialization`
- `software_workspace_patch_bundle_repair`
- `software_workspace_runner_smoke`

### 6.3 种子数据：`data/seed/splits`

这是更早期的小规模数据谱系起点。

规模：

- train：`18`
- val：`2`
- test：`3`
- 合计：`23`

它现在不是主训练集，但仍然有两个作用：

1. 提供数据谱系起点
2. 作为早期小规模验证参考

### 6.4 模板扩增数据：`template-v1` / `template-v2`

生成脚本：

- `data/generate/template_datagen.py`

做法很直接：

1. 遍历单文件可执行任务
2. 读取参考正确解
3. 先跑测试确认参考解确实过
4. 为同一任务生成多种 prompt 表述
5. 对答案做轻微格式变体
6. 输出 chat-SFT 格式样本

已知规模：

- `template-v1.jsonl`：`115`
- `template-v2.jsonl`：`460`

这一步的作用是：

- 不靠模型自举伪标签
- 直接把“真实可执行任务”变成监督样本

### 6.5 当前主训练数据族：`fast-*`

当前真正进入训练主循环的是 `fast-*` 这条线，特别是 `fast-mini` 及其派生版本。

#### 5.5.1 `fast-mini`

规模：

- train：`160`
- eval：`32`

训练集领域分布：

- quantum：`90`
- software：`70`

评估集领域分布：

- quantum：`15`
- software：`17`

它是当前主线数据的基础底座。

#### 5.5.2 `fast-mini-codefirst`

构建脚本：

- `scripts/build_codefirst_fast_mini.py`

做的事情很简单但很关键：

- 去掉答案最前面的 `# Solution`、`# Implementation` 这类 banner
- 让 assistant 输出更像“直接交代码”

规模不变：

- train：`160`
- eval：`32`

#### 5.5.3 `fast-mini-interface-prefix`

构建脚本：

- `scripts/build_interface_augmented_fast_mini.py --variant prefix`

新增约束：

- 必需函数/类签名
- 只返回 Python 代码

核心目的不是增加知识，而是让模型更服从接口合同。

规模：

- train：`160`
- eval：`32`

#### 5.5.4 `fast-mini-interface-prefix-semantic`

构建脚本同上，但使用：

- `--variant prefix-semantic`

这一层进一步加了“语义合同”提示，尤其针对容易只看函数名就乱写的任务。

例如：

- `software_session_event_log`
- `software_session_window_summary`
- `quantum_measurement_bug_repair`
- `quantum_stabilizer_tableau_update_repair`

它加入的不是更多废话，而是更窄、更明确的任务语义。

规模：

- train：`160`
- eval：`32`

#### 5.5.5 `fast-mini-interface-prefix-semantic-v4`

这是当前最重要的数据集。

规模：

- train：`160`
- eval：`32`

当前最佳结果就来自这一版数据。

#### 5.5.6 `fast-mini-codefirst-semantic-mix75`

构建脚本：

- `scripts/build_mixed_fast_mini.py`

输入：

- `data/generated/fast-mini-codefirst`
- `data/generated/fast-mini-interface-prefix-semantic-v4`

构建方式：

1. 两边按 `example_id` 对齐
2. 对每个样本做稳定哈希
3. 按比例选择用 codefirst 版本还是 semantic 版本

当前配置：

- `semantic_ratio = 0.75`
- `seed_tag = mix-v1`

实际抽样结果：

- train：`160`
  - semantic：`121`
  - codefirst：`39`
- eval：`32`
  - semantic：`23`
  - codefirst：`9`

这条线已经完成一次真实训练，但暂时没有超过纯 `semantic-v4`。

#### 5.5.7 `fast-mini-codefirst-semantic-mix90`

这一版数据已经生成，但报告周期内还没有看到对应训练结果。

配置：

- `semantic_ratio = 0.9`

实际抽样结果：

- train：`160`
  - semantic：`142`
  - codefirst：`18`
- eval：`32`
  - semantic：`27`
  - codefirst：`5`

它的意义是：

- 为“更保守地注入 codefirst 信号”做准备
- 便于下一轮回答：是不是 `mix75` 太激进，而不是混合方向本身错误

### 6.6 数据设计到目前为止的判断

当前数据演化路径可以概括为：

`fast-mini`  
→ `codefirst`  
→ `interface-prefix`  
→ `interface-prefix-semantic-v4`

这条路径本质上是在逐步加三种监督信号：

1. 代码输出更干净
2. 接口更服从
3. 语义合同更明确

到目前为止，最有效的是第 3 类，也就是 **语义合同约束**。

---

## 7. 训练算法与损失函数

### 7.1 当前主训练算法：LoRA SFT

训练脚本：

- `training/qwen_sft_peft.py`

当前主线不是全参数微调，而是：

- LoRA / PEFT
- 因果语言模型训练
- chat-SFT 输入格式

选择 LoRA 的原因很实际：

1. 小模型也要快速迭代
2. 数据实验远比大规模训练更值得先做
3. LoRA 更适合做多轮 ablation

### 7.2 SFT 输入与标签

训练样本格式是 chat JSONL：

- system
- user
- assistant

训练过程：

1. 读取 JSONL
2. 用 tokenizer 的 chat template 渲染成文本
3. 截断到 `max_length`
4. padding
5. `labels = input_ids.clone()`
6. 把 padding 位置打成 `-100`
7. 如果启用 `--train-on-completions-only`，再把 prompt 部分也 mask 掉

对应到当前代码，可以把它理解成三层：

1. `ChatSftDataset`
   - 负责把 JSONL 样本变成 chat 文本和 token
2. `PaddingCollator`
   - 负责 padding，并把不该参与 loss 的位置打成 `-100`
3. 训练循环里的 `model(**batch).loss`
   - 真正向后传播的就是 Hugging Face causal LM 标准 loss

### 7.3 SFT loss

当前主线 SFT 的 loss 没有花活，就是标准 causal LM token-level cross entropy。

如果写成更接近公式的样子：

```text
L_sft = CE_theta(input_ids, labels)
```

其中：

- padding token 不参与损失
- 如果启用 completions-only，prompt token 也不参与损失

用更通俗的话说：

- 这条主线不是在学“整段提示词”，而是在学“应该生成出来的回答部分”
- `--train-on-completions-only` 的作用，就是进一步强调“只为答案部分负责”

### 7.4 当前 LoRA 配置

默认值：

- `lora_rank = 16`
- `lora_alpha = 32`
- `lora_dropout = 0.05`
- `target_modules = [q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj]`

这不是只改 attention 的最小 LoRA，而是 attention + MLP 一起改。

### 7.5 优化器与学习率调度

当前主线：

- 优化器：`AdamW`
- 调度器：`CosineAnnealingLR`
- 梯度裁剪：`clip_grad_norm_ = 1.0`

### 7.6 训练安全保护

当前 trainer 里已经补上了两个很重要的安全保护：

1. 输出目录复用保护
   - 如果 `run_config.json` 里的训练签名和当前不一致，就拒绝复用旧目录
2. 真实步数可追踪
   - `optimizer_steps_per_epoch`
   - `max_available_steps`
   - `requested_max_steps`
   - `completed_steps`

这一点很关键，因为项目曾经踩过一个坑：

- 命令行写了 `20 steps`
- 实际只跑了 `10`

这个坑后来是通过上述字段修正掉的。

### 7.7 当前远端主训练配置

当前被验证有效的配置大致是：

- `torchrun --nproc_per_node=8`
- `--max-length 512`
- `--per-device-batch-size 1`
- `--gradient-accumulation-steps 2`
- `--num-epochs 2`
- `--max-steps 20`
- `--eval-steps 10`
- `--device npu`

### 7.8 RL 原型算法：名义 GRPO，实际是加权 NLL 原型

RL 脚本：

- `training/grpo_trainer.py`

它的名义目标是：

- 对同一个 prompt 采样多条解
- 用测试结果给 reward
- 根据组内相对好坏更新模型

当前实际流程：

1. 从 `evals/tasks` 随机采样一个任务
2. 构造 prompt
3. 采样 `group_size` 个候选代码
4. 用测试器执行每个候选
5. reward：
   - pass：`1.0`
   - fail：`0.0`
6. 在组内做标准化：

```python
mean_reward = rewards.mean()
std_reward = rewards.std() + 1e-8
advantages = (rewards - mean_reward) / std_reward
```

7. 只取 reward 最好的前一半样本
8. 对这些样本重算标准 LM loss，再乘以 `-advantage`

### 7.9 RL 原型的真实 loss

虽然脚本里定义了一个 `grpo_loss()`：

```python
ratio = exp(log_probs - old_log_probs.detach())
pg_loss = -(ratio * advantages.detach()).mean()
kl = (old_log_probs.detach() - log_probs).mean()
loss = pg_loss + kl_coeff * kl
```

但要非常明确：

**当前主训练循环并没有真正调用这个 `grpo_loss()`。**

当前真正执行的更接近：

```text
L_rl_current = (1 / top_k) * Σ_i [ -A_i * CE_theta(prompt + code_i) ]
```

其中：

- `A_i` 是组内标准化后的 advantage
- `CE_theta(...)` 是普通 token-level cross entropy
- 只对 top half 候选求和

所以当前 RL 原型更准确的说法是：

**带组内相对优势的加权 NLL / on-policy weighted SFT**

而不是严格意义上的 PPO/GRPO 完整实现。

### 7.10 RL 原型当前的价值与缺口

价值：

1. reward 来自真实测试通过率
2. 数据源和评测体系天然统一
3. 已经能作为未来 test-driven RL 的代码骨架

缺口：

1. reward 太稀疏
2. old policy / ratio / KL 没有进入主训练闭环
3. rollout 与 logging 不够稳定
4. 还没有形成连续的远端 RL 实验记录

阶段性结论：

- RL 代码现在证明了“用测试结果当 reward”这件事在工程上能接进去
- 但它还没有跑出比当前 SFT 主线更强的真实结果
- 所以现在 RL 是储备路线，不是当前主战场

---

## 8. 评测体系

这部分最容易被误解，所以先把一句话说死：

- 定量评测回答的是“统计上有没有变好”
- 定性评测回答的是“写出来的东西到底像不像可交付代码”

当前项目的决策必须同时看两者，不能只看 loss，也不能只凭肉眼抽样印象。

### 8.1 定量评测：本地可执行回归

命令：

```bash
python3 evals/runner/run_eval.py
```

特点：

1. CPU 就能跑
2. 每个任务都走真实测试器
3. 单文件和多文件任务都支持
4. 可以按 domain 和 category 汇总

### 8.2 定性评测：固定 5 条样本切片

切片文件：

- `reports/base_vs_adapter_eval_slice_interface_prefix.json`

当前固定切片覆盖 5 个样本，重点不是“大而全”，而是高信号：

1. `software_session_window_summary`（两个 prompt 变体）
2. `software_session_event_log`
3. `quantum_measurement_bug_repair`
4. `quantum_stabilizer_tableau_update_repair`

它主要测试三类能力：

1. 接口服从性
   - 函数名、签名、代码-only 输出
2. 语义合同理解
   - 有没有抓住字段名、状态迁移、量子语义
3. 明显测试风险
   - 是否存在明显错字段、错映射、错规则

### 8.3 定性评测脚本

脚本：

- `scripts/run_base_vs_adapter_eval.py`

当前行为：

1. 加载固定切片
2. 先跑 base model
3. 再跑 base + adapter
4. 输出 side-by-side JSON

最近针对它做过两类改进：

1. 性能/监控改进
   - 不再每个样本重复加载模型
   - 打印逐样本进度
2. 日志去噪改进
   - 清理 deterministic generation 场景下的无效 sampling warning

### 8.4 定性结果快速摘要

新补了一个本地辅助脚本：

- `scripts/summarize_base_vs_adapter_report.py`

用途：

- 报告一旦回到本地，就快速提取启发式信号
- 例如：
  - 是否像代码开头
  - 是否带 code fence
  - 是否包含要求的函数名
  - 是否出现明显字段漂移（如该用 `ts` 却写成 `timestamp`）

它不会替代人工审查，但能让定性比较更快。

截至 2026-03-27 中午，这个摘要器已经进一步补强到可以直接输出：

1. `base` 和 `adapter` 的总分对比
2. `avg_score_delta`
3. 每条样本的 `winner`
4. 按 `software` / `quantum` 分领域汇总
5. `parse_error`、`first_nonempty_line`、`code_fence_closed` 这类更接近“为什么坏掉”的线索

也就是说，它已经不只是“像不像代码”的粗筛，而是能更快指出：

- 哪边整体更强
- 强弱主要发生在哪个领域
- 每条样本具体是因为语法截断、字段漂移，还是接口合同不对

### 8.5 目前从历史定性评测得到的经验

历史 smoke run 的共同结论是：

1. adapter 相比 base，最稳定的收益是：
   - 更像代码
   - 更少前置解释
   - 更容易贴近指定函数签名
2. 但 adapter 早期的主要问题是：
   - 表面格式更像对
   - 实际语义仍经常抓偏

也就是说，过去的主要提升是：

**“更像正确答案”**

而不是：

**“真正更懂任务语义”**

这就是为什么现在必须跑 `semantic-v4` 和 `mix75` 的同切片定性评测。

---

## 9. 当前结果与实验结论

### 9.1 当前最佳结果：`semantic-v4 true20-e2`

输出目录：

- `outputs/interface-prefix-semantic-v4-8npu-true20-e2-20260326T1627CST`

核心指标：

- `train_examples = 160`
- `eval_examples = 32`
- `world_size = 8`
- `optimizer_steps_per_epoch = 10`
- `max_available_steps = 20`
- `requested_max_steps = 20`
- `completed_steps = 20`
- `final_eval.loss = 0.6986174695193768`
- `final_eval.perplexity = 2.0109705566192857`

对比历史基线：

- 相比 `semantic_v4_8npu_20step`
  - `delta_eval_loss = -0.137220753357`
- 相比 `semantic_v4_smoke20`
  - `delta_eval_loss = -0.138441754505`
- 相比 `codefirst_mini`
  - `delta_eval_loss = -0.180158812553`

当前结论：

- 这是目前最好的定量结果
- 而且它是一个**真实跑满 20 optimizer steps** 的结果

### 9.2 新混合实验：`mix75`

输出目录：

- `outputs/codefirst-semantic-mix75-8npu-true20-e2-20260326T2118CST`

核心指标：

- `train_examples = 160`
- `eval_examples = 32`
- `optimizer_steps_per_epoch = 10`
- `max_available_steps = 20`
- `requested_max_steps = 20`
- `completed_steps = 20`
- `final_eval.loss = 0.735347468405962`
- `final_eval.perplexity = 2.086206757517806`

与当前最佳 semantic run 相比：

- `delta_eval_loss = +0.036729998886585236`
- `delta_eval_perplexity = +0.07523620089852034`

当前结论：

1. `mix75` 不是没跑起来，而是已经跑完了
2. 但第一轮结果没有超过纯 `semantic-v4`
3. 这说明在当前小数据规模下，语义约束仍然比 codefirst 混合更重要

### 9.3 现在还没回答完的问题

虽然 `mix75` 定量上输了，但还有一个问题没有回答完：

**它会不会在代码输出风格、接口服从、少废话这些维度上更好？**

这就是为什么还需要看当前正在跑的定性评测。

### 9.4 当前仍在运行的远端评测

截至本次报告更新时间（2026-03-27 中午），本地还没有拿到这两份定性报告的 JSON 文件。

目前对两条远端任务的已知状态要分开看：

1. `ai2`：`semantic-v4` 定性评测
   - 目标报告：
     - `reports/base_vs_adapter_outputs_interface_prefix_semantic_v4_true20_e2.json`
   - 旧任务已知远端 python child：
     - `pid 128866`（旧任务，现已失效）
   - 新 rerun 当前远端 python child：
     - `pid 132382`
   - 当前状态：
     - 截至 2026-03-27 中午最新轮询，新的 rerun 远端进程 `132382` 仍存活
     - 最新可见日志已经推进到：
       - `[adapter] 1/5 template_session_window_summary_10_ab155b35`
     - 说明 rerun 至少已经跑完整个 base 阶段，并进入 adapter 阶段，但报告仍未落盘
     - 由于旧任务最终没有留下可稳定回收的报告文件，2026-03-27 已经重新发起一条新的 rerun：
       - 输出文件：`reports/base_vs_adapter_outputs_interface_prefix_semantic_v4_true20_e2_rerun_20260327.json`
       - 已确认新的远端 python 进程存在
       - 且不是卡在启动，而是在慢速 CPU 生成阶段

2. `ai1`：`mix75` 定性评测
   - 目标报告：
     - `reports/base_vs_adapter_outputs_codefirst_semantic_mix75_true20_e2.json`
   - 启动时 launcher pid：
     - `5757`
   - 当前状态：
     - 已经成功启动过，并确认进入实际生成
     - 但截至 2026-03-27 中午，这一轮没有拿到 fresh readback，最终 JSON 仍未回到本地
     - 当前更准确的说法是：
       - `ai1` 是否仍在继续跑，暂时没有新的可靠远端回读证据
       - 已知最大摩擦仍然是本地浏览器控制面偶发失稳，而不是训练逻辑本身

这两个任务的目的都是：

- 用同一个固定切片判断“输出是不是更像正确代码”
- 而不是继续只看 loss

---

## 10. 已发生的研发过程时间线

### 10.1 2026-03-25：发现远端 shell 读取不可靠

当时做了最小只读探测，结果失败：

- `./scripts/ai2_shell.sh ...`
- 返回：
  - `Detected stale Huanxin shell output: expected run marker ... was not observed.`

所以那一轮没有盲目发训练，先停下来修控制面可靠性。

### 10.2 2026-03-26：重新打通 ai2，并启动 semantic-v4 训练

当天先重新确认：

- 本地回归：`25/25 passed`
- trainer 语法检查：通过
- ai2 shell fresh marker：通过

然后在 `ai2` 上发起 `semantic-v4 true20` 训练。

### 10.3 同日：发现“20 steps”并不一定真是 20

后来检查旧 run 时发现：

- 命令写的是 `max_steps = 20`
- 但实际只跑到了 `10`

原因是：

- 当前数据规模 `160`
- `world_size = 8`
- `batch_size = 1`
- `grad_accum = 2`
- 所以每个 epoch 实际只有 `10` 个 optimizer steps

结论：

- 如果想跑真 `20 steps`
- 必须用 `--num-epochs 2`

### 10.4 同日：修正后重新跑 `semantic-v4 true20-e2`

修正后在 `ai2` 上重新发起：

- `semantic-v4-true20-e2`

这次最终完成并成为当前最好结果。

### 10.5 同日：发现 `Huanxin -> S3` 上传是系统性问题

一开始以为只是 `ai2` 或 adapter 文件的问题，后来在 `ai1` 上复现：

- 连一个合成的 `2 MB` 文件都能触发：
  - `S3 PutObject 500`
  - `XML syntax error ... <hr> closed by </body>`

因此更可信的结论是：

- 故障域在共享 HTTP/代理链路
- 不是某一个环境、某一类文件、某一个 adapter 目录的特殊问题

### 10.6 同日：补上小文件回收路径

为了不让分析完全停住，新增了：

- `scripts/huanxin_fetch_small_file.sh`

并成功把 `ai1 mix75` 的：

- `metrics.json`
- `run_config.json`

直接拉回本地。

### 10.7 同日：新增并跑通 `mix75`

先生成了：

- `data/generated/fast-mini-codefirst-semantic-mix75`

随后在 `ai1` 上完成真实训练：

- `outputs/codefirst-semantic-mix75-8npu-true20-e2-20260326T2118CST`

结论：

- 路线可跑通
- 但定量暂时不如纯 `semantic-v4`

### 10.8 同日夜间：双环境并行定性评测

用户明确要求加速后，当前同时做两件事：

1. `ai2` 跑 `semantic-v4` 的固定切片定性评测
2. `ai1` 跑 `mix75` 的同切片定性评测

这样下一轮决策就不需要等两轮串行评测。

### 10.9 2026-03-27：补齐双环境 wrapper，并在 ai2 上重跑丢失的定性评测

为了减少“能做实验，但控制面拖慢推进”的摩擦，本轮又做了两类工程修复：

1. 补齐双环境 shell 入口：
   - `scripts/huanxin_shell.sh <ai1|ai2> "<cmd>"`
   - `scripts/ai1_shell.sh`
   - `scripts/ai2_shell.sh` 现在只做薄转发
2. 修复本地浏览器 profile copy 的脆弱点：
   - `browser-automation/huanxin_profile.js` 在临时 profile 清理遇到 `ENOTEMPTY/EBUSY/EPERM` 时，会自动退到唯一临时 profile
3. 把 `scripts/huanxin_fetch_small_file.sh` 切到新的通用 wrapper，避免硬绑 `--require-daemon`
4. 补强 `scripts/summarize_base_vs_adapter_report.py`
   - 现在可以输出 `avg_score_delta`
   - 可以给每条样本打 `winner`
   - 可以按 `software` / `quantum` 分开看差异
5. 修控制面的两个小瓶颈：
   - daemon HTTP 超时现在会跟 `waitMs` 对齐，而不是固定 120 秒
   - daemon 启动失败时会更快回退到 standalone，而不是空等满整轮启动超时
6. 新增本地 watcher：
   - `scripts/watch_base_vs_adapter_report.sh`
   - 用来轮询远端 qualitative 报告，一旦落盘就自动抓回本地并跑摘要

这轮新确认的现实是：

- `ai2` 旧的 `semantic-v4` 定性评测进程已经死掉
- 旧报告文件在当前可访问工作区里不存在
- 因此不是继续等待，而是直接在 `ai2` 发起新的 rerun

新的 `ai2` rerun 已确认进入实际生成：

- 输出文件：
  - `reports/base_vs_adapter_outputs_interface_prefix_semantic_v4_true20_e2_rerun_20260327.json`
- 已确认远端进程：
  - `132382 python3 scripts/run_base_vs_adapter_eval.py ...`
- 已确认日志：
  - `loading base model from models/Qwen2.5-1.5B-Instruct for 5 examples on cpu`
  - `[base] 1/5 template_session_window_summary_10_ab155b35`

---

## 11. 当前真正的判断

### 11.1 已经可以明确说的事

1. **当前最强主线是 `semantic-v4`。**
2. **`mix75` 第一轮没有在定量上打赢。**
3. **项目真正有效的推动力是数据设计，不是更复杂的训练名字。**
4. **RL 现在还是原型，不是主战场。**
5. **远端大文件回传不稳，但结果分析已经有替代路径。**

### 11.2 还不能提前下结论的事

1. `semantic-v4` 的更低 loss 是否真的意味着更好的可读代码输出
2. `mix75` 是否在代码风格/接口服从上有可保留优势
3. 更保守的混合比例（例如 `mix90`）是否比 `mix75` 更合理
4. RL 什么时候才会真正优于继续做高质量监督数据工程

---

## 12. 当前阻塞与真实风险

### 12.1 基础设施阻塞

主要阻塞不是训练，而是结果回传：

- `Huanxin -> S3` 大文件/目录写回不稳定

直接影响：

- adapter 整目录难以稳定回收
- 大报告目录难以批量同步

已缓解：

- 小型关键产物可用 `scripts/huanxin_fetch_small_file.sh` 回收

### 12.2 控制面风险

浏览器 Shell 本身也有过这些问题：

- stdout marker 丢失
- xterm 输出换行导致 job marker 解析脆弱
- daemon 被前序只读命令卡住
- `ai1` daemon 重启时，本地临时 profile 清理偶发 `ENOTEMPTY`

已做过的修正包括：

- `ai2_job.sh` marker 解析增强
- `huanxin_shell_exec.js` wrapper marker 清理修正
- `ai1` daemon 卡住后重启恢复 `/exec`
- 新增通用双环境 wrapper：
  - `scripts/huanxin_shell.sh <ai1|ai2> "<cmd>"`
  - `scripts/ai1_shell.sh`
  - `scripts/ai2_shell.sh` 现在只是薄转发
- `browser-automation/huanxin_profile.js` 现在在 profile copy 清理遇到 `ENOTEMPTY/EBUSY/EPERM` 时，会自动退到唯一临时 profile，而不是直接让 daemon 启动失败
- `scripts/huanxin_fetch_small_file.sh` 现在改为复用通用 wrapper：
  - 优先尝试 daemon
  - daemon 不可用时自动退回 standalone

### 12.3 研究风险

最大的研究风险不是“没有实验可做”，而是：

- 容易把“格式看起来更好”误判成“语义真的更正确”

所以当前一定要坚持：

1. 先看定量
2. 再看固定切片定性
3. 不因为一轮混合数据看起来更像代码，就立刻替代当前最优主线

---

## 13. 下一步计划

### 13.1 第一优先级：收完当前双定性评测

最先要做的是把当前两个远端定性评测收完：

1. `ai2` 的 `semantic-v4`
2. `ai1` 的 `mix75`

一旦 JSON 报告落地，就要立刻：

1. 拉回本地
2. 用 `scripts/summarize_base_vs_adapter_report.py` 做快速摘要
3. 再做人读的结论判断

### 13.2 第二优先级：根据定性结果决定混合线去留

如果 `mix75` 定性也不占优：

- 这条配方优先级就应该明显下降

如果 `mix75` 在 code-only 或接口服从上明显更好：

- 才值得继续探索：
  - `mix90`
  - 更窄比例
  - 按任务类别选择性混合

截至当前，若必须在没有新定性 JSON 的情况下先做一个“最小下一实验”判断，那么更合理的不是重跑旧 `mix75`，而是：

- 保持 `semantic-v4` 为默认主线
- 把 `mix90` 视为最小信息增益实验候选

原因是：

1. `semantic-v4` 已经是当前明确最优定量结果
2. `mix75` 已经给出了“混得太多可能伤主线”的负面证据
3. `mix90` 刚好能验证：
   - 问题到底是“混合路线本身不行”
   - 还是“`mix75` 里 codefirst 比例太高”

### 13.3 第三优先级：继续拆解基础设施问题

继续做更小的最小复现实验，定位：

- 为什么 `Huanxin -> S3` 会返回 500 + 异常 HTML/XML

目标不是一次性修完所有传输，而是进一步稳定：

- 小文件结果回收
- 必要元数据回收
- 定性报告回收

---

## 14. 关键文件索引

### 14.1 训练与算法

- SFT trainer：
  - `training/qwen_sft_peft.py`
- RL prototype：
  - `training/grpo_trainer.py`

### 14.2 数据生成

- 模板数据生成：
  - `data/generate/template_datagen.py`
- codefirst 派生：
  - `scripts/build_codefirst_fast_mini.py`
- interface / semantic 派生：
  - `scripts/build_interface_augmented_fast_mini.py`
- 混合数据：
  - `scripts/build_mixed_fast_mini.py`

### 14.3 评测

- 本地回归：
  - `evals/runner/run_eval.py`
- 定性切片：
  - `reports/base_vs_adapter_eval_slice_interface_prefix.json`
- 定性评测：
  - `scripts/run_base_vs_adapter_eval.py`
- 定性报告快速摘要：
  - `scripts/summarize_base_vs_adapter_report.py`

### 14.4 传输与远端控制

- 本地推送：
  - `scripts/push_to_s3.sh`
- 本地拉回：
  - `scripts/pull_from_s3.sh`
- 远端同步：
  - `scripts/ai2_sync_from_s3.sh`
- 远端结果回推：
  - `scripts/ai2_push_results_to_s3.sh`
- 小文件直拉：
  - `scripts/huanxin_fetch_small_file.sh`
- ai2 shell：
  - `scripts/ai2_shell.sh`

### 14.5 当前最重要的结果文件

- 当前最佳 semantic run：
  - `outputs/interface-prefix-semantic-v4-8npu-true20-e2-20260326T1627CST/metrics.json`
- `mix75` 首轮真实结果：
  - `outputs/codefirst-semantic-mix75-8npu-true20-e2-20260326T2118CST/metrics.json`
- `mix75` 本地快照：
  - `artifacts/remote-run-snapshots/ai1-codefirst-semantic-mix75-8npu-true20-e2-20260326T2118CST.json`

---

## 15. 最终总结

到这一步，项目已经不是“想法验证阶段”，而是一个真实运行中的小模型研发系统：

1. 数据能构造
2. 本地能评测
3. 远端能训练
4. 结果能分析
5. 失败能复盘

当前最强路线仍然是：

**高质量任务派生监督数据 + LoRA SFT + 可执行评测**

当前最重要的下一步不是继续盲目训练，而是把正在跑的两条定性评测收完，确认：

**`semantic-v4` 是否不仅分数更好，而且输出也更好；`mix75` 是否虽然分数差一些，但在代码风格或接口服从上还有保留价值。**
