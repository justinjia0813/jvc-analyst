---
name: jvc-ic-memo
description: |
  投决备忘录：汇总所有前序素材，按十段式标准结构合成 IC memo 初稿。风险篇幅不少于投资逻辑篇幅。
  Use when user says '/jvc-ic-memo', 'IC memo', '投决备忘录', '写memo', '出memo', '投委会材料'.
user_invocable: true
version: "3.0.0"
---

# /jvc-ic-memo — 投决备忘录

汇总所有素材，合成一份正式的 IC memo 初稿供用户修改。

## 3.0 适用级别

最低适用级别：**L3**（Level 3，三级深度尽调，用于重仓、领投或投决会前研究）。

- 开始前读取 `spec/CONTEXT.md`、`spec/hypotheses.md`、`spec/tasks.md`、Bull/Bear Case、模型、证据索引和 `STATE.md`。
- 项目低于 L3 时，先列出尚缺的 IC（Investment Committee，投资决策委员会，负责审议投资项目）前工件和关键证据，由用户确认是否只生成明确标注不完整的草稿。
- Memo 只整理证据、分歧和待决事项；`decision-journal.md` 由人在做出决定时立案，本 Skill 不代写终局判断。

## 反合理化约束

- “前序材料已经很多，可以直接合成” → 数量不等于覆盖；先核对关键假设、反证、来源与未解决冲突。
- “为了让 memo 完整可以补齐空白” → 不编造；缺口留在待决事项并标明责任人或下一步。
- “风险会削弱投资逻辑，可以压缩” → 风险篇幅不得短于投资逻辑，反面证据不得移到附件隐藏。
- “IC memo 需要明确推荐” → AI 不写建议投资/不建议投资，只呈现条件、证据和未决问题。

## 输入

- 项目相关的所有素材（deck、prescreen、尽调笔记、bull-case、bear-case、背调、赛道研究、comps、market-sizing、roi-model 等）
- 用户的核心投资逻辑（几句话即可，LLM 来展开和补充论据）

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

## 执行步骤

### 1. 素材清点

先列出手头有哪些素材、哪些环节还缺，告知用户。不阻塞——有多少用多少，缺失部分在 memo 中标注「此部分缺少输入素材」。

### 2. 按十段结构合成

| # | 章节 | 内容 |
|---|------|------|
| 1 | 交易摘要 | 一段话：这是什么、要多少钱、估值多少、用来做什么 |
| 2 | 公司概况 | 成立时间、阶段、核心数据、里程碑 |
| 3 | 市场与竞争 | 引用赛道研究和 comps，定位公司在图谱中的位置 |
| 4 | 产品与技术 | 做什么、怎么做、壁垒在哪 |
| 5 | 团队 | 核心人背景、为什么是他们、团队缺什么 |
| 6 | 财务与单位经济 | 已有数据 + 关键假设，引用 market-sizing 和 roi-model |
| 7 | 投资逻辑 | 用户给的核心逻辑 + LLM 补充的论据，引用 bull-case |
| 8 | 风险与反方观点 | 直接引用 bear-case 产出，补充 memo 视角的风险 |
| 9 | 估值与条款 | 摆事实（可比估值、历史轮次、ROI 模型结果），不下结论 |
| 10 | 待决事项 | 还缺什么信息、还有什么需要投决会讨论 |

### 3. 篇幅检查

写完后检查：第 8 章「风险与反方观点」的篇幅是否不少于第 7 章「投资逻辑」。如果不够，补充。

### 4. 来源追溯检查

逐段检查所有数字和事实是否有来源标注。无来源的标 `[未核实]` 或 `[需要用户提供]`。

## 输出格式

Markdown 文档，按上述十段结构。每段之间用 `---` 分隔。

## 硬约束

- 「风险与反方观点」篇幅不少于「投资逻辑」
- 所有数字可追溯到素材来源
- 不出现没有证据的修饰词（"领先的"、"颠覆性的"等）
- **不出现"建议投资"/"不建议投资"等终局判断**——memo 是决策材料，不是决策本身
- 缺失素材在对应章节显式标注，不用模糊语言掩盖
- 中文输出，术语首次出现附中文解释
