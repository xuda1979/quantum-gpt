from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_sensitive_exec_redacts_state_response_and_terminal_scrollback() -> None:
    source = (ROOT / "browser-automation/huanxin_browser_daemon.js").read_text(encoding="utf-8")

    assert "lastCommand = sensitive ? '[sensitive command redacted]' : command" in source
    assert "command: sensitive ? '[sensitive command redacted]' : command" in source
    assert "redactSensitiveResult(rawResult, redactValues)" in source
    assert "if (sensitive) await eraseTerminalScrollback()" in source
    assert "sensitive ? '[sensitive terminal redacted]'" in source
    assert "[3J" in source and "[2J" in source
    assert "const stateKey = args.instance" in source
    assert "currentUrl: redactAuthUrl(currentUrl)" in source
