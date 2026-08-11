# /jvc-market-sizing 市场规模单表模板合同

CSV（Comma-Separated Values，逗号分隔值，一种纯文本表格格式）最终输出文件固定为 `market-sizing.csv`。唯一活跃数据母版是同目录的 `market-sizing-template.csv`；本文只解释如何填写，不是第二份数据模板。

## 填写规则

- 保留固定表头和六个分区，不添加工作表或并行数据文件。
- 把模板中的零值、`[需要用户提供]` 和正交性占位说明全部替换为真实输入或明确缺口。
- 金额使用清楚的币种和量纲，例如 `CNY（Chinese Yuan，人民币元，用于人民币金额单位）`；比例统一使用 `ratio`，不要把 `10` 与 `10%` 混用。
- 输入行只要任一情景是数值，就只能在 `source_or_formula` 写有效 `[S编号]`，并在 `sources` 分区提供公开链接或本地材料定位；混合数值/公式行也不例外，写在 `notes` 的编号不能代替来源列。
- Top-down（自上而下：从上位市场逐层收窄）和 Bottom-up（自下而上：从底层客户、用量与价格汇总）各保留 `[key_summary]` 公式行。
- 每个 `[key_summary]` 沿公式依赖至少到达一个同侧或 `assumptions` 的带来源数值叶；不得形成直接或间接循环。
- `reconciliation` 的绝对差、相对差公式直接引用两侧 `[key_summary]`；`orthogonality_check` 按 `shared_input`、`shared_row_ids`、`independent_validation` 各一次披露共享输入和独立性，多行披露不得冲突。
- 来源行不使用 `model` 置信度；纯公式行和结构披露行必须使用 `model`；数值输入行不得使用 `model`。

完整字段、公式与失败规则见 `skills/jvc-market-sizing/references/model-contract.md`。

## 校验

```bash
python3 skills/jvc-market-sizing/scripts/validate_csv.py templates/market-sizing-template.csv
```

validator 只审计结构、公式语法和引用关系，不替代公式求值与人工口径复核。
