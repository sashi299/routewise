# Demo script and Devpost copy

## Three-minute demo script

**0:00–0:25 — Problem.** Every extraction workflow that defaults to the largest model pays the largest-model price. Invoice extraction is repetitive, but failures are expensive when arithmetic or grounding is wrong.

**0:25–1:25 — Live demo.** Paste an invoice into the dashboard. RouteWise sends it to Tier 1, shows the structured JSON, and runs schema, arithmetic, and grounding checks. If the checks pass, the trace ends. If not, the trace escalates to Tier 2 and then Tier 3 only when needed. The companion panel compares this with always using the largest model.

**1:25–2:10 — Architecture.** The model ladder and token prices live in configuration. The router records tokens, latency, cost, and every verification decision. The evaluation runner compares always-small, always-medium, always-large, and RouteWise on a seeded 150-invoice dataset.

**2:10–2:40 — Measured result.** Show the generated `results/summary.csv` from a real Nebius run and read the actual cost, latency, and accuracy numbers from the dashboard. Do not use placeholder metrics.

**2:40–3:00 — Limitation and next step.** The dataset is synthetic and small, so the result is directional. The next step is validation on a representative invoice corpus with carefully reviewed ground truth.

## Devpost description

RouteWise is a cost-aware invoice extraction system that earns the right to use a larger model. It tries a low-cost open model first, verifies schema validity, arithmetic consistency, and source grounding, then escalates only when verification fails. The project measures the trade-off between cost, latency, and accuracy against always-small, always-medium, and always-large baselines. The benchmark is reproducible, the model ladder is configuration-driven, and the system emits a full routing trace instead of hiding the failure path.
