---
name: jvc-roi-modeler
description: |
  投资回报模型：根据投资条款、财务预测、后续融资假设和退出情形，逐轮计算稀释并输出 MOIC/IRR 区间的 Excel 工作簿。
  Use when user says '回报模型', 'ROI', 'IRR', '回报测算', '稀释计算', '退出测算'.
---

# /jvc-roi-modeler — 投资回报模型

根据本轮投资条款、财务预测、后续融资稀释和退出假设，测算单笔投资的回报区间。

## 输入

用户提供以下信息（缺失项会提示用户补充）：

| 类别 | 需要的数据 |
|------|-----------|
| 本轮条款 | 投资金额、投前/投后估值、初始持股比例、优先权条款 |
| 财务预测 | 未来 3-5 年收入、毛利、EBITDA（净利润）、现金消耗 |
| 后续融资 | 预期的后续轮次数量、每轮融资金额和估值、是否跟投 |
| 退出假设 | 保守/中性/乐观三种退出情形的估值倍数或绝对估值、退出年份 |

## 执行步骤

### 1. 确认输入完整性

检查用户提供的数据，缺失关键项时明确列出需要补充的内容，不自行假设。

### 2. 逐轮稀释计算

从本轮开始，逐轮计算：
- 每轮新增股份
- 每轮后的持股比例
- 累计稀释率
- 跟投情形下的追加投资和持股

### 3. 三情形退出计算

对保守/中性/乐观三种情形，分别计算：
- 退出时公司估值
- 投资人持有的股权价值
- 退出回款（考虑优先权）
- MOIC（投资倍数）
- IRR（内部收益率，按退出年份计算）

### 4. 敏感性分析

识别关键敏感变量（退出估值、稀释轮次数、跟投比例等），对核心变量做 ±20% 的敏感性矩阵。

### 5. 生成 Excel

先用仓库内 workbook 模板脚本生成 `.xlsx`：

```bash
python3 scripts/generate-workbook.py templates/roi-modeler-template.md output/{项目}_jvc-roi-modeler_{YYYYMMDD}.xlsx
```

填完条款、预测、稀释、退出情形和敏感性分析后运行结构校验：

```bash
python3 scripts/validate-workbook.py output/{项目}_jvc-roi-modeler_{YYYYMMDD}.xlsx templates/roi-modeler-template.md
```

Workbook 包含以下 sheet：

- **investment_terms**：本轮投资条款汇总
- **financial_forecast**：财务预测表
- **financing_dilution**：逐轮融资稀释计算（过程表）
- **ownership**：各轮次后的持股比例变化
- **exit_scenarios**：三种退出情形及回款计算
- **returns**：MOIC 和 IRR 汇总
- **sensitivity**：关键变量敏感性矩阵
- **sources**：所有假设的来源标注

## 输出

Excel 文件（`.xlsx`），保存到用户指定路径或当前目录。

## 硬约束

- 不用最终持股倒推，必须逐轮计算稀释
- 退出倍数、财务预测、后续融资假设必须有来源或标 `[用户假设]` / `[未核实]`
- 不输出"值得投/不值得投"，只输出回报区间、驱动因素和敏感项
- 缺失关键输入时提示用户补充，不自行填充
- 中文输出
