from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import statistics
import time
from pathlib import Path
from typing import Any

import yaml

from .router import NebiusClient, route_invoice

FIELDS = ("vendor", "invoice_number", "date", "subtotal", "tax", "total", "currency")


def load_config(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def normalize(value: Any) -> str:
    return "" if value is None else str(value).strip().lower()


def accuracy(answer: dict[str, Any] | None, truth: dict[str, Any]) -> tuple[float, bool]:
    answer = answer or {}
    matches = [normalize(answer.get(field)) == normalize(truth.get(field)) for field in FIELDS]
    return sum(matches) / len(matches), all(matches)


def row_metrics(strategy: str, result: dict[str, Any], truth: dict[str, Any]) -> dict[str, Any]:
    score, exact = accuracy(result.get("answer"), truth)
    trace = result.get("trace", [])
    return {"strategy": strategy, "field_accuracy": score, "exact_match": int(exact), "cost_usd": sum(float(x.get("cost_usd", 0)) for x in trace), "latency_ms": sum(float(x.get("latency_ms", 0)) for x in trace), "tiers_used": ">".join(x.get("tier", "") for x in trace), "selected_tier": result.get("selected_tier", "")}


async def call_strategy(name: str, source: str, truth: dict[str, Any], client: NebiusClient, tiers: list[dict[str, Any]]) -> dict[str, Any]:
    if name == "routewise":
        return await route_invoice(source, tiers, client)
    tier = {"always-small": tiers[0], "always-medium": tiers[1], "always-large": tiers[2]}[name]
    answer, input_tokens, output_tokens = await client.complete(tier["id"], source)
    from .cost import TokenPrice, calculate_cost
    from .verifier import verify_invoice
    started = time.perf_counter()
    verification = verify_invoice(source, answer)
    latency_ms = (time.perf_counter() - started) * 1000
    return {"answer": answer, "selected_tier": tier["name"], "trace": [{"tier": tier["name"], "model_id": tier["id"], "input_tokens": input_tokens, "output_tokens": output_tokens, "latency_ms": latency_ms, "cost_usd": calculate_cost(input_tokens, output_tokens, TokenPrice(tier["input_usd_per_million"], tier["output_usd_per_million"])), "verification": verification}]}


async def run(args: argparse.Namespace) -> None:
    if not os.getenv("NEBIUS_API_KEY"):
        raise SystemExit("NEBIUS_API_KEY is required for live evaluation; no model metrics were fabricated.")
    config = load_config(args.config)
    endpoint = config["endpoint"]
    tiers = [{"name": name, **spec} for name, spec in config["models"].items() if name in ("tier1", "tier2", "tier3")]
    client = NebiusClient(os.getenv("NEBIUS_BASE_URL", endpoint["base_url"]), os.environ["NEBIUS_API_KEY"], endpoint["timeout_seconds"], endpoint["max_retries"])
    rows = [json.loads(line) for line in args.data.open(encoding="utf-8")]
    all_metrics: list[dict[str, Any]] = []
    for item in rows:
        for strategy in ("always-small", "always-medium", "always-large", "routewise"):
            result = await call_strategy(strategy, item["source"], item["ground_truth"], client, tiers)
            all_metrics.append({"id": item["id"], **row_metrics(strategy, result, item["ground_truth"])})
    args.results.mkdir(parents=True, exist_ok=True)
    with (args.results / "per_invoice.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(all_metrics[0]))
        writer.writeheader(); writer.writerows(all_metrics)
    summary = []
    for strategy in ("always-small", "always-medium", "always-large", "routewise"):
        subset = [row for row in all_metrics if row["strategy"] == strategy]
        summary.append({"strategy": strategy, "field_accuracy": statistics.mean(row["field_accuracy"] for row in subset), "exact_match_rate": statistics.mean(row["exact_match"] for row in subset), "total_cost_usd": sum(row["cost_usd"] for row in subset), "avg_latency_ms": statistics.mean(row["latency_ms"] for row in subset), "p95_latency_ms": sorted(row["latency_ms"] for row in subset)[max(0, int(len(subset) * 0.95) - 1)]})
    with (args.results / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0])); writer.writeheader(); writer.writerows(summary)
    (args.results / "metrics.json").write_text(json.dumps({"strategies": summary, "dataset_size": len(rows), "generated_at": time.time()}, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("models.yaml"))
    parser.add_argument("--data", type=Path, default=Path("data/invoices_test.jsonl"))
    parser.add_argument("--results", type=Path, default=Path("results"))
    asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    main()
