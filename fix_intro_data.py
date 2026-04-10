import re

with open('research/RESEARCH-REPORT.tex', 'r') as f:
    content = f.read()

# 1. Remove the standalone Executive Summary heading and table of contents line
content = re.sub(
    r'\\section\*\{重点架构与执行概览 \(Executive Summary\)\}\n\\addcontentsline\{toc\}\{section\}\{重点架构与执行概览 \(Executive Summary\)\}\n\n',
    r'',
    content
)

# 2. Change section 引言与数据 to 引言
content = re.sub(
    r'\\section\{引言与数据\}',
    r'\\section{引言}\n\n\\subsection{重点架构与执行概览}',
    content
)

# 3. Change \subsection{数据设计原则} to add \section{数据} before it
content = re.sub(
    r'\\subsection\{数据设计原则\}',
    r'\\section{数据}\n\n\\subsection{数据设计原则}',
    content
)

# 4. We want the Glossary (\noindent\textbf{术语速查}) to be a subsection if the user wants it professional, or just leave it inside Intro.
# Actually, the Executive summary block (the text starting with "?mport re

with open('research/R b
with ope G    content = f.read()

# 1. Remove the standalone on
# 1. Remove the stanthe old \section{引言与数据}.
# Let's see exactly how this is structured.
