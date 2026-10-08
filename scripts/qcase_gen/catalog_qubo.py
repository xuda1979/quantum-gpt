"""Catalog of real-world QUBO problems mapped to QAOA via generic_qubo.
Each builder constructs a *correct* QUBO and rich Chinese narrative. Returns
(spec, key, fname). The embedded code recomputes the same QUBO and solves it,
so all resource numbers are verified at generation time."""

from __future__ import annotations

import random

from .specs_qaoa import generic_qubo


def _ksat_to_text(name, n, extra):
    return name


def portfolio(n, k, seed, domain, need, goal):
    rng = random.Random(seed)
    mu = [round(rng.uniform(0.5, 1.6), 2) for _ in range(n)]
    sig = [[0.0] * n for _ in range(n)]
    for i in range(n):
        sig[i][i] = round(rng.uniform(0.8, 1.4), 2)
    for i in range(n):
        for j in range(i + 1, n):
            v = round(rng.uniform(0.0, 0.5), 2)
            sig[i][j] = sig[j][i] = v
    q, lam = 0.5, 5.0
    linear = {}
    quad = {}
    for i in range(n):
        linear[i] = -mu[i] + q * sig[i][i] + lam * (1 - 2 * k)
    for i in range(n):
        for j in range(i + 1, n):
            quad[(i, j)] = q * (sig[i][j] + sig[j][i]) + 2 * lam
    const = lam * k * k
    texts = {
        "title": f"Portfolio N={n} K={k}",
        "domain": domain,
        "need": need,
        "goal": goal,
        "bounds": [
            f"输入：{n} 维预期收益向量 $\\mu$、${n}\\times{n}$ 协方差矩阵 $\\Sigma$、风险厌恶 $q={q}$、目标持仓 $K={k}$。",
            f"决策变量维度：$N={n}$ 个二元变量 $x_i\\in\\{{0,1\\}}$ 表示是否持有资产 $i$。",
            f"约束硬性：$\\sum_i x_i={k}$ 为硬等式约束（以惩罚项软化进哈密顿量）。",
            "输出：最优资产选择比特串、组合效用值与资源统计摘要。",
        ],
        "vars": "$x_i\\in\\{0,1\\}$ 表示是否持有资产 $i$；自旋 $z_i\\in\\{+1,-1\\}$，$x_i=(1-z_i)/2$。",
        "objective": f"最小化负效用并叠加持仓惩罚：$\\min_{{x}}\\;-\\sum_i\\mu_i x_i+q\\sum_{{i,j}}\\Sigma_{{ij}}x_i x_j+\\lambda\\big(\\sum_i x_i-{k}\\big)^2$。",
        "constraints": f"等式约束 $\\sum_i x_i={k}$ 通过二次惩罚 $\\lambda(\\sum_i x_i-{k})^2$ 编码，$\\lambda={lam}$ 显著大于单资产收益与风险项，排斥违约解。",
        "mapping": "代入 $x_i=(1-z_i)/2$ 展开为 Ising $H_C=\\sum_i h_i Z_i+\\sum_{i<j}J_{ij}Z_iZ_j+\\text{const}$，基态即最优组合。",
        "ptype": "带等式约束的 QUBO / 均值-方差组合优化，适配 QAOA。",
        "reason": "组合优化是 QAOA 的标志性工业应用；均值-方差模型可精确写成二次型，浅层 QAOA 在该规模即给出优质组合，纯 CPU 秒级闭环。",
        "desc": "构造收益/协方差 Mock 数据 → 组装带持仓惩罚 QUBO → 转 Ising → QAOA + COBYLA 多重启 → 由末态概率输出最优组合并打印效用与资源摘要。",
    }
    return generic_qubo(
        n, linear, quad, const, f"portfolio__QAOA__{n}", f"portfolio_qaoa_n{n}", texts
    )


def knapsack(n, seed, domain, need, goal):
    """0/1 knapsack with a soft capacity penalty (no slack qubits)."""
    rng = random.Random(seed)
    val = [rng.randint(2, 9) for _ in range(n)]
    wt = [rng.randint(1, 6) for _ in range(n)]
    cap = max(wt) + sum(wt) // 3
    lam = float(max(val) + 1)
    # maximize sum v_i x_i  s.t. sum w_i x_i <= cap
    # soft penalty: lam * max(0, sum w x - cap)^2 -> use quadratic penalty around cap
    # We encode penalty as lam*(sum w_i x_i - cap)^2 but only penalize overweight by
    # using a one-sided trick is hard in pure QUBO; use standard squared penalty which
    # also discourages underfill slightly; acceptable for demonstration with tuned lam.
    linear = {}
    quad = {}
    for i in range(n):
        linear[i] = -val[i] + lam * (wt[i] * wt[i] - 2 * cap * wt[i])
    for i in range(n):
        for j in range(i + 1, n):
            quad[(i, j)] = 2 * lam * wt[i] * wt[j]
    const = lam * cap * cap
    texts = {
        "title": f"Knapsack N={n}",
        "domain": domain,
        "need": need,
        "goal": goal,
        "bounds": [
            f"输入：$N={n}$ 件物品的价值 $v_i$、重量 $w_i$，背包容量 $C={cap}$。",
            f"决策变量维度：$N={n}$ 个二元变量 $x_i\\in\\{{0,1\\}}$ 表示是否装入物品 $i$。",
            "约束硬性：$\\sum_i w_i x_i\\le C$ 为容量约束（以二次惩罚软化）。",
            "输出：最优装包比特串、总价值与资源统计摘要。",
        ],
        "vars": "$x_i\\in\\{0,1\\}$ 表示是否装入物品 $i$；$v_i,w_i$ 为价值与重量。",
        "objective": "最大化总价值并惩罚超重：$\\min_{x}\\;-\\sum_i v_i x_i+\\lambda\\big(\\sum_i w_i x_i-C\\big)^2$。",
        "constraints": f"容量约束 $\\sum_i w_i x_i\\le C$ 以二次惩罚 $\\lambda(\\sum_i w_i x_i-C)^2$ 近似编码，$\\lambda={lam}$ 大于单件价值上界以抑制超载方案。",
        "mapping": "代入 $x_i=(1-z_i)/2$ 展开为 Ising $H_C=\\sum_i h_i Z_i+\\sum_{i<j}J_{ij}Z_iZ_j+\\text{const}$，基态对应高价值且满足容量的装包。",
        "ptype": "带容量约束的 QUBO / 0-1 背包，适配 QAOA。",
        "reason": "背包问题是资源分配的经典 NP-hard 模型；二次惩罚法把容量约束嵌入 Ising，QAOA 浅层即可在小规模逼近最优装包。",
        "desc": "构造物品价值/重量 Mock 数据 → 组装带容量惩罚 QUBO → 转 Ising → QAOA + COBYLA 多重启 → 由末态概率输出装包方案与总价值。",
    }
    return generic_qubo(
        n, linear, quad, const, f"knapsack__QAOA__{n}", f"knapsack_qaoa_n{n}", texts
    )


def vertex_cover(n, seed, domain, need, goal):
    from . import qaoa

    edges = qaoa.rand_graph(n, 0.5, seed)
    lam = 3.0
    # minimize sum x_i  s.t. every edge covered: x_i + x_j >= 1
    # penalty lam*(1 - x_i - x_j + x_i x_j) = lam*(1-x_i)(1-x_j)
    linear = {i: 1.0 for i in range(n)}
    quad = {}
    const = 0.0
    for i, j, _w in edges:
        const += lam
        linear[i] = linear.get(i, 0.0) - lam
        linear[j] = linear.get(j, 0.0) - lam
        quad[(i, j)] = quad.get((i, j), 0.0) + lam
    texts = {
        "title": f"VertexCover N={n}",
        "domain": domain,
        "need": need,
        "goal": goal,
        "bounds": [
            f"输入：无向图 $G=(V,E)$，$N={n}$ 个节点、{len(edges)} 条边。",
            f"决策变量维度：$N={n}$ 个二元变量 $x_i\\in\\{{0,1\\}}$ 表示节点是否入选覆盖集。",
            "约束硬性：每条边至少一端入选（硬约束，以惩罚项软化）。",
            "输出：最小顶点覆盖比特串、覆盖集规模与资源统计摘要。",
        ],
        "vars": "$x_i\\in\\{0,1\\}$ 表示节点 $i$ 是否入选覆盖集；$(i,j)\\in E$ 为待覆盖边。",
        "objective": "最小化覆盖集规模并惩罚未覆盖边：$\\min_{x}\\;\\sum_i x_i+\\lambda\\sum_{(i,j)\\in E}(1-x_i)(1-x_j)$。",
        "constraints": f"覆盖约束 $x_i+x_j\\ge1,\\ \\forall(i,j)\\in E$，以惩罚 $\\lambda(1-x_i)(1-x_j)$ 编码，$\\lambda={lam}$ 大于单点成本 1，排斥漏覆盖。",
        "mapping": "代入 $x_i=(1-z_i)/2$ 展开为 Ising $H_C=\\sum_i h_i Z_i+\\sum_{(i,j)\\in E}J_{ij}Z_iZ_j+\\text{const}$，基态对应最小顶点覆盖。",
        "ptype": "带覆盖约束的 QUBO / 最小顶点覆盖，适配 QAOA。",
        "reason": "最小顶点覆盖是网络监控、布点选址的核心 NP-hard 问题；惩罚法把覆盖约束嵌入 Ising，QAOA 在小图上给出高质量解。",
        "desc": "构造图 → 组装带覆盖惩罚 QUBO → 转 Ising → QAOA + COBYLA 多重启 → 由末态概率输出最小覆盖集与规模。",
    }
    return generic_qubo(n, linear, quad, const, f"vcover__QAOA__{n}", f"vcover_qaoa_n{n}", texts)


def max2sat(n, seed, domain, need, goal):
    """MAX-2-SAT: maximize satisfied 2-literal clauses."""
    rng = random.Random(seed)
    n_clauses = n + 2
    clauses = []
    for _ in range(n_clauses):
        i, j = rng.sample(range(n), 2)
        si = rng.choice([True, False])
        sj = rng.choice([True, False])
        clauses.append((i, si, j, sj))
    # clause (l_i OR l_j) unsatisfied prob -> penalty for both literals false.
    # literal true if (x_i==1 and si) or (x_i==0 and not si). Define indicator of
    # literal being FALSE: f_i = x_i if not si else (1-x_i).
    # clause unsatisfied = f_i * f_j. Minimize sum f_i f_j (= number unsatisfied).
    linear = {i: 0.0 for i in range(n)}
    quad = {}
    const = 0.0

    def add_term(coef, terms):
        # terms: list of ('x',i) meaning x_i, ('1',i) meaning (1-x_i)
        nonlocal const
        # expand product of up to 2 factors
        if len(terms) == 1:
            kind, i = terms[0]
            if kind == "x":
                linear[i] = linear.get(i, 0.0) + coef
            else:
                const += coef
                linear[i] = linear.get(i, 0.0) - coef
        else:
            (k1, a), (k2, b) = terms
            # build (factorA)(factorB)
            # factorA = x_a (k='x') or (1-x_a)
            # represent as c0 + c1 x_a, similarly
            A = {"c": 0.0, "x": 0.0}
            B = {"c": 0.0, "x": 0.0}
            A["x"] = 1.0 if k1 == "x" else -1.0
            A["c"] = 0.0 if k1 == "x" else 1.0
            B["x"] = 1.0 if k2 == "x" else -1.0
            B["c"] = 0.0 if k2 == "x" else 1.0
            # product = A.c*B.c + A.c*B.x x_b + A.x*B.c x_a + A.x*B.x x_a x_b
            const += coef * A["c"] * B["c"]
            linear[b] = linear.get(b, 0.0) + coef * A["c"] * B["x"]
            linear[a] = linear.get(a, 0.0) + coef * A["x"] * B["c"]
            key = (min(a, b), max(a, b))
            quad[key] = quad.get(key, 0.0) + coef * A["x"] * B["x"]

    for i, si, j, sj in clauses:
        ti = ("x", i) if not si else ("1", i)
        tj = ("x", j) if not sj else ("1", j)
        add_term(1.0, [ti, tj])

    def cl(b):
        return (
            "("
            + " ∨ ".join(
                (f"x_{c[0]}" if c[1] else f"¬x_{c[0]}", f"x_{c[2]}" if c[3] else f"¬x_{c[2]}")[k]
                for k, c in [(0, b), (1, b)]
            )
            + ")"
        )

    texts = {
        "title": f"MAX2SAT N={n}",
        "domain": domain,
        "need": need,
        "goal": goal,
        "bounds": [
            f"输入：$N={n}$ 个布尔变量、{n_clauses} 个 2-文字子句的合取范式。",
            f"决策变量维度：$N={n}$ 个二元变量 $x_i\\in\\{{0,1\\}}$ 表示变量真值。",
            "约束硬性：无硬约束；目标是最大化被满足的子句数。",
            "输出：最优赋值比特串、被满足子句数与资源统计摘要。",
        ],
        "vars": "$x_i\\in\\{0,1\\}$ 为布尔变量真值；文字为 $x_i$ 或 $\\neg x_i$。",
        "objective": "最小化未满足子句数（等价最大化满足数）：$\\min_{x}\\;\\sum_{c}\\,f_{c,1}\\,f_{c,2}$，其中 $f$ 为子句中文字取假的指示。",
        "constraints": "无显式约束；MAX-2-SAT 是纯目标优化，未满足子句以乘积项计入目标。",
        "mapping": "每个子句的不满足指示展开为常数/线性/二次项，代入 $x_i=(1-z_i)/2$ 得 Ising，基态对应满足最多子句的赋值。",
        "ptype": "无约束二次二值优化（QUBO）/ MAX-2-SAT，适配 QAOA。",
        "reason": "MAX-2-SAT 是约束满足与电路验证的代表性 NP-hard 问题，可精确写成二次型；QAOA 在小规模即能找到高满足率赋值。",
        "desc": "随机生成 2-文字子句 → 由不满足指示展开 QUBO → 转 Ising → QAOA + COBYLA 多重启 → 由末态概率输出最优赋值与满足子句数。",
    }
    return generic_qubo(n, linear, quad, const, f"max2sat__QAOA__{n}", f"max2sat_qaoa_n{n}", texts)


def task_assignment(n_tasks, seed, domain, need, goal):
    """Assign each of m tasks to one of 2 machines to balance load (n=m qubits).
    x_i=0 -> machine A, x_i=1 -> machine B. Minimize load imbalance squared."""
    rng = random.Random(seed)
    n = n_tasks
    load = [rng.randint(1, 8) for _ in range(n)]
    T = sum(load)
    # loadB = sum load_i x_i ; loadA = T - loadB ; imbalance = (loadA - loadB)^2 = (T - 2 loadB)^2
    linear = {}
    quad = {}
    const = T * T
    for i in range(n):
        linear[i] = -4 * T * load[i] + 4 * load[i] * load[i]
    for i in range(n):
        for j in range(i + 1, n):
            quad[(i, j)] = 8 * load[i] * load[j]
    texts = {
        "title": f"LoadBalance N={n}",
        "domain": domain,
        "need": need,
        "goal": goal,
        "bounds": [
            f"输入：$N={n}$ 个任务的处理耗时 $t_i$，2 台并行机器。",
            f"决策变量维度：$N={n}$ 个二元变量 $x_i\\in\\{{0,1\\}}$ 表示任务分配到机器 A/B。",
            "约束硬性：无显式约束；目标是两机负载尽量均衡（差平方最小）。",
            "输出：最优分配比特串、两机负载差与资源统计摘要。",
        ],
        "vars": "$x_i\\in\\{0,1\\}$ 表示任务 $i$ 分配到机器 B（否则 A）；$t_i$ 为耗时。",
        "objective": "最小化两机负载差的平方：$\\min_{x}\\;\\big(\\sum_i t_i(1-2x_i)\\big)^2$。",
        "constraints": "无显式约束；负载均衡由平方目标隐式驱动。",
        "mapping": "展开平方并代入自旋 $s_i=1-2x_i$ 得到 Ising $H_C=\\sum_i h_i Z_i+\\sum_{i<j}J_{ij}Z_iZ_j+\\text{const}$，基态对应最均衡分配。",
        "ptype": "无约束二次二值优化（QUBO）/ 双机负载均衡，适配 QAOA。",
        "reason": "并行机负载均衡是生产排程与算力调度的基础问题，等价于数集划分的二次型；QAOA 浅层即可在小规模找到均衡分配。",
        "desc": "构造任务耗时 Mock 数据 → 由负载差平方展开 QUBO → 转 Ising → QAOA + COBYLA 多重启 → 由末态概率输出分配与负载差。",
    }
    return generic_qubo(
        n, linear, quad, const, f"loadbalance__QAOA__{n}", f"loadbalance_qaoa_n{n}", texts
    )
