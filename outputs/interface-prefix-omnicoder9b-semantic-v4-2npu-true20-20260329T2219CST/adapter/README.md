---
base_model: models/OmniCoder-9B
library_name: peft
---

# OmniCoder 9B Interface-Prefix Semantic-v4 Adapter

This directory contains the first verified working OmniCoder 9B fine-tuned adapter produced in this workspace.

## Artifact

- Base model: `models/OmniCoder-9B`
- Adapter type: LoRA
- Adapter path: `outputs/interface-prefix-omnicoder9b-semantic-v4-2npu-true20-20260329T2219CST/adapter`
- Training metrics: `outputs/interface-prefix-omnicoder9b-semantic-v4-2npu-true20-20260329T2219CST/metrics.json`

## Verified Run

- Devices: `ASCEND_RT_VISIBLE_DEVICES=6,7`
- World size: `2`
- Train examples: `160`
- Eval examples: `32`
- Completed steps: `20`
- Final eval loss: `0.3727272283285856`
- Final eval perplexity: `1.4516883063761739`

This adapter outperformed the current local Qwen semantic-v4 true20 reference in this workspace on the recorded eval metrics.

## LoRA Configuration

- Rank `r=16`
- Alpha `32`
- Dropout `0.05`
- Target modules: `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`

## Load Example

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoProcessor, AutoTokenizer, PreTrainedTokenizerFast

from training.qwen_sft_peft import load_text_preprocessor_backend

base_path = "models/OmniCoder-9B"
adapter_path = "outputs/interface-prefix-omnicoder9b-semantic-v4-2npu-true20-20260329T2219CST/adapter"

backend = load_text_preprocessor_backend(
    base_path,
    AutoTokenizer,
    AutoProcessor,
    PreTrainedTokenizerFast,
)

model = AutoModelForCausalLM.from_pretrained(
    base_path,
    trust_remote_code=True,
    low_cpu_mem_usage=True,
    torch_dtype="auto",
)
model = PeftModel.from_pretrained(model, adapter_path)
model.eval()
```

## Runtime Notes

- The OmniCoder snapshot uses the `qwen3_5` architecture.
- Local environments with older `transformers` releases will fail to load it.
- ai2 is already verified with a new enough runtime and successfully trained this adapter.
