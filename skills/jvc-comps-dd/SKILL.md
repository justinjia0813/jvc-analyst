---
name: jvc-comps-dd
description: |
  竞品尽调：调研目标项目的竞争对手和可比公司，输出包含上市公司和初创公司对比的 Excel 工作簿。
  Use when user says '/jvc-comps-dd', '竞品分析', 'comps', '可比公司', '竞争对手调研', '帮我看看竞品'.
user_invocable: true
version: "3.0.0"
---

# /jvc-comps-dd — 竞品尽调

系统调研目标项目面对哪些竞争者和可比公司，输出结构化 Excel。

## 3.0 适用级别

最低适用级别：**L2+**（Level 2 or above，二级及以上尽调，用于验证关键假设）。

- 开始前读取 `spec/CONTEXT.md` 中的竞品分类与比较口径，以及 `spec/hypotheses.md` 中关联假设。
- 当前项目低于 L2 时，先说明完整竞品尽调的来源覆盖与客户验证成本，由用户确认是否提前使用。
- 工作簿进入 `05-comps-dd.xlsx`；来源、覆盖缺口和对比口径不得因级别裁剪。

## 反合理化约束

- “公开资料足够代表产品实力” → 公开资料是发布方选择呈现的内容；与客户侧验证分列。
- “没有搜到竞品，所以没有竞品” → 记录检索范围和无结果原因，不把搜索缺口写成市场结论。
- “数据缺失可以留 0 方便计算” → 未披露写 `N/A` 或 `[未核实]`；零必须有来源证明。
- “相似公司可以直接当可比” → 明确直接竞品、替代方案、上下游和参照标的，不能混算。

## 输入

- 目标项目或细分赛道
- 可选：已知竞品名单、`/jvc-track-research` 产出、关注地区

## 证据内核（必须）

从本 `SKILL.md` 的实际目录解析同级 `../jvc-research-core/scripts/researchctl.py`，并使用绝对路径执行；不要依赖当前工作目录。

执行前必须读取同级 `../jvc-research-core/references/evidence-contract.md` 和当前 profile `../jvc-research-core/profiles/jvc-comps-dd.json`。

1. 新研究先准备完整 `scope` JSON，再运行 `init --skill jvc-comps-dd --run-dir <研究目录> --scope-file <scope.json>`；初始 `scope` 只能通过 `init --scope-file` 创建。
2. 复用已有研究链时运行 `init --skill jvc-comps-dd --run-dir <研究目录> --resume`。后续 `scope` 更正必须通过 `record --run-dir <研究目录> --input <records.jsonl>` 登记，并用 `supersedes` 指向当前 effective scope；问题、检索、来源、主张和更正也只能通过该命令登记，不得直接编辑 `evidence_registry.jsonl`，generic `record` 不得创建 waiver。
3. 跨 skill 消费已有主张时，在新主张的 `derived_from_claim_ids` 中登记上游主张编号；缺失或失效的上游审计会阻断下游完成。
4. 最终产物中的本阶段支持与反证来源统一写为 `[S编号]`；Markdown 写在对应主张后，工作簿写入 `sources` 表，DOCX 写入来源附注，多文件产物至少在 `evidence_index.md` 建立映射。
5. 完成现有产物生成与格式校验后，运行 `audit --run-dir <研究目录> --skill jvc-comps-dd --artifact <最终产物>`；多文件产物重复传入 `--artifact`。每次 audit 必须同时读取命令退出状态和 `audit.json`。
6. 只有 status 为 `blocked`、findings 中唯一 block 是 `partial_label_missing`，且至少一个 finding 为 `partial` 时，才按产物补写 `研究状态：partial`：Markdown 写入标题与结论，XLSX 在 `sources` 表表头和列结构不变的前提下追加一条可见状态数据行，DOCX 写入首段与来源附注，多文件产物至少写入 `knowledge_tree.md` 与 `evidence_index.md`；任何类型写回标签后，必须先重新运行原有产物格式校验/validator，确认结构仍有效，再重跑 audit；存在其他 block 时不得用标签绕过。重跑得到 `partial` / exit `10` 才可 partial 交付；`ready` / exit `0` 才能称为完成；其他 `blocked` / exit `20` 只能交付证据缺口和下一步，不能形成受影响的判断；exit `1` 必须修复后重跑。
7. 只有用户明确批准、且 blocker 与同 skill 最新有效 blocked audit 精确匹配时，才可运行 `waive --run-dir <研究目录> --skill jvc-comps-dd --rule <阻断规则> --reason <批准理由> --scope <批准范围> --approved-by <批准人> --residual-risk <剩余风险>`；不得自我批准，waiver 最多降级为 partial。

找不到内核、profile 不兼容、账本损坏或终审异常时，不得退回纯 prompt 模式。

本 skill 必须登记公司字段级主张、来源日期、估值或市值口径及反向证据。

## 执行步骤

### 1. 联网搜索

搜集公开信息，国内为主、海外龙头为辅。同时覆盖上市公司和初创公司。

### 2. 分类

将找到的公司分为四类：
- **直接竞品**：同赛道、同客群、正面竞争
- **可比公司**：相似商业模式或技术路线，但不同细分
- **上下游参照**：产业链上相关公司
- **海外标杆**：海外同赛道的龙头或对标公司

### 3. 信息收集

每家公司尽量覆盖以下字段（缺失标 `[未披露]`）：

| 字段 | 说明 |
|------|------|
| 公司名称 | 中文名（英文名） |
| 国家/地区 | |
| 分类 | 直接竞品/可比/上下游/海外标杆 |
| 技术路线 | 核心技术方案 |
| 核心产品 | 主要产品或服务 |
| 目标客群 | |
| 差异化定位 | 一句话区分 |
| 成立时间 | |
| 融资阶段 | 最新轮次 |
| 最近一年收入 | 标注口径和来源 |
| 最新估值/市值 | 标注日期和来源 |

### 4. 生成 Excel

先用仓库内 workbook 模板脚本生成 `.xlsx` 文件：

```bash
python3 scripts/generate-workbook.py templates/comps-dd-template.md output/{项目或赛道}_jvc-comps-dd_{YYYYMMDD}.xlsx
```

填完调研结果后运行结构校验：

```bash
python3 scripts/validate-workbook.py output/{项目或赛道}_jvc-comps-dd_{YYYYMMDD}.xlsx templates/comps-dd-template.md
```

Workbook 包含以下 sheet：

- **companies**：主表，上述所有字段
- **segmentation**：按分类分组的简要对比
- **sources**：所有数据来源的汇总（公司、字段、来源、日期）
- **coverage_notes**：本次调研的覆盖范围、局限性、建议补充方向

## 输出

Excel 文件（`.xlsx`），保存到用户指定路径或当前目录。

## 硬约束

- 最近一年收入、最新估值、市值必须标来源和日期
- 上市公司市值和初创公司融资估值不得混为同一口径
- 找不到数据标 `[未披露]` 或 `[未核实]`，不补数字
- 不编造融资金额、收入、估值
- 中文输出
