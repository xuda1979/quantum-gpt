"""Concrete VQE case specs: molecular ground states and spin-model ground
states. Uses EfficientSU2 + SLSQP (verified tight convergence)."""

from __future__ import annotations

from . import vqe


def _mol_spec(name_cn, formula, terms, ref_str, domain, need, goal, fname, fp, n=2, reps=2):
    code = vqe.build_vqe_code(
        title=f"{formula}",
        terms=terms,
        ansatz_kind="EfficientSU2",
        nq=n,
        reps=reps,
        optimizer="SLSQP",
        maxiter=150,
        restarts=4,
        seed=11,
    )
    spec = {
        "scenario": {
            "domain": domain,
            "need": need,
            "goal": goal,
            "bounds": [
                f"输入：{name_cn}的 {n} 量子比特锥化泡利哈密顿量系数表（STO-3G 近似）。",
                "决策变量维度：变分线路参数 $\\boldsymbol{\\theta}$，维度由 Ansatz 决定。",
                "约束硬性：无显式不等式约束；物理对称性由锥化哈密顿量隐式保证。",
                "输出：基态能量估计 $E_0$（Hartree）、最优参数与资源统计摘要。",
            ],
        },
        "modeling": {
            "vars": "$\\boldsymbol{\\theta}\\in\\mathbb{R}^{p}$ 为变分参数；$|\\psi(\\boldsymbol{\\theta})\\rangle=U(\\boldsymbol{\\theta})|0\\rangle^{\\otimes n}$ 为试探态。",
            "objective": "由变分原理最小化能量期望：$E_0=\\min_{\\boldsymbol{\\theta}}\\langle\\psi(\\boldsymbol{\\theta})|\\hat{H}|\\psi(\\boldsymbol{\\theta})\\rangle$。",
            "constraints": "试探态归一化 $\\langle\\psi|\\psi\\rangle=1$ 由幺正演化自动满足，无需惩罚项。",
            "mapping": f"二次量子化并锥化后哈密顿量写为泡利线性组合 $\\hat{{H}}=\\sum_k c_k P_k$，参考基态能量约 {ref_str} Ha。",
            "ptype": "厄米算符基态求解，适配变分量子本征求解器 (VQE)。",
            "shots": "状态向量精确期望，无采样噪声（`StatevectorEstimator`）",
            "iters": "SLSQP `maxiter=150`，4 次随机重启取最优",
            "sim": "全状态向量（`StatevectorEstimator`）",
            "framework": "Qiskit ($\\ge 1.2$) + `qiskit.primitives` (`StatevectorEstimator`) + `EfficientSU2` + SciPy SLSQP。",
            "reason": "分子基态是 VQE 标准范式；锥化后比特数少，`EfficientSU2`（$R_y/R_z$ 旋转 + 纠缠）配合梯度型 SLSQP 在低维光滑能面上收敛快且精确，纯 CPU 毫秒级闭环并与精确对角化核对。",
        },
        "program": {
            "target": "Qiskit 1.x Primitives V2（`StatevectorEstimator`），`EfficientSU2` 硬件高效 Ansatz。",
            "deps": "`qiskit>=1.2`，`numpy>=1.24`，`scipy>=1.10`。",
            "desc": f"以 `SparsePauliOp` 写入{name_cn}哈密顿量 → `EfficientSU2` 构造 Ansatz → `StatevectorEstimator` 求 $\\langle H\\rangle$ → SLSQP 多重启最小化 → 与精确对角化比对误差并打印资源摘要。",
            "cmd": f"python {fname}.py",
            "expect": "打印 num_qubits={num_qubits}、circuit.depth()={depth}、泡利项数={num_terms}、VQE 能量 {objective} Ha 与精确值 {reference} Ha（绝对误差 {abs_error:.1e}）。",
        },
        "code": code,
    }
    return spec, fp, fname


def h2(domain, need, goal):
    return _mol_spec(
        "氢分子 $H_2$",
        "H2",
        vqe.H2_TERMS,
        "-1.857",
        domain,
        need,
        goal,
        "h2_vqe_n2",
        "chem_h2__VQE__2",
    )


def hehp(domain, need, goal):
    return _mol_spec(
        "氦氢离子 $HeH^{+}$",
        "HeH+",
        vqe.HEHP_TERMS,
        "-3.99",
        domain,
        need,
        goal,
        "hehp_vqe_n2",
        "chem_hehp__VQE__2",
    )


def tfim(n, seed, domain, need, goal):
    terms = vqe.tfim_terms(n)
    code = vqe.build_vqe_code(
        title=f"TFIM N={n}",
        terms=terms,
        ansatz_kind="EfficientSU2",
        nq=n,
        reps=3,
        optimizer="SLSQP",
        maxiter=200,
        restarts=5,
        seed=seed,
    )
    spec = {
        "scenario": {
            "domain": domain,
            "need": need,
            "goal": goal,
            "bounds": [
                f"输入：横场 Ising 链，$N={n}$ 个自旋，开边界，耦合 $J=1$、横场 $h=1$。",
                "决策变量维度：变分参数 $\\boldsymbol{\\theta}$，维度由 `EfficientSU2` 层数决定。",
                "约束硬性：无显式约束；目标是求哈密顿量最小本征值（基态能量）。",
                "输出：基态能量估计、最优参数与资源统计摘要。",
            ],
        },
        "modeling": {
            "vars": "$Z_i, X_i$ 为第 $i$ 个自旋的泡利算符；$\\boldsymbol{\\theta}$ 为变分参数。",
            "objective": "最小化能量期望：$E_0=\\min_{\\boldsymbol{\\theta}}\\langle\\psi(\\boldsymbol{\\theta})|\\hat{H}|\\psi(\\boldsymbol{\\theta})\\rangle$。",
            "constraints": "试探态归一化由幺正线路自动满足，无需惩罚项。",
            "mapping": "横场 Ising 哈密顿量 $\\hat{H}=-J\\sum_{i}Z_iZ_{i+1}-h\\sum_i X_i$，其基态为量子相变研究的核心对象。",
            "ptype": "凝聚态自旋模型基态求解，适配 VQE。",
            "shots": "状态向量精确期望（`StatevectorEstimator`）",
            "iters": "SLSQP `maxiter=200`，5 次随机重启取最优",
            "sim": "全状态向量（`StatevectorEstimator`）",
            "framework": "Qiskit ($\\ge 1.2$) + `qiskit.primitives` + `EfficientSU2` + SciPy SLSQP。",
            "reason": "横场 Ising 是量子多体与相变研究的范式模型；`EfficientSU2` 含 $R_x$ 类等价旋转可覆盖横场基态，梯度型 SLSQP 多重启在该规模逼近精确基态。",
        },
        "program": {
            "target": "Qiskit 1.x Primitives V2（`StatevectorEstimator`），`EfficientSU2`。",
            "deps": "`qiskit>=1.2`，`numpy>=1.24`，`scipy>=1.10`。",
            "desc": "构造横场 Ising 哈密顿量 → `EfficientSU2` Ansatz → SLSQP 多重启最小化 $\\langle H\\rangle$ → 与精确对角化比对并打印资源摘要。",
            "cmd": f"python tfim_vqe_n{n}.py",
            "expect": "打印 num_qubits={num_qubits}、circuit.depth()={depth}、泡利项数={num_terms}、VQE 能量 {objective} 与精确值 {reference}（误差 {abs_error:.1e}）。",
        },
        "code": code,
    }
    return spec, f"tfim__VQE__{n}", f"tfim_vqe_n{n}"


def heisenberg(n, seed, domain, need, goal):
    terms = vqe.heisenberg_terms(n)
    code = vqe.build_vqe_code(
        title=f"Heisenberg N={n}",
        terms=terms,
        ansatz_kind="EfficientSU2",
        nq=n,
        reps=3,
        optimizer="SLSQP",
        maxiter=200,
        restarts=6,
        seed=seed,
    )
    spec = {
        "scenario": {
            "domain": domain,
            "need": need,
            "goal": goal,
            "bounds": [
                f"输入：各向同性 Heisenberg 链，$N={n}$ 个自旋，开边界，$J_x=J_y=J_z=1$。",
                "决策变量维度：变分参数 $\\boldsymbol{\\theta}$，维度由 Ansatz 决定。",
                "约束硬性：无显式约束；目标是求基态能量。",
                "输出：基态能量估计、最优参数与资源统计摘要。",
            ],
        },
        "modeling": {
            "vars": "$X_i, Y_i, Z_i$ 为第 $i$ 个自旋的泡利算符；$\\boldsymbol{\\theta}$ 为变分参数。",
            "objective": "最小化能量期望：$E_0=\\min_{\\boldsymbol{\\theta}}\\langle\\psi(\\boldsymbol{\\theta})|\\hat{H}|\\psi(\\boldsymbol{\\theta})\\rangle$。",
            "constraints": "归一化由幺正线路自动满足，无需惩罚项。",
            "mapping": "Heisenberg 哈密顿量 $\\hat{H}=\\sum_i (X_iX_{i+1}+Y_iY_{i+1}+Z_iZ_{i+1})$，描述磁性材料的自旋交换相互作用。",
            "ptype": "凝聚态自旋模型基态求解，适配 VQE。",
            "shots": "状态向量精确期望（`StatevectorEstimator`）",
            "iters": "SLSQP `maxiter=200`，6 次随机重启取最优",
            "sim": "全状态向量（`StatevectorEstimator`）",
            "framework": "Qiskit ($\\ge 1.2$) + `qiskit.primitives` + `EfficientSU2` + SciPy SLSQP。",
            "reason": "Heisenberg 模型是量子磁性的基石；纠缠型 `EfficientSU2` 能表达其强关联基态，梯度型 SLSQP 多重启可逼近精确能量。",
        },
        "program": {
            "target": "Qiskit 1.x Primitives V2（`StatevectorEstimator`），`EfficientSU2`。",
            "deps": "`qiskit>=1.2`，`numpy>=1.24`，`scipy>=1.10`。",
            "desc": "构造 Heisenberg 哈密顿量 → `EfficientSU2` Ansatz → SLSQP 多重启最小化 → 与精确对角化比对并打印资源摘要。",
            "cmd": f"python heisenberg_vqe_n{n}.py",
            "expect": "打印 num_qubits={num_qubits}、circuit.depth()={depth}、泡利项数={num_terms}、VQE 能量 {objective} 与精确值 {reference}（误差 {abs_error:.1e}）。",
        },
        "code": code,
    }
    return spec, f"heisenberg__VQE__{n}", f"heisenberg_vqe_n{n}"
