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

    # --- initial tableau: destabilizers X_i, stabilizers Z_i ---
    try:
        t = module.new_tableau(3)
        stabs = sorted(module.stabilizer_paulis(t))
        destabs = sorted(module.destabilizer_paulis(t))
        if stabs != ["+IIZ", "+IZI", "+ZII"]:
            failures.append(f"initial_stabilizers={stabs}, expected +ZII/+IZI/+IIZ")
        if destabs != ["+IIX", "+IXI", "+XII"]:
            failures.append(f"initial_destabilizers={destabs}, expected +XII/+IXI/+IIX")
        # commuting: every stabilizer commutes with every stabilizer
        violations = 0
        for i in range(3):
            for j in range(3):
                violations += module.symplectic_product(t, 3 + i, 3 + j)
        if violations != 0:
            failures.append(f"initial_commute_violations={violations}, expected 0")
        # stabilizer i anticommutes with its own destabilizer
        anticomm = 0
        for i in range(3):
            anticomm += module.symplectic_product(t, i, 3 + i)
        if anticomm != 3:
            failures.append(f"destab_stab_anticommutes={anticomm}, expected 3")
    except Exception as e:  # noqa: BLE001
        failures.append(f"new_tableau checks raised: {e}")

    # --- GHZ: generators +XXX, +ZZI, +IZZ ---
    ghz = None
    try:
        ghz = sorted(module.stabilizer_paulis(module.ghz_tableau()))
        expected = ["+XXX", "+ZIZ", "+ZZI"]
        matching = sum(1 for g in ghz if g in expected)
        if matching != 3:
            failures.append(f"ghz_generators_matching={matching}, expected 3 (got {ghz})")
    except Exception as e:  # noqa: BLE001
        failures.append(f"ghz_tableau raised: {e}")

    # --- cluster: generators +XZI, +ZXZ, +IZX ---
    cluster = None
    try:
        cluster = sorted(module.stabilizer_paulis(module.cluster_tableau()))
        expected = ["+IZX", "+XZI", "+ZXZ"]
        matching = sum(1 for g in cluster if g in expected)
        if matching != 3:
            failures.append(f"cluster_generators_matching={matching}, expected 3 (got {cluster})")
    except Exception as e:  # noqa: BLE001
        failures.append(f"cluster_tableau raised: {e}")

    # --- independent oracle: claimed generators leave the simulated
    #     GHZ/cluster state invariant (expectation +1) ---
    try:
        from qiskit import QuantumCircuit
        from qiskit.quantum_info import SparsePauliOp, Statevector

        ghz_circuit = QuantumCircuit(3)
        ghz_circuit.h(0)
        ghz_circuit.cx(0, 1)
        ghz_circuit.cx(0, 2)
        cluster_circuit = QuantumCircuit(3)
        cluster_circuit.h(range(3))
        cluster_circuit.cz(0, 1)
        cluster_circuit.cz(1, 2)
        for name, generators, circuit in (
            ("ghz", ghz, ghz_circuit),
            ("cluster", cluster, cluster_circuit),
        ):
            sv = Statevector(circuit)
            ok = 0
            for gen in generators:
                label = gen[1:]
                op = SparsePauliOp.from_list([(label, 1.0)])
                value = float((sv.expectation_value(op)).real)
                if abs(value - 1.0) < 1e-9:
                    ok += 1
            if ok != 3:
                failures.append(f"{name}_invariant_generators={ok}, expected 3")
    except Exception as e:  # noqa: BLE001
        failures.append(f"independent oracle raised: {e}")

    # --- commutation relations on the prepared states ---
    try:
        result = module.run_checks()
        if result.get("ghz_commute_violations", 1) != 0:
            failures.append(
                f"ghz_commute_violations={result.get('ghz_commute_violations')}, expected 0"
            )
        if result.get("cluster_commute_violations", 1) != 0:
            failures.append(
                f"cluster_commute_violations={result.get('cluster_commute_violations')}, expected 0"
            )
    except Exception as e:  # noqa: BLE001
        failures.append(f"run_checks raised: {e}")

    return {
        "passed": not failures,
        "details": failures
        or [
            "A-G binary tableau 3 qubits: initial Z_i/X_i rows, GHZ generators "
            "{XXX, ZZI, ZIZ}, cluster {XZI, ZXZ, IZX}, all stabilizer pairs "
            "commute, destabilizer/stabilizer pairs anticommute, all 6 "
            "generators verified +1 on simulated states",
        ],
    }
