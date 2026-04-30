# 新闻稿：Qwen3.6-27B 量子 RAG 本地版正式发布

今日，Qwen3.6-27B 量子 RAG 本地版正式发布。该版本面向量子编程、量子 SDK 使用、量子语言安装与量子开发资料查询等场景，帮助用户在本地环境中获得更可靠的量子文档依据。

本次发布聚焦 Qwen3.6-27B 单一模型路线，并强烈建议本地用户使用 4-bit Q4_K_M 量化版本。该量化文件已在本地完成下载、文件检查和发布链路验证，模型文件大小为 16,817,244,384 bytes。

Qwen3.6-27B 量子 RAG 本地版内置量子文档检索增强能力。用户提问后，系统会先从本地量子文档索引中检索相关资料，再将命中文档注入 Qwen3.6-27B 的回答上下文，使回答能够围绕实际文档内容展开。

本次 RAG 索引覆盖 16 个量子文档源，包含 968 个外部文档文件、13,621 个检索片段和 996 个文档来源。文档范围覆盖 Qiskit、Cirq、PennyLane、Amazon Braket、CUDA-Q、QuTiP、pyQuil、OpenFermion、Mitiq、PyZX、TKET、Q# / Azure Quantum、TensorCircuit、Strawberry Fields、ProjectQ 和 Arclight ISQ。

在本地用户问题检索测试中，Qwen3.6-27B 量子 RAG 本地版取得了明确提升：可引用文档覆盖率从直接回答基线的 0/5 提升到 5/5；对应文档源 top-1 命中从 0/5 提升到 5/5；检索 MRR 从 0.0 提升到 1.0；用户问题检索集 hit@3 达到 5/5。

本次测试集包含 5 道用户真实关心的问题类型，覆盖 Arclight ISQ 安装、Qiskit Bell pair 与 measurement counts、PennyLane VQE workflow、Cirq circuit measurement 和 Amazon Braket local simulator。5 道题均 top-1 命中对应文档源。

发布前，本地预检、用户问题检索集和测试套件均已通过。当前测试套件结果为 124 passed。

完整安装说明、使用方法、4-bit 量化建议、RAG 构成、测试题目和实测结果已集中写入 README.md，用户阅读 README.md 即可完成本地安装和使用。
