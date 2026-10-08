import re

with open('research/RESEARCH-REPORT.tex', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Rename sections
content = content.replace(r"\section{算力与实验环境}", r"\section{算力}")
content = content.replace(r"\section{研发架构（软件架构）}", r"\section{研发架构与实验环境}")

# Fix small text
content = content.replace("当前算力与环境层的状态", "当前算力层的状态")

# 2. Add descriptions to datasets
dataset_descriptions = r"""

\noindent 在上述概览之上，每个特定角色数据集的具体定位与构造来源如下：

\begin{itemize}
    \item \textbf{\code{template-large-v1}}：本项目最大的宽口径监督微调（SFT）基础数据集，总计包含超过 2700 条高质量记录，结合了量子计算逻辑与经典软件工程代码片段。该数据集运用 \code{family disjoint} 策略划分训练与验证集，确保模型能够在学习各种代码生成模板时，掌握坚实的基础编程能力。
    \item \textbf{\co
with op-ho    content = f.read()

# 1. Rename sections
content = content.replac??# 1. Rename sections??近 2000 样本的混?ontent = content.replace(r"\section{研发架构（软件架构）}", r"\section??
# Fix small text
content = content.replace("当前算力与环境层的状态", "当前算力层的犀?
    \itemcontent = contequ
# 2. Add descriptions to datasets
dataset_descriptions = r"""

\noindent 在上述概览??ataset_descriptions = r"""

\no??
\noindent 在上述概览??\begin{itemize}
    \item \textbf{\code{template-large-v1}}：本项目最大的宽口径监督微       m \textbf{\c    \item \textbf{\co
with op-ho    content = f.read()

# 1. Rename sections
content = content.replac??# 1. Rename sections??近 2000 样本的混?ontent = content.replace(r"\section{研发架构（软件架构）}", r"\section??
# Fix small text
content = content.replace("当前算力与环境层的状态", "当前算力层的犀?
    \itemcontent = contequ
# 2. Add descriptions to?ith op-ho    conten??
# 1. Rename sections
content =???ontent = content.r?? Fix small text
content = content.replace("当前算力与环境层的状态", "当前算力层的犀?
    \itemcontent = contequ
# 2. Add descriptions ??content = conte?   \itemcontent = contequ
# 2. Add descriptions to datasets
dataset_descriptions = rag# 2. Add descriptions to ??datase家路由机制，该前置?\noind?仅包含几十组特
\no??
\noindent 在上述概览??\begin{itemize}
  ?? \noi ?   \item \textbf{\code{template-large-v1}}??ith op-ho    content = f.read()

# 1. Rename sections
content = content.replac??# 1. Rename sections??近 2000 样本?d
# 1. Rename sections
content = r"content = content.rt-# Fix small text
content = content.replace("当前算力与环境层的状态", "当前算力层的犀?
    \itemcontent = contequ
# 2. Add descriptions ??ontent = contech    \itemcontent = contequ
# 2. Add descriptions to?ith op-ho    conten??
# 1. Renaor# 2. Add descriptions to?+# 1. Rename sections
content =???ontent = contotcontent =???ontentr!content = content.replace("当前算力与环境',    \itemcontent = co f:
    f.write(content)

print("Updates applied.")
