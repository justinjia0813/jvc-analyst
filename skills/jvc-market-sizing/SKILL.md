---
name: jvc-market-sizing
description: |
  市场规模建模：针对细分赛道同时建立自上而下和自下而上两套 TAM/SAM/SOM 模型，输出 Excel 工作簿。
  Use when user says '市场规模', 'market sizing', 'TAM', '市场有多大', '规模测算'.
---

# /jvc-market-sizing — 市场规模建模

针对细分赛道估算 TAM（总可及市场）/SAM（可服务市场）/SOM（可获得市场），拆成可复核的模型。

## 输入

- 细分赛道定义、地域范围、目标客户、应用场景
- 可选：`/jvc-track-research`、`/jvc-comps-dd` 产出、用户已有假设

## 执行步骤

### 1. 联网搜索

搜集与市场规模相关的公开数据点（行业报告、上市公司年报、政策文件、新闻）。

### 2. 自上而下模型（Top-Down）

从宏观数字逐步收窄：
- 大行业总规模 → 细分赛道占比 → 可服务区域 → 可服务客群
- 每一步的缩减比例必须有来源或标 `[推测]`

### 3. 自下而上模型（Bottom-Up）

从微观单位堆叠：
- 目标客户数量 × 单客户年支出 × 渗透率 → SOM → SAM → TAM
- 客户数量和单价必须有来源或标 `[推测]`

### 4. 正交性检查

- 检查分项是否正交（不重叠不遗漏）
- 如有重叠，说明扣除方式或唯一归属方式

### 5. 两套模型对账（Reconciliation）

- 比较 Top-Down 和 Bottom-Up 的结果差异
- 分析差异原因，标注哪套更可信、为什么

### 6. 生成 Excel

先用仓库内 workbook 模板脚本生成 `.xlsx`：

```bash
python3 scripts/generate-workbook.py templates/market-sizing-template.md output/{细分赛道}_jvc-market-sizing_{YYYYMMDD}.xlsx
```

填完模型、公式、来源和正交检查后运行结构校验：

```bash
python3 scripts/validate-workbook.py output/{细分赛道}_jvc-market-sizing_{YYYYMMDD}.xlsx templates/market-sizing-template.md
```

Workbook 包含以下 sheet：

- **assumptions**：所有假设及其来源
- **top_down**：自上而下模型，每步有公式和来源
- **bottom_up**：自下而上模型，每步有公式和来源
- **reconciliation**：两套模型对比和差异分析
- **orthogonality_check**：分项正交性验证
- **sources**：所有数据来源汇总

## 输出

Excel 文件（`.xlsx`），保存到用户指定路径或当前目录。

## 硬约束

- 分项必须正交；重叠时必须说明扣除或唯一归属方式
- 不编造市场规模、渗透率、价格、客户数
- TAM/SAM/SOM 不混写，所有数字标来源或标 `[未核实]`
- 每个条目明确口径、年份、币种、来源
- 中文输出
