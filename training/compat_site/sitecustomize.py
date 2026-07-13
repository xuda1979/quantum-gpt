try:
    import inspect

    import torch.utils._pytree as _pytree

    if not hasattr(_pytree, "register_pytree_node"):
        _orig = getattr(_pytree, "_register_pytree_node", None)
        if _orig is not None:
            try:
                _accepted = set(inspect.signature(_orig).parameters.keys())
            except (TypeError, ValueError):
                _accepted = None

            def _compat_register_pytree_node(cls, flatten_fn, unflatten_fn, *args, **kwargs):
                if _accepted is not None:
                    kwargs = {k: v for k, v in kwargs.items() if k in _accepted}
                return _orig(cls, flatten_fn, unflatten_fn, *args, **kwargs)

            _pytree.register_pytree_node = _compat_register_pytree_node
except Exception:
    pass

# Compat shim: transformers>=5.x hard-gates on torch>=2.4 and regex>=2025.10.22 via
# importlib.metadata.version() distribution lookups (NOT via torch.__version__ or the
# real regex module attribute). The NPU training pods are pinned to torch==2.1.0 (tightly
# coupled to the Ascend CANN toolkit / torch_npu build) and an older regex, so we cannot
# upgrade the real packages. Instead we spoof ONLY what importlib.metadata reports for
# these two distributions, leaving the actual installed torch/torch_npu/regex modules
# untouched so NPU device binding and regex behavior at runtime are unaffected.
try:
    import importlib.metadata as _ilm

    _SPOOF_VERSIONS = {
        "torch": "2.4.0",
        "regex": "2025.10.22",
    }

    _orig_version = _ilm.version

    def _compat_version(name, *args, **kwargs):
        if name in _SPOOF_VERSIONS:
            try:
                real = _orig_version(name, *args, **kwargs)
            except Exception:
                real = None
            spoof = _SPOOF_VERSIONS[name]
            return spoof if real is not None else real
        return _orig_version(name, *args, **kwargs)

    _ilm.version = _compat_version
except Exception:
    pass

# Compat shim: transformers>=5.x (utils/generic.py's ModelOutput pytree registration)
# calls torch.compiler.is_compiling(), which does not exist on the pod's real torch==2.1.0
# build. We are running plain eager-mode training (no torch.compile anywhere in this SFT
# script), so it is always correct to report "not compiling". Prefer delegating to
# torch._dynamo.is_compiling() if present (older equivalent API); otherwise fall back to a
# constant False. Also backfill a couple of other torch.compiler helpers that newer
# transformers code occasionally probes for, using the same eager-mode-safe semantics.
try:
    import torch as _torch

    if not hasattr(_torch, "compiler"):
        import types as _types

        _torch.compiler = _types.ModuleType("torch.compiler")

    _compiler_mod = _torch.compiler

    if not hasattr(_compiler_mod, "is_compiling"):
        _dynamo_is_compiling = None
        try:
            import torch._dynamo as _dynamo

            _dynamo_is_compiling = getattr(_dynamo, "is_compiling", None)
        except Exception:
            _dynamo_is_compiling = None

        if _dynamo_is_compiling is not None:
            _compiler_mod.is_compiling = _dynamo_is_compiling
        else:
            _compiler_mod.is_compiling = lambda: False

    if not hasattr(_compiler_mod, "is_dynamo_compiling"):
        _compiler_mod.is_dynamo_compiling = _compiler_mod.is_compiling

    if not hasattr(_compiler_mod, "is_exporting"):
        _compiler_mod.is_exporting = lambda: False
except Exception:
    pass

# Compat shim: newer transformers modules reference dtype constants
# (torch.uint16 / torch.uint32 / torch.uint64) that were only added to torch in later
# releases (torch's real unsigned-int-beyond-uint8 dtypes landed after 2.1.0). These are
# referenced as module-level constants (e.g. by image-processing / AutoProcessor plumbing)
# that this text-only LoRA SFT run never actually exercises, so it is safe to backfill
# them with the closest signed dtype of the same bit width purely so the attribute lookup
# and any incidental import-time references succeed; no unsigned-dtype tensor math is
# performed in this training script.
try:
    import torch as _torch

    for _bits, _signed_name in ((16, "int16"), (32, "int32"), (64, "int64")):
        _uname = f"uint{_bits}"
        if not hasattr(_torch, _uname):
            _fallback = getattr(_torch, _signed_name, None)
            if _fallback is not None:
                setattr(_torch, _uname, _fallback)
except Exception:
    pass

# Compat shim: transformers>=5.x MoE integration module
# (transformers/integrations/moe.py) unconditionally calls, at *module import time*,
# torch.library.custom_op(...) / register_fake(...) / register_autograd(...) to wire up a
# "grouped_mm_fallback" custom op used by MoE models (e.g. Qwen3.5-MoE) whenever the newer
# torch._grouped_mm primitive is unavailable. torch.library.custom_op is a torch>=2.4 API
# that does not exist on the pod's real torch==2.1.0, so the bare `import
# transformers.models.qwen3_5_moe...` raises AttributeError before any model code runs.
#
# We are always in plain eager mode here (no torch.compile in this LoRA SFT script), so the
# dispatcher-level machinery (fake/meta shape inference for compile, manual autograd
# registration for compiled backward) is unnecessary: the wrapped Python function
# (`_grouped_mm_fallback`) is written using ordinary differentiable torch ops (bmm, index,
# cumsum, ...), so PyTorch's normal eager autograd can differentiate through it directly
# without any custom op registration at all. We polyfill `torch.library.custom_op` /
# `register_fake` / `register_autograd` with lightweight shims: `custom_op` registers the
# *plain* wrapped function directly onto the `torch.ops.<namespace>.<name>` attribute (so
# the call site `torch.ops.transformers.grouped_mm_fallback(...)` still resolves and runs,
# using ordinary eager-differentiable Python code instead of a dispatcher-level custom op),
# and `register_fake`/`register_autograd` become no-ops since nothing needs to consume them
# outside of torch.compile.
try:
    import torch as _torch

    if not hasattr(_torch.library, "custom_op"):

        def _custom_op_polyfill(qualname, fn=None, *, mutates_args=(), **_kwargs):
            def _bind(target_fn):
                ns_name, _, op_name = qualname.partition("::")
                try:
                    ns_obj = getattr(_torch.ops, ns_name)
                except Exception:
                    ns_obj = None
                bound = False
                if ns_obj is not None:
                    try:
                        setattr(ns_obj, op_name, target_fn)
                        bound = True
                    except Exception:
                        bound = False
                if not bound:
                    # Fallback: at least make the namespace importable/callable via a
                    # plain attribute on torch.ops itself if the real _OpNamespace proxy
                    # refuses attribute assignment.
                    try:
                        import types as _types3

                        shim_ns = getattr(_torch.ops, ns_name, None)
                        if shim_ns is None or not hasattr(shim_ns, "__dict__"):
                            shim_ns = _types3.SimpleNamespace()
                            setattr(_torch.ops, ns_name, shim_ns)
                        setattr(shim_ns, op_name, target_fn)
                    except Exception:
                        pass
                return target_fn

            if fn is not None:
                return _bind(fn)
            return _bind

        _torch.library.custom_op = _custom_op_polyfill
        _torch.library.register_fake = lambda *a, **k: (lambda f: f)
        _torch.library.register_autograd = lambda *a, **k: None
except Exception:
    pass

# Compat shim: accelerate>=0.something imports `from torch.amp import GradScaler`, a
# unified (device-agnostic) GradScaler API that was only added to the top-level
# `torch.amp` namespace in a later torch release. The pod's real torch==2.1.0 only has the
# older `torch.cuda.amp.GradScaler` location. Alias it in so the import succeeds; this
# training script runs LoRA SFT on NPU without CUDA-style loss-scaling AMP, so the actual
# GradScaler class is never instantiated/used, only imported.
try:
    import torch as _torch

    if not hasattr(_torch.amp, "GradScaler"):
        _grad_scaler_cls = None
        try:
            from torch.cuda.amp import GradScaler as _grad_scaler_cls
        except Exception:
            _grad_scaler_cls = None

        if _grad_scaler_cls is None:

            class _grad_scaler_cls:  # minimal no-op stand-in, never expected to be used
                def __init__(self, *args, **kwargs):
                    pass

                def scale(self, loss):
                    return loss

                def step(self, optimizer, *args, **kwargs):
                    return optimizer.step(*args, **kwargs)

                def update(self, *args, **kwargs):
                    pass

                def unscale_(self, optimizer):
                    pass

                def get_scale(self):
                    return 1.0

                def is_enabled(self):
                    return False

                def state_dict(self):
                    return {}

                def load_state_dict(self, state_dict):
                    pass

        _torch.amp.GradScaler = _grad_scaler_cls
except Exception:
    pass

# Compat shim: torch.get_default_device() (device-agnostic accessor for whatever device
# torch.set_default_device() configured, defaulting to CPU) was added in a torch release
# newer than the pod's real torch==2.1.0. transformers>=5.x model-loading code calls this
# to decide where to materialize tensors before explicit .to(device) placement happens
# later. Since this training script always passes an explicit --device (npu) and moves the
# model itself, the exact value returned here is not load-bearing; default to CPU (torch's
# own historical implicit default) unless torch.set_default_device has stashed something we
# can introspect.
try:
    import torch as _torch

    if not hasattr(_torch, "get_default_device"):

        def _get_default_device_polyfill():
            try:
                return _torch.empty(0).device
            except Exception:
                return _torch.device("cpu")

        _torch.get_default_device = _get_default_device_polyfill
except Exception:
    pass

# Compat shim: transformers>=5.x (utils/generic.py's maybe_autocast helper, used by
# Qwen3.5/Qwen3.5-MoE modeling code to force float32 in certain submodules) calls
# torch.is_autocast_enabled(device_type) with a positional device_type argument. That
# device-type-aware signature was only added to torch.is_autocast_enabled() in a later
# torch release; the pod's real torch==2.1.0 build only has the old zero-argument form
# (which implicitly always meant the CUDA autocast flag). We wrap it to accept and ignore
# any device_type argument, delegating to the real no-arg implementation. This is safe for
# this eager-mode NPU LoRA SFT run since we never rely on per-device-type autocast state
# differing from the single global flag torch 2.1.0 tracks.
try:
    import torch as _torch

    _orig_is_autocast_enabled = _torch.is_autocast_enabled

    def _is_autocast_enabled_polyfill(device_type=None, *args, **kwargs):
        return _orig_is_autocast_enabled()

    _torch.is_autocast_enabled = _is_autocast_enabled_polyfill
except Exception:
    pass
