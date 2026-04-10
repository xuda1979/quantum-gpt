#!/usr/bin/env python3
"""Debug and fix remaining 3 replacements."""

with open("research/RESEARCH-REPORT.tex", "r", encoding="utf-8") as f:
    text = f.read()

# Debug: find what's there
print("=== DEBUG ===")
for s in ["\\section{软件架构}", "\\section{研发架构"]:
    i = text.find(s)
    if i >= 0:
        print(f"Found '{s}' at {i}")
        print(repr(text[i:i+60]))

for s in ["自动化研发循环", "自治研发循环"]:
    i = text.find(s)
    if i >= 0:
        print(f"Found '{s}' at {i}")
        print(repr(text[max(0,i-30):i+40]))

for s in ["唯一正式报告与证据索引", "唯一正式报告为什么"]:
    i = text.find(s)
    if i >= 0:
        print(f"Found '{s}' at {i}")
        print(repr(text[max(0,i-30):i+50]))

print("\n=== APPLYING FIXES ===")

# Fix 1: section{软件架构} -> section{研发架构（软件架构）} + fbox
old1_start = "\\section{软件架构}\n"
if old1_start in text:
    # Find the full block to replace
    idx = text.find(old1_start)
    # Find end: the line with 汇报层
    end_marker = "\\code{research/RESEARCH-REPORT.tex}。"
    end_idx = text.find(end_marker, idx)
    if end_idx >= 0:
        end_idx += len(end_marker)
        old_block = text[idx:end_idx]
        new_block = (
            "\\section{研发架构（软件架构）}\n\n"
            "\\noindent\\fbox{\\parbox{0.96\\textwidth}{%\n"
            "\\textbf{本章关键结论：}研发架构的核心原则是\u201c分层、留痕、可恢复\u201d。"
            "先在本地验证，再通过 S3 relay 送到远端；trainer 与 plugin 分离；"
            "所有实验状态都沉淀为工件。即使会话中断，研发主线也能从 state 文件恢复。}}\n\n"
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
        )
        text = text[:idx] + new_block + text[end_idx:]
        print("[OK] Fix 1: section + fbox + itemize applied")
    else:
        print("[FAIL] Fix 1: end marker not found")
else:
    print("[SKIP] Fix 1: section{软件架构} not found (maybe already fixed)")

# Fix 5: 自动化研发循环 -> 自治研发循环脚本 (removing figure block)
old5_sub = "\\subsection{自动化研发循环}"
if old5_sub in text:
    idx5 = text.find(old5_sub)
    # Find the figure block start
    fig_start = "\\begin{figure}[htbp]\n\\centering\n\\includegraphics[width=0.95\\textwidth]{figures/claude-code-agent.png}"
    fig_idx = text.find(fig_start, idx5)
    if fig_idx >= 0:
        # Find figure end
        fig_end_marker = "\\end{figure}"
        fig_end = text.find(fig_end_marker, fig_idx)
        if fig_end >= 0:
            fig_end += len(fig_end_marker)
            # Remove figure block (including surrounding newlines)
            while fig_end < len(text) and text[fig_end] == '\n':
                fig_end += 1
            while fig_idx > 0 and text[fig_idx-1] == '\n':
                fig_idx -= 1
            text = text[:fig_idx] + "\n" + text[fig_end:]
            print("[OK] Fix 5a: removed claude-code-agent figure")
    
    # Now rename subsection
    text = text.replace("\\subsection{自动化研发循环}", "\\subsection{自治研发循环脚本}")
    # Fix wording
    text = text.replace("这类脚本的核心价值在于", "这类脚本的价值在于")
    text = text.replace("即使发生团队交接或上下文切换", "即使团队交接或上下文切换")
    print("[OK] Fix 5b: subsection renamed + wording fixed")
else:
    print("[SKIP] Fix 5: already fixed")

# Fix 8: 唯一正式报告与证据索引 -> with itemize
old8_sub = "\\subsection{唯一正式报告与证据索引}"
if old8_sub in text:
    idx8 = text.find(old8_sub)
    # Find the end of this subsection's list (up to the \par lines)
    # The exact old block:
    old8_full = (
        "\\subsection{唯一正式报告与证据索引}\n\n"
        "研究报告不是项目收尾时才补写的文档，而是研发架构的有机组成部分。理由很简单："
    )
    if old8_full in text:
        # Find the three \par lines after it
        par_section_start = text.find(old8_full)
        # Find from there the three par lines
        after = text[par_section_start + len(old8_full):]
        # Find last \par line end
        last_par = "工件遗漏的问题。"
        lp_idx = after.find(last_par)
        if lp_idx >= 0:
            end8 = par_section_start + len(old8_full) + lp_idx + len(last_par)
            old8_block = text[par_section_start:end8]
            new8_block = (
                "\\subsection{唯一正式报告为什么是架构的一部分}\n\n"
                "研究报告不是最终才补写的文档，而是研发架构的一部分。原因很简单：\n"
                "\\begin{itemize}\n"
                "  \\item 如果没有唯一正式报告，汇报口径就会漂移；\n"
                "  \\item 如果没有单一 PDF 产物，警告清理、版式统一、证据索引都无从谈起；\n"
                "  \\item 如果没有\u201c唯一报告 + 唯一证据索引\u201d，下一轮迭代很容易再次出现造口径、混口径、漏工件的问题。\n"
                "\\end{itemize}"
            )
            text = text[:par_section_start] + new8_block + text[end8:]
            print("[OK] Fix 8: 唯一正式报告 restored with itemize")
        else:
            print("[FAIL] Fix 8: end marker not found")
    else:
        print("[FAIL] Fix 8: full block not found, trying partial")
        text = text.replace(old8_sub, "\\subsection{唯一正式报告为什么是架构的一部分}")
        print("[OK] Fix 8: at least renamed subsection")
else:
    print("[SKIP] Fix 8: already fixed")

with open("research/RESEARCH-REPORT.tex", "w", encoding="utf-8") as f:
    f.write(text)

print("\nDone. File updated.")
