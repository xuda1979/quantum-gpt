import re

with open("research/RESEARCH-REPORT.tex", "r", encoding="utf-8") as f:
    text = f.read()

# Merge section 1 and 2
text = re.sub(r'\\section\{引言与核心结论\}', r'\\section{引言与数据}', text)
text = re.sub(r'\\section\{数据\}', r'', text)

with open("research/RESEARCH-REPORT.tex", "w", encoding="utf-8") as f:
    f.write(text)
print("Merged")
