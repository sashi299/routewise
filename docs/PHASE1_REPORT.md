# RouteWise Build Report

## Delivered

- Reproducible seeded invoice generator in `routewise/data.py`.
- Dataset generated at `data/invoices.jsonl` with **150** records.
- Split generated at `data/invoices_train.jsonl` with **50** records and `data/invoices_test.jsonl` with **100** records.
- Pydantic invoice schema with line-item, amount, currency, and date fields.
- Layered verifier for schema validity, arithmetic consistency, and scalar grounding.
- Token cost calculator and async Nebius client/router interfaces.
- FastAPI endpoint contract and SSE progress endpoint.
- React/Vite dashboard skeleton with live routing trace panel.
- Pytest tests, Ruff linting, GitHub Actions CI, Docker/Render/Netlify manifests.

## Validation evidence

- `pytest -q`: **3 passed**.
- `ruff check .`: **passed**.
- `npm run build`: **passed**.
- `GET /health`: `{"status":"ok","service":"routewise"}`.
- API preview: https://8000-itcwxfygx9jtqfinsz4sc-bcae9ca0.sg2.manus.computer
- Dashboard preview: https://5173-itcwxfygx9jtqfinsz4sc-bcae9ca0.sg2.manus.computer

## Explicit blocker

`NEBIUS_API_KEY` is not present in the execution environment. Therefore the live model evaluation was not run, and this project does **not** report invented field accuracy, exact-match rate, cost, latency, p95 latency, escalation rate, or classifier precision/recall. The evaluation command fails explicitly until a valid key is supplied.

The model ladder and prices are configuration-driven in `models.yaml`. The initial values and source URLs are recorded in `docs/research.md`; verify account-level availability and pricing before production benchmarking.

## Remaining external requirement

The implementation is ready for a live Nebius run. Once `NEBIUS_API_KEY` is available, run `python -m routewise.eval --config models.yaml` to produce measured `/results` CSVs and JSON. External GitHub, Netlify, and Render publication also requires connected accounts or deployment credentials.
