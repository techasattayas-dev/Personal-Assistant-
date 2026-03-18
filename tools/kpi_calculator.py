"""
Tool: kpi_calculator — Calculate KPI scorecards from definitions and data.

Reads KPI definitions from Areas/Business-Units/{BU}/kpi-definitions.yaml,
optionally loads actual data from a CSV file, and produces a formatted
markdown scorecard with traffic-light status indicators.

If no data file is provided, returns a template scorecard for manual fill.
"""

from pathlib import Path

import yaml
import pandas as pd


PROJECT_ROOT = Path(__file__).parent.parent
BU_DIR = PROJECT_ROOT / "Areas" / "Business-Units"

# Allowed business unit names (prevents path traversal)
_VALID_BU_NAMES = {"VCF-Group", "VC-Meat-Processing", "VC-Meat-Distribution", "GT21-Myanmar"}


def _get_status(actual, target, yellow, red, direction):
    """Determine traffic-light status for a KPI metric."""
    if actual is None or target is None:
        return "---"

    # Guard against missing thresholds — fall back to target-only comparison
    if yellow is None or red is None:
        if direction == "higher_is_better":
            return "GREEN" if actual >= target else "RED"
        else:
            return "GREEN" if actual <= target else "RED"

    if direction == "higher_is_better":
        if actual >= target:
            return "GREEN"
        elif actual >= yellow:
            return "YELLOW"
        elif actual >= red:
            return "RED"
        else:
            return "RED"
    else:  # lower_is_better
        if actual <= target:
            return "GREEN"
        elif actual <= yellow:
            return "YELLOW"
        elif actual <= red:
            return "RED"
        else:
            return "RED"


def _get_achievement(actual, target, direction):
    """Calculate achievement percentage."""
    if actual is None or target is None or target == 0:
        return "---"

    if direction == "higher_is_better":
        pct = (actual / target) * 100
    else:
        # For lower_is_better, invert so being under target gives >100%
        pct = (target / actual) * 100 if actual != 0 else 100

    return f"{pct:.0f}%"


def _sanitize_path(path: Path, allowed_root: Path) -> Path | None:
    """Ensure a resolved path stays within the allowed root directory."""
    try:
        resolved = path.resolve()
        if resolved.is_relative_to(allowed_root.resolve()):
            return resolved
    except (ValueError, OSError):
        pass
    return None


def calculate_kpis(
    business_unit: str,
    period: str | None = None,
    data_file: str | None = None,
) -> str:
    """Calculate KPI scorecard for a business unit.

    Args:
        business_unit: BU folder name (e.g. 'VCF-Group', 'GT21-Myanmar')
        period: Report period (e.g. '2026-03'). Used in header and file lookup.
        data_file: Optional path to CSV with actual KPI values.
                   CSV should have columns: metric_key, actual, prior_period (optional)
                   If not provided, checks {BU}/data/kpi-{period}.csv automatically.

    Returns:
        Formatted markdown scorecard string.
    """
    # Validate business unit name (prevent path traversal)
    if business_unit not in _VALID_BU_NAMES:
        return f"ERROR: Invalid business unit '{business_unit}'. Valid: {sorted(_VALID_BU_NAMES)}"

    bu_path = BU_DIR / business_unit
    if not bu_path.exists():
        return f"ERROR: Business unit directory not found at {bu_path}"

    # Load KPI definitions
    defs_path = bu_path / "kpi-definitions.yaml"
    if not defs_path.exists():
        return f"ERROR: KPI definitions not found at {defs_path}"

    try:
        with open(defs_path) as f:
            defs = yaml.safe_load(f)
    except Exception as e:
        return f"ERROR: Failed to parse KPI definitions: {type(e).__name__}"

    # Try to load actual data
    actuals = {}
    prior = {}
    data_loaded = False

    # Check explicit data_file first, then auto-detect
    csv_path = None
    if data_file:
        candidate = Path(data_file)
        if not candidate.is_absolute():
            candidate = PROJECT_ROOT / candidate
        # Sanitize: must stay within project root
        csv_path = _sanitize_path(candidate, PROJECT_ROOT)
        if csv_path is None:
            return f"ERROR: Data file path is outside the project directory."
    elif period:
        auto_path = bu_path / "data" / f"kpi-{period}.csv"
        if auto_path.exists():
            csv_path = auto_path

    if csv_path and csv_path.exists():
        try:
            df = pd.read_csv(csv_path)
            has_prior = "prior_period" in df.columns
            for _, row in df.iterrows():
                key = row.get("metric_key", "")
                if key:
                    actuals[key] = row.get("actual")
                    if has_prior:
                        prior[key] = row.get("prior_period")
            data_loaded = True
        except Exception as e:
            return f"ERROR: Failed to load data from {csv_path.name}: {type(e).__name__}"

    # Build scorecard
    bu_label = defs.get("business_unit", business_unit)
    period_label = period or "N/A"

    lines = []
    lines.append(f"# KPI Scorecard — {bu_label}")
    lines.append(f"**Period**: {period_label}")
    if data_loaded:
        lines.append(f"**Data Source**: {csv_path.name}")
    else:
        lines.append("**Data Source**: No data file — showing targets only (fill in actuals)")
    lines.append("")

    red_alerts = []
    yellow_alerts = []
    all_metrics_summary = []

    categories = defs.get("categories", {})
    for cat_key, cat_data in categories.items():
        cat_label = cat_data.get("label", cat_key)
        lines.append(f"## {cat_label}")
        lines.append("")
        lines.append("| Metric | Target | Actual | Achievement | Status |")
        lines.append("|--------|--------|--------|-------------|--------|")

        metrics = cat_data.get("metrics", {})
        for metric_key, metric in metrics.items():
            label = metric.get("label", metric_key)
            unit = metric.get("unit", "")
            target = metric.get("target")
            yellow = metric.get("yellow_threshold")
            red = metric.get("red_threshold")
            direction = metric.get("direction", "higher_is_better")

            actual = actuals.get(metric_key)
            prior_val = prior.get(metric_key)

            # Handle status-type metrics (compliant/non-compliant)
            if unit == "status":
                actual_display = str(actual) if actual else "---"
                target_display = str(target)
                if actual == target:
                    status = "GREEN"
                    achievement = "100%"
                elif actual == "in_progress":
                    status = "YELLOW"
                    achievement = "50%"
                else:
                    status = "RED" if actual else "---"
                    achievement = "0%" if actual else "---"
            else:
                target_display = f"{target} {unit}" if target is not None else "---"
                actual_display = f"{actual} {unit}" if actual is not None else "---"
                status = _get_status(actual, target, yellow, red, direction)
                achievement = _get_achievement(actual, target, direction)

            lines.append(f"| {label} | {target_display} | {actual_display} | {achievement} | {status} |")

            # Collect alerts
            if status == "RED":
                red_alerts.append(f"- **{label}** ({cat_label}): {actual_display} vs target {target_display}")
            elif status == "YELLOW":
                yellow_alerts.append(f"- **{label}** ({cat_label}): {actual_display} vs target {target_display}")

            # Collect for summary
            all_metrics_summary.append({
                "category": cat_label,
                "metric": label,
                "target": target,
                "actual": actual,
                "status": status,
                "prior": prior_val,
            })

        lines.append("")

    # Alerts section
    lines.append("## Alerts")
    lines.append("")
    if red_alerts:
        lines.append("### CRITICAL (RED)")
        for alert in red_alerts:
            lines.append(alert)
        lines.append("")
    if yellow_alerts:
        lines.append("### NEEDS ATTENTION (YELLOW)")
        for alert in yellow_alerts:
            lines.append(alert)
        lines.append("")
    if not red_alerts and not yellow_alerts:
        lines.append("No alerts — all metrics on target.")
        lines.append("")

    # Trends section (if prior data available)
    if any(m["prior"] is not None for m in all_metrics_summary):
        lines.append("## Trends vs Prior Period")
        lines.append("")
        lines.append("| Metric | Prior | Current | Change |")
        lines.append("|--------|-------|---------|--------|")
        for m in all_metrics_summary:
            if m["prior"] is not None and m["actual"] is not None:
                try:
                    change = float(m["actual"]) - float(m["prior"])
                    arrow = "+" if change >= 0 else ""
                    lines.append(f"| {m['metric']} | {m['prior']} | {m['actual']} | {arrow}{change:.1f} |")
                except (ValueError, TypeError):
                    pass
        lines.append("")

    # Summary stats
    total = len(all_metrics_summary)
    green_count = sum(1 for m in all_metrics_summary if m["status"] == "GREEN")
    yellow_count = sum(1 for m in all_metrics_summary if m["status"] == "YELLOW")
    red_count = sum(1 for m in all_metrics_summary if m["status"] == "RED")
    no_data = sum(1 for m in all_metrics_summary if m["status"] == "---")

    lines.append("## Summary")
    lines.append("")
    lines.append("| Status | Count | % of Total |")
    lines.append("|--------|-------|------------|")
    if data_loaded and total > 0:
        lines.append(f"| GREEN | {green_count} | {green_count/total*100:.0f}% |")
        lines.append(f"| YELLOW | {yellow_count} | {yellow_count/total*100:.0f}% |")
        lines.append(f"| RED | {red_count} | {red_count/total*100:.0f}% |")
        if no_data:
            lines.append(f"| No Data | {no_data} | {no_data/total*100:.0f}% |")
    else:
        lines.append(f"| Total Metrics | {total} | — |")
        lines.append(f"| Awaiting Data | {total} | 100% |")
    lines.append("")

    return "\n".join(lines)
