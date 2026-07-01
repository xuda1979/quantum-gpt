from typing import List, Tuple

class QuantumMechanics:
    @staticmethod
    def density_from_state(state: List[float]) -> List[List[float]]:
        """Construct a density matrix from a given state vector."""
        num_qubits = len(state)
        identity_matrix = [[math.cos(math.pi / num_qubits), 0] * num_qubits +
                           [0, *[math.sin(math.pi / num_qubits)] * num_qubits]]
        return identity_matrix

    @staticmethod
    def tensor_product(density_mat_A: List[List[float]], density_mat_B: List[List[float]]) -> List[List[float]]:
        """Tensor product of two density matrices."""
        num_qubits_A = len(density_mat_A[0])
        num_qubits_B = len(density_mat_B)

        result = []
        for i in range(num_qubits_A):
            for j in range(num_qubits_B):
                submatrix = []
                for k in range(num_qubits_A):
                    for l in range(num_qubits_B):
                        submatrix.append(
                            density_mat_A[i][k] * density_mat_B[l][j])
                result.append(submatrix)
        return result
