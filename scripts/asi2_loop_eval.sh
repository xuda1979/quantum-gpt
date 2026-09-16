#!/usr/bin/env bash
# =============================================================================
# asi2_loop_eval.sh — idempotent 5h-eval runner for ASI2 RL checkpoints.
#
# Every ~5h the watchdog loop calls this script. It:
#   1. Lists NAS checkpoints (checkpoint_<ts>) + run outputs on the box (via
#      the daemon /exec transport, http://127.0.0.1:19004/exec) and picks the
#      newest checkpoint as the eval target (fallback: newest run's adapter).
#   2. Skips if the newest checkpoint was already evaluated (local state file
#      reports/.asi2_eval_state.json OR on-box marker
#      outputs/reeval_latest_<ts>.json / outputs/grpo-27b-selfeval-<ts>/reeval_*).
#      Prints "ALREADY_EVALUATED <ts>" and exits 0.
#   3. Runs a FAST CPU-only adapter-delta precheck on the box (merge the
#      adapter into the base with peft -> max_abs_diff across weights). If
#      max_abs_diff == 0 the checkpoint is INERT (the failure mode of every
#      past checkpoint); a diff within bf16 rounding ULP is
#      INERT_AT_PRECISION (audit #6). Both skip the expensive rubric eval.
#   4. Otherwise launches scripts/run_asi2_base_adapter_rubric_eval.py on the
#      box via nohup (takes hours, needs NPUs), polls every EVAL_POLL_INTERVAL
#      seconds up to EVAL_WAIT_SECONDS for the output file to appear, then
#      prints the verdict (pass@1 base vs adapter, rubric, heldout CE loss).
#   5. Records the result in the local state file.
#
# Evaluator CLI (from scripts/run_asi2_base_adapter_rubric_eval.py):
#   python3 scripts/run_asi2_base_adapter_rubric_eval.py \
#       --base-model <required> --adapter <required> --output <required> \
#       [--device npu] [--max-new-tokens 384] [--limit 0]
#   (--limit 0 = ALL tasks in EVAL_BENCHMARK — the FROZEN 18-task promotion
#   holdout by default (2026-09-01 instrument fix; was the 13-task TRAINING
#   set, which is not a valid beats-base instrument); writes the output file
#   atomically, then prints a "done" JSON line.)
#
# Auth-down handling: if the /exec daemon returns an empty/non-JSON response
# the helper prints AUTH_DOWN and the script exits 2 so the loop retries later.
#
# Exit codes: 0 = handled (evaluated / already evaluated / inert / still
# running / nothing to do), 2 = AUTH_DOWN (retry later), 1 = hard error.
#
# Usage:
#   bash scripts/asi2_loop_eval.sh [--dry-run]
#
# Env overrides:
#   DAEMON_PORT             daemon port (default 19004)
#   REMOTE_ROOT             remote repo root (default /root/work/software/quantum-gpt)
#   NAS_CHECKPOINT_ROOT     NAS checkpoint root (default
#                           /root/work/filestorage/grpo_checkpoints/qwen36_27b_selfeval)
#   BASE_MODEL              base model path (default /root/work/filestorage/Qwen3.8-27B,
#                           the model the SAPO run fine-tunes; must match its --model-name)
#   EVAL_WAIT_SECONDS       max wait for rubric eval output (default 7200)
#   EVAL_POLL_INTERVAL      rubric eval poll cadence (default 60)
#   PRECHECK_WAIT_SECONDS   max wait for precheck output (default 3600)
#   PRECHECK_POLL_INTERVAL  precheck poll cadence (default 30)
#   PRECHECK_DEVICE         precheck merge device (default cpu; NPU-free)
#   EVAL_STATE_FILE         local state marker file (default reports/.asi2_eval_state.json)
#   SAPO_RUN_DIR            evaluate a checkpoint inside this run dir (the
#                           parallel-eval agent's driver; takes precedence)
#   SAPO_RUN_ADAPTER        basename pinning ONE checkpoint inside SAPO_RUN_DIR
#   SAPO_EVAL_LIB_ONLY=1    define the functions and STOP (test seam: lets a
#                           test call checkpoint_identity/state_get/update_state
#                           without a box probe or a main flow)
#   DRY_RUN=1               print the plan without touching anything
# =============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ---------------- config (env-overridable) ----------------
DAEMON_PORT="${DAEMON_PORT:-19004}"
DAEMON_BASE="http://127.0.0.1:${DAEMON_PORT}"
REMOTE_ROOT="${REMOTE_ROOT:-/root/work/software/quantum-gpt}"
NAS_CHECKPOINT_ROOT="${NAS_CHECKPOINT_ROOT:-/root/work/filestorage/grpo_checkpoints/qwen36_27b_selfeval}"
# B-221 (2026-09-14): the SAPO run fine-tunes Qwen3.8-27B (its --model-name), and the
# promotion verdict instrument scores against THAT base (1/18). This default used to be
# Qwen3.6-27B, so every leg fired without an explicit BASE_MODEL compared the adapter
# against the WRONG base (3/18) and wrote verdicts saying
#   "tie vs Qwen3.6 base (3/18=3/18); ... NO promotion per tie rule"
# for adapters that genuinely beat the real base. A stale default that silently changes
# the meaning of every verdict is the worst class of instrument defect.
BASE_MODEL="${BASE_MODEL:-/root/work/filestorage/Qwen3.8-27B}"
EVAL_WAIT_SECONDS="${EVAL_WAIT_SECONDS:-7200}"
EVAL_POLL_INTERVAL="${EVAL_POLL_INTERVAL:-60}"
PRECHECK_WAIT_SECONDS="${PRECHECK_WAIT_SECONDS:-3600}"
PRECHECK_POLL_INTERVAL="${PRECHECK_POLL_INTERVAL:-30}"
PRECHECK_DEVICE="${PRECHECK_DEVICE:-cpu}"
EVAL_STATE_FILE="${EVAL_STATE_FILE:-${ROOT_DIR}/reports/.asi2_eval_state.json}"
# C-0036: asi2-eval box lease -- serialize eval-leg dispatch at ASI2. C-0035
# measured ZERO callers of the landed helper lock, so N concurrent launchers
# still double-fired 18-task NPU legs. EVAL_LOCK_FILE is overridable so tests
# can point it at a temp dir (test_eval_launcher_lock.py).
EVAL_LOCK_FILE="${EVAL_LOCK_FILE:-${ROOT_DIR}/harness/state/locks/asi2-eval.lock}"
EVAL_LOCK_TOKEN=""

# C-0048 (finishing bounced C-0028): launch-side freeze-integrity gate. The
# asi2-eval lease serializes legs, but nothing here refused to FIRE a leg
# against a drifted holdout/scorer -- the box-side driver check (C-0024)
# only runs AFTER the leg is dispatched, so the serialized slot and the
# poll window still burn. FREEZE_* are overridable so tests can point the
# gate at a throwaway tree (test_eval_launcher_freeze_gate.py).
FREEZE_REPO_ROOT="${FREEZE_REPO_ROOT:-${ROOT_DIR}}"
FREEZE_MANIFEST="${FREEZE_MANIFEST:-${FREEZE_REPO_ROOT}/evals/benchmarks/sapo_promotion_holdout_v1_18.sha256}"

# 2026-09-01 (manager, beats-base instrument fix): the rubric eval MUST run on
# the FROZEN promotion holdout — the loop previously omitted --benchmark and
# the evaluator defaulted to the 13-task v1 TRAINING set (whose header forbids
# eval use; only 4/18 overlap with the frozen holdout), so even a genuinely
# better adapter never showed beats-base through the loop. Default = the
# frozen 18-task gate; override only for deliberate experiments.
EVAL_BENCHMARK="${EVAL_BENCHMARK:-${ROOT_DIR}/evals/benchmarks/sapo_promotion_holdout_v1_18.txt}"
# box-relative benchmark path (the EVAL_CMD runs with cd ${REMOTE_ROOT}):
# 2026-09-01 (P-7 fix): DERIVE from EVAL_BENCHMARK by stripping the local
# ROOT_DIR prefix — EVAL_BENCHMARK was dead config (only the hardcoded box
# path reached the launch). Setting EVAL_BENCHMARK=<custom> now actually
# changes what the box evaluates. Falls back to the basename if the path
# is not under ROOT_DIR.
EVAL_BENCHMARK_BOX="${EVAL_BENCHMARK#${ROOT_DIR}/}"
if [[ "$EVAL_BENCHMARK_BOX" == "$EVAL_BENCHMARK" ]]; then
  EVAL_BENCHMARK_BOX="$(basename "$EVAL_BENCHMARK")"
fi

if [[ "${1:-}" == "--dry-run" || "${DRY_RUN:-0}" == "1" ]]; then
  DRY_RUN=1
else
  DRY_RUN=0
fi
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  sed -n '2,60p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//' >&2
  exit 0
fi

# ---------------- helpers ----------------
# log: timestamped, human-readable -> stderr (stdout stays machine-readable)
log() { printf '[%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >&2; }
# say: status keywords for the watchdog loop -> stdout
say() { printf '%s\n' "$*"; }

# checkpoint_identity CHECKPOINT_PATH -> the state key for this checkpoint.
#
# 2026-09-11 (B-107, the B-105 family): the state entry used to be keyed by the
# BARE STEP NUMBER (`step_000047_adapter` -> `47`), with the adapter path kept
# only in the entry's `adapter` field. The parallel-eval agent keys its
# done-filter by the checkpoint's FULL PATH, and the state file is per-ENV, not
# per-run — so the agent's lookup never matched a verdict this loop wrote and
# re-fired every already-evaluated checkpoint (the live, endless
# `step_000024_adapter` re-eval loop). A bare step number is not an identity:
# it is identical across runs, which is exactly the ambiguity B-105 fixed on the
# agent side. The fix belongs HERE, in the writer, so writer and reader agree on
# one key; making the reader re-derive a key from `adapter` would keep two
# implementations of "which checkpoint is this" in the tree.
#
# The key is the path the caller gave, normalized (no trailing slash, no doubled
# slash) and otherwise verbatim — exactly the string the agent computes from its
# own listing. A bare basename (no path separator, so nothing to disambiguate)
# is returned UNFOLDED: folding `step_000004_adapter` to `4` here would recreate
# the cross-run ambiguity this fix removes, and would key the same checkpoint
# under two different names depending on how the caller spelled it.
#
# FAIL-CLOSED: no caller may treat a NON-matching key as a verdict. An
# unrecognised checkpoint stays PENDING and is re-evaluated (see state_get +
# the already-evaluated check below) — re-evaluating a finished checkpoint costs
# one leg, while suppressing an unevaluated one is a silent coverage gap.
checkpoint_identity() {
  local raw="${1:-}" path
  # collapse the doubled slashes a caller-built run dir can carry
  # (live state shows `.../outputs/sapo-27b-ai-20260902T072812Z//step_000001_adapter`)
  # so the same checkpoint always yields the same key.
  path="$(printf '%s' "$raw" | sed -e 's|//*|/|g')"
  case "$path" in
    "")  printf '%s' ""; return 0;;
    /)   printf '%s' "/"; return 0;;           # degenerate, but a path
    */*) printf '%s' "${path%/}"; return 0;;   # a real path is its own identity
  esac
  printf '%s' "$path"   # bare name: no path to normalise, and never folded
}

jq_escape() {
  python3 -c 'import json, sys; print(json.dumps(sys.argv[1]))' "$1"
}

# exec_remote CMD [quiet]
#   POST CMD to the daemon /exec. On success prints the remote stdout, rc 0.
#   On failure (empty / non-JSON / ok!=true, i.e. auth down) prints "AUTH_DOWN"
#   to stdout (unless quiet=1) and returns 2.
exec_remote() {
  local cmd="$1"
  local quiet="${2:-0}"
  local resp out rc=0
  if ! resp=$(curl -sS --max-time 130 -X POST "${DAEMON_BASE}/exec" \
      -H 'Content-Type: application/json' \
      -d "{\"command\": $(jq_escape "$cmd"), \"waitMs\": 90000}" 2>/dev/null); then
    log "exec_remote: curl failed to ${DAEMON_BASE}/exec (daemon down?)"
    if [[ "$quiet" != "1" ]]; then printf '%s' "AUTH_DOWN"; fi
    return 2
  fi
  out=$(printf '%s' "$resp" | python3 -c '
import json, re, sys
raw = sys.stdin.read()
try:
    d = json.loads(raw)
except Exception:
    sys.exit(2)
if not isinstance(d, dict) or d.get("ok") is not True:
    sys.exit(2)
out = d.get("output") or ""
if isinstance(out, str):
    out = re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", out)
    sys.stdout.write(out.split("__ASI2_RUN")[0])
') || rc=$?
  if [[ $rc -ne 0 ]]; then
    log "exec_remote: daemon response empty/non-JSON/ok!=true (auth down?)"
    if [[ "$quiet" != "1" ]]; then printf '%s' "AUTH_DOWN"; fi
    return 2
  fi
  printf '%s' "$out"
  return 0
}

# marker_is_for_checkpoint MARKER ADAPTER -> is MARKER a verdict for ADAPTER?
#
# B-229 (measured live 2026-09-14, run sapo-27b-ai-20260913T233607Z): the on-box
# marker fallback below globs outputs/reeval_latest_<TS>.json, keyed by the leg's
# SHORT name alone -- a bare step number, identical across runs. An existing file
# was therefore taken as a verdict for whatever checkpoint this leg happened to be
# evaluating. Live: step_000003_adapter was backfilled as status=done
# verdict=marker-found from reeval_latest_3.json dated 2026-09-02T13:58:57Z
# (a different epoch: pass_at_1 adapter 3/18 base 3/18) and the leg never ran.
# That is the silent coverage gap the identity check above exists to prevent --
# the marker path re-opened it (same shape as B-105/B-107, one layer down).
#
# A marker is a verdict only for the checkpoint it was produced FROM, so it must
# be at least as new as the adapter directory it is claimed for. Freshness is
# format-agnostic (the two marker producers write different JSON shapes).
# Unknown freshness -- daemon down, auth down, no stat -- fails CLOSED: the
# checkpoint is EVALUATED. A re-run costs one leg; a false DONE costs coverage.
marker_is_for_checkpoint() {
  local marker="$1" adapter="$2" out m a
  if [[ -z "$marker" || -z "$adapter" ]]; then return 1; fi
  if ! out=$(exec_remote "stat -c %Y '$marker' 2>/dev/null; stat -c %Y '$adapter' 2>/dev/null"); then
    return 1
  fi
  m=$(printf '%s\n' "$out" | sed -n '1p' | tr -dc '0-9')
  a=$(printf '%s\n' "$out" | sed -n '2p' | tr -dc '0-9')
  if [[ -z "$m" || -z "$a" ]]; then return 1; fi
  [[ "$m" -ge "$a" ]]
}

# state_get TS -> prints the state entry status ("" if absent)
state_get() {
  python3 - "$EVAL_STATE_FILE" "$1" <<'PYEOF'
import json, os, sys
path, ts = sys.argv[1], sys.argv[2]
status = ""
if os.path.exists(path):
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception:
        data = {}
    if not isinstance(data, dict):
        data = {}
    entry = data.get(ts)
    if isinstance(entry, dict):
        status = entry.get("status", "")
print(status)
PYEOF
}

# update_state TS STATUS VERDICT EVAL_OUTPUT ADAPTER MAX_ABS_DIFF EXTRA_JSON
update_state() {
  local ts="$1" status="$2" verdict="$3" eval_output="$4" adapter="$5"
  local max_abs_diff="${6:-null}" extra="${7:-"{}"}"
  python3 - "$EVAL_STATE_FILE" "$ts" "$status" "$verdict" "$eval_output" \
      "$adapter" "$max_abs_diff" "$extra" <<'PYEOF'
import datetime, json, os, sys
path, ts, status, verdict = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
eval_output, adapter, max_abs_diff, extra = (
    sys.argv[5], sys.argv[6], sys.argv[7], json.loads(sys.argv[8] or "{}"))
data = {}
if os.path.exists(path):
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception:
        data = {}
    if not isinstance(data, dict):
        data = {}
entry = {
    "status": status,
    "verdict": verdict,
    "eval_output": eval_output or None,
    "adapter": adapter or None,
    "max_abs_diff": float(max_abs_diff) if max_abs_diff not in ("", "null") else None,
    "updated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
entry.update(extra)
data[ts] = entry
os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
tmp = path + ".tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump(data, fh, indent=2, sort_keys=True)
    fh.write("\n")
os.replace(tmp, path)
PYEOF
}

# poll_for_file REMOTE_PATH TIMEOUT INTERVAL LABEL
#   Polls the box every INTERVAL s until REMOTE_PATH exists or TIMEOUT passes.
#   Tolerates transient daemon flakes during polling (continues).
poll_for_file() {
  local path="$1" timeout="$2" interval="$3" label="$4"
  local waited=0 mark=""
  while [[ $waited -lt $timeout ]]; do
    sleep "$interval"
    waited=$((waited + interval))
    mark=""
    if mark=$(exec_remote "test -f ${path} && echo DONE || echo PENDING" 1); then
      if [[ "$mark" == *DONE* ]]; then
        log "${label}: output file present (${path}, waited ${waited}s)"
        return 0
      fi
    else
      log "${label}: poll call failed, continuing (waited ${waited}s)"
    fi
  done
  log "${label}: timeout after ${timeout}s — ${path} not present yet"
  return 1
}

# ---------------- asi2-eval box lease (C-0036) ----------------
# Defined BEFORE the SAPO_EVAL_LIB_ONLY seam so tests can source the launcher
# and drive the lease path with no box probe (test_eval_launcher_lock.py).
asi2_eval_lock_acquire() {
  # Take the lease via harness_lib.acquire_lock, then rewrite the holder pid
  # to THIS launcher shell ($$): acquire_lock stamps the short-lived python
  # helper's pid, and a young lock with a dead pid is taken over, so without
  # the rewrite the next launcher could steal the lease mid-dispatch. Prints
  # LOCK_BUSY (rc 1) when a fresh lease held by a live pid exists.
  EVAL_LOCK_TOKEN="$(python3 - "$EVAL_LOCK_FILE" "$$" "${ROOT_DIR}/harness" <<'PYLOCK'
import json, sys
sys.path.insert(0, sys.argv[3])
import harness_lib
tok = harness_lib.acquire_lock(sys.argv[1])
if tok is None:
    print("LOCK_BUSY")
else:
    tok["pid"] = int(sys.argv[2])
    with open(sys.argv[1], "w", encoding="utf-8") as f:
        json.dump(tok, f)
    print(json.dumps(tok))
PYLOCK
)" || return 1
  if [[ "$EVAL_LOCK_TOKEN" == "LOCK_BUSY" ]]; then
    return 1
  fi
  log "asi2-eval lease acquired: ${EVAL_LOCK_FILE}"
  return 0
}

asi2_eval_lock_release() {
  if [[ -n "${EVAL_LOCK_TOKEN:-}" ]]; then
    python3 - "$EVAL_LOCK_FILE" "$EVAL_LOCK_TOKEN" "${ROOT_DIR}/harness" <<'PYUNLOCK' >/dev/null 2>&1 || true
import json, sys
sys.path.insert(0, sys.argv[3])
import harness_lib
print(harness_lib.release_lock(sys.argv[1], json.loads(sys.argv[2])))
PYUNLOCK
    EVAL_LOCK_TOKEN=""
  fi
  return 0
}

# ---------------- freeze-integrity sha gate (C-0024/C-0048) ----------------
# Defined BEFORE the SAPO_EVAL_LIB_ONLY seam so tests can source the launcher
# and drive the gate against a throwaway tree with no box probe
# (test_eval_launcher_freeze_gate.py). Fail-closed: drift, a missing covered
# file, or a missing manifest all refuse the leg and NAME the violation. On
# success it stamps one `freeze sha <digest> <rel>` line per covered file
# into this log, so the leg log records WHICH bytes the holdout/scorer ran
# under (traceability for cross-leg verdict comparison).
asi2_eval_freeze_gate() {
  local out
  if ! out="$(python3 - "$ROOT_DIR" "${FREEZE_REPO_ROOT}" "${FREEZE_MANIFEST}" <<'PYFREEZE'
import sys
sys.path.insert(0, sys.argv[1])
from evals.runner.holdout_freeze import HoldoutFreezeError, verify_holdout_freeze
try:
    entries = verify_holdout_freeze(repo_root=sys.argv[2], manifest_path=sys.argv[3])
except HoldoutFreezeError as exc:
    print("FREEZE_VIOLATION: " + str(exc))
    sys.exit(1)
for rel, digest in entries:
    print("freeze sha {} {}".format(digest, rel))
PYFREEZE
)"; then
    log "freeze-integrity gate FAILED -- refusing the eval leg (fail-closed): ${out}"
    return 1
  fi
  while IFS= read -r line; do
    log "${line}"
  done <<< "${out}"
  log "freeze-integrity gate OK: $(printf '%s\n' "${out}" | grep -c '^freeze sha ' || true) files verified against the freeze manifest"
  return 0
}

# ---------------- dry run ----------------
if [[ $DRY_RUN == 1 ]]; then
  say "DRY_RUN — no /exec calls, no state writes. Plan:"
  say ""
  say "Step 1  find newest target on the box:"
  say "  exec_remote: ls -t ${NAS_CHECKPOINT_ROOT}/ 2>/dev/null | grep -E '^checkpoint_[0-9T]+(_step[0-9a-z]+)?$' | head -1"
  say "  exec_remote: ls -t ${REMOTE_ROOT}/outputs/ 2>/dev/null | grep '^grpo-27b-selfeval-[0-9T]\\+$' | head -1"
  say "  exec_remote: probe newest run's adapter dir (adapter/ preferred, else newest step_*_adapter)"
  say "  target = newest NAS checkpoint_<ts> (fallback: newest run adapter)"
  say ""
  say "Step 2  idempotency markers for <ts>:"
  say "  local  ${EVAL_STATE_FILE} entry with status done/inert  -> ALREADY_EVALUATED"
  say "  remote ${REMOTE_ROOT}/outputs/reeval_latest_<ts>.json or grpo-27b-selfeval-<ts>/reeval_*.json"
  say "  remote /tmp/reeval_<ts>.pid alive                        -> EVAL_RUNNING"
  say "  -> prints ALREADY_EVALUATED <ts> and exits 0"
  say ""
  say "Step 3  fast CPU-only adapter-delta precheck on the box:"
  say "  upload embedded precheck python (~4KB) in base64 chunks -> /tmp/asi2_loop_precheck_<ts>.py"
  say "  nohup python3 /tmp/asi2_loop_precheck_<ts>.py --adapter <target> --base ${BASE_MODEL} \\"
  say "        --output ${REMOTE_ROOT}/outputs/adapter_delta_<ts>.json --device ${PRECHECK_DEVICE}"
  say "  phase 1 (seconds, no model load): all LoRA A/B zero -> max_abs_diff=0"
  say "  phase 2 (CPU merge via PeftModel.merge_and_unload + base) only if phase 1 inconclusive"
  say "  verdict (audit #6, bf16-ULP aware): max_abs_diff == 0 -> INERT;"
  say "    0 < diff <= bf16 ULP at weight scale -> INERT_AT_PRECISION;"
  say "    else ACTIVE — INERT/INERT_AT_PRECISION mark state, exit 0 (no rubric eval)"
  say ""
  say "Step 4  rubric eval on NPUs (hours), only if delta != 0:"
  say "  cd ${REMOTE_ROOT} && nohup python3 scripts/run_asi2_base_adapter_rubric_eval.py \\"
  say "    --base-model '${BASE_MODEL}' --adapter '<target>' \\"
  say "    --output 'outputs/reeval_latest_<ts>.json' --benchmark '${EVAL_BENCHMARK_BOX}' \\"
  say "    --device npu --max-new-tokens 384 --limit 0 \\"
  say "    > /tmp/reeval_<ts>.log 2>&1 & echo \$! > /tmp/reeval_<ts>.pid"
  say "  poll every ${EVAL_POLL_INTERVAL}s up to ${EVAL_WAIT_SECONDS}s for the output file"
  say ""
  say "Step 5  print verdict (pass@1 base vs adapter, rubric, heldout CE loss, max_abs_diff)"
  say "        and update ${EVAL_STATE_FILE}"
  exit 0
fi

# ---------------- main flow ----------------
# Test seam (SAPO_EVAL_LIB_ONLY=1, see the env block at the top): every helper
# above is now defined, so stop BEFORE the first box probe. Default 0 = the real
# main flow, unchanged.
if [[ "${SAPO_EVAL_LIB_ONLY:-0}" == "1" ]]; then
  return 0 2>/dev/null || exit 0
fi

log "asi2_loop_eval start (daemon=${DAEMON_BASE} remote=${REMOTE_ROOT} state=${EVAL_STATE_FILE})"

# ---- step 1a: newest NAS checkpoint ----
# Snapshot names are checkpoint_<ts> (legacy) or checkpoint_<ts>_step<N>
# (sync-daemon step-content naming, audit #5) — accept both.
if ! NAS_OUT=$(exec_remote "ls -t ${NAS_CHECKPOINT_ROOT}/ 2>/dev/null | grep -E '^checkpoint_[0-9T]+(_step[0-9a-z]+)?$' | head -1"); then
  printf '%s\n' "${NAS_OUT:-AUTH_DOWN}"
  exit 2
fi
NAS_TS=$(printf '%s' "$NAS_OUT" | head -1 | sed -E 's/^checkpoint_([0-9T]+)(_step[0-9a-z]+)?$/\1/' | tr -d '[:space:]')
NAS_STEP=$(printf '%s' "$NAS_OUT" | head -1 | sed -nE 's/^checkpoint_[0-9T]+_step([0-9]+)$/\1/p')
TS="$NAS_TS"
log "newest NAS checkpoint ts: ${TS:-<none>} step: ${NAS_STEP:-<none>}"

# ---- step 1b: newest run output dir + its adapter dir ----
RUN_TS=""
if ! RUN_OUT=$(exec_remote "ls -t ${REMOTE_ROOT}/outputs/ 2>/dev/null | grep '^grpo-27b-selfeval-[0-9T]\\+$' | head -1"); then
  printf '%s\n' "${RUN_OUT:-AUTH_DOWN}"
  exit 2
fi
RUN_TS=$(printf '%s' "$RUN_OUT" | head -1 | sed 's/^grpo-27b-selfeval-//' | tr -d '[:space:]')
log "newest run output ts: ${RUN_TS:-<none>}"

RUN_ADAPTER=""
if [[ -n "$RUN_TS" ]]; then
  if ! RUN_ADAPTER=$(exec_remote "if [ -d '${REMOTE_ROOT}/outputs/grpo-27b-selfeval-${RUN_TS}/adapter' ]; then echo '${REMOTE_ROOT}/outputs/grpo-27b-selfeval-${RUN_TS}/adapter'; else ls -dt '${REMOTE_ROOT}/outputs/grpo-27b-selfeval-${RUN_TS}'/step_*_adapter 2>/dev/null | head -1; fi"); then
    printf '%s\n' "${RUN_ADAPTER:-AUTH_DOWN}"
    exit 2
  fi
  RUN_ADAPTER=$(printf '%s' "$RUN_ADAPTER" | head -1 | tr -d '[:space:]')
  log "newest run adapter dir: ${RUN_ADAPTER:-<none>}"
fi

# ---- step 1c: pick the eval target ----
# 2026-09-02: SAPO_RUN_DIR override — evaluate the newest step_*_adapter in an
# explicit run dir (resume-3 era). Takes precedence over NAS/run-glob selection
# so the parallel-eval agent targets the LIVE run's checkpoints, not stale NAS.
# SAPO_RUN_ADAPTER (basename) pins ONE checkpoint inside SAPO_RUN_DIR — used to
# schedule high-priority legs (e.g. step_000009, the first-pass checkpoint).
TARGET_KIND=""
if [[ -n "${SAPO_RUN_DIR:-}" ]]; then
  if [[ -n "${SAPO_RUN_ADAPTER:-}" ]]; then
    SAPO_ADAPTER="${SAPO_RUN_DIR%/}/${SAPO_RUN_ADAPTER}"
    if ! exec_remote "test -d '${SAPO_ADAPTER}'"; then
      say "NO_CHECKPOINTS"
      log "SAPO_RUN_ADAPTER ${SAPO_RUN_ADAPTER} not found in ${SAPO_RUN_DIR}"
      exit 0
    fi
  elif ! SAPO_ADAPTER=$(exec_remote "ls -dt ${SAPO_RUN_DIR}/step_*_adapter 2>/dev/null | head -1"); then
    printf '%s\n' "AUTH_DOWN"; exit 2
  fi
  SAPO_ADAPTER=$(printf '%s' "$SAPO_ADAPTER" | head -1 | tr -d '[:space:]')
  if [[ -z "$SAPO_ADAPTER" ]]; then
    say "NO_CHECKPOINTS"
    log "SAPO_RUN_DIR set but no step_*_adapter found in ${SAPO_RUN_DIR}"
    exit 0
  fi
  TARGET_KIND="run-adapter"
  TS="$(basename "$SAPO_ADAPTER" | sed -E 's/step_0*([0-9]+)_adapter/\1/')"
  ADAPTER="$SAPO_ADAPTER"
  log "eval target (SAPO_RUN_DIR): ${ADAPTER}"
elif [[ -n "$TS" ]]; then
  TARGET_KIND="nas-checkpoint"
  ADAPTER="${NAS_CHECKPOINT_ROOT}/checkpoint_${TS}"
  log "eval target: NAS checkpoint ${ADAPTER}"
elif [[ -n "$RUN_ADAPTER" ]]; then
  TARGET_KIND="run-adapter"
  TS="$RUN_TS"
  ADAPTER="$RUN_ADAPTER"
  log "eval target (NAS empty fallback): run adapter ${ADAPTER}"
else
  say "NO_CHECKPOINTS"
  log "no NAS checkpoints and no run adapter found — nothing to evaluate"
  exit 0
fi

# ---- step 1d: the checkpoint's state identity (B-107) ----
# ONE definition, used by every state read and write below. `$TS` stays the
# leg's SHORT name and is still what the box-side artifact paths are built from
# (/tmp/reeval_<ts>.json, adapter_delta_<ts>.json, the on-box marker names) —
# those are the leg's own files and must keep their existing names.
STATE_KEY="$(checkpoint_identity "$ADAPTER")"
log "state key: ${STATE_KEY:-<none>} (leg short name ${TS:-<none>})"

# ---- step 2: already evaluated? ----
# FAIL-CLOSED: only THIS checkpoint's own identity counts as a verdict. A key
# that does not match (a legacy bare step number, another run's checkpoint, a
# path written by an older tree) leaves it PENDING and the leg re-runs. Never
# widen this to "any entry that looks like it might be this one": an unmatched
# key suppressing a leg is a silent coverage gap, the worse failure of the two.
ST=$(state_get "$STATE_KEY")
if [[ "$ST" == "done" || "$ST" == "inert" ]]; then
  say "ALREADY_EVALUATED ${TS}"
  log "local state file already marks ${STATE_KEY} as ${ST} (leg short name ${TS})"
  exit 0
fi
if ! MARKER_OUT=$(exec_remote "for f in ${REMOTE_ROOT}/outputs/reeval_latest_${TS}.json ${REMOTE_ROOT}/outputs/grpo-27b-selfeval-${TS}/reeval_*.json; do if [ -f \"\$f\" ]; then echo \"\$f\"; break; fi; done"); then
  printf '%s\n' "${MARKER_OUT:-AUTH_DOWN}"
  exit 2
fi
MARKER_OUT=$(printf '%s' "$MARKER_OUT" | head -1 | tr -d '[:space:]')
if [[ -n "$MARKER_OUT" ]]; then
  if marker_is_for_checkpoint "$MARKER_OUT" "$ADAPTER"; then
  say "ALREADY_EVALUATED ${TS}"
  log "on-box marker found: ${MARKER_OUT}; backfilling local state"
  update_state "$STATE_KEY" "done" "marker-found" "${MARKER_OUT}" "$ADAPTER" "null" '{"source": "on-box-marker"}'
  exit 0
  fi
  # B-229: the marker is not a verdict for THIS checkpoint -- evaluate it.
  say "STALE_MARKER $TS"
  log "on-box marker $MARKER_OUT predates $ADAPTER -- not a verdict for this checkpoint; evaluating"
fi

# checkpoint completeness (adapter_config.json + at least one safetensors)
if [[ "$TARGET_KIND" == "nas-checkpoint" ]]; then
  if ! CFG=$(exec_remote "ls ${ADAPTER}/adapter_config.json ${ADAPTER}/*.safetensors >/dev/null 2>&1 && echo CFG_OK || echo CFG_MISSING"); then
    printf '%s\n' "${CFG:-AUTH_DOWN}"
    exit 2
  fi
  if [[ "$CFG" != *CFG_OK* ]]; then
    say "CHECKPOINT_INCOMPLETE ${TS}"
    log "checkpoint dir ${ADAPTER} lacks adapter_config.json/safetensors — skip this cycle"
    exit 0
  fi
fi

# ---- step 3a: precheck already running for this ts? ----
if ! PIDSTATE=$(exec_remote "if [ -f /tmp/asi2_loop_precheck_${TS}.pid ] && kill -0 \$(cat /tmp/asi2_loop_precheck_${TS}.pid) 2>/dev/null; then echo RUNNING; else echo NOT_RUNNING; fi"); then
  printf '%s\n' "${PIDSTATE:-AUTH_DOWN}"
  exit 2
fi
if [[ "$PIDSTATE" == *RUNNING* && "$PIDSTATE" != *NOT_RUNNING* ]]; then
  say "PRECHECK_RUNNING ${TS}"
  update_state "$STATE_KEY" "pending" "precheck-running" "" "$ADAPTER" "null"
  exit 0
fi
exec_remote "rm -f /tmp/asi2_loop_precheck_${TS}.pid /tmp/asi2_loop_precheck_${TS}.log" >/dev/null 2>&1 || true

# ---- step 3b: upload the precheck script (chunked base64, ~4K chunks) ----
PRECHECK_LOCAL_DIR="$(mktemp -d)"
trap 'rm -rf "${PRECHECK_LOCAL_DIR-}"' EXIT
PRECHECK_LOCAL="${PRECHECK_LOCAL_DIR}/asi2_loop_precheck.py"
cat > "$PRECHECK_LOCAL" <<'PYEOF'
#!/usr/bin/env python3
"""Fast adapter-delta precheck for an ASI2 RL checkpoint (runs on the box).

Phase 1 (seconds, no model load): inspect the adapter safetensors. If every
tensor is a LoRA A/B matrix and no module has both a nonzero A and a nonzero B,
the merged weights are bit-identical to base by construction -> max_abs_diff=0.
Phase 2 (minutes, CPU merge): only when phase 1 is inconclusive -- load the
base model and PeftModel.from_pretrained(...).merge_and_unload(), then report
max_abs_diff across all shared tensors (the definitive check used by past
reports; max_abs_diff == 0 -> inert adapter). Verdicts are bf16-ULP aware
(audit #6): "active" requires a per-tensor diff above one ULP at that
weight's scale; smaller nonzero diffs are "inert_at_precision".

Writes a JSON result to --output and prints a compact one-line result.
"""
import argparse, json, math, os, sys, time
from pathlib import Path

QG_ROOT = os.environ.get("QG_ROOT", "/root/work/software/quantum-gpt")
if QG_ROOT not in sys.path:
    sys.path.insert(0, QG_ROOT)


def load_tensors(adapter_dir):
    try:
        from safetensors import safe_open
    except Exception:
        safe_open = None
    files = sorted(Path(adapter_dir).glob("*.safetensors"))
    tensors = {}
    if safe_open is None:
        import torch
        for f in files:
            tensors.update(torch.load(f, map_location="cpu", weights_only=True))
        return tensors
    for f in files:
        with safe_open(str(f), framework="pt", device="cpu") as h:
            for k in h.keys():
                tensors[k] = h.get_tensor(k)
    return tensors


def phase1(tensors):
    pairs = {}
    lora_only = True
    for name, t in tensors.items():
        if "lora_A" in name:
            pairs.setdefault(name.split("lora_A")[0], {})["A"] = t
        elif "lora_B" in name:
            pairs.setdefault(name.split("lora_B")[0], {})["B"] = t
        else:
            lora_only = False
    max_abs_all = max((t.abs().max().item() for t in tensors.values()), default=0.0)
    max_abs_b = max(
        (p["B"].abs().max().item() for p in pairs.values() if p.get("B") is not None),
        default=0.0,
    )
    possible = any(
        p.get("A") is not None and p.get("B") is not None
        and p["A"].abs().max().item() > 0.0 and p["B"].abs().max().item() > 0.0
        for p in pairs.values()
    )
    return {
        "lora_only": lora_only,
        "max_abs_lora": max_abs_all,
        "max_abs_lora_b": max_abs_b,
        "nonzero_pair_possible": possible,
    }


def phase2(base_path, adapter_dir, device):
    from training.runtime_overlay import configure_runtime_overlay_from_env
    configure_runtime_overlay_from_env()
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM
    from training.model_backend import load_causal_lm_with_text_backend_preflight
    from training.qwen_sft_peft import resolve_device
    dev = resolve_device(torch, device)
    base = load_causal_lm_with_text_backend_preflight(
        base_path,
        auto_config_cls=AutoConfig,
        auto_model_for_causal_lm_cls=AutoModelForCausalLM,
        model_kwargs={"trust_remote_code": True, "low_cpu_mem_usage": True, "torch_dtype": "auto"},
    ).to(dev)
    base.eval()
    # CRITICAL (2026-08-21 review): peft's merge_and_unload() mutates the base
    # params IN PLACE — holding references made every comparison report
    # max_abs_diff=0 ("inert") even for a functional adapter (proven: true
    # delta 0.54 reported 0.0). Clone BEFORE merging.
    base_params = {n: p.detach().clone() for n, p in base.named_parameters()}
    from peft import PeftModel
    merged = PeftModel.from_pretrained(base, str(adapter_dir)).merge_and_unload()
    # Audit #6: a nonzero max_abs_diff from bf16 representational noise
    # (1-2 ULP round-trip) is NOT training progress. Per tensor: bf16 ULP =
    # 2^floor(log2(|w|)) * 2^-7 (significand has 7 mantissa bits); a tensor
    # counts as active only if its max |diff| exceeds one ULP at its own
    # weight scale.
    max_diff = 0.0
    max_ulp = 0.0
    max_abs_weight = 0.0
    any_active = False
    compared = 0
    for name, p in merged.named_parameters():
        if name in base_params:
            compared += 1
            p_f = p.detach().float()
            b_f = base_params[name].detach().float()
            diff = (p_f - b_f).abs().max().item()
            max_w = max(p_f.abs().max().item(), b_f.abs().max().item())
            if max_w > 0.0:
                ulp = 2.0 ** (math.floor(math.log2(max_w)) - 7)
                max_ulp = max(max_ulp, ulp)
                if diff > ulp:
                    any_active = True
            max_abs_weight = max(max_abs_weight, max_w)
            if diff > max_diff:
                max_diff = diff
    return {
        "max_abs_diff": float(max_diff),
        "tensors_compared": compared,
        "max_abs_weight": float(max_abs_weight),
        "max_ulp": float(max_ulp),
        "any_active": any_active,
    }


def finish(output, result):
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".tmp")
    tmp.write_text(json.dumps(result, indent=2, default=str) + "\n")
    tmp.replace(out)
    print(json.dumps(
        {k: result.get(k) for k in (
            "verdict", "phase", "max_abs_diff", "tensors_compared",
            "max_abs_weight", "max_ulp", "any_active",
            "max_abs_lora", "max_abs_lora_b", "error")}, default=str))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args()
    result = {
        "adapter": args.adapter,
        "base": args.base,
        "checked_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    try:
        cfg = json.loads((Path(args.adapter) / "adapter_config.json").read_text())
        r = int(cfg.get("r", 0) or 0)
        alpha = float(cfg.get("lora_alpha", r or 1))
        result["scaling"] = (alpha / r) if r else 1.0
    except Exception as exc:
        result.update(verdict="unknown", error="adapter_config unreadable: %s" % str(exc)[:160])
        return finish(args.output, result)
    tensors = load_tensors(args.adapter)
    if not tensors:
        result.update(verdict="unknown", error="no *.safetensors in adapter dir")
        return finish(args.output, result)
    p1 = phase1(tensors)
    result.update({k: v for k, v in p1.items()})
    if p1["lora_only"] and not p1["nonzero_pair_possible"]:
        result.update(phase=1, verdict="inert", max_abs_diff=0.0, tensors_compared=len(tensors))
        return finish(args.output, result)
    try:
        result["phase"] = 2
        result.update(phase2(args.base, args.adapter, args.device))
        result["max_abs_diff"] = float(result["max_abs_diff"])
        # Audit #6: max_abs_diff > 0 was previously enough for "active", so a
        # few ULP of bf16 round-trip noise in a dead adapter passed the
        # precheck and burned hours of NPU rubric eval. Verdicts:
        #   inert               -> diff == 0
        #   inert_at_precision  -> 0 < diff <= bf16 ULP at the weight scale
        #   active              -> at least one tensor changed by > 1 ULP
        if result["max_abs_diff"] == 0.0:
            result["verdict"] = "inert"
        elif result.get("any_active"):
            result["verdict"] = "active"
        else:
            result["verdict"] = "inert_at_precision"
    except Exception as exc:
        result.update(verdict="unknown", error="phase2 merge failed: %s" % str(exc)[:200])
    return finish(args.output, result)


if __name__ == "__main__":
    raise SystemExit(main())
PYEOF
PRECHECK_BYTES=$(wc -c < "$PRECHECK_LOCAL" | tr -d '[:space:]')
log "precheck script: ${PRECHECK_BYTES} bytes to upload"

exec_remote "rm -f /tmp/asi2_loop_precheck_${TS}.py" >/dev/null 2>&1 || true
UPLOAD_OK=1
while IFS= read -r chunk; do
  [[ -n "$chunk" ]] || continue
  if ! exec_remote "printf '%s' '${chunk}' | base64 -d >> /tmp/asi2_loop_precheck_${TS}.py" >/dev/null 2>&1; then
    UPLOAD_OK=0
    break
  fi
done < <(python3 - "$PRECHECK_LOCAL" <<'CHUNKPY'
import base64, sys
data = open(sys.argv[1], "rb").read()
b64 = base64.b64encode(data).decode()
for i in range(0, len(b64), 4000):
    print(b64[i:i + 4000])
CHUNKPY
) || true
if [[ $UPLOAD_OK != 1 ]]; then
  log "precheck upload failed — aborting this cycle"
  say "AUTH_DOWN"
  exit 2
fi
if ! REMOTE_BYTES=$(exec_remote "wc -c < /tmp/asi2_loop_precheck_${TS}.py"); then
  printf '%s\n' "${REMOTE_BYTES:-AUTH_DOWN}"
  exit 2
fi
REMOTE_BYTES=$(printf '%s' "$REMOTE_BYTES" | head -1 | tr -d '[:space:]')
if [[ "$REMOTE_BYTES" != "$PRECHECK_BYTES" ]]; then
  log "precheck upload size mismatch local=${PRECHECK_BYTES} remote=${REMOTE_BYTES} — abort"
  exit 1
fi
log "precheck script uploaded and verified (${REMOTE_BYTES} bytes)"

# ---- step 3c: launch the precheck (CPU-only, nohup) ----
LAUNCH_OUT=""
if ! LAUNCH_OUT=$(exec_remote "cd ${REMOTE_ROOT}; rm -f outputs/adapter_delta_${TS}.json; nohup python3 /tmp/asi2_loop_precheck_${TS}.py --adapter '${ADAPTER}' --base '${BASE_MODEL}' --output 'outputs/adapter_delta_${TS}.json' --device '${PRECHECK_DEVICE}' > /tmp/asi2_loop_precheck_${TS}.log 2>&1 & echo \$! > /tmp/asi2_loop_precheck_${TS}.pid; echo PRE_PID=\$(cat /tmp/asi2_loop_precheck_${TS}.pid)"); then
  printf '%s\n' "${LAUNCH_OUT:-AUTH_DOWN}"
  exit 2
fi
if ! PIDSTATE=$(exec_remote "test -f /tmp/asi2_loop_precheck_${TS}.pid && echo PID_OK || echo PID_MISSING"); then
  printf '%s\n' "${PIDSTATE:-AUTH_DOWN}"
  exit 2
fi
if [[ "$PIDSTATE" != *PID_OK* ]]; then
  log "precheck launch failed (no pid file) — see /tmp/asi2_loop_precheck_${TS}.log on the box"
  say "PRECHECK_LAUNCH_FAILED ${TS}"
  exit 1
fi
log "precheck launched (pid=$(printf '%s' "$LAUNCH_OUT" | grep -o 'PRE_PID=[0-9]*' | head -1 | cut -d= -f2 || true)); polling up to ${PRECHECK_WAIT_SECONDS}s"
update_state "$STATE_KEY" "pending" "precheck-running" "" "$ADAPTER" "null"

# ---- step 3d: wait for the precheck result ----
if ! poll_for_file "${REMOTE_ROOT}/outputs/adapter_delta_${TS}.json" "$PRECHECK_WAIT_SECONDS" "$PRECHECK_POLL_INTERVAL" "precheck"; then
  say "PRECHECK_PENDING ${TS}"
  log "precheck still running after ${PRECHECK_WAIT_SECONDS}s — will resume next cycle"
  exit 0
fi
if ! PRECHECK_JSON=$(exec_remote "cat ${REMOTE_ROOT}/outputs/adapter_delta_${TS}.json"); then
  printf '%s\n' "${PRECHECK_JSON:-AUTH_DOWN}"
  exit 2
fi
PRECHECK_VERDICT="unknown"
PRECHECK_MAX_DIFF="null"
PRECHECK_PHASE="?"
read -r PRECHECK_VERDICT PRECHECK_MAX_DIFF PRECHECK_PHASE < <(printf '%s' "$PRECHECK_JSON" | python3 -c '
import json, sys
d = json.load(sys.stdin)
print(d.get("verdict", "unknown"),
      str(d.get("max_abs_diff")) if d.get("max_abs_diff") is not None else "null",
      str(d.get("phase", "?")))
') || true
log "precheck result: verdict=${PRECHECK_VERDICT} max_abs_diff=${PRECHECK_MAX_DIFF} phase=${PRECHECK_PHASE}"

# 2026-09-02 (manager, realtime bug fix): PROVABLE-INERT-only gating.
# The precheck used to SKIP the rubric holdout eval for BOTH "inert" (all LoRA
# B tensors zero / max_abs_diff==0, i.e. provably no delta) AND
# "inert_at_precision" (nonzero delta below one bf16 ULP at the largest weight
# scale). The latter is a WRONG skip for LoRA: rank-16 deltas are ~1e-4-1e-3
# while the bf16 ULP at a ~19-magnitude weight is 0.125, so the gate silently
# discarded every genuine resume-3 adapter and NO holdout verdict ever fired
# (step_000026 -> INERT_AT_PRECISION on the frozen 18-task gate despite the
# trainer's own step-9 25% strict pass). A 2.4e-4 delta can still be
# behaviorally significant; the frozen holdout eval is the ONLY ground truth
# for "beats base". Fix: ONLY provable-inert (zero delta) skips. Everything
# else (inert_at_precision / active / unknown) MUST reach the rubric eval so
# the objective is actually measured.
if [[ "$PRECHECK_VERDICT" == "inert" ]]; then
  say "INERT ${TS} (max_abs_diff=${PRECHECK_MAX_DIFF})"
  log "adapter delta is PROVABLY zero (verdict=${PRECHECK_VERDICT}) — the only case that skips the rubric eval"
  update_state "$STATE_KEY" "inert" "adapter_delta_zero" "" "$ADAPTER" "$PRECHECK_MAX_DIFF" "{\"precheck_phase\": \"${PRECHECK_PHASE}\", \"verdict\": \"${PRECHECK_VERDICT}\"}"
  exit 0
fi
if [[ "$PRECHECK_VERDICT" == "inert_at_precision" ]]; then
  say "INERT_AT_PRECISION_NOTE ${TS} (max_abs_diff=${PRECHECK_MAX_DIFF} below bf16 ULP at largest weight) — RUNNING holdout eval anyway (nonzero delta may be behaviorally significant)"
  log "nonzero-but-sub-ULP delta; proceeding to the frozen holdout eval (ground truth)"
fi
if [[ "$PRECHECK_VERDICT" == "unknown" ]]; then
  log "precheck inconclusive — running the rubric eval anyway (conservative)"
fi

# ---- step 4: rubric eval on NPUs (hours) ----
# C-0036: take the asi2-eval box lease BEFORE the dispatch decision -- the
# per-ts pid checks only catch re-entry for the SAME checkpoint, so without
# the lease, launchers carrying different checkpoints double-fire 18-task
# NPU legs at ASI2. A busy lease = another dispatcher is mid-leg: skip this
# cycle (the watchdog retries) rather than queue a second NPU leg.
if ! asi2_eval_lock_acquire; then
  say "EVAL_LOCK_BUSY ${TS}"
  log "asi2-eval lease held elsewhere (${EVAL_LOCK_FILE}) -- skipping this cycle"
  exit 0
fi
# the lease must never outlive this shell: release on every exit path below
trap 'asi2_eval_lock_release; rm -rf "${PRECHECK_LOCAL_DIR-}"' EXIT

# ---- freeze-integrity sha gate (C-0048, finishing bounced C-0028) ----
# Refuse BEFORE firing the leg: a drifted holdout/scorer must burn zero box
# budget, not a serialized NPU leg plus a poll window (the box-side driver
# check runs only after dispatch). The EXIT trap above releases the lease on
# this path.
if ! asi2_eval_freeze_gate; then
  say "FREEZE_GATE_REFUSED ${TS}"
  exit 1
fi

if ! PIDSTATE=$(exec_remote "if [ -f /tmp/reeval_${TS}.pid ] && kill -0 \$(cat /tmp/reeval_${TS}.pid) 2>/dev/null; then echo RUNNING; else echo NOT_RUNNING; fi"); then
  printf '%s\n' "${PIDSTATE:-AUTH_DOWN}"
  exit 2
fi
if [[ "$PIDSTATE" == *RUNNING* && "$PIDSTATE" != *NOT_RUNNING* ]]; then
  say "EVAL_RUNNING ${TS}"
  update_state "$STATE_KEY" "pending" "eval-running" "" "$ADAPTER" "$PRECHECK_MAX_DIFF"
  exit 0
fi
exec_remote "rm -f /tmp/reeval_${TS}.pid /tmp/reeval_${TS}.log" >/dev/null 2>&1 || true

EVAL_CMD="cd ${REMOTE_ROOT}; nohup python3 scripts/run_asi2_base_adapter_rubric_eval.py --base-model '${BASE_MODEL}' --adapter '${ADAPTER}' --output 'outputs/reeval_latest_${TS}.json' --benchmark '${EVAL_BENCHMARK_BOX}' --device npu --max-new-tokens 384 --limit 0 > /tmp/reeval_${TS}.log 2>&1 & echo \$! > /tmp/reeval_${TS}.pid; echo EVAL_PID=\$(cat /tmp/reeval_${TS}.pid)"
log "launching rubric eval: ${EVAL_CMD}"
LAUNCH_OUT=""
if ! LAUNCH_OUT=$(exec_remote "$EVAL_CMD"); then
  printf '%s\n' "${LAUNCH_OUT:-AUTH_DOWN}"
  exit 2
fi
if ! PIDSTATE=$(exec_remote "test -f /tmp/reeval_${TS}.pid && echo PID_OK || echo PID_MISSING"); then
  printf '%s\n' "${PIDSTATE:-AUTH_DOWN}"
  exit 2
fi
if [[ "$PIDSTATE" != *PID_OK* ]]; then
  log "rubric eval launch failed (no pid file) — see /tmp/reeval_${TS}.log on the box"
  say "EVAL_LAUNCH_FAILED ${TS}"
  exit 1
fi
log "rubric eval launched (pid=$(printf '%s' "$LAUNCH_OUT" | grep -o 'EVAL_PID=[0-9]*' | head -1 | cut -d= -f2 || true)); polling up to ${EVAL_WAIT_SECONDS}s"
update_state "$STATE_KEY" "pending" "eval-running" "" "$ADAPTER" "$PRECHECK_MAX_DIFF"

# dispatch complete (box pid confirmed, state recorded): the lease covers the
# DISPATCH window, not the multi-hour leg -- the holder is this short-lived
# shell, and the box-side /tmp/reeval_<ts>.pid check + EVAL_RUNNING keyword
# guard the leg itself. Release so the next dispatcher can fire its leg.
asi2_eval_lock_release
log "asi2-eval lease released after dispatch"

if ! poll_for_file "${REMOTE_ROOT}/outputs/reeval_latest_${TS}.json" "$EVAL_WAIT_SECONDS" "$EVAL_POLL_INTERVAL" "rubric-eval"; then
  say "EVAL_PENDING ${TS}"
  log "rubric eval still running after ${EVAL_WAIT_SECONDS}s — will resume next cycle"
  exit 0
fi

# ---- step 5: parse the verdict and record the result ----
SUMMARY_JSON=""
if ! SUMMARY_JSON=$(exec_remote "cd ${REMOTE_ROOT} && python3 -c \"import json;d=json.load(open('outputs/reeval_latest_${TS}.json'));s=d['summary'];print(json.dumps({'pass_at_1':{'base':s['base']['pass_at_1'],'adapter':s['adapter']['pass_at_1']},'rubric_overall':{'base':s['base']['scores']['overall'],'adapter':s['adapter']['scores']['overall']},'heldout_ce_loss':{'base':d['heldout_sft_eval']['base']['loss'],'adapter':d['heldout_sft_eval']['adapter']['loss']},'duration_sec':d['duration_sec']}))\""); then
  printf '%s\n' "${SUMMARY_JSON:-AUTH_DOWN}"
  exit 2
fi
SUMMARY_JSON=$(printf '%s' "$SUMMARY_JSON" | tr -d '[:space:]')
if [[ -z "$SUMMARY_JSON" ]] || ! printf '%s' "$SUMMARY_JSON" | python3 -c 'import json, sys; json.load(sys.stdin)' >/dev/null 2>&1; then
  say "EVAL_OUTPUT_INVALID ${TS}"
  update_state "$STATE_KEY" "error" "eval-output-unparseable" "${REMOTE_ROOT}/outputs/reeval_latest_${TS}.json" "$ADAPTER" "$PRECHECK_MAX_DIFF"
  exit 1
fi

B_PASS="" A_PASS="" B_RUB="" A_RUB="" B_CE="" A_CE="" DUR=""
read -r B_PASS A_PASS B_RUB A_RUB B_CE A_CE DUR < <(printf '%s' "$SUMMARY_JSON" | python3 -c '
import json, sys
d = json.load(sys.stdin)
p, r = d["pass_at_1"], d["rubric_overall"]
c = d["heldout_ce_loss"]
print(p["base"], p["adapter"], r["base"], r["adapter"], c["base"], c["adapter"], d["duration_sec"])
') || true

VVERDICT="adapter==base (noop)"
if [[ -n "$B_PASS" && -n "$A_PASS" && ( "$B_PASS" != "$A_PASS" || "$B_RUB" != "$A_RUB" ) ]]; then
  VVERDICT="adapter differs from base"
fi
say "VERDICT ${TS}"
say "  pass@1:          base ${B_PASS} | adapter ${A_PASS}"
say "  rubric overall:  base ${B_RUB} | adapter ${A_RUB}"
say "  heldout CE loss: base ${B_CE} | adapter ${A_CE}"
say "  duration_sec:    ${DUR}"
say "  max_abs_diff (precheck): ${PRECHECK_MAX_DIFF}"
say "  => ${VVERDICT}"
say "EVAL_DONE ${TS} ${VVERDICT}"
update_state "$STATE_KEY" "done" "$VVERDICT" "${REMOTE_ROOT}/outputs/reeval_latest_${TS}.json" "$ADAPTER" "$PRECHECK_MAX_DIFF" "$SUMMARY_JSON"
log "state updated in ${EVAL_STATE_FILE}"
exit 0
