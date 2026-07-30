---
name: jvc-knowledge-tree-builder
description: |
  知识树构建器：读取本地 VC 赛道/项目/Obsidian 文件夹，将其中的文件转化为递归问题树、Mermaid 知识图谱、证据索引、开放问题清单和可复用节点。用于沉淀已有研究资料，不作为首次网页调研工具。
  Use when user says '/jvc-knowledge-tree-builder', '知识树', 'knowledge tree', '构建知识图谱', '整理研究资料', or asks to read a local VC track, project, Obsidian, or source folder and convert existing files into a recursive question tree, Mermaid graph, evidence index, open-question list, and reusable nodes. Do not use for first-pass web research, one-off summaries, translation, or UI-only mind-map drawing.
user_invocable: true
version: "3.0.0"
---

# /jvc-knowledge-tree-builder — JVC Knowledge Tree Builder

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

## 证据内核（必须）

从本 `SKILL.md` 的实际目录解析同级 `../jvc-research-core/scripts/researchctl.py`，并使用绝对路径执行；不要依赖当前工作目录。

执行前必须读取同级 `../jvc-research-core/references/evidence-contract.md` 和当前 profile `../jvc-research-core/profiles/jvc-knowledge-tree-builder.json`。

1. 新研究先准备完整 `scope` JSON，再运行 `init --skill jvc-knowledge-tree-builder --run-dir <研究目录> --scope-file <scope.json>`；初始 `scope` 只能通过 `init --scope-file` 创建。
2. 复用已有研究链时运行 `init --skill jvc-knowledge-tree-builder --run-dir <研究目录> --resume`。后续 `scope` 更正必须通过 `record --run-dir <研究目录> --input <records.jsonl>` 登记，并用 `supersedes` 指向当前 effective scope；问题、检索、来源、主张和更正也只能通过该命令登记，不得直接编辑 `evidence_registry.jsonl`，generic `record` 不得创建 waiver。
3. 跨 skill 消费已有主张时，在新主张的 `derived_from_claim_ids` 中登记上游主张编号；缺失或失效的上游审计会阻断下游完成。
4. 最终产物中的本阶段支持与反证来源统一写为 `[S编号]`；Markdown 写在对应主张后，工作簿写入 `sources` 表，DOCX 写入来源附注，多文件产物至少在 `evidence_index.md` 建立映射。
5. 完成现有产物生成与格式校验后，运行 `audit --run-dir <研究目录> --skill jvc-knowledge-tree-builder --artifact <最终产物>`；多文件产物重复传入 `--artifact`。每次 audit 必须同时读取命令退出状态和 `audit.json`。
6. 只有 status 为 `blocked`、findings 中唯一 block 是 `partial_label_missing`，且至少一个 finding 为 `partial` 时，才按产物补写 `研究状态：partial`：Markdown 写入标题与结论，XLSX 在 `sources` 表表头和列结构不变的前提下追加一条可见状态数据行，DOCX 写入首段与来源附注，多文件产物至少写入 `knowledge_tree.md` 与 `evidence_index.md`；任何类型写回标签后，必须先重新运行原有产物格式校验/validator，确认结构仍有效，再重跑 audit；存在其他 block 时不得用标签绕过。重跑得到 `partial` / exit `10` 才可 partial 交付；`ready` / exit `0` 才能称为完成；其他 `blocked` / exit `20` 只能交付证据缺口和下一步，不能形成受影响的判断；exit `1` 必须修复后重跑。
7. 只有用户明确批准、且 blocker 与同 skill 最新有效 blocked audit 精确匹配时，才可运行 `waive --run-dir <研究目录> --skill jvc-knowledge-tree-builder --rule <阻断规则> --reason <批准理由> --scope <批准范围> --approved-by <批准人> --residual-risk <剩余风险>`；不得自我批准，waiver 最多降级为 partial。

找不到内核、profile 不兼容、账本损坏或终审异常时，不得退回纯 prompt 模式。

本 skill 把 source_manifest 来源映射进统一账本，并保持知识树节点与来源编号一致。

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
