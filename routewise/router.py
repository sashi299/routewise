from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import asdict, dataclass
from typing import Any

import httpx

from .cost import TokenPrice, calculate_cost
from .verifier import verify_invoice

log = logging.getLogger("routewise")


@dataclass
class ModelResult:
    tier: str
    model_id: str
    output: dict[str, Any]
    input_tokens: int
    output_tokens: int
    latency_ms: float
    cost_usd: float
    verification: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class NebiusClient:
    def __init__(self, base_url: str, api_key: str, timeout: float = 45, retries: int = 3):
        if not api_key:
            raise RuntimeError("NEBIUS_API_KEY is required for live model calls")
        self.base_url, self.api_key, self.timeout, self.retries = base_url.rstrip("/"), api_key, timeout, retries

    async def complete(self, model_id: str, prompt: str) -> tuple[dict[str, Any], int, int]:
        body = {"model": model_id, "messages": [{"role": "user", "content": prompt}], "temperature": 0, "response_format": {"type": "json_object"}}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        last: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=body)
                    response.raise_for_status()
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    usage = data.get("usage", {})
                    return json.loads(content), int(usage.get("prompt_tokens", 0)), int(usage.get("completion_tokens", 0))
            except (httpx.HTTPError, KeyError, json.JSONDecodeError) as exc:
                last = exc
                if attempt < self.retries:
                    await asyncio.sleep(2 ** attempt)
        raise RuntimeError(f"Nebius request failed after retries: {last}")


async def route_invoice(source_text: str, ladder: list[dict[str, Any]], client: NebiusClient, call: Callable[..., Awaitable[tuple[dict[str, Any], int, int]]] | None = None) -> dict[str, Any]:
    call = call or client.complete
    trace: list[ModelResult] = []
    for tier in ladder:
        started = time.perf_counter()
        output, input_tokens, output_tokens = await call(tier["id"], source_text)
        verification = verify_invoice(source_text, output)
        latency_ms = (time.perf_counter() - started) * 1000
        price = TokenPrice(tier["input_usd_per_million"], tier["output_usd_per_million"])
        result = ModelResult(tier=tier["name"], model_id=tier["id"], output=output, input_tokens=input_tokens, output_tokens=output_tokens, latency_ms=latency_ms, cost_usd=calculate_cost(input_tokens, output_tokens, price), verification=verification)
        trace.append(result)
        log.info("model_call", extra={"tier": tier["name"], "latency_ms": latency_ms, "cost_usd": result.cost_usd, "input_tokens": input_tokens, "output_tokens": output_tokens})
        if verification["passed"]:
            return {"answer": output, "trace": [r.as_dict() for r in trace], "selected_tier": tier["name"]}
    return {"answer": trace[-1].output if trace else None, "trace": [r.as_dict() for r in trace], "selected_tier": trace[-1].tier if trace else None}
