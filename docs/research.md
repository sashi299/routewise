# Nebius model research

Checked 2026-10-12 for initial configuration. The official Nebius Token Factory page describes an OpenAI-compatible API and lists Nemotron-3-Ultra among available open models: https://nebius.com/services/token-factory.

The official Nemotron page documents the OpenAI-compatible endpoint and the model identifier `nvidia/nemotron-3-super-120b-a12b`, and describes the Nemotron 3 Nano, Super, and Ultra families: https://nebius.com/services/token-factory/nemotron.

For concrete input/output prices used in the first config, the independent Mastra Nebius catalog lists:

- `nebius/meta-llama/meta-llama-3.1-8b-instruct`: $0.02 / $0.06 per 1M input/output tokens.
- `nebius/qwen/qwen3-32b`: $0.10 / $0.30.
- `nebius/nvidia/nvidia-nemotron-3-nano-30b-a3b`: $0.06 / $0.24.
- `nebius/nvidia/llama-3_1-nemotron-ultra-253b-v1`: $0.60 / $2.00.

Source: https://mastra.ai/models/providers/nebius

These values are configuration inputs, not measured benchmark results. Re-check current account-level availability and pricing before evaluation or deployment.
