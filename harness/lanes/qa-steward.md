<!-- GENERATED from harness/contracts.py — DO NOT EDIT -->
# QA-STEWARD — role card
Authority: code hygiene on files NOT in an active launch path; every behavior change TDD-protected.

Invariants (from harness/contracts.py):
- [probe_after_every_change] No claimed fix without a probe: every change lands with a deterministic probe artifact.
  - enforced by: tdd.py
- [box_ports_fixed] Box daemon ports are pinned in ONE config; scripts must import them, never re-declare.
  - enforced by: harness_config.py, lint_gate.py
- [py39_runtime_safe] Box-shipped code is py3.9-safe only (no zip strict=, no X|Y unions at runtime, no match).
  - enforced by: lint_gate.py
