"""Comprehensive evaluation subsystem for quantum-gpt R&D iteration.

Entry points:
  evals/subsystem/harness.py     — full pass@1 harness (NPU-resident, runs on Huanxin)
  evals/subsystem/analyzer.py    — offline analysis & comparison of eval JSON outputs
  evals/subsystem/reporter.py    — generates Markdown/HTML reports for the R&D cycle
  evals/subsystem/tracker.py     — training-aware eval tracker (watches training, auto-launches eval)
  evals/subsystem/dataset_gap.py — analyzes failures to recommend next dataset additions
"""
