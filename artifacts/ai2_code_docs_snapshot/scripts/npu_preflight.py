#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NPU Pre-flight Check Script (NPU 预检脚本)

在远程 NPU 服务器上启动训练作业之前运行此脚本，用于验证:
  1. torch 是否已安装并可导入
  2. torch_npu (昇腾 PyTorch 扩展) 是否已安装
  3. NPU 设备是否可见且可用
  4. 关键环境变量是否已设置 (ASCEND_*, HCCL_*)

Usage:
    python scripts/npu_preflight.py

Exit codes:
    0 - All checks passed
    1 - One or more checks failed
"""

import os
import sys

# ANSI colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_ok(msg: str):
    print(f"  {GREEN}✓{RESET} {msg}")


def print_fail(msg: str):
    print(f"  {RED}✗{RESET} {msg}")


def print_warn(msg: str):
    print(f"  {YELLOW}⚠{RESET} {msg}")


def print_section(title: str):
    print(f"\n{BOLD}[{title}]{RESET}")


def check_torch() -> bool:
    """Check if PyTorch is installed and importable."""
    print_section("PyTorch")
    try:
        import torch
        print_ok(f"torch imported successfully (version {torch.__version__})")
        return True
    except ImportError as e:
        print_fail(f"Failed to import torch: {e}")
        print_fail("Install a PyTorch build compatible with Ascend. See https://www.hiascend.com/")
        return False


def check_torch_npu() -> bool:
    """Check if torch_npu extension is installed."""
    print_section("torch_npu (Ascend Extension)")
    try:
        import torch_npu
        version = getattr(torch_npu, "__version__", "unknown")
        print_ok(f"torch_npu imported successfully (version {version})")
        return True
    except ImportError as e:
        print_fail(f"Failed to import torch_npu: {e}")
        print_fail("Install the Ascend PyTorch extension (torch_npu).")
        print_fail("See https://www.hiascend.com/ or your cluster admin for instructions.")
        return False


def check_npu_devices() -> bool:
    """Check if NPU devices are visible and accessible."""
    print_section("NPU Devices")
    try:
        import torch
        if not hasattr(torch, "npu"):
            print_fail("torch.npu namespace not available. torch_npu may not be loaded correctly.")
            return False

        if not torch.npu.is_available():
            print_fail("torch.npu.is_available() returned False.")
            print_fail("Ensure the Ascend driver is installed and NPU devices are accessible.")
            return False

        device_count = torch.npu.device_count()
        if device_count == 0:
            print_fail("torch.npu.device_count() returned 0. No NPU devices found.")
            return False

        print_ok(f"NPU devices available: {device_count}")

        # List device names if possible
        for i in range(device_count):
            try:
                name = torch.npu.get_device_name(i)
                print_ok(f"  NPU:{i} - {name}")
            except Exception:
                print_ok(f"  NPU:{i} - (name unavailable)")

        return True
    except Exception as e:
        print_fail(f"Error checking NPU devices: {e}")
        return False


def check_env_vars() -> bool:
    """Check important Ascend/HCCL environment variables."""
    print_section("Environment Variables")

    critical_vars = [
        "ASCEND_VISIBLE_DEVICES",
        "ASCEND_RT_VISIBLE_DEVICES",
    ]
    optional_vars = [
        "HCCL_WHITELIST_DISABLE",
        "HCCL_CONNECT_TIMEOUT",
        "COMBINED_ENABLE",
        "ASCEND_LAUNCH_BLOCKING",
    ]

    all_ok = True

    for var in critical_vars:
        val = os.environ.get(var)
        if val is not None:
            print_ok(f"{var}={val}")
        else:
            print_warn(f"{var} is not set (may be auto-configured by driver)")
            # Not a hard failure, but worth noting

    for var in optional_vars:
        val = os.environ.get(var)
        if val is not None:
            print_ok(f"{var}={val}")
        # Silently skip if not set; these are truly optional

    # Check MASTER_ADDR / MASTER_PORT for distributed
    master_addr = os.environ.get("MASTER_ADDR")
    master_port = os.environ.get("MASTER_PORT")
    if master_addr or master_port:
        print_ok(f"MASTER_ADDR={master_addr}, MASTER_PORT={master_port} (distributed mode)")

    return all_ok


def check_hccl() -> bool:
    """Check if HCCL backend can be initialized (optional, may require multi-process)."""
    print_section("HCCL Backend (informational)")
    try:
        import torch.distributed as dist
        backends = dist.Backend.backend_list if hasattr(dist.Backend, "backend_list") else []
        if "hccl" in str(backends).lower() or hasattr(dist, "is_hccl_available"):
            print_ok("HCCL backend appears to be registered.")
        else:
            print_warn("HCCL backend registration could not be confirmed (may still work).")
        return True
    except Exception as e:
        print_warn(f"Could not check HCCL backend: {e}")
        return True  # Non-fatal


def main():
    print(f"{BOLD}========================================{RESET}")
    print(f"{BOLD}    NPU Pre-flight Check{RESET}")
    print(f"{BOLD}========================================{RESET}")

    results = []

    results.append(("PyTorch", check_torch()))
    if results[-1][1]:
        results.append(("torch_npu", check_torch_npu()))
        if results[-1][1]:
            results.append(("NPU Devices", check_npu_devices()))
            results.append(("HCCL Backend", check_hccl()))

    results.append(("Environment", check_env_vars()))

    print(f"\n{BOLD}========================================{RESET}")
    print(f"{BOLD}    Summary{RESET}")
    print(f"{BOLD}========================================{RESET}")

    failed = [name for name, ok in results if not ok]
    if failed:
        print(f"\n{RED}Pre-flight FAILED.{RESET} The following checks did not pass:")
        for name in failed:
            print(f"  - {name}")
        print(f"\nPlease fix the issues above before running training with --use_npu.")
        sys.exit(1)
    else:
        print(f"\n{GREEN}All pre-flight checks passed!{RESET}")
        print("You can now run training with --use_npu.\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
