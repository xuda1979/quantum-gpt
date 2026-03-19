True workspace-bound repair task.

Public contracts are split across files and must stay compatible through imports:
- pkg.patch_engine.apply_patches(base_state, patches) -> dict
- pkg.reporting.render_conflict_report(result) -> dict
- pkg.models helpers define shared schema behavior used by reporting and tests

The writable candidate surface is only `pkg/patch_engine.py`.
Support modules live under `workspace/pkg/` and are copied into a temp workspace during scoring.
The reference candidate also exists at task-root `pkg/patch_engine.py` so legacy reference scoring and generated overlay paths share the same relative destination.
