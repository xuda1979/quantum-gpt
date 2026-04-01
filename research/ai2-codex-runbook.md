# ai2 Codex Runbook

This file documents the verified way to use Codex on `ai2` against the finetuned OmniCoder model served from the remote workspace.

Remote workspace:

- `/root/root/work/quantum-gpt`

Fresh verified on:

- `2026-04-01`

Verified model alias:

- `quantum-gpt-omnicoder9b.1`

Verified backing model path:

- `/root/root/work/quantum-gpt/models/OmniCoder-9B`

Verified backing adapter path:

- `/root/root/work/quantum-gpt/outputs/interface-prefix-omnicoder9b-semantic-v4-2npu-true20-20260329T2219CST/adapter`

Verified Codex version:

- `codex-cli 0.117.0`

## Quick Start

If the ai2 local model server is already running, the shortest usable pattern on ai2 is:

```bash
cd /root/root/work/quantum-gpt
export LOCAL_CODEX_API_KEY=dummy
/root/.local/bin/codex exec --skip-git-repo-check --color never -C /root/root/work/quantum-gpt -p local -m quantum-gpt-omnicoder9b.1 'Reply with exactly OK and nothing else.'
```

The key part is the profile/model selection:

```bash
codex -p local -m quantum-gpt-omnicoder9b.1
```

Fresh validated behavior:

- the `local` profile resolves to provider `quantum_local`
- the selected model is `quantum-gpt-omnicoder9b.1`
- a dedicated `codex exec -p local -m quantum-gpt-omnicoder9b.1 ...` smoke on `2026-04-01` returned `PROFILE_OK`

## Required Remote Config

Codex reads:

- `/root/.codex/config.toml`

The verified config is rendered with:

```bash
python3 scripts/render_codex_local_config.py \
  --model-name quantum-gpt-omnicoder9b.1 \
  --base-url http://127.0.0.1:8000/v1 \
  --env-key LOCAL_CODEX_API_KEY \
  --wire-api responses \
  --supports-websockets false \
  > /root/.codex/config.toml
```

Important:

- `wire_api` must be `responses`
- `LOCAL_CODEX_API_KEY` can be any dummy value for this local provider path

## Start The Local Model Server

If `http://127.0.0.1:8000/health` is not healthy, start the verified local adapter server on ai2:

```bash
cd /root/root/work/quantum-gpt
export NO_PROXY=127.0.0.1,localhost
export no_proxy=127.0.0.1,localhost
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY
nohup env \
  PYTHONUNBUFFERED=1 \
  PYTHONPYCACHEPREFIX=/tmp/pycache \
  ASCEND_RT_VISIBLE_DEVICES=6 \
  python3 scripts/serve_openai_chat_adapter.py \
    --base-model /root/root/work/quantum-gpt/models/OmniCoder-9B \
    --adapter /root/root/work/quantum-gpt/outputs/interface-prefix-omnicoder9b-semantic-v4-2npu-true20-20260329T2219CST/adapter \
    --model-name quantum-gpt-omnicoder9b.1 \
    --device npu \
    --host 127.0.0.1 \
    --port 8000 \
  > /tmp/quantum_codex_server.log 2>&1 &
```

Health check:

```bash
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
  NO_PROXY=127.0.0.1,localhost \
  curl --noproxy '*' -fsS http://127.0.0.1:8000/health
```

Fresh verified healthy response:

```json
{"ok": true, "model": "quantum-gpt-omnicoder9b.1"}
```

## Install Codex If Missing

If ai2 does not have Codex installed:

```bash
cd /root/root/work/quantum-gpt
bash scripts/install_codex_standalone.sh
```

Verify:

```bash
/root/.local/bin/codex --version
```

Fresh verified output:

```text
codex-cli 0.117.0
```

## Fresh Smoke Test

The exact smoke test that succeeded on `2026-04-01` was:

```bash
cd /root/root/work/quantum-gpt
export LOCAL_CODEX_API_KEY=dummy
rm -f /tmp/codex_last.txt
/root/.local/bin/codex exec \
  --skip-git-repo-check \
  --color never \
  -C /root/root/work/quantum-gpt \
  -p local \
  -m quantum-gpt-omnicoder9b.1 \
  -o /tmp/codex_last.txt \
  'Reply with exactly OK and nothing else.'
cat /tmp/codex_last.txt
```

Fresh verified output:

```text
OK
```

Additional profile/model-selection smoke verified on `2026-04-01`:

```bash
cd /root/root/work/quantum-gpt
export LOCAL_CODEX_API_KEY=dummy
/root/.local/bin/codex exec \
  --skip-git-repo-check \
  --color never \
  -C /root/root/work/quantum-gpt \
  -p local \
  -m quantum-gpt-omnicoder9b.1 \
  -o /tmp/codex_profile_model_check.txt \
  'Reply with exactly PROFILE_OK and nothing else.'
cat /tmp/codex_profile_model_check.txt
```

Fresh verified output:

```text
PROFILE_OK
```

## Local Launch From This Mac

When launching from the local repo on this Mac, the most direct end-to-end helper is:

```bash
bash scripts/ai2_codex_local_exec.sh --prompt "Reply with exactly OK and nothing else."
```

What it does:

- ensures Codex helper scripts are staged
- refreshes `/root/.codex/config.toml`
- starts the local model server if needed
- runs Codex on ai2 against `quantum-gpt-omnicoder9b.1`

## Reliable Control Plane

For simple ai2 control-plane commands, the usual wrapper is:

```bash
./scripts/ai2_shell.sh "<command>"
```

For Codex restore/smoke operations, the more reliable path at the moment is direct shell execution:

```bash
node browser-automation/huanxin_shell_exec.js ai2 --skip-daemon --wait-ms 180000 --command "<command>"
```

Reason:

- the wrapper `scripts/ai2_shell.sh` can still fail on stale marker detection even when the underlying ai2 shell is healthy
- direct `huanxin_shell_exec.js` bypasses that wrapper check

## Working Defaults

Use these defaults unless there is a concrete reason to change them:

- profile: `local`
- model alias: `quantum-gpt-omnicoder9b.1`
- base URL: `http://127.0.0.1:8000/v1`
- env key: `LOCAL_CODEX_API_KEY`
- wire API: `responses`
- websockets: `false`

## Source Files

The relevant local helper files are:

- [ai2_codex_local_exec.sh](/Users/daxu/software/quantum-gpt/scripts/ai2_codex_local_exec.sh)
- [install_codex_standalone.sh](/Users/daxu/software/quantum-gpt/scripts/install_codex_standalone.sh)
- [render_codex_local_config.py](/Users/daxu/software/quantum-gpt/scripts/render_codex_local_config.py)
- [serve_openai_chat_adapter.py](/Users/daxu/software/quantum-gpt/scripts/serve_openai_chat_adapter.py)
