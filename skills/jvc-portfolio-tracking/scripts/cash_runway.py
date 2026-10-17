#!/usr/bin/env python3
"""Project monthly available cash. Future financing is scenario-only."""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path


def amount(value, label, *, signed=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label}: finite number required; unknown is not zero")
    if not signed and value < 0:
        raise ValueError(f"{label}: must be nonnegative")
    return value


def month_index(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", value):
        raise ValueError("month must use YYYY-MM")
    year, month = map(int, value.split("-"))
    return year * 12 + month


def project(payload):
    if payload.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    if not payload.get("unit"):
        raise ValueError("unit is required")
    as_of = month_index(payload["as_of_month"])
    opening = amount(payload["cash"], "cash") - amount(payload["restricted_cash"], "restricted_cash")
    if opening < 0:
        raise ValueError("restricted_cash exceeds cash")
    periods = payload["periods"]
    if not isinstance(periods, list) or not periods:
        raise ValueError("periods must be a nonempty monthly forecast")
    months = []
    for offset, row in enumerate(periods, 1):
        if month_index(row["month"]) != as_of + offset:
            raise ValueError("forecast months must be consecutive and start after as_of_month")
        months.append(row["month"])
        for key in ("operating_net", "capex", "debt_service", "other_net"):
            amount(row[key], key, signed=key.endswith("_net"))
        if "financing" in row or "financing_inflow" in row:
            raise ValueError("future financing belongs in financing_scenarios, never baseline")
    milestone = payload.get("milestone_month", months[-1])
    if milestone not in months:
        raise ValueError("milestone_month must be inside forecast horizon")

    def calculate(inflows):
        balance = opening
        balances = []
        first_zero = payload["as_of_month"] if opening <= 0 else None
        for row in periods:
            balance += row["operating_net"] + row["other_net"] - row["capex"] - row["debt_service"] + inflows.get(row["month"], 0)
            balances.append({"month": row["month"], "ending_cash": round(balance, 8)})
            if first_zero is None and balance <= 0:
                first_zero = row["month"]
        minimum = min([opening] + [row["ending_cash"] for row in balances[:months.index(milestone) + 1]])
        return {"balances": balances, "first_nonpositive_month": first_zero,
                "minimum_cash_to_milestone": minimum,
                "funding_gap_to_milestone": max(0, -minimum),
                "status": "cash_exhausted_within_horizon" if first_zero else "positive_within_forecast_horizon",
                "horizon_end": months[-1]}

    result = {"unit": payload["unit"], "opening_available_cash": opening,
              "milestone_month": milestone, "baseline": calculate({}), "scenarios": []}
    names = set()
    for scenario in payload.get("financing_scenarios", []):
        name = scenario["name"]
        if not isinstance(name, str) or not name.strip() or name in names or not scenario.get("condition"):
            raise ValueError("scenario requires a unique name and financing condition")
        names.add(name)
        inflows = scenario["inflows"]
        if not isinstance(inflows, dict) or not inflows or set(inflows) - set(months):
            raise ValueError("scenario inflows must map forecast months to amounts")
        for value in inflows.values():
            amount(value, "scenario inflow")
        result["scenarios"].append({"name": name, "condition": scenario["condition"], **calculate(inflows)})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        result = project(json.loads(args.input.read_text(encoding="utf-8")))
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f"cash projection failed: {error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
