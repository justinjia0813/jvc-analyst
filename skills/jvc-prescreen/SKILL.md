---
name: jvc-prescreen
description: |
  项目初筛：给 deck 或项目素材，按 7 个核心维度快速过一遍，输出结构化初筛纪要 + bear case 雏形 + 关键问题清单。
  Use when user says '/jvc-prescreen', '初筛', 'prescreen', '过一遍这个项目', '帮我看看这个deck', '值不值得深入'.
user_invocable: true
version: "2.0.0"
---

# /jvc-prescreen — 项目初筛

给 deck 或项目素材，30 分钟内判断值不值得花时间深入。

## 输入

用户提供以下任意组合：
- deck（PDF / 图片 / 文本摘要）
- 公开信息链接
- 用户的初步印象或已知信息

## 2.0 证据内核（必须）

从本 `SKILL.md` 的实际目录解析同级 `../jvc-research-core/scripts/researchctl.py`，并使用绝对路径执行；不要依赖当前工作目录。

执行前必须读取同级 `../jvc-research-core/references/evidence-contract.md` 和当前 profile `../jvc-research-core/profiles/jvc-prescreen.json`。

1. 新研究先准备完整 `scope` JSON，再运行 `init --skill jvc-prescreen --run-dir <研究目录> --scope-file <scope.json>`；初始 `scope` 只能通过 `init --scope-file` 创建。
2. 复用已有研究链时运行 `init --skill jvc-prescreen --run-dir <研究目录> --resume`。后续 `scope` 更正必须通过 `record --run-dir <研究目录> --input <records.jsonl>` 登记，并用 `supersedes` 指向当前 effective scope；问题、检索、来源、主张和更正也只能通过该命令登记，不得直接编辑 `evidence_registry.jsonl`，generic `record` 不得创建 waiver。
3. 跨 skill 消费已有主张时，在新主张的 `derived_from_claim_ids` 中登记上游主张编号；缺失或失效的上游审计会阻断下游完成。
4. 最终产物中的本阶段支持与反证来源统一写为 `[S编号]`；Markdown 写在对应主张后，工作簿写入 `sources` 表，DOCX 写入来源附注，多文件产物至少在 `evidence_index.md` 建立映射。
5. 完成现有产物生成与格式校验后，运行 `audit --run-dir <研究目录> --skill jvc-prescreen --artifact <最终产物>`；多文件产物重复传入 `--artifact`。每次 audit 必须同时读取命令退出状态和 `audit.json`。
6. 只有 status 为 `blocked`、findings 中唯一 block 是 `partial_label_missing`，且至少一个 finding 为 `partial` 时，才按产物补写 `研究状态：partial`：Markdown 写入标题与结论，XLSX 在 `sources` 表表头和列结构不变的前提下追加一条可见状态数据行，DOCX 写入首段与来源附注，多文件产物至少写入 `knowledge_tree.md` 与 `evidence_index.md`；任何类型写回标签后，必须先重新运行原有产物格式校验/validator，确认结构仍有效，再重跑 audit；存在其他 block 时不得用标签绕过。重跑得到 `partial` / exit `10` 才可 partial 交付；`ready` / exit `0` 才能称为完成；其他 `blocked` / exit `20` 只能交付证据缺口和下一步，不能形成受影响的判断；exit `1` 必须修复后重跑。
7. 只有用户明确批准、且 blocker 与同 skill 最新有效 blocked audit 精确匹配时，才可运行 `waive --run-dir <研究目录> --skill jvc-prescreen --rule <阻断规则> --reason <批准理由> --scope <批准范围> --approved-by <批准人> --residual-risk <剩余风险>`；不得自我批准，waiver 最多降级为 partial。

找不到内核、profile 不兼容、账本损坏或终审异常时，不得退回纯 prompt 模式。

本 skill 从已有本地来源登记初筛主张；未要求联网时不扩展来源宇宙。

## 执行步骤

### 1. 提取事实

从素材中逐条提取可验证的事实，标注来源：
- `[S1]（deck p.N）`、`[S2]（创始人自述）`、`[S3]（公开新闻: 来源 日期）`
- `[未核实]` 只是核验状态，不能替代 `[S编号]`。

### 2. 七维度过筛

对每个维度，输出三列：「素材里说了什么」→「缺什么」→「初步判断」

| # | 维度 | 核心问题 |
|---|------|---------|
| 1 | 市场 | 目标市场有多大？增长由什么驱动？ |
| 2 | 痛点 | 解决的问题是否真实、紧迫、高频？ |
| 3 | 方案 | 产品/技术路线是否成立？与现有方案差异在哪？ |
| 4 | 团队 | 创始团队为什么能做这件事？背景、资源、认知匹配度 |
| 5 | 时机 | 为什么是现在？政策/技术/需求侧发生了什么变化？ |
| 6 | 商业模式 | 怎么赚钱？单位经济有没有初步可行性？ |
| 7 | 显性风险 | 一眼能看到的硬伤（监管、依赖、竞争格局） |

### 3. Bear case 雏形

**必须输出**，至少 2 条。不需要面面俱到，但要指向真正可能致命的风险，而非泛泛而谈。

### 4. 关键问题清单

**必须输出**。列出「如果要继续深入，首先需要回答的 3-5 个问题」，问题要足够具体，可以直接拿去问创始人或行业人士。

## 输出格式

Markdown 文档，结构：

```
## 一页事实摘要
（表格：公司名/成立时间/阶段/行业/创始人/融资历史/核心数据）

## 七维度判断
（每个维度一个子标题，三列表格）

## Bear Case 雏形
（编号列表，每条一句话 + 简要论据）

## 继续深入需回答的关键问题
（编号列表，每条可直接拿去提问）
```

## 硬约束

- 所有数字必须标注来源，无来源标 `[未核实]` 或 `[需要用户提供]`
- 不编造市场规模、估值、用户数
- 不下"建议投资/不建议"结论
- 不用没有证据支撑的修饰词（"领先的"、"颠覆性的"等）
- 中文输出，行业缩写首次出现附中文解释
