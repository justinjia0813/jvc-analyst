#!/usr/bin/env python3
"""Validate jvc skill route and output eval fixtures.

This is deterministic fixture validation. It checks that eval cases point to
real skills, prompts carry their intended route signals, and output assertions
still match tracked templates/examples. It does not claim model-executed eval
evidence.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    if not path.is_file():
        raise AssertionError(f"missing eval file: {relative_path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_text(relative_path: str) -> str:
    path = ROOT / relative_path
    if not path.is_file():
        raise AssertionError(f"missing file: {relative_path}")
    return path.read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def skill_path(skill: str) -> Path:
    return ROOT / "skills" / skill / "SKILL.md"


def require_skill(skill: str) -> str:
    path = skill_path(skill)
    require(path.is_file(), f"missing skill: {skill}")
    text = path.read_text(encoding="utf-8")
    require(f"name: {skill}" in text, f"{skill} SKILL.md missing matching name")
    return text


def require_unique_ids(cases: list[dict[str, Any]], source: str) -> None:
    seen: set[str] = set()
    for case in cases:
        case_id = case.get("id")
        require(isinstance(case_id, str) and case_id, f"{source} case missing id")
        require(case_id not in seen, f"duplicate {source} case id: {case_id}")
        seen.add(case_id)


def check_trigger_cases() -> int:
    data = load_json("evals/trigger_cases.json")
    cases = data.get("cases")
    require(data.get("schema_version") == 1, "trigger cases schema_version must be 1")
    require(isinstance(cases, list) and cases, "trigger cases must be a non-empty list")
    require_unique_ids(cases, "trigger")

    expected_pairs = {
        ("jvc-prescreen", "jvc-ic-memo"),
        ("jvc-talk-notes", "jvc-meeting-notes"),
        ("jvc-meeting-notes", "jvc-talk-notes"),
        ("jvc-bull-case", "jvc-ic-memo"),
        ("jvc-bear-case", "jvc-bull-case"),
        ("jvc-ic-memo", "jvc-bull-case"),
        ("jvc-track-research", "jvc-comps-dd"),
        ("jvc-comps-dd", "jvc-track-research"),
        ("jvc-market-sizing", "jvc-track-research"),
        ("jvc-roi-modeler", "jvc-market-sizing"),
        ("jvc-invoice-manager", "jvc-comps-dd"),
    }
    covered_pairs: set[tuple[str, str]] = set()
    no_route_count = 0

    for case in cases:
        case_id = case["id"]
        prompt = case.get("prompt")
        require(isinstance(prompt, str) and prompt.strip(), f"{case_id}: missing prompt")
        for signal in case.get("prompt_signals", []):
            require(signal in prompt, f"{case_id}: prompt missing signal {signal!r}")

        expected_skill = case.get("expected_skill")
        if expected_skill is None:
            no_route_count += 1
            reason = case.get("no_route_reason")
            require(isinstance(reason, str) and reason.strip(), f"{case_id}: missing no_route_reason")
            for skill in case.get("should_not_trigger", []):
                require_skill(skill)
            continue

        require(isinstance(expected_skill, str) and expected_skill, f"{case_id}: missing expected_skill")
        skill_text = require_skill(expected_skill)
        for signal in case.get("skill_contract_signals", []):
            require(signal in skill_text, f"{case_id}: {expected_skill} missing contract signal {signal!r}")

        neighbors = case.get("near_neighbors", [])
        require(isinstance(neighbors, list) and neighbors, f"{case_id}: expected at least one near neighbor")
        for neighbor in neighbors:
            neighbor_skill = neighbor.get("skill")
            why_not = neighbor.get("why_not")
            require(isinstance(neighbor_skill, str) and neighbor_skill, f"{case_id}: neighbor missing skill")
            require_skill(neighbor_skill)
            require(isinstance(why_not, str) and why_not.strip(), f"{case_id}: neighbor {neighbor_skill} missing why_not")
            covered_pairs.add((expected_skill, neighbor_skill))

    missing_pairs = expected_pairs - covered_pairs
    require(not missing_pairs, f"missing near-neighbor trigger coverage: {sorted(missing_pairs)}")
    require(no_route_count >= 1, "trigger evals should include at least one no-route teaching/explanation case")
    routed_skills = {case.get("expected_skill") for case in cases if case.get("expected_skill")}
    skill_dirs = {path.parent.name for path in (ROOT / "skills").glob("jvc-*/SKILL.md")}
    missing_skills = skill_dirs - routed_skills
    require(not missing_skills, f"missing trigger coverage for skills: {sorted(missing_skills)}")
    return len(cases)


def check_assertion(case_id: str, assertion: dict[str, Any]) -> None:
    assertion_type = assertion.get("type")
    relative_path = assertion.get("path")
    if assertion_type in {"file_exists", "contains", "contains_any", "not_contains_any", "workbook_sheets"}:
        require(isinstance(relative_path, str) and relative_path, f"{case_id}: assertion missing path")

    if assertion_type == "file_exists":
        require((ROOT / relative_path).is_file(), f"{case_id}: missing file {relative_path}")
        return

    if assertion_type == "contains":
        text = assertion.get("text")
        require(isinstance(text, str) and text, f"{case_id}: contains assertion missing text")
        require(text in read_text(relative_path), f"{case_id}: {relative_path} missing {text!r}")
        return

    if assertion_type == "contains_any":
        texts = assertion.get("texts")
        require(isinstance(texts, list) and texts, f"{case_id}: contains_any missing texts")
        haystack = read_text(relative_path)
        require(any(isinstance(text, str) and text in haystack for text in texts), f"{case_id}: {relative_path} missing any of {texts!r}")
        return

    if assertion_type == "not_contains_any":
        texts = assertion.get("texts")
        require(isinstance(texts, list), f"{case_id}: not_contains_any missing texts")
        haystack = read_text(relative_path)
        found = [text for text in texts if isinstance(text, str) and text in haystack]
        require(not found, f"{case_id}: {relative_path} contains forbidden text {found!r}")
        return

    if assertion_type == "workbook_sheets":
        sheets = assertion.get("sheets")
        require(isinstance(sheets, list) and sheets, f"{case_id}: workbook_sheets missing sheets")
        try:
            from openpyxl import load_workbook
        except ImportError as exc:
            raise AssertionError("openpyxl is required for workbook_sheets assertions") from exc
        workbook_path = ROOT / relative_path
        require(workbook_path.is_file(), f"{case_id}: missing workbook {relative_path}")
        workbook = load_workbook(workbook_path, read_only=True)
        actual = set(workbook.sheetnames)
        missing = [sheet for sheet in sheets if sheet not in actual]
        require(not missing, f"{case_id}: {relative_path} missing workbook sheets {missing!r}")
        return

    raise AssertionError(f"{case_id}: unknown assertion type {assertion_type!r}")


def check_output_cases() -> int:
    data = load_json("evals/output/cases.json")
    cases = data.get("cases")
    require(data.get("schema_version") == 1, "output cases schema_version must be 1")
    require(isinstance(cases, list) and cases, "output cases must be a non-empty list")
    require_unique_ids(cases, "output")

    required_families = {"markdown", "excel", "docx", "excel_pdf_archive"}
    families: set[str] = set()
    for case in cases:
        case_id = case["id"]
        skill = case.get("skill")
        artifact_family = case.get("artifact_family")
        assertions = case.get("assertions")
        require(isinstance(skill, str) and skill, f"{case_id}: missing skill")
        require_skill(skill)
        require(isinstance(artifact_family, str) and artifact_family, f"{case_id}: missing artifact_family")
        families.add(artifact_family)
        require(isinstance(assertions, list) and assertions, f"{case_id}: missing assertions")
        for assertion in assertions:
            check_assertion(case_id, assertion)

    missing_families = required_families - families
    require(not missing_families, f"missing output artifact families: {sorted(missing_families)}")
    output_skills = {case.get("skill") for case in cases}
    skill_dirs = {path.parent.name for path in (ROOT / "skills").glob("jvc-*/SKILL.md")}
    missing_skills = skill_dirs - output_skills
    require(not missing_skills, f"missing output coverage for skills: {sorted(missing_skills)}")
    return len(cases)


def main() -> int:
    try:
        trigger_count = check_trigger_cases()
        output_count = check_output_cases()
    except AssertionError as exc:
        print(f"skill eval check failed: {exc}", file=sys.stderr)
        return 1

    print(f"skill eval fixtures passed: {trigger_count} trigger cases, {output_count} output cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
