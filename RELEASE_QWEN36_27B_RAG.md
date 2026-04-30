# 发布稿：Qwen3.6-27B 量子 RAG 本地版

今天发布 `Qwen3.6-27B + 量子 RAG` 本地一键安装版。

这个版本面向量子编程和量子 SDK 问答场景：用户执行一个安装脚本，就可以在本地下载 Qwen3.6-27B GGUF 模型，抓取 Qiskit、Cirq、PennyLane、Amazon Braket、CUDA-Q、QuTiP、OpenFermion、Arclight ISQ 等量子文档，建立本地混合检索索引，并通过 `llama.cpp` 启动 CPU-only 本地服务。

本版本的核心变化：

- 一键安装：`scripts/install_qwen36_rag_local.sh`
- 默认模型：`unsloth/Qwen3.6-27B-GGUF`
- 默认量化：`Qwen3.6-27B-Q4_K_M.gguf`
- 本地推理：CPU-only，不使用本地 GPU/NPU
- 本地 RAG：BM25 + TF-IDF/SVD 混合检索
- 文档来源：量子 SDK 官方或稳定文档入口
- 查询入口：`scripts/query_qwen36_rag_local.sh`
- 预检入口：`scripts/check_qwen36_rag_local.py`

RAG 的作用是让 27B 模型回答前先检索本地量子文档，把相关 API、安装说明和算法背景注入上下文。相比纯模型记忆，这个版本更适合处理量子 SDK API、安装步骤、小众量子语言和近期文档变化。

本地发布验证已经完成：

- 27B GGUF 下载路径验证完成。
- 文档抓取流程完成过 16 个来源、968 个外部文档文件。
- RAG 索引完成过 13,621 个 chunks、996 个 sources。
- Arclight ISQ 安装问题检索第一名命中官方安装页。
- 发布测试 `123 passed`。

使用方式：

```bash
scripts/install_qwen36_rag_local.sh
scripts/check_qwen36_rag_local.py
scripts/start_qwen36_rag_local.sh
scripts/query_qwen36_rag_local.sh "How do I build a Bell pair in Qiskit?"
```

注意：Qwen3.6-27B 是大模型。本地 CPU-only 可以完成下载、索引和预检链路，但在 16GB 机器上本地实测 1 token 生成 180 秒超时。这个版本优先保证安装链路、文档检索、引用式 RAG 问答和可复现发布流程；真实交互推荐 32GB 以上内存。

本地硬件建议：最低链路验证需要 16GB 内存和约 25GB 可用磁盘；真实交互推荐 32GB 以上内存和 40GB 以上可用磁盘。用户必须使用 GGUF 量化模型；默认 `Q4_K_M`，可通过 `--quantization Q5_K_XL` 等参数切换更高量化档位。

本地 RAG 前后对比已经测试：同一 Arclight ISQ 安装问题，无 RAG 没有文档上下文；启用 RAG 后 top-1 命中 Arclight ISQ install 文档，并注入 14,157 字符上下文。由于 16GB 本机 27B Q4 生成超时，本次不声称完整生成质量 A/B 分数。
