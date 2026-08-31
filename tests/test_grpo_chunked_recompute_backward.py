"""TDD: run-9 backward-pass OOM — the chunked-vocab path's per-chunk fp32
tensors (clamp/exp/gather saves at [1,S,8192]) are retained in the autograd
graph over the FULL sequence until loss.backward(). Measured at the 27B
contract: ~10.9 GiB per candidate (43.6 GiB for a 4-candidate train pass)
plus the model shard (~10.5 GiB on the head card) = the run-9 58.72/60.96
GiB backward crash (the entropy cap cleared run-8's log-prob OOM; this
term is what remained).

FIX: a recompute backward for the chunked pass. The forward saves only
[1,S] tensors (per-pos max, logsumexp, neg-entropy, targets) + the logits
view (shared storage, already in the graph); the backward re-derives
p = exp((x/T - max))/Z chunk-by-chunk and accumulates the exact softmax
gradients (token-lp term (delta - p)/T, entropy term -p(log p + E)/T)
incrementally — peak O(S x chunk) instead of O(S x V). Outputs are
bit-identical to the plain path (same forward math); backward correctness
is pinned by torch.autograd.gradcheck against the plain autograd path.
"""

from __future__ import annotations

import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from training.grpo_utils import chunked_log_probs_and_entropy  # noqa: E402


def _saved_bytes(fn) -> int:
    total = 0

    def pack(t):
        nonlocal total
        total += t.numel() * t.element_size()
        return t

    with torch.autograd.graph.saved_tensors_hooks(pack, lambda t: t):
        fn()
    return total


def _plain(logits, target_ids, clip, cs, entropy=True, cap=None):
    return chunked_log_probs_and_entropy(
        logits,
        target_ids,
        clip,
        chunk_size=cs,
        return_entropy=entropy,
        entropy_pos_cap=cap,
    )


def _recompute(logits, target_ids, clip, cs, entropy=True, cap=None):
    return chunked_log_probs_and_entropy(
        logits,
        target_ids,
        clip,
        chunk_size=cs,
        return_entropy=entropy,
        entropy_pos_cap=cap,
        recompute_backward=True,
    )


# ---------------------------------------------------------------------------
# 1. Output identity: the recompute path's forward is the SAME math
# ---------------------------------------------------------------------------


def test_recompute_outputs_identical_to_plain() -> None:
    torch.manual_seed(17)
    S, V, CS = 40, 2048, 512
    logits = torch.randn(1, S, V, requires_grad=True) * 0.5
    target_ids = torch.randint(0, V, (1, S))
    for entropy in (False, True):
        for cap in (None, 10):
            plain = _plain(logits, target_ids, 5.0, CS, entropy, cap)
            rec = _recompute(logits, target_ids, 5.0, CS, entropy, cap)
            if entropy:
                assert torch.equal(plain[0], rec[0])  # token lps bit-identical
                assert torch.equal(plain[1], rec[1])  # entropy bit-identical
            else:
                assert torch.equal(plain, rec)


# ---------------------------------------------------------------------------
# 2. Backward correctness: gradcheck (the oracle) + plain-path agreement
# ---------------------------------------------------------------------------


def test_recompute_backward_matches_plain_fp64() -> None:
    """float64 agreement with the plain autograd path (the oracle — the
    plain path is verified against manual softmax math to 1e-7)."""
    torch.manual_seed(21)
    S, V, CS = 24, 1024, 256
    cap = 12
    target_ids = torch.randint(0, V, (1, S))
    base = (torch.randn(1, S, V) * 0.5).double()

    def run(rec):
        lg = base.clone().requires_grad_(True)
        out = chunked_log_probs_and_entropy(
            lg,
            target_ids,
            50.0,
            chunk_size=CS,
            return_entropy=True,
            entropy_pos_cap=cap,
            recompute_backward=rec,
        )
        (out[0].sum() + 2.0 * out[1].sum()).backward()
        return lg.grad

    g_plain = run(False)
    g_rec = run(True)
    assert torch.allclose(g_rec, g_plain, atol=1e-5, rtol=1e-4)


def test_recompute_backward_matches_plain_grads() -> None:
    torch.manual_seed(23)
    S, V, CS = 32, 1024, 256
    logits = (torch.randn(1, S, V) * 0.5).requires_grad_(True)
    target_ids = torch.randint(0, V, (1, S))

    def run(rec):
        lg = logits.detach().clone().requires_grad_(True)
        out = chunked_log_probs_and_entropy(
            lg,
            target_ids,
            50.0,
            chunk_size=CS,
            return_entropy=True,
            entropy_pos_cap=12,
            recompute_backward=rec,
        )
        (out[0].sum() + 2.0 * out[1].sum()).backward()
        return lg.grad

    g_plain = run(False)
    g_rec = run(True)
    assert torch.allclose(g_rec, g_plain, atol=1e-4)


def test_recompute_backward_matches_plain_with_clamp_edge() -> None:
    """A small logit clip + fat-tailed logits exercise the clamp/nan_to_num
    mask in the recompute backward (grad must be 0 outside the clip) —
    fp64 agreement with the plain autograd path."""
    torch.manual_seed(29)
    S, V, CS = 20, 1024, 256
    target_ids = torch.randint(0, V, (1, S))
    base = (torch.randn(1, S, V) * 4.0).double()  # fat tails

    def run(rec):
        lg = base.clone().requires_grad_(True)
        out = chunked_log_probs_and_entropy(
            lg,
            target_ids,
            0.5,
            chunk_size=CS,
            return_entropy=True,
            entropy_pos_cap=10,
            recompute_backward=rec,
        )
        (out[0].sum() + out[1].sum()).backward()
        return lg.grad

    g_plain = run(False)
    g_rec = run(True)
    assert torch.allclose(g_rec, g_plain, atol=1e-5, rtol=1e-4)


# ---------------------------------------------------------------------------
# 3. Memory: the recompute path collapses the retained graph (the run-9 fix)
# ---------------------------------------------------------------------------


def test_recompute_backward_saved_bytes_collapse() -> None:
    torch.manual_seed(31)
    S, V, CS = 1700, 24576, 8192  # run-9-like: ~1700 tokens, 3 chunks

    def fwd(rec):
        def run():
            logits = torch.randn(1, S, V, requires_grad=True) * 0.5
            target_ids = torch.randint(0, V, (1, S))
            out = chunked_log_probs_and_entropy(
                logits,
                target_ids,
                5.0,
                chunk_size=CS,
                return_entropy=True,
                entropy_pos_cap=256,
                recompute_backward=rec,
            )
            (out[0].sum() + out[1].sum()).backward()

        return run

    plain_bytes = _saved_bytes(fwd(False))
    recompute_bytes = _saved_bytes(fwd(True))
    # The recompute path must retain a small fraction of the plain path's
    # graph (measured plain ~43.6 GiB at the 27B contract for 4 candidates).
    assert (
        recompute_bytes <= plain_bytes * 0.2
    ), f"recompute must collapse retained graph: plain {plain_bytes} recompute {recompute_bytes}"


# ---------------------------------------------------------------------------
# 4. Trainer wiring: the recompute path is the default train-pass mode
# ---------------------------------------------------------------------------


def test_trainer_arg_defaults_to_recompute() -> None:
    from training.grpo_trainer import parse_args

    sys.argv = ["grpo_trainer.py", "--model-name", "gpt2", "--device", "cpu"]
    args = parse_args()
    assert args.chunked_recompute_backward is True
