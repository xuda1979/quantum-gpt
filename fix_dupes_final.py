import re

with open("research/RESEARCH-REPORT.tex", "r", encoding="utf-8") as f:
    text = f.read()

# The entire block from \subsection{研究目标} to the end of the paragraph
block_pattern = r"\\subsection\{研究目标\}\s*本项目.*?的量子编码大模型研发闭环。[\s\S]*?\\end\{figure\}\s*本报告重点介绍系统.*?为量子领域的大语言模型研发提供参考。\s*"

# Let's write a targeted function to remove duplicates
# First get all of them
matches = list(re.finditer(block_pattern, text))
if matches:
    original_block = matches[0].group(0)
    
    # remove all
    text = re.sub(block_pattern, "", text)
    
    # modify text
    new_block = original_block.replace("本项目的核心目标是：围绕量子算法与软件工程双域任务，构建一个", "本项目的研究目标是量子科学和编码大模型，构建一个")
    
    # insert after section 引言
    idx = text.find(r"\section{引言}")
    if idx != -1:
        insert_idx = text.find("\n", idx) + 1
        text = text[:insert_idx] + "\n" + new_block + "\n" + text[insert_idx:]

with open("research/RESEARCH-REPORT.tex", "w", encoding="utf-8") as f:
    f.write(text)
