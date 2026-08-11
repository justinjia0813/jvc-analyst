#!/usr/bin/env python3
"""Validate the fixed ROI Modeler CSV layout and return formulas."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path


DEFAULT_HEADER = [
    "section",
    "metric",
    "unit",
    "2024_实际",
    "2025_预测",
    "2026_预测_B轮",
    "2027_预测_C轮",
    "2028_预测_上市申报",
    "2029_预测_上市",
    "2030_退出_保守",
    "2030_退出_中性",
    "2030_退出_乐观",
    "source_id",
    "assumption_status",
    "notes",
]
METRICS = [
    "model_status",
    "dilution_rate",
    "revenue",
    "net_income",
    "net_margin",
    "valuation_method",
    "price_to_sales",
    "price_to_earnings",
    "company_valuation",
    "fund_ownership",
    "fund_equity_value",
    "invested_capital",
    "proceeds",
    "net_gain",
    "MOIC",
    "cumulative_return",
    "IRR",
    "scenario",
    "cash_flow_conservative",
    "cash_flow_base",
    "cash_flow_optimistic",
]
SOURCE_ROWS = {
    "dilution_rate",
    "revenue",
    "net_income",
    "valuation_method",
    "price_to_earnings",
    "company_valuation",
    "invested_capital",
}
SOURCE_ID = re.compile(r"\[S[1-9]\d*\]")


def expected_formulas() -> dict[tuple[str, int], str]:
    formulas: dict[tuple[str, int], str] = {}
    for col in range(3, 12):
        letter = chr(ord("A") + col)
        formulas[("net_margin", col)] = f"=IF({letter}4=0,NA(),{letter}5/{letter}4)"
    for col in range(4, 12):
        letter = chr(ord("A") + col)
        formulas[("price_to_sales", col)] = f"=IF({letter}4=0,NA(),{letter}10/{letter}4)"
    for col in (4, 5):
        letter = chr(ord("A") + col)
        formulas[("price_to_earnings", col)] = f"=IF({letter}5=0,NA(),{letter}10/{letter}5)"
    for col in range(6, 12):
        letter = chr(ord("A") + col)
        formulas[("company_valuation", col)] = f"={letter}5*{letter}9"
    formulas[("fund_ownership", 4)] = "=IF(E10=0,NA(),E13/E10)"
    for col in range(5, 9):
        letter = chr(ord("A") + col)
        previous = chr(ord(letter) - 1)
        formulas[("fund_ownership", col)] = f"={previous}11*(1-{letter}3)"
    for col in range(9, 12):
        letter = chr(ord("A") + col)
        formulas[("fund_ownership", col)] = f"=I11*(1-{letter}3)"
    for col in range(4, 12):
        letter = chr(ord("A") + col)
        formulas[("fund_equity_value", col)] = f"={letter}10*{letter}11"
    for col in range(9, 12):
        letter = chr(ord("A") + col)
        formulas[("invested_capital", col)] = "=SUM($D$13:$I$13)"
        formulas[("proceeds", col)] = f"={letter}12"
        formulas[("net_gain", col)] = f"={letter}14-{letter}13"
        formulas[("MOIC", col)] = f"=IF({letter}13=0,NA(),{letter}14/{letter}13)"
        formulas[("cumulative_return", col)] = f"=IF({letter}13=0,NA(),{letter}15/{letter}13)"
    for col, row in zip(range(9, 12), range(20, 23)):
        letter = chr(ord("A") + col)
        formulas[("IRR", col)] = (
            f'=IF(AND(COUNTIF(D{row}:I{row},"<0")>0,'
            f'COUNTIF(D{row}:I{row},">0")>0),IRR(D{row}:I{row}),NA())'
        )
    for metric, terminal_col in (
        ("cash_flow_conservative", "J"),
        ("cash_flow_base", "K"),
        ("cash_flow_optimistic", "L"),
    ):
        for col, source_col in zip(range(3, 8), "EFGHI"):
            formulas[(metric, col)] = f"=-{source_col}13"
        formulas[(metric, 8)] = f"={terminal_col}14"
    return formulas


def validate(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.reader(handle))
    if not rows:
        return ["empty CSV"]
    errors: list[str] = []
    header = rows[0]
    if (
        len(header) != len(DEFAULT_HEADER)
        or header[:3] != DEFAULT_HEADER[:3]
        or header[-3:] != DEFAULT_HEADER[-3:]
        or len(set(header[3:12])) != 9
        or not all(header[3:12])
        or not all(
            label in header[index]
            for index, label in zip(range(9, 12), ("保守", "中性", "乐观"))
        )
    ):
        errors.append("header mismatch")
    if any(len(row) != len(DEFAULT_HEADER) for row in rows):
        errors.append("row width mismatch")
        return errors
    metrics = [row[1] for row in rows[1:]]
    if metrics != METRICS:
        errors.append("metric order mismatch")
        return errors
    by_metric = {row[1]: row for row in rows[1:]}
    for metric in SOURCE_ROWS:
        if not SOURCE_ID.search(by_metric[metric][12]):
            errors.append(f"{metric}: missing [S编号]")
        if not by_metric[metric][13]:
            errors.append(f"{metric}: missing assumption_status")
    for (metric, col), formula in expected_formulas().items():
        actual = by_metric[metric][col]
        if actual != formula:
            errors.append(f"{metric}/{header[col]}: expected {formula}, got {actual}")
    follow_on_values = by_metric["invested_capital"][5:9]
    if any(value.strip() not in {"", "0", "0.0"} for value in follow_on_values):
        errors.append("follow-on investment requires an extended ownership contract")
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} FILE.csv", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if path.suffix.lower() != ".csv" or not path.is_file():
        print(f"invalid CSV path: {path}", file=sys.stderr)
        return 2
    errors = validate(path)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"validated {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
