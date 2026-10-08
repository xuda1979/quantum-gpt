# graph_cut.py

def main():
    # Define edges
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)]
    n = 4  # number of vertices

    max_cut = -1
    best_assignment = None

    # Brute-force all 2^4 = 16 assignments
    for i in range(16):
        # Convert integer to 4-bit binary string
        assignment = format(i, '04b')
        cut_value = 0
        for u, v in edges:
            if assignment[u] != assignment[v]:
                cut_value += 1
        if cut_value > max_cut:
            max_cut = cut_value
            best_assignment = assignment

    print(f"Max cut value: {max_cut}")
    print(f"Optimal bitstring: {best_assignment}")

if __name__ == "__main__":
    main()
