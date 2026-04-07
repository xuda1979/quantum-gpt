# TurboQuant Runbook

This file documents the current TurboQuant-style KV-cache path implemented in this repository for local and `ai2` inference.

Scope:

- pure PyTorch runtime in `training/turboquant.py`
- optional integration in `scripts/serve_openai_chat_adapter.py`
- optional integration in `scripts/run_hf_pass1_eval.py`

Status:

- local unit tests passed on `2026-04-01`
- local `transformers` generate smoke with `TurboQuantCache` passed on `2026-04-01`
- ai2 verification commands are listed below for the same day

## Source Files

- [`training/turboquant.py`](../training/turboquant.py)
- [`tests/test_turboquant.py`](../tests/test_turboquant.py)
- [`scripts/serve_openai_chat_adapter.py`](../scripts/serve_openai_chat_adapter.py)
- [`scripts/run_hf_pass1_eval.py`](../scripts/run_hf_pass1_eval.py)

## What It Is

This repo currently implements an experimental TurboQuant-style cache:

- quantized KV prefix storage
- fp residual window for recent tokens
- optional Hadamard-style rotation before quantization
- compatibility aliases so the cache can be injected as `past_key_values=<cache>`

It is intended for controlled inference experiments, not as a paper-fidelity claim.

## Local Validation

Syntax and unit tests:

```bash
cd /Users/daxu/software/quantum-gpt
PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m py_compile \
  training/turboquant.py \
  scripts/run_hf_pass1_eval.py \
  scripts/serve_openai_chat_adapter.py
python3 -m pytest tests/test_turboquant.py
```

Tiny `transformers` generation smoke without downloading a model:

```bash
cd /Users/daxu/software/quantum-gpt
python3 - <<'PY'
import torch
from transformers import Qwen2Config, Qwen2ForCausalLM
from training.turboquant import TurboQuantCache, TurboQuantConfig

model = Qwen2ForCausalLM(
    Qwen2Config(
        vocab_size=128,
        hidden_size=64,
        intermediate_size=128,
        num_hidden_layers=2,
        num_attention_heads=4,
        num_key_value_heads=4,
        max_position_embeddings=128,
    )
).eval()

cache = TurboQuantCache(
    config=TurboQuantConfig(
        nbits=4,
        secondary_nbits=1,
        group_size=16,
        residual_length=4,
        rotation="none",
        compute_dtype=torch.float32,
    )
)
output = model.generate(
    input_ids=torch.tensor([[1, 2, 3, 4]]),
    max_new_tokens=3,
    do_sample=False,
    past_key_values=cache,
)
print({"shape": tuple(output.shape), "seq_length": cache.get_seq_length(0)})
PY
```

Expected shape from the validated local smoke:

```text
{'shape': (1, 7), 'seq_length': 6}
```

## Local Server Usage

TurboQuant is off by default. To enable it in the local OpenAI-compatible adapter server:

```bash
cd /Users/daxu/software/quantum-gpt
python3 scripts/serve_openai_chat_adapter.py \
  --base-model /path/to/base-model \
  --adapter /path/to/adapter \
  --model-name quantum-gpt-omnicoder9b.1 \
  --device cpu \
  --enable-turboquant-cache \
  --turboquant-nbits 4 \
  --turboquant-secondary-nbits 1 \
  --turboquant-group-size 64 \
  --turboquant-residual-length 128 \
  --turboquant-rotation hadamard
```

If that server is backing Codex, the Codex invocation pattern is unchanged:

```bash
codex -p local -m quantum-gpt-omnicoder9b.1
```

The server-side TurboQuant flag changes the model-serving path; the Codex client command stays the same.

## Local Eval Usage

To enable TurboQuant in the HF pass@1 runner:

```bash
cd /Users/daxu/software/quantum-gpt
python3 scripts/run_hf_pass1_eval.py \
  --run-dir /path/to/run \
  --base-model /path/to/base-model \
  --adapter /path/to/adapter \
  --device cpu \
  --score \
  --turboquant-enable \
  --turboquant-nbits 4 \
  --turboquant-group-size 64 \
  --turboquant-residual-length 128 \
  --turboquant-axis-key 0 \
  --turboquant-axis-value 0 \
  --turboquant-q-group-size 64
```

The runner records effective TurboQuant settings in:

- `hf-pass1-generation-log.json`

## ai2 Sync

Push the relevant code from this Mac to S3:

```bash
cd /Users/daxu/software/quantum-gpt
scripts/push_to_s3.sh \
  training/turboquant.py \
  tests/test_turboquant.py \
  scripts/serve_openai_chat_adapter.py \
  scripts/run_hf_pass1_eval.py \
  research/turboquant-runbook.md
```

Then sync S3 to `ai2`:

```bash
cd /Users/daxu/software/quantum-gpt
scripts/ai2_sync_from_s3.sh
```

## ai2 Validation

Remote unit tests:

```bash
cd /root/root/work/quantum-gpt
PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m py_compile \
  training/turboquant.py \
  scripts/run_hf_pass1_eval.py \
  scripts/serve_openai_chat_adapter.py
python3 -m pytest tests/test_turboquant.py
```

Remote tiny generate smoke:

```bash
cd /root/root/work/quantum-gpt
python3 - <<'PY'
import torch
from transformers import Qwen2Config, Qwen2ForCausalLM
from training.turboquant import TurboQuantCache, TurboQuantConfig

model = Qwen2ForCausalLM(
    Qwen2Config(
        vocab_size=128,
        hidden_size=64,
        intermediate_size=128,
        num_hidden_layers=2,
        num_attention_heads=4,
        num_key_value_heads=4,
        max_position_embeddings=128,
    )
).eval()

cache = TurboQuantCache(
    config=TurboQuantConfig(
        nbits=4,
        secondary_nbits=1,
        group_size=16,
        residual_length=4,
        rotation="none",
        compute_dtype=torch.float32,
    )
)
output = model.generate(
    input_ids=torch.tensor([[1, 2, 3, 4]]),
    max_new_tokens=3,
    do_sample=False,
    past_key_values=cache,
)
print({"shape": tuple(output.shape), "seq_length": cache.get_seq_length(0)})
PY
```

## ai2 OmniCoder Server With TurboQuant

To run the ai2 local server with the finetuned OmniCoder model and TurboQuant enabled:

```bash
cd /root/root/work/quantum-gpt
export NO_PROXY=127.0.0.1,localhost
export no_proxy=127.0.0.1,localhost
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY
nohup env \
  PYTHONUNBUFFERED=1 \
  PYTHONPYCACHEPREFIX=/tmp/pycache \
  ASCEND_RT_VISIBLE_DEVICES=6 \
  python3 scripts/serve_openai_chat_adapter.py \
    --base-model /root/root/work/quantum-gpt/models/OmniCoder-9B \
    --adapter /root/root/work/quantum-gpt/outputs/interface-prefix-omnicoder9b-semantic-v4-2npu-true20-20260329T2219CST/adapter \
    --model-name quantum-gpt-omnicoder9b.1 \
    --device npu \
    --host 127.0.0.1 \
    --port 8000 \
    --enable-turboquant-cache \
    --turboquant-nbits 4 \
    --turboquant-secondary-nbits 1 \
    --turboquant-group-size 64 \
    --turboquant-residual-length 128 \
    --turboquant-rotation hadamard \
  > /tmp/quantum_codex_server_turboquant.log 2>&1 &
```

Health check:

```bash
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
  NO_PROXY=127.0.0.1,localhost \
  curl --noproxy '*' -fsS http://127.0.0.1:8000/health
```

If the server is healthy, Codex uses the same verified command:

```bash
cd /root/root/work/quantum-gpt
export LOCAL_CODEX_API_KEY=dummy
/root/.local/bin/codex exec \
  --skip-git-repo-check \
  --color never \
  -C /root/root/work/quantum-gpt \
  -p local \
  -m quantum-gpt-omnicoder9b.1 \
  'Reply with exactly OK and nothing else.'
```
