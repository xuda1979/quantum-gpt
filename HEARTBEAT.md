# HEARTBEAT.md

- Continue the quantum coding LLM R&D project in this workspace.
- Read PROJECT.md first, then inspect recent memory notes before acting.
- Prefer one concrete improvement per cycle: research note, code change, dataset artifact, eval artifact, remote-run preparation, or backlog refinement.
- Use local CPU only when designing experiments and infrastructure.
- Optimize for a fine-tuning path centered on the smallest practical Qwen 3.5 model.
- Keep software-engineering capability as a first-class goal, not a side effect.
- Before any Huanxin training action, run `python3 evals/runner/run_eval.py` and any other relevant local tests for changed files; only proceed if all local checks pass.
- The remote target is the Huanxin train-dev environment for project `3ed7854b946a47b1a49ad754baa76cd3`, with code moved from this machine into `/root/root/work/quantum-gpt` by direct copy/paste or equivalent browser-side editing actions.
- When automating remote edits, prefer browser-side click/paste actions through the local persistent Playwright profile in `browser-automation/`.
- Do not use S3 staging for now.
- If Huanxin auth or the remote editing surface is unavailable, record the exact blocker and the smallest next unblocker instead of claiming remote progress.
- After each cycle, write a concise summary and next step to memory/YYYY-MM-DD.md.
- If nothing useful can be advanced, document the blocker and reply HEARTBEAT_OK.
