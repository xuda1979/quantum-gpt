import importlib.util


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures = []
    expected = {"00": "I", "01": "X", "10": "Z", "11": "XZ"}

    for bits, opcode in expected.items():
        if module.encode_message(bits) != opcode:
            failures.append(f"encode_message failed for {bits}")
        if module.decode_message(opcode) != bits:
            failures.append(f"decode_message failed for {opcode}")

    if module.decode_message("zx") != "11":
        failures.append("decode_message should canonicalize zx -> XZ")

    try:
        module.decode_message("YY")
        failures.append("decode_message accepted invalid opcode")
    except ValueError:
        pass

    return {
        "passed": not failures,
        "details": failures or ["superdense Pauli router preserves canonical XZ mapping"],
    }
