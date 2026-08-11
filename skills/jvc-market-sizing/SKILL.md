---
name: jvc-market-sizing
description: |
  市场规模建模：针对细分赛道同时建立自上而下和自下而上模型，拆解 TAM（Total Addressable Market，总潜在市场，表示理论总需求）、SAM（Serviceable Available Market，可服务市场，表示能力与范围内可覆盖需求）和 SOM（Serviceable Obtainable Market，可获得市场，表示现实可获取份额），输出单一可审计 CSV（Comma-Separated Values，逗号分隔值，一种纯文本表格格式）。
  Use when user says '/jvc-market-sizing', '市场规模', 'market sizing', 'TAM', '市场有多大', '规模测算'.
user_invocable: true
version: "4.0.0"
---

# /jvc-market-sizing — 市场规模建模

针对细分赛道建立两条尽量独立的市场规模路径，用来源、公式和勾稽解释区间，而不是只给一个结论数字。

## 3.0 适用级别

最低适用级别：**L2+**（Level 2 or above，二级及以上尽调，用于验证关键假设）。

- 开始前读取 `spec/CONTEXT.md` 的市场定义和 `spec/hypotheses.md` 的市场假设；口径冲突先登记再计算。
- 当前项目低于 L2 时，先说明双路径测算、正交检查与来源核验成本，由用户确认是否提前使用。
- 唯一活跃模型进入 `market-sizing.csv`；公式、来源、三情景和正交检查不按级别省略。

## 反合理化约束

- “市场显然很大，不必精确测算” → 不确定就给区间和缺口，不能用形容词替代模型。
- “行业惯例可以直接当参数” → 每个输入写数值、单位、年份、地域和来源；无来源不得进入基准情景。
- “两种方法结果接近就算交叉验证” → 共享输入时不独立，必须在正交检查中披露。
- “模型算出数字，所以数字可靠” → 公式正确不能修复输入或口径错误；保留敏感项和证伪条件。

## 输入

- 细分赛道定义、地域范围、目标客户、应用场景
- 可选：`/jvc-track-research`、`/jvc-comps-dd` 产物和用户已有假设

## 证据内核（必须）

从本 `SKILL.md` 的实际目录解析同级 `../jvc-research-core/scripts/researchctl.py`，并使用绝对路径执行；不要依赖当前工作目录。

执行前必须读取同级 `../jvc-research-core/references/evidence-contract.md` 和当前 profile `../jvc-research-core/profiles/jvc-market-sizing.json`。

1. 新研究先准备完整 JSON（JavaScript Object Notation，JavaScript 对象表示法，一种结构化文本格式）`scope`，再运行 `init --skill jvc-market-sizing --run-dir <研究目录> --scope-file <scope.json>`；初始 `scope` 只能通过 `init --scope-file` 创建。
2. 复用已有研究链时运行 `init --skill jvc-market-sizing --run-dir <研究目录> --resume`。后续 `scope` 更正必须通过 `record --run-dir <研究目录> --input <records.jsonl>` 登记，并用 `supersedes` 指向当前有效 `scope`；问题、检索、来源、主张和更正也只能通过该命令登记，不得直接编辑 `evidence_registry.jsonl`，通用 `record` 不得创建 waiver。
3. 跨 skill 消费已有主张时，在新主张的 `derived_from_claim_ids` 中登记上游主张编号；缺失或失效的上游审计会阻断下游完成。
4. 本 CSV 的外部事实和用户假设在 `source_or_formula` 写 `[S编号]`；计算行保留公式及其输入行引用，不把模型估算伪装成来源事实。
5. 先运行本 skill 的 CSV validator，再运行 `audit --run-dir <研究目录> --skill jvc-market-sizing --artifact <研究目录>/market-sizing.csv`；每次 audit 必须同时读取命令退出状态和 `audit.json`。
6. 只有状态为 `blocked`、findings 中唯一阻断是 `partial_label_missing`，且至少一个 finding 为 `partial` 时，才在首个 `sources` 行的 `notes` 写入 `研究状态：partial`；写回后必须先重跑 CSV validator，再重跑 audit。存在其他阻断时不得用标签绕过。重跑得到 `partial` / exit `10` 才可 partial 交付；`ready` / exit `0` 才能称为完成；其他 `blocked` / exit `20` 只能交付证据缺口和下一步；exit `1` 必须修复后重跑。
7. 只有用户明确批准、且 blocker 与同 skill 最新有效 blocked audit 精确匹配时，才可运行 `waive --run-dir <研究目录> --skill jvc-market-sizing --rule <阻断规则> --reason <批准理由> --scope <批准范围> --approved-by <批准人> --residual-risk <剩余风险>`；不得自我批准，waiver 最多降级为 partial。

找不到内核、profile 不兼容、账本损坏或终审异常时，不得退回纯 prompt 模式。

## 执行步骤

### 1. 读取合同并核对来源

先读取 `references/model-contract.md` 和仓库 `templates/market-sizing-template.csv`。继承 Track Research 的赛道边界与 `derived_from_claim_ids`，再补充本模型确实需要的公开来源或用户假设；模板零值不得进入真实结论。

### 2. 建立两条路径

- Top-down（自上而下：从宏观或上位市场逐层收窄）按市场总量、可服务范围和渗透条件计算。
- Bottom-up（自下而上：从客户数、用量和价格等底层变量汇总）按正交客户或场景分项计算。
- 每个输入都保留年份、单位、三情景和 `[S编号]`；每条路径至少有一个 `[key_summary]` 汇总行。

### 3. 勾稽与正交检查

- reconciliation（勾稽：比较两条路径结果并解释差异）同时保留绝对差和相对差公式。
- orthogonality（正交性：判断分项及两条路径是否共享关键输入）用 `shared_input`、`shared_row_ids` 和 `independent_validation` 结构化披露；共享时必须写 `independent_validation=no`，不能声称构成独立验证。
- 三情景默认满足 `conservative <= base <= optimistic`；业务上合理的反向顺序必须在备注写 `[scenario_order_exception]`，并紧随原因。

### 4. 生成并校验 CSV

复制唯一活跃数据母版，替换占位输入并保留基于 `row_id` 的公式。最终文件固定命名为：

```text
market-sizing.csv
```

把 `SKILL_ROOT` 设为包含本 `SKILL.md` 的绝对目录，先运行：

```bash
python3 "$SKILL_ROOT/scripts/validate_csv.py" <研究目录>/market-sizing.csv
```

validator 通过后，才运行 Research Core audit。

## 输出

单个 `market-sizing.csv`，保存到当前研究目录；不并行生成 Excel 或第二份数据模板。

## 硬约束

- 只使用 `assumptions`、`top_down`、`bottom_up`、`reconciliation`、`orthogonality_check`、`sources` 六个分区。
- 不编造总量、增长率、渗透率、价格、客户数或用量；无可信输入时保留缺口并收窄结论。
- TAM、SAM、SOM 不混写；每个模型行明确年份、单位、情景、来源或公式、置信度和备注。
- 公式只引用已声明 `row_id`，不得形成直接或间接循环；关键汇总必须到达带来源数值叶。validator 只检查语法和依赖，不充当电子表格计算引擎。
- 中文输出；不输出“值得投/不值得投”等终局判断。
