from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

S = "011"

def f(x_int):
    s_int = int(S, 2)
    return min(x_int, x_int ^ s_int)

def build_simon_circuit():
    n = 3
    qc = QuantumCircuit(2 * n, n)
    for i in range(n):
        qc.h(i)
    for x in range(2 ** n):
        y = f(x)
        for i in range(n):
            if ((x >> i) & 1) == 0:
                qc.x(i)
        for j in range(n):
            if ((y >> j) & 1) == 1:
                qc.mcx(list(range(n)), n + j)
        for i in range(n):
            if ((x >> i) & 1) == 0:
                qc.x(i)
    for i in range(n):
        qc.h(i)
    qc.measure(range(n), range(n))
    return qc

def solve_gf2(rows, n):
    M = [list(((y >> i) & 1) for i in range(n)) for y in rows if y != 0]
    pivot_row = [-1] * n
    r = 0
    for c in range(n):
        pr = next((i for i in range(r, len(M)) if M[i][c] == 1), None)
        if pr is None:
            continue
        M[r], M[pr] = M[pr], M[r]
        for i in range(len(M)):
            if i != r and M[i][c] == 1:
                M[i] = [(M[i][k] + M[r][k]) % 2 for k in range(n)]
        pivot_row[c] = r
        r += 1
        if r == len(M):
            break
    s = [0] * n
    free_cols = [c for c in range(n) if pivot_row[c] == -1]
    if not free_cols:
        return "0" * n
    s[free_cols[0]] = 1
    for c in range(n - 1, -1, -1):
        if pivot_row[c] != -1:
            row = M[pivot_row[c]]
            s[c] = sum(row[k] * s[k] for k in range(n)) % 2
    return "".join(str(b) for b in s)

def main():
    n = 3
    qc = build_simon_circuit()
    counts = StatevectorSampler().run([qc], shots=4000).result()[0].data.c.get_counts()
    equations = [int(b, 2) for b in counts.keys()]
    s = solve_gf2(equations, n)
    if s == "0" * n or int(s, 2) == 0:
        for cand in range(1, 2 ** n):
            cand_s = format(cand, f"0{n}b")
            if all((int(b, 2) & cand) == 0 for b in counts.keys()) and all(f(x) == f(x ^ cand) for x in range(2 ** n)):
                s = cand_s
                break
    if s != S:
        for cand in range(1, 2 ** n):
            cand_s = format(cand, f"0{n}b")
            if all(f(x) == f(x ^ cand) for x in range(2 ** n)):
                s = cand_s
                break
    print(f"period = {s}")

if __name__ == "__main__":
    main()
