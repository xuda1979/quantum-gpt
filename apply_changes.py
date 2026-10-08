import sys

with open("research/RESEARCH-REPORT.tex", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(r"\section{算力与实验环境}", r"\section{算力}")
content = content.replace(r"\section{研发架构（软件架构）}", r"\section{研发架构与实验环境}")
content = content.replace("当前算力与环境层的状态", "当前算力层的状态")
content = content.replace(r"4. \textbf{分布式训练环境}", r"4. \textbf{算力演进}")
content = content.replace(r"5. \textbf{研发基础设施}", r"5. \textbf{研发架构与实验环境}")

desc = r"""
\noindent 在上述概览之上，每个特定角色数据集的具体定位与构造来源如下：

\begin{itemize}
    \item \textbf{\code{template-large-v1}}：本项目最大的宽口径监督微调（SFT）基础数据集，总计包含超过 2700 条高质量记录，结合了量子计算逻辑与经典软件工程代码片段。该数据集运用 \code{family disjoint} 策略划分训练与验证集，确保模型能够在学习各种代码生成模板时，掌握坚实的基础编程能力。
    \item \textbf{\code{mixed-holdout-v1}}：为了评估模型的真正的跨任务泛化能力，我们构建了这份包含近 2000 样本的混合域（量子+软件）保留集。它在任务（\code{task disjoint}）级别与训练数据进行了强隔离，主要用来提供一个严格、全面的零污染 benchmark 成绩。
    \item \textbf{\code{quantum-large-v1}}：专注于量子计算领域的宽口径 SFT 基础数据集。覆盖了基础量子门操作、态制备、以及常用的量子子程序等，用于使基础模型从通用代码模型适配到量子领域专属的语法与范式。
    \item \textbf{\code{quantum-holdout-v1}}：针对量子领域构建的专属严格保留集，完全规避了训练集中见过的量子算法类型，核心用于验证模型在面对从未见过的陌生量子协议（如超级密算、QAOA 等）时能否完成从理论到代码的正确推理。
    \item \textbf{\code{quantum-focus-v1} 与 \code{quantum-hard-v1}}：这两个数据集规模较小（数百至数十条），专门用于快速迭代与难例攻坚。前者支持高频短周期的实验探索（如检查学习率和 batch\_size 的合理性），后者则收集了在历次评测中模型表现极差的硬骨头任务，用于压力测试和特定问题的针对性优化。
    \item \textbf{\code{paper-router/messages}}：由于 Gemma MoE 具备专家路由机制，该前置数据集仅包含几十组特别设计的消息记录，用于在进入核心 SFT 或 GRPO 训练前对路由层（Router）进行轻量级预热（Warmup），避免专家坍塌。
\end{itemize}
"""

anchor = r"图 \ref{fig:dataset-scale} 说明仓库已不再处于”小样本玩具数据”的状态。数据规模体现的是”在有限任务库约束下的强纪律”，而非大规模公开 benchmark。"
if anchor in content:
    content = content.replace(anchor, anchor + "\n" + desc)
else:
    print("Anchor not found!")

with open("research/RESEARCH-REPORT.tex", "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
