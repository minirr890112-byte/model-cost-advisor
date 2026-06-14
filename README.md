# model-cost-advisor

> Analyze any task and recommend the most cost-effective LLM — with live pricing from 30+ models

[![Stars](https://img.shields.io/github/stars/minirr890112-byte/model-cost-advisor?style=flat-square&color=f6c242)](https://github.com/minirr890112-byte/model-cost-advisor/stargazers)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)](https://python.org)

## Why This Exists

Choosing the right LLM for a task is hard. GPT-4o is expensive, Claude is great but not always right, Gemini is cheap but weaker. This tool analyzes your task requirements and recommends the most cost-effective model — factoring in token estimates, quality needs, and live pricing.

## Install

```bash
pip install git+https://github.com/minirr890112-byte/model-cost-advisor.git
```

## Usage

```bash
# Quick recommendation
model-cost "summarize 1000 customer reviews daily"

# Quality-first recommendation
model-cost --tier quality "write a research paper outline"

# Budget-first
model-cost --tier budget "classify 10k support tickets weekly"

# Show all options ranked
model-cost "build a coding agent" --ranked
```

## Features

- Compares 30+ models across budget/value/quality/premium tiers
- Token estimation per task
- Cost projection: per-run, per-day, per-year
- Live pricing updates
- Tier-aware: budget → value → quality → premium

## Ecosystem

| Tool | Description |
|---|---|
| [api-cost-compare](https://github.com/minirr890112-byte/api-cost-compare) | Compare LLM API pricing across providers |
| [model-watch](https://github.com/minirr890112-byte/model-watch) | Monitor models over time for regressions |
| [task-cost-estimator](https://github.com/minirr890112-byte/task-cost-estimator) | Estimate dev task costs |

## License

MIT © [HermesMade](https://github.com/minirr890112-byte)
