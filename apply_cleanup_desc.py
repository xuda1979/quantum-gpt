import sys

with open("research/RESEARCH-REPORT.tex", "r", encoding="utf-8") as f:
    text = f.read()

# exact string to remove (if multiple)
desc = r"""
\vspace{1.5em}
\noindent \textbf{核心数据集的详细定位与构成：}
\begin{itemize}
    \item \textbf{\code{template-large-v1}}：宽口径监督微调（SFT）基础数据集，总计包含超过 2000 条高质量记录。结合了量子计算逻辑与经典软件工程代码片段，旨在让模型兼具两者的基础编程能力，而不偏废。
    \item \textbf{\code{mixed-holdout-v1}}：包含 1440 条量子代码和经典软件代码的混合评测集。采用严格的 \code{task disjoint}（任务隔离）策略构造，确保训练与测试在任务层级完全正交，用作核心泛化能力验证的基准指标（Benchmark）。
    \item \textbf{\code{quantum-large-v1}} 与 \textbf{\code{quantum-holdout-v1}}：针对量子域打造的专属训练和纯量子严格未见测试集。前者使模型快速从普遍软件领域适配到深度的量子逻辑体系，后者严卡数据污染确保零重合，用来检验面对陌生量子协议时的真实推理水准。
    \item \textbf{\code{quantum-focus-v1}} 与 \textbf{\code{quantum-hard-v1}}：均是小规模专门子集。前者主要跑通快速验证回路（针对学习率、Batch Size 的小周期试验），后者汇总了在历次评测中暴露的“硬骨头”极端难例，服务于后期的专项突破和高难度动作强化。
    \item \textbf{\code{paper-router/messages}}：专供 Gemma 这类基于混合专家（MoE）结构模型的路由层进行“微热身”（Warmup）的前置型轻量数据，防患路由塌缩和单极化分布。
\end{itemize}
"""

while desc in text:
    text = text.replace(desc, "")

anchor = r"\caption{当前主要数据集的规模与角色。}"
idx_anchor = text.find(anchor)
if idx_anchor != -1:
    table_end = text.find(r"\end{table}", idx_anchor) + len(r"\end{table}")
    text = text[:table_end] + "\n" + desc + "\n" + text[table_end:]

with open("research/RESEARCH-REPORT.tex", "w", encoding="utf-8") as f:
    f.write(text)
