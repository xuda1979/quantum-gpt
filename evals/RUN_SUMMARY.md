# Evaluation runs summary

Total runs with scorecards: **49**

## OpenAI baseline (6)

| run | model | style | pass | scored_at_utc |
|---|---|---|---|---|
| openai-10task-baseline | gpt-5.4 | direct | 10/10 | 2026-03-13T08:06:11 |
| openai-12task-baseline | gpt-5.4 | direct | 12/12 | 2026-03-13T08:49:09 |
| openai-16task-baseline | gpt-5.4 | direct | 16/16 | 2026-03-13T12:17:52 |
| openai-17task-baseline | gpt-5.4 | direct | 17/17 | 2026-03-13T14:04:10 |
| openai-baseline-smoke | ? | ? | 6/6 | 2026-03-13T06:34:08 |
| openai-meta-compare | gpt-5.4 | direct | 6/6 | 2026-03-13T07:34:51 |

## Harness smoke / style (5)

| run | model | style | pass | scored_at_utc |
|---|---|---|---|---|
| adapter-smoke | ? | ? | 6/6 | 2026-03-13T06:00:15 |
| backend-meta-smoke | reference-copy | direct | 6/6 | 2026-03-13T07:18:38 |
| exec-smoke | ? | ? | 0/6 | 2026-03-13T02:04:14 |
| style-direct | ? | ? | 6/6 | 2026-03-13T02:02:10 |
| style-plan | ? | ? | 6/6 | 2026-03-13T02:02:10 |

## Qwen/Omnicoder local FT (6)

| run | model | style | pass | scored_at_utc |
|---|---|---|---|---|
| omnicoder-quantum-generalization-holdout-base-omnicoder9b-20260410 | ? | repair_focused | 44/44 | 2026-04-17T03:31:59 |
| qwen25-quantum-generalization-holdout-base-local | ? | repair_focused | 25/25 | 2026-03-30T14:23:35 |
| qwen25-quantum-generalization-holdout-base-rerun-20260412 | ? | repair_focused | 22/26 | 2026-04-12T07:57:08 |
| qwen25-quantum-generalization-holdout-clean-local | ? | repair_focused | 21/25 | 2026-03-30T14:40:03 |
| qwen25-quantum-generalization-holdout-fastlora-small-20260412 | ? | repair_focused | 22/26 | 2026-04-12T07:51:04 |
| qwen25-quantum-generalization-holdout-fastlora-tiny-20260412 | ? | repair_focused | 21/25 | 2026-03-30T14:40:03 |

## Huanxin-trained (ai1/ai2) (5)

| run | model | style | pass | scored_at_utc |
|---|---|---|---|---|
| qwen25-quantum-generalization-holdout-ai1-continue-safe-v2-rerun-20260412T220828CST | ? | repair_focused | 22/26 | 2026-04-12T14:11:08 |
| qwen25-quantum-generalization-holdout-ai1-enriched-v1-rerun-20260412T224900CST | ? | repair_focused | 22/26 | 2026-04-12T15:15:19 |
| qwen25-quantum-generalization-holdout-ai1-ft-20260412T1622CST | ? | repair_focused | 21/25 | 2026-03-30T14:40:03 |
| qwen25-quantum-generalization-holdout-ai1-ft-rerun-20260412T1627CST | ? | repair_focused | 22/26 | 2026-04-12T08:29:16 |
| qwen25-quantum-generalization-holdout-ai1-stage2-rerun-20260412T181013CST | ? | repair_focused | 22/26 | 2026-04-12T10:13:54 |

## Omnicoder delivery (2)

| run | model | style | pass | scored_at_utc |
|---|---|---|---|---|
| omnicoder-delivery-pass1-v1 | ? | repair_focused | 15/25 | 2026-03-30T04:12:28 |
| omnicoder-quantum-generalization-holdout-8npu-fastiter-eval-20260409T122347Z | ? | repair_focused | 24/26 | 2026-04-09T12:27:00 |

## Gemma4 26B (1)

| run | model | style | pass | scored_at_utc |
|---|---|---|---|---|
| gemma4-26b-a4b-it-quantum-generalization-holdout-base-20260413 | ? | repair_focused | 38/38 | 2026-04-13T19:38:05 |

## Qwen2.5-1.5B RAG sweep (24)

| run | model | style | pass | scored_at_utc |
|---|---|---|---|---|
| qwen25-1p5b-no-rag-20260422T160635Z | ? | ? | 28/44 | 2026-04-22T16:15:20 |
| qwen25-1p5b-no-rag-20260428T020739Z | ? | ? | 40/44 | 2026-04-28T02:13:57 |
| qwen25-1p5b-no-rag-20260428T021435Z | ? | ? | 40/44 | 2026-04-28T02:18:44 |
| qwen25-1p5b-no-rag-20260428T023559Z | ? | ? | 43/44 | 2026-04-28T02:36:23 |
| qwen25-1p5b-no-rag-20260428T031827Z | ? | ? | 42/44 | 2026-04-28T03:24:53 |
| qwen25-1p5b-no-rag-20260428T052701Z | ? | ? | 43/44 | 2026-04-28T05:28:32 |
| qwen25-1p5b-with-rag-20260422T161520Z | ? | ? | 13/44 | 2026-04-22T16:21:32 |
| qwen25-1p5b-with-rag-20260428T022412Z | ? | ? | 43/44 | 2026-04-28T02:24:32 |
| qwen25-1p5b-with-rag-20260428T022634Z | ? | ? | 43/44 | 2026-04-28T02:26:53 |
| qwen25-1p5b-with-rag-20260428T022742Z | ? | ? | 43/44 | 2026-04-28T02:28:05 |
| qwen25-1p5b-with-rag-20260428T022848Z | ? | ? | 43/44 | 2026-04-28T02:29:11 |
| qwen25-1p5b-with-rag-20260428T023006Z | ? | ? | 43/44 | 2026-04-28T02:30:45 |
| qwen25-1p5b-with-rag-20260428T023159Z | ? | ? | 43/44 | 2026-04-28T02:32:40 |
| qwen25-1p5b-with-rag-20260428T023402Z | ? | ? | 43/44 | 2026-04-28T02:34:26 |
| qwen25-1p5b-with-rag-20260428T023455Z | ? | ? | 44/44 | 2026-04-28T02:35:23 |
| qwen25-1p5b-with-rag-20260428T032453Z | ? | ? | 42/44 | 2026-04-28T03:28:59 |
| qwen25-1p5b-with-rag-20260428T050207Z | ? | ? | 43/44 | 2026-04-28T05:02:58 |
| qwen25-1p5b-with-rag-20260428T050439Z | ? | ? | 43/44 | 2026-04-28T05:05:22 |
| qwen25-1p5b-with-rag-20260428T050701Z | ? | ? | 43/44 | 2026-04-28T05:07:59 |
| qwen25-1p5b-with-rag-20260428T050852Z | ? | ? | 43/44 | 2026-04-28T05:09:45 |
| qwen25-1p5b-with-rag-20260428T051127Z | ? | ? | 43/44 | 2026-04-28T05:12:54 |
| qwen25-1p5b-with-rag-20260428T051506Z | ? | ? | 43/44 | 2026-04-28T05:16:01 |
| qwen25-1p5b-with-rag-20260428T051642Z | ? | ? | 43/44 | 2026-04-28T05:17:45 |
| qwen25-1p5b-with-rag-20260428T052421Z | ? | ? | 44/44 | 2026-04-28T05:25:40 |

## Domain breakdown (quantum / software) for substantive runs

| run | quantum | software | other domains |
|---|---|---|---|
| adapter-smoke | 3/3 | 3/3 | - |
| backend-meta-smoke | 3/3 | 3/3 | - |
| exec-smoke | 0/3 | 0/3 | - |
| gemma4-26b-a4b-it-quantum-generalization-holdout-base-20260413 | 25/25 | 13/13 | - |
| omnicoder-delivery-pass1-v1 | 7/12 | 8/13 | - |
| omnicoder-quantum-generalization-holdout-8npu-fastiter-eval-20260409T122347Z | 11/13 | 13/13 | - |
| omnicoder-quantum-generalization-holdout-base-omnicoder9b-20260410 | 31/31 | 13/13 | - |
| openai-10task-baseline | 5/5 | 5/5 | - |
| openai-12task-baseline | 6/6 | 6/6 | - |
| openai-16task-baseline | 8/8 | 8/8 | - |
| openai-17task-baseline | 8/8 | 9/9 | - |
| openai-baseline-smoke | 3/3 | 3/3 | - |
| openai-meta-compare | 3/3 | 3/3 | - |
| qwen25-1p5b-no-rag-20260422T160635Z | 15/31 | 13/13 | - |
| qwen25-1p5b-no-rag-20260428T020739Z | 27/31 | 13/13 | - |
| qwen25-1p5b-no-rag-20260428T021435Z | 27/31 | 13/13 | - |
| qwen25-1p5b-no-rag-20260428T023559Z | 30/31 | 13/13 | - |
| qwen25-1p5b-no-rag-20260428T031827Z | 29/31 | 13/13 | - |
| qwen25-1p5b-no-rag-20260428T052701Z | 30/31 | 13/13 | - |
| qwen25-1p5b-with-rag-20260422T161520Z | 0/31 | 13/13 | - |
| qwen25-1p5b-with-rag-20260428T022412Z | 30/31 | 13/13 | - |
| qwen25-1p5b-with-rag-20260428T022634Z | 30/31 | 13/13 | - |
| qwen25-1p5b-with-rag-20260428T022742Z | 30/31 | 13/13 | - |
| qwen25-1p5b-with-rag-20260428T022848Z | 30/31 | 13/13 | - |
| qwen25-1p5b-with-rag-20260428T023006Z | 30/31 | 13/13 | - |
| qwen25-1p5b-with-rag-20260428T023159Z | 30/31 | 13/13 | - |
| qwen25-1p5b-with-rag-20260428T023402Z | 30/31 | 13/13 | - |
| qwen25-1p5b-with-rag-20260428T023455Z | 31/31 | 13/13 | - |
| qwen25-1p5b-with-rag-20260428T032453Z | 29/31 | 13/13 | - |
| qwen25-1p5b-with-rag-20260428T050207Z | 30/31 | 13/13 | - |
| qwen25-1p5b-with-rag-20260428T050439Z | 30/31 | 13/13 | - |
| qwen25-1p5b-with-rag-20260428T050701Z | 30/31 | 13/13 | - |
| qwen25-1p5b-with-rag-20260428T050852Z | 30/31 | 13/13 | - |
| qwen25-1p5b-with-rag-20260428T051127Z | 30/31 | 13/13 | - |
| qwen25-1p5b-with-rag-20260428T051506Z | 30/31 | 13/13 | - |
| qwen25-1p5b-with-rag-20260428T051642Z | 30/31 | 13/13 | - |
| qwen25-1p5b-with-rag-20260428T052421Z | 31/31 | 13/13 | - |
| qwen25-quantum-generalization-holdout-ai1-continue-safe-v2-rerun-20260412T220828CST | 9/13 | 13/13 | - |
| qwen25-quantum-generalization-holdout-ai1-enriched-v1-rerun-20260412T224900CST | 9/13 | 13/13 | - |
| qwen25-quantum-generalization-holdout-ai1-ft-20260412T1622CST | 8/12 | 13/13 | - |
| qwen25-quantum-generalization-holdout-ai1-ft-rerun-20260412T1627CST | 9/13 | 13/13 | - |
| qwen25-quantum-generalization-holdout-ai1-stage2-rerun-20260412T181013CST | 9/13 | 13/13 | - |
| qwen25-quantum-generalization-holdout-base-local | 12/12 | 13/13 | - |
| qwen25-quantum-generalization-holdout-base-rerun-20260412 | 9/13 | 13/13 | - |
| qwen25-quantum-generalization-holdout-clean-local | 8/12 | 13/13 | - |
| qwen25-quantum-generalization-holdout-fastlora-small-20260412 | 9/13 | 13/13 | - |
| qwen25-quantum-generalization-holdout-fastlora-tiny-20260412 | 8/12 | 13/13 | - |
| style-direct | 3/3 | 3/3 | - |
| style-plan | 3/3 | 3/3 | - |
