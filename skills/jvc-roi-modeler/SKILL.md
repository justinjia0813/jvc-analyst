---
name: jvc-roi-modeler
description: |
  投资回报模型：按用户提供的母版，根据投资条款、财务预测、后续融资假设和退出情形，逐轮计算稀释并输出公式可审计的 CSV 回报表。
  Use when user says '/jvc-roi-modeler', '回报模型', 'ROI', 'IRR', '回报测算', '稀释计算', '退出测算'.
user_invocable: true
version: "4.0.0"
---

# /jvc-roi-modeler — ROI（Return on Investment，投资回报，用于衡量投入资本收益）模型

根据本轮投资条款、财务预测、后续融资稀释和退出假设，复用用户母版的行式结构，测算单笔投资的回报区间。

## 3.0 适用级别

最低适用级别：**L2+**（Level 2 or above，二级及以上尽调，用于验证关键假设）。

- 开始前读取 `spec/CONTEXT.md` 的估值口径、`spec/hypotheses.md` 的财务假设和已有条款来源。
- 当前项目低于 L2 时，先说明条款、稀释与退出假设的补充成本，由用户确认是否提前建模。
- 输出进入 `05-roi-modeler.csv`；公式、输入来源、三种退出情景和稀释检查不得省略。

## 反合理化约束

- “缺少条款时先用行业默认值” → 不猜；缺失输入写 `[需要用户提供]`，对应结果不得伪装成可用结论。
- “乐观情景最符合团队目标，可作基准” → 基准情景必须有证据；乐观/悲观情景与基准并列展示。
- “做了敏感性分析就覆盖了模型风险” → 敏感性不能修复公式、币种、时间点或口径错误。
- “退出倍数沿用可比公司即可” → 先检查业务模式、市场、增长阶段与流动性差异，并保留折价依据。

## 输入

用户提供以下信息（缺失项会提示用户补充）：

| 类别 | 需要的数据 |
|------|-----------|
| 本轮条款 | 投资金额、投前/投后估值或初始持股比例、优先权条款 |
| 财务预测 | 未来 5 年收入、净利润；可补充市场预测及其与收入预测的换算关系 |
| 后续融资 | 每轮稀释率或足以计算稀释率的融资金额与投后估值；母版默认基金不跟投 |
| 退出假设 | 保守/中性/乐观三种退出情形的市盈率、市销率或绝对估值、退出年份 |

## 证据内核（必须）

从本 `SKILL.md` 的实际目录解析同级 `../jvc-research-core/scripts/researchctl.py`，并使用绝对路径执行；不要依赖当前工作目录。

执行前必须读取同级 `../jvc-research-core/references/evidence-contract.md` 和当前 profile `../jvc-research-core/profiles/jvc-roi-modeler.json`。

1. 新研究先准备完整 `scope` JSON，再运行 `init --skill jvc-roi-modeler --run-dir <研究目录> --scope-file <scope.json>`；初始 `scope` 只能通过 `init --scope-file` 创建。
2. 复用已有研究链时运行 `init --skill jvc-roi-modeler --run-dir <研究目录> --resume`。后续 `scope` 更正必须通过 `record --run-dir <研究目录> --input <records.jsonl>` 登记，并用 `supersedes` 指向当前 effective scope；问题、检索、来源、主张和更正也只能通过该命令登记，不得直接编辑 `evidence_registry.jsonl`，generic `record` 不得创建 waiver。
3. 跨 skill 消费已有主张时，在新主张的 `derived_from_claim_ids` 中登记上游主张编号；缺失或失效的上游审计会阻断下游完成。
4. 最终产物中的本阶段支持与反证来源统一写为 `[S编号]`；本 CSV 写入 `source_id`、`assumption_status` 和 `notes` 列，计算行与输入行不得混淆。
5. 完成现有产物生成与格式校验后，运行 `audit --run-dir <研究目录> --skill jvc-roi-modeler --artifact <最终产物>`；多文件产物重复传入 `--artifact`。每次 audit 必须同时读取命令退出状态和 `audit.json`。
6. 只有 status 为 `blocked`、findings 中唯一 block 是 `partial_label_missing`，且至少一个 finding 为 `partial` 时，才把 `model_status` 行的 `notes` 改为 `研究状态：partial`，不得改变表头和行项目；写回后必须先重新运行 CSV validator，再重跑 audit。存在其他 block 时不得用标签绕过。重跑得到 `partial` / exit `10` 才可 partial 交付；`ready` / exit `0` 才能称为完成；其他 `blocked` / exit `20` 只能交付证据缺口和下一步，不能形成受影响的判断；exit `1` 必须修复后重跑。
7. 只有用户明确批准、且 blocker 与同 skill 最新有效 blocked audit 精确匹配时，才可运行 `waive --run-dir <研究目录> --skill jvc-roi-modeler --rule <阻断规则> --reason <批准理由> --scope <批准范围> --approved-by <批准人> --residual-risk <剩余风险>`；不得自我批准，waiver 最多降级为 partial。

找不到内核、profile 不兼容、账本损坏或终审异常时，不得退回纯 prompt 模式。

本 skill 登记条款、预测和模型假设来源，保持已知条款与用户假设分离。

## 执行步骤

### 1. 读取模型合同并确认输入

先读取 `references/model-contract.md` 和仓库 `templates/roi-modeler-template.csv`。检查用户数据；缺失关键项时明确列出，不把母版示例值当作真实输入。年度标题可以随项目平移，但列数、三种退出情景和行项目保持不变。

### 2. 逐轮稀释计算

从本轮开始，按时间顺序计算每轮稀释率和轮后持股比例。母版只覆盖基金不跟投的情形；用户明确要求跟投时，先说明需要扩展持股公式和 validator，不得把新增投入只写入现金流而不调整持股。

### 3. 三情形退出计算

对保守/中性/乐观三种情形，分别计算：
- 退出时公司估值
- 投资人持有的股权价值
- 退出总回款和净收益（考虑优先权）
- MOIC（Multiple on Invested Capital，投入资本倍数，用于衡量总回款是投入资本的多少倍）
- 累计收益率
- IRR（Internal Rate of Return，内部收益率，用于按现金流时间衡量年化回报）

IRR 的终期现金流使用退出总回款；累计收益率使用净收益除以累计投入。两者不得混用。

### 4. 估值与情景检查

每列只指定一种主估值方法，另一种倍数只作交叉检查。三种退出情景构成默认敏感性；用户明确要求时才增加额外敏感性表。

### 5. 生成并校验 CSV

保持模板的固定列和固定行项目，替换所有示例输入并保留公式。最终文件命名：

```text
{项目}_jvc-roi-modeler_{YYYYMMDD}.csv
```

把 `SKILL_ROOT` 设为包含本 `SKILL.md` 的绝对目录，再运行：

```bash
python3 "$SKILL_ROOT/scripts/validate_csv.py" output/{项目}_jvc-roi-modeler_{YYYYMMDD}.csv
```

校验通过后再运行证据内核 audit。

## 输出

CSV（Comma-Separated Values，逗号分隔值，一种可由表格软件打开的纯文本表格格式）文件，保存到用户指定路径或当前目录。

## 硬约束

- 不用最终持股倒推，必须逐轮计算稀释
- 退出倍数、财务预测、后续融资假设必须有来源或标 `[用户假设]` / `[未核实]`
- 退出总回款、净收益、MOIC、累计收益率和 IRR 必须按模型合同相互勾稽
- 本版不处理基金后续跟投；出现跟投条款时停止套用母版并明确扩展需求
- 不输出未经要求的 Excel、多工作表模型或额外敏感性矩阵
- 不输出"值得投/不值得投"，只输出回报区间、驱动因素和敏感项
- 缺失关键输入时提示用户补充，不自行填充
- 中文输出
