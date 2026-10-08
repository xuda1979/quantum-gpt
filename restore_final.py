#!/usr/bin/env python3
"""Replace 测试结果 section with backup version and restore 总结与下一步 fbox."""
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
        return None, -1, -1
    next_sec = re.search(r'\n\\section\{', text[idx+10:])
    end = idx + 10 + next_sec.start() if next_sec else len(text)
    return text[idx:end], idx, end

# 1. Replace 测试结果 section entirely with backup version
bak_test, _, _ = extract_section(backup, "测试结果")
_, cur_start, cur_end = extract_section(current, "测试结果")

if bak_test and cur_start >= 0:
    current = current[:cur_start] + bak_test + current[cur_end:]
    print(f"[OK] Replaced 测试结果 section ({cur_end-cur_start}b -> {len(bak_test)}b)")
else:
    print("[FAIL] Could not find 测试结果 section")

# 2. Restore 总结与下一步 fbox preamble
old_preamble = "\\section{总结与下一步}\n\n\\subsection{"
bak_summ, _, _ = extract_section(backup, "总结与下一步")
if bak_summ:
    # Extract backup preamble
    bak_pre_end = bak_summ.find("\\subsection{")
    bak_preamble = bak_summ[:bak_pre_end]
    new_preamble = bak_preamble + "\\subsection{"
    if old_preamble in current:
        current = current.replace(old_preamble, new_preamble, 1)
        print(f"[OK] Restored 总结与下一步 fbox preamble")
    else:
        print("[SKIP] 总结与下一步 preamble already has content")

with open("research/RESEARCH-REPORT.tex", "w", encoding="utf-8") as f:
    f.write(current)

print(f"\nFinal size: {len(current)} bytes, {len(current.splitlines())} lines")
print("Done.")
