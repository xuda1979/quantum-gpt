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

    # All single-qubit gates on different qubits -> depth 1
    gates1 = [("H", [0]), ("H", [1]), ("H", [2])]
    d = module.circuit_depth(gates1)
    if d != 1:
        failures.append(f"3 parallel H gates: depth={d}, expected 1")

    # Sequential gates on same qubit -> depth 3
    gates2 = [("H", [0]), ("X", [0]), ("Z", [0])]
    d = module.circuit_depth(gates2)
    if d != 3:
        failures.append(f"3 sequential gates on q0: depth={d}, expected 3")

    # CNOT(0,1) then CNOT(2,3) -> depth 1 (disjoint)
    gates3 = [("CX", [0, 1]), ("CX", [2, 3])]
    d = module.circuit_depth(gates3)
    if d != 1:
        failures.append(f"2 disjoint CNOTs: depth={d}, expected 1")

    # CNOT(0,1) then CNOT(1,2) -> depth 2 (share qubit 1)
    gates4 = [("CX", [0, 1]), ("CX", [1, 2])]
    d = module.circuit_depth(gates4)
    if d != 2:
        failures.append(f"2 chained CNOTs: depth={d}, expected 2")

    # Mixed: H(0), H(1), CX(0,1), H(2), CX(1,2)
    # H(0) and H(1) -> layer 0; H(2) also layer 0
    # CX(0,1) -> layer 1 (needs q0,q1 free after layer 0)
    # CX(1,2) -> layer 2 (needs q1 free after layer 1, q2 free after layer 0 -> max=1... wait q1 ready at 2)
    gates5 = [("H", [0]), ("H", [1]), ("CX", [0, 1]), ("H", [2]), ("CX", [1, 2])]
    d = module.circuit_depth(gates5)
    if d != 3:
        failures.append(f"Mixed circuit: depth={d}, expected 3")

    # Verify optimize_circuit preserves all gates
    layers = module.optimize_circuit(gates5)
    all_gates = [g for layer in layers for g in layer]
    if len(all_gates) != 5:
        failures.append(f"optimize_circuit lost gates: {len(all_gates)} != 5")

    # Empty circuit
    if module.circuit_depth([]) != 0:
        failures.append("Empty circuit depth should be 0")

    # Single gate
    if module.circuit_depth([("X", [0])]) != 1:
        failures.append("Single gate depth should be 1")

    # 3-qubit gate
    gates6 = [("CCX", [0, 1, 2]), ("H", [0])]
    d = module.circuit_depth(gates6)
    if d != 2:
        failures.append(f"CCX then H(0): depth={d}, expected 2")

    # CCX(0,1,2) then H(3) -> depth 1
    gates7 = [("CCX", [0, 1, 2]), ("H", [3])]
    d = module.circuit_depth(gates7)
    if d != 1:
        failures.append(f"CCX(0,1,2) + H(3): depth={d}, expected 1")

    return {
        "passed": not failures,
        "details": failures or ["Circuit depth optimization correct for all test cases"],
    }
