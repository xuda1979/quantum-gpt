from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
from typing import Any, Iterable


DEFAULT_MIN_VERSION = (3, 10)
DEFAULT_PYTHON_BASENAMES = (
    "python3.13",
    "python3.12",
    "python3.11",
    "python3.10",
    "python3",
)
WORKSPACE_ROOT = Path(__file__).resolve().parents[1]


def format_version(version: tuple[int, ...] | None) -> str | None:
    if version is None:
        return None
    return ".".join(str(part) for part in version)


def parse_min_version(raw: str) -> tuple[int, int]:
    pieces = raw.strip().split(".")
    if len(pieces) != 2:
        raise ValueError(f"Expected <major>.<minor>, got: {raw!r}")
    major, minor = (int(piece) for piece in pieces)
    return major, minor


def detect_python_version(python_bin: str) -> tuple[int, int, int] | None:
    completed = subprocess.run(
        [
            python_bin,
            "-c",
            "import sys; print('.'.join(str(part) for part in sys.version_info[:3]))",
        ],
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return None
    raw = completed.stdout.strip().split(".")
    if len(raw) != 3:
        return None
    try:
        return int(raw[0]), int(raw[1]), int(raw[2])
    except ValueError:
        return None


def candidate_python_prefixes() -> list[Path]:
    return [
        Path.home() / "homebrew" / "bin",
        Path("/opt/homebrew/bin"),
        Path("/usr/local/bin"),
    ]


def workspace_python_candidates() -> list[Path]:
    local_root = WORKSPACE_ROOT / ".local-python"
    return [
        local_root / "cpython-3.11.15" / "bin" / "python3.11",
        local_root / "cpython-3.11.15" / "bin" / "python3",
    ]


def candidate_brew_binaries() -> list[Path]:
    return [
        Path(path)
        for path in [
            shutil.which("brew"),
            str(Path.home() / "homebrew" / "bin" / "brew"),
            "/opt/homebrew/bin/brew",
            "/usr/local/bin/brew",
        ]
        if path
    ]


def _iter_candidate_paths(
    basenames: Iterable[str] = DEFAULT_PYTHON_BASENAMES,
    extra_candidates: Iterable[str] = (),
) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
    seen: set[str] = set()

    def add(path_str: str, source: str) -> None:
        if not path_str:
            return
        if path_str in seen:
            return
        seen.add(path_str)
        candidates.append((path_str, source))

    for raw in extra_candidates:
        add(str(raw), "extra_candidate")
    for candidate in workspace_python_candidates():
        add(str(candidate), "workspace_local")
    for basename in basenames:
        resolved = shutil.which(basename)
        if resolved:
            add(resolved, "path_lookup")
    for prefix in candidate_python_prefixes():
        for basename in basenames:
            add(str(prefix / basename), f"prefix:{prefix}")
    return candidates


def resolve_python_interpreter(
    *,
    min_version: tuple[int, int] = DEFAULT_MIN_VERSION,
    extra_candidates: Iterable[str] = (),
) -> dict[str, Any]:
    minimum_version_text = format_version(min_version)
    candidate_summaries: list[dict[str, Any]] = []
    selected: dict[str, Any] | None = None
    for candidate_path, source in _iter_candidate_paths(extra_candidates=extra_candidates):
        path = Path(candidate_path)
        exists = path.is_file() and path.exists()
        version = detect_python_version(candidate_path) if exists else None
        meets_minimum = version is not None and version[:2] >= min_version
        summary = {
            "path": candidate_path,
            "source": source,
            "exists": exists,
            "version": format_version(version),
            "meets_minimum": meets_minimum,
        }
        candidate_summaries.append(summary)
        if selected is None and meets_minimum:
            selected = summary

    brew_binary = next((path for path in candidate_brew_binaries() if path.exists()), None)
    install_command = None
    bootstrap_script = WORKSPACE_ROOT / "scripts" / "bootstrap_local_python311_from_cache.sh"
    python_cache_matches = list((Path.home() / "Library" / "Caches" / "Homebrew" / "downloads").glob("*--Python-3.11.15.tgz"))
    local_openssl_candidates = [
        Path.home() / "homebrew" / "opt" / "openssl",
        Path.home() / "homebrew" / "opt" / "openssl@3",
        Path("/opt/homebrew/opt/openssl"),
        Path("/opt/homebrew/opt/openssl@3"),
        Path("/usr/local/opt/openssl"),
        Path("/usr/local/opt/openssl@3"),
    ]
    local_openssl_available = any(
        (candidate / "include" / "openssl" / "ssl.h").exists() and (candidate / "lib" / "libssl.dylib").exists()
        for candidate in local_openssl_candidates
    )
    if selected is None and bootstrap_script.exists() and python_cache_matches and local_openssl_available:
        install_command = f"bash {bootstrap_script.relative_to(WORKSPACE_ROOT)}"
    elif selected is None and brew_binary is not None:
        install_command = f"{brew_binary} install python@3.11"

    result = {
        "status": "ok" if selected is not None else "error",
        "minimum_version": minimum_version_text,
        "selected_path": selected["path"] if selected is not None else None,
        "selected_version": selected["version"] if selected is not None else None,
        "brew_binary": str(brew_binary) if brew_binary is not None else None,
        "install_command": install_command,
        "candidates": candidate_summaries,
    }
    if selected is None:
        result["error"] = (
            f"No local Python interpreter meeting >= {minimum_version_text} was found on PATH "
            "or known local bootstrap paths."
        )
    return result
