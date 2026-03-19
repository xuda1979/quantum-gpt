# Remote Huanxin Workflow Note

## Context

A direct remote-edit path is now in scope for the project:

- Huanxin train page: `https://aihuanxin.cn/kunlun/kl-web?poolId=1&projectId=3ed7854b946a47b1a49ad754baa76cd3#/train-dev`
- target remote workdir: `/root/root/work/quantum-gpt`
- transfer mode for now: copy/paste validated code and commands from the local machine into the Huanxin remote environment
- required local validation gate before any remote action: `python3 evals/runner/run_eval.py` plus any additional tests for touched files

Browser automation setup has already progressed enough to support future webpage interaction:

- Playwright installed locally in the workspace
- bundled Chromium installed
- persistent browser profile created and reusable again for authenticated Huanxin navigation
- helper script available for browser-side click/paste actions: `browser-automation/huanxin_mouse_paste.js`

## Confirmed blocker

The remote blocker narrowed again during this cycle.

Current local validation is green:

- `python3 evals/runner/run_eval.py` passes `19/19`
- `python3 -m py_compile scripts/render_huanxin_bootstrap_commands.py training/huanxin_cpu_smoke.py training/qwen_sft_peft.py scripts/prepare_huanxin_bootstrap.py` passes
- `artifacts/huanxin-bootstrap/20260316T143522Z/REMOTE_BOOTSTRAP_COMMANDS.sh` was re-rendered successfully after the latest renderer hardening change

The latest browser check narrowed the issue substantially:

- `node browser-automation/huanxin_probe.js` now returns a readable authenticated train-dev page with `state=train_surface_or_project_page`
- the page body includes the 开发环境 table and no longer looks like an empty SPA shell
- a new helper, `browser-automation/huanxin_env_visibility_probe.js`, confirms that `ai1` and `ai2` are both present and `运行中`
- the earlier `暂无开发环境` diagnosis was not a true remote absence; it was a visibility/probe mistake around page state and filter interpretation

So the blocker is no longer auth, no-env, or empty-page observability. The remaining honest question is narrower: whether `ai2` can still be opened into a usable Shell/VSCode/Jupyter surface from the current machine-local browser context.

## What now exists locally

- a narrow CPU bootstrap requirements file: `training/requirements-huanxin-cpu.txt`
- a remote-first tokenizer/model-load smoke script: `training/huanxin_cpu_smoke.py`
- a minimal PEFT SFT entrypoint: `training/qwen_sft_peft.py`
- audited Huanxin bundle pack/render tooling under `scripts/prepare_huanxin_bootstrap.py` and `scripts/render_huanxin_bootstrap_commands.py`
- a current audited bundle and exact command sheet under `artifacts/huanxin-bootstrap/20260316T143522Z/`

## What is still missing remotely in the current state

- a visible or openable Huanxin development environment row for this project
- a verified terminal/editor surface reachable from the authenticated page
- a verified Huanxin run of the package-install bootstrap sequence from the current project state
- a verified Qwen3.5-1.5B-Instruct tokenizer smoke in Huanxin from the current machine-local auth context
- a verified full model-load smoke in Huanxin from the current machine-local auth context
- any verified 1-step PEFT startup smoke in Huanxin from the current machine-local auth context

## Why this matters

The project can already prove:

- local validation before remote steps
- audited remote bootstrap packaging
- reusable authenticated browser access to the project page

But it still cannot honestly claim:

- remote file paste into `/root/root/work/quantum-gpt` from the current state
- remote bootstrap success from the current project page
- model load success for the target checkpoint
- training-loop startup in Huanxin

So this is now an **environment-availability blocker**, not an auth blocker.

## Smallest next unblocker

Re-verify direct shell reachability from the current browser context before any new remote-transfer claim:

1. use `browser-automation/huanxin_shell_exec.js ai2 --command 'cd /root/root/work/quantum-gpt && pwd && ls'` or an equivalent minimal command
2. if shell opens and returns output, the blocker is cleared and the next honest step is to use the already-rendered audited bundle/command sheet
3. if shell fails to open, document the exact failure mode at the surface-open step instead of regressing to vague page/auth claims

## Decision

Do not guess the remote browser workflow and do not claim remote progress just because login reuse works again.

The correct next step is:

1. keep the local validation gate green
2. recover or create the actual Huanxin development environment on the authenticated page
3. probe again until a real remote surface exists
4. only then paste the validated bootstrap bundle and continue the remote fine-tuning workflow
