import re

with open("research/RESEARCH-REPORT.tex", "r", encoding="utf-8") as f:
    text = f.read()

# Regex to match \begin{abstract} ... up to the \clearpage right before Executive Summary
pattern = r'\\begin\{abstract\}.*?\\end\{abstract\}\s*\\vspace\{1em\}\s*\\noindent\\textbf\{Keywords:\}.*?\\clearpage'

text = re.sub(pattern, '', text, flags=re.DOTALL)

with open("research/RESEARCH-REPORT.tex", "w", encoding="utf-8") as f:
    f.write(text)

print("Removed abstract")
