#!/bin/bash
# C-10605 leg2 monitor: poll box every 10 min until envelope written or 5h timeout.
# Usage: bash .c10605_work/c10605_leg2_watch.sh
LOG=/private/tmp/future-501/-Users-daxu-software-quantum-gpt/b6dc6e69-8ecd-4300-9181-27002c3441d0/tasks
OUT="/root/work/quantum-gpt/outputs/eval_leg2_c10605_v22resume_1941"
DEADLINE=$(( $(date +%s) + 18000 ))  # 5h

while [ $(date +%s) -lt $DEADLINE ]; do
  python3 - <<'EOF'
import json, urllib.request, time, re

PORTS = [20646, 19004, 20653]
def exec_any(cmd, timeout=120, total_wait=240):
    last = None
    deadline = time.time() + total_wait
    while time.time() < deadline:
        for port in PORTS:
            try:
                req = urllib.request.Request('http://127.0.0.1:%d/exec' % port, data=json.dumps({'command': cmd, 'waitMs': 60000}).encode(), headers={'Content-Type': 'application/json'})
                d = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
                if d.get('ok') is True and d.get('commandOk') is True:
                    return d['output']
                last = 'ok=%s' % d.get('ok')
            except Exception as e:
                last = type(e).__name__
        time.sleep(10)
    raise RuntimeError('no daemon: %s' % last)

LOG = '/root/work/quantum-gpt/outputs/eval_leg2_c10605_v22resume_1941/leg2_step-1941-c10605-v22resume-leg2.log'
ENV = '/root/work/quantum-gpt/outputs/eval_leg2_c10605_v22resume_1941/holdout_leg2_step-1941-c10605-v22resume-leg2.json'
try:
    out = exec_any(
        'grep -c \'"stage": "generate"\' ' + LOG + ' 2>/dev/null; '
        'grep \'"stage": "generate"\' ' + LOG + ' 2>/dev/null | tail -1; '
        'ls ' + ENV + ' 2>/dev/null && echo ENVELOPE_PRESENT || echo ENVELOPE_ABSENT; '
        'tail -c 400 ' + LOG + ' 2>/dev/null | tail -3'
    )
    print('[leg2-watch %s] %s' % (time.strftime('%H:%M:%SZ', time.gmtime()), out.replace('\n', ' | ')))
    if 'ENVELOPE_PRESENT' in out:
        print('LEG2_COMPLETE')
except Exception as e:
    print('[leg2-watch] probe failed: %s' % e)
EOF
  if [ $? -eq 0 ] && python3 -c "
import json, urllib.request, time, re, sys
PORTS = [20646, 19004, 20653]
def exec_any(cmd, timeout=60, total_wait=60):
    for port in PORTS:
        try:
            req = urllib.request.Request('http://127.0.0.1:%d/exec' % port, data=json.dumps({'command': cmd, 'waitMs': 30000}).encode(), headers={'Content-Type': 'application/json'})
            d = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
            if d.get('ok') is True and d.get('commandOk') is True:
                return d['output']
        except Exception:
            continue
    return ''
env = exec_any('ls /root/work/quantum-gpt/outputs/eval_leg2_c10605_v22resume_1941/holdout_leg2_step-1941-c10605-v22resume-leg2.json 2>/dev/null && echo YES || echo NO')
sys.exit(0 if 'YES' in env else 1)
"; then
    echo 'LEG2 ENVELOPE WRITTEN - DONE'
    exit 0
  fi
  sleep 600
done
echo 'LEG2 WATCH TIMEOUT after 5h'
exit 1
