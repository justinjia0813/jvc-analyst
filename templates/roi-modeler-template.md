# /jvc-roi-modeler 投资回报 Excel 模板

最终输出文件：`{项目名}_jvc-roi-modeler_{YYYYMMDD}.xlsx`

## Workbook Rules

- 所有金额注明币种。
- 五年预测保留逐年数据，不只保留退出年。
- 所有公式列保留公式。
- 缺失假设使用 `[需要用户提供]` 或 `[未核实]`。

## Sheet: investment_terms

| 字段 | 说明 |
| --- | --- |
| investment_amount | 本轮投资金额 |
| pre_money_valuation | 投前估值 |
| post_money_valuation | 投后估值 |
| initial_ownership | 本轮后持股比例 |
| security_type | 股权 / 可转债 / SAFE / 其他 |
| option_pool | 期权池比例 |
| currency | 币种 |
| source_id | 来源编号 |
| notes | 备注 |

## Sheet: financial_forecast

| 字段 | 说明 |
| --- | --- |
| year | 年份 |
| revenue | 收入 |
| gross_margin | 毛利率 |
| gross_profit | 毛利 |
| EBITDA | EBITDA |
| net_income | 净利润 |
| cash_burn | 现金消耗 |
| ending_cash | 年末现金 |
| source_id | 来源编号 |
| notes | 备注 |

## Sheet: financing_dilution

| 字段 | 说明 |
| --- | --- |
| round | 后续轮次 |
| year | 年份 |
| new_money | 新融资金额 |
| pre_money_valuation | 该轮投前估值 |
| post_money_valuation | 该轮投后估值 |
| investor_participates | 是否跟投 |
| pro_rata_amount | 跟投金额 |
| dilution_pct | 本轮稀释比例 |
| ownership_after_round | 该轮后持股比例 |
| source_id | 来源编号 |
| notes | 备注 |

## Sheet: exit_scenarios

| 字段 | 说明 |
| --- | --- |
| scenario | 保守 / 中性 / 乐观 |
| exit_year | 退出年份 |
| exit_metric | 收入 / EBITDA / 净利润 |
| exit_metric_value | 退出年指标值 |
| exit_multiple | 退出倍数 |
| enterprise_value | 企业价值 |
| net_debt_or_cash | 净债务或净现金 |
| equity_value | 股权价值 |
| source_id | 来源编号 |
| notes | 备注 |

## Sheet: ownership

| 字段 | 说明 |
| --- | --- |
| year_or_round | 年份或轮次 |
| ownership_start | 期初持股 |
| dilution_pct | 稀释比例 |
| pro_rata_investment | 跟投金额 |
| ownership_end | 期末持股 |
| notes | 备注 |

## Sheet: returns

| 字段 | 说明 |
| --- | --- |
| scenario | 保守 / 中性 / 乐观 |
| invested_capital | 累计投入资本 |
| exit_year | 退出年份 |
| final_ownership | 退出时持股比例 |
| exit_equity_value | 退出股权价值 |
| proceeds | 投资人回款金额 |
| MOIC | 投资回报倍数 |
| IRR | 内部收益率 |
| key_driver | 回报最大驱动因素 |

## Sheet: sensitivity

| 字段 | 说明 |
| --- | --- |
| variable | 敏感变量 |
| low_case | 低值 |
| base_case | 基准值 |
| high_case | 高值 |
| impact_on_MOIC | 对 MOIC 的影响 |
| impact_on_IRR | 对 IRR 的影响 |

## Sheet: sources

| 字段 | 说明 |
| --- | --- |
| source_id | 来源编号 |
| source_name | 来源名称 |
| source_type | deck / 财务模型 / comps / 用户假设 / 推测 |
| url_or_location | 链接或本地位置 |
| date | 来源日期 |
| fields_supported | 支撑字段 |
| reliability | 高 / 中 / 低 |
