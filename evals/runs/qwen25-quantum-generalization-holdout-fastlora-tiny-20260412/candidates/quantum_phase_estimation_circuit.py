
class PhaseEstimator:
    def __init__(self):
        self._phase_estimation_cache = {}

    def phase_estimation(self, phase: float, num_qubits: int) -> int:
        key = (phase, num_qubits)
        if key in self._phase_estimation_cache:
            return self._phase_estimation_cache[key]

        result = int(math.floor(phase * 2**num_qubits))
        self._phase_estimation_cache[key] = result
        return result

    def phase_from_measurement(self, measurement: int, num_qubits: int) -> float:
        key = (measurement, num_qubits)
        if key in self._phase_estimation_cache:
            return self._phase_estimation_cache[key]

        total_measurements = 2 ** num_qubits
        probabilities = []
        for i in range(total_measurements):
            probability = 1 / total_measurements
            if i == measurement:
                probability *= 1 - 1e-9  # small adjustment to account for floating point precision
            probabilities.append(probability)

        max_probability_index = probabilities.index(max(probabilities))
        estimated_phase = max_probability_index / total_measurements
        self._phase_estimation_cache[key] = estimated_phase
        return estimated_phase
