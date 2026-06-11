# /comps-dd 竞品尽调 Excel 示例

> 示例只展示 workbook 内容结构。真实运行时应输出 `.xlsx`。

## companies

| company_name | country_region | company_type | listing_status | value_chain_position | technology_route | product | target_customers | latest_year_revenue | revenue_year | revenue_currency | latest_valuation_or_market_cap | valuation_type | valuation_date | financing_stage | key_investors | comparability | source_id | confidence | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 星尘工坊 | 中国 | 初创公司 | 未上市 | 中游 | 低代码训练平台 | 质检模型训练 + 边缘盒子 | 中小制造企业 | 420万 | 2026E | CNY | [未披露] | 未披露 | [未披露] | Pre-A | [未披露] | 目标项目 | S1 | 低 | 收入来自创始人自述，[未核实] |
| 传统视觉厂商 A | 中国 | 上市公司 | A股 | 中游 | 传统规则视觉 | 工业视觉设备 | 3C/汽车制造 | [未核实] | 2025 | CNY | [未核实] | 市值 | 2026-06-11 | 不适用 | 不适用 | 客户预算替代方案 | S2 | 低 | 示例占位 |
| 海外视觉龙头 B | 海外 | 海外龙头 | 美股 | 上游/中游 | 传统规则视觉 | 工业相机和视觉系统 | 全球制造业 | [未核实] | 2025 | USD | [未核实] | 市值 | 2026-06-11 | 不适用 | 不适用 | 海外标杆 | S3 | 低 | 需查分部收入 |

## segmentation

| segment_type | segment_name | included_companies | why_it_matters | overlap_warning | source_id |
| --- | --- | --- | --- | --- | --- |
| 技术路线 | 低代码训练平台 | 星尘工坊 | 代表软件化和低门槛交付方向 | 可能与深度学习视觉重叠 | S1 |
| 技术路线 | 传统规则视觉 | 传统视觉厂商 A, 海外视觉龙头 B | 代表成熟方案和客户替代路径 | 与设备/集成商业模式重叠 | S2 |

## sources

| source_id | source_name | source_type | url_or_location | date | fields_supported | reliability |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | 虚构 deck | 用户材料 | 本地素材 | 2026-06-11 | 星尘工坊产品、融资、收入 | 低 |
| S2 | 示例上市公司公告 | 年报 | N/A | 2026-04-30 | 收入、市值 | 低 |
| S3 | 示例海外公司年报 | 年报 | N/A | 2026-03-15 | 收入、市值 | 低 |

## coverage_notes

| issue | affected_companies | impact | next_step |
| --- | --- | --- | --- |
| 初创公司估值普遍未披露 | 星尘工坊及同类初创公司 | 难以直接做 EV/Sales 横向比较 | 查融资新闻、企查查/IT桔子、询问创始人 |
| 海外龙头可能只有集团收入 | 海外视觉龙头 B | 与细分业务收入不可比 | 查分部披露或分析师报告 |
