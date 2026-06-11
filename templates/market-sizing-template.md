# /jvc-market-sizing 市场规模建模 Excel 模板

最终输出文件：`{细分赛道}_market-sizing_{YYYYMMDD}.xlsx`

## Workbook Rules

- 所有金额注明币种，所有年份注明口径。
- 每个模型行都必须有 `source_id` 或 `[未核实]`。
- 所有分项必须通过 `orthogonality_check`，避免复算、多算。
- 所有公式列应保留公式，不只贴结果值。

## Sheet: assumptions

| 字段 | 说明 |
| --- | --- |
| assumption_id | 假设编号 |
| variable | 变量名 |
| value | 数值 |
| unit | 单位 |
| year | 年份 |
| geography | 地域 |
| source_id | 来源编号 |
| confidence | 高 / 中 / 低 |
| notes | 备注 |

## Sheet: top_down

| 字段 | 说明 |
| --- | --- |
| line_id | 行编号 |
| level | TAM / SAM / SOM |
| parent_line_id | 上一级口径 |
| market_item | 市场条目 |
| base_value | 基础市场规模 |
| filter_or_share | 筛选比例或占比 |
| calculated_value | 计算后规模 |
| formula | 公式 |
| currency | 币种 |
| year | 年份 |
| source_id | 来源编号 |
| notes | 备注 |

## Sheet: bottom_up

| 字段 | 说明 |
| --- | --- |
| line_id | 行编号 |
| segment | 正交客户/场景分组 |
| customer_count | 客户数 |
| units_per_customer | 单客户点位/设备/账号数 |
| annual_price_or_spend | 年单价或年支出 |
| penetration_rate | 渗透率 |
| calculated_value | 计算后规模 |
| formula | 公式 |
| currency | 币种 |
| year | 年份 |
| source_id | 来源编号 |
| notes | 备注 |

## Sheet: reconciliation

| 字段 | 说明 |
| --- | --- |
| metric | TAM / SAM / SOM |
| top_down_value | 自上而下结果 |
| bottom_up_value | 自下而上结果 |
| difference | 差异 |
| difference_pct | 差异比例 |
| explanation | 差异解释 |
| preferred_value | 建议采用值 |
| reason | 采用原因 |

## Sheet: orthogonality_check

| 字段 | 说明 |
| --- | --- |
| item_a | 条目 A |
| item_b | 条目 B |
| overlap_risk | 是否可能重叠 |
| overlap_description | 重叠原因 |
| resolution | 唯一归属或扣除方式 |
| status | clear / needs_review |

## Sheet: sources

| 字段 | 说明 |
| --- | --- |
| source_id | 来源编号 |
| source_name | 来源名称 |
| source_type | 年报 / 报告 / 访谈 / 数据库 / 推测 |
| url_or_location | 链接或本地位置 |
| date | 来源日期 |
| fields_supported | 支撑字段 |
| reliability | 高 / 中 / 低 |
