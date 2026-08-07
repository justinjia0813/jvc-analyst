---
name: jvc-ic-memo
description: |
  投决备忘录：汇总所有前序素材，按十七章标准结构合成 IC memo 初稿。风险篇幅不少于投资逻辑篇幅。
  Use when user says '/jvc-ic-memo', 'IC memo', '投决备忘录', '写memo', '出memo', '投委会材料'.
user_invocable: true
version: "4.0.0"
---

# /jvc-ic-memo — 投决备忘录（v4.0 · 十七章工程化模板）

汇总所有前序 JVC skill 产出和原始素材，按标准化模板合成 IC memo 初稿。

运行前**必须**读取本 skill 目录下的 `references/ic-memo-template.md`——它是每个章节的结构定义、内容标准、数据要求和质量门控的唯一权威来源。本文件定义生产流程和 skill 映射；模板定义内容规范。两者配合使用。

## 适用级别

最低适用级别：**L3**（重仓、领投或投决会前研究）。

- 开始前读取 `spec/CONTEXT.md`、`spec/hypotheses.md`、`spec/tasks.md`、Bull/Bear Case、模型、证据索引和 `STATE.md`。
- 项目低于 L3 时，先列出尚缺的 IC 前工件和关键证据，由用户确认是否只生成明确标注不完整的草稿。
- Memo 只整理证据、分歧和待决事项；`decision-journal.md` 由人在做出决定时立案，本 Skill 不代写终局判断。

## 反合理化约束

- "前序材料已经很多，可以直接合成" → 数量不等于覆盖；先核对关键假设、反证、来源与未解决冲突。
- "为了让 memo 完整可以补齐空白" → 不编造；缺口留在待决事项并标明责任人或下一步。
- "风险会削弱投资逻辑，可以压缩" → 风险篇幅不得短于投资亮点，反面证据不得移到附件隐藏。
- "IC memo 需要明确推荐" → AI 不写建议投资/不建议投资，只呈现条件、证据和未决问题。

---

## 五阶段生产流程

### Phase 1: 素材准备与清点

读取项目目录下的所有可用素材，按下方「JVC Skill 产出到模板章节映射表」逐章标记：✅ 已有 / ⚠️ 部分可用 / ❌ 缺失。

向用户输出素材清点表，格式：

```
素材清点结果（[项目名]）

| 模板章节 | 需要的 JVC skill 产出 | 状态 | 备注 |
|---------|---------------------|------|------|
| 1. 执行摘要 | prescreen / roi-modeler / deal-flow | ✅/⚠️/❌ | ... |
| ... | ... | ... | ... |

❌ 缺失项（共 x 项）：
- [列出缺失项及其对 memo 质量的影响]
- [建议用户先运行哪些 skill]

是否继续？缺失章节将标注「此部分缺少输入素材」。
```

等待用户确认后进入 Phase 2。不阻塞——有多少用多少。

### Phase 2: 骨架搭建

1. 读取 `references/ic-memo-template.md` 获取完整结构
2. 填写执行摘要的交易概要部分（先锚定核心数字）
3. 列出各章节的关键论点骨架（每章 3–5 个要点），向用户展示骨架供确认
4. 用户确认或调整骨架后进入 Phase 3

### Phase 3: 逐章填充

按依赖顺序分层填充，严格遵循模板中每章的结构规范和数据要求：

```
行业层（不依赖公司数据）：
  4. 行业概况 → 5. 市场规模 → 6. 产业链分析 → 7. 竞争格局

公司层（不依赖判断）：
  8. 公司概况 → 9. 产品矩阵 → 10. 核心团队 → 11. 核心壁垒 → 12. 主要客户

判断层（依赖行业层 + 公司层）：
  2. 投资亮点 → 3. 投资风险

估值层（依赖判断层 + 公司层）：
  14. 收入预测模型 → 15. 可比公司 → 16. 投资回报模型 → 13. Cap Table

汇总层：
  17. 交易-收益测算总结 → 1. 执行摘要（回写）
```

### Phase 4: 质量门控

完成全文后，执行三轮校验：

**第一轮：章节级质量门控**
逐章执行模板中定义的质量门控 checklist（每章末尾的 `[ ]` 项）。未通过的项标记为 `❌ 未通过: [原因]`，汇总后向用户报告。

**第二轮：数据一致性校验**
按模板附录「数据一致性校验清单」逐项核对：

| 数据点 | 涉及章节 | 校验方法 |
|--------|---------|---------|
| 收入数据 | 执行摘要 ↔ 收入预测模型 | 直接比对 |
| 净利润数据 | 执行摘要 ↔ 收入预测模型 ↔ 投资回报模型 | 直接比对 |
| 估值/融资金额 | 执行摘要 ↔ Cap Table ↔ 投资回报模型 ↔ 交易总结 | 直接比对 |
| 回报倍数 | 执行摘要 ↔ 投资回报模型 ↔ 交易总结 | 直接比对 |
| 市场规模 | 市场规模 ↔ 行业概况 | 交叉引用 |
| 竞品数据 | 竞争格局 ↔ 可比公司 | 数据源一致 |
| 客户数据 | 主要客户 ↔ 收入预测模型 | 逻辑一致 |
| 持股比例 | 核心团队 ↔ Cap Table | 直接比对 |
| 产品结构 | 产品矩阵 ↔ 收入预测模型 | 产品线对应 |

不一致的数据点在 memo 末尾「质量报告」中列出，标明来源冲突，请用户裁定。

**第三轮：全局硬约束检查**
- [ ] 风险章节（第 3 章）字数 ≥ 亮点章节（第 2 章）字数
- [ ] 风险条数 ≥ 亮点条数
- [ ] 至少有一条风险涉及估值/退出
- [ ] 每条风险有量化影响评估
- [ ] 所有数字可追溯到素材来源——无来源的标 `[未核实]` 或 `[需要用户提供]`
- [ ] 不出现没有证据的修饰词（"领先的"、"颠覆性的"、"赋能"、"护城河"等）
- [ ] 不出现 "建议投资" / "不建议投资" 等终局判断
- [ ] 口径说明完整（收入含税/不含税、人民币/美元）
- [ ] 缺失素材的章节有显式标注
- [ ] 术语首次出现附中文解释

### Phase 5: 终稿组装

1. 修复 Phase 4 发现的问题（数据不一致需用户裁定的除外）
2. 组装完整 Markdown 终稿
3. 在终稿末尾附「质量报告」：通过/未通过的门控项、待用户裁定的数据冲突、未覆盖的章节
4. 输出文件名：`IC Memo - [公司简称] - [日期].md`

---

## JVC Skill 产出到模板章节映射表

| 模板章节 | 主要来源 skill | 次要来源 | 映射说明 |
|---------|--------------|---------|---------|
| 1. 执行摘要 | roi-modeler (`investment_terms`, `returns`) | prescreen (事实摘要), deal-flow (`DATA_LAYER.md`) | 全文最后回写；交易参数从 roi-modeler 取，业务简介从 prescreen 取 |
| 2. 投资亮点 | bull-case (四层结构) | track-research (行业趋势), meeting-notes (商业化数据) | bull-case 每条亮点直接对应一个投资论点；补充模板要求的6个维度覆盖检查 |
| 3. 投资风险 | bear-case (四角色反驳) | prescreen (bear case雏形), track-research (政策风险) | bear-case 论点重组为模板的6类风险维度；每条补充量化影响和缓释措施 |
| 4. 行业概况 | track-research (A 行业定义, B 简史, E 趋势) | — | 直接映射；用模板的 Where/Go/Path 三问结构重组 |
| 5. 市场规模 | market-sizing (`top_down`, `bottom_up`, `reconciliation`) | track-research (市场数据) | Excel 各 sheet 直接对应模板的 Bottom-up/Top-down/对比/Driver 结构 |
| 6. 产业链分析 | track-research (D 产业链图谱) | — | 直接映射；补充标的位置标记和议价能力判断 |
| 7. 竞争格局 | comps-dd (`companies`, `segmentation`) | track-research (F 关键玩家分层) | comps-dd 数据填入竞品对比表；track-research 提供格局演变叙事 |
| 8. 公司概况 | prescreen (事实摘要表格) | meeting-notes (六段式), deck | prescreen 的基础信息 + meeting-notes 的里程碑 |
| 9. 产品矩阵 | meeting-notes (核心产品段) | talk-notes (客户反馈), deck | meeting-notes 的产品信息 + talk-notes 的客户视角 |
| 10. 核心团队 | meeting-notes (核心团队段) | prescreen (创始人信息), deck | meeting-notes 的团队详情 + 模板要求的4个判断点 |
| 11. 核心壁垒 | bull-case (技术/商业化亮点) | track-research (技术路线), meeting-notes (技术段) | 从 bull-case 提取壁垒相关亮点，用模板的壁垒类型清单重组 |
| 12. 主要客户 | meeting-notes (商业化段) | talk-notes (客户访谈), deck | meeting-notes 的客户数据 + talk-notes 的客户反馈 |
| 13. Cap Table | roi-modeler (`investment_terms`, `financing_dilution`, `ownership`) | deal-flow, deck | roi-modeler 的条款和稀释数据 + 模板要求的保护性条款清单 |
| 14. 收入预测模型 | roi-modeler (`financial_forecast`) | meeting-notes (收入数据), market-sizing (渗透率) | roi-modeler 的预测 + 模板要求的量×价拆分和敏感性分析 |
| 15. 可比公司 | comps-dd (`companies` 中上市公司) | — | comps-dd 提取上市可比公司，按模板的估值倍数表重组 |
| 16. 投资回报模型 | roi-modeler (`exit_scenarios`, `returns`, `sensitivity`) | comps-dd (退出 PE 参照) | roi-modeler 各 sheet 直接对应模板的三种情景 + 稀释假设 |
| 17. 交易-收益测算总结 | roi-modeler (`returns`) | comps-dd (估值锚) | 最终浓缩页；加权回报用 roi-modeler 计算 |

**读取优先级**：deal-flow 的 `DATA_LAYER.md` / `INVEST_MEMO.md` / `INSIGHT_LAYER.md` > 各 skill 原始产出 > deck 等原始素材 > 用户口头补充。

---

## 十七章结构速览

每章的详细结构定义、模板代码块、质量门控清单见 `references/ic-memo-template.md`。以下仅列章节名称和定位：

| # | 章节 | 一句话定位 |
|---|------|----------|
| 1 | 执行摘要 | IC 委员 30 秒抓住核心信息的入口（最后写、最先读） |
| 2 | 投资亮点 | 回答「为什么要投」——每条 = 一个独立投资论点 |
| 3 | 投资风险 | 回答「为什么不投 / 投了可能亏在哪」——篇幅 ≥ 亮点 |
| 4 | 行业概况 | IC 委员 2 分钟建立行业认知框架 |
| 5 | 市场规模 | 回答「这个生意能做多大」——Bottom-up + Top-down 双验证 |
| 6 | 产业链分析 | 回答「价值如何分配，标的卡在什么位置」 |
| 7 | 竞争格局 | 回答「标的在同行中排第几，靠什么赢」 |
| 8 | 公司概况 | 标的公司快照（简洁完整，不展开分析） |
| 9 | 产品矩阵 | 回答「靠什么挣钱，产品之间什么关系」 |
| 10 | 核心团队 | 回答「这帮人能不能把事做成」 |
| 11 | 核心壁垒 | 回答「别人为什么做不了同样的事」 |
| 12 | 主要客户 | 回答「谁在买单，付费意愿和能力如何」 |
| 13 | Cap Table | 回答「股权怎么分的，条款怎么保护我们」 |
| 14 | 收入预测模型 | 回答「未来 3–5 年能赚多少钱」——量 × 价，非拍增速 |
| 15 | 可比公司 | 回答「市场给类似公司什么估值」 |
| 16 | 投资回报模型 | 回答「华胥投了能赚多少倍」——三种情景 + 稀释 |
| 17 | 交易-收益测算总结 | 全文最后的决策浓缩——一页纸让 IC 委员做判断 |

---

## 证据内核（必须）

从本 `SKILL.md` 的实际目录解析同级 `../jvc-research-core/scripts/researchctl.py`，并使用绝对路径执行；不要依赖当前工作目录。

执行前必须读取同级 `../jvc-research-core/references/evidence-contract.md` 和当前 profile `../jvc-research-core/profiles/jvc-ic-memo.json`。

1. 新研究先准备完整 `scope` JSON，再运行 `init --skill jvc-ic-memo --run-dir <研究目录> --scope-file <scope.json>`；初始 `scope` 只能通过 `init --scope-file` 创建。
2. 复用已有研究链时运行 `init --skill jvc-ic-memo --run-dir <研究目录> --resume`。后续 `scope` 更正必须通过 `record --run-dir <研究目录> --input <records.jsonl>` 登记，并用 `supersedes` 指向当前 effective scope；问题、检索、来源、主张和更正也只能通过该命令登记，不得直接编辑 `evidence_registry.jsonl`，generic `record` 不得创建 waiver。
3. 跨 skill 消费已有主张时，在新主张的 `derived_from_claim_ids` 中登记上游主张编号；缺失或失效的上游审计会阻断下游完成。
4. 最终产物中的本阶段支持与反证来源统一写为 `[S编号]`；Markdown 写在对应主张后，工作簿写入 `sources` 表，DOCX 写入来源附注，多文件产物至少在 `evidence_index.md` 建立映射。
5. 完成现有产物生成与格式校验后，运行 `audit --run-dir <研究目录> --skill jvc-ic-memo --artifact <最终产物>`；多文件产物重复传入 `--artifact`。每次 audit 必须同时读取命令退出状态和 `audit.json`。
6. 只有 status 为 `blocked`、findings 中唯一 block 是 `partial_label_missing`，且至少一个 finding 为 `partial` 时，才按产物补写 `研究状态：partial`：Markdown 写入标题与结论，XLSX 在 `sources` 表表头和列结构不变的前提下追加一条可见状态数据行，DOCX 写入首段与来源附注，多文件产物至少写入 `knowledge_tree.md` 与 `evidence_index.md`；任何类型写回标签后，必须先重新运行原有产物格式校验/validator，确认结构仍有效，再重跑 audit；存在其他 block 时不得用标签绕过。重跑得到 `partial` / exit `10` 才可 partial 交付；`ready` / exit `0` 才能称为完成；其他 `blocked` / exit `20` 只能交付证据缺口和下一步，不能形成受影响的判断；exit `1` 必须修复后重跑。
7. 只有用户明确批准、且 blocker 与同 skill 最新有效 blocked audit 精确匹配时，才可运行 `waive --run-dir <研究目录> --skill jvc-ic-memo --rule <阻断规则> --reason <批准理由> --scope <批准范围> --approved-by <批准人> --residual-risk <剩余风险>`；不得自我批准，waiver 最多降级为 partial。

找不到内核、profile 不兼容、账本损坏或终审异常时，不得退回纯 prompt 模式。

本 skill 只消费有效审查记录；新增事实必须先登记，不能在 memo 中补造来源。

---

## 执行步骤

### Step 1: 读取模板

读取 `references/ic-memo-template.md`，加载所有章节的结构定义和质量门控清单。

### Step 2: 素材准备（Phase 1）

1. 扫描项目目录，识别已有的 JVC skill 产出（按映射表匹配）
2. 读取 deal-flow 的 `STATE.md` 了解项目当前阶段
3. 如有 `DATA_LAYER.md` / `INVEST_MEMO.md` / `INSIGHT_LAYER.md`，优先读取
4. 输出素材清点表，等待用户确认

### Step 3: 骨架搭建（Phase 2）

1. 锚定交易核心参数（估值、金额、轮次）
2. 各章列出关键论点骨架
3. 向用户展示骨架，等待确认或调整

### Step 4: 逐章填充（Phase 3）

按依赖顺序（行业层 → 公司层 → 判断层 → 估值层 → 汇总层）逐章填充。

每章填充时：
- 先读取映射表中对应的 skill 产出
- 按模板中该章的结构规范组织内容
- 事实陈述后标注来源类型：`[deck p.x]` / `[创始人自述]` / `[行业报告: xxx]` / `[S编号]` / `[推测]` / `[未核实]`
- 缺失数据标注 `[需要用户提供]` 或 `待确认 ⚠️`

### Step 5: 质量门控（Phase 4）

执行三轮校验（章节级 → 数据一致性 → 全局硬约束），汇总结果。

### Step 6: 终稿组装（Phase 5）

组装终稿 + 质量报告。

---

## 输出格式

Markdown 文档，十七章结构 + 质量报告附录。

文件名：`IC Memo - [公司简称] - [YYYY-MM-DD].md`

文件结构：

```
# IC Memo — [公司全称]

> 生成日期：[日期] | 研究级别：L3 | 素材覆盖：[x/17 章完整]
> ⚠️ 本文件为 AI 辅助生成的初稿，所有判断和数据需经投资经理核实。

---

## 1. 执行摘要
...（按模板结构）

## 2. 投资亮点
...

## 3. 投资风险
...

[4–17 章]

---

## 附录：质量报告

### 章节级门控结果
| 章节 | 通过/未通过 | 未通过项 |
| ... | ... | ... |

### 数据一致性校验
| 数据点 | 章节A值 | 章节B值 | 状态 |
| ... | ... | ... | ✅/❌ |

### 待用户裁定事项
- [列出需要用户判断的数据冲突或信息缺口]

### 未覆盖章节
- [列出因素材缺失而未完整填充的章节]
```

## 硬约束

- 投资风险（第 3 章）篇幅 ≥ 投资亮点（第 2 章）
- 风险条数 ≥ 亮点条数
- 所有数字可追溯到素材来源
- 不出现没有证据的修饰词
- **不出现 "建议投资" / "不建议投资" 等终局判断**
- 缺失素材在对应章节显式标注
- 中文输出，术语首次出现附中文解释
- 同一数据全文统一口径
- 执行摘要最后写（Phase 5 回写）
