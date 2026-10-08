#!/usr/bin/env python3
"""Detailed comparison of sections after 软件架构."""
import re

def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

current = read("research/RESEARCH-REPORT.tex")
backup = read("/Users/daxu/Library/Application Support/Code/User/History/1185b895/Zb4b.tex")

def get_from_arch(text):
    idx = text.find("\\section{研发架构（软件架构）}")
    if idx < 0:
        idx = text.find("\\section{软件架构}")
    return text[idx:] if idx >= 0 else ""

cur_after = get_from_arch(current)
bak_after = get_from_arch(backup)

# Split by \section
sec_re = re.compile(r'(?=\\section\{)')
cur_sections = sec_re.split(cur_after)
bak_sections = sec_re.split(bak_after)

# Remove empty strings
cur_sections = [s for s in cur_sections if s.strip()]
bak_sections = [s for s in bak_sections if s.strip()]

print("=== SECTION-LEVEL SIZE COMPARISON (from 软件架构 to end) ===\n")
for i in range(max(len(cur_sections), len(bak_sections))):
    cur_s = cur_sections[i] if i < len(cur_sections) else "(missing)"
    bak_s = bak_sections[i] if i < len(bak_sections) else "(missing)"
    
    cur_title = re.search(r'\\section\{([^}]+)\}', cur_s)
    bak_title = re.search(r'\\section\{([^}]+)\}', bak_s)
    ct = cur_title.group(1) if cur_title else "?"
    bt = bak_title.group(1) if bak_title else "?"
    
    cur_len = len(cur_s) if isinstance(cur_s, str) else 0
    bak_len = len(bak_s) if isinstance(bak_s, str) else 0
    diff = cur_len - bak_len
    marker = " <<< DIFF" if abs(diff) > 100 else ""
    
    print(f"Section {i}: backup='{bt}' ({bak_len}b) vs current='{ct}' ({cur_len}b) diff={diff:+d}{marker}")

# Now do subsection comparison for sections with big diffs
print("\n=== DETAILED SUBSECTION COMPARISON FOR SECTIONS WITH DIFFS ===\n")

for i in range(min(len(cur_sections), len(bak_sections))):
    cur_s = cur_sections[i]
    bak_s = bak_sections[i]
    
    if abs(len(cur_s) - len(bak_s)) < 100:
        continue
    
    sec_title = re.search(r'\\section\{([^}]+)\}', bak_s)
    print(f"\n--- {sec_title.group(1) if sec_title else '?'} ---")
    
    # Split by subsection
    sub_re = re.compile(r'(?=\\subsection\{)')
    cur_subs = sub_re.split(cur_s)
    bak_subs = sub_re.split(bak_s)
    
    # Get titles
    def get_sub_titles(parts):
        result = []
        for p in parts:
            m = re.search(r'\\subsection\{([^}]+)\}', p)
            if m:
                result.append((m.group(1), len(p)))
            else:
                result.append(("(preamble)", len(p)))
        return result
    
    cur_titled = get_sub_titles(cur_subs)
    bak_titled = get_sub_titles(bak_subs)
    
    cur_dict = {t: s for t, s in cur_titled}
    bak_dict = {t: s for t, s in bak_titled}
    
    all_titles = []
    seen = set()
    for t, _ in bak_titled + cur_titled:
        if t not in seen:
            all_titles.append(t)
            seen.add(t)
    
    for t in all_titles:
        b = bak_dict.get(t, 0)
        c = cur_dict.get(t, 0)
        d = c - b
        m = " <<< DIFF" if abs(d) > 50 else ""
        status = ""
        if t not in cur_dict:
            status = " [MISSING IN CURRENT]"
        elif t not in bak_dict:
            status = " [EXTRA IN CURRENT]"
        print(f"  {t}: backup={b}, current={c}, diff={d:+d}{m}{status}")
