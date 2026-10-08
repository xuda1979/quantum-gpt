#!/usr/bin/env python3
"""Extract 测试结果 sections from both files for comparison."""
import re

def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

current = read("research/RESEARCH-REPORT.tex")
backup = read("/Users/daxu/Library/Application Support/Code/User/History/1185b895/Zb4b.tex")

def extract_section(text, title):
    pattern = f"\\section{{{title}}}"
    idx = text.find(pattern)
    if idx < 0:
        return None
    # Find next \section
    next_sec = re.search(r'\n\\section\{', text[idx+10:])
    end = idx + 10 + next_sec.start() if next_sec else len(text)
    return text[idx:end]

# Extract 测试结果
bak_test = extract_section(backup, "测试结果")
cur_test = extract_section(current, "测试结果")

with open("/tmp/bak_test.tex", "w") as f:
    f.write(bak_test or "NOT FOUND")
with open("/tmp/cur_test.tex", "w") as f:
    f.write(cur_test or "NOT FOUND")

print(f"Backup 测试结果: {len(bak_test)} bytes, {len(bak_test.splitlines())} lines")
print(f"Current 测试结果: {len(cur_test)} bytes, {len(cur_test.splitlines())} lines")

# Also extract 总结与下一步 preamble
bak_sum = extract_section(backup, "总结与下一步")
cur_sum = extract_section(current, "总结与下一步")

if bak_sum and cur_sum:
    # Show preamble (before first subsection)
    bak_pre = bak_sum[:bak_sum.find("\\subsection{")]
    cur_pre = cur_sum[:cur_sum.find("\\subsection{")]
    print(f"\nBackup 总结与下一步 preamble ({len(bak_pre)}b):")
    print(bak_pre[:500])
    print(f"\nCurrent 总结与下一步 preamble ({len(cur_pre)}b):")
    print(cur_pre[:500])
