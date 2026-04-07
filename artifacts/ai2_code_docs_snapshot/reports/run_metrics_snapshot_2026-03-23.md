# Quantum run summary snapshot

Recent local/remote metrics snapshot extracted from `outputs/*/metrics.json`:

- `fast-lora-qwen25-1p5b-interface-prefix-smoke1`: eval_loss 1.0842, ppl 2.9571
- `fast-lora-qwen25-1p5b-interface-prefix-smoke4`: eval_loss 0.9487, ppl 2.5824
- `fast-lora-qwen25-1p5b-interface-prefix-smoke8`: eval_loss 0.9025, ppl 2.4659
- `fast-lora-qwen25-1p5b-mini`: eval_loss 0.9136, ppl 2.4934
- `fast-lora-qwen25-1p5b-codefirst-mini`: eval_loss 0.8788, ppl 2.4080
- `fast-lora-qwen25-1p5b-interface-prefix-semantic-v4-smoke20`: eval_loss 0.8371, ppl 2.3096
- `interface-prefix-semantic-v4-8npu-20step`: eval_loss 0.8358, ppl 2.3067

Observation:
- The best currently captured metrics are now from `interface-prefix-semantic-v4-8npu-20step`.
- Relative to the previous best `fast-lora-qwen25-1p5b-codefirst-mini`, this semantic-v4 run improved eval_loss by about 0.0430 and eval_perplexity by about 0.1013.
- Relative to `fast-lora-qwen25-1p5b-interface-prefix-semantic-v4-smoke20`, the improvement is small but real: about 0.0012 lower eval_loss and about 0.0028 lower eval_perplexity.
- Important correction: despite the `20step` / `smoke20` naming, both recovered semantic-v4 artifacts currently show `max_steps: 10` in `metrics.json`. Treat them as 10-step runs until a true 20-step artifact is launched and recovered.
- The semantic interface-prefix data continues to outperform both the earlier pure interface-prefix smokes and the codefirst-mini baseline at this recovered 10-step remote smoke scale.
- The next sensible remote experiment is a verified true 20-step semantic-v4 run or a codefirst+semantic mixture, while separately tightening the flaky S3 result-pull path.
