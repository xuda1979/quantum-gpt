# Huanxin Remote Fine-Tuning Runbook

## Purpose

This runbook narrows the Huanxin path to a small, repeatable sequence:

1. validate locally
2. probe whether the persisted browser session is still authenticated
3. only if the remote surface is usable, paste the minimum validated code and commands into `/root/root/work/quantum-gpt`
4. continue remote fine-tuning there

The goal is to avoid fake progress. If auth or the edit surface is broken, stop and record the blocker.

## Local gate

Before any remote transfer or training action:

```bash
python3 evals/runner/run_eval.py
# plus any additional tests for files changed in this cycle
```

Do not touch the remote environment unless these checks pass.

## Auth / surface probe

Use the persisted Playwright profile first:

```bash
cd browser-automation
node huanxin_probe.js
```

If the live profile is locked or a visible browser is already using it, prefer an isolated clone instead of guessing:

```bash
HUANXIN_PROFILE_COPY_NAME=probe node browser-automation/huanxin_probe.js
```

Artifacts produced:

- `browser-automation/huanxin-probe.png`
- `browser-automation/huanxin-probe.html`
- `browser-automation/huanxin-probe.json`
- JSON stdout with final URL, title, page-text preview, a coarse state classification, and a surface summary listing likely editor/terminal targets when present

Expected states:

- `login_required`  blocker; auth is not reusable
- `train_surface_or_project_page`  likely usable, but still verify editor/terminal controls before pasting code
- `unknown`  inspect screenshot/HTML and document the exact mismatch

For manual debugging in the saved profile:

```bash
cd browser-automation
node open_persistent.js 'https://aihuanxin.cn/kunlun/kl-web?poolId=1&projectId=3ed7854b946a47b1a49ad754baa76cd3#/train-dev'
```

## Remote handoff rules

Once the probe confirms an authenticated usable surface:

1. open or create `/root/root/work/quantum-gpt`
2. paste only the files changed and validated locally
3. paste only the minimum commands needed to recreate the next remote step
4. rerun the remote command sequence there
5. capture logs or screenshots proving the step actually happened

## Preferred paste seam

For direct text injection after focusing the target input/editor:

```bash
cd browser-automation
node huanxin_mouse_paste.js 'https://aihuanxin.cn/kunlun/kl-web?poolId=1&projectId=3ed7854b946a47b1a49ad754baa76cd3#/train-dev' \
  --click-text '<visible target text>' \
  --paste-file <local-file> \
  --replace
```

This helper is intentionally simple. It assumes:

- the saved browser profile is authenticated
- a stable clickable text target exists
- the focused surface accepts normal keyboard paste/input

## Minimal remote bootstrap commands

These are the kind of commands to paste once the remote shell/editor is confirmed usable:

```bash
mkdir -p /root/root/work/quantum-gpt
cd /root/root/work/quantum-gpt
```

Then add only the validated files and the smallest next training/eval command set.

## Local bootstrap packager

Use the local packager to freeze exactly which validated files are allowed to move:

```bash
python3 scripts/prepare_huanxin_bootstrap.py \
  research/huanxin-remote-runbook.md \
  research/huanxin-remote-env-manifest.md \
  data/seed/train-chat.jsonl \
  data/seed/splits-auto-seed/train.jsonl \
  data/seed/splits-auto-seed/val.jsonl \
  evals/runner/run_eval.py \
  --label seed-bootstrap
```

This produces a timestamped bundle under `artifacts/huanxin-bootstrap/` with:

- `manifest.json` — exact file list, sizes, and SHA-256 hashes
- `REMOTE_COMMANDS.sh` — the minimum remote directory/setup commands
- copied validated files preserving workspace-relative paths

That gives the Huanxin step an audit trail and a paste-ready file set without relying on S3 staging.

To turn that audited bundle into a concrete remote execution sheet with paste stubs plus install/smoke commands:

```bash
python3 scripts/render_huanxin_bootstrap_commands.py \
  artifacts/huanxin-bootstrap/<timestamp>
```

This emits `REMOTE_BOOTSTRAP_COMMANDS.sh` inside the bundle so the next authenticated Huanxin session has one exact command sheet instead of relying on prose notes.

## Failure policy

If the probe lands on login, an unexpected redirect, or a non-editable surface:

- do not claim remote progress
- save the probe artifacts
- update `research/remote-transfer-blocker.md`
- log the blocker and next unblocker in `memory/YYYY-MM-DD.md`

## Smallest next unblockers

- refresh the persisted Huanxin login in the local profile
- identify one stable visible text target for the remote editor/terminal
- prove one no-op paste into the remote shell before attempting project code transfer
