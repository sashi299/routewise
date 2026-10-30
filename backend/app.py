from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from routewise.router import NebiusClient, route_invoice

app = FastAPI(title="RouteWise API", version="0.1.0")
origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5173,https://5173-itcwxfygx9jtqfinsz4sc-bcae9ca0.sg2.manus.computer").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


class RouteRequest(BaseModel):
    source_text: str = Field(min_length=1)


class RouteResponse(BaseModel):
    answer: dict[str, Any] | None
    selected_tier: str | None
    trace: list[dict[str, Any]]


def runtime() -> tuple[NebiusClient, list[dict[str, Any]]]:
    key = os.getenv("NEBIUS_API_KEY")
    if not key:
        raise HTTPException(status_code=503, detail="NEBIUS_API_KEY is required for live routing")
    config_path = Path(os.getenv("ROUTEWISE_CONFIG", "models.yaml"))
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    endpoint = config["endpoint"]
    client = NebiusClient(os.getenv("NEBIUS_BASE_URL", endpoint["base_url"]), key, endpoint["timeout_seconds"], endpoint["max_retries"])
    tiers = [{"name": name, **spec} for name, spec in config["models"].items() if name in ("tier1", "tier2", "tier3")]
    return client, tiers


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "routewise"}


@app.get("/metrics")
def metrics() -> dict[str, Any]:
    metrics_file = Path("results/metrics.json")
    return json.loads(metrics_file.read_text(encoding="utf-8")) if metrics_file.exists() else {"status": "not_evaluated", "message": "Run with NEBIUS_API_KEY to produce measured metrics."}


@app.post("/route", response_model=RouteResponse)
async def route(request: RouteRequest) -> RouteResponse:
    client, tiers = runtime()
    result = await route_invoice(request.source_text, tiers, client)
    return RouteResponse(**result)


@app.post("/compare")
async def compare(request: RouteRequest) -> dict[str, Any]:
    client, tiers = runtime()
    routewise = await route_invoice(request.source_text, tiers, client)
    large = await route_invoice(request.source_text, [tiers[-1]], client)
    return {"routewise": routewise, "always_large": large}


@app.post("/route/stream")
async def route_stream(request: RouteRequest) -> StreamingResponse:
    async def events():
        yield "event: status\ndata: " + json.dumps({"step": "received", "message": "Task received"}) + "\n\n"
        try:
            client, tiers = runtime()
            yield "event: status\ndata: " + json.dumps({"step": "tier1", "message": "Trying the cheapest model"}) + "\n\n"
            result = await route_invoice(request.source_text, tiers, client)
            yield "event: result\ndata: " + json.dumps(result) + "\n\n"
        except HTTPException as exc:
            yield "event: error\ndata: " + json.dumps({"message": exc.detail}) + "\n\n"
        except (RuntimeError, OSError, ValueError, KeyError) as exc:
            yield "event: error\ndata: " + json.dumps({"message": str(exc)}) + "\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")


static_dir = Path(__file__).resolve().parents[1] / "frontend" / "dist"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
