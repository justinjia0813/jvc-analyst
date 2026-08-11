# /jvc-roi-modeler 投资回报 CSV 模板合同

最终输出文件：`{项目名}_jvc-roi-modeler_{YYYYMMDD}.csv`

实际母版位于 `templates/roi-modeler-template.csv`，其结构来自用户提供的 `roi-modeler-template.xlsx`，但已修正以下勾稽：

- IRR（Internal Rate of Return，内部收益率，用于按现金流时间衡量年化回报）的终期现金流使用退出总回款，不使用扣除本金后的净收益。
- 累计收益率使用净收益除以累计投入；不再把 MOIC（Multiple on Invested Capital，投入资本倍数，用于衡量总回款是投入资本的多少倍）乘以 100% 充当收益率。
- 投资本金通过单元格引用进入净收益与现金流公式，不在计算区硬编码示例金额。

## 固定结构

- 单个 CSV 文件，不拆分工作表。
- 固定列：`section`、`metric`、`unit`、年度/退出情景、`source_id`、`assumption_status`、`notes`。
- 年度标题可以整体平移，但保留一个实际期、五个年度现金流期和同一退出年的保守/中性/乐观三列。
- 固定行：研究状态、稀释率、收入、净利润、净利率、估值方法、估值倍数、公司估值、基金持股、基金股权价值、投入资本、退出总回款、净收益、MOIC、累计收益率、IRR 和三条情景现金流。
- 输入与计算保持分行；计算单元格保留以 `=` 开头的公式。
- 当前母版只覆盖基金不跟投；出现后续跟投时必须扩展持股公式和校验器。

## 校验

```bash
python3 skills/jvc-roi-modeler/scripts/validate_csv.py templates/roi-modeler-template.csv
```
