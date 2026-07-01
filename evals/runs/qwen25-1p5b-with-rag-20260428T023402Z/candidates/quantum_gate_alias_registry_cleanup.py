class QuantumGateAliasRegistryCleanup:
    def normalize_gate_sequence(self, gate_sequence: list, canonical_registry=None, alias_registry=None) -> list:
        """
        Normalizes a given gate sequence according to standard conventions.
        
        Parameters:
        - gate_sequence (list): A list of strings representing quantum gates in their original form.
        - canonical_registry (dict, optional): A dictionary mapping gate symbols to their canonical representations.
        - alias_registry (dict, optional): An additional dictionary for resolving aliases during normalization.
        
        Returns:
        - list: The normalized gate sequence.
        """
        if canonical_registry is None:
            canonical_registry = {
                "I": "Identity",
                "X": "Pauli-X (NOT)",
                "Y": "Pauli-Y",
                "Z": "Pauli-Z",
                "H": "Hadamard",
                "S": "Phase",
                "Sdg": "S-dagger",
                "T": "pi/8",
                "Tdg": "T-dagger"
            }
        
        if alias_registry is None:
            alias_registry = {}
        
        normalized_sequence = []
        for gate in gate_sequence:
            symbol = gate.split()[0].upper()
            action = ""
            
            if symbol == "X":
                action = "NOT"
            elif symbol == "Y":
                action = "Y"
            elif symbol == "Z":
                action = "Z"
            elif symbol == "H":
                action = "(1/sqrt(2)) [[1,1],[1,-1]]"
            elif symbol == "S":
                action = "[[1,0],[0,i]]"
            elif symbol == "Sdg":
                action = "[[1,0],[0,-i]]"
