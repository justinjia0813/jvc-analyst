# Route Scorecard

日期：2026-07-31

证据类型：deterministic fixture evidence（确定性样例证据）。15 个 trigger case（触发案例）全部通过完整性与 source-contract（源码契约）检查；这不是模型实际路由准确率。

## 缩写说明

| 缩写 | 英文全称 | 中文全称 | 含义 |
| --- | --- | --- | --- |
| Eval | Evaluation | 评估 | 用样例和断言检查 skill 行为是否保持稳定 |
| Q&A | Question and Answer | 问答 | `jvc-talk-notes` 的一问一答输出结构 |
| IC | Investment Committee | 投资委员会 | `jvc-ic-memo` 和 `jvc-bear-case` 面向的投决会场景 |
| TAM | Total Addressable Market | 总可触达市场 | 最大理论市场空间 |
| SAM | Serviceable Available Market | 可服务市场 | 当前产品和地域约束下可服务的市场 |
| SOM | Serviceable Obtainable Market | 可获得市场 | 一定时间内可实际获取的市场份额 |
| OCR | Optical Character Recognition | 光学字符识别 | 从 PDF 发票中识别文字 |
| PDF | Portable Document Format | 便携式文档格式 | 发票和 deck 常见文件格式 |
| HTML | HyperText Markup Language | 超文本标记语言 | 浏览器预览使用的页面结构格式 |

## 结果

| 项目 | 当前状态 |
| --- | --- |
| Trigger cases | 15 |
| User-routable skill cases | 14 |
| Near-neighbor pairs | 18 |
| No-route teaching case | 1 |
| Hidden core route | 无；`jvc-research-core` 为 `user_invocable: false`，由 12 个研究业务/编排 skill 固定调用；发票和 report renderer 保持排除 |
| Verification command | `python3 scripts/check-skill-evals.py` |
| Latest local result | pass |

## 覆盖范围

| Case | Expected route | Near-neighbor boundary |
| --- | --- | --- |
| `deal-flow-initialize-to-pre-dd-gate` | `jvc-deal-flow` | `jvc-prescreen`, `jvc-ic-memo` |
| `prescreen-deck-quick-review` | `jvc-prescreen` | `jvc-ic-memo`, `jvc-deal-flow` |
| `talk-notes-qna-transcript` | `jvc-talk-notes` | `jvc-meeting-notes` |
| `meeting-notes-six-section-founder-call` | `jvc-meeting-notes` | `jvc-talk-notes` |
| `bull-case-positive-arguments` | `jvc-bull-case` | `jvc-ic-memo` |
| `bear-case-adversarial-review` | `jvc-bear-case` | `jvc-bull-case` |
| `ic-memo-full-synthesis` | `jvc-ic-memo` | `jvc-bull-case` |
| `track-research-sector-map` | `jvc-track-research` | `jvc-comps-dd` |
| `research-report-fixed-markdown-render` | `jvc-research-report` | `jvc-track-research`, `jvc-ic-memo` |
| `knowledge-tree-builder-local-folder` | `jvc-knowledge-tree-builder` | `jvc-track-research` |
| `comps-dd-competitor-workbook` | `jvc-comps-dd` | `jvc-track-research` |
| `market-sizing-workbook` | `jvc-market-sizing` | `jvc-track-research` |
| `roi-modeler-return-workbook` | `jvc-roi-modeler` | `jvc-market-sizing` |
| `explain-market-sizing-terms-no-route` | no route | `jvc-market-sizing` |
| `invoice-operational-boundary` | `jvc-invoice-manager` | `jvc-comps-dd` |

## Remaining Gaps

- 没有 model-executed route run（模型实际路由运行），不能声称真实路由准确率。
- 没有 blind holdout（盲测保留集）或 adversarial holdout（对抗性保留集）。
- hidden core 不应新增独立 route；它的正确入口是业务 skill 内的固定命令协议。
- 当前 15 个样例验证 fixture integrity、prompt signals、source contract signals 和 near-neighbor coverage；report 的文件渲染证据不是模型路由或盲审证据。
