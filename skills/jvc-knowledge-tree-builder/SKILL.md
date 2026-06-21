---
name: jvc-knowledge-tree-builder
description: Use when the user asks to read a local VC track, project, Obsidian, or source folder and convert existing files into a recursive question tree, Mermaid graph, evidence index, open-question list, and reusable nodes. Do not use for first-pass web research, one-off summaries, translation, or UI-only mind-map drawing.
metadata:
  author: jvc-analyst
---

# /jvc-knowledge-tree-builder — JVC Knowledge Tree Builder

Build a source-backed knowledge tree package from local VC files.

## Workflow

1. Resolve the folder or file list. If scope is broad, choose the nearest topic/project folder and report the boundary.
2. Inventory sources with `python3 scripts/collect_sources.py <path> --output <output_dir>/source_manifest.json` when practical.
3. Read the manifest and source files. Record unreadable or skipped files as access issues.
4. Model one root question, 5-9 branches, recursive child questions, and cross-links. Keep tree edges separate from graph relations.
5. Write `knowledge_tree.md`, `knowledge_graph.mmd`, `nodes.json`, `evidence_index.md`, and `open_questions.md`.
6. Validate against `references/output-contract.md`.

## Rules

- Preserve source paths as evidence references.
- Separate source facts, inference, and unknowns.
- Every node needs a question, summary, parent, open question, and evidence pointer or explicit evidence gap.
- Expand English abbreviations on first use with English full name, Chinese full name, and a brief explanation.
- If coverage is partial, state what was read, skipped, or unreadable.
- For VC work, keep investment conclusions separate; route comps, market sizing, bull/bear case, and IC memo to matching `jvc-*` skills.

## Reference Map

- `references/output-contract.md` — artifact schemas and validation checklist.
- `scripts/collect_sources.py` — deterministic source inventory and readable-text sampler.
