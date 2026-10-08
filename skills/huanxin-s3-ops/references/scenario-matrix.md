# Huanxin Scenario Matrix

Use this when the normal wrapper flow is failing or ambiguous.

## Scenario 1: Manual Mode Lock Active

Signs:

- `.huanxin_manual_mode` exists
- the human reports page refreshes, reconnects, or lost typed input

Action:

- do not run browser probes, keepalive, repair, shell wrappers, or Huanxin UI automation
- use `bash scripts/huanxin_manual_mode.sh --status`
- if local automation must stop, use `bash scripts/huanxin_manual_mode.sh --kill-local`

## Scenario 2: Automation Disabled

Signs:

- `.huanxin_automation_enabled` is missing
- shell wrappers refuse browser automation before opening a shell

Action:

- do not silently re-enable automation
- only use `bash scripts/huanxin_manual_mode.sh --enable-automation` after the human explicitly wants Codex to control Huanxin again

## Scenario 3: Cold Probe Says `login_required`, But Repair Or Daemon Reaches Train-Dev

Signs:

- a cold persistent-profile probe lands on auth
- the isolated repair flow or daemon still reaches the exact `#/train-dev/environment/...` URL

Action:

- prefer the exact wrapper/repair result over the stale cold probe
- record both facts clearly
- only call auth a blocker when the real wrapper path also fails to reach the exact train-dev surface

## Scenario 4: Daemon Is `booting`, `busy=true`, Or IPC Requests Are Stuck

Signs:

- daemon `/health` shows `startupState=booting`
- `busy=true`
- `pendingRequestCount > 0`
- stale `.processing.json` files remain under `/tmp/huanxin-daemon-<env>.ipc`

Action:

- do not pile on more wrapper requests first
- inspect `/tmp/huanxin-daemon-<env>.log`, daemon `/health`, and the IPC directory
- distinguish local queueing from remote shell failure before restarting anything

## Scenario 5: Shell Endpoint Provisioning Fails On The Platform Side

Signs:

- `getShellVisitUrl` returns a failure such as `code=170022`
- the UI or console falls through to `wss://.../kunlun/null`
- websocket connect then fails with `404`

Action:

- classify the daemon terminal endpoint as a Huanxin backend shell-endpoint failure, not a normal local retry case
- capture the request/response payload and concise blocker artifact
- try only the project wrapper's documented fallback path, if one exists and is safe for the current manual-mode/session rules
- if fallback command execution returns fresh marker output, report the state as "command channel connected; daemon shell endpoint degraded"
- stop looping blind reconnects once this failure shape is confirmed and no fresh command output is available

## Scenario 5B: Environment Opens But Connection State Is Ambiguous

Signs:

- the train-dev page opens and shows the requested environment
- `Jupyter`, `VSCode`, or `Shell` buttons are visible
- no fresh command output or wrapper run marker has been observed yet

Action:

- report `opened/authenticated`, not `connected`
- run the generic shell wrapper with a tiny marker command such as `printf '__HX_CONNECTED__\n'; pwd; whoami`
- use the wrapper output and its local connection-status artifact as the authority for command-channel health
- keep daemon endpoint failures visible as degraded infrastructure even when fallback command execution succeeds

## Scenario 6: S3 Endpoint Is Not A Real S3 API

Signs:

- `rclone` receives HTML instead of XML
- `PutObject` returns `405 Method Not Allowed`
- bucket listing or upload only works as a web app page, not as object storage

Action:

- stop broad uploads
- keep the probe artifact
- ask for or discover the real S3 API endpoint or bucket mapping before retrying

## Scenario 7: Training Launch Gate

Before launch, verify all of:

- local code/tests/launcher validation passed
- exact target env login is verified
- remote project root exists
- code, data, and model paths exist remotely
- dependency probe is acceptable
- checkpointing is durable enough for resume or scale-up
- training emits live eval / monitoring signals to catch regressions

For this workspace, the minimum preferred pattern is hourly checkpoints plus live status/eval artifacts.

## Scenario 8: Remote Shell Is Still Blocked

Action:

- keep making local progress on trainer, launchers, monitors, evals, and transfer packaging
- prepare the smallest validated S3 payload needed for the next remote attempt
- document the exact failed shell/auth/API step and the exact command or artifact that proves it
- do not claim the remote step succeeded until a real shell or fetched artifact proves it
