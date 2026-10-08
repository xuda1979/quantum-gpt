def main():
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)]
    max_cut = -1
    best_bits = "0000"

    for n in range(16):
        bits = format(n, "04b")
        cut = 0
        for u, v in edges:
            if bits[u] != bits[v]:
                cut += 1
        if cut > max_cut:
            max_cut = cut
            best_bits = bits

    print(f"Max cut value: {max_cut}")
    print(f"Optimal bitstring: {best_bits}")


if __name__ == "__main__":
    main()
