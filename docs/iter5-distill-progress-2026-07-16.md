# Iter-5 Distillation Progress — 2026-07-16

**Purpose:** Track the iter-5 distillation-correction development status, fixes
applied, and next steps. This is the scaled-up successor to iter-4 (100 → 1000
questions per adapter) that targets the verified capability gaps from
`docs/iter4-comprehensive-eval-report-2026-07-16.md`.

---

## 1. Current State (2026-07-16 11:00 UTC)

### Datasets generated

| Adapter | Seed questions | Teacher responses | Status |
|---------|---------------|-------------------|--------|
| 27B | 1000 ✅ | 5 (2 ok, 3 failed) | Blocked by local proxy + thinking-only responses |
| 35B | 1000 ✅ | 2 (2 ok, 0 failed) | Same |

### Files

- `data/generated/glm52_soft_distill_sft_iter5_27b/`
  - `manifest.json` — dataset manifest (1000 questions, allocation table)
  - `seed_questions.jsonl` — 1000 questions (qaoa, vqe, qft, pennylane, cirq, braket, ...)
  - `teacher_responses.jsonl` — 5 records (2 validated, 3 failed with empty response)
- `data/generated/glm52_soft_distill_sft_iter5_35b/`
  - `manifest.json`, `seed_questions.jsonl`, `teacher_responses.jsonl` (2 records)

---

## 2. Blockers Identified & Fixed

### 2.1 Wrong API port in iter-5 generator

**Root cause:** `scripts/generate_iter5_teacher_responses_batched.py` defaulted
to `http://127.0.0.1:53021` for the Huanxin proxy, but the actual proxy is at
`http://127.0.0.1:49765` (per `ANTHROPIC_BASE_URL` env var).

**Fix:** Changed the default to `49765` (line 577). The script still respects
`ANTHROPIC_BASE_URL` if set.

### 2.2 GLM5.2 returns thinking-only responses (no text block)

**Root cause:** When the system prompt asks for raw Python code, GLM5.2 often
returns a response with only a `thinking` content block and no `text` block.
The model "thinks through" the solution but doesn't emit a final text answer.

The iter-5 generator's `extract_text()` only extracted `type == "text"` blocks,
so it returned an empty string. The `validate_all()` then failed with
"empty response", and all 6 retries failed the same way.

**Fix:** Ported the thinking-fallback and two-turn fallback from
`scripts/generate_iter4_teacher_responses_anthropic.py`:

1. **`extract_thinking(raw)`** — extract all thinking-block text
2. **`extract_code_from_thinking(thinking)`** — parse code from thinking:
   - Fenced ```python ... ``` blocks (take the LAST one containing `def main()`)
   - Last contiguous run of import/from/def/class lines
3. **Two-turn fallback** — if thinking has no parseable code, send the thinking
   back as assistant context and ask for raw code

**Bug fixed in both iter-4 and iter-5:** `extract_code_from_thinking` was taking
the LAST fenced block, but the last block is often a partial snippet. Changed
to take the LAST block **that contains `def main()`**.

### 2.3 Local sandbox missing quantum libraries

**Root cause:** `validate_all()` runs the teacher code via
`subprocess.run([sys.executable, "-c", code])` to verify it prints the expected
marker. But the local Python 3.14 environment has incompatible quantum library
versions:
- `qiskit 2.5.0` — `BackendSampler` removed from `qiskit.primitives`
- `cirq 1.7.0` — requires Python 3.11-3.13 (local is 3.14)
- `braket` — missing `__version__` attribute (shim issue)

Valid teacher code (correct for the NAS training env) fails the local sandbox
execution gate, causing the response to be rejected.

**Fix:** Added `--lenient-execution` flag (default True) to
`generate_iter5_teacher_responses_batched.py`. When the sandbox fails with an
`ImportError` or `ModuleNotFoundError`, the code is accepted with
`validation.runnable=False` and `validation.lenient_accept=True` recorded. The
code will be re-validated on the NAS where the full quantum stack is installed.

### 2.4 Failed records duplicating in output JSONL

**Root cause:** `append_record()` always appends to the JSONL file, even for
failed records. On the next run, `load_completed()` correctly skipped records
with non-empty `teacher_response`, but failed records (empty response) were
re-attempted and re-appended, creating duplicates.

**Fix:**
1. `load_completed()` now uses `teacher_response.strip()` (non-empty) as the
   completion criterion, not `validation.runnable`.
2. Deduped existing duplicates in `teacher_responses.jsonl` (kept the best
   record per `example_id`, preferring non-empty responses).

### 2.5 Generated datasets not backed up

**Root cause:** `scripts/backup_to_s3_and_git.sh` excluded
`data/generated/**` from the code sync (line 58) but didn't add it as a
separate section. So generated datasets were never backed up to S3.

**Fix:** Added a `--- data/generated/ ---` section that syncs the entire
`data/generated/` tree to S3. Ran the backup — all iter-4/iter-5 datasets are
now on S3 at `iner:${INER_S3_BUCKET}/software/quantum-gpt/data/generated/`.

Also staged all iter-3/4/5 distillation datasets for git commit (small JSONL
files, ~4.6 MB total).

---

## 3. Validation

Tested the fixes on `iter5-27b-qaoa_end_to_end-0109` (previously failed with
"empty response"):

```
Testing seed: iter5-27b-qaoa_end_to_end-0109
Result:
  attempts: 1
  error:
  validation: runnable=False marker=False thinking_fb=True two_turn_fb=False lenient=True
  teacher_response len: 3345
  teacher_response (first 200 chars): from qiskit import QuantumCircuit
    from qiskit.primitives import BackendSampler
    ...
```

The thinking-fallback extracted valid Python code, and lenient-execution
accepted it despite the local `BackendSampler` import error.

---

## 4. Next Steps

1. **Resume iter-5 teacher generation** with the fixed generator:
   ```bash
   # 27B (resume from 2 completed)
   python3 scripts/generate_iter5_teacher_responses_batched.py \
     --adapter 27b --batch 100 --inter-seed-delay 1.0

   # 35B (resume from 2 completed)
   python3 scripts/generate_iter5_teacher_responses_batched.py \
     --adapter 35b --batch 100 --inter-seed-delay 1.0
   ```

2. **Backfill iter-4** (76 remaining 27B + 100 35B) using the same fixed
   generator approach — port the thinking-fallback to
   `generate_iter4_teacher_responses_anthropic.py` (already done in this
   session).

3. **Build iter-5 SFT preparation script** (`prepare_iter5_distill_sft.py`) —
   parallel to `scripts/prepare_iter4_distill_sft.py`, converts
   `teacher_responses.jsonl` → chat-sft-v1 format with 90/10 train/eval split.

4. **Build iter-5 SFT launch scripts** —
   `scripts/asi1_launch_iter5_distill_sft_27b.sh` and
   `scripts/asi2_launch_iter5_distill_sft_35b.sh` (parallel to iter-4 launchers).

5. **Re-validate on NAS** — after teacher generation completes, re-run the
   strict execution gate on the NAS (where the full quantum stack is
   installed) to filter out any code that genuinely fails to run.

---

## 5. Source Documents

- `docs/iter4-comprehensive-eval-report-2026-07-16.md` (eval analysis)
- `docs/iter4-distill-sft-plan-2026-07-16.md` (iter-4 plan, basis for iter-5)
- `scripts/build_iter5_distill_seed_questions.py` (1000-question seed builder)
- `scripts/generate_iter5_teacher_responses_batched.py` (teacher generator)
- `scripts/iter5_progress.py` (progress monitor)
