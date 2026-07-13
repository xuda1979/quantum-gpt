import ast
import sys

import torch
import torch.nn as nn
import torch.nn.functional as F

src_path = "/Users/daxu/software/quantum-gpt/artifacts/runtime-bundles/omnicoder-qwen35-runtime-c585eea/transformers-src/src/transformers/models/qwen3_5_moe/modeling_qwen3_5_moe.py"
src = open(src_path).read()
tree = ast.parse(src)
cls_src = None
for node in tree.body:
    if isinstance(node, ast.ClassDef) and node.name == "Qwen3_5MoeExperts":
        cls_src = ast.get_source_segment(src, node)
assert cls_src
cls_src = "\n".join(l for l in cls_src.splitlines() if "use_experts_implementation" not in l)
ACT2FN = {"silu": F.silu}
ns = {"torch": torch, "nn": nn, "ACT2FN": ACT2FN}
exec(cls_src, ns)
Experts = ns["Qwen3_5MoeExperts"]


class Cfg:
    num_experts = 8
    hidden_size = 16
    moe_intermediate_size = 32
    hidden_act = "silu"


cfg = Cfg()
torch.manual_seed(1)
exp = Experts(cfg)
nn.init.normal_(exp.gate_up_proj)
nn.init.normal_(exp.down_proj)

T, K = 6, 2
x = torch.randn(T, cfg.hidden_size)
idx = torch.stack([torch.randperm(cfg.num_experts)[:K] for _ in range(T)])
val = torch.softmax(torch.randn(T, K), dim=-1)

x1 = x.clone().requires_grad_(True)
o_stock = exp.forward(x1, idx, val)
o_stock.sum().backward()
g_stock_gu = exp.gate_up_proj.grad.clone()
g_stock_dn = exp.down_proj.grad.clone()
gx_stock = x1.grad.clone()
exp.gate_up_proj.grad = None
exp.down_proj.grad = None

# bind the dense forward from runtime_overlay by execing its body against this class
sys.path.insert(0, "/Users/daxu/software/quantum-gpt")
ro_src = open("/Users/daxu/software/quantum-gpt/training/runtime_overlay.py").read()
ro_tree = ast.parse(ro_src)
fn_src = None
for node in ro_tree.body:
    if isinstance(node, ast.FunctionDef) and node.name == "_patch_qwen35_moe_dense_experts":
        fn_src = ast.get_source_segment(ro_src, node)
# extract just the inner dense_experts_forward def
inner = None
for node in ast.walk(ast.parse(fn_src)):
    if isinstance(node, ast.FunctionDef) and node.name == "dense_experts_forward":
        inner = ast.get_source_segment(fn_src, node)
ns2 = {"torch": torch}
exec(inner, ns2)
Experts.forward = ns2["dense_experts_forward"]

x2 = x.clone().requires_grad_(True)
o_dense = exp.forward(x2, idx, val)
o_dense.sum().backward()
g_dense_gu = exp.gate_up_proj.grad.clone()
g_dense_dn = exp.down_proj.grad.clone()
gx_dense = x2.grad.clone()

print("fwd diff      :", (o_stock - o_dense).abs().max().item())
print("grad gate_up  :", (g_stock_gu - g_dense_gu).abs().max().item())
print("grad down     :", (g_stock_dn - g_dense_dn).abs().max().item())
print("grad input    :", (gx_stock - gx_dense).abs().max().item())
ok = (
    torch.allclose(o_stock, o_dense, atol=1e-4)
    and torch.allclose(g_stock_gu, g_dense_gu, atol=1e-3)
    and torch.allclose(g_stock_dn, g_dense_dn, atol=1e-3)
    and torch.allclose(gx_stock, gx_dense, atol=1e-3)
)
banned = [w for w in ("nonzero", "index_add_", "torch.where", "for ") if w in inner]
print("banned ops in dense forward:", banned)
print("RESULT:", "PASS" if (ok and not banned) else "FAIL")
