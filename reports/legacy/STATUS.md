# Historical Legacy Workbooks（历史遗留产物归档）

> 本目录保存 CSV / Markdown 迁移前（2026-07-29/30）的输出评测与盲审产物。它们由旧工作簿时代的
> 模型输出与人工判断生成，**无法从当前活跃 CSV/Markdown 案例确定性再生成**（再生会凭空制造人工
> 判断），因此保留为历史记录，**已移出活跃治理证据**。

## 分类规则

| 文件 | 分类 | 说明 |
| --- | --- | --- |
| `research-core-output-eval.json` / `.md` | historical-legacy-workbook | 基于旧 `output_cases.jsonl`（工作簿时代输出）的评分；旧评分器不在仓库内，无法从新 CSV 案例确定再生 |
| `output_blind_review_pack.json` / `.md` | historical-legacy-workbook | A/B 盲审包，内含旧工作簿时代模型输出，无法确定再生 |
| `output_blind_answer_key.json` | historical-legacy-workbook | 与旧盲审包配套的答案密钥 |
| `output_review_kit.json` / `.md` / `.html` | historical-legacy-workbook | 盲审包的可读渲染产物 |
| `output_review_adjudication.json` / `.md` | historical-legacy-workbook | 裁决结果嵌入 Justin 的人工判断，禁止再生 |
| `output_review_decisions.json` | historical-legacy-workbook | Justin 的原始盲审决定，禁止再生 |

## 边界

- 这些文件**不得**被 Review Studio、Output Quality Scorecard 或其他活跃治理证据引用为“新合同通过”的证明。
- 当前活跃的评测证据是 `evals/output/cases.json`、`evals/research-core/cases.json`、
  `evals/research-core/output_cases.jsonl` 及其 CSV 案例文件。
- 每个 JSON 顶部均带 `historical_legacy_workbook` 状态块；每个 Markdown 顶部均带历史遗留横幅。
