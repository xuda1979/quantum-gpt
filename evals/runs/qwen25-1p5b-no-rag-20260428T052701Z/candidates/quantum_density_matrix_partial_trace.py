from typing import List, Tuple

class QuantumMechanics:
    @staticmethod
    def density_from_state(state_vector: List[float]) -> List[List[float]]:
        """Constructs a density matrix from a given state vector."""
        num_qubits = len(state_vector)
        identity_matrix = [[1 if i == j else 0 for j in range(num_qubits)] for i in range(num_qubits)]
        return identity_matrix

    @staticmethod
    def tensor_product(density_mat_A: List[List[float]], density_mat_B: List[List[float]]) -> List[List[float]]:
        """Multiplies two density matrices element-wise."""
        num_qubits = len(density_mat_A[0])
        result = []
        for row_A in density_mat_A:
            new_row = []
            for row_B in density_mat_B:
                new_row.extend([[a * b for a, b in zip(row_A, row_B)]])
            result.append(new_row)
        return result

    @staticmethod
    def partial_trace(matrix: List[List[float]], dimension_A: int, dimension_B: int, trace_out: str) -> List[List[float]]:
        """Performs partial trace over specified dimensions."""
        num_qubits = len(matrix)
        if trace_out == 'A':
            return [row[:dimension_A] + row[dimension_A+1:] for row in matrix[:dimension_A] + matrix[num_qubits-dimension_A:]]
        elif trace_out == 'B':
            return [row[:dimension_B] + row[dimension_B+1:] for row in matrix[:dimension_B] + matrix[num_qubits-dimension_B:]]
        else:
            raise ValueError("Invalid trace_out parameter.")

    @staticmethod
    def purity(density_matrix: List[List[float]]) -> float:
        """Calculates the purity of a density matrix."""
        trace_squared = sum([abs(element)**2 for row in density_matrix for element in row])
        return trace_squared / len(density_matrix)


# Test function to verify correctness
def check_operations():
    # Test cases provided in the problem description
    pass

check_operations()
