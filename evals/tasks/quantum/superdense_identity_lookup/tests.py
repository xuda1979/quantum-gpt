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
        if module.encode_bits(bits) != opcode:
            failures.append(f"encode_bits({bits!r}) failed")
        if module.decode_opcode(opcode) != bits:
            failures.append(f"decode_opcode({opcode!r}) failed")

    if module.decode_opcode("i") != "00":
        failures.append("decode_opcode should preserve the identity opcode I")
    if module.decode_opcode("zx") != "11":
        failures.append("decode_opcode should canonicalize zx -> XZ")

    try:
        module.decode_opcode("YY")
        failures.append("decode_opcode accepted invalid opcode")
    except ValueError:
        pass

    return {
        "passed": not failures,
        "details": failures or ["superdense identity lookup preserves the I opcode and canonical XZ routing"],
    }
