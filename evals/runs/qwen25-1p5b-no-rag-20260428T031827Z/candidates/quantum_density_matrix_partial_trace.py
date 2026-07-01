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

    @staticmethod
    def partial_trace(matrix: List[List[float]], dimension_A: int, dimension_B: int, trace_out: str) -> List[List[float]]:
        """Partial trace over specified dimensions."""
        num_qubits = len(matrix[0])

        if trace_out == 'A':
            start_index = dimension_A * num_qubits
            end_index = (dimension_A + 1) * num_qubits
            return matrix[start_index:end_index]

        elif trace_out == 'B':
            start_index = dimension_B * num_qubits
            end_index = (dimension_B + 1) * num_qubits
            return matrix[:start_index] + matrix[end_index:]

        else:
            raise ValueError("Invalid trace_out parameter.")

    @staticmethod
    def purity(density_matrix: List[List[float]]) -> float:
        """Calculate the purity of a density matrix."""
        trace_squared = sum(abs(element)**2 for row in density_matrix for element in row)
        return trace_squared / len(density_matrix)


# Test function to verify correctness
def run_tests():
    candidate_path = "path_to_candidate_file"
    results = run_tests(candidate_path)
    print(results)


if __name__ == "__main__":
    run_tests()
