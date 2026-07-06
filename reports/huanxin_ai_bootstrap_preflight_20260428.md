# Huanxin AI bootstrap preflight - 2026-04-28

## Target

All new training targets the Huanxin `AI` train-dev environment:

```text
https://aihuanxin.cn/kunlun/kl-web?poolId=6&projectId=21b4208dde424e96b159362ef49c9c96#/train-dev/environment/dl-9a5a098accce31c28cf4c6ca23391341?name=AI
```

Remote project root: `/root/software/quantum-gpt`

## Completed

The AI shell login/session path was repaired enough to run commands through the
daemon transport. An initial NPU probe showed no running processes on NPU 0-7.

The remote project root was missing, so a focused local bootstrap payload was
created and uploaded through the existing S3 relay:

```text
/tmp/quantum-gpt-ai-bootstrap-20260428T033345Z.tar.gz
```

Payload size: about 957 KiB.

The payload was downloaded in the AI shell with `curl`, extracted into
`/root/software/quantum-gpt`, and verified there.

Verified present on AI after extraction:

- `training/qwen_sft_peft.py`
- `data/generated/omnicoder-quantum-generalization-holdout-v1/train.jsonl`
- `data/generated/omnicoder-quantum-generalization-holdout-v1/eval.jsonl`
- `artifacts/quantum-rag/quantum-docs-only-index.pkl.gz`

## Current Blocker

Training was not launched because the required new base model is still missing:

```text
models/Qwen3.6-27B/config.json = false
```

The next remote action is to place or acquire `Qwen/Qwen3.6-27B` at:

```text
/root/software/quantum-gpt/models/Qwen3.6-27B
```

After that, rerun the dependency/model preflight and only then start:

```bash
bash scripts/ai_launch_quantum_sft.sh
```

Secondary reliability note: the Huanxin browser daemon repeatedly needed local
auth repair between commands. The successful bootstrap proves AI shell control is
usable, but long training launch commands should be preceded by a fresh short
`ai_shell` preflight.
