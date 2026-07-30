# Quantum Dedup 1k GLM5.2 Soft Distill V3 - Analysis

Generated: 2026-07-29T20:12:22.041800

Total samples: 1000
Fixed samples: 55
Pass rate target: 100%

## Overview

This file contains the analysis of all 1000 training samples in the
quantum_dedup_1k_glm52_soft_distill_v3 dataset. Each sample consists of a
quantum programming question and corresponding Python code.

## Summary of Fixes Applied

55 rows were fixed to ensure all code runs correctly. The fixes fall into
the following categories:

| Category | Count | Description |
|----------|-------|-------------|
| braket_numba_cache | 17 | Added NUMBA_DISABLE_CACHE=1 for Python 3.14 compatibility |
| qsharp_modern_syntax | 11 | Rewrote Q# code to use qsharp.init() + qsharp.eval() |
| mindspore_not_installed | 7 | Replaced MindSpore Quantum with Qiskit (not installable on Python 3.14) |
| qutip_wigner_tuple | 4 | Added tuple handling for qutip wigner return value |
| mitiq_not_installed | 2 | Implemented CDR/ZNE manually with cirq |
| pyquil_broken | 2 | Used numpy/direct implementation (pyQuil broken on Python 3.14) |
| Other API changes | 12 | Various import/API fixes for pytket, qiskit, pennylane, etc. |
| **Total** | **55** | |