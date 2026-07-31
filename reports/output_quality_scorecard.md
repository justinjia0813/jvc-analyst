# Output Quality Scorecard

日期：2026-07-31

结论：15 个确定性输出契约全部通过；`jvc-deal-flow` 另通过临时项目库的端到端状态机自检。2 个同输入基线/候选案例中，1.0 基线通过率为 64.09%，2.0 候选为 100.00%，提升 35.91 个百分点且无回退。人工盲审只构成部分支持：玻璃基板案例选择 2.0，市场模型案例低置信度选择 1.0 的格式呈现。`jvc-research-report` 另有文件支撑的 13 页本地渲染与逐页视觉检查。

## 缩写说明

| 缩写 | 英文全称 | 中文全称 | 含义 |
| --- | --- | --- | --- |
| Eval | Evaluation | 评估 | 用样例和断言检查输出契约 |
| DOCX | Office Open XML Word Document | Word 文档格式 | `jvc-meeting-notes` 和 `jvc-talk-notes` 的输出格式 |
| PDF | Portable Document Format | 便携式文档格式 | 固定版式报告和发票归档格式 |
| HTML | HyperText Markup Language | 超文本标记语言 | 浏览器预览使用的页面结构格式 |
| URI | Uniform Resource Identifier | 统一资源标识符 | 标识资源位置或内嵌数据的字符串；本报告中的 `data:` URI 用于内嵌本地资源 |
| JSON | JavaScript Object Notation | JavaScript 对象表示法 | 保存机器可读结构化数据的文本格式 |
| A/B | A/B Test | A/B 对照测试 | 隐藏来源后比较两个版本的评审方法 |
| OCR | Optical Character Recognition | 光学字符识别 | 从 PDF 发票中提取文字 |
| TAM | Total Addressable Market | 总可触达市场 | 最大理论市场空间 |
| SAM | Serviceable Available Market | 可服务市场 | 当前产品和地域约束下可服务的市场 |
| SOM | Serviceable Obtainable Market | 可获得市场 | 一定时间内可实际获取的市场份额 |
| MOIC | Multiple on Invested Capital | 投资资本倍数 | 投资回款与投入资本的倍数 |
| IRR | Internal Rate of Return | 内部收益率 | 按时间折现后的年化回报率 |

## 结果

| 项目 | 当前状态 |
| --- | --- |
| Deterministic output cases | 15 / 15 pass |
| Artifact families | Project state、Markdown、Excel、DOCX、Excel + PDF archive、Research PDF + HTML、evidence ledger + audit |
| File-backed baseline/candidate cases | 2 |
| Baseline pass rate | 64.09% |
| 2.0 candidate pass rate | 100.00% |
| Delta | +35.91 个百分点 |
| Candidate regressions | 0 |
| Real acceptance cases | 4 `ready` + 1 expected `blocked`（exit 20） |
| Blind human review | 1 match + 1 disagree；agreement rate 50%，n=2 |
| Verification command | `python3 scripts/check-skill-evals.py` |

## 15 个确定性输出契约

| Case | Skill | Artifact family |
| --- | --- | --- |
| `deal-flow-state-contract` | `jvc-deal-flow` | append-only events + derived project state |
| `prescreen-markdown-contract` | `jvc-prescreen` | Markdown |
| `track-research-markdown-contract` | `jvc-track-research` | Markdown |
| `research-report-pdf-contract` | `jvc-research-report` | Research PDF + HTML |
| `knowledge-tree-builder-artifact-contract` | `jvc-knowledge-tree-builder` | Markdown + Mermaid + JSON |
| `bull-case-markdown-contract` | `jvc-bull-case` | Markdown |
| `bear-case-four-role-contract` | `jvc-bear-case` | Markdown |
| `ic-memo-markdown-contract` | `jvc-ic-memo` | Markdown |
| `comps-dd-workbook-contract` | `jvc-comps-dd` | Excel |
| `market-sizing-workbook-contract` | `jvc-market-sizing` | Excel |
| `roi-modeler-workbook-contract` | `jvc-roi-modeler` | Excel |
| `meeting-notes-docx-contract` | `jvc-meeting-notes` | DOCX |
| `talk-notes-docx-contract` | `jvc-talk-notes` | DOCX |
| `invoice-manager-operational-boundary` | `jvc-invoice-manager` | Excel + PDF archive |
| `research-core-audit-contract` | hidden `jvc-research-core` | evidence ledger + deterministic audit |

## 真实案例与对照证据

| Case | 实际结果 | 关键证据 |
| --- | --- | --- |
| `local-interview-to-prescreen` | `ready` | 受访者自述与用户观察分离；DOCX 与初筛产物均绑定审计 |
| `glass-substrate-conflicting-public-sources` | `ready` | 保留同源时间序列张力、工程反证与量产证据缺口 |
| `market-model-fact-vs-assumption` | `ready` | 外部事实、用户假设、模型估算与冲突市场口径分离 |
| `audited-chain-to-ic-memo` | `ready` | 前序审计按文件指纹复核；bull/bear/memo 依赖链有效 |
| `missing-critical-commercial-proof` | `blocked`，exit 20 | 公司规模收入主张无独立商业证据，未升级为事实或伪装为 ready |

| Blind case | 确定性结果 | Justin 的盲审决定 |
| --- | --- | --- |
| 玻璃基板 | 2.0：100%，1.0：68.18%，delta +31.82 | 选 B=2.0，置信度 0.7；理由原文：“实用性更好” |
| 市场模型 | 2.0：100%，1.0：60%，delta +40.00 | 选 B=1.0，置信度 0.3；理由原文：“格式处理更胜一筹” |

人工盲审不是 2-0。市场案例的理由反映 presentation usability（呈现实用性）或格式偏好，不是六项 evidence-quality（证据质量）断言的正向证据。

## Evidence Boundary

- Fixture evidence（样例证据）：15 个静态输出契约证明结构、信号与审计规则可重复检查；deal-flow 另有临时项目库状态机自检，report fixture 还验证本地资源防护和事务式三产物。
- File-backed rendering evidence（文件支撑渲染证据）：`jvc-research-report` 的虚构样例实际生成 A4 13 页 PDF；文本提取、13/13 页渲染和逐页视觉检查通过。这不是模型执行或盲审证据。
- Model/tool execution evidence（模型/工具执行证据）：5 个真实路径案例证明本地脚本、文件产物、来源记录和审计状态能端到端工作；这不是大样本模型质量或跨平台路由统计。
- Human review（人工审阅）：仅 1 名审阅者、2 个案例；一胜一负，只能视为部分支持。

## Remaining Gaps

- 未运行 Codex 之外的平台适配器或权限探针。
- 没有 model-executed route holdout（模型实际路由保留集）或 adversarial holdout（对抗性保留集）。
- `jvc-comps-dd`、`jvc-roi-modeler` 仍缺带公式和真实行数据的代表性工作簿案例。
- 人工盲审样本量 n=2，市场模型显示格式可读性仍可能压过证据结构优势。
- 发票流程未纳入研究内核；真实光学字符识别和报销流程不属于本次发布证据。
