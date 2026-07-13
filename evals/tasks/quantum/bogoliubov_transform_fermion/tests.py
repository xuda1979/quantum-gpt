import importlib.util
import math


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures = []

    # Quasiparticle energy
    if not math.isclose(
        module.bogoliubov_basis_energy(0.0, math.pi / 4, 0.0), math.pi / 4, abs_tol=1e-12
    ):
        failures.append("energy with delta=0 should be |epsilon|")
    if not math.isclose(module.bogoliubov_basis_energy(0.0, 3.0, 4.0), 5.0, abs_tol=1e-12):
        failures.append("energy with (3,4) should be 5 (3-4-5 triangle)")

    # Bogoliubov angle
    if not math.isclose(module.bogoliubov_angle(1.0, 0.0), 0.0, abs_tol=1e-12):
        failures.append("angle(epsilon=1, delta=0) should be 0")
    # tan(2*theta) = 1 -> 2*theta = pi/4 -> theta = pi/8
    if not math.isclose(module.bogoliubov_angle(1.0, 1.0), math.pi / 8, abs_tol=1e-12):
        failures.append("angle(1, 1) should be pi/8")
    # tan(2*theta) -> infinity (epsilon=0) -> 2*theta = pi/2 -> theta = pi/4
    if not math.isclose(module.bogoliubov_angle(0.0, 1.0), math.pi / 4, abs_tol=1e-12):
        failures.append("angle(0, 1) should be pi/4")

    # Ground-state energy is negative of quasiparticle energy
    E = module.bogoliubov_basis_energy(0.0, 3.0, 4.0)
    if not math.isclose(module.bogoliubov_ground_state_energy(3.0, 4.0), -E, abs_tol=1e-12):
        failures.append("ground-state energy should be -E")

    # Transform coefficients
    u, v = module.bogoliubov_transform_coefficients(math.pi / 4)
    if not (
        math.isclose(u, math.sqrt(2) / 2, abs_tol=1e-12)
        and math.isclose(v, math.sqrt(2) / 2, abs_tol=1e-12)
    ):
        failures.append("coefficients at theta=pi/4 should be (sqrt2/2, sqrt2/2)")
    u0, v0 = module.bogoliubov_transform_coefficients(0.0)
    if not (math.isclose(u0, 1.0, abs_tol=1e-12) and math.isclose(v0, 0.0, abs_tol=1e-12)):
        failures.append("coefficients at theta=0 should be (1, 0)")

    return {
        "passed": not failures,
        "details": failures or ["Bogoliubov transform coefficients correct"],
    }
