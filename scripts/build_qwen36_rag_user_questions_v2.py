#!/usr/bin/env python3
"""Build the user-facing Qwen3.6-27B-RAG benchmark v2.

The benchmark is intentionally concrete: every question includes expected
source substrings and answer terms so retrieval and answer quality can be
judged without subjective reading. A large subset of the coding questions is
also pinned to exact input/output checks from the repo's unit-test tasks.
"""

from __future__ import annotations

import json
from pathlib import Path


OUTPUT = Path("evals/benchmarks/qwen36_27b_user_rag_questions_v2.json")


def item(
    id_: str,
    category: str,
    query: str,
    sources: list[str],
    terms: list[str],
    *,
    minimum: int = 3,
    coding: bool = False,
    answer_requirements: list[str] | None = None,
    unit_test_file: str | None = None,
    example_io: list[str] | None = None,
) -> dict[str, object]:
    if len(query.split()) < 8:
        query = f"For a quantum coding task, {query[0].lower()}{query[1:]}"
    if coding and "must include these check points" not in query:
        query = (
            f"{query} The answer must include these check points: "
            f"{'; '.join(terms[:3])}."
        )
    judge_type = "unit_test_backed" if unit_test_file else "source_and_terms"
    entry: dict[str, object] = {
        "id": id_,
        "category": category,
        "coding_problem": coding,
        "judge_type": judge_type,
        "query": query,
        "expected_source_substrings": sources,
        "expected_terms": terms,
        "minimum_term_hits": minimum,
        "answer_requirements": answer_requirements or terms[:minimum],
        "judge": (
            "Pass if the answer cites one expected source and includes at least "
            f"{minimum} of the expected terms exactly or with equivalent code syntax."
        ),
    }
    if unit_test_file:
        entry["unit_test_file"] = unit_test_file
        entry["judge"] = (
            "Pass if the answer cites one expected source, includes the required terms, "
            f"and gives code or steps that satisfy {unit_test_file}."
        )
    if example_io:
        entry["example_io"] = example_io
    return entry


def build_items() -> list[dict[str, object]]:
    qiskit = "docs/quantum_libraries/qiskit_basics.md"
    cirq = "docs/quantum_libraries/cirq_basics.md"
    pennylane = "docs/quantum_libraries/pennylane_basics.md"
    braket = "docs/quantum_libraries/braket_basics.md"
    arclight = "docs/external/quantum-sdk-docs-latest/arclight-isq/"
    gates = "docs/quantum_libraries/quantum_gates_reference.md"
    repair = "docs/quantum_libraries/circuit_repair_recipes.md"
    state_vector = "docs/quantum_libraries/state_vector_simulation.md"
    density = "docs/quantum_libraries/density_matrix_partial_trace.md"
    density_api = "docs/quantum_libraries/density_matrix_eval_api.md"
    depol = "docs/quantum_libraries/depolarizing_channel.md"
    qft = "docs/quantum_libraries/quantum_fourier_transform.md"
    qpe = "docs/quantum_libraries/quantum_phase_estimation.md"
    grover = "docs/quantum_libraries/grover_search.md"
    vqe = "docs/quantum_libraries/vqe_basics.md"
    qaoa = "docs/quantum_libraries/qaoa_maxcut.md"
    bell = "docs/quantum_libraries/bell_state_construction.md"
    ghz = "docs/quantum_libraries/ghz_state.md"
    teleport = "docs/quantum_libraries/quantum_teleportation.md"
    superdense = "docs/quantum_libraries/superdense_coding.md"
    error = "docs/quantum_libraries/error_correction_basics.md"
    stabilizer = "docs/quantum_libraries/stabilizer_formalism.md"
    trotter = "docs/quantum_libraries/trotter_decomposition.md"
    decoders = "docs/quantum_libraries/binary_measurement_decoders.md"

    items = [
        item("arclight_install_binary_tarball", "install", "How do I install Arclight ISQ with the Binary Tarball path, and what exact command verifies the compiler?", [arclight], ["Binary Tarball", "unshare --user --pid echo YES", "sha256sum -c", "./isqc --version"], minimum=3),
        item("arclight_install_nix_flake", "install", "For Arclight ISQ, show the Nix Flake install route and the command that checks isqc is on PATH.", [arclight], ["Nix Flake", "cachix use arclight-quantum", "nix shell github:isQ-Team/isQ-Compiler", "isqc --version"], minimum=3),
        item("arclight_install_docker", "install", "For Arclight ISQ, what Docker Container commands are documented for Ubuntu and binary-only images?", [arclight], ["Docker Container", "arclightquantum/isqc:ubuntu-0.0.1", "arclightquantum/isqc:0.0.1", "isqc --version"], minimum=3),
        item("qiskit_bell_aer_counts", "sdk_api", "In Qiskit v1.x, write a 2-qubit Bell circuit, measure both qubits, run AerSimulator for shots=1024, and retrieve counts.", [qiskit], ["QuantumCircuit", "qc.h(0)", "qc.cx(0, 1)", "AerSimulator", "get_counts"], minimum=4),
        item("qiskit_statevector_index_rule", "sdk_api", "In Qiskit, explain the Statevector index rule and the measured bitstring rightmost-character gotcha.", [qiskit], ["Statevector", "rightmost", "little-endian", "sum_i", "2^i"], minimum=4),
        item("qiskit_operator_unitary", "sdk_api", "Which Qiskit import and call returns the matrix of a unitary circuit?", [qiskit], ["Operator", "Operator(qc).data", "from qiskit.quantum_info", "unitary"], minimum=3),
        item("qiskit_transpile_aer", "sdk_api", "For Qiskit Aer sampling, what exact transpile-and-run pattern should I use before result.get_counts?", [qiskit], ["transpile", "AerSimulator", "sim.run", "shots=1024", "result.get_counts"], minimum=4),
        item("qiskit_measure_register_order", "sdk_api", "In Qiskit, show the exact call for measuring qubits [0,1] into classical bits [0,1] and mention the register-order pitfall.", [qiskit], ["qc.measure([0, 1], [0, 1])", "classical-bit", "index order", "rightmost"], minimum=3),
        item("qiskit_common_gate_methods", "sdk_api", "List Qiskit QuantumCircuit method names for H, CX, CCX, SWAP, reset, barrier, and parameterized RX.", [qiskit], [".h(q)", ".cx(c, t)", ".ccx(c1, c2, t)", ".swap(a, b)", ".rx(theta, q)"], minimum=4),
        item("qiskit_angles_radians", "sdk_api", "What Qiskit pitfall should I remember for parameterized gate angles such as 90 degrees?", [qiskit], ["radians", "pi", "parameterised gates", "90 degrees"], minimum=3),
        item("qiskit_partial_trace_import", "sdk_api", "What Qiskit import surface should I use for Statevector, Operator, and partial_trace?", [qiskit], ["Statevector", "Operator", "partial_trace", "qiskit.quantum_info"], minimum=3),
        item("qiskit_vqe_imports", "sdk_api", "For a Qiskit VQE workflow, name the documented imports for VQE, COBYLA, and RealAmplitudes.", [vqe, qiskit], ["VQE", "COBYLA", "RealAmplitudes", "qiskit_algorithms"], minimum=3),
        item("cirq_line_qubit_bell", "sdk_api", "In Cirq, create three LineQubits and a circuit with H(q0), CNOT(q0,q1), CNOT(q1,q2).", [cirq], ["cirq.LineQubit.range", "cirq.Circuit", "cirq.H(q0)", "cirq.CNOT(q0, q1)", "cirq.CNOT(q1, q2)"], minimum=4),
        item("cirq_sampling_histogram", "sdk_api", "In Cirq, sample q0/q1/q2 with key='m' for repetitions=1024 and print the histogram.", [cirq], ["cirq.Simulator", "cirq.measure", "key=\"m\"", "repetitions=1024", "histogram"], minimum=4),
        item("cirq_statevector_simulation", "sdk_api", "In Cirq, what call simulates a circuit and where is the final state vector stored?", [cirq], ["cirq.Simulator", "sim.simulate", "final_state_vector", "result"], minimum=3),
        item("cirq_endianness_index", "sdk_api", "What is Cirq's big-endian state-vector index formula for listed qubits?", [cirq], ["big-endian", "sum_i", "2^(n-1-i)", "first qubit"], minimum=3),
        item("cirq_grid_qubit_topology", "sdk_api", "When should I prefer Cirq GridQubit(row, col), and what problem does it model?", [cirq], ["cirq.GridQubit(row, col)", "hardware-realistic", "topologies"], minimum=2),
        item("cirq_unitary_pitfall", "sdk_api", "What limitation should I remember before calling cirq.unitary(circuit)?", [cirq], ["cirq.unitary(circuit)", "unitary", "no measurement", "operations"], minimum=3),
        item("cirq_gate_names", "sdk_api", "List the Cirq symbols for RX, RY, RZ, CNOT, CZ, SWAP, ISWAP, TOFFOLI, and CSWAP.", [cirq], ["cirq.rx(theta)", "cirq.ry(theta)", "cirq.rz(theta)", "cirq.CNOT", "cirq.TOFFOLI"], minimum=4),
        item("cirq_insert_strategy", "sdk_api", "What Cirq InsertStrategy is mentioned when operation ordering matters inside Circuit construction?", [cirq], ["cirq.Circuit", "moments", "cirq.InsertStrategy.NEW_THEN_INLINE", "order"], minimum=3),
        item("pennylane_minimal_qnode", "sdk_api", "Show the minimal PennyLane QNode pattern with qml.device, @qml.qnode, RY, CNOT, and qml.expval.", [pennylane], ["qml.device", "@qml.qnode", "qml.RY", "qml.CNOT", "qml.expval"], minimum=4),
        item("pennylane_trainable_parameter", "sdk_api", "In PennyLane, what exact array form is needed so a parameter is trainable?", [pennylane], ["pennylane.numpy", "requires_grad=True", "trainable", "plain numpy"], minimum=3),
        item("pennylane_return_types", "sdk_api", "Name the documented PennyLane QNode return types for state, probabilities, expectation, and sampling.", [pennylane], ["qml.state()", "qml.probs", "qml.expval", "qml.sample"], minimum=4),
        item("pennylane_device_shots", "sdk_api", "For PennyLane shots-based sampling, what device argument should I set instead of relying on analytic default?", [pennylane], ["qml.device", "shots=1024", "default.qubit", "analytically"], minimum=3),
        item("pennylane_hamiltonian", "sdk_api", "Show the PennyLane Hamiltonian pattern with coeffs and observables including PauliZ @ PauliZ.", [pennylane], ["qml.Hamiltonian", "coeffs", "observables", "qml.PauliZ(0) @ qml.PauliZ(1)"], minimum=3),
        item("pennylane_qaoa_maxcut_helpers", "sdk_api", "Which PennyLane helper builds MaxCut cost and mixer Hamiltonians from a graph?", [pennylane], ["from pennylane import qaoa", "qaoa.maxcut", "cost_h", "mixer_h"], minimum=3),
        item("pennylane_templates", "sdk_api", "List PennyLane templates named in the notes for embedding, entanglers, QFT, and phase estimation.", [pennylane], ["qml.AngleEmbedding", "qml.BasicEntanglerLayers", "qml.StronglyEntanglingLayers", "qml.QFT", "qml.QuantumPhaseEstimation"], minimum=4),
        item("pennylane_multiwire_gate", "sdk_api", "What PennyLane pitfall is documented for multi-wire gates such as CNOT or SWAP?", [pennylane], ["wires=[0, 1]", "multi-wire", "tuple", "brittle"], minimum=3),
        item("pennylane_vqe_workflow", "sdk_api", "For PennyLane VQE, name the ansatz/QNode/optimizer pieces documented in the VQE note.", [vqe, pennylane], ["qml.SimplifiedTwoDesign", "qml.QNode", "qml.AdamOptimizer", "0.05"], minimum=3),
        item("braket_bell_local_counts", "sdk_api", "In Amazon Braket, build a Bell circuit and run LocalSimulator for shots=1024 to get measurement_counts.", [braket], ["Circuit().h(0).cnot", "measure([0, 1])", "LocalSimulator", "shots=1024", "measurement_counts"], minimum=4),
        item("braket_state_vector_result", "sdk_api", "In Braket LocalSimulator, what must I add to request state_vector amplitudes and what shots value should I use?", [braket], ["state_vector()", "shots=0", "result.values[0]", "analytical"], minimum=3),
        item("braket_endianness", "sdk_api", "What endianness does Braket use for bitstrings, and which qubit is most significant?", [braket], ["big-endian", "qubit 0", "most significant bit", "bitstring"], minimum=3),
        item("braket_remote_vs_local", "sdk_api", "When should I prefer Braket LocalSimulator instead of AwsDevice in this project?", [braket], ["AwsDevice", "AWS credentials", "LocalSimulator", "local testing"], minimum=3),
        item("braket_gate_methods", "sdk_api", "List Braket chainable gate methods for rx, ry, rz, cnot, cz, swap, and ccnot.", [braket], [".rx(q, theta)", ".ry(q, theta)", ".rz(q, theta)", ".cnot(control, target)", ".ccnot(control1, control2, target)"], minimum=4),
        item("bell_phi_plus_amplitudes", "algorithm", "For a coding answer, return the exact |Phi+> Bell pair amplitude list in basis |00>,|01>,|10>,|11>.", [bell], ["2 ** -0.5", "[amp, 0.0, 0.0, amp]", "|Phi+>", "basis"], minimum=3, coding=True),
        item("bell_reference_circuit", "algorithm", "What two gate steps create the default Bell pair |Phi+>, and what are the Qiskit calls?", [bell], ["H to qubit 0", "CNOT", "qc.h(0)", "qc.cx(0, 1)"], minimum=3, coding=True),
        item("ghz_state_list", "algorithm", "For n=3, what exact GHZ amplitude list should a coding task return under big-endian indexing?", [ghz], ["2 ** -0.5", "ghz3", "state[0]", "state[(1 << n) - 1]"], minimum=3, coding=True),
        item("ghz_witness_expectation", "algorithm", "How do I compute a GHZ witness expectation and what sign indicates entanglement?", [ghz], ["W = 1/2 I - |GHZ><GHZ|", "0.5 - fidelity", "negative", "entanglement"], minimum=3, coding=True),
        item("qft_phase_pattern", "algorithm", "For QFT|x>, what phase formula should tests expect for phases[k]?", [qft], ["2 * pi * x * k / N", "mod 2*pi", "phases[k]", "QFT"], minimum=3, coding=True),
        item("qft_matrix_formula", "algorithm", "What is the QFT matrix element formula and a NumPy construction pattern?", [qft], ["exp(2*pi*i * j*k / N)", "1 / sqrt(N)", "np.meshgrid", "qft_matrix"], minimum=3, coding=True),
        item("qft_inverse_steps", "algorithm", "How do I invert a QFT circuit in code?", [qft], ["reverse the order", "negate all rotation angles", "QFT_dagger", "inverse"], minimum=3, coding=True),
        item("qpe_measurement_integer", "algorithm", "In ideal QPE, what integer y is measured and how do I convert it back to phase?", [qpe], ["round(true_phase * (1 << t))", "% (1 << t)", "y / 2**t", "phi_estimate"], minimum=3, coding=True),
        item("qpe_protocol_order", "algorithm", "List the QPE protocol order: counting register preparation, controlled powers, inverse QFT, and measurement.", [qpe], ["H on each", "controlled-U^(2^k)", "inverse QFT", "Measure"], minimum=4, coding=True),
        item("qpe_eigenvalue_numpy", "algorithm", "How does the note estimate the eigenvalue phase from U and an eigenvector using NumPy?", [qpe], ["Uv = unitary @ eigenvector", "np.vdot", "np.angle", "np.exp(2j * np.pi * phi_est)"], minimum=3, coding=True),
        item("grover_oracle_diffusion", "algorithm", "For a pure Python Grover simulator, define the oracle sign flip and diffusion update.", [grover], ["flip the sign", "marked", "2 * mean - a", "uniform superposition"], minimum=3, coding=True),
        item("grover_iteration_count", "algorithm", "What approximate Grover iteration count should I use for N items and M marked items?", [grover], ["(pi/4)", "sqrt(N / M)", "O(sqrt(N))", "marked"], minimum=3),
        item("vqe_energy_expectation", "algorithm", "For VQE, what exact NumPy expression computes E(theta)=<psi|H|psi>?", [vqe], ["np.vdot(state, hamiltonian @ state)", "np.real", "expectation", "ground-state energy"], minimum=3, coding=True),
        item("vqe_workflow_steps", "algorithm", "List the VQE workflow steps from Hamiltonian Pauli strings through optimizer.", [vqe], ["sum_i c_i P_i", "ansatz", "measurement basis", "COBYLA", "SPSA"], minimum=4),
        item("qaoa_layer_pattern", "algorithm", "In a QAOA layer, what Qiskit gate pattern implements each weighted edge and mixer rotation?", [qaoa], ["qc.cx(u, v)", "qc.rz(2 * w * gamma, v)", "qc.rx(2 * beta, q)", "Cost unitary", "Mixer unitary"], minimum=4, coding=True),
        item("qaoa_maxcut_cost", "algorithm", "For MaxCut coding, when does an edge (u,v) contribute 1 to maxcut_cost(bitstring, edges)?", [qaoa, "evals/tasks/quantum/qaoa_maxcut/"], ["bitstring[u] != bitstring[v]", "cost += 1", "edges", "MaxCut"], minimum=3, coding=True),
        item("teleportation_corrections_table", "algorithm", "Return the teleportation correction table for (m1,m2) -> I, X, Z, ZX.", [teleport], ["(0, 0): \"I\"", "(0, 1): \"X\"", "(1, 0): \"Z\"", "(1, 1): \"ZX\""], minimum=4, coding=True),
        item("teleportation_apply_order", "algorithm", "In the teleport(alpha,beta,m1,m2) snippet, which bit controls X and which controls Z?", [teleport], ["if m2 == 1", "X", "if m1 == 1", "Z"], minimum=4, coding=True),
        item("superdense_encode_table", "algorithm", "For superdense coding with Alice as qubit 0, give the encode table for 00,01,10,11.", [superdense], ["00 -> I", "01 -> X", "10 -> Z", "11 -> ZX"], minimum=4, coding=True),
        item("superdense_bell_measurement", "algorithm", "What Bob-side Bell-basis measurement gates recover the two classical bits in superdense coding?", [superdense], ["CNOT(0, 1)", "H(0)", "Bell-basis measurement", "recover"], minimum=3, coding=True),
        item("density_plain_python_api", "algorithm", "For the density-matrix eval API, name the four public functions and say whether NumPy is allowed.", [density, density_api], ["density_from_state", "tensor_product", "partial_trace", "purity", "Do not import NumPy"], minimum=4, coding=True),
        item("density_partial_trace_b", "algorithm", "In partial_trace(rho, dim_a, dim_b, trace_out), what loops compute tracing out subsystem B?", [density, density_api], ["trace_out == \"B\"", "dim_a x dim_a", "rho[i * dim_b + k][j * dim_b + k]", "return reduced"], minimum=3, coding=True),
        item("density_partial_trace_a", "algorithm", "In partial_trace, what output shape and index formula are used when trace_out is 'A'?", [density, density_api], ["trace_out == \"A\"", "dim_b x dim_b", "rho[i * dim_b + k][i * dim_b + l]", "ValueError"], minimum=3, coding=True),
        item("depolarizing_channel_formula", "algorithm", "For a single-qubit depolarizing channel, give both E(rho) formulas in the notes.", [depol], ["(1 - p) * rho + p * I / 2", "1 - 3p/4", "p/4", "X rho X"], minimum=3, coding=True),
        item("depolarizing_kraus", "algorithm", "Write the Kraus coefficient pattern for depolarizing_kraus(p).", [depol], ["np.sqrt(1 - 3 * p / 4)", "np.sqrt(p / 4)", "I", "X", "Y", "Z"], minimum=4, coding=True),
        item("bitflip_syndrome_decoder", "algorithm", "For the 3-qubit bit-flip code, return the syndrome lookup table for (s1,s2).", [error, decoders], ["(0, 0): None", "(1, 0): 0", "(1, 1): 1", "(0, 1): 2"], minimum=4, coding=True),
        item("shor9_encoded_states", "algorithm", "What are the |0_L> and |1_L> encoded state formulas for Shor 9-qubit code?", [error], ["1/(2*sqrt(2))", "|000> + |111>", "|000> - |111>", "three blocks"], minimum=3),
        item("stabilizer_h_update", "algorithm", "In tableau simulation, what is the H update rule including the sign flip condition?", [stabilizer], ["swap x_q and z_q", "x & z", "sign", "pre-update"], minimum=3, coding=True),
        item("stabilizer_s_update", "algorithm", "In tableau simulation, what is the S update rule for z_q and sign?", [stabilizer], ["z_q ^= x_q", "flip sign", "x_q AND z_q", "apply_s"], minimum=3, coding=True),
        item("stabilizer_cnot_update", "algorithm", "In tableau simulation, give the CNOT update formulas for x_t, z_c, and sign.", [stabilizer], ["x_t ^= x_c", "z_c ^= z_t", "xc & zt", "xt ^ zc ^ 1"], minimum=3, coding=True),
        item("trotter_first_order", "algorithm", "Give the first-order Trotter formula for exp(-i(A+B)t) and the dt pattern.", [trotter], ["exp(-i A t/n)", "exp(-i B t/n)", "dt = t / n_steps", "matrix_power"], minimum=3, coding=True),
        item("trotter_second_order", "algorithm", "Give the second-order symmetric Trotter formula S2(t).", [trotter], ["exp(-i A t/2)", "exp(-i B t)", "exp(-i A t/2)", "O(t^3 / n^2)"], minimum=3),
        item("gate_alias_normalization_table", "algorithm", "For gate alias normalization, what lookup entries canonicalize hadamard, pauli_x, cnot, toffoli, and fredkin?", [gates], ["hadamard", "\"H\"", "pauli_x", "\"X\"", "toffoli"], minimum=4, coding=True),
        item("gate_unknown_error", "algorithm", "What should gate normalization do for an unknown alias instead of returning the original token?", [gates], ["gate.strip().lower()", "ValueError", "unknown gate", "lookup"], minimum=3, coding=True),
        item("state_vector_single_qubit_apply", "algorithm", "In pure NumPy state-vector simulation, what reshape/tensordot/moveaxis pattern applies a single-qubit gate?", [state_vector], ["reshape([2] * n)", "np.tensordot", "np.moveaxis", "target"], minimum=3, coding=True),
        item("state_vector_measurement_probs", "algorithm", "How do I compute measurement probabilities and sample outcomes from a state vector?", [state_vector], ["np.abs(state) ** 2", "rng.choice", "shots", "p=probs"], minimum=3, coding=True),
        item("circuit_repair_cnot_swapped", "repair", "In circuit repair, what symptom and fix are documented for swapped CNOT control/target?", [repair], ["Swapped control/target", "probabilities mirror", "control comes first", "cx(c, t)"], minimum=3, coding=True),
        item("circuit_repair_missing_h", "repair", "In Bell-basis measurement repair, what gate sequence is needed before measurement?", [repair], ["CX(0, 1)", "H(0)", "Bell-basis", "Missing H"], minimum=3, coding=True),
        item("circuit_repair_float_precision", "repair", "How should candidate code compare 1/sqrt(2) amplitudes in tests?", [repair, bell], ["math.isclose", "np.allclose", "abs_tol=1e-9", "exact equality"], minimum=3, coding=True),
    ]

    coding_tasks = [
        ("task_bell_pair_state", "bell_pair_construction", "Implement bell_pair_state() for the eval task and return the exact Phi+ list.", ["bell_pair_state", "2 ** -0.5", "[amp, 0.0, 0.0, amp]"]),
        ("task_measurement_mapping", "measurement_bug_repair", "Repair measurement_mapping(bitstring) where input ordering is q1q0; map the rightmost bit to q0.", ["measurement_mapping", "q1q0", "rightmost", "{\"q0\": int(bitstring[1])"]),
        ("task_phase_estimation_measurement", "phase_estimation_circuit", "Implement phase_estimation(eigenvalue_phase, n_counting_bits) with ideal rounded measurement modulo 2^n.", ["phase_estimation", "round(eigenvalue_phase * n_states)", "% n_states", "1 << n_counting_bits"]),
        ("task_phase_from_measurement", "phase_estimation_circuit", "Implement phase_from_measurement(measurement, n_counting_bits) returning measurement / 2^n.", ["phase_from_measurement", "measurement / n_states", "[0, 1)", "1 << n_counting_bits"]),
        ("task_qaoa_maxcut_cost", "qaoa_maxcut", "Implement maxcut_cost so an edge contributes only when the two endpoint bits differ.", ["maxcut_cost", "bitstring[u] != bitstring[v]", "cost += 1", "edges"]),
        ("task_qaoa_bruteforce", "qaoa_maxcut", "Implement brute_force_maxcut with lexicographically smallest tie-break.", ["brute_force_maxcut", "format(i", "best_cost", "lexicographically smallest"]),
        ("task_qaoa_landscape_sort", "qaoa_maxcut", "Implement qaoa_cost_landscape sorted by descending cost and ascending bitstring.", ["qaoa_cost_landscape", "results.sort", "-x[1]", "x[0]"]),
        ("task_grover_uniform", "grover_oracle_diffusion", "Implement uniform_superposition(n_qubits) with amplitude 1/sqrt(2^n).", ["uniform_superposition", "math.sqrt", "[amp] * n", "2 ** n_qubits"]),
        ("task_grover_oracle", "grover_oracle_diffusion", "Implement oracle(state, marked) by flipping only the marked basis amplitude sign.", ["oracle", "marked", "-result[marked]", "list(state)"]),
        ("task_grover_diffusion", "grover_oracle_diffusion", "Implement diffusion(state) as reflection about the mean amplitude.", ["diffusion", "mean = sum(state) / n", "2 * mean - a", "return"]),
        ("task_grover_search_loop", "grover_oracle_diffusion", "Implement grover_search by alternating oracle and diffusion for the requested iterations.", ["grover_search", "for _ in range(iterations)", "oracle", "diffusion"]),
        ("task_density_from_state", "density_matrix_partial_trace", "Implement density_from_state(state) as a plain-list outer product.", ["density_from_state", "state[i] * state[j]", "list[list[float]]", "rho"]),
        ("task_tensor_product", "density_matrix_partial_trace", "Implement tensor_product(a,b) using result[i*db+k][j*db+l] = a[i][j] * b[k][l].", ["tensor_product", "i * db + k", "j * db + l", "a[i][j] * b[k][l]"]),
        ("task_partial_trace_b", "density_matrix_partial_trace", "Implement partial_trace trace_out='B' returning the dim_a x dim_a reduced matrix.", ["partial_trace", "trace_out == \"B\"", "dim_a", "rho[i * dim_b + k][j * dim_b + k]"]),
        ("task_partial_trace_a", "density_matrix_partial_trace", "Implement partial_trace trace_out='A' returning the dim_b x dim_b reduced matrix.", ["trace_out == \"A\"", "dim_b", "rho[i * dim_b + k][i * dim_b + l]", "result"]),
        ("task_purity", "density_matrix_partial_trace", "Implement purity(rho) as Tr(rho^2) with nested loops over i,j.", ["purity", "rho[i][j] * rho[j][i]", "Tr(rho^2)", "total"]),
        ("task_shor_encode", "quantum_error_correction_shor_9qubit", "Implement shor_encode(logical_bit) with amplitudes at the 8 block combinations.", ["shor_encode", "1.0 / (2 * math.sqrt(2))", "block_states = [0, 7]", "512"]),
        ("task_shor_apply_x_error", "quantum_error_correction_shor_9qubit", "Implement apply_x_error(state, qubit) for qubit index 0-8 with MSB-first conversion.", ["apply_x_error", "8 - qubit", "i ^ (1 << bit)", "MSB"]),
        ("task_shor_decode_majority", "quantum_error_correction_shor_9qubit", "Implement Shor decode bit-flip correction by majority vote within each 3-qubit block.", ["shor_decode", "majority vote", "bin(b0).count", "corrected"]),
        ("task_shor_decode_phase", "quantum_error_correction_shor_9qubit", "Implement Shor decode logical bit by comparing amp_000 and amp_111 signs.", ["amp_000", "amp_111", "same sign", "opposite signs"]),
        ("task_teleportation_corrections", "teleportation_corrections", "Implement teleportation_corrections(m0,m1) where m0 controls X and m1 controls Z.", ["teleportation_corrections", "m0 controls the X", "m1 controls the Z", "ops.append"]),
        ("task_bitflip_decoder", "error_detection_bit_flip", "Implement the 3-qubit bit-flip syndrome decoder table for all four outcomes.", ["(0, 0): None", "(1, 0): 0", "(1, 1): 1", "(0, 1): 2"]),
        ("task_gate_alias_normalize", "gate_alias_normalization", "Implement normalize_gate so cnot maps to CX, toffoli maps to CCX, and unknown aliases raise ValueError.", ["normalize_gate", "cnot", "CX", "ValueError"]),
        ("task_gate_casefold_barrier", "gate_alias_casefold_barrier", "Implement gate alias casefolding with strip().lower() and preserve barrier handling if present.", ["strip().lower()", "barrier", "casefold", "ValueError"]),
        ("task_gate_registry_cleanup", "gate_alias_registry_cleanup", "Clean a gate alias registry so aliases map to canonical H, X, CX, CCX, CSWAP symbols.", ["alias", "canonical", "CCX", "CSWAP"]),
        ("task_gate_token_canonicalizer", "gate_token_canonicalizer", "Implement a token canonicalizer that normalizes whitespace/case and raises on unknown gates.", ["canonicalizer", "strip", "lower", "unknown"]),
        ("task_superdense_encode", "superdense_coding", "Implement superdense coding encode table: 00 I, 01 X, 10 Z, 11 ZX.", ["superdense", "00", "I", "ZX"]),
        ("task_superdense_identity_lookup", "superdense_identity_lookup", "Return the canonical 4-row superdense identity lookup table without inventing formulas.", ["identity lookup", "(0, 0)", "(1, 1)", "ZX"]),
        ("task_superdense_pauli_router", "superdense_pauli_router", "Implement the Pauli router for 2-bit superdense messages with I/X/Z/Y or ZX convention.", ["PAULI_ROUTER", "(0, 1): \"X\"", "(1, 0): \"Z\"", "(1, 1)"]),
        ("task_pauli_message_codec", "pauli_message_codec", "Implement a Pauli message codec mapping two classical bits to I, X, Z, or Y/ZX.", ["Pauli", "I", "X", "Z", "Y"]),
        ("task_binary_measurement_decoder", "binary_measurement_decoder", "Implement Bell and syndrome binary measurement decoders with pinned bit order.", ["BELL_LABELS", "SYNDROMES", "(m1, m2)", "not swappable"]),
        ("task_phase_measurement_register", "phase_measurement_register", "Implement phase measurement register parsing without bit-reversing the expected integer.", ["phase", "measurement", "register", "bit-reversed"]),
        ("task_phase_register_roundtrip", "phase_register_roundtrip", "Implement phase register encode/decode roundtrip for fixed counting bits.", ["phase_register", "roundtrip", "counting bits", "measurement"]),
        ("task_qft_phase_pattern", "qft_phase_pattern", "Implement QFT phase pattern phases[k] = 2*pi*x*k/N mod 2*pi.", ["phases[k]", "2 * pi * x * k / N", "mod", "2*pi"]),
        ("task_circuit_phase_repair", "circuit_phase_repair", "Repair phase comparisons by reducing phases modulo 2*pi before allclose.", ["np.mod", "2 * np.pi", "np.allclose", "phase"]),
        ("task_circuit_depth_optimization", "circuit_depth_optimization", "Optimize a gate sequence by canceling adjacent self-inverse gates and merging rotations.", ["HH", "XX", "CNOT-CNOT", "Rz(a+b)"]),
        ("task_stabilizer_tableau_update", "stabilizer_tableau_update_repair", "Repair stabilizer tableau H/S/CNOT updates using pre-update sign bits.", ["apply_h", "apply_s", "apply_cnot", "pre-update"]),
        ("task_quantum_channel_depolarizing", "quantum_channel_depolarizing", "Implement depolarizing Kraus operators and apply_channel with K @ rho @ K.conj().T.", ["depolarizing", "Kraus", "K @ rho @ K.conj().T", "CPTP"]),
        ("task_trotterized_evolution", "trotterized_hamiltonian_evolution", "Implement trotter_step and trotter_evolve using dt=t/n_steps and matrix_power.", ["trotter_step", "trotter_evolve", "dt = t / n_steps", "matrix_power"]),
        ("task_vqe_energy_minimization", "vqe_energy_minimization", "Implement VQE energy minimization helper around expectation <psi|H|psi>.", ["VQE", "expectation", "np.vdot", "minimise"]),
        ("task_bitstring_maxcut_landscape", "bitstring_maxcut_landscape", "Implement bitstring MaxCut landscape over all 2^n assignments with deterministic sorting.", ["bitstring", "MaxCut", "2^n", "sorting"]),
        ("task_maxcut_assignment_enumerator", "maxcut_assignment_enumerator", "Enumerate all MaxCut assignments as zero-padded bitstrings.", ["enumerate", "format", "bitstrings", "MaxCut"]),
        ("task_maxcut_partition_ranker", "maxcut_partition_ranker", "Rank MaxCut partitions by cut value with deterministic tie-breaks.", ["rank", "partition", "cut value", "tie"]),
        ("task_ghz_state_witness", "ghz_state_witness", "Implement GHZ state and witness returning negative value for the perfect GHZ state.", ["GHZ", "witness", "0.5 - fidelity", "negative"]),
        ("task_quantum_circuit_construction", "bell_pair_construction", "For a code task, choose one endianness convention and construct the Bell pair without markdown fences.", ["endianness", "Bell pair", "candidate.py", "no markdown"]),
    ]
    for id_, task_dir, query, terms in coding_tasks:
        concrete_query = (
            f"{query} The answer must include these check points: "
            f"{'; '.join(terms[:3])}."
        )
        items.append(
            item(
                id_,
                "quantum_coding_task",
                concrete_query,
                [f"evals/tasks/quantum/{task_dir}/", repair, f"docs/quantum_libraries/"],
                terms,
                minimum=min(3, len(terms)),
                coding=True,
            )
        )

    concrete_coding_tasks = [
        (
            "concrete_bell_phi_plus_state",
            "bell_pair_construction",
            "Write bell_pair_state(); the unit test expects length 4 and amplitudes [1/sqrt(2), 0, 0, 1/sqrt(2)] in |00>, |01>, |10>, |11> order.",
            ["bell_pair_state", "len(state) == 4", "2 ** -0.5", "[amp, 0.0, 0.0, amp]"],
            ["bell_pair_state() -> [0.70710678..., 0.0, 0.0, 0.70710678...]"],
        ),
        (
            "concrete_measurement_q1q0_mapping",
            "measurement_bug_repair",
            "Repair measurement_mapping(bitstring): for input ordering q1q0, bitstring '10' must map q1=1 and q0=0.",
            ["measurement_mapping", "bitstring[1]", "q0", "q1"],
            ["measurement_mapping('10') -> {'q0': 0, 'q1': 1}"],
        ),
        (
            "concrete_phase_estimation_rounding_cases",
            "phase_estimation_circuit",
            "Implement phase_estimation(phi, n_bits) so phi=0.25,n_bits=3 returns 2; phi=0.75,n_bits=4 returns 12; phi=1/3,n_bits=3 returns 3.",
            ["phase_estimation", "round", "1 << n_bits", "% n_states"],
            ["phase_estimation(0.25, 3) -> 2", "phase_estimation(0.75, 4) -> 12", "phase_estimation(1/3, 3) -> 3"],
        ),
        (
            "concrete_phase_from_measurement_roundtrip",
            "phase_estimation_circuit",
            "Implement phase_from_measurement(m, n_bits) so measurement 4 with 3 counting bits returns 0.5 and exact phases round-trip.",
            ["phase_from_measurement", "measurement / n_states", "1 << n_bits", "round-trip"],
            ["phase_from_measurement(4, 3) -> 0.5"],
        ),
        (
            "concrete_qaoa_triangle_costs",
            "qaoa_maxcut",
            "Implement maxcut_cost for triangle edges [(0,1),(1,2),(0,2)]: '000' returns 0, '010' returns 2, and '100' returns 2.",
            ["maxcut_cost", "bitstring[u] != bitstring[v]", "'010'", "2"],
            ["maxcut_cost('000', triangle) -> 0", "maxcut_cost('010', triangle) -> 2", "maxcut_cost('100', triangle) -> 2"],
        ),
        (
            "concrete_qaoa_line_costs",
            "qaoa_maxcut",
            "Implement maxcut_cost for line edges [(0,1),(1,2),(2,3)]: '0101' returns 3 and '0011' returns 1.",
            ["line_edges", "'0101'", "3", "'0011'"],
            ["maxcut_cost('0101', line_edges) -> 3", "maxcut_cost('0011', line_edges) -> 1"],
        ),
        (
            "concrete_qaoa_landscape_sorting",
            "qaoa_maxcut",
            "Implement qaoa_cost_landscape for a 3-node triangle so it returns 8 rows sorted by descending cost, with top cost 2 and bottom cost 0.",
            ["qaoa_cost_landscape", "len(landscape) == 8", "sorted", "reverse=True"],
            ["qaoa_cost_landscape(3, triangle)[0][1] -> 2", "qaoa_cost_landscape(3, triangle)[-1][1] -> 0"],
        ),
        (
            "concrete_grover_uniform_two_qubits",
            "grover_oracle_diffusion",
            "Implement uniform_superposition(2): the test expects four amplitudes, each exactly 0.5 within tolerance.",
            ["uniform_superposition", "2 ** n_qubits", "1.0 / math.sqrt(4)", "0.5"],
            ["uniform_superposition(2) -> [0.5, 0.5, 0.5, 0.5]"],
        ),
        (
            "concrete_grover_oracle_marked3",
            "grover_oracle_diffusion",
            "Implement oracle(state, marked) so oracle([0.5,0.5,0.5,0.5], 3) returns [0.5,0.5,0.5,-0.5].",
            ["oracle", "marked", "-0.5", "list(state)"],
            ["oracle([0.5, 0.5, 0.5, 0.5], 3) -> [0.5, 0.5, 0.5, -0.5]"],
        ),
        (
            "concrete_grover_diffusion_exact",
            "grover_oracle_diffusion",
            "Implement diffusion(state): for [0.5,0.5,0.5,-0.5], mean=0.25 and the output must be [0,0,0,1].",
            ["diffusion", "mean = sum(state) / n", "2 * mean - a", "[0.0, 0.0, 0.0, 1.0]"],
            ["diffusion([0.5, 0.5, 0.5, -0.5]) -> [0.0, 0.0, 0.0, 1.0]"],
        ),
        (
            "concrete_grover_search_two_qubits",
            "grover_oracle_diffusion",
            "Implement grover_search for n_qubits=2, marked=3, iterations=1 so the marked-state probability is 1.0.",
            ["grover_search", "marked=3", "iterations=1", "probability"],
            ["sum amplitude^2 is 1", "result_state[3] ** 2 -> 1.0"],
        ),
        (
            "concrete_density_zero_state",
            "density_matrix_partial_trace",
            "Implement density_from_state([1,0]) so it returns [[1,0],[0,0]] as a plain Python nested list.",
            ["density_from_state", "[[1.0, 0.0], [0.0, 0.0]]", "plain Python", "outer product"],
            ["density_from_state([1.0, 0.0]) -> [[1.0, 0.0], [0.0, 0.0]]"],
        ),
        (
            "concrete_density_plus_state",
            "density_matrix_partial_trace",
            "Implement density_from_state for |+>: input [1/sqrt(2),1/sqrt(2)] must return all four matrix entries as 0.5.",
            ["density_from_state", "1 / math.sqrt(2)", "0.5", "[[0.5, 0.5], [0.5, 0.5]]"],
            ["density_from_state([1/sqrt(2), 1/sqrt(2)]) -> [[0.5, 0.5], [0.5, 0.5]]"],
        ),
        (
            "concrete_tensor_product_01",
            "density_matrix_partial_trace",
            "Implement tensor_product so |0><0| tensor |1><1| produces a 4x4 matrix with the only 1.0 at row 1 column 1.",
            ["tensor_product", "i * db + k", "j * db + l", "expected_tp"],
            ["tensor_product(|0><0|, |1><1|)[1][1] -> 1.0"],
        ),
        (
            "concrete_partial_trace_product_b",
            "density_matrix_partial_trace",
            "Implement partial_trace for trace_out='B': tracing B from |01><01| must return |0><0|.",
            ["partial_trace", "trace_out == \"B\"", "[[1.0, 0.0], [0.0, 0.0]]", "dim_a"],
            ["partial_trace(tp, 2, 2, trace_out='B') -> [[1.0, 0.0], [0.0, 0.0]]"],
        ),
        (
            "concrete_partial_trace_bell_b",
            "density_matrix_partial_trace",
            "Implement partial_trace for a Bell density matrix: tracing out B must return the maximally mixed matrix [[0.5,0],[0,0.5]].",
            ["Bell", "trace_out=\"B\"", "maximally mixed", "[[0.5, 0.0], [0.0, 0.5]]"],
            ["partial_trace(rho_bell, 2, 2, trace_out='B') -> [[0.5, 0.0], [0.0, 0.5]]"],
        ),
        (
            "concrete_purity_values",
            "density_matrix_partial_trace",
            "Implement purity(rho): |0><0| and Bell rho must return 1.0; I/2 and the reduced Bell state must return 0.5.",
            ["purity", "rho[i][j] * rho[j][i]", "1.0", "0.5"],
            ["purity(|0><0|) -> 1.0", "purity(I/2) -> 0.5"],
        ),
        (
            "concrete_shor_x_error_msb",
            "quantum_error_correction_shor_9qubit",
            "Implement apply_x_error(state, qubit) for qubits 0..8 using MSB-first mapping, so the bit index is 8 - qubit.",
            ["apply_x_error", "8 - qubit", "i ^ (1 << bit)", "MSB"],
            ["qubit 0 flips the most significant bit", "qubit 8 flips the least significant bit"],
        ),
        (
            "concrete_shor_decode_majority",
            "quantum_error_correction_shor_9qubit",
            "Implement Shor bit-flip correction by majority vote inside each 3-qubit block before logical phase decoding.",
            ["shor_decode", "majority", "3-qubit block", "corrected"],
            ["each block is decoded by majority vote"],
        ),
        (
            "concrete_teleportation_all_bits",
            "teleportation_corrections",
            "Implement teleportation_corrections(m0,m1): (0,0)->[], (1,0)->['X'], (0,1)->['Z'], (1,1)->['Z','X']; invalid bits raise ValueError.",
            ["teleportation_corrections", "(1, 0): [\"X\"]", "(0, 1): [\"Z\"]", "ValueError"],
            ["teleportation_corrections(1, 1) -> ['Z', 'X']", "teleportation_corrections(0, 2) raises ValueError"],
        ),
        (
            "concrete_bitflip_syndrome_table",
            "error_detection_bit_flip",
            "Implement the 3-qubit bit-flip syndrome decoder: (0,0)->None, (1,0)->0, (1,1)->1, and (0,1)->2.",
            ["(0, 0): None", "(1, 0): 0", "(1, 1): 1", "(0, 1): 2"],
            ["decode_syndrome(1, 1) -> 1"],
        ),
        (
            "concrete_gate_alias_cnot_unknown",
            "gate_alias_normalization",
            "Implement normalize_gate so 'cnot' maps to 'CX', 'toffoli' maps to 'CCX', and unknown aliases raise ValueError.",
            ["normalize_gate", "cnot", "CX", "ValueError"],
            ["normalize_gate('cnot') -> 'CX'", "normalize_gate('toffoli') -> 'CCX'", "normalize_gate('???') raises ValueError"],
        ),
        (
            "concrete_gate_casefold_barrier",
            "gate_alias_casefold_barrier",
            "Implement gate alias normalization with strip().lower(): ' Hadamard ' maps to H and barrier handling is preserved.",
            ["strip().lower()", "Hadamard", "H", "barrier"],
            ["normalize_gate(' Hadamard ') -> 'H'", "normalize_gate('barrier') keeps barrier behavior"],
        ),
        (
            "concrete_superdense_encode_table",
            "superdense_coding",
            "Implement the superdense encode table exactly: '00'->I, '01'->X, '10'->Z, and '11'->ZX.",
            ["superdense", "'00': 'I'", "'01': 'X'", "'11': 'ZX'"],
            ["encode('00') -> 'I'", "encode('11') -> 'ZX'"],
        ),
        (
            "concrete_superdense_router_table",
            "superdense_pauli_router",
            "Implement PAULI_ROUTER for superdense messages: (0,0)->I, (0,1)->X, (1,0)->Z, and (1,1)->ZX or Y by the task convention.",
            ["PAULI_ROUTER", "(0, 0)", "(0, 1): \"X\"", "(1, 1)"],
            ["PAULI_ROUTER[(0, 1)] -> 'X'", "PAULI_ROUTER[(1, 0)] -> 'Z'"],
        ),
        (
            "concrete_binary_decoder_tables",
            "binary_measurement_decoder",
            "Implement Bell and syndrome binary measurement decoders with fixed bit order; do not swap (m1,m2).",
            ["BELL_LABELS", "SYNDROMES", "(m1, m2)", "not swappable"],
            ["Bell label table and syndrome table use the documented bit order"],
        ),
        (
            "concrete_phase_register_bounds",
            "phase_measurement_register",
            "Implement phase measurement register parsing so measurements stay in [0, 2^n) and are not bit-reversed.",
            ["phase", "measurement", "[0, 2^n)", "not bit-reversed"],
            ["measurement integer is used directly, without reversing bits"],
        ),
        (
            "concrete_qft_phase_x1_n4",
            "qft_phase_pattern",
            "Implement QFT phase pattern for N=4,x=1: phases[k] are 0, pi/2, pi, and 3*pi/2 modulo 2*pi.",
            ["phases[k]", "2 * pi * x * k / N", "pi/2", "3*pi/2"],
            ["qft_phases(x=1, N=4) -> [0, pi/2, pi, 3*pi/2]"],
        ),
        (
            "concrete_phase_repair_modulo",
            "circuit_phase_repair",
            "Repair phase comparisons so values are reduced modulo 2*pi before np.allclose, making 0 and 2*pi equivalent.",
            ["np.mod", "2 * np.pi", "np.allclose", "equivalent"],
            ["phase 0 compares equal to 2*pi after modulo reduction"],
        ),
        (
            "concrete_depth_cancel_self_inverse",
            "circuit_depth_optimization",
            "Optimize a gate list by canceling adjacent self-inverse pairs such as H-H, X-X, and CNOT-CNOT.",
            ["HH", "XX", "CNOT-CNOT", "cancel"],
            ["['H','H'] is removed", "two adjacent identical CNOTs are removed"],
        ),
        (
            "concrete_stabilizer_updates",
            "stabilizer_tableau_update_repair",
            "Repair stabilizer tableau apply_h/apply_s/apply_cnot using pre-update x/z bits and the documented sign flips.",
            ["apply_h", "apply_s", "apply_cnot", "pre-update"],
            ["H swaps x_q and z_q", "S updates z_q ^= x_q", "CNOT updates x_t and z_c"],
        ),
        (
            "concrete_depolarizing_half_zero",
            "quantum_channel_depolarizing",
            "Implement depolarizing_channel so |0><0| with p=0.5 returns [[0.75,0],[0,0.25]].",
            ["depolarizing_channel", "p=0.5", "[[0.75, 0.0], [0.0, 0.25]]", "I / 2"],
            ["depolarizing_channel([[1,0],[0,0]], 0.5) -> [[0.75, 0.0], [0.0, 0.25]]"],
        ),
        (
            "concrete_depolarizing_full_mixed",
            "quantum_channel_depolarizing",
            "Implement depolarizing_channel so p=1.0 maps |0><0| to the maximally mixed state [[0.5,0],[0,0.5]].",
            ["depolarizing_channel", "p=1.0", "maximally mixed", "[[0.5, 0.0], [0.0, 0.5]]"],
            ["depolarizing_channel([[1,0],[0,0]], 1.0) -> [[0.5, 0.0], [0.0, 0.5]]"],
        ),
        (
            "concrete_amplitude_damping_one_to_zero",
            "quantum_channel_depolarizing",
            "Implement amplitude_damping_channel so |1><1| with gamma=1 maps to |0><0|.",
            ["amplitude_damping_channel", "gamma=1", "[[1.0, 0.0], [0.0, 0.0]]", "Kraus"],
            ["amplitude_damping_channel(|1><1|, 1.0) -> |0><0|"],
        ),
        (
            "concrete_trotter_pauli_matrices",
            "trotterized_hamiltonian_evolution",
            "Implement pauli_matrix so X is [[0,1],[1,0]], Z is [[1,0],[0,-1]], and I is [[1,0],[0,1]].",
            ["pauli_matrix", "\"X\"", "\"Z\"", "\"I\""],
            ["pauli_matrix('X') -> [[0, 1], [1, 0]]", "pauli_matrix('Z') -> [[1, 0], [0, -1]]"],
        ),
        (
            "concrete_trotter_z_pi",
            "trotterized_hamiltonian_evolution",
            "Implement trotter_evolve so evolving |0> under Z for t=pi returns approximately -|0> and preserves norm.",
            ["trotter_evolve", "Z", "math.pi", "norm"],
            ["trotter_evolve([1,0], [(1.0,'Z')], t=pi, steps=100) -> [-1, 0] approximately"],
        ),
        (
            "concrete_vqe_energy_z",
            "vqe_energy_minimization",
            "Implement VQE expectation energy so <0|Z|0> evaluates to 1.0 and <1|Z|1> evaluates to -1.0.",
            ["VQE", "expectation", "np.vdot", "Z"],
            ["energy(|0>, Z) -> 1.0", "energy(|1>, Z) -> -1.0"],
        ),
        (
            "concrete_maxcut_assignment_enumerator",
            "maxcut_assignment_enumerator",
            "Enumerate all MaxCut assignments for n=3 as zero-padded bitstrings from '000' through '111'.",
            ["enumerate", "format", "03b", "'111'"],
            ["enumerate_assignments(3) -> ['000', ..., '111']"],
        ),
        (
            "concrete_maxcut_partition_ranker",
            "maxcut_partition_ranker",
            "Rank MaxCut partitions by descending cut value with deterministic ascending-bitstring tie breaks.",
            ["rank", "partition", "descending", "tie"],
            ["higher cut values appear first", "equal cut values sort by bitstring"],
        ),
        (
            "concrete_ghz_witness_negative",
            "ghz_state_witness",
            "Implement GHZ witness so the perfect 3-qubit GHZ state has witness value 0.5 - fidelity = -0.5.",
            ["GHZ", "witness", "0.5 - fidelity", "-0.5"],
            ["ghz_witness(perfect_ghz) -> -0.5"],
        ),
    ]
    for id_, task_dir, query, terms, example_io in concrete_coding_tasks:
        task_path = f"evals/tasks/quantum/{task_dir}"
        items.append(
            item(
                id_,
                "quantum_coding_exact",
                query,
                [f"{task_path}/tests.py", f"{task_path}/", repair, "docs/quantum_libraries/"],
                terms,
                minimum=min(3, len(terms)),
                coding=True,
                answer_requirements=terms,
                unit_test_file=f"{task_path}/tests.py",
                example_io=example_io,
            )
        )

    return items


def main() -> int:
    items = build_items()
    seen: set[str] = set()
    duplicates = [entry["id"] for entry in items if entry["id"] in seen or seen.add(str(entry["id"]))]
    if duplicates:
        raise SystemExit(f"duplicate ids: {duplicates}")
    if len(items) < 150:
        raise SystemExit(f"expected at least 150 items, got {len(items)}")
    coding_count = sum(1 for entry in items if entry["coding_problem"])
    if coding_count < 100:
        raise SystemExit(f"expected at least 100 coding problems, got {coding_count}")
    exact_count = sum(1 for entry in items if entry["judge_type"] == "unit_test_backed")
    if exact_count < 35:
        raise SystemExit(f"expected at least 35 unit-test-backed questions, got {exact_count}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(items)} questions to {OUTPUT} ({coding_count} coding problems)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
