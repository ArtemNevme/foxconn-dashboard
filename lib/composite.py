"""
lib/composite.py — Weighted normalized composite index for Mexico vs Brazil.

Problem: Comparison.csv mixes scales (GDP=0.0143 vs EV Growth=180).
Solution: normalize each metric to 0–100 using indicator-specific logic,
then apply weights aligned with Advanced Manufacturing & Assembly focus.
"""

import pandas as pd
from lib.data_loader import load_comparison, load_manufacturing_ev
from lib.theme import GOOD, BAD

WEIGHTS = {
    "Manufacturing_Pct_GDP": 0.20,
    "Labor_Cost": 0.15,
    "STEM": 0.15,
    "Credit_Rating": 0.15,
    "Economic_Freedom": 0.10,
    "Foxconn_Plants": 0.10,
    "EV_Growth": 0.10,
    "CPI": 0.05,
}

# Credit rating mapping to numeric scale (higher = better)
RATING_MAP = {
    "AAA": 100, "AA+": 95, "AA": 90, "AA-": 85,
    "A+": 80, "A": 75, "A-": 70,
    "BBB+": 65, "BBB": 60, "BBB-": 55,
    "BB+": 45, "BB": 40, "BB-": 35,
    "B+": 30, "B": 25, "B-": 20,
    "CCC+": 15, "CCC": 10, "CC": 5, "C": 2, "D": 0,
    # Moody's equivalents
    "Aaa": 100, "Aa1": 95, "Aa2": 90, "Aa3": 85,
    "A1": 80, "A2": 75, "A3": 70,
    "Baa1": 65, "Baa2": 60, "Baa3": 55,
    "Ba1": 40, "Ba2": 35, "Ba3": 30,
    "B1": 25, "B2": 20, "B3": 15,
    "Caa1": 10, "Caa2": 5, "Caa3": 2, "Ca": 1, "C": 0,
}


def _to_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _normalize_metric(value, direction: str, ref_min: float, ref_max: float) -> float:
    """Normalize a single value to 0–100 using a reference range."""
    if value is None or pd.isna(value):
        return 50.0
    rng = ref_max - ref_min
    if rng == 0:
        return 50.0
    if direction == "higher_better":
        norm = (value - ref_min) / rng
    else:
        norm = (ref_max - value) / rng
    norm = max(0.0, min(1.0, norm))
    return norm * 100.0


def compute_composite() -> dict:
    """
    Compute composite scores for Mexico and Brazil.
    Returns dict with keys: mexico_score, brazil_score, breakdown_df, weights_df.
    """
    comp = load_comparison()
    mev = load_manufacturing_ev()

    # Build metric lookup from Comparison.csv
    metrics = {}
    for _, row in comp.iterrows():
        metric = row["Metric"]
        metrics[metric] = {"Mexico": row["Mexico"], "Brazil": row["Brazil"]}

    def getv(metric, country):
        return metrics.get(metric, {}).get(country)

    metric_specs = {
        "Manufacturing_Pct_GDP": {
            "mx": _to_float(getv("Manufacturing % GDP", "Mexico")),
            "br": _to_float(getv("Manufacturing % GDP", "Brazil")),
            "direction": "higher_better",
            "ref_min": 0.05, "ref_max": 0.30,
        },
        "Labor_Cost": {
            "mx": _to_float(getv("Labor Cost/hr", "Mexico")),
            "br": _to_float(getv("Labor Cost/hr", "Brazil")),
            "direction": "lower_better",
            "ref_min": 2.0, "ref_max": 12.0,
        },
        "STEM": {
            "mx": mev.loc[mev["Country"] == "Mexico", "STEM_Graduates_Annual"].values[0],
            "br": mev.loc[mev["Country"] == "Brazil", "STEM_Graduates_Annual"].values[0],
            "direction": "higher_better",
            "ref_min": 20000, "ref_max": 300000,
        },
        "Credit_Rating": {
            "mx": getv("Credit Rating", "Mexico"),
            "br": getv("Credit Rating", "Brazil"),
            "direction": "higher_better",
            "ref_min": 0, "ref_max": 100,
            "is_rating": True,
        },
        "Economic_Freedom": {
            "mx": _to_float(getv("Economic Freedom", "Mexico")),
            "br": _to_float(getv("Economic Freedom", "Brazil")),
            "direction": "higher_better",
            "ref_min": 40, "ref_max": 80,
        },
        "Foxconn_Plants": {
            "mx": mev.loc[mev["Country"] == "Mexico", "Foxconn_Plants"].values[0],
            "br": mev.loc[mev["Country"] == "Brazil", "Foxconn_Plants"].values[0],
            "direction": "higher_better",
            "ref_min": 0, "ref_max": 10,
        },
        "EV_Growth": {
            "mx": _to_float(getv("EV Growth (In %)", "Mexico")),
            "br": _to_float(getv("EV Growth (In %)", "Brazil")),
            "direction": "higher_better",
            "ref_min": 0, "ref_max": 250,
        },
        "CPI": {
            "mx": _to_float(getv("CPI Score", "Mexico")),
            "br": _to_float(getv("CPI Score", "Brazil")),
            "direction": "higher_better",
            "ref_min": 0, "ref_max": 100,
        },
    }

    breakdown = []
    mx_total = 0.0
    br_total = 0.0

    for key, spec in metric_specs.items():
        mx_raw = spec["mx"]
        br_raw = spec["br"]
        weight = WEIGHTS[key]
        direction = spec["direction"]

        if spec.get("is_rating"):
            mx_norm = RATING_MAP.get(str(mx_raw), 50)
            br_norm = RATING_MAP.get(str(br_raw), 50)
        else:
            mx_norm = _normalize_metric(mx_raw, direction, spec["ref_min"], spec["ref_max"])
            br_norm = _normalize_metric(br_raw, direction, spec["ref_min"], spec["ref_max"])

        mx_contrib = mx_norm * weight
        br_contrib = br_norm * weight
        mx_total += mx_contrib
        br_total += br_contrib

        breakdown.append({
            "Metric": key,
            "Weight": weight,
            "Direction": direction,
            "Mexico_Raw": mx_raw,
            "Brazil_Raw": br_raw,
            "Mexico_Norm": round(mx_norm, 2),
            "Brazil_Norm": round(br_norm, 2),
            "Mexico_Score": round(mx_contrib, 2),
            "Brazil_Score": round(br_contrib, 2),
        })

    breakdown_df = pd.DataFrame(breakdown)
    weights_df = pd.DataFrame([{"Metric": k, "Weight": v} for k, v in WEIGHTS.items()])

    return {
        "mexico_score": round(mx_total, 2),
        "brazil_score": round(br_total, 2),
        "breakdown_df": breakdown_df,
        "weights_df": weights_df,
    }
