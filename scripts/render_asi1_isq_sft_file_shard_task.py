#!/usr/bin/env bash
"""exec' python3 "$0" "$@"
'"""

"""Render a small ASI1 task command that writes one local file shard remotely."""

import argparse
import base64
import hashlib
import json
import shlex
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
REMOTE_ROOT = "/root/work/software/quantum-gpt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--remote-rel", required=True)
    parser.add_argument("--remote-root", default=REMOTE_ROOT)
    parser.add_argument("--shard-index", required=True, type=int)
    parser.add_argument("--shard-count", required=True, type=int)
    parser.add_argument("--shard-chars", default=900_000, type=int)
    parser.add_argument("--command-chunk-chars", default=6_000, type=int)
    return parser.parse_args()


def py_line(source: str) -> str:
    return "python3 -c " + shlex.quote("exec(" + repr(source) + ")")


def main() -> int:
    args = parse_args()
    source = args.source if args.source.is_absolute() else ROOT / args.source
    if not source.is_file():
        raise SystemExit(f"missing source file: {source}")
    if args.shard_index < 0 or args.shard_index >= args.shard_count:
        raise SystemExit("--shard-index must be in [0, shard-count)")

    raw = source.read_bytes()
    encoded = base64.b64encode(raw).decode("ascii")
    start = args.shard_index * args.shard_chars
    end = min(len(encoded), start + args.shard_chars)
    if start >= len(encoded) and len(encoded) > 0:
        raise SystemExit("shard index starts beyond encoded payload")
    shard = encoded[start:end]

    remote_path = f"{args.remote_root.rstrip('/')}/{args.remote_rel}"
    b64_path = (
        f"{args.remote_root.rstrip('/')}/.upload/asi1_isq_sft/"
        f"{hashlib.sha256(args.remote_rel.encode()).hexdigest()[:16]}.gz.b64"
    )
    parent = str(PurePosixPath(remote_path).parent)

    lines = [
        "set -euo pipefail",
        f"echo __ASI1_ISQ_UPLOAD_SHARD_START__ {shlex.quote(args.remote_rel)} {args.shard_index + 1}/{args.shard_count}",
        "mkdir -p " + shlex.quote(str(PurePosixPath(b64_path).parent)) + " " + shlex.quote(parent),
    ]
    if args.shard_index == 0:
        lines.append("rm -f " + shlex.quote(b64_path) + " " + shlex.quote(remote_path))
    for offset in range(0, len(shard), args.command_chunk_chars):
        chunk = shard[offset : offset + args.command_chunk_chars]
        lines.append(
            py_line(
                "from pathlib import Path\n"
                f"p=Path({b64_path!r})\n"
                "old=p.read_text() if p.exists() else ''\n"
                f"text={chunk!r}\n"
                "p.write_text(old+text)\n"
            )
        )
    lines.append(
        py_line(
            "import pathlib\n"
            f"p=pathlib.Path({b64_path!r})\n"
            f"expected={end!r}\n"
            "actual=len(p.read_text())\n"
            "assert actual == expected\n"
            "print('__ASI1_ISQ_UPLOAD_B64_BYTES__ '+str(actual))\n"
        )
    )
    if args.shard_index == args.shard_count - 1:
        sha = hashlib.sha256(raw).hexdigest()
        lines.append(
            py_line(
                "import base64\n"
                "import hashlib\n"
                "import pathlib\n"
                f"src=pathlib.Path({b64_path!r})\n"
                f"dst=pathlib.Path({remote_path!r})\n"
                "data=base64.b64decode(src.read_text())\n"
                "dst.write_bytes(data)\n"
                f"expected={sha!r}\n"
                "actual=hashlib.sha256(data).hexdigest()\n"
                "assert actual == expected\n"
                f"print('__ASI1_ISQ_UPLOAD_FILE_OK__ {args.remote_rel} ' + actual)\n"
            )
        )
    lines.append(
        f"echo __ASI1_ISQ_UPLOAD_SHARD_DONE__ {shlex.quote(args.remote_rel)} {args.shard_index + 1}/{args.shard_count}"
    )

    print(
        json.dumps(
            {
                "remote_root": args.remote_root,
                "job_name": "asi1-isq-upload-shard",
                "remote_command": "\n".join(lines),
                "execution_command": "\n".join(lines),
                "single_line_execution": False,
                "source": str(source),
                "remote_path": remote_path,
                "remote_rel": args.remote_rel,
                "shard_index": args.shard_index,
                "shard_count": args.shard_count,
                "raw_bytes": len(raw),
                "encoded_bytes": len(encoded),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
