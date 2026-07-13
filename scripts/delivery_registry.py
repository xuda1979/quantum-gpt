from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MODEL_REGISTRY_INDEX = Path("artifacts/model-registry/index.json")
DELIVERIES_DIR = Path("artifacts/deliveries")
PAPERS_INDEX = Path("research/papers/index.json")
CANONICAL_REPORT_TEX = Path("research/RESEARCH-REPORT.tex")
CANONICAL_REPORT_PDF = Path("research/build/RESEARCH-REPORT.pdf")


@dataclass(frozen=True)
class RegistryIssue:
    scope: str
    identifier: str
    problem: str
    target: str

    def as_dict(self) -> dict[str, str]:
        return {
            "scope": self.scope,
            "identifier": self.identifier,
            "problem": self.problem,
            "target": self.target,
        }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _relative(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _artifact_record(root: Path, rel_path: str | Path) -> dict[str, Any]:
    path = rel_path if isinstance(rel_path, Path) else root / rel_path
    record = {
        "path": _relative(root, path),
        "exists": path.exists(),
    }
    if path.exists():
        stat = path.stat()
        record["bytes"] = stat.st_size
        record["modified_at_utc"] = datetime.fromtimestamp(
            stat.st_mtime, tz=timezone.utc
        ).isoformat()
    return record


def _append_missing_issue(
    issues: list[RegistryIssue], *, scope: str, identifier: str, problem: str, path_text: str
) -> None:
    issues.append(
        RegistryIssue(scope=scope, identifier=identifier, problem=problem, target=path_text)
    )


def _check_path_reference(
    root: Path,
    issues: list[RegistryIssue],
    *,
    scope: str,
    identifier: str,
    problem: str,
    path_text: str | None,
    expect_dir: bool | None = None,
) -> dict[str, Any] | None:
    if not path_text:
        _append_missing_issue(
            issues, scope=scope, identifier=identifier, problem=problem, path_text="<missing>"
        )
        return None

    path = root / path_text
    record = _artifact_record(root, path)
    if not path.exists():
        _append_missing_issue(
            issues, scope=scope, identifier=identifier, problem=problem, path_text=path_text
        )
        return record
    if expect_dir is True and not path.is_dir():
        _append_missing_issue(
            issues,
            scope=scope,
            identifier=identifier,
            problem=f"{problem}:expected-directory",
            path_text=path_text,
        )
    if expect_dir is False and not path.is_file():
        _append_missing_issue(
            issues,
            scope=scope,
            identifier=identifier,
            problem=f"{problem}:expected-file",
            path_text=path_text,
        )
    return record


def _find_adapter_weight_path(adapter_dir: Path) -> Path | None:
    for candidate in ("adapter_model.safetensors", "adapter_model.bin"):
        path = adapter_dir / candidate
        if path.exists():
            return path
    return None


def build_model_registry_section(root: Path, issues: list[RegistryIssue]) -> dict[str, Any]:
    index_path = root / MODEL_REGISTRY_INDEX
    index_record = _artifact_record(root, index_path)
    if not index_path.exists():
        _append_missing_issue(
            issues,
            scope="model_registry",
            identifier="index",
            problem="missing-index",
            path_text=str(MODEL_REGISTRY_INDEX),
        )
        return {"index": index_record, "runs": []}

    payload = load_json(index_path)
    runs = payload.get("runs") or []
    run_records: list[dict[str, Any]] = []
    for run in runs:
        identifier = str(run.get("label") or run.get("output_dir") or "unknown-run")
        archive_path = str(run.get("archive_path") or "")
        output_dir = str(run.get("output_dir") or "")
        record = {
            "label": run.get("label"),
            "base_model": run.get("base_model"),
            "training_method": run.get("training_method"),
            "archive": _check_path_reference(
                root,
                issues,
                scope="model_registry",
                identifier=identifier,
                problem="missing-archive",
                path_text=archive_path,
                expect_dir=False,
            ),
            "output_dir": _check_path_reference(
                root,
                issues,
                scope="model_registry",
                identifier=identifier,
                problem="missing-output-dir",
                path_text=output_dir,
                expect_dir=True,
            ),
        }
        run_records.append(record)

    return {
        "index": index_record,
        "archive_version": payload.get("archive_version"),
        "run_count": len(run_records),
        "runs": run_records,
    }


def _build_delivery_manifest_entry(
    root: Path, issues: list[RegistryIssue], manifest_path: Path, payload: dict[str, Any]
) -> dict[str, Any]:
    identifier = manifest_path.stem
    adapter_dir_text = str(payload.get("adapter_dir") or "")
    adapter_dir_record = _check_path_reference(
        root,
        issues,
        scope="deliveries",
        identifier=identifier,
        problem="missing-adapter-dir",
        path_text=adapter_dir_text,
        expect_dir=True,
    )
    adapter_weight_record = None
    if adapter_dir_text:
        adapter_dir = root / adapter_dir_text
        weight_path = _find_adapter_weight_path(adapter_dir)
        if weight_path is None:
            _append_missing_issue(
                issues,
                scope="deliveries",
                identifier=identifier,
                problem="missing-adapter-weights",
                path_text=str(Path(adapter_dir_text) / "adapter_model.safetensors"),
            )
            adapter_weight_record = {
                "path": str(Path(adapter_dir_text) / "adapter_model.safetensors"),
                "exists": False,
            }
        else:
            adapter_weight_record = _artifact_record(root, weight_path)
    return {
        "manifest": _artifact_record(root, manifest_path),
        "artifact": _check_path_reference(
            root,
            issues,
            scope="deliveries",
            identifier=identifier,
            problem="missing-delivery-artifact",
            path_text=str(payload.get("artifact") or ""),
            expect_dir=False,
        ),
        "adapter_dir": adapter_dir_record,
        "adapter_weights": adapter_weight_record,
        "metrics_file": _check_path_reference(
            root,
            issues,
            scope="deliveries",
            identifier=identifier,
            problem="missing-metrics-file",
            path_text=str(payload.get("metrics_file") or ""),
            expect_dir=False,
        ),
        "report_file": _check_path_reference(
            root,
            issues,
            scope="deliveries",
            identifier=identifier,
            problem="missing-report-file",
            path_text=str(payload.get("report_file") or ""),
            expect_dir=False,
        ),
        "base_model": _check_path_reference(
            root,
            issues,
            scope="deliveries",
            identifier=identifier,
            problem="missing-base-model",
            path_text=str(payload.get("base_model") or ""),
            expect_dir=True,
        ),
        "verified_run": payload.get("verified_run") or {},
    }


def _build_handoff_entry(
    root: Path, issues: list[RegistryIssue], manifest_path: Path, payload: dict[str, Any]
) -> dict[str, Any]:
    identifier = manifest_path.parent.name
    adapter = payload.get("adapter") or {}
    eval_slice = payload.get("eval_slice") or {}
    script_inputs = payload.get("script_inputs") or []
    adapter_path_text = str(adapter.get("path") or "")
    adapter_dir_record = _check_path_reference(
        root,
        issues,
        scope="deliveries",
        identifier=identifier,
        problem="missing-handoff-adapter-dir",
        path_text=adapter_path_text,
        expect_dir=True,
    )
    adapter_weight_record = None
    if adapter_path_text:
        adapter_dir = root / adapter_path_text
        weight_path = _find_adapter_weight_path(adapter_dir)
        if weight_path is None:
            _append_missing_issue(
                issues,
                scope="deliveries",
                identifier=identifier,
                problem="missing-handoff-adapter-weights",
                path_text=str(Path(adapter_path_text) / "adapter_model.safetensors"),
            )
            adapter_weight_record = {
                "path": str(Path(adapter_path_text) / "adapter_model.safetensors"),
                "exists": False,
            }
        else:
            adapter_weight_record = _artifact_record(root, weight_path)

    script_input_records = []
    for item in script_inputs:
        script_input_records.append(
            _check_path_reference(
                root,
                issues,
                scope="deliveries",
                identifier=identifier,
                problem="missing-handoff-script-input",
                path_text=str(item.get("path") or ""),
                expect_dir=False,
            )
        )

    return {
        "manifest": _artifact_record(root, manifest_path),
        "base_model": _check_path_reference(
            root,
            issues,
            scope="deliveries",
            identifier=identifier,
            problem="missing-handoff-base-model",
            path_text=str(payload.get("base_model") or ""),
            expect_dir=True,
        ),
        "adapter_dir": adapter_dir_record,
        "adapter_weights": adapter_weight_record,
        "eval_slice": _check_path_reference(
            root,
            issues,
            scope="deliveries",
            identifier=identifier,
            problem="missing-handoff-eval-slice",
            path_text=str(eval_slice.get("path") or ""),
            expect_dir=False,
        ),
        "script_inputs": script_input_records,
        "blocked_command": (payload.get("blocker") or {}).get("blocked_command"),
    }


def build_deliveries_section(root: Path, issues: list[RegistryIssue]) -> dict[str, Any]:
    deliveries_dir = root / DELIVERIES_DIR
    deliveries_record = _artifact_record(root, deliveries_dir)
    if not deliveries_dir.exists():
        _append_missing_issue(
            issues,
            scope="deliveries",
            identifier="root",
            problem="missing-deliveries-dir",
            path_text=str(DELIVERIES_DIR),
        )
        return {"root": deliveries_record, "delivery_manifests": [], "handoffs": []}

    delivery_manifests: list[dict[str, Any]] = []
    for manifest_path in sorted(deliveries_dir.glob("*.json")):
        payload = load_json(manifest_path)
        delivery_manifests.append(
            _build_delivery_manifest_entry(root, issues, manifest_path, payload)
        )

    handoffs: list[dict[str, Any]] = []
    for manifest_path in sorted(deliveries_dir.glob("*/handoff_manifest.json")):
        payload = load_json(manifest_path)
        handoffs.append(_build_handoff_entry(root, issues, manifest_path, payload))

    return {
        "root": deliveries_record,
        "delivery_manifest_count": len(delivery_manifests),
        "handoff_count": len(handoffs),
        "delivery_manifests": delivery_manifests,
        "handoffs": handoffs,
    }


def build_papers_section(root: Path, issues: list[RegistryIssue]) -> dict[str, Any]:
    index_path = root / PAPERS_INDEX
    index_record = _artifact_record(root, index_path)
    if not index_path.exists():
        _append_missing_issue(
            issues,
            scope="papers",
            identifier="index",
            problem="missing-index",
            path_text=str(PAPERS_INDEX),
        )
        return {"index": index_record, "papers": []}

    payload = load_json(index_path)
    paper_records: list[dict[str, Any]] = []
    for paper in payload.get("papers") or []:
        paper_id = str(paper.get("paper_id") or "unknown-paper")
        paper_dir = Path("research/papers") / paper_id
        paper_md = paper_dir / "paper.md"
        paper_records.append(
            {
                "paper_id": paper_id,
                "title": paper.get("title"),
                "type": paper.get("type"),
                "has_plugin": bool(paper.get("has_plugin")),
                "directory": _check_path_reference(
                    root,
                    issues,
                    scope="papers",
                    identifier=paper_id,
                    problem="missing-paper-directory",
                    path_text=str(paper_dir),
                    expect_dir=True,
                ),
                "paper_md": _check_path_reference(
                    root,
                    issues,
                    scope="papers",
                    identifier=paper_id,
                    problem="missing-paper-markdown",
                    path_text=str(paper_md),
                    expect_dir=False,
                ),
            }
        )

    return {
        "index": index_record,
        "paper_count": len(paper_records),
        "papers": paper_records,
    }


def build_canonical_report_section(root: Path, issues: list[RegistryIssue]) -> dict[str, Any]:
    return {
        "tex": _check_path_reference(
            root,
            issues,
            scope="canonical_report",
            identifier="research-report",
            problem="missing-report-tex",
            path_text=str(CANONICAL_REPORT_TEX),
            expect_dir=False,
        ),
        "pdf": _check_path_reference(
            root,
            issues,
            scope="canonical_report",
            identifier="research-report",
            problem="missing-report-pdf",
            path_text=str(CANONICAL_REPORT_PDF),
            expect_dir=False,
        ),
    }


def build_delivery_registry(root: Path = ROOT) -> dict[str, Any]:
    issues: list[RegistryIssue] = []
    model_registry = build_model_registry_section(root, issues)
    deliveries = build_deliveries_section(root, issues)
    papers = build_papers_section(root, issues)
    canonical_report = build_canonical_report_section(root, issues)

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "workspace_root": str(root),
        "summary": {
            "model_run_count": model_registry.get("run_count", 0),
            "delivery_manifest_count": deliveries.get("delivery_manifest_count", 0),
            "handoff_count": deliveries.get("handoff_count", 0),
            "paper_count": papers.get("paper_count", 0),
            "issue_count": len(issues),
        },
        "model_registry": model_registry,
        "deliveries": deliveries,
        "papers": papers,
        "canonical_report": canonical_report,
        "issues": [issue.as_dict() for issue in issues],
        "ok": not issues,
    }


def write_delivery_registry(
    payload: dict[str, Any], out_path: Path = ROOT / "artifacts/delivery-registry/index.json"
) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out_path
