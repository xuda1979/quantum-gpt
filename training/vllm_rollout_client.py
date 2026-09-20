"""vLLM rollout client (2026-08-31, CEO Tier-1: the orders-of-magnitude lever).

Replaces per-candidate transformers generate() (~3 tok/s aggregate) with calls
to a vLLM-ascend server (continuous batching + paged attention, 10-50x).

Contract (TDD in tests/test_vllm_rollout_client.py):
- generate_batch(prompt, n, max_tokens, temperature, seed) ->
    list[str] completions (len == n)
- Server down / timeout -> VllmUnavailable exception (caller falls back to
  transformers path; fail-closed, never silent).
- Health check: is_up() -> bool (cached 10s).
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

DEFAULT_BASE = "http://127.0.0.1:8355"


class VllmUnavailable(RuntimeError):
    """Raised when the vLLM rollout server cannot be reached or errors."""


# Injectable opener factory (tests replace this with a mock).
def _default_opener_factory():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


opener_factory = _default_opener_factory


class VllmRolloutClient:
    def __init__(self, base_url: str = DEFAULT_BASE, timeout_s: float = 600.0):
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self._health_ts: float = 0.0
        self._health_ok: bool = False

    def is_up(self, *, force: bool = False) -> bool:
        now = time.time()
        if not force and now - self._health_ts < 10.0:
            return self._health_ok
        try:
            req = urllib.request.Request(self.base_url + "/health")
            with urllib.request.urlopen(req, timeout=5) as resp:
                self._health_ok = resp.status == 200
        except Exception:
            self._health_ok = False
        self._health_ts = now
        return self._health_ok

    def generate_batch(
        self,
        prompt: str,
        n: int,
        max_tokens: int,
        temperature: float,
        seed: int | None = None,
        stop: list[str] | None = None,
        suppress_token_ids: list[int] | None = None,
    ) -> list[str]:
        if n <= 0:
            return []
        payload = {
            "prompt": prompt,
            "n": n,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 1.0,
        }
        if seed is not None:
            payload["seed"] = seed
        if stop:
            payload["stop"] = stop
        if suppress_token_ids:
            ids = sorted(set(suppress_token_ids))
            payload["bad_words_ids"] = [ids]
        req = urllib.request.Request(
            self.base_url + "/v1/completions",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        opener = opener_factory()
        try:
            with opener.open(req, timeout=self.timeout_s) as resp:
                body = json.loads(resp.read().decode())
        except Exception as exc:
            raise VllmUnavailable(repr(exc)[:200]) from exc
        choices = body.get("choices") or []
        outs = [c.get("text", "") for c in choices]
        if len(outs) != n:
            raise VllmUnavailable(f"expected {n} completions, got {len(outs)}")
        return outs


def generate_with_fallback(
    client: VllmRolloutClient | None,
    prompt: str,
    n: int,
    max_tokens: int,
    temperature: float,
    fallback_fn,
    seed: int | None = None,
    stop: list[str] | None = None,
    suppress_token_ids: list[int] | None = None,
) -> tuple[list[str], str]:
    """Try vLLM; on unavailability fall back to the transformers path.
    Returns (completions, engine_used) where engine_used in {\"vllm\", \"hf\"}."""
    if client is not None and client.is_up():
        try:
            return (
                client.generate_batch(
                    prompt, n, max_tokens, temperature, seed, stop, suppress_token_ids
                ),
                "vllm",
            )
        except VllmUnavailable:
            pass
    return fallback_fn(prompt, n, max_tokens, temperature), "hf"
