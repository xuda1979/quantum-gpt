#!/usr/bin/env python3
"""upload_to_env.py — upload a local file to a Huanxin environment via base64 chunks.

Usage:
  scripts/upload_to_env.py <local-file> <env-name> <remote-path>
"""

import base64
import pathlib
import subprocess
import sys


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    local_file = pathlib.Path(sys.argv[1])
    env = sys.argv[2]
    remote_target = sys.argv[3]
    if not local_file.exists():
        print(f"Error: {local_file} not found.")
        sys.exit(1)

    raw_bytes = local_file.read_bytes()
    b64_str = base64.b64encode(raw_bytes).decode("ascii")
    print(f"Local file size: {len(raw_bytes)} bytes, base64 length: {len(b64_str)}")

    def shell(cmd):
        r = subprocess.run(
            ["bash", "scripts/huanxin_shell.sh", env, cmd], capture_output=True, text=True
        )
        if r.returncode != 0:
            print(f"shell failed: {cmd}\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
            sys.exit(1)
        return r.stdout

    temp_b64 = f"/tmp/upload_{local_file.name}.b64"
    shell(f"rm -f {temp_b64}")
    chunk_size = 12000
    chunks = [b64_str[i : i + chunk_size] for i in range(0, len(b64_str), chunk_size)]
    for idx, chunk in enumerate(chunks, 1):
        # shell-safe: wrap chunk in single quotes; base64 alphabet has no quotes.
        cmd = f"python3 -c \"import pathlib; p=pathlib.Path('{temp_b64}'); p.write_text((p.read_text() if p.exists() else '') + '{chunk}')\""
        shell(cmd)
        print(f"Uploaded chunk {idx}/{len(chunks)}", flush=True)

    shell(
        f"python3 -c \"import base64, pathlib; pathlib.Path('{remote_target}').write_bytes(base64.b64decode(pathlib.Path('{temp_b64}').read_text()))\""
    )
    shell(f"rm -f {temp_b64}")
    print(f"Uploaded -> {remote_target}")


if __name__ == "__main__":
    main()
