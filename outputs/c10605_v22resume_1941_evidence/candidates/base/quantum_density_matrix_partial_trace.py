import numpy as np


def construct_density_matrix(state_vector):
    """
    Construct a density matrix from a state vector.

    Parameters:
    state_vector: numpy array representing a quantum state vector

    Returns:
    numpy array representing the density matrix
    """
    state_vector = np.asarray(state_vector)
    if state_vector.ndim == 1:
        state_vector = state_vector.reshape(-1, 1)
    return state_vector @ state_vector.conj().T


def partial_trace(density_matrix, subsystems, total_subsystems):
    """
    Compute the partial trace of a density matrix over specified subsystems.

    Parameters:
    density_matrix: numpy array representing the density matrix
    subsystems: list of subsystem indices to trace out (0-indexed)
    total_subsystems: total number of subsystems

    Returns:
    numpy array representing the reduced density matrix
    """
    # Determine the dimension of each subsystem
    # We assume equal dimensions for simplicity, or we can infer from the total dimension
    total_dim = density_matrix.shape[0]

    # For simplicity, assume all subsystems have the same dimension
    # If total_subsystems is given, we can compute the dimension per subsystem
    if total_subsystems > 0:
        dim_per_subsystem = int(round(total_dim ** (1.0 / total_subsystems)))
        # Verify
        if dim_per_subsystem**total_subsystems != total_dim:
            # Try to find dimensions that multiply to total_dim
            # For now, assume equal dimensions
            pass
    else:
        dim_per_subsystem = int(round(total_dim**0.5))

    # Reshape the density matrix into a tensor with 2*total_subsystems indices
    # The first total_subsystems indices correspond to the row (ket) indices
    # The last total_subsystems indices correspond to the column (bra) indices
    shape = [dim_per_subsystem] * (2 * total_subsystems)
    tensor = density_matrix.reshape(shape)

    # Determine which subsystems to keep
    keep_subsystems = [i for i in range(total_subsystems) if i not in subsystems]

    # We need to trace out the specified subsystems
    # For each subsystem to trace out, we sum over the diagonal elements
    # This means we set the ket index equal to the bra index for that subsystem and sum

    # Let's do this step by step
    # First, let's identify the axes to trace
    # For subsystem i, the ket axis is i and the bra axis is total_subsystems + i

    # We'll trace out subsystems in reverse order to avoid index shifting issues
    # Actually, let's use einsum or a more systematic approach

    # Alternative approach: use np.einsum
    # Build the einsum string
    # For each subsystem, assign a label
    # Ket indices: 0, 1, 2, ..., total_subsystems-1
    # Bra indices: total_subsystems, total_subsystems+1, ..., 2*total_subsystems-1

    # For subsystems to trace out, we use the same label for ket and bra
    # For subsystems to keep, we use different labels

    # Let's assign labels
    # We need unique labels for kept subsystems (both ket and bra)
    # And same labels for traced subsystems (ket and bra)

    # Let's use letters
    import string

    letters = string.ascii_lowercase + string.ascii_uppercase

    # Assign labels
    # For each subsystem i:
    #   if i in subsystems: ket_label = bra_label = some letter
    #   else: ket_label = one letter, bra_label = another letter

    ket_labels = []
    bra_labels = []
    used_labels = set()

    for i in range(total_subsystems):
        if i in subsystems:
            # Use a single label for both
            label = letters[len(used_labels)]
            used_labels.add(label)
            ket_labels.append(label)
            bra_labels.append(label)
        else:
            ket_label = letters[len(used_labels)]
            used_labels.add(ket_label)
            bra_label = letters[len(used_labels)]
            used_labels.add(bra_label)
            ket_labels.append(ket_label)
            bra_labels.append(bra_label)

    # Build the input string: ket_labels + bra_labels
    input_str = "".join(ket_labels) + "".join(bra_labels)

    # Build the output string: only the labels for kept subsystems
    # For kept subsystems, we want both ket and bra labels in the output
    output_labels = []
    for i in range(total_subsystems):
        if i not in subsystems:
            output_labels.append(ket_labels[i])
            output_labels.append(bra_labels[i])

    output_str = "".join(output_labels)

    # Perform the einsum
    result = np.einsum(input_str + "->" + output_str, tensor)

    # Reshape the result to a 2D matrix
    # The result has shape (dim_per_subsystem, dim_per_subsystem, ...) for each kept subsystem
    # We need to combine the ket indices into one and the bra indices into one
    if len(keep_subsystems) == 0:
        # Traced out all subsystems, result is a scalar
        return np.array([[result]])
    else:
        # The result shape is (d, d, d, d, ...) where there are 2*len(keep_subsystems) dimensions
        # We need to reshape to (d^k, d^k) where k = len(keep_subsystems)
        k = len(keep_subsystems)
        new_shape = (dim_per_subsystem**k, dim_per_subsystem**k)
        return result.reshape(new_shape)
