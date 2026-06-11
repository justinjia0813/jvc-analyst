# /roi-modeler 投资回报 Excel 示例

> 示例只展示 workbook 内容结构。真实运行时应输出 `.xlsx`。

## investment_terms

| investment_amount | pre_money_valuation | post_money_valuation | initial_ownership | security_type | option_pool | currency | source_id | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 30000000 | 270000000 | 300000000 | 10% | 股权 | [未核实] | CNY | S1 | 示例条款 |

## financial_forecast

| year | revenue | gross_margin | gross_profit | EBITDA | net_income | cash_burn | ending_cash | source_id | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026 | 4200000 | 45% | 1890000 | -15000000 | -18000000 | 20000000 | 10000000 | S1 | [未核实] |
| 2027 | 15000000 | 50% | 7500000 | -12000000 | -15000000 | 18000000 | 20000000 | S2 | 用户假设 |
| 2028 | 50000000 | 55% | 27500000 | -5000000 | -8000000 | 10000000 | 15000000 | S2 | 用户假设 |
| 2029 | 120000000 | 60% | 72000000 | 10000000 | 5000000 | 0 | 25000000 | S2 | 用户假设 |
| 2030 | 250000000 | 62% | 155000000 | 40000000 | 28000000 | 0 | 60000000 | S2 | 用户假设 |

## financing_dilution

| round | year | new_money | pre_money_valuation | post_money_valuation | investor_participates | pro_rata_amount | dilution_pct | ownership_after_round | source_id | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Series A | 2027 | 80000000 | 600000000 | 680000000 | no | 0 | 11.8% | 8.8% | S2 | 示例假设 |
| Series B | 2029 | 150000000 | 1500000000 | 1650000000 | no | 0 | 9.1% | 8.0% | S2 | 示例假设 |

## exit_scenarios

| scenario | exit_year | exit_metric | exit_metric_value | exit_multiple | enterprise_value | net_debt_or_cash | equity_value | source_id | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 保守 | 2030 | revenue | 180000000 | 3x | 540000000 | 0 | 540000000 | S3 | 倍数[未核实] |
| 中性 | 2030 | revenue | 250000000 | 5x | 1250000000 | 0 | 1250000000 | S3 | 倍数[未核实] |
| 乐观 | 2030 | revenue | 400000000 | 8x | 3200000000 | 0 | 3200000000 | S3 | 倍数[未核实] |

## ownership

| year_or_round | ownership_start | dilution_pct | pro_rata_investment | ownership_end | notes |
| --- | --- | --- | --- | --- | --- |
| 本轮后 | 0% | 0% | 30000000 | 10.0% | 初始持股 |
| Series A | 10.0% | 11.8% | 0 | 8.8% | 未跟投 |
| Series B | 8.8% | 9.1% | 0 | 8.0% | 未跟投 |

## returns

| scenario | invested_capital | exit_year | final_ownership | exit_equity_value | proceeds | MOIC | IRR | key_driver |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 保守 | 30000000 | 2030 | 8.0% | 540000000 | 43200000 | 1.44x | 9.6% | 倍数收缩且收入不达预期 |
| 中性 | 30000000 | 2030 | 8.0% | 1250000000 | 100000000 | 3.33x | 35.1% | 收入增长和 5x revenue multiple |
| 乐观 | 30000000 | 2030 | 8.0% | 3200000000 | 256000000 | 8.53x | 70.9% | 高收入和高倍数 |

## sensitivity

| variable | low_case | base_case | high_case | impact_on_MOIC | impact_on_IRR |
| --- | --- | --- | --- | --- | --- |
| exit_multiple | 3x | 5x | 8x | 高 | 高 |
| ownership_dilution | 25% | 20% | 10% | 中 | 中 |

## sources

| source_id | source_name | source_type | url_or_location | date | fields_supported | reliability |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | 虚构融资条款 | 用户假设 | 本地素材 | 2026-06-11 | 投资金额、估值 | 低 |
| S2 | 虚构五年预测 | 用户假设 | 本地素材 | 2026-06-11 | 收入、融资稀释 | 低 |
| S3 | 虚构 comps 倍数 | comps | N/A | 2026-06-11 | 退出倍数 | 低 |
