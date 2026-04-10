#!/usr/bin/env python3
"""Print explicit samples from train and eval JSONL files."""
import json, sys

def show(path, label, indices):
    with open(path) as f:
        lines = f.readlines()
    for i in indices:
        if i >= len(lines):
            continue
        d = json.loads(lines[i])
        meta = d.get("metadata", {})
        print(f"========== {label} -- Sample #{i+1} ==========")
        print(f"example_id : {d.get('example_id','?')}")
        print(f"task_id    : {meta.get('task_id','?')}")
        print(f"domain     : {meta.get('domain','?')}  |  category: {meta.get('category','?')}")
        print(f"task_type  : {meta.get('task_type','?')}  |  difficulty: {meta.get('difficulty','?')}")
        print(f"source     : {meta.get('source','?')}")
        print()
        for msg in d["messages"]:
            role = msg["role"].upper()
            content = msg["content"]
            if len(content) > 1500:
                content = content[:1500] + f"\n... [truncated, total {len(msg['content'])} chars]"
            print(f"--- {role} ---")
            print(content)
            print()
        print()

show("data/seed/splits/train.jsonl", "SEED TRAIN", [0, 3, 9])
show("data/generated/fast-mini/train.jsonl", "GENERATED TRAIN", [25, 80])
show("data/generated/fast-mini/eval.jsonl", "GENERATED EVAL", [0, 7, 20])
