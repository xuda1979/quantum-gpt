#!/usr/bin/env python3
"""Create interface-augmented derivatives of the fast-mini-codefirst split.

Variants:
- append: add explicit required symbol hints to the end of the user prompt
- prefix: place the required interface and code-only contract before the task text
- prefix-semantic: like prefix, plus compact semantic contract bullets for a
  narrow set of task families whose prompts are too title-like at tiny smoke scale
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SYMBOL_LINE_RE = re.compile(r'^(def|class)\s+([A-Za-z_][A-Za-z0-9_]*)\b', re.M)
RETURN_ONLY_CODE_RE = re.compile(r'return only (?:python )?code|return the solution as python code only|return only the code, no explanations', re.I)

SEMANTIC_HINTS_BY_TASK = {
    'quantum_measurement_bug_repair': [
        '- Semantic requirements: input is a two-bit string in q1q0 order.',
        '- Return a dict with integer keys/values for q0 and q1 measurements.',
        '- Validate length and bit characters; invalid input must raise ValueError.',
    ],
    'software_session_event_log': [
        '- Semantic requirements: maintain state with active sessions and history.',
        '- Events use type/session_id and may include user/ts.',
        '- start creates an active session; message updates message count and last_seen; end moves the session into sorted history.',
        '- Invalid transitions must raise ValueError.',
    ],
    'software_session_window_summary': [
        '- Semantic requirements: events have session_id, ts, and kind in {open, message, close}.',
        '- Return active_sessions, closed_sessions, message_counts, and timeline.',
        '- active_sessions are those not closed whose latest activity is within active_window of max ts.',
        '- Invalid transitions or unsupported kinds must raise ValueError.',
    ],
    'quantum_stabilizer_tableau_update_repair': [
        '- Semantic requirements: support Pauli labels I/X/Y/Z with normalization and validation.',
        '- apply_gate_sequence must update a signed single-qubit Pauli under Clifford conjugation.',
        '- Support the gates H, S, and SDG; unsupported labels or gates must raise ValueError.',
    ],
}


def extract_required_symbols(text: str) -> list[str]:
    hints: list[str] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        match = SYMBOL_LINE_RE.match(line)
        if not match:
            i += 1
            continue

        kind, name = match.groups()
        if kind == 'class':
            hints.append(f'- Required class: {name}')
            i += 1
            continue

        signature = line.strip()
        while not signature.rstrip().endswith(':') and i + 1 < len(lines):
            i += 1
            signature += ' ' + lines[i].strip()
        signature = signature.rstrip(':').strip()
        hints.append(f'- Required function: {signature}')
        i += 1
    return hints


def augment_user_prompt_append(user_text: str, assistant_text: str) -> str:
    hints = extract_required_symbols(assistant_text)
    if not hints:
        return user_text

    extra = ['', 'Interface requirements:'] + hints
    if not RETURN_ONLY_CODE_RE.search(user_text):
        extra.append('- Output requirement: return only Python code.')
    return user_text.rstrip() + '\n' + '\n'.join(extra) + '\n'


def augment_user_prompt_prefix(user_text: str, assistant_text: str, semantic_hints: list[str] | None = None) -> str:
    hints = extract_required_symbols(assistant_text)
    if not hints:
        return user_text

    lines = ['Follow these interface requirements exactly:', *hints]
    if semantic_hints:
        lines.extend(semantic_hints)
    if not RETURN_ONLY_CODE_RE.search(user_text):
        lines.append('- Output requirement: return only Python code.')
    lines.extend(['', user_text.strip()])
    return '\n'.join(lines).rstrip() + '\n'


def rewrite_split(src: Path, dst: Path, variant: str) -> dict[str, int]:
    dst.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    changed = 0
    semantic_augmented = 0
    with src.open('r', encoding='utf-8') as in_f, dst.open('w', encoding='utf-8') as out_f:
        for line in in_f:
            row = json.loads(line)
            total += 1
            user_msg = row['messages'][-2]
            assistant_msg = row['messages'][-1]
            before = user_msg['content']
            task_id = row.get('metadata', {}).get('task_id')
            semantic_hints = None
            if variant == 'prefix-semantic':
                semantic_hints = SEMANTIC_HINTS_BY_TASK.get(task_id)
                if semantic_hints:
                    semantic_augmented += 1
            if variant in {'prefix', 'prefix-semantic'}:
                after = augment_user_prompt_prefix(before, assistant_msg['content'], semantic_hints=semantic_hints)
            else:
                after = augment_user_prompt_append(before, assistant_msg['content'])
            if after != before:
                changed += 1
                user_msg['content'] = after
            row.setdefault('metadata', {})['prompt_variant'] = f'interface-{variant}-v4'
            out_f.write(json.dumps(row, ensure_ascii=False) + '\n')
    return {'total': total, 'changed': changed, 'semantic_augmented': semantic_augmented}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--src-dir', type=Path, default=Path('data/generated/fast-mini-codefirst'))
    parser.add_argument('--out-dir', type=Path, default=Path('data/generated/fast-mini-interface'))
    parser.add_argument('--variant', choices=['append', 'prefix', 'prefix-semantic'], default='append')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    train_stats = rewrite_split(args.src_dir / 'train.jsonl', args.out_dir / 'train.jsonl', args.variant)
    eval_stats = rewrite_split(args.src_dir / 'eval.jsonl', args.out_dir / 'eval.jsonl', args.variant)
    print(json.dumps({'variant': args.variant, 'train': train_stats, 'eval': eval_stats}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
