import copy
import importlib.util


DEFAULTS = {
    "optimizer": {"name": "adam", "lr": 0.001, "beta1": 0.9},
    "batch_size": 8,
    "logging": {"level": "info", "json": False},
}

OVERRIDES = {
    "optimizer": {"lr": 0.0005},
    "logging": {"json": True},
    "new_flag": True,
}

EXPECTED = {
    "optimizer": {"name": "adam", "lr": 0.0005, "beta1": 0.9},
    "batch_size": 8,
    "logging": {"level": "info", "json": True},
    "new_flag": True,
}


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)

    defaults = copy.deepcopy(DEFAULTS)
    overrides = copy.deepcopy(OVERRIDES)
    merged = module.merge_config(defaults, overrides)

    failures = []
    if merged != EXPECTED:
        failures.append(f"merge_config returned {merged}, expected {EXPECTED}")
    if defaults != DEFAULTS:
        failures.append("merge_config mutated defaults input")
    if overrides != OVERRIDES:
        failures.append("merge_config mutated overrides input")
    if merged is defaults:
        failures.append("merge_config returned the original defaults object")
    if merged["optimizer"] is defaults["optimizer"]:
        failures.append("merge_config reused nested optimizer dict instead of producing a merged copy")

    return {
        "passed": not failures,
        "details": failures or ["Recursive config merge preserves semantics and input immutability"],
    }
