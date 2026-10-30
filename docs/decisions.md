# RouteWise implementation decisions

## Model configuration

Model IDs and token prices are stored in `models.yaml`, not application code. The initial values are based on the Nebius Token Factory catalog research in `docs/research.md` and must be rechecked against the owner's account before a live run.

## Verification policy

The router applies Pydantic schema validation, arithmetic consistency, and scalar grounding before considering escalation. A failed check is visible in the trace. The system does not claim an answer is correct merely because a model returned valid JSON.

## Missing credentials

The sandbox does not contain `NEBIUS_API_KEY`, GitHub credentials, Netlify credentials, or Render credentials. Live evaluation and external publication therefore remain pending. No mock output is used as reported benchmark data.

## Deployment

The repository contains `render.yaml`, `netlify.toml`, `Dockerfile`, and `docker-compose.yml` so publication can proceed once the corresponding accounts are connected. The local API and dashboard previews are used for validation only.
