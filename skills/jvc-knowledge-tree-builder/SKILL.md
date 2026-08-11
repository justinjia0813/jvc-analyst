---
name: jvc-knowledge-tree-builder
description: |
  知识树构建器：读取本地投资赛道、项目或 Obsidian 文件夹，将其中的文件转化为递归问题树、Mermaid 知识图谱、证据索引、开放问题清单和可复用节点。用于沉淀已有研究资料，不作为首次网页调研工具。
  Use when user says '/jvc-knowledge-tree-builder', '知识树', 'knowledge tree', '构建知识图谱', '整理研究资料', or asks to read a local investment track, project, Obsidian, or source folder and convert existing files into a recursive question tree, Mermaid graph, evidence index, open-question list, and reusable nodes. Do not use for first-pass web research, one-off summaries, translation, or interface-only mind-map drawing.
user_invocable: true
version: "4.0.0"
---

# /jvc-knowledge-tree-builder — JVC Knowledge Tree Builder

把 Track Research（Track Research，赛道研究：首次建立完整赛道证据与权威叙事）的 `tracks/{track-slug}/landscape.md`、Research Core（Research Core，研究证据内核：维护共享证据台账与审计状态）和用户指定本地材料转换为 visual-first（visual-first，可视化优先：让主图、图例、关键关系和开放问题先于细节呈现）的知识包。

本 Skill 不重新承担首次完整联网赛道研究。若 `landscape.md` 或共享台账缺少支撑，只登记证据缺口或请用户先运行 `/jvc-track-research`；不得为了填满图谱自行重做整轮网页研究。Pre-Screen（Pre-Screen，投资前快筛：为资源分配做快速判断）、Market Sizing（Market Sizing，市场规模测算：为模型变量补任务专项证据）与 Comparable Companies Analysis / Due Diligence（Comps/DD，可比公司分析/尽职调查：核验特定公司与项目事实）仍可在各自任务边界内做任务专项公开研究。

## 3.0 适用级别

最低适用级别：**L1+**（Level 1 or above，一级及以上初筛，用于形成可验证研究假设）。

- 若输入属于具体项目，先读取 `spec/CONTEXT.md` 与 `spec/hypotheses.md`；若属于赛道，先确认 `tracks/{track-slug}/` 的边界。
- 当前项目仍为 Research Level 0（L0，研究级别 0：约 30-60 分钟的资源筛选）时，先说明知识树会增加结构化维护成本，由用户确认是否升级或只做一次性整理。
- 本 Skill 复用已有材料，不为了填满树而新增未经验证的节点或关系。

## 反合理化约束

- “文件相邻，所以概念有关联” → 关系必须来自来源或明确推断；推断单独标注。
- “已经读取主要文件，可以声称完整覆盖” → 列出读取、跳过、无法读取的文件和边界。
- “旧项目节点可以直接复用” → 先列至少一个当前语境差异；没有差异分析就不复用结论。
- “图更完整比证据指针更重要” → 无来源节点保留为开放问题，不补造证据。

## 证据内核（必须）

从本 `SKILL.md` 的实际目录解析同级 `../jvc-research-core/scripts/researchctl.py`，并使用绝对路径执行；不要依赖当前工作目录。

执行前必须读取同级 `../jvc-research-core/references/evidence-contract.md` 和当前 profile `../jvc-research-core/profiles/jvc-knowledge-tree-builder.json`。

1. 新研究先准备完整 `scope` 结构化文件，再运行 `init --skill jvc-knowledge-tree-builder --run-dir <研究目录> --scope-file <scope.json>`；初始 `scope` 只能通过 `init --scope-file` 创建。
2. 复用已有研究链时运行 `init --skill jvc-knowledge-tree-builder --run-dir <研究目录> --resume`。后续 `scope` 更正必须通过 `record --run-dir <研究目录> --input <records.jsonl>` 登记，并用 `supersedes` 指向当前 effective scope；问题、检索、来源、主张和更正也只能通过该命令登记，不得直接编辑 `evidence_registry.jsonl`，generic `record` 不得创建 waiver。
3. 跨 skill 消费已有主张时，在新主张的 `derived_from_claim_ids` 中登记上游主张编号；缺失或失效的上游审计会阻断下游完成。
4. 最终产物中的本阶段支持与反证来源统一写为 `[S编号]`；Markdown 写在对应主张后，工作簿写入 `sources` 表，Office Open XML Document（DOCX，Office 开放 XML 文档：保存可编辑文字报告）写入来源附注，多文件产物至少在 `evidence_index.md` 建立映射。
5. 完成现有产物生成与格式校验后，运行 `audit --run-dir <研究目录> --skill jvc-knowledge-tree-builder --artifact <最终产物>`；多文件产物重复传入 `--artifact`。每次 audit 必须同时读取命令退出状态和 `audit.json`。
6. 只有 status 为 `blocked`、findings 中唯一 block 是 `partial_label_missing`，且至少一个 finding 为 `partial` 时，才按产物补写 `研究状态：partial`：Markdown 写入标题与结论，Microsoft Excel Open XML Spreadsheet（XLSX，微软 Excel 开放 XML 电子表格：保存公式模型和来源表）在 `sources` 表表头和列结构不变的前提下追加一条可见状态数据行，DOCX 写入首段与来源附注，多文件产物至少写入 `knowledge_tree.md` 与 `evidence_index.md`；任何类型写回标签后，必须先重新运行原有产物格式校验/validator，确认结构仍有效，再重跑 audit；存在其他 block 时不得用标签绕过。重跑得到 `partial` / exit `10` 才可 partial 交付；`ready` / exit `0` 才能称为完成；其他 `blocked` / exit `20` 只能交付证据缺口和下一步，不能形成受影响的判断；exit `1` 必须修复后重跑。
7. 只有用户明确批准、且 blocker 与同 skill 最新有效 blocked audit 精确匹配时，才可运行 `waive --run-dir <研究目录> --skill jvc-knowledge-tree-builder --rule <阻断规则> --reason <批准理由> --scope <批准范围> --approved-by <批准人> --residual-risk <剩余风险>`；不得自我批准，waiver 最多降级为 partial。

找不到内核、profile 不兼容、账本损坏或终审异常时，不得退回纯 prompt 模式。

本 Skill 消费共享台账中的 effective source（有效来源：未被后续记录取代且当前生效的来源），不要求为已由 Track Research 登记的来源复制一条当前 Skill source record（来源记录）。若形成新的下游主张，必须在 `derived_from_claim_ids` 中保留有效上游主张编号，不得把 Track Research 主张改写为无继承关系的新事实。

## 固定输出

恰好输出以下五个非空文件，名称不得改变：

- `knowledge_tree.md`：visual-first 主用户制品；近开头放 Mermaid 主图，并紧接图例、关键关系和开放问题概览。
- `knowledge_graph.mmd`：可复用 Mermaid 图源。
- `nodes.json`：JavaScript Object Notation（JSON，JavaScript 对象表示法：保存可机器复用的节点与关系）结构。
- `evidence_index.md`：节点、关系、来源编号与有效主张编号的映射。
- `open_questions.md`：待补研究问题、重要性和所需证据。

主图只保留影响投资理解的核心关系；分支细节进入问题树或子图，不把全部节点挤进一张不可读的大图。

## Workflow

1. 读取 `landscape.md` 的根问题、主要分支、实体与关系、来源编号、有效主张编号、Market Sizing 变量和开放问题，再读取共享台账及用户指定本地材料。
2. 范围较宽时选择最近的赛道或项目目录并报告边界；需要文件清单时可运行 `python3 scripts/collect_sources.py <path> --output <临时目录>/source_manifest.json`，但 `source_manifest.json` 只是中间清单，不进入固定五文件包。
3. 记录已读、跳过和无法读取的材料；不得用新增网页研究掩盖输入缺口。
4. 建模一个根问题、5-9 个一级分支、递归子问题和跨分支关系；父子边与 claimed relation（主张关系：表达依赖、影响、对比等可证伪判断的关系）分开。
5. 写入固定五文件，并按 `references/output-contract.md` 建立节点 / 关系到来源与有效主张的可见映射。
6. 在 Research Core audit（Research Core audit，研究内核审计：检查证据台账、继承关系与产物引用）之前运行：

```bash
python3 skills/jvc-knowledge-tree-builder/scripts/validate_output.py <知识包目录>
```

validator 非零或 Mermaid 本地渲染失败时停止，不得进入 Research Core audit。
7. validator 通过后，再把五个文件分别作为 `--artifact` 传给 Research Core audit。

## Rules

- Preserve source paths as evidence references.
- Separate source facts, inference, and unknowns.
- Every node needs a question, summary, parent, open question, and evidence pointer or explicit evidence gap.
- Expand English abbreviations on first use with English full name, Chinese full name, and a brief explanation.
- If coverage is partial, state what was read, skipped, or unreadable.
- For venture-capital work, keep investment conclusions separate; route comparable-company analysis, market sizing, bull/bear case, and investment memo to matching `jvc-*` skills.
- 上游 `landscape.md` 或有效主张实质变化时，只把受影响节点、关系和开放问题标为 stale（过期：上游变化后需要复核），不自动全量重跑。
- 执行最小更新仍须用户批准；批准前只报告影响范围和建议更新项。

## Reference Map

- `references/output-contract.md` — artifact schemas and validation checklist.
- `scripts/collect_sources.py` — deterministic source inventory and readable-text sampler.
- `scripts/validate_output.py` — standard-library structural validator for the fixed five-file package.
