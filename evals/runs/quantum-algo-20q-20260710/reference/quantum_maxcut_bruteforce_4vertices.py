def main():
    edges = [(0,1), (1,2), (2,3), (3,0), (0,2)]
    n = 4
    best_cut = -1
    best_bs = None
    for i in range(1 << n):
        bs = format(i, f"0{n}b")
        cut = sum(1 for u, v in edges if bs[u] != bs[v])
        if cut > best_cut:
            best_cut = cut
            best_bs = bs
    print(f"Max cut value: {best_cut}")
    print(f"Optimal bitstring: {best_bs}")

if __name__ == "__main__":
    main()
