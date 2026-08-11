# Skill Registry

这里记录 `jvc-analyst` 已收录的 skills。

`meeting-notes` 和 `invoice-manager` 的原始实现已经并入本仓库。来源只保留为本地组件名，当前实现和安装入口以本仓库为准。

叙事研究默认使用 Markdown，公式模型默认使用 CSV（Comma-Separated Values，逗号分隔值，一种纯文本表格格式）。Market Sizing 的 P1（Priority 1，优先级 1，表示第一迁移优先项）已迁移到 CSV；Comps/DD（Comparable Companies Analysis / Due Diligence，可比公司分析/尽职调查，用于系统核验竞争与可比对象）的 P2（Priority 2，优先级 2，表示第二迁移优先项）已迁移到 Markdown，主产物为 `03-comps-dd.md`。Word 纪要与发票归档继续作为办公/业务工具例外。

| 分类 | Skill | 事实来源 | 本地入口 | 工具集角色 | 触发位置 |
| --- | --- | --- | --- | --- | --- |
| 控制与引擎 | `jvc-deal-flow` | 本仓库 | `skills/jvc-deal-flow/SKILL.md` | 唯一项目总控：维护身份、状态、依赖、最小调度、增量重跑与人工闸门；不解析或重算专业研究。 | `/jvc-deal-flow` |
| 控制与引擎 | `jvc-research-core` | 本仓库 | `skills/jvc-research-core/SKILL.md` | 不可直接调用的证据引擎：维护追加式证据台账、主张继承，并对研究产物执行确定性审查；不推进业务阶段。 | 不可直接调用；只由已接入的研究 Skill 使用。 |
| 赛道级 | `jvc-track-research` | 本仓库 | `skills/jvc-track-research/SKILL.md` | 快速构建产业知识图谱，梳理行业简史、技术路线、产业趋势和关键玩家；活跃产物固定为 `tracks/{track-slug}/landscape.md`。 | `/jvc-track-research` |
| 赛道级 | `jvc-knowledge-tree-builder` | 本仓库 | `skills/jvc-knowledge-tree-builder/SKILL.md` | 将已有本地赛道或 Obsidian 文件夹整理成 visual-first（视觉优先，先用图和树展示结构）的固定五文件知识包：`knowledge_tree.md`、`knowledge_graph.mmd`、`nodes.json`、`evidence_index.md`、`open_questions.md`；validator 和 package check 必须通过。 | `/jvc-knowledge-tree-builder` |
| 赛道级 | `jvc-market-sizing` | 本仓库 | `skills/jvc-market-sizing/SKILL.md` | 针对细分赛道做市场规模建模；唯一活跃模型为固定单表 `market-sizing.csv`，validator 和 package check 必须通过。 | `/jvc-market-sizing` |
| 项目级 | `jvc-prescreen` | 本仓库 | `skills/jvc-prescreen/SKILL.md` | Research Level 0（L0，研究级别 0，指约 30–60 分钟的资源筛选）快筛商业模式、上下游、赛道有效性、Top-down 市场、五年收入和交易回报；固定输出 `01-prescreen.md`，只作研究资源判断，非最终投决。 | `/jvc-prescreen` |
| 项目级 | `jvc-bull-case` | 本仓库 | `skills/jvc-bull-case/SKILL.md` | 从行业趋势、技术节点、团队优势、商业化进展四个层面提炼投资亮点。 | `/jvc-bull-case` |
| 项目级 | `jvc-bear-case` | 本仓库 | `skills/jvc-bear-case/SKILL.md` | 从挑剔有限合伙人、竞品公司负责人、怀疑论同行、投资决策委员会负责人四个视角提炼反方论证和可证伪风险假设。 | `/jvc-bear-case` |
| 项目级 | `jvc-comps-dd` | 本仓库 | `skills/jvc-comps-dd/SKILL.md` | 调研竞争对手、可比公司、上下游和海外标杆；唯一活跃主产物为 Markdown 文件 `03-comps-dd.md`，保留来源、覆盖缺口与反向检索。 | `/jvc-comps-dd` |
| 项目级 | `jvc-meeting-notes` | 本仓库，整合自 `meeting-notes` | `skills/jvc-meeting-notes/SKILL.md` | 把逐字稿和用户笔记整理成结构化 `.docx` 访谈纪要。 | `/jvc-meeting-notes` |
| 项目级 | `jvc-talk-notes` | 本仓库 | `skills/jvc-talk-notes/SKILL.md` | 把高管访谈、客户访谈和专家访谈整理成问答式 `.docx` 纪要。 | `/jvc-talk-notes` |
| 项目级 | `jvc-roi-modeler` | 本仓库 | `skills/jvc-roi-modeler/SKILL.md` | 根据五年财务预测、融资稀释和退出情形计算投资回报，输出公式可审计的单表 CSV。 | `/jvc-roi-modeler` |
| 输出级 | `jvc-ic-memo` | 本仓库 | `skills/jvc-ic-memo/SKILL.md` | 先生成含引用、证据状态、冲突和质量报告的 `06-ic-memo-review.md` 预审版；用户明确预审通过后，再生成不含审查痕迹、供 IC（Investment Committee，投资决策委员会，负责审议投资项目）阅读和 Quarto 渲染的干净 Markdown 终版 `06-ic-memo.md`。 | `/jvc-ic-memo` |
| 输出级 | `jvc-research-report` | 本仓库 | `skills/jvc-research-report/SKILL.md` | 先组装：把已审计的赛道级上游（Track Research、Knowledge Tree、Market Sizing、可选 Comps/DD）重组为 canonical `research-report.md`，保留来源标识、继承上游主张、暴露覆盖缺口、不新增事实；再发布：校验固定章节与本地资源后渲染为 `report.pdf`、`report.html` 和 `build-report.txt`。 | `/jvc-research-report` |
| 日常工具 | `jvc-invoice-manager` | 本仓库，整合自 `invoice-manager` | `skills/jvc-invoice-manager/SKILL.md` | OCR（Optical Character Recognition，光学字符识别，用于从发票图片提取文字）处理差旅发票，生成报销汇总 Excel，并按行程/项目归档 PDF（Portable Document Format，可移植文档格式，用于固定版式发票归档）。 | `/jvc-invoice-manager` |

其中，`jvc-research-core` 是隐藏支持组件，不提供 slash command；其分类与职责以上方“控制与引擎”主表为准。

## 接入规则

- 原始材料保持本地存放。不要把 BP、逐字稿、财务文件、创始人沟通记录上传到第三方网页工具。
- `jvc-meeting-notes` 和 `jvc-talk-notes` 的输出视为事实层材料。任何解读、不确定性、回避回答、尽调缺口，都写入对应项目 Markdown 文件。
- `jvc-invoice-manager` 只作为运营基础设施。它可以在归档命名中引用项目 slug，但不参与投资判断。
- 新增 skill 必须使用 `jvc-` 前缀，并通过 `setup` 注册。
