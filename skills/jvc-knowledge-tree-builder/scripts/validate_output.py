#!/usr/bin/env python3
"""Validate the fixed five-file Knowledge Tree output package."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


OUTPUTS = {
    "knowledge_tree.md",
    "knowledge_graph.mmd",
    "nodes.json",
    "evidence_index.md",
    "open_questions.md",
}
MERMAID_FENCES = {"```mermaid", "```{mermaid}"}
GRAPH_DECLARATION = re.compile(r"(?:graph|flowchart)\s+(?:TB|TD|BT|RL|LR)")
EVIDENCE_HEADING = re.compile(r"^##\s+(S[0-9A-Za-z._-]+)\s*$", re.MULTILINE)
EVIDENCE_MAPPING = re.compile(r"^\s*-\s*(映射节点|映射关系)：(.*)$")
BACKTICK_ID = re.compile(r"`([^`]+)`")
NODE_STATUSES = {"source-backed", "inferred", "needs-evidence", "open-question"}
RELATION_TYPES = {"related", "depends_on", "contrasts_with", "affects", "parent"}


def fail(message: str) -> int:
    print(f"validation failed: {message}", file=sys.stderr)
    return 1


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return text
    closing = next(
        (index for index, line in enumerate(lines[1:], start=1) if line in {"---", "..."}),
        None,
    )
    return "" if closing is None else "\n".join(lines[closing + 1 :])


def evidence_sections(text: str) -> dict[str, dict[str, set[str]]]:
    text = strip_frontmatter(text)
    matches = list(EVIDENCE_HEADING.finditer(text))
    sections: dict[str, dict[str, set[str]]] = {}
    for index, heading in enumerate(matches):
        source_id = heading.group(1)
        block = text[
            heading.end() : matches[index + 1].start()
            if index + 1 < len(matches)
            else len(text)
        ]
        mapping = sections.setdefault(source_id, {"node": set(), "relation": set()})
        for line in block.splitlines():
            match = EVIDENCE_MAPPING.fullmatch(line)
            if match:
                kind = "node" if match.group(1) == "映射节点" else "relation"
                mapping[kind].update(BACKTICK_ID.findall(match.group(2)))
    return sections


def visible_evidence_error(
    item: dict[str, Any],
    item_id: str,
    sections: dict[str, dict[str, set[str]]],
    kind: str,
) -> str | None:
    references = item.get("evidence_refs", [])
    gap = item.get("evidence_gap")
    if not isinstance(references, list) or any(
        not non_empty_string(value) for value in references
    ):
        return f"invalid evidence_refs for {kind}: {item_id}"
    if references:
        for reference in references:
            section = sections.get(reference)
            if section is None or item_id not in section[kind]:
                return f"evidence pointer not visible for {kind} {item_id}: {reference}"
        return None
    if non_empty_string(gap):
        return None
    return f"{kind} missing evidence pointer or explicit gap: {item_id}"


def mermaid_block_error(text: str) -> str | None:
    lines = strip_frontmatter(text).splitlines()
    opening = next(
        (
            index
            for index in range(min(len(lines), 40))
            if lines[index].strip() in MERMAID_FENCES
        ),
        None,
    )
    if opening is None:
        return "knowledge_tree.md missing complete Mermaid near beginning"
    closing = next(
        (index for index in range(opening + 1, len(lines)) if lines[index].strip() == "```"),
        None,
    )
    if closing is None:
        return "knowledge_tree.md Mermaid fence is not closed"
    first_line = next(
        (line.strip() for line in lines[opening + 1 : closing] if line.strip()), ""
    )
    if GRAPH_DECLARATION.fullmatch(first_line) is None:
        return "knowledge_tree.md Mermaid block missing supported graph declaration"
    return None


def validate_nodes(data: Any, evidence_text: str) -> str | None:
    if not isinstance(data, dict) or not isinstance(data.get("nodes"), list):
        return "nodes.json must contain a nodes array"
    nodes = data["nodes"]
    if not nodes:
        return "nodes.json nodes array is empty"
    if any(not isinstance(node, dict) for node in nodes):
        return "nodes.json node must be an object"

    identifiers: list[str] = []
    for node in nodes:
        identifier = node.get("id")
        if not non_empty_string(identifier):
            return "node id must be a non-empty string"
        if identifier in identifiers:
            return f"duplicate node id: {identifier}"
        identifiers.append(identifier)
        for field in ("title", "question", "summary"):
            if not non_empty_string(node.get(field)):
                return f"node {field} must be a non-empty string: {identifier}"
        status = node.get("status")
        if not non_empty_string(status) or status not in NODE_STATUSES:
            return f"invalid node status: {identifier}"
        parent = node.get("parent_id")
        if "parent_id" not in node or (
            parent is not None and not non_empty_string(parent)
        ):
            return f"node parent_id must be null or a non-empty string: {identifier}"

    known = set(identifiers)
    roots: list[str] = []
    for node in nodes:
        identifier = node["id"]
        parent = node["parent_id"]
        if parent is None:
            if node["status"] == "open-question":
                continue
            roots.append(identifier)
        elif parent not in known:
            return f"missing parent for {identifier}: {parent}"
    if not roots:
        return "missing root node"
    if len(roots) > 1:
        return f"isolated non-root node: {roots[1]}"
    root = roots[0]

    parent_by_id = {node["id"]: node["parent_id"] for node in nodes}
    status_by_id = {node["id"]: node["status"] for node in nodes}
    for identifier in identifiers:
        trail: list[str] = []
        current: str | None = identifier
        while current is not None:
            if current in trail:
                cycle = trail[trail.index(current) :] + [current]
                return f"parent cycle: {' -> '.join(cycle)}"
            trail.append(current)
            current = parent_by_id[current]
        if status_by_id[identifier] != "open-question" and trail[-1] != root:
            return f"node ancestry does not reach root: {identifier}"

    sections = evidence_sections(evidence_text)
    for node in nodes:
        error = visible_evidence_error(node, node["id"], sections, "node")
        if error:
            return error

    relations = data.get("relations")
    if (
        not isinstance(relations, list)
        or not relations
        or any(not isinstance(relation, dict) for relation in relations)
    ):
        return "nodes.json requires a non-empty relations array"

    relation_ids: set[str] = set()
    for relation in relations:
        relation_id = relation.get("id")
        if not non_empty_string(relation_id):
            return "relation id must be a non-empty string"
        if relation_id in relation_ids:
            return f"duplicate relation id: {relation_id}"
        relation_ids.add(relation_id)

        source = relation.get("from")
        target = relation.get("to")
        if not non_empty_string(source) or not non_empty_string(target):
            return f"relation from/to must be non-empty strings: {relation_id}"
        relation_type = relation.get("type")
        if not non_empty_string(relation_type) or relation_type not in RELATION_TYPES:
            return f"invalid relation type: {relation_id}"
        if not non_empty_string(relation.get("claim")):
            return f"relation claim must be a non-empty string: {relation_id}"
        if source not in known or target not in known:
            return f"relation endpoint missing: {relation_id}"

        references = relation.get("evidence_refs", [])
        gap = relation.get("evidence_gap")
        if not references and not non_empty_string(gap):
            return f"claimed relation missing evidence mapping: {relation_id}"
        error = visible_evidence_error(relation, relation_id, sections, "relation")
        if error:
            return error
    return None


def validate(package: Path) -> str | None:
    if not package.is_dir():
        return f"package directory not found: {package}"
    actual = {path.name for path in package.iterdir()}
    if actual != OUTPUTS:
        return "package must contain exactly five files"
    for name in sorted(OUTPUTS):
        path = package / name
        if not path.is_file() or path.stat().st_size == 0:
            return f"required file is empty: {name}"

    try:
        tree = (package / "knowledge_tree.md").read_text(encoding="utf-8")
        graph = (package / "knowledge_graph.mmd").read_text(encoding="utf-8")
        evidence = (package / "evidence_index.md").read_text(encoding="utf-8")
        data = json.loads((package / "nodes.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return f"cannot read package: {error}"

    error = mermaid_block_error(tree)
    if error:
        return error
    first_graph_line = next((line.strip() for line in graph.splitlines() if line.strip()), "")
    if GRAPH_DECLARATION.fullmatch(first_graph_line) is None:
        return "knowledge_graph.mmd missing supported graph declaration"
    return validate_nodes(data, evidence)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        return fail("usage: validate_output.py <knowledge-package-directory>")
    error = validate(Path(argv[1]))
    if error:
        return fail(error)
    print("knowledge tree validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
