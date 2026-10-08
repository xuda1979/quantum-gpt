"""Concrete specs for VQC / QPE / Grover families."""

from __future__ import annotations

from . import algos


def vqc(n, reps, seed, domain, need, goal):
    code = algos.build_vqc_code(f"VQC N={n}", n, reps, 150, seed, restarts=5)
    spec = {
        "scenario": {
            "domain": domain,
            "need": need,
            "goal": goal,
            "bounds": [
                f"输入：${n}$ 维特征样本（两类各 12 个，共 24 个），标签 $y\\in\\{{-1,+1\\}}$。",
                f"决策变量维度：变分权重 $\\boldsymbol{{w}}$，由 `RealAmplitudes(reps={reps})` 决定。",
                "约束硬性：无显式约束；目标是最小化预测与标签的均方误差。",
                "输出：训练损失、训练集准确率、最优权重与资源统计摘要。",
            ],
        },
        "modeling": {
            "vars": "$\\boldsymbol{x}_i\\in\\mathbb{R}^{n}$ 为样本特征（角度编码到 $R_y$ 门）；$\\boldsymbol{w}$ 为变分权重；预测 $f(\\boldsymbol{x};\\boldsymbol{w})=\\langle\\psi|Z_0|\\psi\\rangle$。",
            "objective": "最小化均方损失：$\\min_{\\boldsymbol{w}}\\;\\frac{1}{M}\\sum_{i=1}^{M}\\big(f(\\boldsymbol{x}_i;\\boldsymbol{w})-y_i\\big)^2$。",
            "constraints": "无显式约束；分类边界由变分线路与观测量 $Z_0$ 隐式决定。",
            "mapping": "数据经 $R_y(x_j)$ 角度编码进量子态，再由参数化纠缠线路演化；测量首比特 $Z_0$ 期望作为决策函数，符号给出类别。",
            "ptype": "监督二分类 / 变分量子分类器 (VQC)，属量子机器学习。",
            "shots": "状态向量精确期望，无采样噪声（`StatevectorEstimator`）",
            "iters": "COBYLA `maxiter=150`，5 次随机重启取最优",
            "sim": "全状态向量（`StatevectorEstimator`）",
            "framework": "Qiskit ($\\ge 1.2$) + `qiskit.primitives` (`StatevectorEstimator`) + `RealAmplitudes` + SciPy COBYLA。",
            "reason": "VQC 是量子机器学习的代表；角度编码 + `RealAmplitudes` 在小样本可分数据上表达力充足，`StatevectorEstimator` 提供无噪期望，纯 CPU 秒级闭环并可核对训练准确率。",
        },
        "program": {
            "target": "Qiskit 1.x Primitives V2（`StatevectorEstimator`），角度编码 + `RealAmplitudes`。",
            "deps": "`qiskit>=1.2`，`numpy>=1.24`，`scipy>=1.10`。",
            "desc": "生成两类可分高斯样本 → 角度编码特征 + `RealAmplitudes` 变分块 → 以 $Z_0$ 期望为决策函数 → COBYLA 最小化均方损失 → 打印训练准确率与资源摘要。",
            "cmd": f"python vqc_n{n}.py",
            "expect": "打印 num_qubits={num_qubits}、circuit.depth()={depth}、可训练参数 {num_params}、最终损失 {objective}、训练准确率约 1.0。",
        },
        "code": code,
    }
    return spec, f"vqc__VQC__{n}_r{reps}", f"vqc_n{n}_r{reps}"


def qpe(n_count, num, den, domain, need, goal):
    phase = num / den
    frac = f"\\tfrac{{{num}}}{{{den}}}"
    code = algos.build_qpe_code(f"QPE phase {num}/{den}", n_count, phase, 4096)
    total_q = n_count + 1
    spec = {
        "scenario": {
            "domain": domain,
            "need": need,
            "goal": goal,
            "bounds": [
                f"输入：相位门 $U=P(2\\pi\\varphi)$，真实相位 $\\varphi={frac}$，本征态 $|1\\rangle$。",
                f"决策变量维度：$n_{{count}}={n_count}$ 个计数比特 + 1 个本征态比特，共 {total_q} 比特。",
                "约束硬性：相位需落在 $[0,1)$；估计精度受计数比特数限制。",
                "输出：估计相位 $\\hat{\\varphi}$、与真值的绝对误差及资源统计摘要。",
            ],
        },
        "modeling": {
            "vars": "$\\varphi\\in[0,1)$ 为待估相位；$|1\\rangle$ 为 $U$ 的本征态，满足 $U|1\\rangle=e^{2\\pi i\\varphi}|1\\rangle$。",
            "objective": f"通过逆量子傅里叶变换读出相位二进制近似：$\\hat{{\\varphi}}=\\dfrac{{k}}{{2^{{{n_count}}}}}$，使 $\\hat{{\\varphi}}\\approx\\varphi={frac}$。",
            "constraints": f"精度受计数比特数约束，分辨率为 $2^{{-{n_count}}}$；本例 $\\varphi$ 可被精确表示故误差为 0。",
            "mapping": "对计数比特做 Hadamard 叠加，受控施加 $U^{2^j}$ 写入相位，再做逆 QFT 把相位映射到计算基测量结果。",
            "ptype": "量子相位估计 (QPE)，属本征值/谱估计算法。",
            "shots": "4096（采样统计）",
            "iters": "无经典优化迭代（QPE 为确定性线路 + 采样）",
            "sim": "全状态向量采样（`StatevectorSampler`）",
            "framework": "Qiskit ($\\ge 1.2$) + `qiskit.primitives` (`StatevectorSampler`) + `QFT`（逆变换）。",
            "reason": "QPE 是 Shor 算法、量子化学能量估计等的核心子程序；这里用可精确表示的相位验证逆 QFT 读出的正确性，纯 CPU 采样秒级闭环。",
        },
        "program": {
            "target": "Qiskit 1.x Primitives V2（`StatevectorSampler`），`QFT(inverse=True)`。",
            "deps": "`qiskit>=1.2`，`numpy>=1.24`。",
            "desc": "构造计数寄存器 + 本征态比特 → Hadamard 叠加并受控施加相位门幂次 → 逆 QFT → 采样读出相位二进制并换算 → 与真值比对误差。",
            "cmd": f"python qpe_n{n_count}.py",
            "expect": "打印 num_qubits={num_qubits}、circuit.depth()={depth}、估计相位 {objective}（绝对误差 {abs_error:.1e}）。",
        },
        "code": code,
    }
    return spec, f"qpe__QPE__{total_q}_{num}_{den}", f"qpe_n{n_count}_{num}_{den}"


def grover(n, marked, domain, need, goal):
    code = algos.build_grover_code(f"Grover N={n}", n, marked, 4096)
    spec = {
        "scenario": {
            "domain": domain,
            "need": need,
            "goal": goal,
            "bounds": [
                f"输入：$2^{{{n}}}$ 个等概率候选状态，唯一目标比特串为 `{marked}`。",
                f"决策变量维度：$N={n}$ 个量子比特表示搜索空间。",
                "约束硬性：oracle 仅标记目标态；迭代次数须取 $\\approx\\frac{\\pi}{4}\\sqrt{2^N}$ 以最大化命中概率。",
                "输出：搜索命中的比特串、命中概率及资源统计摘要。",
            ],
        },
        "modeling": {
            "vars": "搜索空间 $\\{0,1\\}^{N}$；oracle $O$ 对目标态施加相位翻转 $O|t\\rangle=-|t\\rangle$。",
            "objective": "通过振幅放大最大化目标态测得概率：迭代 $G=D\\cdot O$（$D$ 为关于均匀叠加的反射）约 $\\lfloor\\frac{\\pi}{4}\\sqrt{2^N}\\rfloor$ 次。",
            "constraints": f"迭代次数过多会使概率回落（过旋转），故取最优整数次；目标态 `{marked}` 由相位 oracle 唯一标记。",
            "mapping": "Hadamard 制备均匀叠加 → 相位 oracle 标记目标 → 扩散算子放大目标振幅，重复至接近 1 的命中概率。",
            "ptype": "无结构搜索 / Grover 振幅放大，提供平方加速。",
            "shots": "4096（采样统计）",
            "iters": "无经典优化（Grover 迭代次数由 $\\frac{\\pi}{4}\\sqrt{2^N}$ 解析给定）",
            "sim": "全状态向量采样（`StatevectorSampler`）",
            "framework": "Qiskit ($\\ge 1.2$) + `qiskit.primitives` (`StatevectorSampler`) + `GroverOperator`。",
            "reason": "Grover 是无结构搜索的标志性算法，提供 $O(\\sqrt{N})$ 平方加速；用相位 oracle 标记单一目标，纯 CPU 采样秒级闭环并可核对命中概率。",
        },
        "program": {
            "target": "Qiskit 1.x Primitives V2（`StatevectorSampler`），`GroverOperator`。",
            "deps": "`qiskit>=1.2`，`numpy>=1.24`。",
            "desc": "构造相位 oracle（多控 Z 标记目标）→ `GroverOperator` 扩散 → 按 $\\frac{\\pi}{4}\\sqrt{2^N}$ 迭代 → 采样输出命中比特串与概率。",
            "cmd": f"python grover_n{n}.py",
            "expect": "打印 num_qubits={num_qubits}、circuit.depth()={depth}、命中比特串与命中概率 {objective}（应接近 1）。",
        },
        "code": code,
    }
    return spec, f"grover__Grover__{n}_{marked}", f"grover_n{n}_{marked}"
