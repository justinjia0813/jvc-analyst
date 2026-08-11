# /jvc-market-sizing 单表示例说明

CSV（Comma-Separated Values，逗号分隔值，一种纯文本表格格式）示例位于 `examples/market-sizing-example.csv`。其中数值与来源均为虚构演示，不得用于投资判断。

## 计算路径

- Top-down（自上而下：从上位市场逐层收窄）把上位市场规模乘以细分占比，TAM（Total Addressable Market，总潜在市场，表示理论总需求）的保守/基准/乐观演示结果分别是 64 / 100 / 144 亿元。
- Bottom-up（自下而上：从客户数、单客支出和渗透率汇总）对应演示结果为 1.28 / 2.50 / 4.32 亿元。
- 金额输入使用 CNY（Chinese Yuan，人民币元，用于人民币金额单位）；比例输入使用 `ratio`。
- `REC_ABS` 与 `REC_REL` 直接引用两条 `[key_summary]` 汇总路径，显示绝对差和相对差；示例差异主要来自 Bottom-up 只覆盖目标客户口径。
- `ORTHO_1` 写明 `shared_input=no；shared_row_ids=none；independent_validation=yes`，与两侧公式依赖一致。真实模型若共享输入，必须列出共享 `row_id` 并改为 `independent_validation=no`。

validator 不计算公式。`check_package.py` 对上述数字输入另做明确算术断言，证明示例期望值；validator 本身只检查公式语法和 `row_id` 引用。

## 校验

```bash
python3 skills/jvc-market-sizing/scripts/validate_csv.py examples/market-sizing-example.csv
```

同目录旧 `market-sizing-example.xlsx` 仅为历史、非权威 fixture，不参与当前合同、校验或交付。
