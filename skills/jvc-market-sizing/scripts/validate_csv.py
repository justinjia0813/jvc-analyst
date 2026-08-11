#!/usr/bin/env python3
"""Validate the auditable single-file Market Sizing CSV contract."""

from __future__ import annotations

import ast
import csv
import io
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path


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
SECTIONS = {
    "assumptions",
    "top_down",
    "bottom_up",
    "reconciliation",
    "orthogonality_check",
    "sources",
}
CONFIDENCE = {"high", "medium", "low", "model", "unknown"}
SOURCE_CONFIDENCE = {"high", "medium", "low", "unknown"}
INPUT_SECTIONS = {"assumptions", "top_down", "bottom_up"}
SCENARIO_COLUMNS = range(5, 8)
ROW_ID = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
SOURCE_ID = re.compile(r"S[1-9]\d*\Z")
SOURCE_REFERENCE = re.compile(r"\[(S[^\]]+)\]")
YEAR = re.compile(r"\d{4}\Z")
KEY_SUMMARY = "[key_summary]"
ORDER_EXCEPTION = "[scenario_order_exception]"
RECONCILIATION_MARKERS = {"[absolute_difference]", "[relative_difference]"}
DISCLOSURE_SEPARATOR = r"(?=$|[；;])"
SHARED_INPUT = re.compile(rf"(?:^|[；;])shared_input=(yes|no){DISCLOSURE_SEPARATOR}")
SHARED_ROW_IDS = re.compile(
    rf"(?:^|[；;])shared_row_ids=(none|[A-Za-z_][A-Za-z0-9_]*(?:\|[A-Za-z_][A-Za-z0-9_]*)*){DISCLOSURE_SEPARATOR}"
)
INDEPENDENT_VALIDATION = re.compile(
    rf"(?:^|[；;])independent_validation=(yes|no){DISCLOSURE_SEPARATOR}"
)
FORMULA_FUNCTIONS = {"ABS": 1}
ALLOWED_AST_NODES = {
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Call,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.UAdd,
    ast.USub,
}


def explanatory_text(notes: str, *markers: str, minimum: int = 4) -> bool:
    for marker in markers:
        notes = notes.replace(marker, "")
    return sum(character.isalnum() for character in notes) >= minimum


def explanatory_text_after(notes: str, marker: str, minimum: int = 4) -> bool:
    _, found, suffix = notes.partition(marker)
    return bool(found) and explanatory_text(suffix, marker, minimum=minimum)


def parse_formula(
    value: str,
    row_id: str,
    declared_model_ids: set[str],
) -> tuple[set[str], str | None]:
    try:
        tree = ast.parse(value[1:], mode="eval")
    except SyntaxError:
        return set(), "malformed formula"
    if not value[1:].strip() or any(type(node) not in ALLOWED_AST_NODES for node in ast.walk(tree)):
        return set(), "malformed formula"

    function_nodes: set[int] = set()
    for call in (node for node in ast.walk(tree) if isinstance(node, ast.Call)):
        if (
            not isinstance(call.func, ast.Name)
            or call.func.id not in FORMULA_FUNCTIONS
            or len(call.args) != FORMULA_FUNCTIONS[call.func.id]
            or call.keywords
        ):
            return set(), "malformed formula"
        function_nodes.add(id(call.func))
    if any(
        isinstance(node, ast.Constant)
        and (type(node.value) not in {int, float} or not Decimal(str(node.value)).is_finite())
        for node in ast.walk(tree)
    ):
        return set(), "malformed formula"

    references = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and id(node) not in function_nodes
    }
    unknown = references - declared_model_ids
    if unknown:
        return references, f"formula references unknown row_id: {sorted(unknown)}"
    if row_id in references:
        return references, "formula directly references its own row_id"
    return references, None


def numeric_value(value: str) -> Decimal | None:
    try:
        number = Decimal(value)
    except InvalidOperation:
        return None
    return number if number.is_finite() else None


def find_dependency_cycle(
    column: int,
    formula_references: dict[tuple[str, int], set[str]],
) -> list[str] | None:
    formula_rows = {
        row_id for row_id, scenario_column in formula_references if scenario_column == column
    }
    state: dict[str, int] = {}
    for start in sorted(formula_rows):
        if state.get(start, 0):
            continue
        state[start] = 1
        path = [start]
        positions = {start: 0}
        stack = [
            (start, iter(sorted(formula_references.get((start, column), set()))))
        ]
        while stack:
            row_id, children = stack[-1]
            try:
                child = next(children)
            except StopIteration:
                stack.pop()
                state[row_id] = 2
                positions.pop(row_id, None)
                path.pop()
                continue
            if child not in formula_rows:
                continue
            child_state = state.get(child, 0)
            if child_state == 1:
                return path[positions[child] :] + [child]
            if child_state == 2:
                continue
            state[child] = 1
            positions[child] = len(path)
            path.append(child)
            stack.append(
                (child, iter(sorted(formula_references.get((child, column), set()))))
            )
    return None


def input_dependencies(
    row_id: str,
    column: int,
    formula_references: dict[tuple[str, int], set[str]],
    scenario_numbers: dict[str, list[Decimal | None]],
) -> set[str]:
    seen: set[str] = set()
    dependencies: set[str] = set()
    stack = [row_id]
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        for reference in formula_references.get((current, column), set()):
            numbers = scenario_numbers.get(reference)
            if numbers and numbers[column - SCENARIO_COLUMNS.start] is not None:
                dependencies.add(reference)
            elif reference not in seen:
                stack.append(reference)
    return dependencies


def read_rows(path: Path) -> tuple[list[list[str]], list[str]]:
    try:
        text = path.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        return [], ["not strict UTF-8"]
    try:
        rows = list(csv.reader(io.StringIO(text, newline="")))
    except csv.Error as exc:
        return [], [f"malformed CSV: {exc}"]
    if not rows:
        return [], ["empty CSV"]
    if rows[0] != HEADER:
        return [], ["header mismatch"]
    if any(len(row) != len(HEADER) for row in rows):
        return [], ["row width mismatch"]
    return rows[1:], []


def validate(path: Path) -> list[str]:
    rows, errors = read_rows(path)
    if errors:
        return errors

    sections = {row[0] for row in rows}
    unknown_sections = sections - SECTIONS
    if unknown_sections:
        errors.append(f"unknown sections: {sorted(unknown_sections)}")
    missing_sections = SECTIONS - sections
    if missing_sections:
        errors.append(f"missing sections: {sorted(missing_sections)}")

    row_ids = [row[1] for row in rows]
    seen: set[str] = set()
    for row_id in row_ids:
        if not ROW_ID.fullmatch(row_id):
            errors.append(f"invalid row_id: {row_id!r}")
        elif row_id in seen:
            errors.append(f"duplicate row_id: {row_id}")
        seen.add(row_id)

    by_id = {row[1]: row for row in rows}
    model_ids = {row[1] for row in rows if row[0] != "sources"}
    source_ids = {row[1] for row in rows if row[0] == "sources" and SOURCE_ID.fullmatch(row[1])}
    formula_references: dict[tuple[str, int], set[str]] = {}
    scenario_numbers: dict[str, list[Decimal | None]] = {}
    valid_source_references: dict[str, set[str]] = {}

    for row in rows:
        section, row_id, item, year, unit = row[:5]
        source_or_formula, confidence, notes = row[8:11]
        if not item.strip():
            errors.append(f"{row_id}: missing item")
        if confidence not in CONFIDENCE:
            errors.append(f"{row_id}: invalid confidence: {confidence!r}")

        source_references = set(SOURCE_REFERENCE.findall(source_or_formula))
        valid_source_references[row_id] = source_references & source_ids
        for source_id in SOURCE_REFERENCE.findall(f"{source_or_formula} {notes}"):
            if source_id not in source_ids:
                errors.append(f"{row_id}: unknown source reference [{source_id}]")

        if section == "sources":
            if confidence not in SOURCE_CONFIDENCE:
                errors.append(
                    f"{row_id}: sources confidence must be high, medium, low, or unknown"
                )
            if not SOURCE_ID.fullmatch(row_id):
                errors.append(f"{row_id}: sources row_id must match S<number>")
            if not source_or_formula.strip():
                errors.append(f"{row_id}: missing source location")
            continue

        if not year.strip():
            errors.append(f"{row_id}: missing year")
        elif not YEAR.fullmatch(year):
            errors.append(f"{row_id}: invalid year: {year!r}")
        if not unit.strip():
            errors.append(f"{row_id}: missing unit")
        if not source_or_formula.strip():
            errors.append(f"{row_id}: missing source_or_formula")

        numbers: list[Decimal | None] = []
        has_formula = False
        for column in SCENARIO_COLUMNS:
            value = row[column].strip()
            number = numeric_value(value)
            numbers.append(number)
            if number is not None:
                continue
            if not value.startswith("="):
                errors.append(f"{row_id}/{HEADER[column]}: scenario is neither numeric nor formula")
                continue
            has_formula = True
            formula_refs, formula_error = parse_formula(value, row_id, model_ids)
            formula_references[(row_id, column)] = formula_refs
            if formula_error:
                errors.append(f"{row_id}/{HEADER[column]}: {formula_error}")
        scenario_numbers[row_id] = numbers
        has_numeric = any(number is not None for number in numbers)
        all_formulas = all(row[column].strip().startswith("=") for column in SCENARIO_COLUMNS)

        if section == "orthogonality_check" or all_formulas:
            if confidence != "model":
                errors.append(
                    f"{row_id}: formula and structure rows must use model confidence"
                )
        elif section in INPUT_SECTIONS and has_numeric and confidence == "model":
            errors.append(f"{row_id}: numeric input rows cannot use model confidence")

        if section in INPUT_SECTIONS and has_numeric and not valid_source_references[row_id]:
            errors.append(f"{row_id}: numeric model row missing source reference")

        if all(number is not None for number in numbers):
            conservative, base, optimistic = numbers
            assert conservative is not None and base is not None and optimistic is not None
            if not conservative <= base <= optimistic:
                if not explanatory_text_after(
                    notes, ORDER_EXCEPTION, minimum=4
                ):
                    errors.append(f"{row_id}: scenario order is reversed without disclosed business explanation")
        elif not has_formula:
            errors.append(f"{row_id}: no valid scenario values")

        if source_or_formula.startswith("="):
            _, formula_error = parse_formula(source_or_formula, row_id, model_ids)
            if formula_error:
                errors.append(f"{row_id}/source_or_formula: {formula_error}")

    for column in SCENARIO_COLUMNS:
        cycle = find_dependency_cycle(column, formula_references)
        if cycle:
            errors.append(
                f"formula dependency cycle in {HEADER[column]}: {' -> '.join(cycle)}"
            )

    key_summary_ids = {
        row[1]
        for row in rows
        if row[0] in {"top_down", "bottom_up"} and KEY_SUMMARY in row[10]
    }
    for section in ("top_down", "bottom_up"):
        summaries = [row for row in rows if row[0] == section and row[1] in key_summary_ids]
        if not summaries:
            errors.append(f"{section}: missing {KEY_SUMMARY} row")
        for row in summaries:
            for column in SCENARIO_COLUMNS:
                sourced_inputs = {
                    dependency
                    for dependency in input_dependencies(
                        row[1],
                        column,
                        formula_references,
                        scenario_numbers,
                    )
                    if by_id.get(dependency, [""])[0] in {"assumptions", section}
                    and valid_source_references.get(dependency)
                }
                if not sourced_inputs:
                    errors.append(
                        f"{row[1]}/{HEADER[column]}: key summary formula must reach a sourced numeric input"
                    )

    top_down_summary_ids = {
        row[1] for row in rows if row[0] == "top_down" and row[1] in key_summary_ids
    }
    bottom_up_summary_ids = {
        row[1] for row in rows if row[0] == "bottom_up" and row[1] in key_summary_ids
    }
    reconciliation_rows = [row for row in rows if row[0] == "reconciliation"]
    reconciliation_marker_rows = {
        marker: {row[1] for row in reconciliation_rows if marker in row[10]}
        for marker in RECONCILIATION_MARKERS
    }
    for marker in RECONCILIATION_MARKERS:
        if not reconciliation_marker_rows[marker]:
            errors.append(f"reconciliation: missing {marker} row")
    absolute_rows = reconciliation_marker_rows["[absolute_difference]"]
    relative_rows = reconciliation_marker_rows["[relative_difference]"]
    if absolute_rows & relative_rows:
        errors.append("reconciliation markers must use different row_id")
    for row in reconciliation_rows:
        if not any(marker in row[10] for marker in RECONCILIATION_MARKERS):
            continue
        for column in SCENARIO_COLUMNS:
            references = formula_references.get((row[1], column), set())
            if (
                not references & top_down_summary_ids
                or not references & bottom_up_summary_ids
            ):
                errors.append(
                    f"{row[1]}/{HEADER[column]}: reconciliation must reference top_down and bottom_up key summaries"
                )

    shared_inputs: set[str] = set()
    for column in SCENARIO_COLUMNS:
        top_down_inputs: set[str] = set()
        bottom_up_inputs: set[str] = set()
        for row_id in top_down_summary_ids:
            top_down_inputs.update(
                input_dependencies(
                    row_id,
                    column,
                    formula_references,
                    scenario_numbers,
                )
            )
        for row_id in bottom_up_summary_ids:
            bottom_up_inputs.update(
                input_dependencies(
                    row_id,
                    column,
                    formula_references,
                    scenario_numbers,
                )
            )
        shared_inputs.update(top_down_inputs & bottom_up_inputs)

    orthogonality_rows = [row for row in rows if row[0] == "orthogonality_check"]
    disclosures = 0
    normalized_disclosures: set[tuple[bool, tuple[str, ...], str]] = set()
    for row in orthogonality_rows:
        notes = row[10]
        field_patterns = {
            "shared_input": SHARED_INPUT,
            "shared_row_ids": SHARED_ROW_IDS,
            "independent_validation": INDEPENDENT_VALIDATION,
        }
        raw_counts = {
            field: notes.count(f"{field}=") for field in field_patterns
        }
        if not any(raw_counts.values()):
            continue
        matches = {
            field: list(pattern.finditer(notes))
            for field, pattern in field_patterns.items()
        }
        if any(
            raw_counts[field] != 1 or len(matches[field]) != 1
            for field in field_patterns
        ):
            errors.append(
                f"{row[1]}: orthogonality disclosure fields must each appear exactly once"
            )
            continue
        shared_match = matches["shared_input"][0]
        ids_match = matches["shared_row_ids"][0]
        independent_match = matches["independent_validation"][0]
        disclosures += 1
        structured_fields = (
            shared_match.group(0),
            ids_match.group(0),
            independent_match.group(0),
        )
        if not explanatory_text(notes, *structured_fields, minimum=4):
            errors.append(f"{row[1]}: orthogonality disclosure missing explanation")
        disclosed_shared = shared_match.group(1) == "yes"
        disclosed_ids = (
            set()
            if ids_match.group(1) == "none"
            else set(ids_match.group(1).split("|"))
        )
        independent = independent_match.group(1)
        normalized_disclosures.add(
            (disclosed_shared, tuple(sorted(disclosed_ids)), independent)
        )
        if disclosed_shared != bool(shared_inputs) or disclosed_ids != shared_inputs:
            errors.append(
                f"{row[1]}: orthogonality disclosure does not match detected shared inputs: {sorted(shared_inputs)}"
            )
        if disclosed_shared and independent == "yes":
            errors.append(f"{row[1]}: shared inputs cannot be independent validation")
    if not disclosures:
        errors.append("orthogonality_check: missing shared_input disclosure")
    if len(normalized_disclosures) > 1:
        errors.append("orthogonality disclosures conflict")

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
