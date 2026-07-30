---
name: jvc-roi-modeler
description: |
  投资回报模型：根据投资条款、财务预测、后续融资假设和退出情形，逐轮计算稀释并输出 MOIC/IRR 区间的 Excel 工作簿。
  Use when user says '/jvc-roi-modeler', '回报模型', 'ROI', 'IRR', '回报测算', '稀释计算', '退出测算'.
user_invocable: true
version: "2.0.0"
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

## 2.0 证据内核（必须）

从本 `SKILL.md` 的实际目录解析同级 `../jvc-research-core/scripts/researchctl.py`，并使用绝对路径执行；不要依赖当前工作目录。

执行前必须读取同级 `../jvc-research-core/references/evidence-contract.md` 和当前 profile `../jvc-research-core/profiles/jvc-roi-modeler.json`。

1. 新研究先准备完整 `scope` JSON，再运行 `init --skill jvc-roi-modeler --run-dir <研究目录> --scope-file <scope.json>`；初始 `scope` 只能通过 `init --scope-file` 创建。
2. 复用已有研究链时运行 `init --skill jvc-roi-modeler --run-dir <研究目录> --resume`。后续 `scope` 更正必须通过 `record --run-dir <研究目录> --input <records.jsonl>` 登记，并用 `supersedes` 指向当前 effective scope；问题、检索、来源、主张和更正也只能通过该命令登记，不得直接编辑 `evidence_registry.jsonl`，generic `record` 不得创建 waiver。
3. 跨 skill 消费已有主张时，在新主张的 `derived_from_claim_ids` 中登记上游主张编号；缺失或失效的上游审计会阻断下游完成。
4. 最终产物中的本阶段支持与反证来源统一写为 `[S编号]`；Markdown 写在对应主张后，工作簿写入 `sources` 表，DOCX 写入来源附注，多文件产物至少在 `evidence_index.md` 建立映射。
5. 完成现有产物生成与格式校验后，运行 `audit --run-dir <研究目录> --skill jvc-roi-modeler --artifact <最终产物>`；多文件产物重复传入 `--artifact`。每次 audit 必须同时读取命令退出状态和 `audit.json`。
6. 只有 status 为 `blocked`、findings 中唯一 block 是 `partial_label_missing`，且至少一个 finding 为 `partial` 时，才按产物补写 `研究状态：partial`：Markdown 写入标题与结论，XLSX 在 `sources` 表表头和列结构不变的前提下追加一条可见状态数据行，DOCX 写入首段与来源附注，多文件产物至少写入 `knowledge_tree.md` 与 `evidence_index.md`；任何类型写回标签后，必须先重新运行原有产物格式校验/validator，确认结构仍有效，再重跑 audit；存在其他 block 时不得用标签绕过。重跑得到 `partial` / exit `10` 才可 partial 交付；`ready` / exit `0` 才能称为完成；其他 `blocked` / exit `20` 只能交付证据缺口和下一步，不能形成受影响的判断；exit `1` 必须修复后重跑。
7. 只有用户明确批准、且 blocker 与同 skill 最新有效 blocked audit 精确匹配时，才可运行 `waive --run-dir <研究目录> --skill jvc-roi-modeler --rule <阻断规则> --reason <批准理由> --scope <批准范围> --approved-by <批准人> --residual-risk <剩余风险>`；不得自我批准，waiver 最多降级为 partial。

找不到内核、profile 不兼容、账本损坏或终审异常时，不得退回纯 prompt 模式。

本 skill 登记条款、预测和模型假设来源，保持已知条款与用户假设分离。

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
