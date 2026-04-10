#!/usr/bin/env python3
"""Compare sections between current and backup to find remaining gaps."""
import re

def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

current = read("research/RESEARCH-REPORT.tex")
backup = read("/Users/daxu/Library/Application Support/Code/User/History/1185b895/Zb4b.tex")

# Find all section/subsection markers
sec_re = re.compile(r'\\(section|subsection|subsubsection)\{([^}]+)\}')

def get_sections(text):
    return [(m.start(), m.group(1), m.group(2)) for m in sec_re.finditer(text)]

cur_secs = get_sections(current)
bak_secs = get_sections(backup)

print("=== SECTIONS IN BACKUP BUT NOT IN CURRENT ===")
cur_titles = set(s[2] for s in cur_secs)
bak_titles = set(s[2] for s in bak_secs)
for t in bak_titles - cur_titles:
    print(f"  MISSING: {t}")

print("\n=== SECTIONS IN CURRENT BUT NOT IN BACKUP ===")
for t in cur_titles - bak_titles:
    print(f"  EXTRA: {t}")

# Now do a block-by-block size comparison from 软件架构 onwards
print("\n=== SIZE COMPARISON FROM 软件架构 ONWARDS ===")

# Find 软件架构 section in both
for name, src in [("backup", backup), ("current", current)]:
    idx = src.find("\\section{研发架构（软件架构）}")
    if idx < 0:
        idx = src.find("\\section{软件架构}")
    if idx >= 0:
        print(f"  {name}: from 软件架构 to end = {len(src) - idx} bytes (starts at {idx})")
    else:
        print(f"  {name}: 软件架构 section NOT FOUND")

# Compare subsection by subsection within 软件架构
print("\n=== SUBSECTION SIZE COMPARISON (研发架构/软件架构 section) ===")

def extract_section_content(text, section_start_str):
    idx = text.find(section_start_str)
    if idx < 0:
        return None, []
    # Find next \section (not subsection)
    next_sec = re.search(r'\n\\section\{', text[idx+10:])
    end = idx + 10 + next_sec.start() if next_sec else len(text)
    section_text = text[idx:end]
    
    # Split by subsections
    subsecs = list(re.finditer(r'\\subsection\{([^}]+)\}', section_text))
    result = []
    for i, m in enumerate(subsecs):
        start = m.start()
        end_sub = subsecs[i+1].start() if i+1 < len(subsecs) else len(section_text)
        result.append((m.group(1), end_sub - start))
    return section_text, result

_, bak_subsecs = extract_section_content(backup, "\\section{研发架构（软件架构）}")
_, cur_subsecs = extract_section_content(current, "\\section{研发架构（软件架构）}")

if bak_subsecs and cur_subsecs:
    bak_dict = {name: size for name, size in bak_subsecs}
    cur_dict = {name: size for name, size in cur_subsecs}
    
    all_names = []
    seen = set()
    for name, _ in bak_subsecs + cur_subsecs:
        if name not in seen:
            all_names.append(name)
            seen.add(name)
    
    for name in all_names:
        b = bak_dict.get(name, 0)
        c = cur_dict.get(name, 0)
        diff = c - b
        marker = " <<< DIFF" if abs(diff) > 50 else ""
        print(f"  {name}: backup={b}, current={c}, diff={diff:+d}{marker}")

# Also check sections AFTER 软件架构
print("\n=== SECTIONS AFTER 软件架构 ===")
for name, text in [("backup", backup), ("current", current)]:
    idx = text.find("\\section{研发架构（软件架构）}")
    if idx < 0:
        idx = text.find("\\section{软件架构}")
    if idx >= 0:
        after = text[idx:]
        secs = re.findall(r'\\section\{([^}]+)\}', after)
        print(f"  {name} sections: {secs}")

# Check total line counts
print(f"\n=== LINE COUNTS ===")
print(f"  backup: {len(backup.splitlines())} lines")
print(f"  current: {len(current.splitlines())} lines")
print(f"  difference: {len(backup.splitlines()) - len(current.splitlines())} lines")
