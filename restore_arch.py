#!/usr/bin/env python3
"""Restore lost content in the 软件架构 section of RESEARCH-REPORT.tex."""

with open("research/RESEARCH-REPORT.tex", "r", encoding="utf-8") as f:
    text = f.read()

# Save backup
with open("research/RESEARCH-REPORT.tex.bak", "w", encoding="utf-8") as f:
    f.write(text)

replacements = [
    # 1. Section title + fbox + subsection title
    (
        "\\section{软件架构}\n\n\\subsection{总体设计原则：本地优先}\n\n"
        "当前研发架构的一个核心原则是：\\textbf{先在本地验证，再通过 S3 relay 与 Huanxin shell 把已验证代码送到 ai2。}"
        " 这比\u201c直接在浏览器里不断手改远端文件\u201d更慢一些，但它换来了至关重要的可复用性与可追溯性。\n\n"
        "这一架构可以概括为如下五层：\n\n"
        "  \\par 本地代码与测试层：\\code{training/}、\\code{evals/}、\\code{tests/}；\n"
        "  \\par 数据与工件层：\\code{data/generated/}、\\code{outputs/}、\\code{reports/}、\\code{artifacts/}；\n"
        "  \\par 远端同步层：\\code{scripts/push_to_s3.sh}、\\code{scripts/ai2_sync_from_s3.sh}；\n"
        "  \\par 远端运行层：\\code{scripts/ai2_shell.sh}、\\code{scripts/ai2_job.sh}、\\code{scripts/queue_ai2_timeboxed_pipeline.sh}；\n"
        "  \\par 研究与汇报层：\\code{research/papers/} 与 \\code{research/RESEARCH-REPORT.tex}。",
        # replacement
        "\\section{研发架构（软件架构）}\n\n"
        "\\noindent\\fbox{\\parbox{0.96\\textwidth}{%\n"
        "\\textbf{本章关键结论：}研发架构的核心原则是\u201c分层、留痕、可恢复\u201d。先在本地验证，再通过 S3 relay 送到远端；trainer 与 plugin 分离；所有实验状态都沉淀为工件。即使会话中断，研发主线也能从 state 文件恢复。}}\n\n"
        "\\subsection{local-first 控制面}\n\n"
        "当前研发架构的一个核心原则是：\\textbf{先在本地验证，再通过 S3 relay 与 Huanxin shell 把已验证代码送到 ai2。}"
        " 这比\u201c直接在浏览器里不断手改远端文件\u201d更慢一些，但它换来了非常重要的可复用性与可追溯性。\n\n"
        "这一控制面可以概括为如下五层：\n"
        "\\begin{itemize}\n"
        "  \\item 本地代码与测试层：\\code{training/}、\\code{evals/}、\\code{tests/}；\n"
        "  \\item 数据与工件层：\\code{data/generated/}、\\code{outputs/}、\\code{reports/}、\\code{artifacts/}；\n"
        "  \\item 远端同步层：\\code{scripts/push_to_s3.sh}、\\code{scripts/ai2_sync_from_s3.sh}；\n"
        "  \\item 远端运行层：\\code{scripts/ai2_shell.sh}、\\code{scripts/ai2_job.sh}、\\code{scripts/queue_ai2_timeboxed_pipeline.sh}；\n"
        "  \\item 研究与汇报层：\\code{research/papers/} 与 \\code{research/RESEARCH-REPORT.tex}。\n"
        "\\end{itemize}"
    ),
    # 2. ai2 subsection + fbox
    (
        "\\subsection{远端资产分布（ai2 工作目录）}\n\n"
        "\\medskip\n"
        "为确保研发资产的可追溯性与项目交接规范，本节将远端节点上的资产分布按\\textbf{基座模型、数据集、微调产物、代码入口}四类列清。",
        "\\subsection{ai2 远端工作目录与资产分布}\n\n"
        "\\noindent\\fbox{\\parbox{0.96\\textwidth}{%\n"
        "\\textbf{ai2 唯一工作目录：}\\code{/root/root/work/quantum-gpt}。本项目在 ai2 上的所有训练、评测、同步、数据与模型操作，均以此目录为根目录执行。下文所有相对路径，均相对于此目录。}}\n\n"
        "\\medskip\n"
        "为确保研发资产的可追溯性与项目交接规范，本节将远端节点上的资产分布按\\textbf{基座模型、数据集、微调产物、代码入口}四类列清。"
    ),
    # 3. subsection title
    ("\\subsection{控制面分层与故障定位}", "\\subsection{控制面组件与职责边界}"),
    # 4. paragraph wording
    ("这种清晰的分层有助于持续提升远端运维的效率与稳定性。", "这种精确的分层使得运维效率大幅提升。"),
    # 5. 自动化研发循环 (remove claude code figure, restore original text)
    (
        "\\subsection{自动化研发循环}\n\n"
        "\\code{scripts/run_autonomous_rd_cycle.py} 代表的是控制面的\u201c叙事层\u201d。"
        "它将一个研发循环明确拆成多个 stage，例如本地评测 gate、holdout integrity、模型来源审计、快照校验、paper router warmup、remote launcher gate 等，"
        "并把状态输出成 \\code{reports/autonomous_rd_cycle_*.json} 与命令单工件。\n\n"
        "\\begin{figure}[htbp]\n"
        "\\centering\n"
        "\\includegraphics[width=0.95\\textwidth]{figures/claude-code-agent.png}\n"
        "\\caption{Claude Code 在本项目的自动化研发循环（Autonomous R\\&D Loop）中的运行界面。"
        "通过多终端并行处理本地执行、远端 Huanxin Shell 与系统检查，跟踪溯源模型数据，协助打通远端与本地的结果同步。}\n"
        "\\label{fig:claude-code-agent}\n"
        "\\end{figure}\n\n\n"
        "这类脚本的核心价值在于，它把\u201c接下来该做什么\u201d也变成了工件的一部分。即使发生团队交接或上下文切换，当前主线仍然可以从 state 文件中恢复。",
        "\\subsection{自治研发循环脚本}\n\n"
        "\\code{scripts/run_autonomous_rd_cycle.py} 代表的是控制面的\u201c叙事层\u201d。"
        "它将一个研发循环明确拆成多个 stage，例如本地评测 gate、holdout integrity、模型来源审计、快照校验、paper router warmup、remote launcher gate 等，"
        "并把状态输出成 \\code{reports/autonomous_rd_cycle_*.json} 与命令单工件。\n\n"
        "这类脚本的价值在于，它把\u201c接下来该做什么\u201d也变成了工件的一部分。即使团队交接或上下文切换，当前主线仍然可以从 state 文件中恢复。"
    ),
    # 6. 训练器与研究插件分层 (restore itemize)
    (
        "\\subsection{训练器与研究插件的分层}\n\n"
        "如果把每个研究方法都直接写进 \\code{qwen_sft_peft.py} 或 \\code{grpo_trainer.py}，"
        "训练器会很快变得难以维护。当前仓库通过 \\code{training/research_plugins.py} 保持分层设计，原因有三：\n\n"
        "  \\par 主干 trainer 应该稳定，方法实验应该可插拔；\n"
        "  \\par 报告中必须能说清\u201c哪些是已稳定主线，哪些只是研究插件\u201d；\n"
        "  \\par 远端快迭代时，最常同步的只是几个关键训练文件与 plugin，不必大面积覆盖整个仓库。",
        "\\subsection{训练器与研究方法为什么要分层}\n\n"
        "如果把每个研究想法都直接写进 \\code{qwen_sft_peft.py} 或 \\code{grpo_trainer.py}，"
        "训练器会很快变得难以维护。当前仓库通过 \\code{training/research_plugins.py} 维持分层，原因有三：\n"
        "\\begin{itemize}\n"
        "  \\item 主干 trainer 应该稳定，方法实验应该可插拔；\n"
        "  \\item 报告中必须能说清\u201c哪些是已稳定主线，哪些只是研究插件\u201d；\n"
        "  \\item 远端快迭代时，最常同步的只是几个关键训练文件与 plugin，不必整仓库胡乱覆盖。\n"
        "\\end{itemize}"
    ),
    # 7. 代码同步 (restore itemize)
    (
        "\\subsection{代码同步机制（S3 Relay）}\n\n"
        "远端连接与操作的架构原则是：\\textbf{浏览器只负责进入环境与 shell 终端；代码传输与文件更新统一走 S3 relay。}\n\n"
        "这个设计避免了两个典型问题：\n\n"
        "  \\par 浏览器页面状态波动时，代码同步也跟着不稳定；\n"
        "  \\par 远端脚本版本容易和本地脱节，导致\u201c本地修好了，远端还是旧 trainer\u201d。",
        "\\subsection{Huanxin 控制面为什么不能依赖浏览器上传代码}\n\n"
        "远端连接与操作的架构原则是：\\textbf{浏览器只负责进入环境与 shell 终端；代码传输与文件更新统一走 S3 relay。}\n\n"
        "这个设计避免了两个典型问题：\n"
        "\\begin{itemize}\n"
        "  \\item 浏览器页面状态波动时，代码同步也跟着不稳定；\n"
        "  \\item 远端脚本版本容易和本地脱节，导致\u201c本地修好了，远端还是旧 trainer\u201d。\n"
        "\\end{itemize}"
    ),
    # 8. 唯一正式报告 (restore itemize)
    (
        "\\subsection{唯一正式报告与证据索引}\n\n"
        "研究报告不是项目收尾时才补写的文档，而是研发架构的有机组成部分。理由很简单：\n\n"
        "  \\par 如果没有唯一正式报告，对外汇报的口径就会出现偏差；\n"
        "  \\par 如果没有单一 PDF 产物，版式统一、证据索引都无从谈起；\n"
        "  \\par 如果没有\u201c唯一报告 + 唯一证据索引\u201d，下一轮迭代很容易再次出现口径不一致、工件遗漏的问题。",
        "\\subsection{唯一正式报告为什么是架构的一部分}\n\n"
        "研究报告不是最终才补写的文档，而是研发架构的一部分。原因很简单：\n"
        "\\begin{itemize}\n"
        "  \\item 如果没有唯一正式报告，汇报口径就会漂移；\n"
        "  \\item 如果没有单一 PDF 产物，警告清理、版式统一、证据索引都无从谈起；\n"
        "  \\item 如果没有\u201c唯一报告 + 唯一证据索引\u201d，下一轮迭代很容易再次出现造口径、混口径、漏工件的问题。\n"
        "\\end{itemize}"
    ),
    # 9. 小结 -> 软件架构章节小结
    (
        "它不是项目的附属产物，而是项目能否进行高质量汇报与决策的必要基础设施。\n\n\\subsection{小结}",
        "它并不是项目的附庸，而是项目能否进行高质量汇报与决策的必要基础设施。\n\n\\subsection{软件架构章节小结}"
    ),
    # 10. 测试结果 fbox (restore richer version)
    (
        "\\textbf{核心结论：}参考解基准 26/26 全部通过；OmniCoder 8-NPU adapter 在协议一致的严格量子 holdout 上把 override 从 0/4 推进到 2/4\u2014\u2014"
        "项目首个经过严格验证的真实 benchmark 收益。训练主干稳定，Gemma 主线推进到 \\code{gemma\\_runtime\\_bootstrap} 阶段。",
        "\\textbf{本章关键结论：}参考解基准 26/26 全部通过；在协议一致的 strict quantum holdout 上，Qwen clean baseline 为 0/4、OmniCoder 8-NPU adapter 为 2/4；"
        "OmniCoder 9B base 同协议回评当前仍被 ai2 模型快照恢复阻塞，因此本章 headline 明确只基于已完成的 protocol-matched run。"
        "训练主干稳定，Gemma 主线当前停在 \\code{gemma\\_runtime\\_bootstrap}。测试结果区分三类：参考解健康度、严格未见任务表现、训练过程指标。"
    ),
]

applied = 0
for i, (old, new) in enumerate(replacements, 1):
    if old in text:
        text = text.replace(old, new, 1)
        applied += 1
        print(f"[OK] Replacement {i} applied")
    else:
        # show what we're looking for
        first_line = old.split('\n')[0][:60]
        print(f"[MISS] Replacement {i}: {first_line}...")

print(f"\nTotal: Applied {applied}/{len(replacements)} replacements")

with open("research/RESEARCH-REPORT.tex", "w", encoding="utf-8") as f:
    f.write(text)
