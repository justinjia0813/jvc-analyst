---
name: market-sizing
description: Use when 需要针对细分赛道做 TAM/SAM/SOM 市场规模建模、同时使用自上而下和自下而上方法，并输出 Excel
---

# /market-sizing 市场规模建模

`/market-sizing` 用于把用户给定的细分赛道拆成可计算、可追溯、可复核的市场规模模型。最终输出必须是 `.xlsx`。

## 输入

- 细分赛道定义和地域范围
- 目标客户、应用场景、价格/用量/渗透率等假设
- 可选：`/track-research` 产业知识图谱、`/comps-dd` 竞品数据、用户已有市场口径

## 必须包含两种方法

1. **自上而下**：从宏观市场、行业收入、可服务细分占比逐层收敛。
2. **自下而上**：从客户数、部署点位、单价、用量、渗透率等底层变量累加。

两种方法要在 `reconciliation` 中对齐差异，不能只给一个孤立数字。

## 正交与防复算约束

- 每个条目必须有明确口径：地域、客户类型、应用场景、时间、币种。
- 分条目时确保正交，不存在复算、多算。
- 如果一个客户或场景可能落入多个条目，必须在 `orthogonality_check` 标出并选择唯一归属。
- 不把 TAM、SAM、SOM 混写：
  - TAM：理论总市场
  - SAM：当前产品/地域/渠道可服务市场
  - SOM：合理周期内可获取市场
- 找不到依据的参数标 `[未核实]`，不要补数字。

## 输出 Workbook

使用 `templates/market-sizing-template.md` 的 sheet schema：

- `assumptions`
- `top_down`
- `bottom_up`
- `reconciliation`
- `orthogonality_check`
- `sources`

## 反馈迭代空间

真实项目跑完后，优先调整：

- 正交检查是否能发现重复计算
- 自下而上变量是否足够贴近真实商业模式
- SAM/SOM 的收敛口径是否过粗
- 输出能否直接进入 `/ic-memo` 的市场章节
