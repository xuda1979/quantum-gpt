# OmniCoder 9B Semantic-v4 2-NPU Run

## Run

- Output dir: `outputs/interface-prefix-omnicoder9b-semantic-v4-2npu-true20-20260329T2219CST`
- Model: `models/OmniCoder-9B`
- Train file: `data/generated/fast-mini-interface-prefix-semantic-v4/train.jsonl`
- Eval file: `data/generated/fast-mini-interface-prefix-semantic-v4/eval.jsonl`
- Devices: `ASCEND_RT_VISIBLE_DEVICES=6,7`
- World size: `2`
- Max steps: `20`
- Gradient accumulation: `2`
- Max length: `512`

## Result

- `completed_steps`: `20`
- `train_examples`: `160`
- `eval_examples`: `32`
- `final_eval.loss`: `0.3727272283285856`
- `final_eval.perplexity`: `1.4516883063761739`
- Step `20` record:
  - `train_loss`: `0.16293290257453918`
  - `eval_loss`: `0.37272723438218236`
  - `eval_perplexity`: `1.4516883151641096`

## Comparison

Reference run already in workspace:

- Qwen semantic-v4 true20:
  - dir: `outputs/interface-prefix-semantic-v4-8npu-true20-e2-20260326T1627CST`
  - `final_eval.loss`: `0.6986174695193768`
  - `final_eval.perplexity`: `2.0109705566192857`

Observed difference:

- OmniCoder 9B `final_eval.loss` is lower by about `0.3259`
- OmniCoder 9B `final_eval.perplexity` is lower by about `0.5593`

## Notes

- This is not an apples-to-apples hardware comparison:
  - OmniCoder ran on `2` free NPUs
  - the Qwen reference ran on `8` NPUs
- It is still a useful signal:
  - OmniCoder 9B now has a verified nontrivial semantic-v4 fine-tune result in this workspace
  - DDP/HCCL is validated on free devices `6,7`
  - the remaining 8-NPU blocker is shared-cluster occupancy on NPUs `0-5`, not trainer correctness
