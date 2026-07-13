#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from transformers import AutoProcessor, AutoTokenizer, PreTrainedTokenizerFast

from training.text_preprocessor_backend import load_text_preprocessor_backend


def main() -> int:
    model_path = sys.argv[1]
    backend = load_text_preprocessor_backend(
        model_path,
        AutoTokenizer,
        AutoProcessor,
        PreTrainedTokenizerFast,
    )
    tokenizer = backend.text_backend
    print(f"backend_kind={backend.backend_kind}")
    print(f"tokenizer_class={tokenizer.__class__.__name__}")
    rendered = backend.render_backend.apply_chat_template(
        [{"role": "user", "content": "hi"}],
        tokenize=False,
        add_generation_prompt=True,
    )
    print(f"rendered_prefix={rendered[:120]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
