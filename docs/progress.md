# RouteWise progress

The complete local implementation is present in the repository. The seeded generator produced 150 invoices: 50 training records and 100 test records. The typed schema, verifier, cost calculator, async Nebius client, routing trace, classifier module, evaluator, FastAPI endpoints, SSE stream, React dashboard, CI, and deployment manifests are implemented.

Validation completed successfully: 3 pytest tests passed, Ruff passed, the Vite production build passed, and `GET /health` returned `{"status":"ok","service":"routewise"}`. The public sandbox previews are available from the final response.

The live evaluation is not complete because `NEBIUS_API_KEY` is absent. Consequently there are no real benchmark CSVs, charts, classifier precision/recall values, or headline cost/latency/accuracy claim. External GitHub, Netlify, and Render publication is also pending because no matching connectors or credentials are configured.
