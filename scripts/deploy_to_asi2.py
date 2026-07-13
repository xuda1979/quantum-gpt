#!/usr/bin/env python3
import base64
import hashlib
import pathlib
import subprocess
import sys


def main():
    if len(sys.argv) > 1:
        local_file = pathlib.Path(sys.argv[1])
    else:
        local_file = pathlib.Path("training/qwen_sft_peft.py")

    if not local_file.exists():
        print(f"Error: {local_file} not found.")
        sys.exit(1)

    raw_bytes = local_file.read_bytes()
    local_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    b64_str = base64.b64encode(raw_bytes).decode("ascii")

    print(f"Local file size: {len(raw_bytes)} bytes")
    print(f"Local SHA256: {local_sha256}")
    print(f"Base64 length: {len(b64_str)}")

    temp_b64 = f"/tmp/{local_file.name}.b64"
    remote_target = f"/vllm-workspace/quantum-gpt/{local_file}"

    # 1. Clean remote b64 file
    print("Cleaning remote temp location...")
    subprocess.run(
        ["bash", "scripts/huanxin_env_shell.sh", "--env", "ASI2", f"rm -f {temp_b64}"], check=True
    )

    # 2. Upload chunk-by-chunk (each chunk is 12000 chars)
    chunk_size = 12000
    chunks = [b64_str[i : i + chunk_size] for i in range(0, len(b64_str), chunk_size)]
    print(f"Uploading {len(chunks)} chunks to ASI2...")

    for idx, chunk in enumerate(chunks):
        cmd = f"python3 -c \"import pathlib; p=pathlib.Path('{temp_b64}'); p.write_text((p.read_text() if p.exists() else '') + '{chunk}')\""
        subprocess.run(["bash", "scripts/huanxin_env_shell.sh", "--env", "ASI2", cmd], check=True)
        print(f"Uploaded chunk {idx+1}/{len(chunks)}")

    # 3. Decode remote b64 file
    print("Decoding remote base64...")
    decode_cmd = (
        f'python3 -c "import base64, pathlib; '
        f"pathlib.Path('{remote_target}').write_bytes("
        f"base64.b64decode(pathlib.Path('{temp_b64}').read_text()))\""
    )
    subprocess.run(
        ["bash", "scripts/huanxin_env_shell.sh", "--env", "ASI2", decode_cmd], check=True
    )

    # 4. Verify remote sha256
    print("Verifying file integrity...")
    res = subprocess.run(
        ["bash", "scripts/huanxin_env_shell.sh", "--env", "ASI2", f"sha256sum {remote_target}"],
        capture_output=True,
        text=True,
        check=True,
    )
    print("Remote verification result:")
    print(res.stdout.strip())

    if local_sha256 in res.stdout:
        print("Success! File synced perfectly.")
    else:
        print("Error: SHA256 mismatch!")
        sys.exit(1)


if __name__ == "__main__":
    main()
