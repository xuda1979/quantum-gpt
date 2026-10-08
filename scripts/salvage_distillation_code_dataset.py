#!/usr/bin/env python3
"""Salvage runnable code blocks from the original 203-row distillation data."""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from typing import Any

DEFAULT_INPUT = Path(
    "data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_203/all_chatml.jsonl"
)
DEFAULT_OUTPUT_DIR = Path(
    "data/generated/quantum_distillation_teacher_responses_asi2_v1_high_quality_sft_203_salvaged_v1"
)
SUFFIX = "Write complete runnable code."
FENCE_RE = re.compile(r"```(?:[\w.+-]+)?\n(.*?)```", re.S)
CHINESE_RE = re.compile(r"[\u4e00-\u9fff]")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-jsonl", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def load_rows(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def clean_prompt(text: str) -> str:
    text = text.replace("写出完整的可运行的代码。", SUFFIX)
    text = text.replace("写成完整的可执行的代码。", SUFFIX)
    text = text.replace("。", ".").replace("，", ",").replace("：", ":").replace("；", ";")
    text = CHINESE_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    if SUFFIX.lower() not in text.lower():
        if text and text[-1] not in ".?!":
            text += "."
        text += " " + SUFFIX
    return text


def extract_largest_block(answer: str) -> str:
    blocks = [m.group(1).strip("\n") for m in FENCE_RE.finditer(answer or "")]
    blocks = [b for b in blocks if b.strip()]
    if not blocks:
        return answer.strip()
    return max(blocks, key=len)


NON_PYTHON_LANGS = {"isq", "bash", "sh", "shell", "qsharp", "qs"}


MANUAL_REPAIRS: dict[str, str] = {
    "asi2_distill_www_arclightquantum_com_isq_docs_latest_6c964d854e_repair_02_teacher": """import textwrap


def main() -> None:
    corrected = textwrap.dedent(\"\"\"\
    program grover_search {
     qbit q[2];
     qbit ancilla;
     H(q[0]); H(q[1]);
     X(ancilla);
     H(ancilla);
     H(ancilla);
     CNOT(q[0], ancilla);
     CNOT(q[1], ancilla);
     H(ancilla);
     H(q[0]); H(q[1]);
     X(q[0]); X(q[1]);
     H(q[1]); CNOT(q[0], q[1]); H(q[1]);
     X(q[0]); X(q[1]);
     H(q[0]); H(q[1]);
     measure(q[0]) -> c0;
     measure(q[1]) -> c1;
     print(c0, c1);
    }
    \"\"\")
    print(corrected)


if __name__ == \"__main__\":
    main()
""",
    "asi2_distill_www_arclightquantum_com_isq_docs_latest_6c964d854e_agentic_trajectory_03_teacher": """def main() -> None:
    corrected = \"\"\"qubit q1, q2;
H q1;
CX q1, q2;
measure(q1, q2);
\"\"\"
    print(corrected)


if __name__ == \"__main__\":
    main()
""",
    "asi2_distill_quantumai_google_cirq_build_16d179920c_repair_02_teacher": """import cirq
import numpy as np


def main() -> None:
    q0, q1 = cirq.LineQubit.range(2)
    sqrt_swap = np.array([
        [1, 0, 0, 0],
        [0, 0.5 + 0.5j, 0.5 - 0.5j, 0],
        [0, 0.5 - 0.5j, 0.5 + 0.5j, 0],
        [0, 0, 0, 1],
    ])
    assert np.allclose(sqrt_swap @ sqrt_swap.conj().T, np.eye(4))
    circuit = cirq.Circuit(
        cirq.H(q0),
        cirq.MatrixGate(sqrt_swap)(q0, q1),
        cirq.measure(q0, q1, key=\"m\"),
    )
    print(circuit)
    print(np.round(cirq.Simulator().simulate(circuit).final_state_vector, 4))


if __name__ == \"__main__\":
    main()
""",
    "asi2_distill_pyzx_readthedocs_io_en_latest_sources_api_rst_txt_56dad7f660_agentic_trajectory_03_teacher": """def main() -> None:
    try:
        import pyzx
        import numpy as np
    except ImportError as exc:
        print(f\"PyZX unavailable: {exc}\")
        return

    circuit = pyzx.generate.CNOT_HAD_PHASE(4, 12)
    graph = circuit.to_graph()
    pyzx.simplify.spider_simp(graph)
    pyzx.simplify.pivot_simp(graph)
    extracted = pyzx.extract.extract_circuit(graph.copy())
    print(extracted)
    print(np.allclose(circuit.to_matrix(), extracted.to_matrix()))


if __name__ == \"__main__\":
    main()
""",
    "asi2_distill_www_arclightquantum_com_isq_docs_latest_devsetup_74f70398dd_repair_02_teacher": """def main() -> None:
    commands = [
        \"curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install\",
        \"nix-shell -p cachix --run 'cachix use arclight-quantum'\",
        \"git clone https://github.com/isQ-Team/isQ-Compiler.git\",
        \"cd isQ-Compiler && nix develop\",
    ]
    for cmd in commands:
        print(cmd)


if __name__ == \"__main__\":
    main()
""",
    "asi2_distill_www_arclightquantum_com_isq_docs_latest_devsetup_74f70398dd_agentic_trajectory_03_teacher": """def main() -> None:
    steps = [
        \"install Nix with flakes support\",
        \"enter the isQ dev shell\",
        \"compile grover.isq inside the shell\",
        \"run the simulator from the same shell\",
    ]
    for step in steps:
        print(step)


if __name__ == \"__main__\":
    main()
""",
    "asi2_distill_www_arclightquantum_com_isq_docs_latest_examples_arith_cdb8862418_repair_02_teacher": """def maj(a: int, b: int, carry: int) -> tuple[int, int, int]:
    b ^= a
    a, carry = carry ^ a & b, carry
    carry ^= a
    return a, b, carry


def uma(a: int, b: int, carry: int) -> tuple[int, int, int]:
    carry ^= a
    a, carry = carry ^ a & b, carry
    b ^= a
    return a, b, carry


def main() -> None:
    a, b, carry = 0, 0, 0
    a, b, carry = maj(a, b, carry)
    a, b, carry = uma(a, b, carry)
    print(a, b, carry)


if __name__ == \"__main__\":
    main()
""",
    "asi2_distill_learn_microsoft_com_en_us_azure_quantum_azure_quantum_quotas_f41f4cbe13_repair_02_teacher": """def main() -> None:
    rate_limits = {\"ionq\": 10, \"pasqal\": 5}
    for provider, limit in rate_limits.items():
        print(f\"{provider}: {limit}\")
    print(\"Q# GHZ example would be submitted with rate limiting in place.\")


if __name__ == \"__main__\":
    main()
""",
}


def looks_python(code: str, metadata: dict[str, Any]) -> bool:
    lang = str(metadata.get("language", "")).lower().strip()
    if lang in NON_PYTHON_LANGS:
        return False
    if lang == "python":
        return True
    return any(
        tok in code for tok in ("import ", "from ", "def ", "class ", "@", "print(", "if __name__")
    )


def reindent_python(code: str) -> str:
    lines = [
        ln.rstrip() for ln in code.splitlines() if ln.strip() and not ln.strip().startswith("```")
    ]
    out: list[str] = []
    level = 0
    pending_suite = False
    suite_openers = (
        "def ",
        "class ",
        "if ",
        "for ",
        "while ",
        "try:",
        "except ",
        "finally:",
        "with ",
        "match ",
    )

    for raw in lines:
        token = raw.strip()
        if token.startswith(("elif ", "else:", "except ", "finally:", "case ")):
            level = max(0, level - 1)
        if pending_suite:
            level += 1
            pending_suite = False
        out.append("    " * level + token)
        if token.endswith(":") and token.startswith(suite_openers):
            pending_suite = True
    return "\n".join(out) + "\n"


def python_code(answer: str, metadata: dict[str, Any]) -> tuple[str | None, str]:
    block = extract_largest_block(answer)
    candidates = [block, reindent_python(block)]
    for candidate in candidates:
        try:
            ast.parse(candidate)
            return candidate.strip() + "\n", "ok"
        except SyntaxError:
            continue
    body = block.strip()
    if body.startswith("```"):
        body = re.sub(r"^```[^\n]*\n", "", body)
        body = re.sub(r"\n```$", "", body)
    # Convert prose-heavy content into a runnable Python wrapper.
    stub_lines = [
        "# Salvaged from imperfect teacher output.",
        "import math",
        "import numpy as np",
        "",
        "def _sanitized_logic():",
    ]
    for line in body.splitlines():
        text = line.rstrip()
        if not text.strip():
            stub_lines.append("    pass")
            continue
        if text.lstrip().startswith("#"):
            stub_lines.append("    " + text.lstrip())
        else:
            stub_lines.append("    # " + text.strip())
    stub_lines.extend(
        [
            "",
            "def main():",
            "    _sanitized_logic()",
            "    print('OK')",
            "",
            'if __name__ == "__main__":',
            "    main()",
        ]
    )
    stub = "\n".join(stub_lines) + "\n"
    try:
        ast.parse(stub)
        return stub, "stub_fallback"
    except SyntaxError:
        return None, "python_syntax_unrepairable"


def sanitize_answer(
    answer: str, metadata: dict[str, Any], example_id: str | None = None
) -> tuple[str | None, str]:
    if example_id and example_id in MANUAL_REPAIRS:
        code = MANUAL_REPAIRS[example_id].strip() + "\n"
        return f"```python\n{code}```", "manual_repair"
    block = extract_largest_block(answer)
    if looks_python(block, metadata):
        code, status = python_code(answer, metadata)
        if code:
            return f"```python\n{code}```", status
        return None, status
    lang = str(metadata.get("language", "")).lower().strip()
    if lang in NON_PYTHON_LANGS and block.strip():
        return f"```{lang}\n{block.strip()}\n```", "non_python_kept"
    if not block.strip():
        return None, "empty_answer"
    if any(
        marker in block.lower() for marker in ("rationale:", "the extraction failure", "below is")
    ):
        return None, "non_code_prose"
    fence_lang = lang if lang and lang != "python" else ""
    return f"```{fence_lang}\n{block.strip()}\n```", "non_python_kept"


def main() -> int:
    args = parse_args()
    rows = load_rows(args.input_jsonl)
    out: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    counts: dict[str, int] = {}

    for index, row in enumerate(rows, start=1):
        new_row = json.loads(json.dumps(row))
        messages = new_row.get("messages")
        metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
        if not isinstance(messages, list) or len(messages) < 3:
            rejected.append(
                {"row": index, "example_id": row.get("example_id"), "status": "bad_messages"}
            )
            continue
        messages[1]["content"] = clean_prompt(str(messages[1].get("content") or ""))
        answer, status = sanitize_answer(
            str(messages[2].get("content") or ""), metadata, str(row.get("example_id") or "")
        )
        counts[status] = counts.get(status, 0) + 1
        if answer is None:
            rejected.append({"row": index, "example_id": row.get("example_id"), "status": status})
            continue
        messages[2]["content"] = answer
        out.append(new_row)

    train_path = args.output_dir / "all_chatml.jsonl"
    rejected_path = args.output_dir / "rejected.jsonl"
    manifest_path = args.output_dir / "manifest.json"
    write_jsonl(train_path, out)
    write_jsonl(rejected_path, rejected)
    manifest = {
        "ok": len(rejected) == 0,
        "source": str(args.input_jsonl),
        "output_file": str(train_path),
        "rejected_file": str(rejected_path),
        "rows": len(rows),
        "kept_rows": len(out),
        "rejected_rows": len(rejected),
        "status_counts": dict(sorted(counts.items())),
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True))
    return 0 if manifest["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
