# Delivery Registry

这个目录是项目交付物的统一入口，不再要求人肉分别翻：

- `artifacts/model-registry/`
- `artifacts/deliveries/`
- `research/papers/index.json`
- `research/RESEARCH-REPORT.tex`

生成命令：

```bash
python3 scripts/build_delivery_registry.py
```

严格校验模式：

```bash
python3 scripts/build_delivery_registry.py --check
```

重建某个 delivery tarball：

```bash
python3 scripts/build_delivery_artifact.py artifacts/deliveries/<manifest>.json --rewrite-manifest
```

输出文件：

- `index.json`
  - 当前 workspace 的统一交付物索引
  - 汇总模型版本、handoff/delivery 包、papers、canonical research report
  - 同时检查被这些索引引用的路径是否真实存在

设计目标：

- 随着 finetuned model 版本和 research paper 数量增加，保持交付物目录只有一个权威入口
- 让“这份结果对应哪份代码/哪份 paper/哪份 handoff”可追溯
- 把缺失工件变成机器可发现的问题，而不是阅读报告时才发现
- 明确要求 adapter delivery 不只是有 README 和 tokenizer，还必须有真正可加载的 adapter 权重
