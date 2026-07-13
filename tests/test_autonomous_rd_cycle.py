from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import scripts.run_autonomous_rd_cycle as autonomous_rd_cycle
from scripts.run_autonomous_rd_cycle import (
    TARGETS,
    build_commands,
    build_gates,
    build_moe_expert_routing_prep,
    build_stakeholder_questions,
    load_cached_snapshot_verify_summary,
    load_paper_router_plan,
)


def test_parse_args_defaults_to_fast_verified_lane(monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["run_autonomous_rd_cycle.py"])
    args = autonomous_rd_cycle.parse_args()
    assert args.target == "omnicoder9b"


def test_build_commands_defaults_to_gemma_targets() -> None:
    target = TARGETS["gemma4-31b-it"]
    commands = build_commands(target)
    assert "google/gemma-4-31B-it" in commands["gemma_audit"]
    assert "--model-name models/gemma-4-31B-it" in commands["gemma_smoke"]
    assert "scripts/ai2_sync_model_from_s3.sh gemma-4-31B-it" == commands["remote_model_sync"]
    assert (
        "scripts/relay_model_snapshot_to_s3.sh gemma-4-31B-it" == commands["gemma_snapshot_relay"]
    )
    assert (
        "scripts/queue_ai2_timeboxed_pipeline.sh --target gemma4-31b-it --iteration-profile fast --visible-devices 6,7 --nproc-per-node 2 --required-idle-npus 2 --stage-only"
        == commands["remote_job_queue"]
    )
    assert (
        "scripts/queue_ai2_timeboxed_pipeline.sh --target omnicoder9b --iteration-profile fast --visible-devices 6,7 --nproc-per-node 2 --required-idle-npus 2 --stage-only"
        == commands["fallback_remote_job_queue"]
    )


def test_build_commands_support_gemma_26b_a4b_target() -> None:
    target = TARGETS["gemma4-26b-a4b-it"]
    commands = build_commands(target)
    assert "google/gemma-4-26B-A4B-it" in commands["gemma_audit"]
    assert (
        commands["gemma_python_probe"]
        == "python3 scripts/resolve_python_interpreter.py --min-version 3.10"
    )
    assert "--print-path" in commands["gemma_runtime_bootstrap"]
    assert "--print-path" in commands["gemma_smoke"]
    assert "--model-name models/gemma-4-26B-A4B-it" in commands["gemma_smoke"]
    assert "scripts/ai2_sync_model_from_s3.sh gemma-4-26B-A4B-it" == commands["remote_model_sync"]
    assert (
        "render_timeboxed_scaleup_commands.py --target gemma4-26b-a4b-it"
        in commands["paper_router_plan"]
    )
    assert (
        "scripts/queue_ai2_timeboxed_pipeline.sh --target gemma4-26b-a4b-it --iteration-profile fast --visible-devices 6,7 --nproc-per-node 2 --required-idle-npus 2 --stage-only"
        == commands["remote_job_queue"]
    )


def test_load_paper_router_plan_reads_command_sheet_and_dataset_counts(
    tmp_path: Path, monkeypatch
) -> None:
    target = TARGETS["gemma4-26b-a4b-it"]
    artifact_path = tmp_path / "artifacts" / f"{target.target_id}-paper-router-command-sheet.txt"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    train_path = (
        tmp_path
        / "data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_train.jsonl"
    )
    eval_path = (
        tmp_path
        / "data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_valid.jsonl"
    )
    train_path.parent.mkdir(parents=True, exist_ok=True)
    train_path.write_text('{"messages":[]}\n{"messages":[]}\n', encoding="utf-8")
    eval_path.write_text('{"messages":[]}\n', encoding="utf-8")
    artifact_path.write_text(
        "# Timeboxed 8-NPU Scale-Up Command Sheet\n\n## JSON\n"
        + json.dumps(
            {
                "resolved_config": {
                    "paper_output_dir": "data/generated/quantum-paper-router-warmup-v1",
                    "paper_train_file": "data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_train.jsonl",
                    "paper_eval_file": "data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_valid.jsonl",
                },
                "paper_dataset": "python3 scripts/build_paper_sft_dataset.py paper --output-dir data/generated/quantum-paper-router-warmup-v1 --dataset-name quantum_paper_router_warmup",
                "paper_router_warmup": "torchrun --nproc_per_node=8 training/qwen_sft_peft.py --model-name models/gemma-4-26B-A4B-it",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(autonomous_rd_cycle, "ROOT", tmp_path)
    plan = load_paper_router_plan(target)
    assert plan is not None
    assert plan["paper_train_rows"] == 2
    assert plan["paper_eval_rows"] == 1
    assert plan["paper_dataset_ready"] is True
    assert "qwen_sft_peft.py" in plan["paper_router_warmup_command"]


def test_build_gates_includes_gemma_trainer_backend_gate() -> None:
    target = TARGETS["gemma4-31b-it"]
    gates = build_gates(target)
    gate_names = [gate["gate"] for gate in gates]
    assert "gemma_local_python_gate" in gate_names
    assert "gemma_runtime_bootstrap_gate" in gate_names
    assert "gemma_trainer_backend_gate" in gate_names
    assert "dataset_integrity_gate" in gate_names
    assert "paper_router_warmup_gate" in gate_names


def test_stakeholder_questions_cover_eval_and_blocker_concerns() -> None:
    target = TARGETS["gemma4-31b-it"]
    questions = build_stakeholder_questions(target)
    rendered = "\n".join(item["question"] + "\n" + item["answer"] for item in questions)
    assert "eval set" in rendered
    assert "Gemma 4" in rendered
    assert "blocker" in rendered.lower()
    assert "ai2 access is repaired" in rendered
    assert "runtime bootstrap" in rendered
    assert "progress percentage" in rendered
    assert "fallback lane" in rendered


def test_derive_cycle_state_marks_partial_snapshot_as_in_flight(
    tmp_path: Path, monkeypatch
) -> None:
    target = TARGETS["gemma4-31b-it"]
    local_snapshot = tmp_path / target.local_model_dir
    download_dir = local_snapshot / ".cache" / "huggingface" / "download"
    download_dir.mkdir(parents=True, exist_ok=True)
    (local_snapshot / "config.json").write_text('{"model_type":"gemma4"}\n', encoding="utf-8")
    (local_snapshot / "model.safetensors.index.json").write_text(
        '{"metadata":{"total_size":4096},"weight_map":{"foo":"model-00001-of-00002.safetensors"}}\n',
        encoding="utf-8",
    )
    (local_snapshot / "processor_config.json").write_text("{}\n", encoding="utf-8")
    (download_dir / "model.safetensors.incomplete").write_bytes(b"x" * 1024)

    monkeypatch.setattr(autonomous_rd_cycle, "ROOT", tmp_path)

    cycle_state = autonomous_rd_cycle.derive_cycle_state(target, build_commands(target), [])
    stage_by_name = {stage["stage"]: stage for stage in cycle_state["stages"]}

    assert "gemma_snapshot_acquire" in stage_by_name
    assert "in flight" in stage_by_name["gemma_snapshot_acquire"]["reason"].lower()
    assert (
        stage_by_name["gemma_snapshot_acquire"]["evidence"]["has_incomplete_weight_files"] is True
    )
    assert (
        stage_by_name["gemma_snapshot_acquire"]["evidence"]["observed_weight_progress_percent"]
        == "25.0%"
    )
    assert stage_by_name["gemma_snapshot_acquire"]["evidence"]["recent_download_activity"] is True
    assert (
        stage_by_name["gemma_snapshot_acquire"]["parallel_action"]
        == build_commands(target)["gemma_snapshot_relay"]
    )
    assert (
        stage_by_name["remote_launcher_gate"]["evidence"]["launcher_path"]
        == "scripts/queue_ai2_timeboxed_pipeline.sh"
    )
    assert cycle_state["fallback_ready"] is False


def test_derive_cycle_state_blocks_on_missing_local_python_for_gemma(
    tmp_path: Path, monkeypatch
) -> None:
    target = TARGETS["gemma4-26b-a4b-it"]
    snapshot_dir = tmp_path / target.local_model_dir
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    for rel_path, body in {
        "config.json": '{"model_type":"gemma4"}\n',
        "processor_config.json": "{}\n",
        "chat_template.jinja": "{{ messages }}\n",
        "tokenizer.json": "{}\n",
        "tokenizer_config.json": '{"tokenizer_class":"PreTrainedTokenizerFast"}\n',
        "model.safetensors.index.json": '{"metadata":{"total_size":8},"weight_map":{"a":"model-00001-of-00002.safetensors","b":"model-00002-of-00002.safetensors"}}\n',
    }.items():
        (snapshot_dir / rel_path).write_text(body, encoding="utf-8")
    (snapshot_dir / "model-00001-of-00002.safetensors").write_bytes(b"aaaa")
    (snapshot_dir / "model-00002-of-00002.safetensors").write_bytes(b"bbbb")

    monkeypatch.setattr(autonomous_rd_cycle, "ROOT", tmp_path)
    monkeypatch.setattr(
        autonomous_rd_cycle,
        "resolve_python_interpreter",
        lambda: {
            "status": "error",
            "minimum_version": "3.10",
            "selected_path": None,
            "selected_version": None,
            "brew_binary": "/Users/daxu/homebrew/bin/brew",
            "install_command": "/Users/daxu/homebrew/bin/brew install python@3.11",
            "candidates": [],
            "error": "missing",
        },
    )

    cycle_state = autonomous_rd_cycle.derive_cycle_state(target, build_commands(target), [])
    stage_by_name = {stage["stage"]: stage for stage in cycle_state["stages"]}

    assert stage_by_name["gemma_local_python_gate"]["status"] == "blocked"
    assert "python@3.11" in stage_by_name["gemma_local_python_gate"]["reason"]
    assert cycle_state["fallback_ready"] is False


def test_build_moe_expert_routing_prep_waits_for_snapshot_completion(
    tmp_path: Path, monkeypatch
) -> None:
    target = TARGETS["gemma4-26b-a4b-it"]
    local_snapshot = tmp_path / target.local_model_dir
    download_dir = local_snapshot / ".cache" / "huggingface" / "download"
    download_dir.mkdir(parents=True, exist_ok=True)
    (local_snapshot / "config.json").write_text('{"model_type":"gemma4"}\n', encoding="utf-8")
    (local_snapshot / "model.safetensors.index.json").write_text(
        '{"metadata":{"total_size":4096},"weight_map":{"foo":"model-00001-of-00002.safetensors"}}\n',
        encoding="utf-8",
    )
    (download_dir / "model.safetensors.incomplete").write_bytes(b"x" * 1024)

    monkeypatch.setattr(autonomous_rd_cycle, "ROOT", tmp_path)

    prep = build_moe_expert_routing_prep(target)
    assert prep["strategy"] == "router_warmup_then_frequency_guided_esft"
    assert prep["state"] == "waiting_for_snapshot_completion"
    assert prep["ready"] is False
    assert "inspect_moe_target_modules.py" in prep["inspection_command"]


def test_build_moe_expert_routing_prep_uses_recorded_manifest_when_available(
    tmp_path: Path, monkeypatch
) -> None:
    target = TARGETS["gemma4-26b-a4b-it"]
    manifest_path = tmp_path / "artifacts" / f"{target.target_id}_moe_target_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            {
                "selection_mode": "structural-discovery-only",
                "router_module_names": ["model.layers.0.block_sparse_moe.router"],
                "expert_index_pool": ["0", "1", "2"],
                "first_pass_expert_budget": 4,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    command_sheet_path = (
        tmp_path / "artifacts" / f"{target.target_id}-paper-router-command-sheet.txt"
    )
    command_sheet_path.write_text(
        "# Timeboxed 8-NPU Scale-Up Command Sheet\n\n## JSON\n"
        + json.dumps(
            {
                "resolved_config": {
                    "paper_output_dir": "data/generated/quantum-paper-router-warmup-v1",
                    "paper_train_file": "data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_train.jsonl",
                    "paper_eval_file": "data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_valid.jsonl",
                },
                "paper_dataset": "python3 scripts/build_paper_sft_dataset.py paper --output-dir data/generated/quantum-paper-router-warmup-v1 --dataset-name quantum_paper_router_warmup",
                "paper_router_warmup": "torchrun --nproc_per_node=8 training/qwen_sft_peft.py --model-name models/gemma-4-26B-A4B-it",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    train_path = (
        tmp_path
        / "data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_train.jsonl"
    )
    eval_path = (
        tmp_path
        / "data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_valid.jsonl"
    )
    train_path.parent.mkdir(parents=True, exist_ok=True)
    train_path.write_text('{"messages":[]}\n', encoding="utf-8")
    eval_path.write_text('{"messages":[]}\n', encoding="utf-8")

    monkeypatch.setattr(autonomous_rd_cycle, "ROOT", tmp_path)

    prep = build_moe_expert_routing_prep(target)
    assert prep["state"] == "manifest_recorded"
    assert prep["ready"] is True
    assert prep["manifest_summary"]["router_module_count"] == 1
    assert prep["manifest_summary"]["expert_index_pool_size"] == 3
    assert prep["paper_router_ready"] is True


def test_derive_cycle_state_promotes_paper_router_warmup_after_snapshot_verify(
    tmp_path: Path, monkeypatch
) -> None:
    target = TARGETS["gemma4-26b-a4b-it"]
    snapshot_dir = tmp_path / target.local_model_dir
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    for rel_path, body in {
        "config.json": '{"model_type":"gemma4"}\n',
        "processor_config.json": "{}\n",
        "chat_template.jinja": "{{ messages }}\n",
        "tokenizer.json": "{}\n",
        "tokenizer_config.json": '{"tokenizer_class":"PreTrainedTokenizerFast"}\n',
        "model.safetensors.index.json": '{"metadata":{"total_size":8},"weight_map":{"a":"model-00001-of-00002.safetensors","b":"model-00002-of-00002.safetensors"}}\n',
    }.items():
        path = snapshot_dir / rel_path
        path.write_text(body, encoding="utf-8")
    (snapshot_dir / "model-00001-of-00002.safetensors").write_bytes(b"aaaa")
    (snapshot_dir / "model-00002-of-00002.safetensors").write_bytes(b"bbbb")

    handoff_path = tmp_path / "artifacts" / f"{target.target_id}-local-snapshot-handoff.json"
    handoff_path.parent.mkdir(parents=True, exist_ok=True)
    handoff_path.write_text(
        json.dumps(
            {
                "status": "ok",
                "model_id": target.model_id,
                "verify_summary": {
                    "status": "ok",
                    "snapshot_dir": str(snapshot_dir),
                    "present_weight_files": [
                        "model-00001-of-00002.safetensors",
                        "model-00002-of-00002.safetensors",
                    ],
                    "indexed_weight_shards": [
                        "model-00001-of-00002.safetensors",
                        "model-00002-of-00002.safetensors",
                    ],
                    "config_model_type": "gemma4",
                    "config_architectures": ["Gemma4ForConditionalGeneration"],
                    "requires_processor_artifacts": True,
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    audit_artifact = tmp_path / target.audit_artifact
    audit_artifact.parent.mkdir(parents=True, exist_ok=True)
    audit_artifact.write_text(
        json.dumps(
            {
                "timestamp_utc": "2026-04-08T10:24:48.892073+00:00",
                "model_id": target.model_id,
                "status": "ok",
                "family_evidence": {"matched": True},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    command_sheet_path = (
        tmp_path / "artifacts" / f"{target.target_id}-paper-router-command-sheet.txt"
    )
    command_sheet_path.write_text(
        "# Timeboxed 8-NPU Scale-Up Command Sheet\n\n## JSON\n"
        + json.dumps(
            {
                "resolved_config": {
                    "paper_output_dir": "data/generated/quantum-paper-router-warmup-v1",
                    "paper_train_file": "data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_train.jsonl",
                    "paper_eval_file": "data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_valid.jsonl",
                },
                "paper_dataset": "python3 scripts/build_paper_sft_dataset.py paper --output-dir data/generated/quantum-paper-router-warmup-v1 --dataset-name quantum_paper_router_warmup",
                "paper_router_warmup": "torchrun --nproc_per_node=8 training/qwen_sft_peft.py --model-name models/gemma-4-26B-A4B-it --train-file data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_train.jsonl",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    train_path = (
        tmp_path
        / "data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_train.jsonl"
    )
    eval_path = (
        tmp_path
        / "data/generated/quantum-paper-router-warmup-v1/messages/quantum_paper_router_warmup_messages_valid.jsonl"
    )
    train_path.parent.mkdir(parents=True, exist_ok=True)
    train_path.write_text('{"messages":[]}\n{"messages":[]}\n', encoding="utf-8")
    eval_path.write_text('{"messages":[]}\n', encoding="utf-8")

    monkeypatch.setattr(autonomous_rd_cycle, "ROOT", tmp_path)
    monkeypatch.setattr(
        autonomous_rd_cycle,
        "resolve_python_interpreter",
        lambda: {
            "status": "ok",
            "minimum_version": "3.10",
            "selected_path": str(tmp_path / ".local-python/cpython-3.11.15/bin/python3.11"),
            "selected_version": "3.11.15",
            "brew_binary": "/Users/daxu/homebrew/bin/brew",
            "install_command": None,
            "candidates": [],
        },
    )
    commands = build_commands(target)
    cycle_state = autonomous_rd_cycle.derive_cycle_state(
        target,
        commands,
        [
            {
                "name": "local_eval_gate",
                "ok": True,
                "exit_code": 0,
                "stdout": '{"gate":"local_quality_gate","ok":true}\n',
                "stderr": "",
                "command": commands["local_eval_gate"],
            },
            {
                "name": "holdout_integrity",
                "ok": True,
                "exit_code": 0,
                "stdout": '{"gate":"dataset_integrity_gate","ok":true}\n',
                "stderr": "",
                "command": commands["holdout_integrity"],
            },
            {
                "name": "gemma_runtime_bootstrap",
                "ok": True,
                "exit_code": 0,
                "stdout": "installed\n",
                "stderr": "",
                "command": commands["gemma_runtime_bootstrap"],
            },
            {
                "name": "gemma_smoke",
                "ok": True,
                "exit_code": 0,
                "stdout": '{"stage":"trainer_backend_preflight","state":"passed"}\n',
                "stderr": "",
                "command": commands["gemma_smoke"],
            },
        ],
    )

    stage_by_name = {stage["stage"]: stage for stage in cycle_state["stages"]}
    assert cycle_state["current_stage"] == "paper_router_warmup"
    assert cycle_state["next_action"] == commands["paper_router_warmup"]
    assert stage_by_name["paper_router_warmup"]["evidence"]["paper_train_rows"] == 2
    assert stage_by_name["paper_router_warmup"]["evidence"]["paper_eval_rows"] == 1
    assert stage_by_name["paper_router_warmup"]["prerequisites"] == [
        commands["code_sync"],
        commands["remote_code_sync"],
        commands["remote_model_sync"],
    ]


def test_derive_cycle_state_surfaces_runtime_bootstrap_network_failure(
    tmp_path: Path, monkeypatch
) -> None:
    target = TARGETS["gemma4-26b-a4b-it"]
    snapshot_dir = tmp_path / target.local_model_dir
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    for rel_path, body in {
        "config.json": '{"model_type":"gemma4"}\n',
        "processor_config.json": "{}\n",
        "chat_template.jinja": "{{ messages }}\n",
        "tokenizer.json": "{}\n",
        "tokenizer_config.json": '{"tokenizer_class":"PreTrainedTokenizerFast"}\n',
        "model.safetensors.index.json": '{"metadata":{"total_size":8},"weight_map":{"a":"model-00001-of-00002.safetensors","b":"model-00002-of-00002.safetensors"}}\n',
    }.items():
        (snapshot_dir / rel_path).write_text(body, encoding="utf-8")
    (snapshot_dir / "model-00001-of-00002.safetensors").write_bytes(b"aaaa")
    (snapshot_dir / "model-00002-of-00002.safetensors").write_bytes(b"bbbb")

    handoff_path = tmp_path / "artifacts" / f"{target.target_id}-local-snapshot-handoff.json"
    handoff_path.parent.mkdir(parents=True, exist_ok=True)
    handoff_path.write_text(
        json.dumps(
            {
                "status": "ok",
                "model_id": target.model_id,
                "verify_summary": {
                    "status": "ok",
                    "snapshot_dir": str(snapshot_dir),
                    "present_weight_files": [
                        "model-00001-of-00002.safetensors",
                        "model-00002-of-00002.safetensors",
                    ],
                    "indexed_weight_shards": [
                        "model-00001-of-00002.safetensors",
                        "model-00002-of-00002.safetensors",
                    ],
                    "config_model_type": "gemma4",
                    "config_architectures": ["Gemma4ForConditionalGeneration"],
                    "requires_processor_artifacts": True,
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    audit_artifact = tmp_path / target.audit_artifact
    audit_artifact.parent.mkdir(parents=True, exist_ok=True)
    audit_artifact.write_text(
        json.dumps(
            {
                "timestamp_utc": "2026-04-10T01:00:00+00:00",
                "model_id": target.model_id,
                "status": "ok",
                "pipeline_tag": "image-text-to-text",
                "config_model_type": "gemma4",
                "config_architectures": ["Gemma4ForConditionalGeneration"],
                "family_evidence": {"matched": True},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(autonomous_rd_cycle, "ROOT", tmp_path)
    monkeypatch.setattr(
        autonomous_rd_cycle,
        "resolve_python_interpreter",
        lambda: {
            "status": "ok",
            "minimum_version": "3.10",
            "selected_path": str(tmp_path / ".local-python/cpython-3.11.15/bin/python3.11"),
            "selected_version": "3.11.15",
            "brew_binary": "/Users/daxu/homebrew/bin/brew",
            "install_command": None,
            "candidates": [],
        },
    )
    commands = build_commands(target)
    cycle_state = autonomous_rd_cycle.derive_cycle_state(
        target,
        commands,
        [
            {
                "name": "local_eval_gate",
                "ok": True,
                "exit_code": 0,
                "stdout": "ok\n",
                "stderr": "",
                "command": commands["local_eval_gate"],
            },
            {
                "name": "holdout_integrity",
                "ok": True,
                "exit_code": 0,
                "stdout": "ok\n",
                "stderr": "",
                "command": commands["holdout_integrity"],
            },
            {
                "name": "gemma_runtime_bootstrap",
                "ok": False,
                "exit_code": 1,
                "stdout": "",
                "stderr": "fatal: unable to access 'https://github.com/huggingface/transformers.git/': Could not resolve host: github.com\n",
                "command": commands["gemma_runtime_bootstrap"],
            },
        ],
    )

    stage_by_name = {stage["stage"]: stage for stage in cycle_state["stages"]}
    assert cycle_state["current_stage"] == "gemma_runtime_bootstrap"
    assert cycle_state["fallback_ready"] is True
    assert stage_by_name["gemma_runtime_bootstrap"]["status"] == "blocked"
    assert "could not be resolved" in stage_by_name["gemma_runtime_bootstrap"]["reason"].lower()


def test_load_cached_snapshot_verify_summary_uses_handoff_manifest(
    tmp_path: Path, monkeypatch
) -> None:
    target = TARGETS["gemma4-26b-a4b-it"]
    handoff_path = tmp_path / "artifacts" / f"{target.target_id}-local-snapshot-handoff.json"
    handoff_path.parent.mkdir(parents=True, exist_ok=True)
    handoff_path.write_text(
        json.dumps(
            {
                "status": "ok",
                "model_id": target.model_id,
                "verify_summary": {
                    "status": "ok",
                    "snapshot_dir": str(tmp_path / target.local_model_dir),
                    "present_weight_files": [
                        "model-00001-of-00002.safetensors",
                        "model-00002-of-00002.safetensors",
                    ],
                    "indexed_weight_shards": [
                        "model-00001-of-00002.safetensors",
                        "model-00002-of-00002.safetensors",
                    ],
                    "config_model_type": "gemma4",
                    "config_architectures": ["Gemma4ForConditionalGeneration"],
                    "requires_processor_artifacts": True,
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(autonomous_rd_cycle, "ROOT", tmp_path)
    summary = load_cached_snapshot_verify_summary(target)
    assert summary is not None
    assert (
        summary["handoff_manifest"] == f"artifacts/{target.target_id}-local-snapshot-handoff.json"
    )
    assert summary["config_model_type"] == "gemma4"


def test_derive_cycle_state_uses_cached_snapshot_verify_summary(
    tmp_path: Path, monkeypatch
) -> None:
    target = TARGETS["gemma4-26b-a4b-it"]
    snapshot_dir = tmp_path / target.local_model_dir
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    for rel_path, body in {
        "config.json": '{"model_type":"gemma4"}\n',
        "processor_config.json": "{}\n",
        "chat_template.jinja": "{{ messages }}\n",
        "tokenizer.json": "{}\n",
        "tokenizer_config.json": '{"tokenizer_class":"PreTrainedTokenizerFast"}\n',
        "model.safetensors.index.json": '{"metadata":{"total_size":8},"weight_map":{"a":"model-00001-of-00002.safetensors","b":"model-00002-of-00002.safetensors"}}\n',
    }.items():
        path = snapshot_dir / rel_path
        path.write_text(body, encoding="utf-8")
    (snapshot_dir / "model-00001-of-00002.safetensors").write_bytes(b"aaaa")
    (snapshot_dir / "model-00002-of-00002.safetensors").write_bytes(b"bbbb")

    handoff_path = tmp_path / "artifacts" / f"{target.target_id}-local-snapshot-handoff.json"
    handoff_path.parent.mkdir(parents=True, exist_ok=True)
    handoff_path.write_text(
        json.dumps(
            {
                "status": "ok",
                "model_id": target.model_id,
                "verify_summary": {
                    "status": "ok",
                    "snapshot_dir": str(snapshot_dir),
                    "present_weight_files": [
                        "model-00001-of-00002.safetensors",
                        "model-00002-of-00002.safetensors",
                    ],
                    "indexed_weight_shards": [
                        "model-00001-of-00002.safetensors",
                        "model-00002-of-00002.safetensors",
                    ],
                    "config_model_type": "gemma4",
                    "config_architectures": ["Gemma4ForConditionalGeneration"],
                    "requires_processor_artifacts": True,
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(autonomous_rd_cycle, "ROOT", tmp_path)
    cycle_state = autonomous_rd_cycle.derive_cycle_state(target, build_commands(target), [])
    stage_by_name = {stage["stage"]: stage for stage in cycle_state["stages"]}
    assert stage_by_name["gemma_snapshot_verify"]["status"] == "passed"
    assert "cached successful handoff artifact" in stage_by_name["gemma_snapshot_verify"]["reason"]
    assert stage_by_name["gemma_snapshot_verify"]["evidence"]["handoff_manifest"] == (
        f"artifacts/{target.target_id}-local-snapshot-handoff.json"
    )


def test_derive_cycle_state_uses_cached_audit_artifact_when_live_refresh_fails(
    tmp_path: Path, monkeypatch
) -> None:
    target = TARGETS["gemma4-31b-it"]
    local_snapshot = tmp_path / target.local_model_dir
    download_dir = local_snapshot / ".cache" / "huggingface" / "download"
    download_dir.mkdir(parents=True, exist_ok=True)
    (local_snapshot / "config.json").write_text('{"model_type":"gemma4"}\n', encoding="utf-8")
    (local_snapshot / "model.safetensors.index.json").write_text(
        '{"metadata":{"total_size":4096},"weight_map":{"foo":"model-00001-of-00002.safetensors"}}\n',
        encoding="utf-8",
    )
    (download_dir / "model.safetensors.incomplete").write_bytes(b"x" * 1024)

    audit_artifact = tmp_path / target.audit_artifact
    audit_artifact.parent.mkdir(parents=True, exist_ok=True)
    audit_artifact.write_text(
        json.dumps(
            {
                "timestamp_utc": "2026-04-08T02:34:23+00:00",
                "model_id": target.model_id,
                "status": "ok",
                "pipeline_tag": "image-text-to-text",
                "config_model_type": "gemma4",
                "config_architectures": ["Gemma4ForConditionalGeneration"],
                "family_evidence": {"matched": True},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(autonomous_rd_cycle, "ROOT", tmp_path)
    commands = build_commands(target)
    cycle_state = autonomous_rd_cycle.derive_cycle_state(
        target,
        commands,
        [
            {
                "name": "gemma_audit",
                "ok": False,
                "exit_code": 1,
                "stdout": '{"status":"error","stage":"fetch_model_info"}\n',
                "stderr": "",
                "command": commands["gemma_audit"],
            }
        ],
    )

    stage_by_name = {stage["stage"]: stage for stage in cycle_state["stages"]}
    assert stage_by_name["gemma_audit"]["status"] == "passed"
    assert "cached verified local artifact" in stage_by_name["gemma_audit"]["reason"]
    assert stage_by_name["gemma_audit"]["evidence"]["audit_artifact"] == target.audit_artifact
    assert cycle_state["current_stage"] == "local_eval_gate"


def test_derive_cycle_state_emits_omnicoder_fallback_when_gemma_blocked_after_local_gates(
    tmp_path: Path, monkeypatch
) -> None:
    target = TARGETS["gemma4-31b-it"]
    local_snapshot = tmp_path / target.local_model_dir
    download_dir = local_snapshot / ".cache" / "huggingface" / "download"
    download_dir.mkdir(parents=True, exist_ok=True)
    (local_snapshot / "config.json").write_text('{"model_type":"gemma4"}\n', encoding="utf-8")
    (local_snapshot / "model.safetensors.index.json").write_text(
        '{"metadata":{"total_size":4096},"weight_map":{"foo":"model-00001-of-00002.safetensors"}}\n',
        encoding="utf-8",
    )
    (download_dir / "model.safetensors.incomplete").write_bytes(b"x" * 1024)

    audit_artifact = tmp_path / target.audit_artifact
    audit_artifact.parent.mkdir(parents=True, exist_ok=True)
    audit_artifact.write_text(
        json.dumps(
            {
                "timestamp_utc": "2026-04-08T02:34:23+00:00",
                "model_id": target.model_id,
                "status": "ok",
                "family_evidence": {"matched": True},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(autonomous_rd_cycle, "ROOT", tmp_path)
    commands = build_commands(target)
    cycle_state = autonomous_rd_cycle.derive_cycle_state(
        target,
        commands,
        [
            {
                "name": "local_eval_gate",
                "ok": True,
                "exit_code": 0,
                "stdout": '{"gate":"local_quality_gate","ok":true}\n',
                "stderr": "",
                "command": commands["local_eval_gate"],
            },
            {
                "name": "holdout_integrity",
                "ok": True,
                "exit_code": 0,
                "stdout": '{"gate":"dataset_integrity_gate","ok":true}\n',
                "stderr": "",
                "command": commands["holdout_integrity"],
            },
        ],
    )

    assert cycle_state["current_stage"] == "gemma_snapshot_acquire"
    assert cycle_state["fallback_ready"] is True
    assert cycle_state["fallback_target"]["target_id"] == "omnicoder9b"
    assert cycle_state["fallback_next_action"] == commands["fallback_remote_job_queue"]


def test_derive_cycle_state_builds_registry_backed_autonomous_evolution_state(
    tmp_path: Path, monkeypatch
) -> None:
    target = TARGETS["omnicoder9b"]
    parent_output_dir = (
        "outputs/interface-prefix-omnicoder9b-semantic-v4-2npu-true20-20260329T2219CST"
    )
    child_output_dir = (
        "outputs/omnicoder9b-quantum-generalization-sft-8npu-fastiter-20260409T1451CST"
    )

    (tmp_path / parent_output_dir / "adapter").mkdir(parents=True, exist_ok=True)
    # A delivery-ready run must have actual adapter weights present, not just an
    # empty output dir: reachability now tracks the weights, not the directory.
    (tmp_path / child_output_dir / "adapter").mkdir(parents=True, exist_ok=True)

    model_registry_dir = tmp_path / "artifacts" / "model-registry"
    model_registry_dir.mkdir(parents=True, exist_ok=True)
    (model_registry_dir / "index.json").write_text(
        json.dumps(
            {
                "archive_version": "model-run-index-v2",
                "runs": [
                    {
                        "label": "omnicoder9b-semantic-v4-2npu-true20",
                        "output_dir": parent_output_dir,
                        "archive_path": "artifacts/model-registry/parent.json",
                        "base_model": "models/OmniCoder-9B",
                        "training_method": "LoRA SFT",
                        "completed_steps": 20,
                        "final_eval_loss": 0.37,
                        "final_eval_perplexity": 1.45,
                        "delivery_manifest": "artifacts/deliveries/omnicoder9b_first_working_adapter_20260330.json",
                        "handoff_manifest": "artifacts/deliveries/omnicoder9b-qual-eval-handoff_20260330T021144Z/handoff_manifest.json",
                    },
                    {
                        "label": "omnicoder9b-quantum-generalization-sft-8npu-fastiter-20260409",
                        "output_dir": child_output_dir,
                        "archive_path": "artifacts/model-registry/child.json",
                        "base_model": "models/OmniCoder-9B",
                        "training_method": "LoRA SFT",
                        "completed_steps": 12,
                        "final_eval_loss": 0.38,
                        "final_eval_perplexity": 1.47,
                        "parent_output_dir": parent_output_dir,
                        "adapter_init": f"{parent_output_dir}/adapter",
                        "headline_summary": {
                            "kind": "override_summary",
                            "override_passes": 2,
                            "override_total": 4,
                            "override_pass_rate": 0.5,
                        },
                    },
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (model_registry_dir / "parent.json").write_text(
        json.dumps(
            {
                "archived_at_utc": "2026-04-09T00:00:00+00:00",
                "linked_artifacts": {
                    "delivery_manifest": {
                        "path": "artifacts/deliveries/omnicoder9b_first_working_adapter_20260330.json"
                    },
                    "handoff_manifest": {
                        "path": "artifacts/deliveries/omnicoder9b-qual-eval-handoff_20260330T021144Z/handoff_manifest.json"
                    },
                },
                "evaluation": {
                    "headline_summary": {
                        "kind": "base_vs_adapter_example_slice",
                        "example_count": 5,
                    },
                    "result_artifacts": [],
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (model_registry_dir / "child.json").write_text(
        json.dumps(
            {
                "archived_at_utc": "2026-04-10T00:00:00+00:00",
                "linked_artifacts": {
                    "delivery_manifest": None,
                    "handoff_manifest": None,
                },
                "evaluation": {
                    "headline_summary": {
                        "kind": "override_summary",
                        "override_passes": 2,
                        "override_total": 4,
                        "override_pass_rate": 0.5,
                    },
                    "result_artifacts": [
                        {
                            "path": "reports/strict_holdout_base_vs_adapter_comparison_20260410.json",
                            "summary": {
                                "kind": "strict_override_comparison",
                                "base_passes": 3,
                                "base_total": 4,
                                "adapter_passes": 2,
                                "adapter_total": 4,
                                "adapter_minus_base_passes": -1,
                                "adapter_minus_base_pass_rate": -0.25,
                            },
                        }
                    ],
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    delivery_registry_dir = tmp_path / "artifacts" / "delivery-registry"
    delivery_registry_dir.mkdir(parents=True, exist_ok=True)
    (delivery_registry_dir / "index.json").write_text(
        json.dumps(
            {
                "generated_at_utc": "2026-04-11T06:20:08+00:00",
                "summary": {"issue_count": 2},
                "issues": [
                    {
                        "scope": "deliveries",
                        "identifier": "omnicoder9b_first_working_adapter_20260330",
                        "problem": "missing-adapter-weights",
                        "target": f"{parent_output_dir}/adapter/adapter_model.safetensors",
                    },
                    {
                        "scope": "deliveries",
                        "identifier": "omnicoder9b_first_working_adapter_20260330",
                        "problem": "missing-delivery-artifact",
                        "target": "artifacts/deliveries/omnicoder9b_first_working_adapter_20260330.tar.gz",
                    },
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(autonomous_rd_cycle, "ROOT", tmp_path)
    cycle_state = autonomous_rd_cycle.derive_cycle_state(target, build_commands(target), [])
    evolution_state = cycle_state["autonomous_evolution_state"]

    assert evolution_state["tracked_run_count"] == 2
    assert evolution_state["delivery_issue_count"] == 2
    assert evolution_state["best_runnable_run"]["label"] == (
        "omnicoder9b-quantum-generalization-sft-8npu-fastiter-20260409"
    )
    assert evolution_state["best_strict_holdout_run"]["label"] == (
        "omnicoder9b-quantum-generalization-sft-8npu-fastiter-20260409"
    )
    assert evolution_state["latest_children_by_parent"] == [
        {
            "parent_output_dir": parent_output_dir,
            "latest_child": evolution_state["best_runnable_run"],
        }
    ]
    assert (
        evolution_state["best_strict_holdout_run"]["strict_holdout_comparison"]["base_passes"] == 3
    )
    assert evolution_state["next_recommended_action"]["kind"] == "repair_or_supersede_delivery"
    assert evolution_state["next_recommended_action"]["command"] == (
        "python3 scripts/build_delivery_artifact.py "
        "artifacts/deliveries/omnicoder9b_first_working_adapter_20260330.json --check-only"
    )


def test_autonomous_evolution_state_prefers_queueing_child_when_delivery_chain_is_clean(
    tmp_path: Path, monkeypatch
) -> None:
    target = TARGETS["omnicoder9b"]
    output_dir = "outputs/omnicoder9b-quantum-generalization-sft-8npu-fastiter-20260409T1451CST"
    # Adapter weights must be present for the run to count as reachable/runnable.
    (tmp_path / output_dir / "adapter").mkdir(parents=True, exist_ok=True)

    model_registry_dir = tmp_path / "artifacts" / "model-registry"
    model_registry_dir.mkdir(parents=True, exist_ok=True)
    (model_registry_dir / "index.json").write_text(
        json.dumps(
            {
                "archive_version": "model-run-index-v2",
                "runs": [
                    {
                        "label": "omnicoder9b-quantum-generalization-sft-8npu-fastiter-20260409",
                        "output_dir": output_dir,
                        "archive_path": "artifacts/model-registry/child.json",
                        "base_model": "models/OmniCoder-9B",
                        "training_method": "LoRA SFT",
                        "completed_steps": 12,
                        "final_eval_loss": 0.38,
                        "final_eval_perplexity": 1.47,
                        "delivery_manifest": "artifacts/deliveries/clean-fastiter.json",
                        "headline_summary": {
                            "kind": "override_summary",
                            "override_passes": 3,
                            "override_total": 4,
                            "override_pass_rate": 0.75,
                        },
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (model_registry_dir / "child.json").write_text(
        json.dumps(
            {
                "archived_at_utc": "2026-04-10T00:00:00+00:00",
                "linked_artifacts": {
                    "delivery_manifest": {"path": "artifacts/deliveries/clean-fastiter.json"},
                    "handoff_manifest": None,
                },
                "evaluation": {
                    "headline_summary": {
                        "kind": "override_summary",
                        "override_passes": 3,
                        "override_total": 4,
                        "override_pass_rate": 0.75,
                    },
                    "result_artifacts": [],
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    delivery_registry_dir = tmp_path / "artifacts" / "delivery-registry"
    delivery_registry_dir.mkdir(parents=True, exist_ok=True)
    (delivery_registry_dir / "index.json").write_text(
        json.dumps(
            {
                "generated_at_utc": "2026-04-11T06:20:08+00:00",
                "summary": {"issue_count": 0},
                "issues": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(autonomous_rd_cycle, "ROOT", tmp_path)
    cycle_state = autonomous_rd_cycle.derive_cycle_state(target, build_commands(target), [])
    evolution_state = cycle_state["autonomous_evolution_state"]

    assert evolution_state["best_delivery_ready_run"]["label"] == (
        "omnicoder9b-quantum-generalization-sft-8npu-fastiter-20260409"
    )
    assert evolution_state["next_recommended_action"]["kind"] == "queue_next_child_iteration"
    assert (
        evolution_state["next_recommended_action"]["command"]
        == build_commands(target)["remote_job_queue"]
    )
    assert evolution_state["next_recommended_action"]["candidate_parent_output_dir"] == output_dir


def test_main_emits_machine_readable_staged_gemma_preflight_results(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    output_dir = tmp_path / "reports"
    artifact_dir = tmp_path / "artifacts"
    target = TARGETS["gemma4-31b-it"]
    commands = build_commands(target)

    monkeypatch.setattr(
        autonomous_rd_cycle,
        "parse_args",
        lambda: argparse.Namespace(
            target=target.target_id,
            report_prefix="autonomous_rd_cycle_test",
            run_local_gates=True,
            run_gemma_audit=True,
            run_gemma_runtime_bootstrap=True,
            run_gemma_smoke=True,
            output_dir=output_dir,
            artifact_dir=artifact_dir,
        ),
    )

    staged_results = {
        commands["local_eval_gate"]: {
            "ok": True,
            "exit_code": 0,
            "stdout": '{"gate":"local_quality_gate","ok":true}\n',
            "stderr": "",
        },
        commands["holdout_integrity"]: {
            "ok": True,
            "exit_code": 0,
            "stdout": '{"gate":"dataset_integrity_gate","ok":true}\n',
            "stderr": "",
        },
        commands["gemma_audit"]: {
            "ok": True,
            "exit_code": 0,
            "stdout": '{"stage":"gemma_source_gate","state":"passed"}\n',
            "stderr": "",
        },
        commands["gemma_runtime_bootstrap"]: {
            "ok": False,
            "exit_code": 1,
            "stdout": "",
            "stderr": "fatal: unable to access 'https://github.com/huggingface/transformers.git/': Could not resolve host: github.com\n",
        },
        commands["gemma_smoke"]: {
            "ok": False,
            "exit_code": 2,
            "stdout": '{"stage":"trainer_backend_preflight","state":"blocked"}\n',
            "stderr": "Gemma trainer/backend preflight unavailable\n",
        },
    }
    executed_commands: list[str] = []

    def fake_run_command(command: list[str]) -> dict[str, object]:
        assert command[:2] == ["bash", "-lc"]
        rendered_command = command[2]
        executed_commands.append(rendered_command)
        result = staged_results[rendered_command]
        return {"command": command, **result}

    monkeypatch.setattr(autonomous_rd_cycle, "run_command", fake_run_command)

    exit_code = autonomous_rd_cycle.main()

    assert exit_code == 0
    assert executed_commands == [
        commands["local_eval_gate"],
        commands["holdout_integrity"],
        commands["gemma_audit"],
        commands["gemma_runtime_bootstrap"],
        commands["gemma_smoke"],
    ]

    rendered_stdout = json.loads(capsys.readouterr().out)
    report_json = Path(rendered_stdout["report_json"])
    cycle_state_json = Path(rendered_stdout["cycle_state_json"])
    command_sheet = Path(rendered_stdout["command_sheet"])
    assert rendered_stdout["target"] == target.model_id
    assert report_json.exists()
    assert cycle_state_json.exists()
    assert command_sheet.exists()

    payload = json.loads(report_json.read_text(encoding="utf-8"))
    cycle_state = json.loads(cycle_state_json.read_text(encoding="utf-8"))
    gate_map = {gate["command_key"]: gate["gate"] for gate in payload["gates"]}
    assert gate_map["local_eval_gate"] == "local_quality_gate"
    assert gate_map["holdout_integrity"] == "dataset_integrity_gate"
    assert gate_map["gemma_audit"] == "gemma_source_gate"
    assert gate_map["gemma_snapshot_verify"] == "gemma_snapshot_gate"
    assert gate_map["paper_router_warmup"] == "paper_router_warmup_gate"
    assert gate_map["gemma_runtime_bootstrap"] == "gemma_runtime_bootstrap_gate"
    assert gate_map["gemma_smoke"] == "gemma_trainer_backend_gate"
    assert gate_map["remote_job_queue"] == "remote_launcher_gate"

    assert payload["readiness"]["status"] == "blocked"
    assert payload["readiness"]["ready_for_remote_finetune"] is False
    assert payload["cycle_state"]["current_stage"] == "gemma_snapshot_acquire"
    assert payload["cycle_state"]["next_action"] == commands["gemma_snapshot_acquire"]
    assert cycle_state["current_stage"] == "gemma_snapshot_acquire"
    assert cycle_state["ready_for_remote_finetune"] is False

    execution_results = payload["execution_results"]
    assert [result["name"] for result in execution_results] == [
        "local_eval_gate",
        "holdout_integrity",
        "gemma_audit",
        "gemma_runtime_bootstrap",
        "gemma_smoke",
    ]
    assert [result["command"] for result in execution_results] == executed_commands
    assert all(
        {"name", "command", "ok", "exit_code", "stdout", "stderr"} <= result.keys()
        for result in execution_results
    )

    result_by_name = {result["name"]: result for result in execution_results}
    assert result_by_name["local_eval_gate"]["ok"] is True
    assert '"gate":"local_quality_gate"' in result_by_name["local_eval_gate"]["stdout"]
    assert result_by_name["holdout_integrity"]["ok"] is True
    assert '"gate":"dataset_integrity_gate"' in result_by_name["holdout_integrity"]["stdout"]
    assert result_by_name["gemma_audit"]["ok"] is True
    assert '"state":"passed"' in result_by_name["gemma_audit"]["stdout"]
    assert result_by_name["gemma_runtime_bootstrap"]["ok"] is False
    assert result_by_name["gemma_runtime_bootstrap"]["exit_code"] == 1
    assert (
        "Could not resolve host: github.com" in result_by_name["gemma_runtime_bootstrap"]["stderr"]
    )
    assert result_by_name["gemma_smoke"]["ok"] is False
    assert result_by_name["gemma_smoke"]["exit_code"] == 2
    assert '"state":"blocked"' in result_by_name["gemma_smoke"]["stdout"]
    assert "Gemma trainer/backend preflight unavailable" in result_by_name["gemma_smoke"]["stderr"]

    machine_results = {
        name: json.loads(result["stdout"])
        for name, result in result_by_name.items()
        if result["stdout"].strip()
    }
    assert machine_results["gemma_audit"]["stage"] == "gemma_source_gate"
    assert machine_results["gemma_audit"]["state"] == "passed"
    assert machine_results["gemma_smoke"]["stage"] == "trainer_backend_preflight"
    assert machine_results["gemma_smoke"]["state"] == "blocked"

    command_sheet_text = command_sheet.read_text(encoding="utf-8")
    assert "gemma_audit:" in command_sheet_text
    assert "gemma_snapshot_acquire:" in command_sheet_text
    assert "fallback_remote_job_queue:" in command_sheet_text
    assert "gemma_snapshot_relay:" in command_sheet_text
    assert "gemma_snapshot_verify:" in command_sheet_text
    assert "gemma_runtime_bootstrap:" in command_sheet_text
    assert "gemma_smoke:" in command_sheet_text
    assert payload["readiness"]["status"] == "blocked"
    assert payload["readiness"]["ready_for_remote_finetune"] is False
    assert "gemma snapshot" in payload["readiness"]["blocker"].lower()
    assert payload["cycle_state"]["fallback_ready"] is True
    assert payload["cycle_state"]["fallback_target"]["target_id"] == "omnicoder9b"
    assert (
        payload["moe_expert_routing_prep"]["strategy"] == "router_warmup_then_frequency_guided_esft"
    )
    assert "inspection_command" in payload["moe_expert_routing_prep"]
