import importlib.util


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures: list[str] = []

    # --- graph fixture ---
    try:
        edges = module.graph_edges()
        if edges != [(0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 5)]:
            failures.append(f"edges={edges}, expected the 6-edge fixture")
    except Exception as e:  # noqa: BLE001
        failures.append(f"graph_edges raised: {e}")

    # --- circuit structure: 6 qubits, 6 CZ gates ---
    try:
        qc = module.graph_state_circuit()
        if qc.num_qubits != 6:
            failures.append(f"circuit_qubits={qc.num_qubits}, expected 6")
        czs = [op for op in qc.data if op.operation.name == "cz"]
        if len(czs) != 6:
            failures.append(f"cz_edges={len(czs)}, expected 6")
    except Exception as e:  # noqa: BLE001
        failures.append(f"graph_state_circuit raised: {e}")

    # --- stabilizer operators: independent from_sparse_list construction ---
    try:
        ops = module.stabilizers()
        if len(ops) != 6:
            failures.append(f"stabilizer_count={len(ops)}, expected 6")
        neighbors = {v: set() for v in range(6)}
        for a, b in module.graph_edges():
            neighbors[a].add(b)
            neighbors[b].add(a)
        from qiskit.quantum_info import SparsePauliOp

        for v in range(6):
            qubits = [v] + sorted(neighbors[v])
            label = "X" + "Z" * (len(qubits) - 1)
            expected = SparsePauliOp.from_sparse_list([(label, qubits, 1.0)], num_qubits=6)
            got = ops[v].to_list()[0][0]
            want = expected.to_list()[0][0]
            if got != want:
                failures.append(f"stab_{v}={got}, expected {want}")
    except Exception as e:  # noqa: BLE001
        failures.append(f"stabilizers check raised: {e}")

    # --- all expectations +1 within 1e-12 ---
    result = None
    try:
        result = module.run_checks()
    except Exception as e:  # noqa: BLE001
        failures.append(f"run_checks raised: {e}")
    if result:
        exp = result.get("expectations") or {}
        if len(exp) != 6:
            failures.append(f"expectation_count={len(exp)}, expected 6")
        for label, value in exp.items():
            if abs(float(value) - 1.0) > 1e-12:
                failures.append(f"expectation_{label}={value:.6f}, expected 1.000000")
        min_exp = float(result.get("min_expectation", 0.0))
        if min_exp < 1.0 - 1e-12:
            failures.append(f"min_expectation={min_exp:.6f}, expected >= 0.999999999999")
        max_dev = float(result.get("max_deviation", 1.0))
        if max_dev > 1e-12:
            failures.append(f"max_deviation={max_dev:.2e}, expected < 1e-12")

    return {
        "passed": not failures,
        "details": failures
        or [
            "6-qubit graph state (6 edges): 6 CZ gates, all six K_v built via "
            "from_sparse_list match the independent construction, every "
            "stabilizer expectation = 1 within 1e-12",
        ],
    }
