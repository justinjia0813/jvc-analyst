# Output Quality Scorecard

日期：2026-07-20

证据类型：deterministic fixture evidence（确定性样例证据）。这不是 model-executed evidence（模型运行证据），也没有 baseline vs with-skill delta（基线输出与使用 skill 输出之间的差值）。

## 缩写说明

| 缩写 | 英文全称 | 中文全称 | 含义 |
| --- | --- | --- | --- |
| Eval | Evaluation | 评估 | 用样例和断言检查输出契约 |
| DOCX | Office Open XML Word Document | Word 文档格式 | `jvc-meeting-notes` 和 `jvc-talk-notes` 的输出格式 |
| PDF | Portable Document Format | 便携式文档格式 | 发票、deck 和归档票据的常见格式 |
| OCR | Optical Character Recognition | 光学字符识别 | 从 PDF 发票中提取文字 |
| TAM | Total Addressable Market | 总可触达市场 | 最大理论市场空间 |
| SAM | Serviceable Available Market | 可服务市场 | 当前产品和地域约束下可服务的市场 |
| SOM | Serviceable Obtainable Market | 可获得市场 | 一定时间内可实际获取的市场份额 |
| MOIC | Multiple on Invested Capital | 投资资本倍数 | 投资回款与投入资本的倍数 |
| IRR | Internal Rate of Return | 内部收益率 | 按时间折现后的年化回报率 |

## 结果

| 项目 | 当前状态 |
| --- | --- |
| Output cases | 11 |
| Artifact families | Markdown, Excel, DOCX, Excel + PDF archive |
| Verification command | `python3 scripts/check-skill-evals.py` |
| Latest local result | pass |

## 覆盖范围

| Case | Skill | Artifact family | Main assertions |
| --- | --- | --- | --- |
| `prescreen-markdown-contract` | `jvc-prescreen` | Markdown | 必要章节、来源/缺口标签、禁止投资结论 |
| `track-research-markdown-contract` | `jvc-track-research` | Markdown | 生命周期权重、四性假设、周期位置、因果链、反证与来源痕迹 |
| `bull-case-markdown-contract` | `jvc-bull-case` | Markdown | 标题级亮点、正文级亮点、待验证亮点、禁止投资结论 |
| `bear-case-four-role-contract` | `jvc-bear-case` | Markdown | 四角色、`IC boss`、IP/TAM/SAM 风险 |
| `ic-memo-markdown-contract` | `jvc-ic-memo` | Markdown | 交易摘要、投资逻辑、风险与反方观点、禁止投资结论 |
| `comps-dd-workbook-contract` | `jvc-comps-dd` | Excel | 文件名规则、workbook sheets |
| `market-sizing-workbook-contract` | `jvc-market-sizing` | Excel | 文件名规则、TAM/SAM/SOM workbook sheets |
| `roi-modeler-workbook-contract` | `jvc-roi-modeler` | Excel | 文件名规则、MOIC/IRR workbook sheets |
| `meeting-notes-docx-contract` | `jvc-meeting-notes` | DOCX | 生成脚本、模板、命名、版式保护 |
| `talk-notes-docx-contract` | `jvc-talk-notes` | DOCX | 完整回答、事实层维度、待验证点、Q&A 结构 |
| `invoice-manager-operational-boundary` | `jvc-invoice-manager` | Excel + PDF archive | 人工确认、只复制 PDF、运营边界 |

## Remaining Gaps

- 还没有脱敏真实输入文件作为 file-backed fixture。
- 还没有 baseline output 和 with-skill output 对比。
- 还没有 blind A/B review pack 或人工 adjudication。
- 当前 scorecard 只证明第一版输出契约断言可运行、可回归。
