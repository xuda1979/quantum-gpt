from __future__ import annotations

import json
from pathlib import Path

from scripts.probe_ai3_shell_endpoint import summarize_probe_artifacts

ROOT = Path(__file__).resolve().parents[1]


def test_probe_summary_extracts_ai3_shell_endpoint_failure_from_repo_artifacts() -> None:
    summary = summarize_probe_artifacts(
        [
            ROOT / "artifacts" / "ai3-shell-request-payload.json",
            ROOT / "artifacts" / "ai3-shell-network-probe.json",
        ]
    )

    assert summary["env_id"] == "dl-c72bd81a96e33134bbe0ae4a478fbab0"
    assert summary["pod_name"] == "dl-c72bd81a96e33134bbe0ae4a478fbab0-r0-818213d4ceb0-0"
    assert summary["requested_shell_type"] == "terminal"
    assert summary["shell_endpoint_failure"] is True
    assert summary["websocket_null_fallback"] is True
    assert any("wss://aihuanxin.cn/kunlun/null" in item for item in summary["websocket_null_urls"])
    assert "getShellVisitUrl returned code=170022" in summary["blocker_summary"]


def test_probe_summary_handles_minimal_synthetic_failure(tmp_path: Path) -> None:
    artifact = tmp_path / "probe.json"
    artifact.write_text(
        json.dumps(
            {
                "responses": [
                    {
                        "url": "./web/develop/v1/detail?id=env-1",
                        "status": 200,
                        "responsePreview": json.dumps(
                            {
                                "code": 0,
                                "msg": "OK",
                                "data": {
                                    "id": "env-1",
                                    "name": "ai3",
                                    "jupyterUrl": None,
                                    "vscodeUrl": None,
                                    "failedMessage": None,
                                    "podInfoList": [{"podName": "env-1-r0-0"}],
                                },
                            }
                        ),
                    },
                    {
                        "url": "./web/develop/v1/getShellVisitUrl",
                        "status": 200,
                        "body": json.dumps(
                            {
                                "id": "env-1",
                                "podName": "env-1-r0-0",
                                "type": "terminal",
                            }
                        ),
                        "responsePreview": json.dumps(
                            {
                                "code": 170022,
                                "msg": "获取shell终端信息失败",
                                "data": None,
                                "traceId": "trace-1",
                            }
                        ),
                    },
                ],
                "console": [
                    {
                        "text": "WebSocket connection to 'wss://aihuanxin.cn/kunlun/null' failed: Error during WebSocket handshake: Unexpected response code: 404"
                    }
                ],
                "websockets": [{"url": "wss://aihuanxin.cn/kunlun/null"}],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    summary = summarize_probe_artifacts([artifact])

    assert summary["env_name"] == "ai3"
    assert summary["shell_endpoint_failure"] is True
    assert summary["websocket_null_fallback"] is True
    assert summary["websocket_404_errors"]
    assert summary["shell_visit_failures"][0]["response"]["traceId"] == "trace-1"
