import numpy as np

def density_from_state(state_vector):
    num_qubits = len(state_vector)
    dimension = 2 ** num_qubits
    density_matrix = np.outer(state_vector, state_vector.conj())
    return density_matrix

def tensor_product(density_matrix1, density_matrix2):
    product = np.kron(density_matrix1, density_matrix2)
    return product

def partial_trace(rho, dim_a, dim_b, trace_out='B'):
    rho4 = rho.reshape(dim_a, dim_b, dim_a, dim_b)
    if trace_out == 'B':
        return np.einsum('abcd->', rho4)
    elif trace_out == 'A':
        return np.einsum('abcd->cd', rho4)

def purity(density_matrix):
    trace_squared = np.trace(np.dot(density_matrix, density_matrix))
    return trace_squared

# Test function to verify correctness
def check_operations():
    # Test case 1: Identity matrix
    identity_matrix = np.eye(2)
    result_identity = partial_trace(identity_matrix, 2, 2, trace_out='B')
    expected_identity = np.array([[1, 0], [0, 1]])
    assert np.allclose(result_identity, expected_identity), f"Incorrect result for identity matrix"

    # Test case 2: Tensor product of two identical states
    state = np.array([[1, 0], [0, 0]])
    tensor_product_result = tensor_product(state, state)
    expected_tensor_product = np.array([
        [1, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ])
    assert np.allclose
