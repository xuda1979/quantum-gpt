"""Unit tests for scripts/rl_distill_pipeline.py.

These tests do NOT call any real API; they mock the HTTP layer and
verify the pipeline's control flow, prompt construction, sample
building, and buffer writing.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.rl_distill_pipeline as rld  # noqa: E402


class TestPrompts(unittest.TestCase):
    """Verify the prompt templates contain the expected placeholders."""

    def test_qgate_prompt_has_placeholders(self):
        rendered = rld.TEACHER_QGATE_PROMPT_TEMPLATE.format(
            question="Q",
            framework="qiskit",
            difficulty="easy",
            topic="circuits",
        )
        self.assertIn("Q", rendered)
        self.assertIn("qiskit", rendered)
        self.assertIn("easy", rendered)
        self.assertIn("circuits", rendered)
        self.assertIn("is_valid", rendered)

    def test_teacher_eval_prompt_has_placeholders(self) -> None:
        rendered = rld.TEACHER_EVAL_PROMPT_TEMPLATE.format(
            question="Q",
            student_code="print('hi')",
            exec_brief="execution_verdict: PASS",
        )
        self.assertIn("Q", rendered)
        self.assertIn("print('hi')", rendered)
        self.assertIn("is_correct", rendered)
        self.assertIn("execution_verdict: PASS", rendered)
        self.assertIn("ground truth", rendered)


class TestParseTeacherJson(unittest.TestCase):
    def test_plain_json(self):
        out = rld.parse_teacher_json('{"is_valid": true, "is_answerable": true}')
        self.assertTrue(out["is_valid"])
        self.assertTrue(out["is_answerable"])

    def test_fenced_json(self):
        out = rld.parse_teacher_json('```json\n{"is_valid": true}\n```')
        self.assertTrue(out["is_valid"])

    def test_json_with_preamble(self):
        out = rld.parse_teacher_json('Here is my answer: {"is_valid": true} thanks')
        self.assertTrue(out["is_valid"])

    def test_invalid_returns_parse_error(self):
        out = rld.parse_teacher_json("not json at all")
        self.assertTrue(out.get("_parse_error"))


class TestExtractCodeBlock(unittest.TestCase):
    def test_plain_text(self):
        self.assertEqual(rld.extract_code_block("print('hi')"), "print('hi')")

    def test_fenced_python(self):
        text = "Here is the code:\n```python\nprint('hi')\n```\nDone."
        self.assertEqual(rld.extract_code_block(text), "print('hi')")

    def test_fenced_no_language(self):
        text = "```\nprint('hi')\n```"
        self.assertEqual(rld.extract_code_block(text), "print('hi')")


class TestCriticLoRASeam(unittest.TestCase):
    """N2 quantum-critic-LoRA wiring seam (docs/rd-line-quantum-critic-lora-2026-07-13.md).

    Verifies the config flag routes teacher_eval correctly and fails loud
    when the adapter path is missing (no silent fallback to GLM5.2).
    """

    def test_default_critic_mode_is_glm52_api(self):
        t = rld.TeacherConfig("http://t/v1", "k", "glm5.2", 0.0, 1024, 20, 60)
        self.assertEqual(t.critic_mode, "glm52_api")
        self.assertEqual(t.critic_adapter_path, "")

    def test_local_lora_empty_adapter_raises(self):
        t = rld.TeacherConfig(
            "http://t/v1",
            "k",
            "glm5.2",
            0.0,
            1024,
            20,
            60,
            critic_mode="local_lora",
            critic_adapter_path="",
        )
        with self.assertRaises(RuntimeError) as ctx:
            rld.teacher_eval(t, "q", "print('hi')")
        self.assertIn("critic_adapter_path", str(ctx.exception))

    def test_local_lora_with_adapter_raises_on_box_seam(self):
        # With a non-empty adapter path, the function proceeds past the
        # empty-path guard and hits the on-box inference seam, which
        # raises RuntimeError (cannot run 27B on CPU). This confirms the
        # routing reaches _critic_lora_eval rather than the GLM5.2 API.
        t = rld.TeacherConfig(
            "http://t/v1",
            "k",
            "glm5.2",
            0.0,
            1024,
            20,
            60,
            critic_mode="local_lora",
            critic_adapter_path="/tmp/fake",
        )
        with self.assertRaises(RuntimeError) as ctx:
            rld.teacher_eval(t, "q", "print('hi')")
        # The on-box seam message mentions the launch script or peft
        msg = str(ctx.exception)
        self.assertTrue(
            "on-box" in msg or "peft" in msg or "launch script" in msg,
            f"unexpected error: {msg}",
        )


class TestSampleBuilder(unittest.TestCase):
    def _make_cfg(self):
        student = rld.StudentConfig("http://s/v1", "k", "stu", 0.7, 1024, 60)
        teacher = rld.TeacherConfig("http://t/v1", "k", "glm5.2", 0.0, 1024, 20, 60)
        qgen = rld.QuestionGenConfig(
            frameworks=["qiskit"],
            topics=["circuits"],
            difficulties=["easy"],
            framework_distribution={"qiskit": 1.0},
            difficulty_distribution={"easy": 1.0},
            topic_distribution={"circuits": 1.0},
            max_resamples_per_question=3,
            rejection_buffer_size=64,
        )
        return rld.PipelineConfig(
            student=student,
            teacher=teacher,
            question_gen=qgen,
            pipeline={},
            output_dir=Path("/tmp"),
            seed=42,
        )

    def test_build_sample_shape(self):
        cfg = self._make_cfg()
        sample = rld._build_sample(
            cfg=cfg,
            question="Q?",
            framework="qiskit",
            topic="circuits",
            difficulty="easy",
            student_code="print(1)",
            teacher_eval_result={
                "is_correct": False,
                "correct_answer": "print(2)",
                "confidence": 0.9,
                "issues": ["bad"],
            },
            teacher_correction={
                "content": "print(2)",
                "logprobs": [{"token": "print", "logprob": -0.1}],
            },
            qgate={
                "is_valid": True,
                "is_answerable": True,
                "is_non_trivial": True,
                "requires_full_program": True,
                "improved_question": "",
                "confidence": 0.95,
                "issues": [],
            },
            student_qgen_meta={"temperature": 0.7, "resample_attempts": 1},
        )
        self.assertEqual(sample["format"], "chat-sft-v1")
        self.assertEqual(sample["messages"][2]["role"], "assistant")
        self.assertEqual(sample["messages"][2]["content"], "print(2)")
        self.assertIn("teacher_logits", sample)
        self.assertEqual(sample["teacher_logits"]["content"], "print(2)")
        self.assertEqual(sample["metadata"]["framework"], "qiskit")
        self.assertEqual(sample["metadata"]["teacher_is_correct"], False)
        self.assertEqual(sample["metadata"]["qgate_is_valid"], True)
        self.assertEqual(sample["metadata"]["qgate_requires_full_program"], True)
        self.assertEqual(sample["source_schema"], "rl-distill-v1")

    def test_reward_tagged_in_metadata(self):
        cfg = self._make_cfg()
        sample = rld._build_sample(
            cfg=cfg,
            question="Build a Bell state in Qiskit and measure it.",
            framework="qiskit",
            topic="circuits",
            difficulty="easy",
            student_code="```python\nfrom qiskit import QuantumCircuit\nqc=QuantumCircuit(2,2);qc.h(0);qc.cx(0,1);qc.measure([0,1],[0,1])\n```",
            teacher_eval_result={
                "is_correct": True,
                "issues": [],
                "correct_answer": "from qiskit import QuantumCircuit\nqc=QuantumCircuit(2,2)\nqc.h(0)\nqc.cx(0,1)\nqc.measure([0,1],[0,1])",
                "confidence": 0.95,
            },
            teacher_correction={
                "content": "from qiskit import QuantumCircuit\nqc=QuantumCircuit(2,2)\nqc.h(0)\nqc.cx(0,1)\nqc.measure([0,1],[0,1])",
                "logprobs": [{"token": "from", "logprob": -0.1}] * 10,
            },
            qgate={
                "is_valid": True,
                "is_answerable": True,
                "is_non_trivial": True,
                "requires_full_program": True,
                "improved_question": "",
                "confidence": 0.9,
                "issues": [],
            },
            student_qgen_meta={"temperature": 0.7, "resample_attempts": 1},
            student_exec={
                "verdict": "PASS",
                "stdout": "",
                "stderr": "",
                "exit_code": 0,
                "runtime_ms": 120,
                "truncated": False,
            },
            teacher_exec={
                "verdict": "PASS",
                "stdout": "",
                "stderr": "",
                "exit_code": 0,
                "runtime_ms": 95,
                "truncated": False,
            },
        )
        self.assertIn("reward", sample["metadata"])
        self.assertGreater(sample["metadata"]["reward"], 0.8)
        # Exec results are recorded in metadata for auditability.
        self.assertEqual(sample["metadata"]["student_exec"]["verdict"], "PASS")
        self.assertEqual(sample["metadata"]["teacher_exec"]["verdict"], "PASS")

    def test_reward_low_when_student_exec_fails(self):
        """When the sandbox is enabled and the student's code fails execution,
        the reward must be low even if the teacher (wrongly) says is_correct."""
        cfg = self._make_cfg()
        sample = rld._build_sample(
            cfg=cfg,
            question="Build a Bell state in Qiskit and measure it.",
            framework="qiskit",
            topic="circuits",
            difficulty="easy",
            student_code="```python\nraise RuntimeError('boom')\n```",
            teacher_eval_result={
                "is_correct": True,
                "issues": [],
                "correct_answer": "from qiskit import QuantumCircuit",
                "confidence": 0.95,
            },
            teacher_correction={
                "content": "from qiskit import QuantumCircuit",
                "logprobs": [{"token": "from", "logprob": -0.1}] * 10,
            },
            qgate={
                "is_valid": True,
                "is_answerable": True,
                "is_non_trivial": True,
                "requires_full_program": True,
                "improved_question": "",
                "confidence": 0.9,
                "issues": [],
            },
            student_qgen_meta={"temperature": 0.7, "resample_attempts": 1},
            student_exec={
                "verdict": "FAIL",
                "stdout": "",
                "stderr": "RuntimeError: boom",
                "exit_code": 1,
                "runtime_ms": 30,
                "truncated": False,
            },
            teacher_exec={
                "verdict": "PASS",
                "stdout": "",
                "stderr": "",
                "exit_code": 0,
                "runtime_ms": 95,
                "truncated": False,
            },
        )
        # w_exec_pass=0.45 contributes 0; the rest sum to at most 0.55.
        self.assertLess(sample["metadata"]["reward"], 0.6)


class TestRejectionTracker(unittest.TestCase):
    def test_down_weights_high_rejection_key(self):
        rt = rld.RejectionTracker(
            {
                "framework": {"qiskit": 0.5, "cirq": 0.5},
                "topic": {"circuits": 1.0},
                "difficulty": {"easy": 1.0},
            }
        )
        for _ in range(20):
            rt.record("framework", "qiskit", True)
        for _ in range(20):
            rt.record("framework", "cirq", False)
        d = rt.adjusted_distribution("framework")
        self.assertGreater(d["cirq"], d["qiskit"])

    def test_no_data_blends_prior_with_uniform(self):
        # With no rejection data, the adjusted distribution should be a
        # low-pass blend of the prior and the uniform-acceptance (smoothing)
        # distribution: w(k) = (1-low_pass)*prior(k) + low_pass*uniform(k).
        rt = rld.RejectionTracker(
            {
                "framework": {"qiskit": 0.3, "cirq": 0.7},
                "topic": {"circuits": 1.0},
                "difficulty": {"easy": 1.0},
            }
        )
        d = rt.adjusted_distribution("framework")
        # cirq should be between the prior (0.7) and the uniform (0.5),
        # pulled toward 0.5 by low_pass=0.25: 0.75*0.7 + 0.25*0.5 = 0.65.
        self.assertGreater(d["cirq"], 0.6)
        self.assertLess(d["cirq"], 0.7)


class TestDedupIndex(unittest.TestCase):
    def test_detects_duplicate(self):
        di = rld.DedupIndex(max_entries=5)
        self.assertFalse(di.is_duplicate("question one", "answer one"))
        self.assertTrue(di.is_duplicate("question one", "answer one"))
        self.assertFalse(di.is_duplicate("question two", "answer two"))

    def test_normalizes_whitespace(self):
        di = rld.DedupIndex(max_entries=5)
        self.assertFalse(di.is_duplicate("what  is  1+1", "2"))
        self.assertTrue(di.is_duplicate("what is 1+1", "2"))


class TestGuardrailConfig(unittest.TestCase):
    def test_defaults(self):
        g = rld.GuardrailConfig()
        self.assertEqual(g.max_consecutive_teacher_rejections, 12)
        self.assertEqual(g.min_teacher_confidence, 0.30)


class TestBufferWriter(unittest.TestCase):
    def test_append_and_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            buf = rld.BufferWriter(Path(td), name="rl_distill")
            buf.append_sample({"example_id": "x1", "messages": []})
            buf.append_sample({"example_id": "x2", "messages": []})
            buf.write_manifest(extra={"stats": {"samples_appended": 2}})
            self.assertEqual(buf._count, 2)
            manifest = json.loads((Path(td) / "rl_distill_manifest.json").read_text())
            self.assertEqual(manifest["buffer_count"], 2)
            self.assertEqual(manifest["accepted_total"], 2)

    def test_rejection(self):
        with tempfile.TemporaryDirectory() as td:
            buf = rld.BufferWriter(Path(td), name="rl_distill")
            buf.append_rejection({"question": "bad", "qgate": {"is_valid": False}})
            buf.write_manifest()
            self.assertEqual(buf._rejected, 1)
            self.assertTrue((Path(td) / "rl_distill_rejected.jsonl").exists())


class TestDistributionSamplers(unittest.TestCase):
    def test_sample_from_distribution(self):
        import random

        rng = random.Random(42)
        counts = {"a": 0, "b": 0}
        for _ in range(1000):
            k = rld._sample_from_distribution({"a": 0.7, "b": 0.3}, rng)
            counts[k] += 1
        # Should be roughly 700/300
        self.assertGreater(counts["a"], 600)
        self.assertLess(counts["a"], 800)
        self.assertGreater(counts["b"], 200)
        self.assertLess(counts["b"], 400)

    def test_normalize_dist(self):
        out = rld._normalize_dist({"a": 2, "b": 2}, ["a", "b"])
        self.assertAlmostEqual(out["a"], 0.5)
        self.assertAlmostEqual(out["b"], 0.5)

    def test_normalize_dist_empty(self):
        out = rld._normalize_dist(None, ["a", "b", "c"])
        self.assertAlmostEqual(out["a"], 1 / 3)


class TestProcessOne(unittest.TestCase):
    """End-to-end mock test of process_one with all HTTP calls patched."""

    def _make_cfg(self):
        student = rld.StudentConfig("http://s/v1", "k", "stu", 0.7, 1024, 60)
        teacher = rld.TeacherConfig("http://t/v1", "k", "glm5.2", 0.0, 1024, 20, 60)
        qgen = rld.QuestionGenConfig(
            frameworks=["qiskit"],
            topics=["circuits"],
            difficulties=["easy"],
            framework_distribution={"qiskit": 1.0},
            difficulty_distribution={"easy": 1.0},
            topic_distribution={"circuits": 1.0},
            max_resamples_per_question=3,
            rejection_buffer_size=64,
        )
        # Sandbox disabled for the mocked happy-path tests; the execution
        # gate is exercised separately by TestSandboxExecution.
        sandbox_off = rld.SandboxConfig(enabled=False)
        return rld.PipelineConfig(
            student=student,
            teacher=teacher,
            question_gen=qgen,
            pipeline={},
            output_dir=Path("/tmp"),
            seed=42,
            sandbox=sandbox_off,
        )

    def test_happy_path(self):
        cfg = self._make_cfg()
        import random

        rng = random.Random(42)
        with tempfile.TemporaryDirectory() as td:
            buf = rld.BufferWriter(Path(td), name="rl_distill")
            stats = {
                k: 0
                for k in [
                    "iterations",
                    "samples_appended",
                    "qgate_rejected",
                    "qgate_exhausted",
                    "student_qgen_errors",
                    "student_qgen_empty",
                    "teacher_qgate_errors",
                    "teacher_qgate_parse_errors",
                    "student_attempt_errors",
                    "student_attempt_empty",
                    "teacher_eval_errors",
                    "teacher_eval_parse_errors",
                    "teacher_correction_empty",
                    "teacher_logprobs_errors",
                    "teacher_logprobs_empty",
                ]
            }
            with (
                mock.patch.object(
                    rld,
                    "student_propose_question",
                    return_value="Write a Bell state in Qiskit and measure both qubits into a classical register of size 2.",
                ),
                mock.patch.object(
                    rld,
                    "teacher_validate_question",
                    return_value={
                        "is_valid": True,
                        "is_answerable": True,
                        "is_non_trivial": True,
                        "requires_full_program": True,
                        "improved_question": "",
                        "confidence": 0.9,
                        "issues": [],
                    },
                ),
                mock.patch.object(
                    rld,
                    "student_attempt",
                    return_value="```python\nfrom qiskit import QuantumCircuit\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\n```",
                ),
                mock.patch.object(
                    rld,
                    "teacher_eval",
                    return_value={
                        "is_correct": False,
                        "issues": ["missing measurement"],
                        "correct_answer": "from qiskit import QuantumCircuit\nqc = QuantumCircuit(2, 2)\nqc.h(0)\nqc.cx(0, 1)\nqc.measure([0,1], [0,1])",
                        "confidence": 0.9,
                    },
                ),
                mock.patch.object(
                    rld,
                    "teacher_correction_with_logits",
                    return_value={
                        "content": "from qiskit import QuantumCircuit\nqc = QuantumCircuit(2, 2)\nqc.h(0)\nqc.cx(0, 1)\nqc.measure([0,1], [0,1])",
                        "logprobs": [
                            {
                                "token": "from",
                                "logprob": -0.1,
                                "top_logprobs": [{"token": "from", "logprob": -0.1}],
                            }
                        ]
                        * 10,
                    },
                ),
            ):
                ok = rld.process_one(cfg, rng, buf, stats)
            self.assertEqual(ok, "appended")
            self.assertEqual(stats["samples_appended"], 1)
            self.assertEqual(buf._count, 1)

    def test_qgate_rejection_then_success(self):
        cfg = self._make_cfg()
        import random

        rng = random.Random(42)
        with tempfile.TemporaryDirectory() as td:
            buf = rld.BufferWriter(Path(td), name="rl_distill")
            stats = {
                k: 0
                for k in [
                    "iterations",
                    "samples_appended",
                    "qgate_rejected",
                    "qgate_exhausted",
                    "student_qgen_errors",
                    "student_qgen_empty",
                    "teacher_qgate_errors",
                    "teacher_qgate_parse_errors",
                    "student_attempt_errors",
                    "student_attempt_empty",
                    "teacher_eval_errors",
                    "teacher_eval_parse_errors",
                    "teacher_correction_empty",
                    "teacher_logprobs_errors",
                    "teacher_logprobs_empty",
                ]
            }
            call_count = {"n": 0}

            def mock_validate(*args, **kwargs):
                call_count["n"] += 1
                if call_count["n"] == 1:
                    return {
                        "is_valid": False,
                        "is_answerable": True,
                        "is_non_trivial": False,
                        "issues": ["too vague"],
                        "improved_question": "",
                        "confidence": 0.8,
                    }
                return {
                    "is_valid": True,
                    "is_answerable": True,
                    "is_non_trivial": True,
                    "requires_full_program": True,
                    "improved_question": "",
                    "confidence": 0.9,
                    "issues": [],
                }

            with (
                mock.patch.object(
                    rld,
                    "student_propose_question",
                    return_value="Write a Bell state in Qiskit. Make it non-trivial.",
                ),
                mock.patch.object(rld, "teacher_validate_question", side_effect=mock_validate),
                mock.patch.object(rld, "student_attempt", return_value="```python\npass\n```"),
                mock.patch.object(
                    rld,
                    "teacher_eval",
                    return_value={
                        "is_correct": False,
                        "issues": ["no code"],
                        "correct_answer": "print('fixed_answer_that_is_long_enough_to_pass_guardrail')",
                        "confidence": 0.9,
                    },
                ),
                mock.patch.object(
                    rld,
                    "teacher_correction_with_logits",
                    return_value={
                        "content": "print('fixed_answer_that_is_long_enough_to_pass_guardrail')",
                        "logprobs": [{"token": "print", "logprob": -0.1}] * 10,
                    },
                ),
            ):
                ok = rld.process_one(cfg, rng, buf, stats)
            self.assertEqual(ok, "appended")
            self.assertEqual(stats["qgate_rejected"], 1)
            self.assertEqual(stats["samples_appended"], 1)

    def test_all_qgate_rejections(self):
        cfg = self._make_cfg()
        import random

        rng = random.Random(42)
        with tempfile.TemporaryDirectory() as td:
            buf = rld.BufferWriter(Path(td), name="rl_distill")
            stats = {
                k: 0
                for k in [
                    "iterations",
                    "samples_appended",
                    "qgate_rejected",
                    "qgate_exhausted",
                    "student_qgen_errors",
                    "student_qgen_empty",
                    "teacher_qgate_errors",
                    "teacher_qgate_parse_errors",
                    "student_attempt_errors",
                    "student_attempt_empty",
                    "teacher_eval_errors",
                    "teacher_eval_parse_errors",
                    "teacher_correction_empty",
                    "teacher_logprobs_errors",
                    "teacher_logprobs_empty",
                ]
            }
            with (
                mock.patch.object(rld, "student_propose_question", return_value="bad"),
                mock.patch.object(
                    rld,
                    "teacher_validate_question",
                    return_value={
                        "is_valid": False,
                        "is_answerable": False,
                        "is_non_trivial": False,
                        "issues": ["too short"],
                        "improved_question": "",
                        "confidence": 0.5,
                    },
                ),
            ):
                ok = rld.process_one(cfg, rng, buf, stats)
            self.assertEqual(ok, "rejected_qgate")
            self.assertEqual(stats["qgate_exhausted"], 1)
            self.assertEqual(stats["samples_appended"], 0)

    def test_coding_qgate_rejects_isolated_function(self):
        """A question that passes is_valid/is_answerable/is_non_trivial but
        does NOT require a full program with main() must be rejected in the
        coding domain (the question-generation contract)."""
        cfg = self._make_cfg()
        self.assertEqual(cfg.task_domain, "coding")
        import random

        rng = random.Random(42)
        with tempfile.TemporaryDirectory() as td:
            buf = rld.BufferWriter(Path(td), name="rl_distill")
            stats = {
                k: 0
                for k in [
                    "iterations",
                    "samples_appended",
                    "qgate_rejected",
                    "qgate_exhausted",
                    "student_qgen_errors",
                    "student_qgen_empty",
                    "teacher_qgate_errors",
                    "teacher_qgate_parse_errors",
                    "student_attempt_errors",
                    "student_attempt_empty",
                    "teacher_eval_errors",
                    "teacher_correction_errors",
                    "qgate_coding_not_full_program",
                    "qgate_science_requires_code",
                ]
            }
            with (
                mock.patch.object(
                    rld,
                    "student_propose_question",
                    return_value="Write a function `bell()` that returns a Bell-state circuit.",
                ),
                mock.patch.object(
                    rld,
                    "teacher_validate_question",
                    return_value={
                        "is_valid": True,
                        "is_answerable": True,
                        "is_non_trivial": True,
                        "requires_full_program": False,
                        "issues": [],
                        "improved_question": "",
                        "confidence": 0.9,
                    },
                ),
            ):
                ok = rld.process_one(cfg, rng, buf, stats)
            self.assertEqual(ok, "rejected_qgate")
            self.assertEqual(stats["qgate_exhausted"], 1)
            self.assertEqual(stats["qgate_coding_not_full_program"], 3)  # 3 resamples, all rejected
            self.assertEqual(stats["samples_appended"], 0)

    def test_science_qgate_rejects_code_requiring_question(self):
        """In the science domain, a question that passes is_valid/is_answerable/
        is_non_trivial but is marked requires_code=true must be rejected
        (science questions must NOT ask for code). Mirrors the coding-domain
        requires_full_program test."""
        student = rld.StudentConfig("http://s/v1", "k", "stu", 0.7, 1024, 60)
        teacher = rld.TeacherConfig("http://t/v1", "k", "glm5.2", 0.0, 1024, 20, 60)
        qgen = rld.QuestionGenConfig(
            frameworks=["L2"],
            topics=["algorithms"],
            difficulties=["medium"],
            framework_distribution={"L2": 1.0},
            difficulty_distribution={"medium": 1.0},
            topic_distribution={"algorithms": 1.0},
            max_resamples_per_question=3,
            rejection_buffer_size=64,
        )
        sandbox_off = rld.SandboxConfig(enabled=False)
        cfg = rld.PipelineConfig(
            student=student,
            teacher=teacher,
            question_gen=qgen,
            pipeline={"task_domain": "science"},
            output_dir=Path("/tmp"),
            seed=42,
            sandbox=sandbox_off,
            task_domain="science",
        )
        self.assertEqual(cfg.task_domain, "science")
        import random

        rng = random.Random(42)
        with tempfile.TemporaryDirectory() as td:
            buf = rld.BufferWriter(Path(td), name="rl_distill")
            stats = {
                k: 0
                for k in [
                    "iterations",
                    "samples_appended",
                    "qgate_rejected",
                    "qgate_exhausted",
                    "student_qgen_errors",
                    "student_qgen_empty",
                    "teacher_qgate_errors",
                    "teacher_qgate_parse_errors",
                    "student_attempt_errors",
                    "student_attempt_empty",
                    "teacher_eval_errors",
                    "teacher_correction_errors",
                    "qgate_coding_not_full_program",
                    "qgate_science_requires_code",
                ]
            }
            with (
                mock.patch.object(
                    rld,
                    "student_propose_question",
                    return_value="Write a Qiskit program that simulates the quantum Fourier transform.",
                ),
                mock.patch.object(
                    rld,
                    "teacher_validate_question",
                    return_value={
                        "is_valid": True,
                        "is_answerable": True,
                        "is_non_trivial": True,
                        "requires_code": True,
                        "issues": [],
                        "improved_question": "",
                        "confidence": 0.9,
                    },
                ),
            ):
                ok = rld.process_one(cfg, rng, buf, stats)
            self.assertEqual(ok, "rejected_qgate")
            self.assertEqual(stats["qgate_exhausted"], 1)
            self.assertEqual(stats["qgate_science_requires_code"], 3)  # 3 resamples, all rejected
            self.assertEqual(stats["samples_appended"], 0)


class TestSandboxExecution(unittest.TestCase):
    """Tests for the execution-gated reward + double-confirmation gate."""

    def test_execute_code_pass(self):
        from scripts.code_exec_sandbox import execute_code

        result = execute_code("print('hello')", timeout_seconds=10)
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["exit_code"], 0)
        self.assertIn("hello", result["stdout"])

    def test_execute_code_fail(self):
        from scripts.code_exec_sandbox import execute_code

        result = execute_code("raise ValueError('boom')", timeout_seconds=10)
        self.assertEqual(result["verdict"], "FAIL")
        self.assertNotEqual(result["exit_code"], 0)
        self.assertIn("ValueError", result["stderr"])

    def test_execute_code_syntax_error(self):
        from scripts.code_exec_sandbox import execute_code

        result = execute_code("def f(:\n  pass\n", timeout_seconds=10)
        self.assertEqual(result["verdict"], "ERROR")
        self.assertIn("SyntaxError", result["stderr"])

    def test_execute_code_timeout(self):
        from scripts.code_exec_sandbox import execute_code

        result = execute_code("while True:\n  pass\n", timeout_seconds=2)
        self.assertEqual(result["verdict"], "ERROR")
        self.assertIn("Timeout", result["stderr"])

    def test_format_exec_brief_includes_verdict(self):
        from scripts.code_exec_sandbox import format_exec_brief

        brief = format_exec_brief(
            {
                "verdict": "FAIL",
                "exit_code": 1,
                "runtime_ms": 42,
                "stdout": "",
                "stderr": "NameError: 'qc' is not defined",
            }
        )
        self.assertIn("execution_verdict: FAIL", brief)
        self.assertIn("NameError", brief)

    def test_check_program_shape_full_program(self):
        from scripts.code_exec_sandbox import check_program_shape

        full = (
            "def main():\n" "    print(1 + 1)\n" "\n" "if __name__ == '__main__':\n" "    main()\n"
        )
        result = check_program_shape(full)
        self.assertTrue(result["has_main_def"])
        self.assertTrue(result["has_main_guard"])
        self.assertTrue(result["calls_main"])
        self.assertTrue(result["is_full_program"])
        self.assertEqual(result["issues"], [])

    def test_check_program_shape_no_main(self):
        from scripts.code_exec_sandbox import check_program_shape

        no_main = "def helper():\n    return 42\n"
        result = check_program_shape(no_main)
        self.assertFalse(result["has_main_def"])
        self.assertFalse(result["is_full_program"])
        self.assertTrue(any("def main" in i for i in result["issues"]))

    def test_check_program_shape_no_guard(self):
        from scripts.code_exec_sandbox import check_program_shape

        no_guard = "def main():\n    print(42)\n"
        result = check_program_shape(no_guard)
        self.assertTrue(result["has_main_def"])
        self.assertFalse(result["has_main_guard"])
        self.assertFalse(result["is_full_program"])
        self.assertTrue(any("__main__" in i for i in result["issues"]))

    def test_check_stdout_nonempty(self):
        from scripts.code_exec_sandbox import check_stdout_nonempty

        self.assertTrue(check_stdout_nonempty({"stdout": "42\n"})["stdout_nonempty"])
        self.assertFalse(check_stdout_nonempty({"stdout": ""})["stdout_nonempty"])
        self.assertFalse(check_stdout_nonempty({"stdout": "   \n  "})["stdout_nonempty"])


class TestWeaknessReport(unittest.TestCase):
    """Tests for the weakness-aware question-generation bias."""

    def _prior(self):
        return {
            "framework": {"qiskit": 0.34, "pennylane": 0.33, "cirq": 0.33},
            "topic": {"algorithms": 0.5, "circuits": 0.5},
            "difficulty": {"easy": 0.3, "medium": 0.5, "hard": 0.2},
        }

    def test_no_report_returns_prior(self):
        wr = rld.WeaknessReport(prior=self._prior())
        d = wr.blended_distribution("framework")
        self.assertAlmostEqual(d["qiskit"], 0.34, places=2)

    def test_report_up_weights_weak_cells(self):
        import json
        import tempfile

        report = {
            "schema_version": 1,
            "cells": [
                {
                    "framework": "qiskit",
                    "topic": "algorithms",
                    "difficulty": "hard",
                    "pass_rate": 0.10,
                    "n": 10,
                },
                {
                    "framework": "cirq",
                    "topic": "circuits",
                    "difficulty": "easy",
                    "pass_rate": 0.95,
                    "n": 10,
                },
            ],
        }
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as f:
            json.dump(report, f)
        wr = rld.WeaknessReport(prior=self._prior(), alpha=0.5)
        self.assertTrue(wr.load(path))
        d = wr.blended_distribution("framework")
        # qiskit (10% pass) should now outweigh cirq (95% pass).
        self.assertGreater(d["qiskit"], d["cirq"])
        os.unlink(path)


if __name__ == "__main__":
    unittest.main()


class TestKlDistillLoss(unittest.TestCase):
    """Smoke tests for the KL loss function in training.qwen_sft_peft_kl."""

    def test_loss_is_positive(self):
        import torch

        from training.qwen_sft_peft_kl import kl_distill_loss

        T, V, _K = 4, 100, 3
        torch.manual_seed(0)
        student_logits = torch.randn(T, V, dtype=torch.float32)
        teacher_token_ids = torch.tensor([10, 20, 30, 40], dtype=torch.long)
        teacher_logprob_argmax = torch.tensor([-0.1, -0.2, -0.3, -0.4], dtype=torch.float32)
        teacher_topk_token_ids = torch.tensor(
            [[11, 12, 13], [21, 22, 23], [31, 32, 33], [41, 42, 43]], dtype=torch.long
        )
        teacher_topk_logprobs = torch.tensor(
            [[-1.0, -2.0, -3.0], [-1.1, -2.1, -3.1], [-1.2, -2.2, -3.2], [-1.3, -2.3, -3.3]],
            dtype=torch.float32,
        )
        nll_labels = torch.tensor([10, 20, 30, 40], dtype=torch.long)
        loss, stats = kl_distill_loss(
            student_logits_at_positions=student_logits,
            teacher_token_ids=teacher_token_ids,
            teacher_logprob_argmax=teacher_logprob_argmax,
            teacher_topk_token_ids=teacher_topk_token_ids,
            teacher_topk_logprobs=teacher_topk_logprobs,
            nll_labels=nll_labels,
            torch_module=torch,
            ignore_index=-100,
            kl_coeff=0.5,
            nll_coeff=0.5,
            temperature=1.0,
        )
        self.assertGreater(loss.item(), 0)
        self.assertGreater(stats["nll"], 0)
        self.assertGreaterEqual(stats["kl"], 0)
        self.assertEqual(stats["valid_tokens"], 4.0)

    def test_empty_returns_zero(self):
        import torch

        from training.qwen_sft_peft_kl import kl_distill_loss

        empty = torch.zeros(0, dtype=torch.long)
        empty_f = torch.zeros(0, dtype=torch.float32)
        empty_logits = torch.zeros(0, 10, dtype=torch.float32)
        loss, stats = kl_distill_loss(
            student_logits_at_positions=empty_logits,
            teacher_token_ids=empty,
            teacher_logprob_argmax=empty_f,
            teacher_topk_token_ids=empty.unsqueeze(0) if empty.numel() else empty.reshape(0, 0),
            teacher_topk_logprobs=empty_f.unsqueeze(0)
            if empty_f.numel()
            else empty_f.reshape(0, 0),
            nll_labels=empty,
            torch_module=torch,
            ignore_index=-100,
            kl_coeff=0.5,
            nll_coeff=0.5,
            temperature=1.0,
        )
        self.assertEqual(loss.item(), 0.0)
        self.assertEqual(stats["nll"], 0.0)

    def test_kl_coeff_zero_uses_only_nll(self):
        import torch

        from training.qwen_sft_peft_kl import kl_distill_loss

        T, V, _K = 2, 50, 3
        torch.manual_seed(1)
        student_logits = torch.randn(T, V, dtype=torch.float32)
        teacher_token_ids = torch.tensor([5, 6], dtype=torch.long)
        teacher_logprob_argmax = torch.tensor([-0.1, -0.2], dtype=torch.float32)
        teacher_topk_token_ids = torch.tensor([[7, 8, 9], [10, 11, 12]], dtype=torch.long)
        teacher_topk_logprobs = torch.tensor(
            [[-1.0, -2.0, -3.0], [-1.1, -2.1, -3.1]], dtype=torch.float32
        )
        nll_labels = torch.tensor([5, 6], dtype=torch.long)
        # With kl_coeff=0, total should equal nll_coeff * nll
        loss, stats = kl_distill_loss(
            student_logits_at_positions=student_logits,
            teacher_token_ids=teacher_token_ids,
            teacher_logprob_argmax=teacher_logprob_argmax,
            teacher_topk_token_ids=teacher_topk_token_ids,
            teacher_topk_logprobs=teacher_topk_logprobs,
            nll_labels=nll_labels,
            torch_module=torch,
            ignore_index=-100,
            kl_coeff=0.0,
            nll_coeff=1.0,
            temperature=1.0,
        )
        self.assertAlmostEqual(loss.item(), stats["nll"], places=4)
