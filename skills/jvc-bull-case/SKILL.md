---
name: jvc-bull-case
description: |
  投资亮点提炼：从项目素材中按四个层面（行业趋势/技术节点/团队优势/商业化进展）提炼投资亮点，每条附论据和待验证项。
  Use when user says '/jvc-bull-case', '投资亮点', 'bull case', '为什么投', '亮点分析', '写bull case'.
user_invocable: true
version: "3.0.0"
---

# /jvc-bull-case — 投资亮点

从项目素材中提炼"为什么值得认真看"的正向论点，压成投决会可讨论的结构。

## 3.0 适用级别

最低适用级别：**L2+**（Level 2 or above，二级及以上尽调，用于验证关键假设）。

- 开始前读取已有 `spec/CONTEXT.md`、`spec/hypotheses.md`、`spec/tasks.md` 和证据索引；缺失时显式列出，不代建空文件。
- 当前项目低于 L2 时，先说明该 Skill 会增加正向论证与证据核验成本，由用户确认是否提前使用。
- Bull Case 只建立可验证正向论点，不改变项目级别，也不代替用户判断。

## 反合理化约束

- “公司材料重复提到，所以已被证明” → 同源重复只算一个公司口径，不能当作独立验证。
- “这是 Bull Case，不必写反证” → 每条亮点仍须写最需要补的反证或证伪材料。
- “商业化趋势很好” → 拆成收入、客户、合同或管线的具体事实；没有数字和来源就放入待验证亮点。
- “为了主线清晰可以略去冲突证据” → 冲突证据必须保留并说明它影响哪条亮点。

## 输入

用户提供以下任意组合：
- deck、prescreen、访谈纪要、客户反馈、公开资料
- 可选：用户已有的正向直觉或想强调的投资主线

## 证据内核（必须）

从本 `SKILL.md` 的实际目录解析同级 `../jvc-research-core/scripts/researchctl.py`，并使用绝对路径执行；不要依赖当前工作目录。

执行前必须读取同级 `../jvc-research-core/references/evidence-contract.md` 和当前 profile `../jvc-research-core/profiles/jvc-bull-case.json`。

1. 新研究先准备完整 `scope` JSON，再运行 `init --skill jvc-bull-case --run-dir <研究目录> --scope-file <scope.json>`；初始 `scope` 只能通过 `init --scope-file` 创建。
2. 复用已有研究链时运行 `init --skill jvc-bull-case --run-dir <研究目录> --resume`。后续 `scope` 更正必须通过 `record --run-dir <研究目录> --input <records.jsonl>` 登记，并用 `supersedes` 指向当前 effective scope；问题、检索、来源、主张和更正也只能通过该命令登记，不得直接编辑 `evidence_registry.jsonl`，generic `record` 不得创建 waiver。
3. 跨 skill 消费已有主张时，在新主张的 `derived_from_claim_ids` 中登记上游主张编号；缺失或失效的上游审计会阻断下游完成。
4. 最终产物中的本阶段支持与反证来源统一写为 `[S编号]`；Markdown 写在对应主张后，工作簿写入 `sources` 表，DOCX 写入来源附注，多文件产物至少在 `evidence_index.md` 建立映射。
5. 完成现有产物生成与格式校验后，运行 `audit --run-dir <研究目录> --skill jvc-bull-case --artifact <最终产物>`；多文件产物重复传入 `--artifact`。每次 audit 必须同时读取命令退出状态和 `audit.json`。
6. 只有 status 为 `blocked`、findings 中唯一 block 是 `partial_label_missing`，且至少一个 finding 为 `partial` 时，才按产物补写 `研究状态：partial`：Markdown 写入标题与结论，XLSX 在 `sources` 表表头和列结构不变的前提下追加一条可见状态数据行，DOCX 写入首段与来源附注，多文件产物至少写入 `knowledge_tree.md` 与 `evidence_index.md`；任何类型写回标签后，必须先重新运行原有产物格式校验/validator，确认结构仍有效，再重跑 audit；存在其他 block 时不得用标签绕过。重跑得到 `partial` / exit `10` 才可 partial 交付；`ready` / exit `0` 才能称为完成；其他 `blocked` / exit `20` 只能交付证据缺口和下一步，不能形成受影响的判断；exit `1` 必须修复后重跑。
7. 只有用户明确批准、且 blocker 与同 skill 最新有效 blocked audit 精确匹配时，才可运行 `waive --run-dir <研究目录> --skill jvc-bull-case --rule <阻断规则> --reason <批准理由> --scope <批准范围> --approved-by <批准人> --residual-risk <剩余风险>`；不得自我批准，waiver 最多降级为 partial。

找不到内核、profile 不兼容、账本损坏或终审异常时，不得退回纯 prompt 模式。

本 skill 复用已有来源，登记正向主张、反向证据和反证条件，不复制来源记录。

## 执行步骤

### 1. 四层面提炼

从以下四个层面各提炼 1-3 条亮点：

| 层面 | 关注什么 |
|------|---------|
| 行业趋势 | 赛道增速、政策红利、需求侧结构性变化 |
| 技术节点 | 技术壁垒、差异化、成本优势、时间窗口 |
| 团队优势 | 认知匹配、资源禀赋、执行力证据 |
| 商业化进展 | 收入、客户、合同、管线——已证明的牵引力 |

### 2. 每条亮点的结构

每条亮点包含三部分：
- **标题级亮点**：一句话概括
- **正文级论证**：事实依据 `[标注来源]` + 判断论点
- **待验证项**：这条亮点最需要补的反证或验证材料是什么

### 3. 待验证亮点

如果用户提到了某个正向判断但没有证据支撑，单独归入「待验证亮点」区，不丢弃也不混入已验证的部分。

## 输出格式

Markdown 文档，结构：

```
## 行业趋势
### 亮点 1: {标题}
（论证 + 待验证）

## 技术节点
### 亮点 N: {标题}

## 团队优势
### 亮点 N: {标题}

## 商业化进展
### 亮点 N: {标题}

## 待验证亮点
（有直觉但缺证据的正向判断）
```

## 硬约束

- 不写"建议投资"、"必投"等终局判断
- 每条亮点必须有来源标签；没有证据的放入「待验证亮点」
- 每条亮点写清楚最需要补的反证或验证材料
- 不用没有证据支撑的修饰词
- 中文输出
