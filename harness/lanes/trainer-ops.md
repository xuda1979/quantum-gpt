<!-- GENERATED from harness/contracts.py — DO NOT EDIT -->
# TRAINER-OPS — role card
Authority: launch/monitor GRPO training on ASI3; publish checkpoints to the bus.

Invariants (from harness/contracts.py):
- [launch_detached_setsid] Training launches detached (setsid + nohup), never in-line in a card.
  - enforced by: launch_training.py, auto_launch_training.py
- [boot_verify_after_launch] Every training launch is boot-verified (process alive + probe file written).
  - enforced by: boot_verify_training.py
- [checkpoint_bus_manifest] Trainer publishes each completed checkpoint to the NAS bus via manifest.json.
  - enforced by: checkpoint_publisher.py, eval_watcher.py
- [probe_after_every_change] No claimed fix without a probe: every change lands with a deterministic probe artifact.
  - enforced by: tdd.py
- [no_training_without_compile_gate] Training never launches until the on-box tree compiles (py_compile sweep).
  - enforced by: launch_training.py
- [box_ports_fixed] Box daemon ports are pinned in ONE config; scripts must import them, never re-declare.
  - enforced by: harness_config.py, lint_gate.py
