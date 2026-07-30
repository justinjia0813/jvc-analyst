---
name: jvc-bear-case
description: |
  反向论证：扮演四种反方角色（挑剔LP/竞品CEO/怀疑论同行/IC boss），输出最锋利的不投理由，每条附可证伪条件。
  Use when user says '/jvc-bear-case', 'bear case', '反向论证', '为什么不投', '找茬', '风险分析', '帮我想想不投的理由'.
user_invocable: true
version: "3.0.0"
---

# /jvc-bear-case — 反向论证

系统性站在反方，写出最锋利的"为什么不该投"。

## 3.0 适用级别

最低适用级别：**L2+**（Level 2 or above，二级及以上尽调，用于验证关键假设）。

- 开始前读取已有 `spec/CONTEXT.md`、`spec/hypotheses.md`、`spec/tasks.md`、Bull Case 与证据索引。
- 当前项目低于 L2 时，先说明该 Skill 需要额外的反向检索与可证伪条件，由用户确认是否提前使用。
- Bear Case 是对抗性验证材料，不是对项目或创始人的终局判决。

## 反合理化约束

- “反方角色可以大胆猜测” → 可以提出假设，但必须标注 `[推测]`，并附可证伪条件。
- “风险听起来合理，不需要证据” → 每条风险至少引用具体材料、反证或历史类比；否则写为证据缺口。
- “为了锋利可以省略不确定性” → 只有 1–2 条信源时暂停并询问用户，不得自行形成对项目或创始人的不利判断。
- “没有找到反证，所以担忧成立” → 无结果只证明检索未命中，不证明风险成立。

## 输入

- 项目的现有分析材料（prescreen、尽调笔记、deck、bull-case 等）
- 可选：用户目前最犹豫的点

## 证据内核（必须）

从本 `SKILL.md` 的实际目录解析同级 `../jvc-research-core/scripts/researchctl.py`，并使用绝对路径执行；不要依赖当前工作目录。

执行前必须读取同级 `../jvc-research-core/references/evidence-contract.md` 和当前 profile `../jvc-research-core/profiles/jvc-bear-case.json`。

1. 新研究先准备完整 `scope` JSON，再运行 `init --skill jvc-bear-case --run-dir <研究目录> --scope-file <scope.json>`；初始 `scope` 只能通过 `init --scope-file` 创建。
2. 复用已有研究链时运行 `init --skill jvc-bear-case --run-dir <研究目录> --resume`。后续 `scope` 更正必须通过 `record --run-dir <研究目录> --input <records.jsonl>` 登记，并用 `supersedes` 指向当前 effective scope；问题、检索、来源、主张和更正也只能通过该命令登记，不得直接编辑 `evidence_registry.jsonl`，generic `record` 不得创建 waiver。
3. 跨 skill 消费已有主张时，在新主张的 `derived_from_claim_ids` 中登记上游主张编号；缺失或失效的上游审计会阻断下游完成。
4. 最终产物中的本阶段支持与反证来源统一写为 `[S编号]`；Markdown 写在对应主张后，工作簿写入 `sources` 表，DOCX 写入来源附注，多文件产物至少在 `evidence_index.md` 建立映射。
5. 完成现有产物生成与格式校验后，运行 `audit --run-dir <研究目录> --skill jvc-bear-case --artifact <最终产物>`；多文件产物重复传入 `--artifact`。每次 audit 必须同时读取命令退出状态和 `audit.json`。
6. 只有 status 为 `blocked`、findings 中唯一 block 是 `partial_label_missing`，且至少一个 finding 为 `partial` 时，才按产物补写 `研究状态：partial`：Markdown 写入标题与结论，XLSX 在 `sources` 表表头和列结构不变的前提下追加一条可见状态数据行，DOCX 写入首段与来源附注，多文件产物至少写入 `knowledge_tree.md` 与 `evidence_index.md`；任何类型写回标签后，必须先重新运行原有产物格式校验/validator，确认结构仍有效，再重跑 audit；存在其他 block 时不得用标签绕过。重跑得到 `partial` / exit `10` 才可 partial 交付；`ready` / exit `0` 才能称为完成；其他 `blocked` / exit `20` 只能交付证据缺口和下一步，不能形成受影响的判断；exit `1` 必须修复后重跑。
7. 只有用户明确批准、且 blocker 与同 skill 最新有效 blocked audit 精确匹配时，才可运行 `waive --run-dir <研究目录> --skill jvc-bear-case --rule <阻断规则> --reason <批准理由> --scope <批准范围> --approved-by <批准人> --residual-risk <剩余风险>`；不得自我批准，waiver 最多降级为 partial。

找不到内核、profile 不兼容、账本损坏或终审异常时，不得退回纯 prompt 模式。

本 skill 复用已有来源，登记反向问题、主张和可证伪条件，不把推测写成事实。

## 执行步骤

### 1. 阅读全部素材

通读用户提供的所有材料，识别正方论点和证据链。

### 2. 四角色攻击

分别扮演四种角色，每个角色写 1-3 条最锋利的论点：

**角色 A：挑剔 LP**
- 视角：基金组合层面的回报/风险比
- 核心问题：这个案子的预期回报能补偿它的尾部风险吗？在同赛道里有没有更好的选择？

**角色 B：竞品 CEO**
- 视角：竞争对手的进攻路线
- 核心问题：如果我是竞争对手，我怎么赢他？他的壁垒真的挡得住吗？他最怕什么？

**角色 C：怀疑论同行**
- 视角：历史类比和模式识别
- 核心问题：历史上类似的团队/市场/时机组合是怎么死的？这次有什么不同——"这次不同"的论点经得起检验吗？

**角色 D：IC boss**
- 视角：IP 法律风险、TAM/SAM 市场规模、大厂竞争、真正壁垒和价值点可靠性
- 核心问题：核心 IP 是否已转到公司旗下？整个市场 TAM/SAM 究竟是什么、规模有多少？大厂为什么不下场做这件事？大厂如果要做，卡点在哪里，初创公司的壁垒在哪里？公司究竟解决了什么难题、创造了什么价值？

### 3. 可证伪性标注

每条反对论点必须附「可证伪条件」：如果这条担忧不成立，需要什么具体证据来打消。这让 bear case 变成可行动的尽调清单，而不是空洞的悲观。

## 输出格式

Markdown 文档，结构：

```
## 角色 A：挑剔 LP
### 论点 1: {标题}
- 论据：...
- 可证伪条件：如果能证明 {X}，这条担忧可打消

## 角色 B：竞品 CEO
### 论点 N: {标题}

## 角色 C：怀疑论同行
### 论点 N: {标题}

## 角色 D：IC boss
### 论点 N: {标题}

## 综合：如果只能带走一条担忧
（从所有论点中选出最致命的一条，一句话概括）
```

## 硬约束

- **不做平衡**——这个环节的任务就是找茬，不需要"但另一方面"
- 每条论点必须附具体论据或历史类比，不写空泛的"存在风险"
- 不用"可能"、"也许"模糊其辞——要么能说出具体担忧，要么不写
- 至少输出 4 条不同维度的反对论点，四个角色都必须覆盖
- IC boss 角色必须至少覆盖 IP 归属、TAM/SAM 口径、大厂竞争、壁垒/价值点四类问题中的两类
- 中文输出
