#!/usr/bin/env bash
"""exec' python3 "$0" "$@"
'"""

"""Render an ASI1 task command that downloads and verifies isq_train_cot.json."""

import argparse
import json
import shlex


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--url", required=True)
    parser.add_argument("--resolve-ip", default="")
    parser.add_argument("--remote-root", default="/root/work/software/quantum-gpt")
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--gzip-sha256", required=True)
    parser.add_argument("--expected-rows", default="5611")
    return parser.parse_args()


def py_line(source: str) -> str:
    return "python3 -c " + shlex.quote("exec(" + repr(source) + ")")


def main() -> int:
    args = parse_args()
    remote_root = args.remote_root.rstrip("/")
    gz_path = f"{remote_root}/isq_train_cot.json.gz"
    json_path = f"{remote_root}/isq_train_cot.json"
    lines = [
        "set -euo pipefail",
        "echo __ASI1_ISQ_SOURCE_DOWNLOAD_START__",
        f"mkdir -p {shlex.quote(remote_root)}",
        f"cd {shlex.quote(remote_root)}",
        (
            "curl -fsSL --connect-timeout 20 --max-time 300 "
            + (
                f"--resolve {shlex.quote('exhibitions-strikes-circles-duck.trycloudflare.com:443:' + args.resolve_ip)} "
                if args.resolve_ip
                else ""
            )
            + f"{shlex.quote(args.url)} -o {shlex.quote(gz_path)}"
        ),
        f"echo __ASI1_ISQ_SOURCE_GZ_DOWNLOADED__ {shlex.quote(gz_path)}",
        py_line(
            "import hashlib\n"
            "import pathlib as p\n"
            f"path={gz_path!r}\n"
            f"expected={args.gzip_sha256!r}\n"
            "actual=hashlib.sha256(p.Path(path).read_bytes()).hexdigest()\n"
            "print('__ASI1_ISQ_SOURCE_GZ_SHA__ '+actual)\n"
            "assert actual == expected\n"
        ),
        py_line(
            "import gzip\n"
            "import pathlib as p\n"
            f"src={gz_path!r}\n"
            f"dst={json_path!r}\n"
            "p.Path(dst).write_bytes(gzip.decompress(p.Path(src).read_bytes()))\n"
        ),
        py_line(
            "import hashlib\n"
            "import pathlib as p\n"
            f"path={json_path!r}\n"
            f"expected={args.sha256!r}\n"
            "actual=hashlib.sha256(p.Path(path).read_bytes()).hexdigest()\n"
            "print('__ASI1_ISQ_SOURCE_JSON_SHA__ '+actual)\n"
            "assert actual == expected\n"
        ),
        py_line(
            "import json\n"
            f"path={json_path!r}\n"
            f"expected={int(args.expected_rows)!r}\n"
            "rows=json.load(open(path))\n"
            "actual=len(rows)\n"
            "assert actual == expected\n"
            "print('__ASI1_ISQ_SOURCE_ROWS__ '+str(actual))\n"
        ),
        "echo __ASI1_ISQ_SOURCE_DOWNLOAD_DONE__",
    ]
    command = "\n".join(lines)
    print(
        json.dumps(
            {
                "remote_root": remote_root,
                "job_name": "asi1-isq-source-download",
                "remote_command": command,
                "execution_command": command,
                "single_line_execution": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
