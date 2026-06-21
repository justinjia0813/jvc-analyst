#!/usr/bin/env python3
"""Lightweight package checks for jvc-knowledge-tree-builder."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "SKILL.md",
    "agents/interface.yaml",
    "manifest.json",
    "references/output-contract.md",
    "scripts/collect_sources.py",
]


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    if missing:
        print("Missing required files:")
        for path in missing:
            print(f"- {path}")
        return 1

    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    required_outputs = {
        "knowledge_tree.md",
        "knowledge_graph.mmd",
        "nodes.json",
        "evidence_index.md",
        "open_questions.md",
    }
    actual_outputs = set(manifest.get("output_contract", []))
    if not required_outputs.issubset(actual_outputs):
        print("manifest.json output_contract is incomplete")
        return 1

    skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    for needle in ["recursive question tree", "knowledge_graph.mmd", "English abbreviations"]:
        if needle not in skill_text:
            print(f"SKILL.md missing required phrase: {needle}")
            return 1

    print("jvc-knowledge-tree-builder package check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
