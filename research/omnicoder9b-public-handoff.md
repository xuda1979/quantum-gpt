# OmniCoder-9B Public Handoff

## 目的

这份说明用于把下一轮 `OmniCoder-9B` 微调从“口头目标”变成“可执行交接”。

它回答的是一个很具体的问题：

- 如果下一轮基座改成 `OmniCoder-9B`，本地应该先做什么，远端应该怎么接，训练和归档要记录什么。

## 当前目标模型

- Hugging Face model id: `Tesslate/OmniCoder-9B`
- 建议远端模型目录：`/root/root/work/quantum-gpt/models/OmniCoder-9B`
- 当前数据主线：`data/generated/fast-mini-interface-prefix-semantic-v4`

## 当前已确认的真实阻塞

截至 `2026-03-27` 的本地探测，阻塞已经不是“还没下载权重”这么简单，而是：

1. `OmniCoder-9B` 暴露的是：
   - `model_type = qwen3_5`
   - `architectures = [Qwen3_5ForConditionalGeneration]`
2. 当前训练器 `training/qwen_sft_peft.py` 走的是：
   - `AutoTokenizer`
   - `AutoModelForCausalLM`
3. 当前 smoke 脚本 `training/huanxin_cpu_smoke.py` 也是同一条纯文本路径

所以当前的真实结论是：

- `OmniCoder-9B` 不是“可以直接按 Qwen2.5 文本模型那样微调，只差下载”
- 而是“需要更高版本的 Transformers/runtime，加上一条 processor-aware 的训练/加载路径”

补充一个已经做过的实测：

- 在隔离虚拟环境里安装了公开发布版 `transformers 4.57.6`
- 依然不能通过 `AutoConfig.from_pretrained('Tesslate/OmniCoder-9B')` 识别 `qwen3_5`
- 但仓库文件侧已经确认存在：
  - `processor_config.json`
  - `preprocessor_config.json`
  - `chat_template.jinja`

所以当前不是“随便升到一个更新 release 就够了”，而是很可能需要：

1. 更靠前的上游 runtime 支持
2. 仓库内 processor-aware 文本子路径

为避免后面拿到本地 snapshot 后再误判，`training/verify_qwen_snapshot.py` 现在也已经升级：

- 对纯文本 Qwen 路径，仍按 `config + tokenizer + weights` 验证
- 对 `ConditionalGeneration / vision_config / image_token_id` 这类路径，会额外要求：
  - processor/preprocessor config
  - chat template 证据

也因此，通用的 remote bootstrap 命令单在这个模型上暂时被禁用，避免误导性地让远端直接跑到 `AutoTokenizer` / `AutoModelForCausalLM` 再失败。

## 为什么这一轮切到 OmniCoder-9B

当前仓库已经证明：

- 数据管线可跑
- LoRA SFT 可跑
- 回归评测可跑
- 结果归档可跑

因此下一轮的高价值变量，不再只是继续在 `Qwen2.5-1.5B-Instruct` 上反复试，而是把同一条可复现流程迁移到更强的 coding base model 上，观察：

1. 同样的数据设计是否能在更强基座上放大收益
2. 定性输出是否更接近真正的 coding agent
3. 训练和评测链路在 9B 量级是否仍然稳定

## 先做什么

### 1. 本地先做 preflight，不直接下载

```bash
python3 training/acquire_public_qwen_snapshot.py \
  --target omnicoder9b \
  --dry-run \
  --render-remote-commands
```

这一步会生成：

- `artifacts/model-source-audit-omnicoder9b.json`
- `artifacts/omnicoder9b-local-snapshot-preflight.json`

它只冻结“目标模型是谁、准备放到哪里、后续该怎么交接”，不假装已经拿到本地权重。

注意：

- 对 `OmniCoder-9B` 来说，`--render-remote-commands` 当前只会返回 warning
- 不会再生成那种假设“纯文本 CausalLM 直接可跑”的通用命令单

### 2. 如果 preflight 没问题，再决定是否真实下载

```bash
python3 training/acquire_public_qwen_snapshot.py --target omnicoder9b
```

真实下载成功后，才会写：

- `artifacts/omnicoder9b-local-snapshot-handoff.json`

## 建议训练路径

### 先跑 smoke

在真正 smoke 之前，必须先补两件事：

1. 让远端/本地 `transformers` 运行时支持 `qwen3_5`
2. 给训练链路补上 processor-aware 路径

在这两件事补完之前，下面这类命令只应被视为“未来目标格式”，不应现在直接下发：

```bash
cd /root/root/work/quantum-gpt
python3 training/qwen_sft_peft.py \
  --model-name models/OmniCoder-9B \
  --train-file data/generated/fast-mini-interface-prefix-semantic-v4/train.jsonl \
  --eval-file data/generated/fast-mini-interface-prefix-semantic-v4/eval.jsonl \
  --output-dir outputs/interface-prefix-omnicoder9b-smoke1 \
  --device npu \
  --max-length 256 \
  --max-steps 1 \
  --num-epochs 1 \
  --per-device-batch-size 1 \
  --gradient-accumulation-steps 1 \
  --eval-steps 1
```

### smoke 通过后再跑正式轮次

建议先沿用当前最稳定的数据和节奏：

- 数据：`semantic-v4`
- 训练方法：`LoRA SFT`
- 步数：`true20-e2`

一个建议命名模板：

```text
outputs/interface-prefix-omnicoder9b-<npuN>-true20-e2-<timestamp>
```

## 这一轮必须额外记录的东西

和 1.5B 基线相比，`OmniCoder-9B` 下一轮要额外写清楚：

1. 基座来源
   - `Tesslate/OmniCoder-9B`
2. 基座上游关系
   - 它是建立在 Qwen 3.5 9B 路线上的 coding model
3. 真实训练资源
   - 用了几张 NPU
   - 每卡 batch
   - gradient accumulation
   - max length
4. smoke 是否通过
   - 失败是加载失败、显存失败，还是训练逻辑失败
5. 正式训练完成后，必须执行归档

```bash
python3 scripts/archive_model_run.py <output-dir> \
  --label omnicoder9b-semantic-v4-true20-e2 \
  --eval-command "python3 evals/runner/run_eval.py"
```

如果还做了固定切片定性评测，要把定性报告一起归档进去。

## 当前状态

截至 `2026-03-27`：

- `OmniCoder-9B` 还没有被证明已经存在于当前本地 `models/` 目录
- 也还没有被证明已经存在于 `ai2` 的远端 `models/` 目录
- preflight/交接/归档链路已经准备好
- 但当前运行时已经被证明确实不兼容 `qwen3_5` 这条模型路径

这意味着：

- 当前不只是“模型本体还未正式落地”
- 当前还存在“训练运行时路径不兼容”的明确工程阻塞

下一步最小动作不再是直接发起远端训练，而是：

1. 先升级并验证 `qwen3_5` 运行时
2. 再实现 processor-aware smoke / SFT 路径
3. 最后才是下载模型并发起真实 smoke
