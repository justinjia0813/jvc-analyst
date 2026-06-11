# /comps-dd 竞品尽调 Excel 模板

最终输出文件：`{赛道或项目名}_comps-dd_{YYYYMMDD}.xlsx`

## Workbook Rules

- 每个 sheet 第一行是字段名。
- 所有金额字段必须注明币种。
- 所有收入、估值、市值、融资金额必须有 `source_id`。
- 缺失数据不要空着，使用 `[未披露]`、`[未核实]`、`[不适用]`。

## Sheet: companies

| 字段 | 说明 |
| --- | --- |
| company_name | 公司名称 |
| country_region | 国家/地区 |
| company_type | 上市公司 / 初创公司 / 海外龙头 / 上下游参照 |
| listing_status | A股 / 港股 / 美股 / 未上市 / 拟上市 |
| value_chain_position | 上游 / 中游 / 下游 / 平台 / 集成 |
| technology_route | 技术路线 |
| product | 核心产品或服务 |
| target_customers | 目标客户/应用场景 |
| latest_year_revenue | 最近一年收入 |
| revenue_year | 收入年份 |
| revenue_currency | 收入币种 |
| latest_valuation_or_market_cap | 最新估值或市值 |
| valuation_type | 融资估值 / 市值 / 未披露 |
| valuation_date | 估值或市值日期 |
| financing_stage | 融资阶段 |
| key_investors | 主要投资方 |
| comparability | 为什么可比 |
| source_id | 来源编号 |
| confidence | 高 / 中 / 低 |
| notes | 备注 |

## Sheet: segmentation

| 字段 | 说明 |
| --- | --- |
| segment_type | 技术路线 / 客户类型 / 商业模式 / 价值链环节 |
| segment_name | 分组名称 |
| included_companies | 公司列表 |
| why_it_matters | 为什么这个分组重要 |
| overlap_warning | 是否与其他分组重叠 |
| source_id | 来源编号 |

## Sheet: sources

| 字段 | 说明 |
| --- | --- |
| source_id | 来源编号 |
| source_name | 来源名称 |
| source_type | 年报 / 招股书 / 新闻 / 数据库 / 公司官网 / 用户材料 |
| url_or_location | 链接或本地位置 |
| date | 来源日期 |
| fields_supported | 支撑哪些字段 |
| reliability | 高 / 中 / 低 |

## Sheet: coverage_notes

| 字段 | 说明 |
| --- | --- |
| issue | 覆盖缺口或口径问题 |
| affected_companies | 受影响公司 |
| impact | 对判断的影响 |
| next_step | 下一步补证据 |
