---
name: jvc-knowledge-tree-builder
description: |
  内部支持，非独立认知入口。知识树构建器：读取本地 VC 赛道/项目/Obsidian 文件夹，将其中的文件转化为递归问题树、Mermaid 知识图谱、证据索引、开放问题清单和可复用节点。用于沉淀已有研究资料，不作为首次网页调研工具。
  Use when user says '/jvc-knowledge-tree-builder', '知识树', 'knowledge tree', '构建知识图谱', '整理研究资料', or asks to read a local VC track, project, Obsidian, or source folder and convert existing files into a recursive question tree, Mermaid graph, evidence index, open-question list, and reusable nodes. Do not use for first-pass web research, one-off summaries, translation, or UI-only mind-map drawing.
user_invocable: false
version: "3.0.0"
---

# jvc-knowledge-tree-builder — JVC Knowledge Tree Builder

内部支持：本模块是 `jvc-track-research`（赛道研究）的知识整理环节，不列入默认 slash 命令清单。用户要把本地资料文件夹整理成知识树，或显式指定本名称时，按本文件执行。

Build a source-backed knowledge tree package from local VC files.

## 3.0 适用级别

最低适用级别：**L1+**（Level 1 or above，一级及以上初筛，用于形成可验证研究假设）。

- 若输入属于具体项目，先读取 `spec/CONTEXT.md` 与 `spec/hypotheses.md`；若属于赛道，先确认 `tracks/{track-slug}/` 的边界。
- 当前项目仍为 L0 时，先说明知识树会增加结构化维护成本，由用户确认是否升级或只做一次性整理。
- 本 Skill 复用已有材料，不为了填满树而新增未经验证的节点或关系。

## 反合理化约束

- “文件相邻，所以概念有关联” → 关系必须来自来源或明确推断；推断单独标注。
- “已经读取主要文件，可以声称完整覆盖” → 列出读取、跳过、无法读取的文件和边界。
- “旧项目节点可以直接复用” → 先列至少一个当前语境差异；没有差异分析就不复用结论。
- “图更完整比证据指针更重要” → 无来源节点保留为开放问题，不补造证据。

## 证据内核（可选）

默认不启用。用户要求留证据台账或 `--rigor` 时，按同级 [调用合同](../jvc-research-core/references/caller-contract.md) 以 `jvc-knowledge-tree-builder` 身份登记，把 source_manifest 来源映射进统一账本，并用 `--mode deliver` 审查（用户要求严格审查时用 `--mode gate`）。

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
- For VC work, keep investment conclusions separate; route comps and market sizing to `jvc-workbook`, investment theses to `jvc-thesis-test`, and IC memos to `jvc-ic-memo`.

## Reference Map

- `references/output-contract.md` — artifact schemas and validation checklist.
- `scripts/collect_sources.py` — deterministic source inventory and readable-text sampler.
