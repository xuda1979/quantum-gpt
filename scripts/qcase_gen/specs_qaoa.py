"""Concrete QAOA case specs across many domains/problem types.
Each builder returns (spec, fingerprint). spec['code'] is runnable; the
generator executes it and injects verified numbers."""

from __future__ import annotations

import random

from . import qaoa

# Shared QAOA narrative fragments (kept consistent with qaoa.QAOA_CODE, which
# evaluates the diagonal cost Hamiltonian exactly via Statevector probabilities).
QAOA_SHOTS = "全状态向量精确期望，无采样噪声（对角代价哈密顿量直接由末态概率求期望）"
QAOA_SIM = "全状态向量精确模拟（`qiskit.quantum_info.Statevector`）"
QAOA_FRAMEWORK = "Qiskit ($\\ge 1.2$) + `qiskit.quantum_info` (`Statevector` / `SparsePauliOp`) + `QAOAAnsatz` + SciPy COBYLA。"
QAOA_TARGET = "Qiskit 1.x 现代接口：`QAOAAnsatz` 构造变分线路，`Statevector` 做全态精确模拟；QUBO 代价哈密顿量在 Z 基对角，期望由末态概率与经典代价向量内积精确求得。"


def qaoa_budget(n):
    """Adaptive (reps, maxiter, restarts) by size. Each Statevector eval has
    fixed Qiskit per-gate Python overhead, so large-N circuits use fewer reps
    and fewer evals; acceptance is approximation-ratio based (>=0.85)."""
    if n <= 5:
        return 3, 80, 4
    if n <= 7:
        return 3, 60, 4
    return 3, 55, 4


def maxcut(n, seed, domain, need, goal):
    edges = qaoa.rand_graph(n, 0.55, seed)
    linear = {i: 0.0 for i in range(n)}
    quad = {}
    const = 0.0
    # Max-Cut: maximize sum w_ij (x_i + x_j - 2 x_i x_j) => minimize negative
    for i, j, w in edges:
        linear[i] += -w
        linear[j] += -w
        quad[(i, j)] = quad.get((i, j), 0.0) + 2 * w
    title = f"MaxCut N={n}"
    reps, maxiter, restarts = qaoa_budget(n)
    code = qaoa.build_qaoa_code(
        title, n, linear, quad, const, reps=reps, maxiter=maxiter, shots=4096, restarts=restarts
    )
    spec = {
        "scenario": {
            "domain": domain,
            "need": need,
            "goal": goal,
            "bounds": [
                f"输入：无向带权图，$N={n}$ 个节点、{len(edges)} 条边及边权 $w_{{ij}}$。",
                f"决策变量维度：$N={n}$ 个二元变量 $x_i \\in \\{{0,1\\}}$ 表示节点划分。",
                "约束硬性：无显式约束，纯目标优化（割边权重最大化）。",
                "输出：最优二分划分比特串、最大割权重与资源统计摘要。",
            ],
        },
        "modeling": {
            "vars": "$x_i \\in \\{0,1\\}$ 表示节点 $i$ 归属的子集；$z_i \\in \\{+1,-1\\}$ 为对应 Ising 自旋，$x_i=(1-z_i)/2$。",
            "objective": "最大化被割开的边权之和，等价于最小化其相反数：$\\min_{x}\\; -\\sum_{(i,j)\\in E} w_{ij}\\,(x_i + x_j - 2x_i x_j)$。",
            "constraints": "无约束（MaxCut 为纯组合优化），故不引入惩罚项。",
            "mapping": "代入 $x_i=(1-z_i)/2$ 后得到 Ising 形式 $H_C=\\sum_{(i,j)\\in E}\\frac{w_{ij}}{2}(Z_iZ_j - I)$，基态对应最大割。",
            "ptype": "无约束二次二值优化（QUBO）/ MaxCut，适配 QAOA。",
            "shots": QAOA_SHOTS,
            "iters": f"COBYLA `maxiter={maxiter}`，{restarts} 次随机重启取最优",
            "sim": QAOA_SIM,
            "framework": QAOA_FRAMEWORK,
            "reason": "MaxCut 是 QAOA 的标杆问题；交替 Cost/Mixer 层天然贴合 Ising 目标，多次随机重启的浅层 QAOA 在该规模即可逆近优质割，纯 CPU 状态向量秒级闭环。",
        },
        "program": {
            "target": QAOA_TARGET,
            "deps": "`qiskit>=1.2`，`numpy>=1.24`，`scipy>=1.10`。",
            "desc": "构造带权图 → 组装 MaxCut QUBO → 转 Ising `SparsePauliOp` → `QAOAAnsatz(reps=3)` + COBYLA 多重启 → 由末态概率输出最优划分并打印割权重与资源摘要。",
            "cmd": f"python maxcut_qaoa_n{n}.py",
            "expect": "打印 num_qubits={num_qubits}、circuit.depth()={depth}、num Pauli terms={num_terms}、QAOA 解比特串 {bitstring}、割目标值 {objective}、与暴力最优 {optimum} 的近似比 {approx_ratio}。",
        },
        "code": code,
    }
    return spec, f"maxcut__QAOA__{n}", f"maxcut_qaoa_n{n}"


def max_independent_set(n, seed, domain, need, goal):
    edges = qaoa.rand_graph(n, 0.5, seed)
    lam = 3.0
    # maximize sum x_i  s.t. no adjacent both selected -> penalty lam * x_i x_j
    linear = {i: -1.0 for i in range(n)}
    quad = {}
    for i, j, _w in edges:
        quad[(i, j)] = quad.get((i, j), 0.0) + lam
    const = 0.0
    title = f"MaxIndependentSet N={n}"
    reps, maxiter, restarts = qaoa_budget(n)
    code = qaoa.build_qaoa_code(
        title, n, linear, quad, const, reps=reps, maxiter=maxiter, shots=4096, restarts=restarts
    )
    spec = {
        "scenario": {
            "domain": domain,
            "need": need,
            "goal": goal,
            "bounds": [
                f"输入：冲突图 $G=(V,E)$，$N={n}$ 个候选项与 {len(edges)} 条互斥边。",
                f"决策变量维度：$N={n}$ 个二元变量 $x_i \\in \\{{0,1\\}}$ 表示是否选入。",
                "约束硬性：相邻节点不可同时选中（硬约束，以惩罚项软化）。",
                "输出：最大独立集比特串、集合规模与资源统计摘要。",
            ],
        },
        "modeling": {
            "vars": "$x_i \\in \\{0,1\\}$ 表示候选项 $i$ 是否入选；$(i,j)\\in E$ 表示互斥关系。",
            "objective": "最大化入选数量并惩罚冲突：$\\min_{x}\\; -\\sum_i x_i + \\lambda\\sum_{(i,j)\\in E} x_i x_j$。",
            "constraints": f"互斥硬约束 $x_i x_j = 0,\\ \\forall (i,j)\\in E$，以惩罚系数 $\\lambda={lam}$ 编码，量级大于单点收益 $1$，确保冲突解被排斥。",
            "mapping": "代入 $x_i=(1-z_i)/2$ 后展开为 $H_C=\\sum_i h_i Z_i + \\sum_{(i,j)\\in E} J_{ij} Z_iZ_j + \\text{const}$，基态对应最大独立集。",
            "ptype": "带不等式（互斥）约束的 QUBO / 最大独立集，适配 QAOA。",
            "shots": QAOA_SHOTS,
            "iters": f"COBYLA `maxiter={maxiter}`，{restarts} 次随机重启取最优",
            "sim": QAOA_SIM,
            "framework": QAOA_FRAMEWORK,
            "reason": "最大独立集是经典 NP-hard 图问题，QAOA 的 Ising 表示能自然编码互斥惩罚；浅层线路多重启即可在该规模给出高质量解。",
        },
        "program": {
            "target": QAOA_TARGET,
            "deps": "`qiskit>=1.2`，`numpy>=1.24`，`scipy>=1.10`。",
            "desc": "构造冲突图 → 组装带互斥惩罚的 QUBO → 转 Ising → QAOA 多重启优化 → 由末态概率输出最大独立集与资源摘要。",
            "cmd": f"python mis_qaoa_n{n}.py",
            "expect": "打印 num_qubits={num_qubits}、circuit.depth()={depth}、QAOA 解比特串 {bitstring}（无相邻冲突）、目标值 {objective}、与暴力最优 {optimum} 的近似比 {approx_ratio}。",
        },
        "code": code,
    }
    return spec, f"mis__QAOA__{n}", f"mis_qaoa_n{n}"


def number_partition(n, seed, domain, need, goal):
    rng = random.Random(seed)
    nums = [rng.randint(1, 9) for _ in range(n)]
    # minimize (sum s_i a_i)^2 with s_i in {+1,-1}; x mapping s_i=1-2x_i
    # In x: sum a_i (1-2x_i) = S - 2 sum a_i x_i ; square it.
    S = sum(nums)
    linear = {}
    quad = {}
    const = S * S
    for i in range(n):
        linear[i] = linear.get(i, 0.0) + (-4.0 * S * nums[i] + 4.0 * nums[i] * nums[i])
    for i in range(n):
        for j in range(i + 1, n):
            quad[(i, j)] = quad.get((i, j), 0.0) + 8.0 * nums[i] * nums[j]
    title = f"NumberPartition N={n}"
    reps, maxiter, restarts = qaoa_budget(n)
    code = qaoa.build_qaoa_code(
        title, n, linear, quad, const, reps=reps, maxiter=maxiter, shots=4096, restarts=restarts
    )
    spec = {
        "scenario": {
            "domain": domain,
            "need": need,
            "goal": goal,
            "bounds": [
                f"输入：正整数集合 $A=\\{{{', '.join(map(str, nums))}\\}}$，$N={n}$ 个元素。",
                f"决策变量维度：$N={n}$ 个二元变量 $x_i \\in \\{{0,1\\}}$ 表示元素归入哪一组。",
                "约束硬性：无显式约束；目标是两组之和尽量相等（差的平方最小）。",
                "输出：两组划分比特串、组间差值与资源统计摘要。",
            ],
        },
        "modeling": {
            "vars": "$x_i\\in\\{0,1\\}$ 选择元素 $a_i$ 的分组；自旋 $s_i=1-2x_i\\in\\{+1,-1\\}$。",
            "objective": "最小化两组和之差的平方：$\\min_{x}\\; \\left(\\sum_i a_i s_i\\right)^2 = \\left(\\sum_i a_i(1-2x_i)\\right)^2$。",
            "constraints": "无显式约束；划分平衡性由平方目标隐式驱动。",
            "mapping": "展开平方并代入 $s_i=1-2x_i$ 得到 $H_C=\\sum_i h_i Z_i+\\sum_{i<j}J_{ij}Z_iZ_j+\\text{const}$，基态对应最均衡划分。",
            "ptype": "无约束二次二值优化（QUBO）/ 数集划分，适配 QAOA。",
            "shots": QAOA_SHOTS,
            "iters": f"COBYLA `maxiter={maxiter}`，{restarts} 次随机重启取最优",
            "sim": QAOA_SIM,
            "framework": QAOA_FRAMEWORK,
            "reason": "数集划分可精确写成 Ising 二次型，是验证 QAOA 表达力的经典算例；浅层线路多重启在小规模即能找到平衡划分。",
        },
        "program": {
            "target": QAOA_TARGET,
            "deps": "`qiskit>=1.2`，`numpy>=1.24`，`scipy>=1.10`。",
            "desc": "构造整数集合 → 由差平方展开 QUBO → 转 Ising → QAOA 多重启优化 → 由末态概率输出划分与组间差。",
            "cmd": f"python numpart_qaoa_n{n}.py",
            "expect": "打印 num_qubits={num_qubits}、circuit.depth()={depth}、QAOA 解比特串 {bitstring}、目标（差平方）{objective}、与暴力最优 {optimum} 的近似比 {approx_ratio}。",
        },
        "code": code,
    }
    return spec, f"numpart__QAOA__{n}", f"numpart_qaoa_n{n}"


# ===========================================================================
# Generic QUBO -> QAOA spec builder, for many real-world problems.
# `texts` provides all narrative fields; `linear/quad/const` define the QUBO.
# ===========================================================================
def generic_qubo(
    n, linear, quad, const, key, fname_stub, texts, reps=None, maxiter=None, shots=4096
):
    title = texts["title"]
    a_reps, a_maxiter, a_restarts = qaoa_budget(n)
    reps = a_reps if reps is None else reps
    maxiter = a_maxiter if maxiter is None else maxiter
    code = qaoa.build_qaoa_code(
        title, n, linear, quad, const, reps=reps, maxiter=maxiter, shots=shots, restarts=a_restarts
    )
    spec = {
        "scenario": {
            "domain": texts["domain"],
            "need": texts["need"],
            "goal": texts["goal"],
            "bounds": texts["bounds"],
        },
        "modeling": {
            "vars": texts["vars"],
            "objective": texts["objective"],
            "constraints": texts["constraints"],
            "mapping": texts["mapping"],
            "ptype": texts["ptype"],
            "shots": QAOA_SHOTS,
            "iters": f"COBYLA `maxiter={maxiter}`，{a_restarts} 次随机重启取最优",
            "sim": QAOA_SIM,
            "framework": QAOA_FRAMEWORK,
            "reason": texts["reason"],
        },
        "program": {
            "target": QAOA_TARGET,
            "deps": "`qiskit>=1.2`，`numpy>=1.24`，`scipy>=1.10`。",
            "desc": texts["desc"],
            "cmd": f"python {fname_stub}.py",
            "expect": "打印 num_qubits={num_qubits}、circuit.depth()={depth}、num Pauli terms={num_terms}、QAOA 解比特串 {bitstring}、目标值 {objective}、与暴力最优 {optimum} 的近似比 {approx_ratio}。",
        },
        "code": code,
    }
    return spec, key, fname_stub
