> **Historical legacy workbook（历史遗留产物）**：本文档由 CSV 迁移前的输出评测/盲审流水线
> （2026-07-29/30）基于旧工作簿时代的模型输出与人工判断生成，无法从当前活跃 CSV/Markdown 案例
> 确定性再生成（再生会凭空制造人工判断），因此保留为历史记录，已移出活跃治理证据。
> **不作为任何新 CSV 合同通过的证明。**

# Output Quality Scorecard

This v0 scorecard compares static without-skill and with-skill outputs using assertion grading.

- Cases: `2`
- Baseline pass rate: `64.09`
- With-skill pass rate: `100.0`
- Delta: `35.91`
- Regressions: `0`
- Blind A/B pairs: `2`
- Gate pass: `True`

Blind review artifacts are generated separately so reviewers can inspect A/B outputs without seeing the answer key.
Run output review adjudication after reviewer decisions are recorded; pending cases should stay pending rather than being counted as human agreement.

## Case Results

| Case | Baseline | With Skill | Delta | Winner | Failed With-Skill Assertions |
| --- | ---: | ---: | ---: | --- | --- |
| glass-substrate-public-research-output | 68.18 | 100.0 | 31.82 | with_skill | None |
| industrial-vision-market-model-output | 60.0 | 100.0 | 40.0 | with_skill | None |

## Failure Taxonomy

- No with-skill assertion failures.

## Next Fixes

- Add holdout cases before using this as a release gate.
- Promote repeated failed assertions into the output-risk profile.
- Keep assertions tied to material deliverables, not phrasing trivia.
