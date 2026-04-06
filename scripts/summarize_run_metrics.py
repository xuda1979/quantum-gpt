#!/usr/bin/env python3
"""Summarize a completed training output dir and compare it to project baselines."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BASELINES: dict[str, Path] = {
    "semantic_v4_8npu_20step": Path("outputs/interface-prefix-semantic-v4-8npu-20step/metrics.json"),
    "semantic_v4_smoke20": Path("outputs/fast-lora-qwen25-1p5b-interface-prefix-semantic-v4-smoke20/metrics.json"),
    "codefirst_mini": Path("outputs/fast-lora-qwen25-1p5b-codefirst-mini/metrics.json"),
}


@dataclass(frozen=True)
class RunSummary:
    output_dir: Path
    model_name: str
    device: str
    world_size: int | None
    train_examples: int | None
    eval_examples: int | None
    optimizer_steps_per_epoch: int | None
    max_available_steps: int | None
    requested_max_steps: int | None
    completed_steps: int | None
    final_eval_loss: float | None
    final_eval_perplexity: float | None
    signature_sha256: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path, help="Completed training output directory")
    parser.add_argument("--markdown", action="store_true", help="Render a human-readable markdown report")
    parser.add_argument(
        "--baseline",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="Optional additional baseline override. Can be repeated.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_summary(output_dir: Path, metrics: dict[str, Any]) -> RunSummary:
    signature = metrics.get("signature") or {}
    final_eval = metrics.get("final_eval") or {}
    return RunSummary(
        output_dir=output_dir,
        model_name=str(metrics.get("model_name", "")),
        device=str(metrics.get("device", "")),
        world_size=metrics.get("world_size"),
        train_examples=metrics.get("train_examples"),
        eval_examples=metrics.get("eval_examples"),
        optimizer_steps_per_epoch=metrics.get("optimizer_steps_per_epoch"),
        max_available_steps=metrics.get("max_available_steps"),
        requested_max_steps=metrics.get("requested_max_steps", metrics.get("signature", {}).get("max_steps")),
        completed_steps=metrics.get("completed_steps", metrics.get("max_steps")),
        final_eval_loss=final_eval.get("loss"),
        final_eval_perplexity=final_eval.get("perplexity"),
        signature_sha256=signature.get("signature_sha256"),
    )


def load_summary_for_dir(output_dir: Path) -> RunSummary:
    metrics_path = output_dir / "metrics.json"
    if not metrics_path.exists():
        raise SystemExit(f"missing metrics file: {metrics_path}")
    return extract_summary(output_dir, load_json(metrics_path))


def resolve_baselines(overrides: list[str]) -> dict[str, Path]:
    baselines = dict(BASELINES)
    for item in overrides:
        if "=" not in item:
            raise SystemExit(f"invalid --baseline value {item!r}; expected NAME=PATH")
        name, raw_path = item.split("=", 1)
        baselines[name] = Path(raw_path)
    return baselines


def metrics_path_for(path: Path) -> Path:
    if path.is_dir():
        return path / "metrics.json"
    return path


def summarize(summary: RunSummary, baselines: dict[str, RunSummary]) -> dict[str, Any]:
    run = {
        "output_dir": str(summary.output_dir),
        "model_name": summary.model_name,
        "device": summary.device,
        "world_size": summary.world_size,
        "train_examples": summary.train_examples,
        "eval_examples": summary.eval_examples,
        "optimizer_steps_per_epoch": summary.optimizer_steps_per_epoch,
        "max_available_steps": summary.max_available_steps,
        "requested_max_steps": summary.requested_max_steps,
        "completed_steps": summary.completed_steps,
        "final_eval_loss": summary.final_eval_loss,
        "final_eval_perplexity": summary.final_eval_perplexity,
        "signature_sha256": summary.signature_sha256,
    }

    comparisons: dict[str, Any] = {}
    for name, baseline in baselines.items():
        comparisons[name] = {
            "baseline_output_dir": str(baseline.output_dir),
            "baseline_requested_max_steps": baseline.requested_max_steps,
            "baseline_completed_steps": baseline.completed_steps,
            "baseline_final_eval_loss": baseline.final_eval_loss,
            "baseline_final_eval_perplexity": baseline.final_eval_perplexity,
            "delta_eval_loss": None
            if summary.final_eval_loss is None or baseline.final_eval_loss is None
            else round(summary.final_eval_loss - baseline.final_eval_loss, 12),
            "delta_eval_perplexity": None
            if summary.final_eval_perplexity is None or baseline.final_eval_perplexity is None
            else round(summary.final_eval_perplexity - baseline.final_eval_perplexity, 12),
            "delta_completed_steps": None
            if summary.completed_steps is None or baseline.completed_steps is None
            else summary.completed_steps - baseline.completed_steps,
        }

    return {"run": run, "baselines": comparisons}


def render_markdown(result: dict[str, Any]) -> str:
    run = result["run"]
    lines = [
        f"# Run Summary: {run['output_dir']}",
        "",
        f"- model_name: `{run['model_name']}`",
        f"- device: `{run['device']}`",
        f"- world_size: `{run['world_size']}`",
        f"- train_examples: `{run['train_examples']}`",
        f"- eval_examples: `{run['eval_examples']}`",
        f"- optimizer_steps_per_epoch: `{run['optimizer_steps_per_epoch']}`",
        f"- max_available_steps: `{run['max_available_steps']}`",
        f"- requested_max_steps: `{run['requested_max_steps']}`",
        f"- completed_steps: `{run['completed_steps']}`",
        f"- final_eval_loss: `{run['final_eval_loss']}`",
        f"- final_eval_perplexity: `{run['final_eval_perplexity']}`",
    ]
    if run.get("signature_sha256"):
        lines.append(f"- signature_sha256: `{run['signature_sha256']}`")

    lines.extend(["", "## Baseline Deltas"])
    for name, baseline in result["baselines"].items():
        lines.extend(
            [
                f"- `{name}`",
                f"  - baseline_final_eval_loss: `{baseline['baseline_final_eval_loss']}`",
                f"  - baseline_final_eval_perplexity: `{baseline['baseline_final_eval_perplexity']}`",
                f"  - baseline_requested_max_steps: `{baseline['baseline_requested_max_steps']}`",
                f"  - baseline_completed_steps: `{baseline['baseline_completed_steps']}`",
                f"  - delta_eval_loss: `{baseline['delta_eval_loss']}`",
                f"  - delta_eval_perplexity: `{baseline['delta_eval_perplexity']}`",
                f"  - delta_completed_steps: `{baseline['delta_completed_steps']}`",
            ]
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir
    summary = load_summary_for_dir(output_dir)
    baselines = resolve_baselines(args.baseline)
    baseline_summaries = {name: load_summary_for_dir(metrics_path_for(path).parent) for name, path in baselines.items()}
    result = summarize(summary, baseline_summaries)

    if args.markdown:
        print(render_markdown(result), end="")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
