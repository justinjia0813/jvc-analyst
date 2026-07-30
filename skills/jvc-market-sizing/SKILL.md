---
name: jvc-market-sizing
description: |
  市场规模建模：针对细分赛道同时建立自上而下和自下而上两套 TAM/SAM/SOM 模型，输出 Excel 工作簿。
  Use when user says '/jvc-market-sizing', '市场规模', 'market sizing', 'TAM', '市场有多大', '规模测算'.
user_invocable: true
version: "2.0.0"
---

# /jvc-market-sizing — 市场规模建模

针对细分赛道估算 TAM（总可及市场）/SAM（可服务市场）/SOM（可获得市场），拆成可复核的模型。

## 输入

- 细分赛道定义、地域范围、目标客户、应用场景
- 可选：`/jvc-track-research`、`/jvc-comps-dd` 产出、用户已有假设

## 2.0 证据内核（必须）

从本 `SKILL.md` 的实际目录解析同级 `../jvc-research-core/scripts/researchctl.py`，并使用绝对路径执行；不要依赖当前工作目录。

执行前必须读取同级 `../jvc-research-core/references/evidence-contract.md` 和当前 profile `../jvc-research-core/profiles/jvc-market-sizing.json`。

1. 新研究先准备完整 `scope` JSON，再运行 `init --skill jvc-market-sizing --run-dir <研究目录> --scope-file <scope.json>`；初始 `scope` 只能通过 `init --scope-file` 创建。
2. 复用已有研究链时运行 `init --skill jvc-market-sizing --run-dir <研究目录> --resume`。后续 `scope` 更正必须通过 `record --run-dir <研究目录> --input <records.jsonl>` 登记，并用 `supersedes` 指向当前 effective scope；问题、检索、来源、主张和更正也只能通过该命令登记，不得直接编辑 `evidence_registry.jsonl`，generic `record` 不得创建 waiver。
3. 跨 skill 消费已有主张时，在新主张的 `derived_from_claim_ids` 中登记上游主张编号；缺失或失效的上游审计会阻断下游完成。
4. 最终产物中的本阶段支持与反证来源统一写为 `[S编号]`；Markdown 写在对应主张后，工作簿写入 `sources` 表，DOCX 写入来源附注，多文件产物至少在 `evidence_index.md` 建立映射。
5. 完成现有产物生成与格式校验后，运行 `audit --run-dir <研究目录> --skill jvc-market-sizing --artifact <最终产物>`；多文件产物重复传入 `--artifact`。每次 audit 必须同时读取命令退出状态和 `audit.json`。
6. 只有 status 为 `blocked`、findings 中唯一 block 是 `partial_label_missing`，且至少一个 finding 为 `partial` 时，才按产物补写 `研究状态：partial`：Markdown 写入标题与结论，XLSX 在 `sources` 表表头和列结构不变的前提下追加一条可见状态数据行，DOCX 写入首段与来源附注，多文件产物至少写入 `knowledge_tree.md` 与 `evidence_index.md`；任何类型写回标签后，必须先重新运行原有产物格式校验/validator，确认结构仍有效，再重跑 audit；存在其他 block 时不得用标签绕过。重跑得到 `partial` / exit `10` 才可 partial 交付；`ready` / exit `0` 才能称为完成；其他 `blocked` / exit `20` 只能交付证据缺口和下一步，不能形成受影响的判断；exit `1` 必须修复后重跑。
7. 只有用户明确批准、且 blocker 与同 skill 最新有效 blocked audit 精确匹配时，才可运行 `waive --run-dir <研究目录> --skill jvc-market-sizing --rule <阻断规则> --reason <批准理由> --scope <批准范围> --approved-by <批准人> --residual-risk <剩余风险>`；不得自我批准，waiver 最多降级为 partial。

找不到内核、profile 不兼容、账本损坏或终审异常时，不得退回纯 prompt 模式。

本 skill 必须把外部事实、用户假设和模型估算分开登记。

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
