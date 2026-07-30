# jvc-analyst Skill Case Quality Review

日期：2026-07-30
案例固定日期：2026-07-29

结论：13 个用户 skill 与 hidden `jvc-research-core` 的 14 个确定性输出契约均通过；14 个 trigger fixtures（触发样例）包含 13 个用户路由和 1 个 no-route（不路由）案例，hidden core 无路由。5 个 core 真实路径案例得到 4 `ready` 与 1 个预期 `blocked`（exit 20）。2 个基线/候选案例的确定性证据质量从 64.09% 提升到 100.00%，但 Justin 的人工盲审为一胜一负，因此 2.0 的人工证据只是 partial support（部分支持）。`jvc-research-report` 另有虚构样例的 A4 13 页本地渲染和逐页视觉检查。

## 缩写与格式说明

- DOCX：Office Open XML Word Document（Word 文档格式），用于保存可编辑的结构化访谈纪要。
- JSON：JavaScript Object Notation（JavaScript 对象表示法），用于保存机器可读的结构化数据。
- PDF：Portable Document Format（便携式文档格式），用于保持跨设备一致的票据版式。
- HVM：High-Volume Manufacturing（大批量制造），指稳定、可重复且具有商业规模的生产状态。
- IC：Investment Committee（投资委员会），指审议投资决策的内部机制。

## 证据层

| 层 | 本次证据 | 能证明 | 不能证明 |
| --- | --- | --- | --- |
| Fixture evidence（样例证据） | 14 trigger + 14 output contracts | 路由边界、源码信号、结构与审计规则可回归 | 真实模型路由准确率 |
| Model/tool execution evidence（模型/工具执行证据） | 5 个文件支持的真实路径案例；公开来源于 2026-07-29 实际打开 | 本地命令、文件产物、记录、审计、阻断路径能端到端工作 | 跨平台、大样本模型质量 |
| Human review（人工审阅） | Justin，2026-07-30，n=2，已声明先判断后查看密钥 | 一个案例的实用性偏好和一个案例的格式偏好 | 统计显著性或 2-0 人工一致胜出 |

## Suite Overview

| Skill | 用户可调用 | 主要产物 | 本次最强证据 | 当前判断 |
| --- | --- | --- | --- | --- |
| `jvc-prescreen` | 是 | Markdown | 脱敏访谈→初筛 `ready`，依赖前序 DOCX 审计 | strong |
| `jvc-bull-case` | 是 | Markdown | bull→bear→memo 链中独立审计有效 | strong |
| `jvc-bear-case` | 是 | Markdown | 反证保留且风险篇幅不被压缩 | strong |
| `jvc-ic-memo` | 是 | Markdown | 复用三个上游 ready 产物，最终指纹稳定 | strong |
| `jvc-track-research` | 是 | Markdown | 玻璃公开研究 `ready`；缺商业证据案例正确 `blocked` | strongest |
| `jvc-knowledge-tree-builder` | 是 | Markdown + Mermaid + JSON | 确定性 artifact contract | moderate |
| `jvc-comps-dd` | 是 | Excel | 确定性 workbook contract | moderate/weak |
| `jvc-market-sizing` | 是 | Excel | 真实六表模型 `ready`；2.0 证据断言 100% | strong，呈现待改进 |
| `jvc-roi-modeler` | 是 | Excel | 确定性 workbook contract | moderate/weak |
| `jvc-meeting-notes` | 是 | DOCX | 脱敏访谈 DOCX 版式与文件名实测通过 | strong |
| `jvc-talk-notes` | 是 | DOCX | 确定性问答纪要 contract | moderate |
| `jvc-invoice-manager` | 是 | Excel + PDF archive | 运营边界 contract；明确排除研究内核 | boundary-only |
| `jvc-research-report` | 是 | PDF + HTML + build log | 虚构样例实测 A4 13 页；文本、13/13 页渲染与逐页视觉检查通过 | strong renderer evidence |
| `jvc-research-core` | 否 | ledger + audit | 5 个真实案例、无 waiver、阻断 exit 20、安装/回滚自检 | strongest infrastructure |

## Five Acceptance Cases

| Case | Skill chain | Expected | Actual | 判断 |
| --- | --- | --- | --- | --- |
| `local-interview-to-prescreen` | meeting-notes → prescreen | ready | ready，exit 0 | 自述与用户观察分离，初筛可追溯 |
| `glass-substrate-conflicting-public-sources` | track-research | ready | ready，exit 0 | 同源不重复计数，保留工程反证和 HVM 缺口 |
| `market-model-fact-vs-assumption` | market-sizing | ready | ready，exit 0 | 事实/假设/估算分离，冲突口径不合并 |
| `audited-chain-to-ic-memo` | bull → bear → IC memo | ready | ready，exit 0 | 前序指纹与审计依赖仍有效 |
| `missing-critical-commercial-proof` | track-research | blocked | blocked，exit 20 | 未验证公司主张没有升级为事实 |

## Baseline/Candidate and Blind Review

六项确定性维度为 factual accuracy（事实准确性）、traceability（可追溯性）、source independence（来源独立性）、counterevidence（反证）、calibration（结论校准）与 next-step usefulness（下一步可用性）。

| Case | 1.0 | 2.0 | Delta | Human decision |
| --- | ---: | ---: | ---: | --- |
| 玻璃基板 | 68.18% | 100.00% | +31.82 | B=2.0，0.7，“实用性更好” |
| 市场模型 | 60.00% | 100.00% | +40.00 | B=1.0，0.3，“格式处理更胜一筹” |
| 合计 | 64.09% | 100.00% | +35.91 | 1 match / 1 disagree |

不得把这个结果写成 2-0。市场理由属于格式/呈现实用性偏好，不是六项证据质量正向支持；它仍是需要保留的产品可用性分歧。

## Strongest and Weakest Outputs

- strongest：`jvc-track-research` + core。它既让冲突公开来源案例通过，也让缺关键商业证据的案例以 exit 20 失败关闭。
- strongest：审计链到 `jvc-ic-memo`。后续 ledger 追加没有使前序有效审计失真，最终产物按指纹绑定。
- strong renderer：`jvc-research-report`。本地资源防护、事务式三产物和 A4 13 页逐页检查通过，但证据仍是虚构样例自检。
- weakest：`jvc-comps-dd` 与 `jvc-roi-modeler`。本轮仍只有确定性 contract，没有代表性的 populated workbook 真实案例。
- weakest signal：市场模型的 2.0 证据结构通过全部断言，但人工低置信度偏好 1.0 格式，说明可读性与审阅效率尚未充分证明。
- boundary-only：`jvc-invoice-manager` 只证明运营边界；本次不执行真实发票识别或归档。

## Remaining Gaps

- 只有 1 名人工审阅者、2 个盲审案例。
- 未运行模型实际路由保留集、对抗路由或 Codex 之外的平台。
- 未运行分发适配器权限 probe（探针，一种验证运行时权限行为的小型检查）。
- `jvc-comps-dd`、`jvc-roi-modeler` 缺带真实行和公式的 acceptance case。
- 发票依赖、真实光学字符识别和运营数据明确排除在研究 2.0 验收之外。
