# JVC Knowledge Tree Builder

`jvc-knowledge-tree-builder` consumes an existing Track Research（Track Research，赛道研究：首次建立完整赛道证据与权威叙事）`landscape.md`, the Research Core（Research Core，研究证据内核：维护共享证据台账与审计状态）ledger, and user-specified local sources. It does not repeat the first complete web-based sector study.

## Fixed Outputs

The package contains exactly five non-empty files:

- `knowledge_tree.md`: visual-first primary user artifact with a Mermaid overview near the beginning.
- `knowledge_graph.mmd`: reusable Mermaid graph source.
- `nodes.json`: structured nodes and claimed relations.
- `evidence_index.md`: source and effective-claim mapping for nodes and relations.
- `open_questions.md`: unresolved questions grouped by branch.

`source_manifest.json`, when useful, is an intermediate inventory outside the five-file output package.

## Use

From the repository root:

```bash
python3 skills/jvc-knowledge-tree-builder/scripts/collect_sources.py /path/to/topic-folder --output /tmp/source_manifest.json
python3 skills/jvc-knowledge-tree-builder/scripts/validate_output.py /path/to/knowledge-package
python3 skills/jvc-knowledge-tree-builder/scripts/check_package.py
```

Run the structural validator before Research Core audit. A missing local renderer, an invalid graph, or a broken evidence mapping is a failed gate.

## Boundary and Updates

Use `/jvc-track-research` when the first complete sector study does not yet exist. Upstream changes mark only affected nodes, relations, and open questions as stale; executing the minimum update still requires user approval.
