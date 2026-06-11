# /jvc-market-sizing 市场规模建模 Excel 示例

> 示例只展示 workbook 内容结构。真实运行时应输出 `.xlsx`。

## assumptions

| assumption_id | variable | value | unit | year | geography | source_id | confidence | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | 目标中小制造企业数量 | 50000 | 家 | 2026 | 中国 | S1 | 低 | 示例数值，[未核实] |
| A2 | 单客户年质检软件支出 | 100000 | CNY/年 | 2026 | 中国 | S2 | 低 | 来自虚构客户访谈 |

## top_down

| line_id | level | parent_line_id | market_item | base_value | filter_or_share | calculated_value | formula | currency | year | source_id | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TD1 | TAM |  | 中国制造业质检自动化总支出 | 100000000000 | 100% | 100000000000 | =base_value*filter_or_share | CNY | 2026 | S1 | [未核实] |
| TD2 | SAM | TD1 | 中小制造企业可服务质检软件市场 | 100000000000 | 10% | 10000000000 | =base_value*filter_or_share | CNY | 2026 | S1 | 示例口径 |
| TD3 | SOM | TD2 | 五年内可获取市场 | 10000000000 | 3% | 300000000 | =base_value*filter_or_share | CNY | 2026 | S2 | [未核实] |

## bottom_up

| line_id | segment | customer_count | units_per_customer | annual_price_or_spend | penetration_rate | calculated_value | formula | currency | year | source_id | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BU1 | 3C 零部件中小工厂 | 10000 | 1 | 100000 | 5% | 50000000 | =customer_count*units_per_customer*annual_price_or_spend*penetration_rate | CNY | 2026 | S2 | 示例数值 |
| BU2 | 注塑件中小工厂 | 8000 | 1 | 80000 | 4% | 25600000 | =customer_count*units_per_customer*annual_price_or_spend*penetration_rate | CNY | 2026 | S2 | 示例数值 |

## reconciliation

| metric | top_down_value | bottom_up_value | difference | difference_pct | explanation | preferred_value | reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SAM | 10000000000 | 75600000 | 9924400000 | 99.2% | 自上而下口径过宽，自下而上只覆盖两个细分场景 | 75600000 | 当前更贴近目标客户，但覆盖不足 |

## orthogonality_check

| item_a | item_b | overlap_risk | overlap_description | resolution | status |
| --- | --- | --- | --- | --- | --- |
| 3C 零部件中小工厂 | 注塑件中小工厂 | yes | 部分 3C 塑胶件工厂可能同时属于两类 | 按主要产品收入归属，只计入一个 segment | needs_review |

## sources

| source_id | source_name | source_type | url_or_location | date | fields_supported | reliability |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | 示例行业报告 | 报告 | N/A | 2026-06-11 | TAM/SAM 假设 | 低 |
| S2 | 示例客户访谈 | 访谈 | 本地素材 | 2026-06-11 | 单价、渗透率 | 低 |
