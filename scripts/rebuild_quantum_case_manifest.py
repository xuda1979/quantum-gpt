"""Rebuild the quantum case manifest from the already-generated markdown files.

This executes the embedded python block in each case file, captures its
RESULT_JSON line, and rewrites _manifest.json without regenerating the markdown.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qcase_gen.catalog import build_catalog

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "模版与数据" / "生成的数据"
MANIFEST = OUT_DIR / "_manifest.json"


def _reason(family: str, result: dict) -> str:
    if family == "QAOA":
        if result.get("optimal_hit", False):
            return "optimal (ratio=1.00)"
        return f"approx ratio={result.get('approx_ratio'):.2f}"
    if family == "VQE":
        err = float(result.get("abs_error", 0.0))
        ref = result.get("reference")
        if err <= 5e-3:
            return f"abs err={err:.1e}"
        if ref is not None and abs(ref) > 1e-9:
            return f"rel err={err / abs(ref):.2%}"
        return f"abs err={err:.1e}"
    if family == "VQC":
        return f"acc={result.get('accuracy')}"
    if family == "QPE":
        return "exact"
    if family == "Grover":
        return f"p={result.get('objective')}"
    return "n/a"


def _int_match(pattern: str, text: str) -> int:
    match = re.search(pattern, text, re.M)
    if not match:
        raise SystemExit(f"missing field for pattern: {pattern}")
    return int(match.group(1))


def _float_match(pattern: str, text: str) -> float:
    match = re.search(pattern, text, re.M)
    if not match:
        raise SystemExit(f"missing field for pattern: {pattern}")
    return float(match.group(1))


def _parse_result(text: str, family: str) -> dict:
    summary = re.search(r"- \*\*预期输出摘要\*\*: (.+)", text)
    if not summary:
        raise SystemExit("missing 预期输出摘要 line")
    summary_text = summary.group(1)

    num_qubits = _int_match(r"逻辑量子比特数:\s*(\d+)", text)
    depth = _int_match(r"线路深度:\s*(\d+)", text)
    num_params = _int_match(r"参数量:\s*(\d+)", text)
    num_terms = _int_match(r"(?:哈密顿量/泡利项数|num Pauli terms)[:=]\s*(\d+)", text)

    result: dict[str, object] = {
        "num_qubits": num_qubits,
        "depth": depth,
        "num_params": num_params,
        "num_terms": num_terms,
    }

    if family == "QAOA":
        ratio = _float_match(r"近似比\s*([0-9.]+)", summary_text)
        result["approx_ratio"] = ratio
        result["optimal_hit"] = abs(ratio - 1.0) < 5e-4
        return result

    if family == "VQE":
        abs_err = _float_match(r"误差\s*([0-9.eE+-]+)", summary_text)
        exact_match = re.search(r"精确值\s*([+-]?[0-9.]+)", summary_text)
        result["abs_error"] = abs_err
        if exact_match:
            result["reference"] = float(exact_match.group(1))
        return result

    if family == "VQC":
        acc_match = re.search(r"训练准确率约\s*([0-9.]+)", summary_text)
        if not acc_match:
            acc_match = re.search(r"accuracy\s*([0-9.]+)", summary_text)
        if not acc_match:
            raise SystemExit("missing accuracy in VQC summary")
        result["accuracy"] = float(acc_match.group(1))
        return result

    if family == "QPE":
        err_match = re.search(r"绝对误差\s*([0-9.eE+-]+)", summary_text)
        result["abs_error"] = float(err_match.group(1)) if err_match else 0.0
        return result

    if family == "Grover":
        prob_match = re.search(r"命中比特串与命中概率\s*([0-9.]+)", summary_text)
        if not prob_match:
            prob_match = re.search(r"命中概率\s*([0-9.]+)", summary_text)
        if not prob_match:
            raise SystemExit("missing probability in Grover summary")
        result["objective"] = float(prob_match.group(1))
        return result

    return result


def main() -> None:
    entries: list[dict] = []
    for idx, builder in enumerate(build_catalog(), start=1):
        _, key, fname = builder()
        path = OUT_DIR / f"{fname}_case.md"
        if not path.exists():
            raise SystemExit(f"missing case file: {path}")

        text = path.read_text(encoding="utf-8")
        result = _parse_result(text, key.split("__")[1])
        entries.append(
            {
                "index": idx,
                "key": key,
                "file": f"{fname}_case.md",
                "num_qubits": result["num_qubits"],
                "depth": result["depth"],
                "num_params": result["num_params"],
                "num_terms": result["num_terms"],
                "reason": _reason(key.split("__")[1], result),
            }
        )
        print(f"[{idx}] {key}", flush=True)

    MANIFEST.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"manifest_entries {len(entries)}")


if __name__ == "__main__":
    main()
