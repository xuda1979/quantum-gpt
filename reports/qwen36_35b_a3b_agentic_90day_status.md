# Qwen3.6 35B A3B Agentic 90-Day Status

Date: 2026-05-25

Current phase: foundation.

Latest verified local commands:

```bash
for f in scripts/launch_huanxin_agentic_grpo.sh scripts/launch_qwen36_35b_a3b_agentic_grpo_ai3.sh scripts/launch_qwen36_35b_a3b_agentic_grpo_asi1.sh scripts/huanxin_env_shell.sh scripts/huanxin_training_job.sh scripts/show_huanxin_agentic_grpo_status.sh; do bash -n "$f" || exit 1; done
python3 -m py_compile training/agentic_grpo_trainer.py training/agent_trajectory_rollout.py scripts/validate_agentic_grpo_run_artifacts.py
python3 -m pytest tests/test_huanxin_agentic_launcher.py tests/test_huanxin_daemon_state.py tests/test_launch_qwen36_35b_a3b_agentic_grpo_asi1.py
```

Latest result:

- The generic Huanxin agentic launcher now accepts `--model-name` and `--benchmark-file`.
- The new ASI1 fast launcher renders `/root/work/filestorage/Qwen3.6-35B-A3B-W8A8` and trims the rollout budget to a launchable first run.
- Configs and research contracts now cover SFT, DPO, GRPO/RLVR, private eval, model presence, and task taxonomy.
- Targeted tests passed: `python3 -m pytest tests/test_huanxin_agentic_launcher.py tests/test_agent_trajectory_rollout.py tests/test_agentic_grpo_trainer.py tests/test_validate_agentic_grpo_run_artifacts.py tests/test_launch_qwen36_35b_a3b_agentic_grpo_asi1.py` reported 18 passed.
- `scripts/huanxin_status.sh ASI1` now accepts literal `ASI1` instead of rejecting it as unsupported.
- `scripts/huanxin_shell.sh` and `scripts/huanxin_status.sh` now map `ASI1` to the exact environment URL `#/train-dev/environment/dl-9a5a098accce31c28cf4c6ca23391341?name=ASI1`.
- `browser-automation/huanxin_shell_exec.js` now records the fixed ASI1 daemon port `20646`.
- `scripts/submit_asi1_preflight_task.sh` now provides a repeatable no-shell ASI1 preflight path through Huanxin task submission. It defaults to fill-only/no-submit, and only submits with explicit `--submit`.
- `browser-automation/huanxin_submit_task_run.js` now rejects route false positives where the environment id matches but the hash-route `name=` does not. This prevented an `AI` page from being accepted as `ASI1`.
- `browser-automation/huanxin_task_status_probe.js` and `scripts/probe_asi1_task_status.sh` now poll Huanxin task-list state without using the broken Shell terminal.

Latest verified local validation:

```bash
bash -n scripts/probe_asi1_task_status.sh scripts/submit_asi1_preflight_task.sh
node -c browser-automation/huanxin_task_status_probe.js browser-automation/huanxin_submit_task_run.js
python3 -m pytest tests/test_probe_asi1_task_status.py tests/test_huanxin_submit_task_route.py tests/test_submit_asi1_preflight_task.py tests/test_huanxin_agentic_launcher.py tests/test_huanxin_daemon_state.py
```

Result: 11 tests passed.

Current blocker before remote launch:

- The exact ASI1 preflight is now green: shell access works, model path exists, trainer exists, benchmark exists. The remaining missing piece is `peft` and `accelerate` in the ASI1 runtime if you want the actual training launch to proceed cleanly.
- The new fast launcher is ready to use, but I have not started a real training job yet because the next safe step is still dependency installation or a follow-up preflight that proves those imports are available.
