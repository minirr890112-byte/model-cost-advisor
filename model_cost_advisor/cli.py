"""
CLI entry point for model-cost-advisor.

Usage:
    model-cost "your task description"
    model-cost --tier quality "write a research paper outline"
    model-cost --runs 500 "summarize 1000 customer reviews daily"
"""

from __future__ import annotations

import sys
from typing import Any

import click

from .advisor import analyze_cost, classify_task, TIER_ORDER, TIER_DESCRIPTIONS
from .pricing import TIER_NAMES


# ─── formatters ─────────────────────────────────────────────────────────────


def _fmt_tokens(n: int) -> str:
    """Format token count with k/M suffix."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        val = n / 1_000
        if val < 10:
            return f"{val:.1f}k"
        return f"{val:.0f}k"
    return str(n)


def _fmt_cost(v: float) -> str:
    """Format cost in USD. Smart formatting based on magnitude."""
    if v == 0:
        return "$0"
    if v >= 1:
        return f"${v:,.2f}"
    if v >= 0.01:
        return f"${v:.4f}"
    # small values — show significant digits
    s = f"${v:.6f}"
    return s.rstrip("0").rstrip(".") if "." in s else s


def _fmt_savings(v: float) -> str:
    """Format savings with color markup equivalent."""
    if v >= 0:
        return f"${v:,.2f}"
    return f"-${abs(v):,.2f}"


# ─── output rendering ──────────────────────────────────────────────────────


def print_analysis(result: Any, ranked: bool = False, compact: bool = False) -> None:
    """Pretty-print the analysis result to the terminal."""

    # Header
    task_emoji = {
        "summarization": "📄",
        "coding": "💻",
        "chat": "💬",
        "research": "🔬",
    }
    emoji = task_emoji.get(result.task_type, "📋")
    task_label = result.task_type.capitalize()

    click.echo()
    click.secho(f"  {emoji}  Model Cost Advisor", bold=True)
    click.echo(f"  {'─' * 48}")
    click.echo(f"  Task: {result.task_description[:72]}")
    if len(result.task_description) > 72:
        click.echo(f"        {result.task_description[72:]}...")
    click.echo(
        f"  Type: {task_label}  │  "
        f"Tokens: {_fmt_tokens(result.input_tokens)} in / {_fmt_tokens(result.output_tokens)} out"
    )
    click.echo(
        f"  Volume: {result.runs_per_day} runs/day  │  "
        f"{result.runs_per_day * 30:,} runs/month"
    )
    click.echo(f"  {'─' * 48}")

    if compact:
        _print_compact(result)
    elif ranked:
        _print_ranked(result)
    else:
        _print_tiers(result)

    # Recommendation footer
    rec = result.recommendation
    click.echo(f"  {'─' * 48}")
    click.secho(
        f"  💡  Recommendation: {rec.model_name} ({rec.provider})",
        bold=True,
        fg="green",
    )
    quality_note = {
        "summarization": "accurate enough for production summaries",
        "coding": "strong code generation at a fraction of the cost",
        "chat": "responsive and capable for conversational tasks",
        "research": "deep reasoning for complex analysis",
    }.get(result.task_type, "excellent quality for this task type")

    click.echo(f"      {quality_note}")

    if result.gpt41_comparison and result.annual_savings > 0:
        click.secho(
            f"      Annual savings vs GPT-4.1: {_fmt_savings(result.annual_savings)}",
            fg="yellow",
        )
    elif result.gpt41_comparison and result.annual_savings <= 0:
        click.echo(
            f"      No savings vs GPT-4.1 (GPT-4.1 is already cost-optimal)"
        )

    click.echo()


def _print_tiers(result: Any) -> None:
    """Print the standard tiered output."""
    for tier in result.tiers:
        tier_emoji = {
            "budget": "💰",
            "value": "⚡",
            "quality": "🏅",
            "premium": "👑",
        }
        emoji = tier_emoji.get(tier.tier_key, "📊")
        click.echo()
        click.secho(
            f"  {emoji}  Tier: {tier.tier_name} ({tier.description})",
            bold=True,
        )

        for model in tier.top_models:
            click.echo(
                f"     → {model.model_name:<22s} "
                f"{_fmt_cost(model.total_cost_per_run):>10s}/run  "
                f"{_fmt_cost(model.cost_per_day):>10s}/day  "
                f"{_fmt_cost(model.cost_per_month):>10s}/mo"
            )


def _print_ranked(result: Any) -> None:
    """Print all models ranked by per-run cost."""
    all_breakdowns = []
    for tier in result.tiers:
        all_breakdowns.extend(tier.all_models)
    all_breakdowns.sort(key=lambda b: b.total_cost_per_run)

    click.echo()
    click.secho("  📊  All Models Ranked (cheapest first)", bold=True)
    click.echo(f"  {'Model':<24s} {'Provider':<12s} {'Tier':<10s} {'/run':>10s} {'/day':>10s} {'/mo':>10s}")
    click.echo(f"  {'─'*24} {'─'*12} {'─'*10} {'─'*10} {'─'*10} {'─'*10}")

    for b in all_breakdowns:
        marker = "→" if b.model_name == result.recommendation.model_name else " "
        click.echo(
            f" {marker} {b.model_name:<23s} {b.provider:<12s} "
            f"{TIER_NAMES.get(b.tier, b.tier):<10s} "
            f"{_fmt_cost(b.total_cost_per_run):>10s} "
            f"{_fmt_cost(b.cost_per_day):>10s} "
            f"{_fmt_cost(b.cost_per_month):>10s}"
        )


def _print_compact(result: Any) -> None:
    """Print a compact one-line-per-tier summary."""
    click.echo()
    for tier in result.tiers:
        if not tier.top_models:
            continue
        best = tier.top_models[0]
        click.echo(
            f"  {TIER_NAMES.get(tier.tier_key, tier.tier_key):<10s} "
            f"→ {best.model_name:<22s} "
            f"{_fmt_cost(best.total_cost_per_run):>10s}/run  "
            f"{_fmt_cost(best.cost_per_month):>10s}/mo"
        )


# ─── CLI ────────────────────────────────────────────────────────────────────


@click.command(
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.argument("task", required=True)
@click.option(
    "--tier",
    "-t",
    type=click.Choice(TIER_ORDER),
    default=None,
    help="Filter to a specific pricing tier only.",
)
@click.option(
    "--runs",
    "-r",
    type=click.IntRange(min=1, max=1000000),
    default=100,
    show_default=True,
    help="Number of runs per day for cost projection.",
)
@click.option(
    "--ranked",
    "-R",
    is_flag=True,
    default=False,
    help="Show all models ranked by cost instead of tiered view.",
)
@click.option(
    "--compact",
    "-c",
    is_flag=True,
    default=False,
    help="Compact output (one line per tier).",
)
@click.option(
    "--task-type",
    "-T",
    type=click.Choice(["summarization", "coding", "chat", "research"]),
    default=None,
    help="Override automatic task type classification.",
)
@click.option(
    "--tokens",
    "-k",
    type=int,
    default=None,
    help="Override estimated input token count.",
)
@click.option(
    "--output-tokens",
    "-o",
    type=int,
    default=None,
    help="Override estimated output token count.",
)
@click.version_option(
    version="1.2.0",
    prog_name="model-cost",
    message="model-cost-advisor %(version)s",
)
def cli(
    task: str,
    tier: str | None,
    runs: int,
    ranked: bool,
    compact: bool,
    task_type: str | None,
    tokens: int | None,
    output_tokens: int | None,
) -> None:
    """Analyze any task and recommend the most cost-effective LLM.

    TASK is a plain-English description of what you want to do.
    Examples: "summarize 1000 reviews daily", "build a todo app with auth".

    Compares 30+ models across Budget / Value / Quality / Premium tiers,
    estimates token usage, and projects per-run, per-day, and per-month costs.
    """
    result = analyze_cost(
        description=task,
        task_type=task_type,
        runs_per_day=runs,
        filter_tier=tier,
    )

    # Override token estimates if provided
    if tokens is not None:
        result.input_tokens = tokens
    if output_tokens is not None:
        result.output_tokens = output_tokens

    print_analysis(result, ranked=ranked, compact=compact)


if __name__ == "__main__":
    cli()
