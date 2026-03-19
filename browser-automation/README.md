# Browser Automation

This directory contains local Playwright helpers for operating the Huanxin train-dev web UI from the local machine.

## Main scripts

- `huanxin_probe.js` checks whether the saved browser profile is authenticated
- `huanxin_inspect.js` inspects the current train-dev DOM for likely controls and remote surfaces
- `huanxin_open_env.js <envName>` opens a named environment row such as `ai2`
- `huanxin_mouse_paste.js ...` performs browser-side click and paste actions

## Recommended sequence

1. `node browser-automation/huanxin_probe.js`
2. if authenticated, `node browser-automation/huanxin_inspect.js`
3. open the target environment, usually `ai2`
4. perform a minimal validated paste into `/root/root/work/quantum-gpt`

## Concurrent workers

When two workers need the Huanxin browser at the same time, give each one an isolated Chromium profile copy:

- `HUANXIN_PROFILE_COPY_NAME=ai1-worker node browser-automation/huanxin_shell_exec.js ai1 --command 'pwd'`
- `HUANXIN_PROFILE_COPY_NAME=ai2-worker node browser-automation/huanxin_shell_exec.js ai2 --command 'pwd'`

The scripts will clone `browser-automation/profile` into `/tmp/huanxin-profile-<name>` and strip Chromium lock files before launching.

For a single command fan-out to both environments:

- `node browser-automation/huanxin_dual_exec.js --ai1-command 'pwd' --ai2-command 'pwd'`

To copy the same validated payload to both environments before running commands:

- `node browser-automation/huanxin_dual_exec.js --remote-dir /root/work/alphaqubit --source AGENTS.md --source PROJECT.md --ai1-command 'cd /root/work/alphaqubit && pwd' --ai2-command 'cd /root/work/alphaqubit && pwd'`

## Profile note

If the browser profile is already in use by a visible Chromium window, either clone it manually to `/tmp/huanxin-profile-copy` and rerun the helpers with `HUANXIN_PROFILE_DIR=/tmp/huanxin-profile-copy`, or let the helpers clone automatically with a throwaway name:

- `HUANXIN_PROFILE_COPY_NAME=probe node browser-automation/huanxin_probe.js`
- `HUANXIN_PROFILE_COPY_NAME=ai2-worker node browser-automation/huanxin_shell_exec.js ai2 --command 'pwd'`

The automatic copy path uses `browser-automation/huanxin_profile.js` to clone `browser-automation/profile` into `/tmp/huanxin-profile-<name>` while stripping Chromium lock files.
