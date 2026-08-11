# Market Sizing 单表模型合同

正式产物是一个严格 UTF-8（Unicode Transformation Format 8-bit，八位 Unicode 转换格式，用于统一文本编码）的 CSV（Comma-Separated Values，逗号分隔值，一种纯文本表格格式）文件，固定命名为 `market-sizing.csv`。唯一活跃数据母版是仓库根目录的 `templates/market-sizing-template.csv`。

## 固定结构

表头必须逐字等于：

```text
section,row_id,item,year,unit,conservative,base,optimistic,source_or_formula,confidence,notes
```

`section` 只允许且必须覆盖：

- `assumptions`
- `top_down`
- `bottom_up`
- `reconciliation`
- `orthogonality_check`
- `sources`

`row_id` 在全文件唯一，只使用英文字母、数字和下划线，且不能以数字开头。`sources` 行的 `row_id` 使用 `S1`、`S2` 等编号。

## 行与来源

- 除 `sources` 外，所有模型行必须填写四位年份、单位和保守/基准/乐观三情景。
- 三情景单元格只能是有限数值，或以 `=` 开头的公式。
- `assumptions`、`top_down`、`bottom_up` 行只要任一情景是数值，就必须在 `source_or_formula` 写一个或多个有效 `[S编号]`；对应编号必须在 `sources` 分区声明。公式与数值混合的行不能绕过该要求。写在 `notes` 的编号仍会做未知来源检查，但不能满足数值输入的来源要求。模型计算行写“模型公式”等口径说明。
- 来源行在 `source_or_formula` 写公开链接或本地材料定位；无法确认时使用 `[需要用户提供]`，不得伪造链接。
- `confidence` 固定为 `high`、`medium`、`low`、`model`、`unknown` 之一。`sources` 只能使用 `high`、`medium`、`low`、`unknown`；三情景全部为公式的行和 `orthogonality_check` 结构披露行必须使用 `model`；含数值的输入行不得使用 `model`。

## 公式语法

公式直接引用已声明的模型 `row_id`。唯一函数是 ABS（Absolute Value，绝对值函数，用于返回数值的非负大小），例如：

```text
=TD_MARKET*TD_SHARE
=ABS(TD_SUMMARY-BU_SUMMARY)/TD_SUMMARY
```

只允许数字、已声明行引用、括号、加减乘除、正负号和 `ABS()`。validator 使用显式栈逐情景检查依赖图；直接或间接循环引用均报出循环路径。它只检查语法和依赖关系，不计算公式，也不实现通用电子表格引擎。

Top-down（自上而下：从宏观或上位市场逐层收窄）与 Bottom-up（自下而上：从客户数、用量和价格等底层变量汇总）各至少有一个在 `notes` 标记 `[key_summary]` 的关键汇总行。每个关键汇总情景沿依赖闭包必须至少到达一个位于 `assumptions` 或同侧分区、带有效来源的数值叶；只写常数公式、无来源叶或汇总循环均不合格。

## 勾稽、正交与情景

- `reconciliation` 至少包含 `notes` 标记 `[absolute_difference]` 的绝对差行和 `[relative_difference]` 的相对差行；两个标记必须位于不同 `row_id`。每个情景公式必须直接引用两侧 `[key_summary]` 行，引用任意原始输入不能代替汇总勾稽。
- validator 从两侧 `[key_summary]` 的三情景公式提取直接及传递的数值输入依赖，并求共享 `row_id`。`orthogonality_check` 至少有一行按 `shared_input=yes|no；shared_row_ids=<以 | 分隔的 row_id 或 none>；independent_validation=yes|no；<具体解释>` 披露；三个结构字段在一个披露行各且仅出现一次。检测到共享输入时，披露必须逐项一致，且只能写 `independent_validation=no`；无共享输入时 `shared_row_ids=none`。存在多行完整披露时，其规范化三元组必须相同。
- 数值行默认满足 `conservative <= base <= optimistic`。若业务含义导致合理反向排序，在 `notes` 写 `[scenario_order_exception]`，并在该标记之后给出具体原因；标记后至少包含四个 Unicode 字母或数字，标点、空白和标记前备注均不能充当原因。
- 公式结果的情景顺序由模型作者在电子表格软件中复核；validator 不求值公式。

## 最小验收

```bash
python3 skills/jvc-market-sizing/scripts/validate_csv.py market-sizing.csv
```

该命令通过后，才可把产物交给 Research Core audit。程序包自检另用独立数字断言验证示例输入的预期算术，不把该断言扩展成公式引擎。
