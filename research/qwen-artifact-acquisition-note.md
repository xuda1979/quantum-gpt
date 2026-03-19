# Qwen Artifact Acquisition Note

## Purpose

Record the current model-artifact acquisition reality before more remote retries:

- `ai2` shell access is real
- the remote bootstrap stack is installed enough to reach tokenizer load
- the current blocker is model artifact availability, not shell access

## Concrete observations from this machine

### Local anonymous URL probes

Tested tokenizer-config URLs with short local `urllib` requests.

Results:

- `https://huggingface.co/Qwen/Qwen3.5-1.5B-Instruct/resolve/main/tokenizer_config.json`
  - returns `HTTP 401 Unauthorized`
- `https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct/resolve/main/tokenizer_config.json`
  - returns `HTTP 200 OK`
- `https://hf-mirror.com/Qwen/Qwen2.5-1.5B-Instruct/resolve/main/tokenizer_config.json`
  - returns `HTTP 403 Forbidden`
- `https://hf-mirror.com/Qwen/Qwen3.5-1.5B-Instruct/resolve/main/tokenizer_config.json`
  - returns `HTTP 404 Not Found`

### Local cache probe

Searched `~/.cache`, `~/.cache/huggingface`, and `~/.cache/huggingface/hub`.

Result:

- no existing local cached snapshot for `Qwen/Qwen3.5-1.5B-Instruct`
- no ready-to-transfer tokenizer/model tree is present on this machine right now

## Implication

The project target remains **Qwen3.5-1.5B-Instruct**.

But the next blocker is now precise:

- the target model path is not anonymously retrievable from this local machine
- the remote `ai2` environment also does not currently provide a reliable direct fetch path for tokenizer/model artifacts
- therefore the next honest unblocker is **authenticated or otherwise approved acquisition of the exact Qwen 3.5 artifacts**, followed by transfer into `/root/root/work/quantum-gpt`

## What not to do

- do not claim training has begun in `ai2`
- do not keep re-running the same remote tokenizer-load failure without new artifacts
- do not silently swap the project target to Qwen 2.5 just because it is easier to fetch

## Smallest next unblocker

One of these must happen next:

1. authenticated local download of `Qwen/Qwen3.5-1.5B-Instruct` tokenizer/model files
2. an approved alternate source for the exact same artifact set
3. a user-provided local snapshot path that can be transferred into `ai2`

Once available, the next remote step is:

```bash
python3 training/huanxin_cpu_smoke.py --model-name <local-qwen35-path> --dataset data/seed/splits-auto-seed/train.jsonl
```

and only after that succeeds should the PEFT smoke/training step begin.
