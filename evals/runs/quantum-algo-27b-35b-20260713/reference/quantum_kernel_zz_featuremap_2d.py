import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import Statevector
from qiskit.circuit.library import ZZFeatureMap

def quantum_kernel(X1, X2, feature_dim, reps=2):
    """Compute the squared-fidelity quantum kernel
    K(x_i, x_j) = |<phi(x_i)|phi(x_j)>|^2
    using the ZZFeatureMap."""
    n = len(X1); m = len(X2)
    K = np.zeros((n, m))
    for i in range(n):
        sv_i = Statevector.from_instruction(ZZFeatureMap(feature_dim, reps=reps).assign_parameters(X1[i]))
        for j in range(m):
            sv_j = Statevector.from_instruction(ZZFeatureMap(feature_dim, reps=reps).assign_parameters(X2[j]))
            K[i, j] = float(np.abs(np.vdot(sv_i.data, sv_j.data)) ** 2)
    return K

def kernel_svm_predict(K_train, y_train, K_test, alpha, b):
    """Predict labels for test points given a precomputed kernel and
    dual coefficients alpha + bias b."""
    n_test = K_test.shape[0]
    n_train = K_train.shape[0]
    preds = np.zeros(n_test)
    for i in range(n_test):
        s = b
        for j in range(n_train):
            s += alpha[j] * y_train[j] * K_test[i, j]
        preds[i] = np.sign(s)
    return preds

def main():
    # Simple 2-feature binary classification: points inside a circle of radius
    # 1.0 are class +1, outside are class -1.
    X_train = np.array([
        [0.3, 0.4],   # inside (r=0.5)
        [-0.5, 0.2],  # inside (r~0.54)
        [1.2, 0.1],   # outside (r~1.2)
        [-0.3, -1.1], # outside (r~1.14)
    ])
    y_train = np.array([1, 1, -1, -1])
    X_test = np.array([
        [0.1, 0.1],   # inside
        [1.5, 1.5],   # outside
    ])
    y_test = np.array([1, -1])
    K_train = quantum_kernel(X_train, X_train, feature_dim=2, reps=2)
    K_test = quantum_kernel(X_test, X_train, feature_dim=2, reps=2)
    # Simple kernel SVM via least-squares: solve (K + lambda I) alpha = y
    lam = 0.1
    alpha = np.linalg.solve(K_train + lam * np.eye(len(y_train)), y_train)
    b = 0.0  # LS-SVM has no explicit bias
    preds = kernel_svm_predict(K_train, y_train, K_test, alpha, b)
    accuracy = float(np.mean(preds == y_test))
    print(f"Training points = {len(y_train)}")
    print(f"Test points = {len(y_test)}")
    print(f"Feature dim = 2")
    print(f"Kernel matrix shape = {K_train.shape}")
    print(f"Kernel diagonal = {np.round(np.diag(K_train), 4).tolist()}")
    print(f"Test predictions = {preds.astype(int).tolist()}")
    print(f"Test accuracy = {accuracy:.4f}")
    print(f"Correct: {accuracy == 1.0}")

if __name__ == "__main__":
    main()
