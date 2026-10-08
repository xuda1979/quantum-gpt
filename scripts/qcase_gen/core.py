"""Generator for verified quantum SFT cases.

Design: the embedded Python code in each case is the single source of truth.
The generator renders the code, executes it, parses a standardized
`RESULT_JSON {...}` line, and injects the *verified* numbers
(num_qubits / depth / num_params / num_terms / objective) into the Markdown.
This guarantees Section 2 resource numbers always match what the code actually
builds and prints, so there can be no logic/science/layout drift.

Output: one .md file per case in 模版与数据/生成的数据/ following the template
structure (Sections 1-3; metadata tracked separately in _manifest.json).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(ROOT, "模版与数据", "生成的数据")
PYEXE = sys.executable


def mem_estimate(nq: int) -> str:
    b = (2**nq) * 16
    if b < 1024:
        return f"$2^{{{nq}}}\\times 16\\,\\text{{B}} = {b}\\,\\text{{B}}$（complex128）"
    if b < 1024**2:
        return f"$2^{{{nq}}}\\times 16\\,\\text{{B}} = {b/1024:.2f}\\,\\text{{KB}}$（complex128）"
    if b < 1024**3:
        return (
            f"$2^{{{nq}}}\\times 16\\,\\text{{B}} = {b/1024**2:.2f}\\,\\text{{MB}}$（complex128）"
        )
    return f"$2^{{{nq}}}\\times 16\\,\\text{{B}} = {b/1024**3:.2f}\\,\\text{{GB}}$（complex128）"


def run_script(code: str):
    """Run an embedded script, return (ok, result_dict, stdout, stderr)."""
    tmp = os.path.join("/tmp", "qcase_run.py")
    with open(tmp, "w") as f:
        f.write(code)
    # Cap BLAS/OMP threads to avoid oversubscription (qiskit threads x BLAS threads
    # can cause 10-100x slowdowns from contention on multicore machines).
    env = dict(os.environ)
    env.update(
        {
            "OMP_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
            "VECLIB_MAXIMUM_THREADS": "1",
            "RAYON_NUM_THREADS": "1",
            "QISKIT_NUM_PROCS": "1",
            "QISKIT_IN_PARALLEL": "TRUE",
        }
    )
    try:
        p = subprocess.run([PYEXE, tmp], capture_output=True, text=True, timeout=300, env=env)
    except subprocess.TimeoutExpired:
        return False, None, "", "TIMEOUT"
    out = p.stdout
    res = None
    for line in out.splitlines():
        if line.startswith("RESULT_JSON "):
            try:
                res = json.loads(line[len("RESULT_JSON ") :])
            except Exception as e:  # noqa
                return False, None, out, f"bad json: {e}\n{p.stderr}"
    if p.returncode != 0 or res is None:
        return False, None, out, p.stderr
    return True, res, out, p.stderr


def render_md(spec: dict, res: dict) -> str:
    """Assemble the Markdown case from spec + verified run results."""
    nq = res["num_qubits"]
    depth = res["depth"]
    nparams = res["num_params"]
    nterms = res["num_terms"]
    sd = spec["scenario"]
    md = []
    md.append("## 1. 场景需求 (Scenario Demand)\n")
    md.append(f"- **领域场景**: {sd['domain']}")
    md.append(f"- **用户原始需求**: {sd['need']}")
    md.append(f"- **核心目标**: {sd['goal']}")
    md.append("- **目标边界与输入输出**:")
    for b in sd["bounds"]:
        md.append(f"  - {b}")
    md.append("")
    md.append("## 2. 建模分析 (Modeling & Solver)\n")
    mo = spec["modeling"]
    md.append("- **数学建模与公式 (LaTeX)**:")
    md.append(f"- **变量定义**: {mo['vars']}")
    md.append(f"- **目标函数**: {mo['objective']}")
    md.append(f"- **约束条件**: {mo['constraints']}")
    md.append(f"- **量子模型映射**: {mo['mapping']}")
    md.append(f"- **问题类型判断**: {mo['ptype']}")
    md.append("- **异构资源联合预估 (量子Qubits + 经典模拟显存)**:")
    md.append(f"  - 逻辑量子比特数: {nq}")
    md.append(f"  - 线路深度: {depth}（由代码运行时 `circuit.depth()` 实测）")
    md.append(f"  - 参数量: {nparams}")
    md.append(f"  - 哈密顿量/泡利项数: {nterms}")
    md.append(f"  - shots/采样次数: {mo['shots']}")
    md.append(f"  - 优化迭代次数: {mo['iters']}")
    md.append(f"  - 模拟模式: {mo['sim']}")
    md.append(f"  - 状态向量显存估算: {mem_estimate(nq)}")
    md.append(f"- **求解框架选择**: {mo['framework']}")
    md.append(f"- **选择理由**: {mo['reason']}")
    md.append("")
    md.append("## 3. 辅助编程 (Assisted Programming)\n")
    pr = spec["program"]
    md.append(f"- **目标框架 (注明API版本特性)**: {pr['target']}")
    md.append(f"- **依赖版本**: {pr['deps']}")
    md.append(f"- **代码功能说明**: {pr['desc']}")
    md.append(f"- **运行命令**: `{pr['cmd']}`")
    md.append(f"- **预期输出摘要**: {pr['expect'].format(**res)}")
    md.append("- **源码实现**:\n")
    md.append("```python")
    md.append(spec["code"].strip("\n"))
    md.append("```")
    md.append("")
    return "\n".join(md)


# ---------------------------------------------------------------------------
# Render-rule self-checks (catch the pitfalls we already fixed)
# ---------------------------------------------------------------------------
def check_render(md: str) -> list[str]:
    errs = []
    if "<think>" in md or "</think>" in md:
        errs.append("contains <think> tag")
    if re.search(r"<(div|span|br|p|table)\b", md):
        errs.append("contains raw HTML tag")
    if "## 0." in md:
        errs.append("contains Section 0")
    # find math segments and check for markdown-escape backslashes inside
    for m in re.finditer(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", md):
        seg = m.group(1)
        if re.search(r"\\[\*_#]", seg):
            errs.append(f"markdown-escape inside math: {seg[:40]}")
    # balanced single $ (rough): count of $ outside code fences should be even
    body = re.sub(r"```.*?```", "", md, flags=re.S)
    if body.count("$") % 2 != 0:
        errs.append("unbalanced $ delimiters")
    for sec in ["## 1.", "## 2.", "## 3."]:
        if sec not in md:
            errs.append(f"missing {sec}")
    return errs
