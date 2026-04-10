import os

with open("research/RESEARCH-REPORT.tex", "r", encoding="utf-8") as f:
    text = f.read()

# make sure graphicx package is included
if "\\usepackage{graphicx}" not in text:
    text = text.replace("\\usepackage{hyperref}", "\\usepackage{graphicx}\n\\usepackage{hyperref}")

figure_tex = r"""

\begin{figure}[htbp]
\centering
\includegraphics[width=0.95\textwidth]{figures/claude-code-agent.png}
\caption{Claude Code 在本项目的自动化研发循环（Autonomous R\&D Loop）中的运行界面。通过多终端并行处理本地执行、远端 Huanxin Shell 与系统检查，跟踪溯源模型数据，协助打通远端与本地的结果同步。}
\label{fig:claude-code-agent}
\end{figure}
"""

anchor = r"的“叙事层”。它将一个研发循环明确拆成多个 stage，例如本地评测 gate、holdout integrity、模型来源审计、快照校验、paper router warmup、remote launcher gate 等，并把状态输出成 \code{reports/autonomous_rd_cycle_*.json} 与命令单工件。"

idx = text.find("的“叙事层”。它将一个")

if idx != -1:
    insert_idx = text.find("\n\n", idx)
    if insert_idx != -1:
        if "claude-code-agent" not in text:
            text = text[:insert_idx] + figure_tex + text[insert_idx:]

with open("research/RESEARCH-REPORT.tex", "w", encoding="utf-8") as f:
    f.write(text)

os.makedirs("research/figures", exist_ok=True)
