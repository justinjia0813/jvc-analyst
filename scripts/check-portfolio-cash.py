#!/usr/bin/env python3
"""Cash regressions use synthetic amounts, not company data."""
import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/jvc-portfolio-tracking/scripts/cash_runway.py"
spec = importlib.util.spec_from_file_location("cash_runway", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def main():
    fixture = ROOT / "examples/portfolio-cash-input.json"
    payload = json.loads(fixture.read_text())
    result = json.loads(subprocess.check_output([sys.executable, str(SCRIPT), str(fixture)], text=True))
    assert [r["ending_cash"] for r in result["baseline"]["balances"]] == [40, -20, -10]
    assert result["baseline"]["first_nonpositive_month"] == "2026-11"
    assert result["baseline"]["funding_gap_to_milestone"] == 20
    assert [r["ending_cash"] for r in result["scenarios"][0]["balances"]] == [40, 40, 50]
    assert result["scenarios"][0]["first_nonpositive_month"] is None
    assert result["opening_available_cash"] == 80
    no_financing = copy.deepcopy(payload)
    no_financing["financing_scenarios"] = []
    assert module.project(no_financing)["baseline"] == result["baseline"]
    zero = copy.deepcopy(no_financing)
    zero["periods"][0].update(operating_net=-80, capex=0)
    assert module.project(zero)["baseline"]["first_nonpositive_month"] == "2026-10"
    positive = copy.deepcopy(no_financing)
    for row in positive["periods"]:
        row.update(capex=0, debt_service=0)
    assert module.project(positive)["baseline"]["status"] == "positive_within_forecast_horizon"
    bad = []
    for field, value in (("restricted_cash", 101), ("cash", float("nan")), ("cash", True), ("milestone_month", "2027-01")):
        case = copy.deepcopy(payload); case[field] = value; bad.append(case)
    for field, value in (("capex", None), ("capex", -1), ("month", "2026-12"), ("financing_inflow", 60)):
        case = copy.deepcopy(payload); case["periods"][0][field] = value; bad.append(case)
    case = copy.deepcopy(payload); del case["periods"][0]["debt_service"]; bad.append(case)
    for case in bad:
        try:
            module.project(case)
        except (ValueError, KeyError):
            pass
        else:
            raise AssertionError("invalid cash input accepted")
    print("portfolio cash regressions passed: capex, debt, restrictions, financing, zero and incomplete inputs")


if __name__ == "__main__":
    main()
