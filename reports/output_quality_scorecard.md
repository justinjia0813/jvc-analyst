# Output Quality Scorecard

日期：2026-08-09

结论：16 个确定性输出契约全部通过；`jvc-deal-flow` 另通过临时项目库的端到端状态机自检。P1/P2 迁移后，叙事研究默认 Markdown、公式模型默认 CSV：Comps/DD 唯一活跃主产物为 `03-comps-dd.md`，Market Sizing 与 ROI Modeler 唯一活跃主产物为 CSV；Word 纪要与发票 Excel+PDF 归档作为明确例外保留。Research Report 采用“组装 + 发布”两阶段，canonical `research-report.md` 由 `validate_assembly.py` 做来源/数字/标签继承校验后渲染为 PDF/HTML。旧工作簿时代的输出评测与人工盲审产物已归档：顶层 11 份历史报告原件保留（与 HEAD 逐字节一致），带 `historical-legacy-workbook` 状态副本归档于 `reports/legacy/`，两者均不得作为新 CSV 合同通过的证据。

## 缩写说明

| 缩写 | 英文全称 | 中文全称 | 含义 |
| --- | --- | --- | --- |
| Eval | Evaluation | 评估 | 用样例和断言检查输出契约 |
| CSV | Comma-Separated Values | 逗号分隔值 | 保存公式模型和来源表的纯文本表格格式 |
| DOCX | Office Open XML Word Document | Word 文档格式 | `jvc-meeting-notes` 和 `jvc-talk-notes` 的输出格式 |
| PDF | Portable Document Format | 便携式文档格式 | 固定版式报告和发票归档格式 |
| HTML | HyperText Markup Language | 超文本标记语言 | 浏览器预览使用的页面结构格式 |
| URI | Uniform Resource Identifier | 统一资源标识符 | 标识资源位置或内嵌数据的字符串；本报告中的 `data:` URI 用于内嵌本地资源 |
| JSON | JavaScript Object Notation | JavaScript 对象表示法 | 保存机器可读结构化数据的文本格式 |
| PNG | Portable Network Graphics | 便携式网络图形 | 无损位图图像格式，用于知识树与研报的逐页页面图 |
| MOIC | Multiple on Invested Capital | 投资资本倍数 | 投资回款与投入资本的倍数 |
| IRR | Internal Rate of Return | 内部收益率 | 按时间折现后的年化回报率 |

## 结果

| 项目 | 当前状态 |
| --- | --- |
| Deterministic output cases | 16 / 16 pass |
| Artifact families | Project state、Markdown、CSV、DOCX、Excel + PDF invoice archive、Research PDF + HTML、evidence ledger + audit |
| Research Core real-path cases | 4 `ready` + 1 expected `blocked`（exit 20） |
| Research Report canonical 组装示例 | `examples/research-report-example/research-report.md` 通过 `validate_assembly.py` 继承校验 |
| Research Report 渲染 | A4 14 页 PDF + HTML + 逐页页面图（`reports/task9-visual/research-report-page-01.png` … `page-14.png`） |
| Knowledge Tree 渲染 | A4 1 页 PDF + 逐页页面图（`reports/task9-visual/knowledge-tree.pdf` + `knowledge-tree-page-01.png`） |
| Task 9 视觉门禁产物 | `reports/task9-visual/`：知识树 PDF+逐页 PNG、研报 PDF+逐页 PNG、机械生成记录；主 Agent 已于 2026-08-10 用 `view_image` 逐页目检通过（见 `reports/task9-visual/MAIN-VISUAL-INSPECTION.md`） |
| Knowledge Tree 五文件包示例 | `examples/knowledge-tree-example/` 通过 `validate_output.py` 与包级自检 |
| Historical legacy workbooks | 顶层 11 份原件保留（与 HEAD 一致）；带状态副本归档于 `reports/legacy/`；两者均不作为新合同证明 |
| Verification command | `python3 scripts/check-skill-evals.py` |

## 16 个确定性输出契约

| Case | Skill | Artifact family |
| --- | --- | --- |
| `deal-flow-state-contract` | `jvc-deal-flow` | append-only events + derived project state |
| `prescreen-supported-markdown-contract` | `jvc-prescreen` | Markdown |
| `prescreen-missing-data-markdown-contract` | `jvc-prescreen` | Markdown |
| `track-research-markdown-contract` | `jvc-track-research` | Markdown |
| `knowledge-tree-builder-artifact-contract` | `jvc-knowledge-tree-builder` | Markdown + Mermaid + JSON |
| `bull-case-markdown-contract` | `jvc-bull-case` | Markdown |
| `bear-case-four-role-contract` | `jvc-bear-case` | Markdown |
| `ic-memo-markdown-contract` | `jvc-ic-memo` | Markdown |
| `comps-dd-markdown-contract` | `jvc-comps-dd` | Markdown |
| `market-sizing-csv-contract` | `jvc-market-sizing` | CSV |
| `roi-modeler-csv-contract` | `jvc-roi-modeler` | CSV |
| `meeting-notes-docx-contract` | `jvc-meeting-notes` | DOCX |
| `talk-notes-docx-contract` | `jvc-talk-notes` | DOCX |
| `invoice-manager-operational-boundary` | `jvc-invoice-manager` | Excel + PDF archive（业务工具例外） |
| `research-core-audit-contract` | hidden `jvc-research-core` | evidence ledger + deterministic audit |
| `research-report-pdf-contract` | `jvc-research-report` | canonical Markdown + Research PDF + HTML |

## 真实案例与对照证据

| Case | 实际结果 | 关键证据 |
| --- | --- | --- |
| `local-interview-to-prescreen` | `ready` | 受访者自述与用户观察分离；DOCX 与初筛产物均绑定审计 |
| `glass-substrate-conflicting-public-sources` | `ready` | 保留同源时间序列张力、工程反证与量产证据缺口 |
| `market-model-fact-vs-assumption` | `ready` | 外部事实、用户假设、模型估算与冲突市场口径分离；baseline/candidate/run 均为 `market-sizing.csv` 单表 |
| `audited-chain-to-ic-memo` | `ready` | 前序审计按文件指纹复核；bull/bear/memo 依赖链有效 |
| `missing-critical-commercial-proof` | `blocked`，exit 20 | 公司规模收入主张无独立商业证据，未升级为事实或伪装为 ready |

## Research Report 两阶段证据

- 组装阶段：`examples/research-report-example/research-report.md` 从 `track-research-example.md`、`knowledge-tree-example/`、`market-sizing-example.csv`、`comps-dd-example.md` 组装；`validate_assembly.py` 校验来源 ID、数字与标签继承（含 1a–1h 对抗反例）。
- 发布阶段：canonical 渲染为 A4 14 页 PDF、HTML 预览与构建日志，页面图位于 `reports/task9-visual/research-report-page-01.png` … `page-14.png`；机械校验（章节/书签/关键数字/SVG 内嵌/callout）通过。
- 视觉检查：主 Agent 已于 2026-08-10 用 `view_image` 逐页目检知识树 1 页与研报 14 页，无裁切、缺字、丢标签或跨页不一致；第 7 页图与图注、第 13 页缺口表、第 14 页七列来源表通过（记录：`reports/task9-visual/MAIN-VISUAL-INSPECTION.md`）。这是视觉检查，不代替 `validate_assembly.py` 等机械校验。

## Historical Legacy Workbooks

- 旧 2 基线/候选案例（`research-core-output-eval.*`）与 n=2 人工盲审产物（`output_blind_review_pack.*`、`output_blind_answer_key.json`、`output_review_kit.*`、`output_review_adjudication.*`、`output_review_decisions.json`）基于 CSV 迁移前的工作簿时代输出，无法从新 CSV 案例确定再生（再生会伪造人工判断）。
- **处置事实**：顶层 `reports/` 下 11 份历史报告原件保留、未删除/移动/改写（与 HEAD 逐字节一致）；带 `historical-legacy-workbook` 状态块/横幅的副本归档于 `reports/legacy/`（含 `STATUS.md` 单一索引）。
- **边界**：原件与归档副本均不得引用为“新 CSV 合同通过”的证据；新合同证据以上表 16 个契约、Research Core 5 个真实路径案例和两阶段渲染证据为准。

## Evidence Boundary

- Fixture evidence（样例证据）：16 个静态输出契约证明结构、信号与审计规则可重复检查；deal-flow 另有临时项目库状态机自检，report fixture 还验证本地资源防护和事务式三产物。
- File-backed rendering evidence（文件支撑渲染证据）：`jvc-research-report` 的虚构 canonical 样例实际生成 A4 14 页 PDF；文本提取与页面渲染通过，逐页视觉检查已由主 Agent 于 2026-08-10 完成（记录：`reports/task9-visual/MAIN-VISUAL-INSPECTION.md`）。这不是模型执行或盲审证据。
