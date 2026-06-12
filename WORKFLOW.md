# jvc-analyst — VC 投资经理工具集

> 一个 VC 投资经理的个人工具箱，不是自动化流水线。
> 流程由你把控，建档、归档、决策都是你自己做。每个 skill 独立调用，按需取用。
> 适用范围：Pre-seed ~ Series B、人民币基金、中国市场。

## 安装

```bash
git clone https://github.com/justinjia0813/jvc-analyst.git && cd jvc-analyst && ./setup
```

`setup` 会自动检测本机已有的 AI 编码平台，将 skills 注册到对应目录：

| 平台 | 目录 |
|------|------|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| Agents | `.agents/skills/` |
| OpenClaw | `.openclaw/skills/` |
| Hermes | `.hermes/skills/` |
| Cursor | `.cursor/skills/` |

安装完成后即可在对话中通过 `/jvc-prescreen`、`/jvc-bear-case` 等 slash command 调用。

---

## 工具总览

| skill | 一句话 | 输出格式 |
|-------|--------|---------|
| `/jvc-prescreen` | 给素材，快速过一遍核心问题，输出结构化初筛纪要 | Markdown |
| `/jvc-bull-case` | 给项目素材，输出投资亮点 + 待验证项 | Markdown |
| `/jvc-track-research` | 给细分赛道，快速构建产业知识图谱 | Markdown |
| `/jvc-comps-dd` | 调研竞争对手和可比公司 | Excel (.xlsx) |
| `/jvc-market-sizing` | 针对细分赛道做 TAM/SAM/SOM 建模 | Excel (.xlsx) |
| `/jvc-roi-modeler` | 计算投资回报、融资稀释、IRR/MOIC | Excel (.xlsx) |
| `/jvc-bear-case` | 四角色反方论证，输出最锋利的不投理由 | Markdown |
| `/jvc-ic-memo` | 汇总所有素材，合成十段式 IC memo 初稿 | Markdown |
| `/jvc-meeting-notes` | 转写 + 笔记 → 结构化访谈纪要 .docx | DOCX |
| `/jvc-talk-notes` | 高管/客户访谈 → 问答式访谈纪要 .docx | DOCX |
| `/jvc-invoice-manager` | PDF 发票 → OCR → 报销汇总 + 归档 | Excel + PDF archive |

**外部前置能力**：

| skill | 一句话 | 来源 |
|-------|--------|------|
| `/asr` | 音频/视频 → 本地转写文本 | 仍视为外部本地转写能力 |

---

## 各 skill 详细说明

每个 skill 的完整 prompt 和约束见 `skills/jvc-*/SKILL.md`。以下是速查摘要。

### `/jvc-prescreen` 初筛

- 输入：deck / 项目素材
- 做什么：按 7 个维度（市场/痛点/方案/团队/时机/商业模式/显性风险）过一遍
- 输出：事实摘要 + 各维度判断 + bear case 雏形 + 关键问题清单

### `/jvc-bull-case` 投资亮点

- 输入：deck、prescreen、访谈纪要、公开资料
- 做什么：从行业趋势/技术节点/团队优势/商业化进展四个层面提炼亮点
- 输出：每条亮点附论据 + 待验证项，可直接迁入 IC memo

### `/jvc-track-research` 产业知识图谱

- 输入：细分赛道名称
- 做什么：联网搜索，输出行业定义→简史→技术路线→产业链→趋势→玩家→监管→投资问题
- 输出：结构化 Markdown，可衔接 `/jvc-comps-dd` 和 `/jvc-market-sizing`

### `/jvc-comps-dd` 竞品尽调

- 输入：目标项目或赛道
- 做什么：搜集上市公司和初创公司，按直接竞品/可比/上下游/海外标杆分类
- 输出：Excel（companies / segmentation / sources / coverage_notes 四个 sheet）

### `/jvc-market-sizing` 市场规模建模

- 输入：细分赛道定义、地域、客群、场景
- 做什么：同时建 Top-Down 和 Bottom-Up 两套模型 + 正交性检查 + 对账
- 输出：Excel（assumptions / top_down / bottom_up / reconciliation / orthogonality_check / sources）

### `/jvc-roi-modeler` 投资回报模型

- 输入：投资条款 + 财务预测 + 后续融资假设 + 退出假设
- 做什么：逐轮计算稀释 → 三情形退出 → MOIC/IRR → 敏感性分析
- 输出：Excel（investment_terms / financial_forecast / financing_dilution / ownership / exit_scenarios / returns / sensitivity / sources）

### `/jvc-bear-case` 反向论证

- 输入：项目分析材料
- 做什么：扮演挑剔LP / 竞品CEO / 怀疑论同行 / IC boss 四种角色找茬
- 输出：至少 4 条反对论点，每条附可证伪条件

### `/jvc-ic-memo` 投决备忘录

- 输入：所有前序素材 + 你的核心投资逻辑
- 做什么：按十段结构合成 memo 初稿（交易摘要→公司→市场→产品→团队→财务→投资逻辑→风险→估值→待决）
- 输出：完整 Markdown 初稿，风险篇幅 ≥ 投资逻辑篇幅

### `/jvc-meeting-notes` 访谈纪要

- 输入：AI 转写逐字稿、用户随笔、会议日期、线上/线下、项目名称
- 做什么：融合逐字稿与随笔，按六段式结构生成 Word 访谈纪要
- 输出：`.docx` 文件，命名为 `{YYYYMMDD}_{项目名称}_访谈纪要.docx`
- 来源：已整合自 `meeting-notes` repo，脚本和模板位于 `skills/jvc-meeting-notes/`

### `/jvc-talk-notes` 问答式访谈纪要

- 输入：高管访谈、客户访谈、专家访谈逐字稿，用户随笔，会议日期，受访人角色
- 做什么：按一问一答制整理问题、回答摘要、关键原话、事实标签、待验证点
- 输出：`.docx` 文件，命名为 `{YYYYMMDD}_{项目名称}_{受访人角色}_问答纪要.docx`
- 来源：复用 `skills/jvc-meeting-notes/` 下的 Word 生成脚本和模板

### `/jvc-invoice-manager` 发票整理

- 输入：PDF 发票目录、用户确认后的费用信息、归属项目、报销人、月份
- 做什么：OCR 识别发票，复核后生成报销汇总 Excel，并按行程归档 PDF
- 输出：`archive/{YYYY-MM}_报销汇总.xlsx` 与行程 PDF 归档目录
- 来源：已整合自 `invoice-manager` repo，脚本和模板位于 `skills/jvc-invoice-manager/`

---

## 项目档案目录约定（参考）

你自己建档。推荐结构，skill 产出物归档位置已标出：

```
projects/{company-slug}/
├── 00-source/              # 只读区：deck、财务表、转写、/jvc-meeting-notes 或 /jvc-talk-notes .docx
├── 01-prescreen.md         # ← /jvc-prescreen
├── 02-dd-notes.md          # 你自己的尽调笔记
├── 03-founder-sync.md      # 你自己的访谈笔记
├── 04-bull-case.md         # ← /jvc-bull-case
├── 04-bear-case.md         # ← /jvc-bear-case
├── 05-comps-dd.xlsx        # ← /jvc-comps-dd
├── 05-market-sizing.xlsx   # ← /jvc-market-sizing
├── 05-roi-modeler.xlsx     # ← /jvc-roi-modeler
├── 06-ic-memo.md           # ← /jvc-ic-memo
└── 99-decision.md          # 你自己写的最终决策

tracks/{track-slug}/
├── landscape.md            # ← /jvc-track-research
├── comps-dd.xlsx           # ← /jvc-comps-dd（赛道级）
└── market-sizing.xlsx      # ← /jvc-market-sizing（赛道级）
```
