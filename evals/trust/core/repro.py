"""Reproduction recipe builder and verifier.

A *reproduction recipe* is a JSON document that captures every input
needed to re-run an evaluation run and obtain bit-identical verdicts:

  - the pinned suite (suite_hash + path to suite.lock.json)
  - the model (base path, adapter path, model kind, hash if available)
  - the prompt template (style, version, body hash)
  - sampling parameters (k, temperature, seed, max_new_tokens)
  - environment (python version, platform, dependency hashes)
  - the harness version (git commit of evals/trust/ at run time)

The recipe is written to ``<run_dir>/recipe.json`` and its hash is the
``run_hash`` recorded in the ledger. ``reproduce`` re-runs the recipe
and asserts that every per-sample verdict is identical.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import hashing


def python_version() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def platform_str() -> str:
    return f"{platform.system()} {platform.machine()} {platform.python_implementation()}"


def git_commit(repo: str | Path) -> str | None:
    repo = Path(repo)
    if not (repo / ".git").is_dir():
        return None
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except Exception:
        pass
    return None


def pip_freeze(python: str | None = None) -> list[str]:
    """Return a sorted list of ``package==version`` strings for the env."""
    py = python or sys.executable
    try:
        out = subprocess.run(
            [py, "-m", "pip", "freeze"], capture_output=True, text=True, timeout=30
        )
        if out.returncode == 0:
            return sorted(out.stdout.strip().splitlines())
    except Exception:
        pass
    return []


@dataclass
class Recipe:
    suite_hash: str
    suite_lock_path: str
    model_label: str
    model_base_path: str
    model_base_hash: str | None
    model_adapter_path: str | None
    model_adapter_hash: str | None
    model_kind: str
    prompt_style: str
    prompt_version: str
    prompt_template_hash: str
    k: int
    temperature: float | None
    seed: int
    max_new_tokens: int | None
    python_version: str
    platform: str
    git_commit: str | None
    pip_freeze_hash: str | None
    harness_version: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "suite_hash": self.suite_hash,
            "suite_lock_path": self.suite_lock_path,
            "model": {
                "label": self.model_label,
                "base_path": self.model_base_path,
                "base_hash": self.model_base_hash,
                "adapter_path": self.model_adapter_path,
                "adapter_hash": self.model_adapter_hash,
                "kind": self.model_kind,
            },
            "prompt": {
                "style": self.prompt_style,
                "version": self.prompt_version,
                "template_hash": self.prompt_template_hash,
            },
            "sampling": {
                "k": self.k,
                "temperature": self.temperature,
                "seed": self.seed,
                "max_new_tokens": self.max_new_tokens,
            },
            "environment": {
                "python_version": self.python_version,
                "platform": self.platform,
                "git_commit": self.git_commit,
                "pip_freeze_hash": self.pip_freeze_hash,
            },
            "harness_version": self.harness_version,
        }

    def hash(self) -> str:
        return hashing.hash_json(self.to_dict())


def build_recipe(
    *,
    suite_hash: str,
    suite_lock_path: str,
    model_label: str,
    model_base_path: str,
    model_base_hash: str | None,
    model_adapter_path: str | None,
    model_adapter_hash: str | None,
    model_kind: str,
    prompt_style: str,
    prompt_version: str,
    prompt_template_hash: str,
    k: int,
    temperature: float | None,
    seed: int,
    max_new_tokens: int | None,
    git_repo: str | Path | None = None,
    harness_version: str = "evals.trust.v1",
    include_pip_freeze: bool = False,
) -> Recipe:
    pf_hash = None
    if include_pip_freeze:
        pf_hash = hashing.hash_json(pip_freeze())
    return Recipe(
        suite_hash=suite_hash,
        suite_lock_path=suite_lock_path,
        model_label=model_label,
        model_base_path=model_base_path,
        model_base_hash=model_base_hash,
        model_adapter_path=model_adapter_path,
        model_adapter_hash=model_adapter_hash,
        model_kind=model_kind,
        prompt_style=prompt_style,
        prompt_version=prompt_version,
        prompt_template_hash=prompt_template_hash,
        k=k,
        temperature=temperature,
        seed=seed,
        max_new_tokens=max_new_tokens,
        python_version=python_version(),
        platform=platform_str(),
        git_commit=git_commit(git_repo) if git_repo else None,
        pip_freeze_hash=pf_hash,
        harness_version=harness_version,
    )


def write_recipe(recipe: Recipe, out_path: str | Path) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(recipe.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return out


def read_recipe(path: str | Path) -> Recipe:
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    m = d["model"]; p = d["prompt"]; s = d["sampling"]; e = d["environment"]
    return Recipe(
        suite_hash=d["suite_hash"],
        suite_lock_path=d["suite_lock_path"],
        model_label=m["label"],
        model_base_path=m["base_path"],
        model_base_hash=m.get("base_hash"),
        model_adapter_path=m.get("adapter_path"),
        model_adapter_hash=m.get("adapter_hash"),
        model_kind=m["kind"],
        prompt_style=p["style"],
        prompt_version=p["version"],
        prompt_template_hash=p["template_hash"],
        k=s["k"],
        temperature=s.get("temperature"),
        seed=s["seed"],
        max_new_tokens=s.get("max_new_tokens"),
        python_version=e["python_version"],
        platform=e["platform"],
        git_commit=e.get("git_commit"),
        pip_freeze_hash=e.get("pip_freeze_hash"),
        harness_version=d["harness_version"],
    )


def compare_recipes(a: Recipe, b: Recipe) -> dict[str, Any]:
    """Return a diff between two recipes (used by `reproduce`)."""
    diffs: list[dict] = []
    da, db = a.to_dict(), b.to_dict()
    for top in ("suite_hash", "model", "prompt", "sampling", "environment", "harness_version"):
        if da[top] != db[top]:
            diffs.append({"field": top, "expected": da[top], "actual": db[top]})
    return {"identical": not diffs, "diffs": diffs}
