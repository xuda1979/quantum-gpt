Tiny multi-file repair task.

Public contract expected by tests:
- candidate.apply_patches(base_state, patches) -> dict
- candidate.render_conflict_report(result) -> dict

The point is not just local patch correctness. Reporting must remain backward-compatible with the expected summary shape.
