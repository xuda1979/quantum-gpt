import importlib.util


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    ok = True
    details = []
    expected = {"00": "I", "01": "X", "10": "Z", "11": "XZ"}

    for bits, op in expected.items():
        if module.encode_message(bits) != op:
            ok = False
            details.append(f"encode_message failed for {bits}")
        if module.decode_message(op) != bits:
            ok = False
            details.append(f"decode_message failed for {op}")

    return {"passed": ok, "details": details or ["all message mappings round-trip correctly"]}
