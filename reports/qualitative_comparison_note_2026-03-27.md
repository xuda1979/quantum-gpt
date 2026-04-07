# Qualitative Summary: reports/base_vs_adapter_outputs_interface_prefix_smoke4_matched_full5.json

## base
- total_examples: `5`
- syntax_ok: `3`
- starts_like_code: `5`
- code_fence: `5`
- all_required_names_present: `5`
- any_suspicious_anchor_hits: `1`
- avg_reference_key_hits: `1.6`

## adapter
- total_examples: `5`
- syntax_ok: `2`
- starts_like_code: `5`
- code_fence: `0`
- all_required_names_present: `5`
- any_suspicious_anchor_hits: `2`
- avg_reference_key_hits: `1.4`

## Takeaways
- On this 5-example matched interface-prefix slice, the adapter does **not** beat the base model on the current heuristic checks.
- The adapter keeps required function/class names, but it more often drifts on contract anchors (`timestamp` vs `ts`, extra `history`, etc.) and produces syntactically invalid code more often than the base.
- By contrast, older codefirst smoke outputs were much worse overall: both base and adapter often answered in prose or non-code, with `syntax_ok=0/2` and `avg_reference_key_hits=0.0`.
- Combined with run metrics, this suggests the newer interface-prefix / semantic-v4 formatting materially improved “answer as code” behavior versus the older codefirst smoke setup, but the current adapter still lacks clear qualitative wins over base on fixed contract-heavy tasks.

## Related run metrics
- `outputs/interface-prefix-semantic-v4-8npu-true20-e2-20260326T1627CST/metrics.json`
  - completed_steps: `20`
  - final_eval.loss: `0.6986`
  - final_eval.perplexity: `2.0110`
- `outputs/codefirst-semantic-mix75-8npu-true20-e2-20260326T2118CST/metrics.json`
  - completed_steps: `20`
  - final_eval.loss: `0.7353`
  - final_eval.perplexity: `2.0862`
- On intrinsic eval loss/perplexity, semantic-v4 also beats codefirst-mix75 in the currently available local artifacts.

## Recommendation
- Keep `interface-prefix-semantic-v4` as the stronger default baseline for the next remote qualitative rerun.
- Next concrete step: regenerate a fresh **true20 qualitative matched report** for the semantic-v4 true20-e2 adapter (5 examples or same fixed slice) and compare it directly against a codefirst-mix75 true20-e2 qualitative report under the same prompt slice and decoding settings.
