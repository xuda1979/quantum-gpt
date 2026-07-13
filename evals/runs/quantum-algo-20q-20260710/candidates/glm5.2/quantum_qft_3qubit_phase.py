    """QFT on the first n qubits in circuit"""
    for j in range(n):
        circuit.h(j)
        for k in range(j+1,n):
            np_angle = np.pi/float(2**(k-j))
            circuit.cp(np_angle, k, j)
    swap_registers(circuit, n)
