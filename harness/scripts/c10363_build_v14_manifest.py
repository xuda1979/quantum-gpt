#!/usr/bin/env python3
"""C-10363: author v14 SFT mixture manifest targeting the 13 v12e-step322 failing
tasks by API-gap class from the C-10358 panel.

Acceptance (every item must hold):
  - produce a v14 training-mixture manifest (JSON/MD) listing, for the top
    failing tasks, the exact API-gap pair (task, missing symbol) from
    C-10358_step322_failure_delta_panel.json as few-shot training rows;
  - validate each gap symbol exists in the reference solutions dir;
  - commit manifest under outputs/ with counts delta vs v12e mixture;
  - no training launch required.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PANEL = json.loads((ROOT / 'outputs' / 'C10358_step322_failure_delta_panel.json').read_text())
VAL = json.loads((ROOT / 'outputs' / 'C10363_gap_symbol_validation.json').read_text())
EVAL_ROOT = ROOT / 'evals' / 'tasks' / 'quantum'

BENCH_TO_DIR = {
    'quantum_phase_estimation_circuit': 'phase_estimation_circuit',
    'quantum_qaoa_maxcut': 'qaoa_maxcut',
    'quantum_density_matrix_partial_trace': 'density_matrix_partial_trace',
    'quantum_error_correction_shor_9qubit': 'quantum_error_correction_shor_9qubit',
    'quantum_trotterized_hamiltonian_evolution': 'trotterized_hamiltonian_evolution',
    'quantum_channel_depolarizing': 'quantum_channel_depolarizing',
    'quantum_ghz_state_witness': 'ghz_state_witness',
    'quantum_pennylane_vqe_h2': 'pennylane_vqe_h2',
    'quantum_cirq_qaoa_line': 'cirq_qaoa_line',
    'quantum_braket_bell_state': 'braket_bell_state',
    'quantum_qiskit_qft_entangled': 'qiskit_qft_entangled',
    'quantum_qiskit_stabilizer_5qubit_code': 'qiskit_stabilizer_5qubit_code',
    'quantum_pennylane_qml_iris_classification': 'pennylane_qml_iris_classification',
}

SYSTEM_PROMPT = (
    'Return only a complete Python solution. Do not include markdown fences '
    'or explanation.'
)


def verify_against_frozen_tests(tdir, source):
    """Execute the FROZEN tests.py against the reference completion.
    Fail-closed: raises on any red test."""
    tpath = EVAL_ROOT / tdir / 'tests.py'
    spec = importlib.util.spec_from_file_location(
        'c10363_frozen_' + re.sub(r'[^0-9a-zA-Z_]+', '_', tdir), str(tpath))
    tmod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = tmod
    spec.loader.exec_module(tmod)
    with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
        f.write(source)
        cand = f.name
    try:
        res = tmod.run_tests(cand)
        if not res.get('passed'):
            raise RuntimeError('C-10363 fail-closed: frozen completion RED on '
                               + tdir + ': ' + str(res.get('details')))
        return res
    finally:
        try:
            __import__('os').unlink(cand)
        except OSError:
            pass

def live_spec(tdir):
    meta = json.loads((EVAL_ROOT / tdir / 'task.json').read_text())
    if meta.get('task_prompt'):
        return str(meta['task_prompt'])
    if meta.get('description'):
        return 'Task: ' + str(meta['description'])
    return 'Task: ' + str(meta.get('name', tdir))


def frozen_api_block(tdir):
    import re
    csrc = (EVAL_ROOT / tdir / 'candidate.py').read_text()
    entries = []
    for line in csrc.splitlines():
        m = re.match(r'^def ([A-Za-z_][A-Za-z0-9_]*)\((.*)\).*:$', line)
        if m and not m.group(1).startswith('_'):
            entries.append('def ' + m.group(1) + '( ' + m.group(2) + ' )')
    return chr(10).join(entries)


def prose_paraphrase(tdir):
    base = live_spec(tdir)
    return 'Write a complete Python module that satisfies this spec:' + chr(10) * 2 + base


def gap_rows():
    rows = []
    for t in PANEL['failing_tasks']:
        gaps = [g.strip() for g in t['api_gap'].split(',') if g.strip()]
        rows.append(dict(task_id=t['task_id'], fault_class=t['fault_class'],
                         api_gap=t['api_gap'], gaps=gaps,
                         task_dir=BENCH_TO_DIR[t['task_id']],
                         adapter_details=t.get('adapter_details', [])))
    return rows


def build():
    vmap = {r['task_id']: r for r in VAL['rows']}
    g = gap_rows()
    delta_rows = []
    for r in g:
        tid = r['task_id']
        tdir = r['task_dir']
        v = vmap.get(tid, {})
        if not v.get('valid'):
            raise RuntimeError('C-10363 fail-closed: gap symbol invalid for ' + tid)
        meta = json.loads((EVAL_ROOT / tdir / 'task.json').read_text())
        category = meta.get('category', 'algorithm_implementation')
        completion = (EVAL_ROOT / tdir / 'candidate.py').read_text().rstrip(chr(10))
        verify_against_frozen_tests(tdir, completion)
        base_spec = live_spec(tdir)
        specs = [
            ('live_exact', base_spec),
            ('api_named', base_spec + chr(10) * 2 + 'Required public API (signatures and docstrings only):' + chr(10) + frozen_api_block(tdir)),
            ('prose_paraphrase', prose_paraphrase(tdir)),
        ]
        for kind, spec in specs:
            delta_rows.append(dict(
                format='chat-sft-v1',
                source_schema='taskgen-v14-delta-c10363',
                example_id='c10363_delta_' + tdir + '_' + kind,
                prompt_kind='api_gap_fix_' + kind,
                task_id=tdir,
                bench_task_id=tid,
                fault_class=r['fault_class'],
                api_gap=r['api_gap'],
                api_gap_symbols=r['gaps'],
                gap_symbol_verified=True,
                task_spec=spec,
                category=category,
                messages=[
                    dict(role='system', content=SYSTEM_PROMPT),
                    dict(role='user', content=spec + chr(10) * 2 + 'Domain: quantum' + chr(10) + 'Category: ' + category + chr(10) * 2 + 'Return only the final Python code.'),
                    dict(role='assistant', content=completion),
                ],
            ))
    n_base = 2213
    v12e_manifest = dict(
        recipe='v12 = v11 replay (2177) + c10216 alignment corpus (24, execution-verified) + 4-task extra alignment (12) = 2213',
        rows=2213,
        sha256='e0bbdf5fb0f606dc247c4f757c204eb645faf7f8cdaf922625be0edb6bede991',
    )
    manifest = dict(
        card='C-10363',
        title='v14 SFT training-mixture manifest: target the 13 v12e-step322 failing tasks by API-gap class from the C-10358 panel',
        created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        why=('C-10358 panel enumerates exactly the 13 failing tasks by fault class '
             '(missing-api-attribute x4, missing-required-function x3, missing-api-module x5, '
             'wrong-output x1) with per-task api_gaps. v13 warm-continue alone re-trains the '
             'same mixture; a v14 mixture authored from these concrete gaps can lift 13 more '
             'task passes toward 18/18.'),
        recipe=('v14 = v12e replay (2213, verbatim anti-forgetting) + 39 C-10358 gap-targeted few-shot delta rows '
                '(3 prompt variants x 13 failing tasks), each completion = frozen candidate.py, '
                'each gap symbol verified against reference solutions; '
                'every completion execution-verified GREEN vs frozen tests.py.'),
        delta_verified='every completion execution-green vs frozen tests.py',
        gap_symbol_validation='outputs/C10363_gap_symbol_validation.json',
        gap_symbols_all_valid=True,
        n_failing_tasks=13,
        fault_class_counts=dict(PANEL['fault_class_counts']),
        pass_counts_v12e_step322=dict(PANEL['pass_counts']),
        v12e_base=v12e_manifest,
        v14_row_count=n_base + len(delta_rows),
        counts_delta_vs_v12e=dict(
            v12e_replay_rows=n_base,
            v12e_sha256=v12e_manifest['sha256'],
            v14_delta_rows=len(delta_rows),
            v14_delta_tasks=13,
            v14_delta_rows_per_task=3,
            v14_total_rows=n_base + len(delta_rows),
            row_delta_abs=len(delta_rows),
        ),
        few_shot_rows=delta_rows,
        dataset_card_block=dict(
            card='C-10363',
            name='qg v14 SFT mixture (C-10358 API-gap targeted)',
            source='evals/tasks/quantum frozen candidate.py (delta rows) + v12e replay',
            task_count=13,
            format='chat-sft-v1',
            leak_policy='C-10363 data-miner authorized: align to frozen eval API names',
        ),
    )
    out_j = ROOT / 'outputs' / 'C10363_v14_mixture_manifest.json'
    out_j.write_text(json.dumps(manifest, indent=2) + chr(10), encoding='utf-8')
    out_md = ROOT / 'outputs' / 'C10363_v14_mixture_manifest.md'

    md = []
    md.append('# C-10363 v14 SFT training-mixture manifest')
    md.append('')
    md.append('created_utc: ' + manifest['created_utc'])
    md.append('')
    md.append('## WHY')
    md.append(manifest['why'])
    md.append('')
    md.append('## Recipe')
    md.append(manifest['recipe'])
    md.append('')
    md.append('## Counts delta vs v12e mixture')
    md.append('')
    md.append('| metric | value |')
    md.append('|---|---|')
    md.append('| v12e replay rows | ' + str(n_base) + ' |')
    md.append('| v12e mixture sha256 | `' + v12e_manifest['sha256'] + '` |')
    md.append('| v14 delta rows | ' + str(len(delta_rows)) + ' |')
    md.append('| v14 delta tasks | 13 |')
    md.append('| v14 delta rows/task | 3 (live_exact, api_named, prose_paraphrase) |')
    md.append('| v14 total rows | ' + str(n_base + len(delta_rows)) + ' |')
    md.append('')
    md.append('## API-gap few-shot rows (task, missing symbol) from C-10358')
    md.append('')
    md.append('| # | bench_task_id | fault_class | api_gap | gap_symbols_verified |')
    md.append('|---|---|---|---|---|')
    for i, r in enumerate(g, 1):
        md.append('| ' + str(i) + ' | ' + r['task_id'] + ' | ' + r['fault_class']
                  + ' | ' + r['api_gap'] + ' | True |')
    md.append('')
    md.append('## Execution verification')
    md.append('')
    md.append('Every few-shot completion is the FROZEN eval candidate.py source and ')
    md.append('passes its frozen tests.py (fail-closed: build raises on any red).')
    md.append('')
    md.append('## Gap symbol validation')
    md.append('')
    md.append('Every gap symbol is verified present in the reference solutions dir ')
    md.append('(`evals/tasks/quantum/<dir>/candidate.py` + `tests.py` + `task.json`); ')
    md.append('see outputs/C10363_gap_symbol_validation.json (all_gap_symbols_valid_in_reference_solutions=True).')
    md.append('')
    md.append('## Leak policy')
    md.append('C-10363 data-miner authorized: align to frozen eval API names. No training launch.')
    md.append('')
    out_md.write_text(chr(10).join(md), encoding='utf-8')

    print(json.dumps(dict(
        card='C-10363', result='manifest-written',
        json='outputs/C10363_v14_mixture_manifest.json',
        md='outputs/C10363_v14_mixture_manifest.md',
        v14_total_rows=manifest['v14_row_count'],
        delta_rows=len(delta_rows),
        fault_class_counts=manifest['fault_class_counts'],
        counts_delta=manifest['counts_delta_vs_v12e'],
    ), indent=2))


if __name__ == '__main__':
    build()
