<!-- GENERATED from harness/contracts.py — DO NOT EDIT -->
# DEPLOY-INTEGRITY — role card
Authority: verify tree == bundle == box (per-file sha256 from the MANIFEST list, never globs).

Invariants (from harness/contracts.py):
- [probe_after_every_change] No claimed fix without a probe: every change lands with a deterministic probe artifact.
  - enforced by: tdd.py
- [box_ports_fixed] Box daemon ports are pinned in ONE config; scripts must import them, never re-declare.
  - enforced by: harness_config.py, lint_gate.py
