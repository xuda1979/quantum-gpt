"""Checked LoRA-adapter apply + generation probe (C-0002 layer).

Restored 2026-09-20 as its OWN module after the concurrent run_hf_pass1_eval
rewrite dropped the functions while scripts/eval_failclosed_probe.py and
scripts/sapo_smoke_probe.py still imported them (the mid-refactor wipe). The
functions here are the fail-closed adapter-apply path: remap SAPO keys,
refuse dropped/inert/zero loads, and prove the adapter CHANGES generation
against a PRE-APPLY base snapshot (peft wraps the base in place -- a
post-apply "base" sample runs WITH the adapter and compares it to itself,
measured 2026-09-20: bit-identical logits, delta 0.0).

Consumers: scripts/run_hf_pass1_eval.py re-exports every public name here;
scripts/eval_failclosed_probe.py and scripts/sapo_smoke_probe.py import them
from run_hf_pass1_eval.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

import torch


def _remap_sapo_keys(keys: list) -> list:
    """Remap text-only SAPO trainer keys into the full multimodal namespace.

    The SAPO trainer wraps the text-only causal LM, so its peft keys lack the
    language_model segment the full multimodal base requires; peft silently
    skips unmapped keys (the 2026-08-24 base-vs-base tie class). Both peft
    prefix shapes are handled; warm-namespace keys pass through untouched.
    """
    remapped: list = []
    for key in keys:
        if key.startswith("base_model.model.model.") and not key.startswith(
            "base_model.model.model.language_model."
        ):
            rest = key[len("base_model.model.model.") :]
            remapped.append("base_model.model.model.language_model." + rest)
        elif (
            key.startswith("base_model.model.")
            and not key.startswith("base_model.model.language_model.")
            # a warm key under base_model.model.model.language_model. already
            # carries the segment -- the old guard missed this shape and
            # double-prefixed it, which peft then silently skips.
            and not key.startswith("base_model.model.model.language_model.")
        ):
            rest = key[len("base_model.model.") :]
            remapped.append("base_model.model.language_model." + rest)
        else:
            remapped.append(key)
    return remapped


def _state_has_nonzero_b(state: dict) -> bool:
    """True iff any lora_B tensor in the checkpoint is nonzero."""
    for key, tensor in state.items():
        if "lora_B" in str(key) and torch.any(tensor != 0):
            return True
    return False


def _state_inert(state: dict) -> bool:
    """Prove a checkpoint inert: LoRA-only tensors with all-zero lora_B.

    Non-LoRA tensors (modules_to_save / full-weight saves) and empty
    checkpoints can never prove inertness, so they fail closed -- a
    zero-loaded model with a nonzero non-LoRA checkpoint is a silent base
    run.
    """
    if not state:
        return False
    lora_b_seen = False
    for key, tensor in state.items():
        k = str(key)
        if "lora_B" in k:
            lora_b_seen = True
            if torch.any(tensor != 0):
                return False
        elif "lora_A" in k:
            continue
        else:
            return False
    return lora_b_seen


def _norm_tensor_key(key: str) -> str:
    """Normalize a peft/checkpoint tensor name for presence comparison.

    Strips the peft wrapper prefix, the adapter-name segment, and the
    language_model segment (its position differs between the text-only
    trainer namespace, the multimodal base, and transformers major
    versions) -- a truly skipped tensor still differs by its module path.
    """
    out = str(key)
    if out.startswith("base_model.model."):
        out = out[len("base_model.model.") :]
    out = out.replace(".default", "")
    out = out.replace("language_model.", "")
    return out


def _missing_loaded_tensors(merged: Any, state: dict) -> list:
    """Checkpoint tensors (normalized names) absent from the loaded model."""
    loaded = set(_norm_tensor_key(k) for k in merged.state_dict().keys())
    missing = []
    for key in state.keys():
        norm = _norm_tensor_key(str(key))
        if norm not in loaded:
            missing.append(norm)
    return missing


def _adapter_effectively_zero(adapter: Any, base: Any = None, base_param_ids: Any = None) -> bool:
    """True iff the adapter has NO live delta.

    A lora_B tensor counts as dead when it is all-zero OR aliases the base
    parameter set. Without the PRE-MUTATION id snapshot, the in-place peft
    wrap makes every live tensor look like base (2026-08-25 aliasing
    regression that aborted three legs) -- callers must pass the snapshot
    taken before PeftModel.from_pretrained/get_peft_model.
    """
    if base_param_ids is None and base is not None:
        base_param_ids = set(id(param) for param in base.parameters())
    live: list = []
    for name, param in adapter.named_parameters():
        if "lora_B" not in name:
            continue
        if base_param_ids is not None and id(param) in base_param_ids:
            continue
        live.append(param)
    if not live:
        return True
    return all(not torch.any(param != 0) for param in live)


def _apply_adapter_checked(base: Any, adapter_dir: Path) -> Any:
    """Load a LoRA adapter with fail-closed verification (C-0002).

    Remaps SAPO text-only keys when the base is the full multimodal model,
    refuses partial peft loads (dropped tensors), refuses provably inert
    checkpoints, and refuses model-level zero merges after the
    aliasing-safe id-snapshot comparison. On success prints the
    adapter_applied stage event and attaches _sapo_base_param_ids.
    """
    from peft import PeftModel
    from safetensors import safe_open
    from safetensors.torch import save_file

    adapter_dir = Path(adapter_dir)
    weights_path = adapter_dir / "adapter_model.safetensors"
    if not weights_path.is_file():
        raise SystemExit("adapter weights missing: " + str(weights_path))
    state: dict = dict()
    with safe_open(str(weights_path), framework="pt", device="cpu") as handle:
        for key in handle.keys():
            state[str(key)] = handle.get_tensor(key)
    if not state:
        raise SystemExit("adapter checkpoint is empty: " + str(weights_path))

    load_dir = adapter_dir
    base_keys = [str(key) for key in base.state_dict().keys()]
    if any("language_model" in key for key in base_keys):
        remapped = _remap_sapo_keys(list(state.keys()))
        if remapped != list(state.keys()):
            tensors = dict()
            for old_key, new_key in zip(state.keys(), remapped):
                tensors[new_key] = state[old_key]
            load_dir = Path(tempfile.mkdtemp(prefix="sapo-adapter-remap-"))
            save_file(tensors, str(load_dir / "adapter_model.safetensors"))
            shutil.copyfile(
                adapter_dir / "adapter_config.json",
                load_dir / "adapter_config.json",
            )

    if _state_inert(state):
        raise SystemExit(
            "adapter checkpoint is provably inert (all lora_B zero): " + str(adapter_dir)
        )

    base_param_ids = set(id(param) for param in base.parameters())
    merged = PeftModel.from_pretrained(base, str(load_dir))
    merged.eval()

    dropped = _missing_loaded_tensors(merged, state)
    if dropped:
        raise SystemExit(
            "adapter weights silently skipped ("
            + str(len(dropped))
            + " tensors missing, e.g. "
            + str(dropped[:3])
            + ")"
        )
    if _adapter_effectively_zero(merged, base, base_param_ids):
        raise SystemExit("adapter merge is effectively zero after load: " + str(adapter_dir))

    merged._sapo_base_param_ids = base_param_ids
    print(
        json.dumps(
            dict(stage="adapter_applied", adapter=str(adapter_dir)),
            ensure_ascii=False,
        ),
        flush=True,
    )
    return merged


def _capture_probe_output(
    base: Any,
    prompt: str,
    backend: Any = None,
    max_new_tokens: int = 8,
) -> dict:
    """Greedy-continuation + first-step-logit snapshot of `base` on the probe
    prompt.

    MUST be captured BEFORE PeftModel.from_pretrained/get_peft_model wraps
    the model: peft replaces the target modules IN PLACE, so after the wrap
    the original object's forward RUNS WITH THE ADAPTER (measured
    2026-09-20 on transformers 5.14.1 + peft 0.19.1: the post-wrap "base"
    produced bit-identical logits to the adapter, delta 0.0 -- the probe
    compared the adapter against itself and every leg failed closed with
    "adapter probe output identical to base").
    """
    from scripts.run_hf_pass1_eval import build_inputs, render_prompt

    device = next(base.parameters()).device
    if backend is not None:
        prompt_text = render_prompt(backend, system_prompt="", user_prompt=prompt)
        inputs = build_inputs(backend, prompt_text, str(device))
    else:
        cfg = getattr(base, "config", None)
        # multimodal bases (Qwen2VL) nest the LM vocab under text_config
        vocab = int(
            getattr(cfg, "vocab_size", 0)
            or getattr(getattr(cfg, "text_config", None), "vocab_size", 0)
            or 0
        )
        if vocab <= 8:
            raise SystemExit("probe requires a model vocab larger than 8")
        ids = torch.tensor([[1, 2, 3, 4, 5, 6, 7]], dtype=torch.long, device=device)
        inputs = dict(input_ids=ids, attention_mask=torch.ones_like(ids))
    prompt_len = inputs["input_ids"].shape[1]
    gen_kwargs: dict = dict(
        max_new_tokens=max_new_tokens,
        do_sample=False,
        output_scores=True,
        return_dict_in_generate=True,
    )
    if backend is not None:
        eos = getattr(backend.text_backend, "eos_token_id", None)
        if eos is not None:
            gen_kwargs["pad_token_id"] = eos
    with torch.inference_mode():
        out = base.generate(**inputs, **gen_kwargs)
    scores = list(getattr(out, "scores", None) or [])
    return dict(
        prompt_len=prompt_len,
        tail=out.sequences[0][prompt_len:].clone(),
        scores0=(scores[0].clone() if scores else None),
    )


def _probe_output_differs(
    captured: dict,
    adapter: Any,
    prompt: str,
    backend: Any = None,
    max_new_tokens: int = 8,
) -> bool:
    """True iff `adapter` differs from the PRE-APPLY captured base probe.

    Compares greedy continuation tokens AND first-step logits -- a
    weak-but-real delta can keep every greedy token identical while still
    moving the logits (2026-08-25 hardening)."""
    adapter_gen = _capture_probe_output(adapter, prompt, backend, max_new_tokens)
    if adapter_gen["tail"].shape != captured["tail"].shape or not torch.equal(
        captured["tail"], adapter_gen["tail"]
    ):
        return True
    if captured["scores0"] is None or adapter_gen["scores0"] is None:
        return False
    return not torch.equal(captured["scores0"], adapter_gen["scores0"])


def _probe_differs(
    base: Any,
    adapter: Any,
    prompt: str,
    backend: Any = None,
    max_new_tokens: int = 8,
) -> bool:
    """Fail-closed generation probe: True iff the adapter changes the model.

    Legacy one-shot signature: samples `base` NOW. Only correct while
    `base` is still PRISTINE (never handed to _apply_adapter_checked /
    get_peft_model, which wrap in place). For the checked-apply flow,
    capture with _capture_probe_output BEFORE the apply and call
    _probe_output_differs with the snapshot."""
    captured = _capture_probe_output(base, prompt, backend, max_new_tokens)
    return _probe_output_differs(captured, adapter, prompt, backend, max_new_tokens)
