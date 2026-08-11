#!/usr/bin/env python3
"""Exercise the Market Sizing CSV contract with valid and invalid fixtures."""

from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
from copy import deepcopy
from decimal import Decimal
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[1]
VALIDATOR = Path(__file__).with_name("validate_csv.py")
HEADER = [
    "section",
    "row_id",
    "item",
    "year",
    "unit",
    "conservative",
    "base",
    "optimistic",
    "source_or_formula",
    "confidence",
    "notes",
]
VALID_ROWS = [
    ["assumptions", "A_PRICE", "单客户年支出", "2026", "CNY/客户/年", "80000", "100000", "120000", "[S2]", "low", "示例输入"],
    ["top_down", "TD_MARKET", "上位市场规模", "2026", "CNY", "80000000000", "100000000000", "120000000000", "[S1]", "low", "示例输入"],
    ["top_down", "TD_SHARE", "细分赛道占比", "2026", "ratio", "0.08", "0.10", "0.12", "[S2]", "low", "示例输入"],
    ["top_down", "TD_SUMMARY", "自上而下市场规模", "2026", "CNY", "=TD_MARKET*TD_SHARE", "=TD_MARKET*TD_SHARE", "=TD_MARKET*TD_SHARE", "模型公式", "model", "[key_summary] TAM 汇总"],
    ["bottom_up", "BU_CUSTOMERS", "目标客户数", "2026", "客户", "40000", "50000", "60000", "[S1]", "low", "示例输入"],
    ["bottom_up", "BU_PENETRATION", "客户渗透率", "2026", "ratio", "0.04", "0.05", "0.06", "[S2]", "low", "示例输入"],
    ["bottom_up", "BU_SUMMARY", "自下而上市场规模", "2026", "CNY", "=BU_CUSTOMERS*A_PRICE*BU_PENETRATION", "=BU_CUSTOMERS*A_PRICE*BU_PENETRATION", "=BU_CUSTOMERS*A_PRICE*BU_PENETRATION", "模型公式", "model", "[key_summary] TAM 汇总"],
    ["reconciliation", "REC_ABS", "两种方法绝对差", "2026", "CNY", "=ABS(TD_SUMMARY-BU_SUMMARY)", "=ABS(TD_SUMMARY-BU_SUMMARY)", "=ABS(TD_SUMMARY-BU_SUMMARY)", "模型公式", "model", "[absolute_difference] 口径差异需结合覆盖范围解释"],
    ["reconciliation", "REC_REL", "两种方法相对差", "2026", "ratio", "=ABS(TD_SUMMARY-BU_SUMMARY)/TD_SUMMARY", "=ABS(TD_SUMMARY-BU_SUMMARY)/TD_SUMMARY", "=ABS(TD_SUMMARY-BU_SUMMARY)/TD_SUMMARY", "模型公式", "model", "[relative_difference] 以自上而下结果为分母"],
    ["orthogonality_check", "ORTHO_1", "关键输入共享检查", "2026", "flag", "0", "0", "0", "模型结构披露", "model", "shared_input=no；shared_row_ids=none；independent_validation=yes；两条路径使用不同的市场锚点"],
    ["sources", "S1", "示例行业报告", "2026", "", "", "", "", "https://example.invalid/report", "low", "虚构演示来源"],
    ["sources", "S2", "示例用户假设记录", "2026", "", "", "", "", "本地研究台账", "low", "虚构演示来源"],
]


def write_csv(path: Path, rows: list[list[str]], header: list[str] = HEADER) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def run_validator(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(path)],
        capture_output=True,
        text=True,
        check=False,
    )


def assert_valid(path: Path) -> None:
    result = run_validator(path)
    assert result.returncode == 0, result.stderr or result.stdout


def assert_invalid(path: Path, message: str) -> None:
    result = run_validator(path)
    assert result.returncode == 1, result.stderr or result.stdout
    assert message in result.stderr, result.stderr


def row_index(rows: list[list[str]], row_id: str) -> int:
    return next(index for index, row in enumerate(rows) if row[1] == row_id)


def mutated_csv(root: Path, name: str, mutate) -> Path:
    rows = deepcopy(VALID_ROWS)
    mutate(rows)
    path = root / f"{name}.csv"
    write_csv(path, rows)
    return path


def add_formula_cycle(rows: list[list[str]]) -> None:
    index = row_index(rows, "TD_SUMMARY")
    rows[index:index] = [
        ["top_down", "CYCLE_A", "循环节点 A", "2026", "CNY", "=CYCLE_B", "=CYCLE_B", "=CYCLE_B", "模型公式", "model", "两节点循环"],
        ["top_down", "CYCLE_B", "循环节点 B", "2026", "CNY", "=CYCLE_A", "=CYCLE_A", "=CYCLE_A", "模型公式", "model", "两节点循环"],
    ]


def add_summary_cycle(rows: list[list[str]]) -> None:
    index = row_index(rows, "TD_SUMMARY")
    rows.insert(
        index,
        ["top_down", "TD_LOOP", "汇总循环中间行", "2026", "CNY", "=TD_SUMMARY", "=TD_SUMMARY", "=TD_SUMMARY", "模型公式", "model", "汇总循环"],
    )
    rows[row_index(rows, "TD_SUMMARY")][5:8] = ["=TD_LOOP", "=TD_LOOP", "=TD_LOOP"]


def add_deep_formula_chain(rows: list[list[str]], depth: int = 1205) -> None:
    index = row_index(rows, "TD_SUMMARY")
    chain = [
        ["top_down", "TD_DEEP_0", "深链来源叶", "2026", "CNY", "1", "2", "3", "[S1]", "low", "深链输入"]
    ]
    for level in range(1, depth + 1):
        previous = f"TD_DEEP_{level - 1}"
        chain.append(
            [
                "top_down",
                f"TD_DEEP_{level}",
                f"深链中间行 {level}",
                "2026",
                "CNY",
                f"={previous}",
                f"={previous}",
                f"={previous}",
                "模型公式",
                "model",
                "迭代依赖验证",
            ]
        )
    rows[index:index] = chain
    terminal = f"TD_DEEP_{depth}"
    rows[row_index(rows, "TD_SUMMARY")][5:8] = [f"={terminal}"] * 3


def add_constant_intermediary(rows: list[list[str]]) -> None:
    index = row_index(rows, "TD_SUMMARY")
    rows.insert(
        index,
        ["top_down", "TD_CONST", "无来源常量中间行", "2026", "CNY", "=1+2", "=1+2", "=1+2", "模型公式", "model", "无输入常量"],
    )
    rows[row_index(rows, "TD_SUMMARY")][5:8] = ["=TD_CONST"] * 3


def check_numeric_arithmetic() -> None:
    by_id = {row[1]: row for row in VALID_ROWS}
    expected_top_down = (Decimal("6400000000"), Decimal("10000000000"), Decimal("14400000000"))
    expected_bottom_up = (Decimal("128000000"), Decimal("250000000"), Decimal("432000000"))
    for offset, expected in enumerate(expected_top_down, start=5):
        actual = Decimal(by_id["TD_MARKET"][offset]) * Decimal(by_id["TD_SHARE"][offset])
        assert actual == expected, (actual, expected)
    for offset, expected in enumerate(expected_bottom_up, start=5):
        actual = Decimal(by_id["BU_CUSTOMERS"][offset]) * Decimal(by_id["A_PRICE"][offset]) * Decimal(by_id["BU_PENETRATION"][offset])
        assert actual == expected, (actual, expected)


def main() -> int:
    assert VALIDATOR.is_file(), f"missing validator: {VALIDATOR}"
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        valid = root / "valid-formulas.csv"
        write_csv(valid, VALID_ROWS)
        assert_valid(valid)

        for packaged in (
            REPO_ROOT / "templates/market-sizing-template.csv",
            REPO_ROOT / "examples/market-sizing-example.csv",
        ):
            assert_valid(packaged)

        wrong_header = root / "wrong-header.csv"
        write_csv(wrong_header, VALID_ROWS, ["wrong", *HEADER[1:]])
        assert_invalid(wrong_header, "header mismatch")

        non_utf8 = root / "non-utf8.csv"
        non_utf8.write_bytes(b"section,row_id\n\xff")
        assert_invalid(non_utf8, "not strict UTF-8")

        assert_invalid(
            mutated_csv(root, "missing-section", lambda rows: rows.__setitem__(slice(None), [row for row in rows if row[0] != "sources"])),
            "missing sections",
        )
        assert_invalid(
            mutated_csv(root, "duplicate-row-id", lambda rows: rows[row_index(rows, "TD_SHARE")].__setitem__(1, "TD_MARKET")),
            "duplicate row_id",
        )
        assert_invalid(
            mutated_csv(root, "unknown-source", lambda rows: rows[row_index(rows, "TD_MARKET")].__setitem__(8, "[S99]")),
            "unknown source reference",
        )
        assert_invalid(
            mutated_csv(
                root,
                "input-without-source",
                lambda rows: (
                    rows[row_index(rows, "TD_MARKET")].__setitem__(8, "模型输入"),
                    rows[row_index(rows, "TD_MARKET")].__setitem__(9, "model"),
                ),
            ),
            "numeric model row missing source reference",
        )
        assert_invalid(
            mutated_csv(
                root,
                "mixed-scenarios-without-source",
                lambda rows: (
                    rows[row_index(rows, "TD_MARKET")].__setitem__(
                        slice(5, 8),
                        ["80000000000", "=TD_SHARE", "=TD_SHARE"],
                    ),
                    rows[row_index(rows, "TD_MARKET")].__setitem__(8, "混合场景"),
                ),
            ),
            "numeric model row missing source reference",
        )
        assert_invalid(
            mutated_csv(
                root,
                "source-reference-in-notes-only",
                lambda rows: (
                    rows[row_index(rows, "TD_MARKET")].__setitem__(8, "用户输入"),
                    rows[row_index(rows, "TD_MARKET")].__setitem__(10, "[S1] 错放在 notes"),
                ),
            ),
            "numeric model row missing source reference",
        )
        assert_invalid(
            mutated_csv(root, "missing-unit", lambda rows: rows[row_index(rows, "TD_MARKET")].__setitem__(4, "")),
            "missing unit",
        )
        assert_invalid(
            mutated_csv(root, "missing-year", lambda rows: rows[row_index(rows, "TD_MARKET")].__setitem__(3, "")),
            "missing year",
        )
        assert_invalid(
            mutated_csv(root, "invalid-scenario", lambda rows: rows[row_index(rows, "TD_MARKET")].__setitem__(5, "not-a-number")),
            "scenario is neither numeric nor formula",
        )
        assert_invalid(
            mutated_csv(root, "malformed-formula", lambda rows: rows[row_index(rows, "TD_SUMMARY")].__setitem__(5, "=TD_MARKET*")),
            "malformed formula",
        )
        assert_invalid(
            mutated_csv(root, "two-node-formula-cycle", add_formula_cycle),
            "formula dependency cycle in conservative",
        )
        assert_invalid(
            mutated_csv(root, "summary-formula-cycle", add_summary_cycle),
            "formula dependency cycle in conservative",
        )

        deep_chain = mutated_csv(root, "deep-formula-chain", add_deep_formula_chain)
        assert_valid(deep_chain)

        assert_invalid(
            mutated_csv(root, "constant-summary-intermediary", add_constant_intermediary),
            "key summary formula must reach a sourced numeric input",
        )
        assert_invalid(
            mutated_csv(root, "missing-two-way-reconciliation", lambda rows: [row.__setitem__(slice(5, 8), ["=TD_SUMMARY", "=TD_SUMMARY", "=TD_SUMMARY"]) for row in rows if row[0] == "reconciliation"]),
            "must reference top_down and bottom_up key summaries",
        )
        assert_invalid(
            mutated_csv(
                root,
                "reconciliation-bypasses-key-summaries",
                lambda rows: [
                    row.__setitem__(
                        slice(5, 8),
                        [
                            "=ABS(TD_MARKET-BU_CUSTOMERS)",
                            "=ABS(TD_MARKET-BU_CUSTOMERS)",
                            "=ABS(TD_MARKET-BU_CUSTOMERS)",
                        ],
                    )
                    for row in rows
                    if row[0] == "reconciliation"
                ],
            ),
            "must reference top_down and bottom_up key summaries",
        )
        assert_invalid(
            mutated_csv(
                root,
                "reconciliation-markers-share-row-id",
                lambda rows: (
                    rows[row_index(rows, "REC_ABS")].__setitem__(
                        10,
                        "[absolute_difference] [relative_difference] 两种差异误用同一行",
                    ),
                    rows.__setitem__(
                        slice(None),
                        [row for row in rows if row[1] != "REC_REL"],
                    ),
                ),
            ),
            "reconciliation markers must use different row_id",
        )
        assert_invalid(
            mutated_csv(root, "missing-orthogonality-disclosure", lambda rows: rows[row_index(rows, "ORTHO_1")].__setitem__(10, "尚未披露")),
            "missing shared_input disclosure",
        )
        assert_invalid(
            mutated_csv(root, "invalid-orthogonality-disclosure", lambda rows: rows[row_index(rows, "ORTHO_1")].__setitem__(10, "shared_input=yesmaybe；不是固定枚举")),
            "missing shared_input disclosure",
        )
        assert_invalid(
            mutated_csv(
                root,
                "partial-orthogonality-disclosure",
                lambda rows: rows[row_index(rows, "ORTHO_1")].__setitem__(
                    10,
                    "shared_input=no；只写了一个结构字段",
                ),
            ),
            "orthogonality disclosure fields must each appear exactly once",
        )
        assert_invalid(
            mutated_csv(
                root,
                "duplicate-orthogonality-field",
                lambda rows: rows[row_index(rows, "ORTHO_1")].__setitem__(
                    10,
                    "shared_input=no；shared_input=no；shared_row_ids=none；independent_validation=yes；重复字段",
                ),
            ),
            "orthogonality disclosure fields must each appear exactly once",
        )
        assert_invalid(
            mutated_csv(
                root,
                "conflicting-orthogonality-disclosures",
                lambda rows: rows.insert(
                    row_index(rows, "ORTHO_1") + 1,
                    [
                        "orthogonality_check",
                        "ORTHO_2",
                        "冲突独立性披露",
                        "2026",
                        "flag",
                        "0",
                        "0",
                        "0",
                        "模型结构披露",
                        "model",
                        "shared_input=no；shared_row_ids=none；independent_validation=no；与上一行冲突",
                    ],
                ),
            ),
            "orthogonality disclosures conflict",
        )
        assert_invalid(
            mutated_csv(
                root,
                "shared-input-disclosed-as-independent",
                lambda rows: (
                    rows[row_index(rows, "TD_SUMMARY")].__setitem__(
                        slice(5, 8),
                        [
                            "=TD_MARKET*TD_SHARE*A_PRICE",
                            "=TD_MARKET*TD_SHARE*A_PRICE",
                            "=TD_MARKET*TD_SHARE*A_PRICE",
                        ],
                    ),
                    rows[row_index(rows, "ORTHO_1")].__setitem__(
                        10,
                        "shared_input=no；shared_row_ids=none；independent_validation=yes；误称两条路径独立",
                    ),
                ),
            ),
            "orthogonality disclosure does not match detected shared inputs",
        )
        assert_invalid(
            mutated_csv(
                root,
                "transitive-shared-input-disclosed-as-independent",
                lambda rows: (
                    rows.insert(
                        row_index(rows, "TD_SUMMARY"),
                        [
                            "top_down",
                            "TD_PRICE_FACTOR",
                            "传递引用单客支出",
                            "2026",
                            "CNY/客户/年",
                            "=A_PRICE",
                            "=A_PRICE",
                            "=A_PRICE",
                            "模型公式",
                            "model",
                            "用于验证简单传递依赖",
                        ],
                    ),
                    rows[row_index(rows, "TD_SUMMARY")].__setitem__(
                        slice(5, 8),
                        [
                            "=TD_MARKET*TD_SHARE*TD_PRICE_FACTOR",
                            "=TD_MARKET*TD_SHARE*TD_PRICE_FACTOR",
                            "=TD_MARKET*TD_SHARE*TD_PRICE_FACTOR",
                        ],
                    ),
                ),
            ),
            "orthogonality disclosure does not match detected shared inputs",
        )
        assert_invalid(
            mutated_csv(
                root,
                "shared-input-with-independent-yes",
                lambda rows: (
                    rows[row_index(rows, "TD_SUMMARY")].__setitem__(
                        slice(5, 8),
                        [
                            "=TD_MARKET*TD_SHARE*A_PRICE",
                            "=TD_MARKET*TD_SHARE*A_PRICE",
                            "=TD_MARKET*TD_SHARE*A_PRICE",
                        ],
                    ),
                    rows[row_index(rows, "ORTHO_1")].__setitem__(
                        10,
                        "shared_input=yes；shared_row_ids=A_PRICE；independent_validation=yes；误称共享输入仍可独立验证",
                    ),
                ),
            ),
            "shared inputs cannot be independent validation",
        )
        assert_invalid(
            mutated_csv(root, "summary-without-input-reference", lambda rows: rows[row_index(rows, "TD_SUMMARY")].__setitem__(slice(5, 8), ["=100*0.08", "=100*0.10", "=100*0.12"])),
            "key summary formula must reach a sourced numeric input",
        )
        assert_invalid(
            mutated_csv(root, "reversed-scenarios", lambda rows: rows[row_index(rows, "TD_MARKET")].__setitem__(slice(5, 8), ["120", "100", "80"])),
            "scenario order is reversed",
        )
        assert_invalid(
            mutated_csv(
                root,
                "short-order-exception",
                lambda rows: (
                    rows[row_index(rows, "TD_MARKET")].__setitem__(slice(5, 8), ["120", "100", "80"]),
                    rows[row_index(rows, "TD_MARKET")].__setitem__(10, "[scenario_order_exception] x"),
                ),
            ),
            "scenario order is reversed",
        )
        assert_invalid(
            mutated_csv(
                root,
                "order-exception-with-prefix-only",
                lambda rows: (
                    rows[row_index(rows, "TD_MARKET")].__setitem__(slice(5, 8), ["120", "100", "80"]),
                    rows[row_index(rows, "TD_MARKET")].__setitem__(10, "前置备注已经足够长；[scenario_order_exception]"),
                ),
            ),
            "scenario order is reversed",
        )
        assert_invalid(
            mutated_csv(
                root,
                "punctuation-only-order-exception",
                lambda rows: (
                    rows[row_index(rows, "TD_MARKET")].__setitem__(slice(5, 8), ["120", "100", "80"]),
                    rows[row_index(rows, "TD_MARKET")].__setitem__(10, "[scenario_order_exception] ----"),
                ),
            ),
            "scenario order is reversed",
        )
        assert_invalid(
            mutated_csv(root, "invalid-confidence", lambda rows: rows[row_index(rows, "TD_MARKET")].__setitem__(9, "very-high")),
            "invalid confidence",
        )
        assert_invalid(
            mutated_csv(root, "formula-summary-high-confidence", lambda rows: rows[row_index(rows, "TD_SUMMARY")].__setitem__(9, "high")),
            "formula and structure rows must use model confidence",
        )
        assert_invalid(
            mutated_csv(root, "source-model-confidence", lambda rows: rows[row_index(rows, "S1")].__setitem__(9, "model")),
            "sources confidence must be high, medium, low, or unknown",
        )
        assert_invalid(
            mutated_csv(root, "numeric-input-model-confidence", lambda rows: rows[row_index(rows, "TD_MARKET")].__setitem__(9, "model")),
            "numeric input rows cannot use model confidence",
        )
        assert_invalid(
            mutated_csv(root, "structure-low-confidence", lambda rows: rows[row_index(rows, "ORTHO_1")].__setitem__(9, "low")),
            "formula and structure rows must use model confidence",
        )

        disclosed = mutated_csv(
            root,
            "disclosed-order-exception",
            lambda rows: (
                rows[row_index(rows, "TD_MARKET")].__setitem__(slice(5, 8), ["120", "100", "80"]),
                rows[row_index(rows, "TD_MARKET")].__setitem__(10, "[scenario_order_exception] 规模下降来自明确的监管收缩假设"),
            ),
        )
        assert_valid(disclosed)
        check_numeric_arithmetic()

    print("market-sizing package checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
