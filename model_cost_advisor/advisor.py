"""
Core advisor logic: task classification, token estimation, cost analysis.

All costs are computed in USD using per-MTok pricing.
"""

from __future__ import annotations

import re as _re
from dataclasses import dataclass, field
from typing import Any

from .pricing import MODELS, TIER_ORDER, TIER_NAMES, TIER_DESCRIPTIONS


# ─── token estimation constants ─────────────────────────────────────────────

CHARS_PER_TOKEN = 4.0  # approximate: 1 token ≈ 4 characters

# Base input tokens per "item" for each task type
# These are realistic estimates for a single atomic task unit
BASE_INPUT_TOKENS = {
    "summarization": 500,   # a typical document/review to summarize
    "coding": 800,          # a typical coding request with context
    "chat": 150,            # a typical chat message
    "research": 1200,       # a research query with context
}

# Output-to-input token ratios by task type
OUTPUT_RATIOS = {
    "summarization": 0.30,
    "coding": 0.80,
    "chat": 0.60,
    "research": 1.20,
}

# Classification keywords
TASK_KEYWORDS = {
    "summarization": [
        "summarize", "summary", "summarise", "tl;dr", "tldr",
        "brief", "condense", "abstract", "recap", "digest",
        "overview of", "outline of", "classify", "categorize",
        "tag", "label", "extract", "parse",
    ],
    "coding": [
        "code", "coding", "program", "debug", "refactor",
        "function", "class ", "api", "endpoint", "algorithm",
        "build", "implement", "develop", "script", "app",
        "bug", "fix", "test", "deploy", "compile",
        "react", "python", "javascript", "sql", "typescript",
        "component", "hook", "database", "backend", "frontend",
        "full-stack", "fullstack", "cli", "module", "package",
    ],
    "chat": [
        "chat", "conversation", "reply", "respond", "message",
        "customer support", "faq", "q&a", "question",
        "assistant", "help desk", "inquiry",
    ],
    "research": [
        "research", "analyze", "analysis", "paper", "report",
        "study", "investigate", "evaluate", "compare",
        "literature review", "thesis", "dissertation",
        "whitepaper", "white paper", "deep dive",
    ],
}


# ─── data classes ───────────────────────────────────────────────────────────


@dataclass
class CostBreakdown:
    """Per-model cost breakdown."""
    model_name: str
    provider: str
    tier: str
    input_tokens: int
    output_tokens: int
    input_cost_per_run: float
    output_cost_per_run: float
    total_cost_per_run: float
    cost_per_day: float
    cost_per_month: float
    cost_per_year: float


@dataclass
class TierResult:
    """All models within a single tier, with top 2 highlighted."""
    tier_key: str
    tier_name: str
    description: str
    top_models: list[CostBreakdown]
    all_models: list[CostBreakdown]


@dataclass
class AnalysisResult:
    """Full analysis result."""
    task_description: str
    task_type: str
    input_tokens: int
    output_tokens: int
    runs_per_day: int
    tiers: list[TierResult]
    recommendation: CostBreakdown
    gpt41_comparison: CostBreakdown | None
    annual_savings: float


# ─── classification ────────────────────────────────────────────────────────


def classify_task(description: str) -> str:
    """Classify a task description into a task type.

    Returns one of: 'summarization', 'coding', 'chat', 'research'.
    """
    lower = description.lower()
    scores: dict[str, int] = {}

    for task_type, keywords in TASK_KEYWORDS.items():
        score = 0
        for kw in keywords:
            # count occurrences (case-insensitive, word-boundary aware)
            matches = _re.findall(rf"\b{_re.escape(kw)}\b", lower)
            score += len(matches)
            # bonus for leading keyword
            if lower.startswith(kw):
                score += 2
        scores[task_type] = score

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        # default: treat as chat/conversational
        return "chat"
    return best


# ─── token estimation ──────────────────────────────────────────────────────


def estimate_tokens(description: str, task_type: str | None = None) -> tuple[int, int]:
    """Estimate input and output token counts for a task.

    Parses the description for batch-size hints (e.g. "1000 reviews daily"),
    then uses base token estimates per task type scaled by detected volume.

    Args:
        description: The task description text.
        task_type: Optional pre-classified task type.

    Returns:
        (input_tokens, output_tokens)
    """
    if task_type is None:
        task_type = classify_task(description)

    # Detect a batch-size multiplier from the description
    # e.g. "1000 reviews", "500 items", "10k messages", "50 pages"
    batch = 1
    lower = description.lower()
    # Look for patterns like "number [optional k/m] [optional adjective] word"
    num_match = _re.search(
        r"(\d[\d,]*\.?\d*)\s*(k|thousand|m|million)?"
        r"(?:\s+\w+){0,3}\s+(reviews?|items?|documents?|"
        r"messages?|pages?|emails?|tickets?|articles?|posts?|records?|rows?|"
        r"entries?|files?|logs?|lines?|requests?|calls?|users?|chats?)",
        lower,
    )
    if num_match:
        raw = num_match.group(1).replace(",", "")
        num = float(raw)
        suffix = num_match.group(2) or ""
        if suffix in ("k", "thousand"):
            num *= 1_000
        elif suffix in ("m", "million"):
            num *= 1_000_000
        # Cap the batch multiplier at a reasonable per-item count;
        # if someone says "10000 items" that's the daily volume,
        # and per-item tokens stay at the base level.
        if num <= 100:
            batch = max(1, int(num))
        else:
            batch = 1  # large numbers represent daily volume, not per-item scaling

    # Base input tokens for this task type
    base_input = BASE_INPUT_TOKENS.get(task_type, 150)

    # Scale by description length (longer descriptions = more context)
    char_count = len(description)
    char_estimate = max(50, int(char_count / CHARS_PER_TOKEN))

    # Blend character-based estimate with task-type base estimate
    # Use the larger of the two, capped at a reasonable maximum
    input_tokens = max(char_estimate, base_input)

    # Additional context scaling for very detailed descriptions
    if char_count > 500:
        input_tokens = int(input_tokens * 1.3)
    if char_count > 2000:
        input_tokens = int(input_tokens * 1.5)

    # Apply batch multiplier for small explicit batch sizes
    input_tokens = int(input_tokens * batch)

    # Fallback volume detection: bump tokens for large-volume tasks
    if batch == 1:
        vol_match = _re.search(
            r"(\d[\d,]*\.?\d*)\s*(k|thousand|m|million)",
            lower,
        )
        if vol_match:
            raw = vol_match.group(1).replace(",", "")
            num = float(raw)
            suffix = vol_match.group(2)
            if suffix in ("k", "thousand"):
                num *= 1_000
            elif suffix in ("m", "million"):
                num *= 1_000_000
            if num >= 1000:
                # Large volume: bump token count to reflect batch processing context
                input_tokens = int(input_tokens * 1.2)

    # Estimate output tokens using task-type ratios
    ratio = OUTPUT_RATIOS.get(task_type, 0.6)
    output_tokens = max(20, int(input_tokens * ratio))

    return input_tokens, output_tokens


# ─── cost calculation ──────────────────────────────────────────────────────


def _calculate_model_cost(
    model_name: str,
    model_info: dict[str, Any],
    input_tokens: int,
    output_tokens: int,
    runs_per_day: int = 100,
) -> CostBreakdown:
    """Calculate cost breakdown for a single model."""
    input_price = model_info["input"]   # per MTok
    output_price = model_info["output"]  # per MTok

    # Convert per-MTok to per-token
    input_cost = (input_tokens / 1_000_000) * input_price
    output_cost = (output_tokens / 1_000_000) * output_price
    total_per_run = input_cost + output_cost

    return CostBreakdown(
        model_name=model_name,
        provider=model_info["provider"],
        tier=model_info["tier"],
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        input_cost_per_run=round(input_cost, 6),
        output_cost_per_run=round(output_cost, 6),
        total_cost_per_run=round(total_per_run, 6),
        cost_per_day=round(total_per_run * runs_per_day, 4),
        cost_per_month=round(total_per_run * runs_per_day * 30, 2),
        cost_per_year=round(total_per_run * runs_per_day * 365, 2),
    )


def analyze_cost(
    description: str,
    task_type: str | None = None,
    runs_per_day: int = 100,
    filter_tier: str | None = None,
) -> AnalysisResult:
    """Run the full cost analysis.

    Args:
        description: Task description text.
        task_type: Override auto-classification.
        runs_per_day: Number of runs per day for projections.
        filter_tier: Only show this tier (budget/value/quality/premium).

    Returns:
        Full AnalysisResult with tiers, recommendation, savings.
    """
    if task_type is None:
        task_type = classify_task(description)

    input_tokens, output_tokens = estimate_tokens(description, task_type)

    # Build cost breakdowns for all models
    breakdowns: list[CostBreakdown] = []
    for name, info in MODELS.items():
        breakdowns.append(
            _calculate_model_cost(name, info, input_tokens, output_tokens, runs_per_day)
        )

    # Sort all breakdowns by per-run cost (ascending)
    breakdowns.sort(key=lambda b: b.total_cost_per_run)

    # Group by tier
    tier_groups: dict[str, list[CostBreakdown]] = {}
    for b in breakdowns:
        tier_groups.setdefault(b.tier, []).append(b)

    # Build ordered tier results
    tiers: list[TierResult] = []
    for tier_key in TIER_ORDER:
        if filter_tier and tier_key != filter_tier:
            continue
        models_in_tier = tier_groups.get(tier_key, [])
        if not models_in_tier:
            continue
        # Sort within tier by cost
        models_in_tier.sort(key=lambda b: b.total_cost_per_run)
        tiers.append(
            TierResult(
                tier_key=tier_key,
                tier_name=TIER_NAMES[tier_key],
                description=TIER_DESCRIPTIONS[tier_key],
                top_models=models_in_tier[:2],
                all_models=models_in_tier,
            )
        )

    # Recommendation: best value model (from Value tier, or Budget if only budget)
    recommendation = _pick_recommendation(breakdowns, task_type)

    # GPT-4.1 comparison
    gpt41 = next((b for b in breakdowns if b.model_name == "GPT-4.1"), None)
    annual_savings = 0.0
    if gpt41 is not None:
        annual_savings = round(gpt41.cost_per_year - recommendation.cost_per_year, 2)

    return AnalysisResult(
        task_description=description,
        task_type=task_type,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        runs_per_day=runs_per_day,
        tiers=tiers,
        recommendation=recommendation,
        gpt41_comparison=gpt41,
        annual_savings=annual_savings,
    )


def _pick_recommendation(
    breakdowns: list[CostBreakdown], task_type: str
) -> CostBreakdown:
    """Pick the recommended model based on task type and cost-effectiveness."""
    # Task-type-specific favorites (ordered by preference for that task)
    coding_favorites = ["DeepSeek Coder V2", "DeepSeek V4 Pro", "Codestral",
                        "Qwen Coder", "GPT-4o Mini"]
    research_favorites = ["DeepSeek R1", "Gemini 2.5 Pro", "Claude Sonnet 4",
                          "Mistral Large 2", "GPT-4o"]
    summarization_favorites = ["DeepSeek V4 Flash", "GPT-4o Mini",
                               "Gemini 2.5 Flash", "Claude Haiku 3.5"]
    chat_favorites = ["DeepSeek Chat V3", "GPT-4o Mini", "Claude Haiku 3.5",
                      "Gemini 2.5 Flash"]

    favorites_map = {
        "coding": coding_favorites,
        "research": research_favorites,
        "summarization": summarization_favorites,
        "chat": chat_favorites,
    }
    favorites = favorites_map.get(task_type, chat_favorites)

    # Find all favorite models that exist, sorted by cost (cheapest first)
    matches = [b for b in breakdowns if b.model_name in favorites]
    matches.sort(key=lambda b: b.total_cost_per_run)

    if matches:
        return matches[0]  # cheapest among task-appropriate favorites

    # Fallback: cheapest model in value tier, or overall cheapest
    value_models = [b for b in breakdowns if b.tier == "value"]
    if value_models:
        return value_models[0]  # already sorted by cost
    return breakdowns[0]  # cheapest available
