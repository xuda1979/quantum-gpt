from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _node_eval(source: str) -> dict:
    result = subprocess.run(
        ["node", "-e", source],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_submit_task_route_match_requires_hash_name_match() -> None:
    source = r"""
const {
  getHashSearchParam,
  isOnTargetAppRoute,
} = require('./browser-automation/huanxin_repair_profile_via_safari_sso.js');
const base = 'https://aihuanxin.cn/kunlun/kl-web?poolId=6&projectId=x#/train-dev/environment/dl-9a5a098accce31c28cf4c6ca23391341';
const target = `${base}?name=ASI1`;
const same = `${base}?name=ASI1&state=abc`;
const wrong = `${base}?name=AI&state=abc`;
console.log(JSON.stringify({
  targetName: getHashSearchParam(target, 'name'),
  same: isOnTargetAppRoute(same, target),
  wrong: isOnTargetAppRoute(wrong, target),
}));
"""
    payload = _node_eval(source)

    assert payload == {
        "targetName": "ASI1",
        "same": True,
        "wrong": False,
    }


def test_submit_task_route_exports_still_delegate_to_shared_matcher() -> None:
    source = r"""
const repair = require('./browser-automation/huanxin_repair_profile_via_safari_sso.js');
const submit = require('./browser-automation/huanxin_submit_task_run.js');
const base = 'https://aihuanxin.cn/kunlun/kl-web?poolId=6&projectId=x#/train-dev/environment/dl-9a5a098accce31c28cf4c6ca23391341';
const target = `${base}?name=ASI1`;
const same = `${base}?name=ASI1&state=abc`;
const wrong = `${base}?name=AI&state=abc`;
console.log(JSON.stringify({
  sharedSame: repair.isOnTargetAppRoute(same, target),
  submitSame: submit.isOnTargetAppRoute(same, target),
  sharedWrong: repair.isOnTargetAppRoute(wrong, target),
  submitWrong: submit.isOnTargetAppRoute(wrong, target),
}));
"""
    payload = _node_eval(source)

    assert payload == {
        "sharedSame": True,
        "submitSame": True,
        "sharedWrong": False,
        "submitWrong": False,
    }


def test_submit_task_launch_spec_allows_large_payloads() -> None:
    source = r"""
const {
  deriveLaunchSpec,
} = require('./browser-automation/huanxin_submit_task_run.js');
const spec = deriveLaunchSpec({
  launcherScript: 'scripts/submit_asi1_embedded_wheelhouse_task.sh',
  launcherArgs: ['__launch-spec'],
  outputDir: '',
  logPath: '',
  remoteRoot: '/root/work/quantum-gpt',
});
console.log(JSON.stringify({
  root: spec.remote_root,
  large: spec.executionCommand.length > 900000,
  marker: spec.executionCommand.includes('__ASI1_EMBEDDED_WHEELHOUSE_DONE__'),
}));
"""
    payload = _node_eval(source)

    assert payload == {
        "root": "/root/work/quantum-gpt",
        "large": True,
        "marker": True,
    }


def test_execution_command_probe_uses_short_prefix_for_large_payloads() -> None:
    source = r"""
const {
  executionCommandProbe,
} = require('./browser-automation/huanxin_submit_task_run.js');
const small = 'python3 -c pass && bash /tmp/run.sh';
const large = 'python3 -c ' + 'x'.repeat(1200) + ' && bash /tmp/run.sh';
console.log(JSON.stringify({
  small,
  smallProbe: executionCommandProbe(small),
  largeProbeLength: executionCommandProbe(large).length,
  largeProbePrefix: executionCommandProbe(large).startsWith('python3 -c '),
}));
"""
    payload = _node_eval(source)

    assert payload == {
        "small": "python3 -c pass && bash /tmp/run.sh",
        "smallProbe": "python3 -c pass && bash /tmp/run.sh",
        "largeProbeLength": 96,
        "largeProbePrefix": True,
    }


def test_large_execution_command_uses_code_contents_override() -> None:
    source = r"""
const {
  shouldAutoOverrideCodeContents,
} = require('./browser-automation/huanxin_submit_task_run.js');
console.log(JSON.stringify({
  small: shouldAutoOverrideCodeContents('x'.repeat(1000), ''),
  large: shouldAutoOverrideCodeContents('x'.repeat(10001), ''),
  singleLineRunner: shouldAutoOverrideCodeContents('x'.repeat(1000), '', {single_line_execution: true}),
  explicitOverrideFile: shouldAutoOverrideCodeContents('x'.repeat(10001), '/tmp/cmd.sh'),
}));
"""
    payload = _node_eval(source)

    assert payload == {
        "small": False,
        "large": True,
        "singleLineRunner": True,
        "explicitOverrideFile": False,
    }


def test_large_command_override_preserves_requested_resource_config() -> None:
    source = r"""
const {
  applyResourceConfigToCreatePayload,
} = require('./browser-automation/huanxin_submit_task_run.js');
const payload = { count: 1, resourceInfo: { cpu: 20, gpu: 1, mem: 240, gpuType: '昇腾910B' } };
applyResourceConfigToCreatePayload(payload, {
  instanceCount: 1,
  acceleratorCardsPerInstance: 8,
  cpuPerInstance: 160,
  memoryPerInstance: 1920,
});
console.log(JSON.stringify(payload));
"""
    payload = _node_eval(source)

    assert payload == {
        "count": 1,
        "resourceInfo": {
            "cpu": 160,
            "gpu": 8,
            "mem": 1920,
            "gpuType": "昇腾910B",
        },
    }


def test_asi1_can_ignore_project_quota_drawer_text_when_confirmed_available() -> None:
    source = r"""
const {
  classifySubmitBlocker,
} = require('./browser-automation/huanxin_submit_task_run.js');
const messages = [
  '训练任务占用资源不得超出项目空间配额，当前项目空间加速卡剩余/总量为：5 / 50卡',
  '超出项目空间配额',
];
console.log(JSON.stringify({
  defaultBlocker: classifySubmitBlocker(messages, {}),
  ignoredBlocker: classifySubmitBlocker(messages, {ignoreProjectQuotaText: true}),
}));
"""
    payload = _node_eval(source)

    assert payload == {
        "defaultBlocker": "project_quota_exceeded",
        "ignoredBlocker": None,
    }


def test_direct_submit_payload_matches_known_huanxin_create_contract() -> None:
    source = r"""
const {
  buildCreateTaskPayload,
  decodeCommandLineFromTask,
  summarizeCreateTaskPayload,
} = require('./browser-automation/huanxin_submit_task_run.js');
const payload = buildCreateTaskPayload({
  taskName: 'q36-direct-test',
  imageName: 'quantumstim',
  resourceGroup: 'huanxin-all-resource',
  resourceGroupType: '公共资源组',
  priority: '高',
  resourceConfig: {
    instanceCount: 1,
    acceleratorCardsPerInstance: 8,
    cpuPerInstance: 160,
    memoryPerInstance: 1920,
  },
  executionCommand: 'set -euo pipefail\necho hello',
});
console.log(JSON.stringify({
  resGroupId: payload.resGroupId,
  resGroupType: payload.resGroupType,
  imageType: payload.imageType,
  imageId: payload.imageId,
  imageGroupId: payload.imageGroupId,
  priority: payload.priority,
  resourceInfo: payload.resourceInfo,
  firstLine: decodeCommandLineFromTask(payload.codeContents[0]),
  secondLine: decodeCommandLineFromTask(payload.codeContents[1]),
  presetDatasetIds: payload.presetDatasetIds,
  personalDatasetVersionIds: payload.personalDatasetVersionIds,
  summary: summarizeCreateTaskPayload(payload),
}));
"""
    payload = _node_eval(source)

    assert payload == {
        "resGroupId": 154,
        "resGroupType": "public",
        "imageType": "personal",
        "imageId": 6273,
        "imageGroupId": 3458,
        "priority": "high",
        "resourceInfo": {
            "gpuType": "昇腾910B",
            "gpu": 8,
            "cpu": 160,
            "mem": 1920,
        },
        "firstLine": "set -euo pipefail",
        "secondLine": "echo hello",
        "presetDatasetIds": [],
        "personalDatasetVersionIds": [],
        "summary": {
            "name": "q36-direct-test",
            "lines": 2,
            "encodedBytes": 44,
            "firstLine": "set -euo pipefail",
            "imageId": 6273,
            "imageName": "quantumstim",
            "resourceInfo": {
                "gpuType": "昇腾910B",
                "gpu": 8,
                "cpu": 160,
                "mem": 1920,
            },
            "priority": "high",
        },
    }


def test_direct_submit_payload_can_wrap_comma_heavy_training_script() -> None:
    source = r"""
const {
  buildCreateTaskPayload,
  decodeCommandLineFromTask,
  summarizeCreateTaskPayload,
} = require('./browser-automation/huanxin_submit_task_run.js');
const command = "python3 -c 'import pathlib;p=pathlib.Path(\"/tmp/run.b64\");old=p.read_text() if p.exists() else \"\";p.write_text(old+\"AAAA\")'\npython3 -c 'import base64,pathlib;pathlib.Path(\"/tmp/run.sh\").write_bytes(base64.b64decode(pathlib.Path(\"/tmp/run.b64\").read_text()))'\nbash /tmp/run.sh";
const payload = buildCreateTaskPayload({
  taskName: 'q36-direct-test',
  imageName: 'qwen3.5-27B-35B-122B-397B-031626-zx',
  resourceGroup: 'huanxin-all-resource',
  resourceGroupType: '公共资源组',
  priority: '高',
  resourceConfig: {
    instanceCount: 1,
    acceleratorCardsPerInstance: 6,
    cpuPerInstance: 96,
    memoryPerInstance: 1440,
  },
  executionCommand: command,
});
console.log(JSON.stringify({
  lines: payload.codeContents.length,
  firstLine: decodeCommandLineFromTask(payload.codeContents[0]),
  secondLine: decodeCommandLineFromTask(payload.codeContents[1]),
  thirdLine: decodeCommandLineFromTask(payload.codeContents[2]),
  summary: summarizeCreateTaskPayload(payload),
}));
"""
    payload = _node_eval(source)

    assert payload["lines"] == 3
    assert 'p.write_text(old+"AAAA")' in payload["firstLine"]
    assert "base64.b64decode" in payload["secondLine"]
    assert payload["thirdLine"] == "bash /tmp/run.sh"
    assert payload["summary"]["lines"] == 3
    assert payload["summary"]["resourceInfo"] == {
        "gpuType": "昇腾910B",
        "gpu": 6,
        "cpu": 96,
        "mem": 1440,
    }


def test_huanxin_profile_auto_isolates_locked_base_profile(tmp_path: Path) -> None:
    base_profile = tmp_path / "base-profile"
    base_profile.mkdir()
    (base_profile / "SingletonLock").write_text("stale lock", encoding="utf-8")
    source = r"""
const {
  ensureProfileDir,
} = require('./browser-automation/huanxin_profile.js');
const info = ensureProfileDir();
console.log(JSON.stringify({
  isolated: info.isolated,
  autoIsolated: info.autoIsolated,
  baseProfileLocked: info.baseProfileLocked,
  sourceDir: info.sourceDir,
  profileDirIncludes: info.profileDir.includes('huanxin-profile-auto-'),
}));
"""
    result = subprocess.run(
        ["node", "-e", source],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            "PATH": os.environ.get("PATH", ""),
            "HUANXIN_BASE_PROFILE_DIR": str(base_profile),
            "HUANXIN_AUTO_ISOLATE_LOCKED_PROFILE": "1",
        },
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload == {
        "isolated": True,
        "autoIsolated": True,
        "baseProfileLocked": True,
        "sourceDir": str(base_profile),
        "profileDirIncludes": True,
    }


def test_huanxin_sso_bridge_sanitizes_auth_urls() -> None:
    source = r"""
const {
  redactAuthUrl,
  sanitizeBridgeResult,
} = require('./browser-automation/huanxin_repair_profile_via_safari_sso.js');
const authUrl = 'https://aihuanxin.cn/auth/realms/TechnicalMiddlePlatform/protocol/openid-connect/auth?client_id=kunlun-front&redirect_uri=https%3A%2F%2Faihuanxin.cn%2Fkunlun%2Fkl-web&state=secret-state&response_type=code&nonce=secret-nonce';
const callbackUrl = 'https://aihuanxin.cn/kunlun/kl-web?poolId=6#/train-dev/environment/dl-x?name=ASI1&state=secret-state&session_state=secret-session&code=secret-code';
const sanitized = sanitizeBridgeResult({
  ok: false,
  mode: 'missing_callback',
  authUrl,
  finalUrl: callbackUrl,
  safariCapture: {
    callback_url: callbackUrl,
    auth_redirect_url: authUrl,
    visit_url: authUrl,
    final_url: callbackUrl,
    redirect_samples: Array.from({ length: 10 }, (_, index) => ({ t: index, url: index === 9 ? callbackUrl : authUrl, title: 'sample' })),
  },
  trace: [{ label: 'x', url: callbackUrl }],
});
const text = JSON.stringify({ redacted: redactAuthUrl(authUrl), sanitized });
console.log(JSON.stringify({
  noSecretCode: !text.includes('secret-code'),
  noSecretState: !text.includes('secret-state'),
  noSecretNonce: !text.includes('secret-nonce'),
  noSecretSession: !text.includes('secret-session'),
  authRedacted: text.includes('[REDACTED_AUTH_QUERY]'),
  samplesTrimmed: sanitized.safariCapture.redirect_samples.length,
  sampleCount: sanitized.safariCapture.redirect_sample_count,
}));
"""
    payload = _node_eval(source)

    assert payload == {
        "noSecretCode": True,
        "noSecretState": True,
        "noSecretNonce": True,
        "noSecretSession": True,
        "authRedacted": True,
        "samplesTrimmed": 8,
        "sampleCount": 10,
    }


def test_huanxin_sso_bridge_password_fallback_reports_missing_credentials_without_urls() -> None:
    source = r"""
const {
  runPasswordLoginFallback,
} = require('./browser-automation/huanxin_repair_profile_via_safari_sso.js');
runPasswordLoginFallback('https://aihuanxin.cn/kunlun/kl-web?poolId=6#/train-dev/environment/dl-x?name=ASI1&state=secret-state&code=secret-code')
  .then((result) => console.log(JSON.stringify(result)))
  .catch((error) => { console.error(error.stack || error.message); process.exit(1); });
"""
    result = subprocess.run(
        ["node", "-e", source],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            "PATH": os.environ.get("PATH", ""),
            "HUANXIN_LOGIN_PHONE": "",
            "HUANXIN_LOGIN_PASSWORD": "",
        },
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload == {"attempted": False, "reason": "missing_credentials"}
