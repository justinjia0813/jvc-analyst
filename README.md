# jvc-analyst

<p align="center">
  <img src="assets/brand/github-hero.svg" alt="jvc-analyst: local-first venture diligence skills" width="100%">
</p>

<p align="center">
  <a href="#安装"><img alt="Install locally" src="https://img.shields.io/badge/install-local--first-253B32?style=flat-square"></a>
  <a href="#工具总览"><img alt="Skills" src="https://img.shields.io/badge/skills-10%20primary-A46A50?style=flat-square"></a>
  <a href="#使用原则"><img alt="Judgment-first" src="https://img.shields.io/badge/method-judgment--first-161514?style=flat-square"></a>
  <a href="#维护检查"><img alt="Checks" src="https://img.shields.io/badge/checks-shell%20%2B%20workbook-5F635B?style=flat-square"></a>
</p>

`jvc-analyst` 是一套本地优先的早期 Venture Capital（VC，风险投资）工具箱，以 Agent Skills 的形式运行在 Claude Code、Codex、Cursor 等 AI 编程助手里，面向中国市场 Pre-seed 到 Series B 的项目。

它不是自动化流水线，也不替人做投资决策。10 个 skill 覆盖一个项目从看 BP、访谈、分析、尽调、投决到投后的日常工作，每个都能单独调用。

设计原则是**判断在前**：产出的主体是能直接转给合伙人的判断和数字，来源和验证过程放在附录；缺数据时给有依据的估算并标注，而不是留空。严格的证据审查只保留在投决备忘录，其他场景按需开启。

## 适合谁

- 做中国市场早期项目（Pre-seed 到 Series B）的投资人、投研和分析师。
- 想让 AI 把 BP、访谈、财务表、尽调报告变成可直接转发的初稿判断，但最终决策仍由自己做的人。
- 在意保密：所有材料留在本地，skill 本身不含任何联网脚本。

## 安装

```bash
mkdir -p "$HOME/.agents/sources"
git clone https://github.com/justinjia0813/jvc-analyst.git "$HOME/.agents/sources/jvc-analyst"
cd "$HOME/.agents/sources/jvc-analyst"
./setup --global
# 可选：另行注册发票运营工具
./setup --global --operations
```

若目标目录已经存在，请先检查其来源与本地改动，不要覆盖。需要固定版本时，在源码目录 `git checkout <tag>`。全局模式把同一份源码链接到 `~/.agents/skills/` 和检测到的客户端目录，默认安装 **10 个主要入口 + 3 个内部组件，共 13 个目录**；加装发票后为 14 个。源码目录需长期保留，更新源码会影响这些链接。需要固定版本时可用 `git checkout --detach <commit>`。

| 共享入口或客户端 | 全局目录 | 注册条件 |
| --- | --- | --- |
| 通用 Agents | `~/.agents/skills/` | 显式全局安装时创建 |
| Claude Code | `~/.claude/skills/` | 已有目录或可找到 Claude 命令 |
| Codex | `~/.codex/skills/` | 已有 `~/.codex/` |
| Hermes | `~/.hermes/skills/` | 已有技能目录 |
| Cursor | `~/.cursor/skills/` | 已有技能目录 |
| OpenClaw | `~/.openclaw/skills/` | 已有技能目录 |
| OpenCode | `~/.config/opencode/skills/` | 已有技能目录 |
| Pi | `~/.pi/agent/skills/` | 已有技能目录 |
| Grok | `~/.grok/skills/` | 已有技能目录 |

被替换的旧目录或链接备份在 `~/.local/state/jvc-analyst/backups/<client>/`。安装器不卸载任何技能；如果本机装过 3.0，安装结束时会列出残留的旧入口位置，确认不用后手动删除。

安装后刷新技能目录或开启新会话，再用 `/jvc-prescreen` 等命令或自然语言点名技能。**文件已安装、客户端已加载、真实任务已验证是三个不同状态。**

### 证据内核（可选）

`jvc-research-core` 维护一条只能追加的证据台账，并对最终产物做确定性审查。默认不启用；用户要求留台账、`--rigor`，或使用 `/jvc-ic-memo` 时才用。

```bash
python3 "<core>/scripts/researchctl.py" init --skill "<skill>" --run-dir "<run-dir>" --scope-file "<scope.json>"
python3 "<core>/scripts/researchctl.py" record --run-dir "<run-dir>" --input "<records.jsonl>"
python3 "<core>/scripts/researchctl.py" audit --run-dir "<run-dir>" --skill "<skill>" --artifact "<artifact>" [--mode deliver|gate]
```

`audit` 有两种模式。默认 `--mode deliver`：`ready`、`partial`、`blocked` 只是证据成熟度标签，写在文末一行，不限制正文；只有产物缺失、台账残缺或夸大成熟度时才拦截（退出码 20）。`--mode gate` 用于 `/jvc-ic-memo`、L3 或用户要求 `--rigor`：只有 `ready` 可以声称研究完成；`partial` 必须标注不完整并缩小结论；`blocked` 只交付证据缺口和下一步。

## 使用原则

- 每个 skill 都可独立调用，按需取用。建档、归档、推进节奏和最终决策由用户自己把控。
- 原始项目材料保持本地存放，默认放在 `projects/{company-slug}/00-source/`。
- 产出先给判断再给依据；公司自述标 `[创始人自述]`，估算标 `[估算：依据]`，每份产出写明最可能错在哪。
- 公开资料可以联网检索；不要把 BP、逐字稿、财务表、尽调报告、被投公司报表上传到第三方网页工具。

### 研究级别

L0–L3（Research Level 0–3，研究级别 0–3，用于按决策场景控制流程密度）决定要建多少项目档案，不决定能不能调用某个 skill：

| 级别 | 什么时候用 | 额外工件上限 |
| --- | --- | --- |
| **L0 快筛** | 看 BP、整理访谈 | 无；按任务只产出初筛、纪要或访谈提纲 |
| **L1 初筛** | 决定是否见创始人 | `spec/CONTEXT.md` + `spec/research-plan.md` + `spec/hypotheses.md` |
| **L2 尽调** | 首面后验证关键假设 | + `spec/tasks.md` + `evidence/` |
| **L3 重仓/领投** | 提交投资决策委员会前 | + 完整证据卡片 + `decision-journal.md` |

## 工具总览

按一个项目的生命周期排列。每个 skill 的完整合同见对应 `SKILL.md`；示例使用虚构项目。

| 入口 | 什么时候用 | 最少输入 | 调用例子 | 交付 |
| --- | --- | --- | --- | --- |
| [/jvc-prescreen](skills/jvc-prescreen/SKILL.md) 初筛 | 第一次看项目，30 分钟判断值不值得见创始人 | 一份 BP 或项目介绍 | `/jvc-prescreen 帮我看看 projects/星澜工控/00-source/BP.pdf，给合伙人一页判断。` | `01-prescreen.md`：一句话判断、七维度、最可能不成立的理由、见面问题 |
| [/jvc-interview-prep](skills/jvc-interview-prep/SKILL.md) 访谈提纲 | 见创始人、客户、专家、推荐人之前 | 访谈对象，加任何已有材料 | `/jvc-interview-prep 明天见星澜的客户质量经理，45 分钟，重点验证是否真的按年付费。` | `interview-prep-{对象}.md`：假设、问题、过关与警惕信号 |
| [/jvc-meeting-notes](skills/jvc-meeting-notes/SKILL.md) 访谈纪要 | 访谈之后，把逐字稿变成 Word 纪要 | 逐字稿（可以是录音转写），建议加随笔 | `/jvc-meeting-notes 把这份管访转写稿和我的随笔整理成六段式纪要。` | 交付版 + 工作版 Word：待验证点、名称对照、三项自查记录 |
| [/jvc-business-economics](skills/jvc-business-economics/SKILL.md) 商业经济 | 想知道一单赚多少、规模化后变好还是变差、现金能撑多久 | 定价、订单、成本或毛利中任意已知部分 | `/jvc-business-economics 按每条产线算星澜的单位贡献和现金跑道。` | `business-economics.md` + 可重跑的计算脚本 |
| [/jvc-track-research](skills/jvc-track-research/SKILL.md) 赛道研究 | 新赛道开题、看行业机制、分析竞争格局 | 赛道名或项目名 | `/jvc-track-research 做一份先进封装玻璃基板的全景研究。` | 全景 `landscape.md` / 机制 `industry-mechanics.md` / 竞争 `competitive-positioning.md`；可渲染 PDF |
| [/jvc-workbook](skills/jvc-workbook/SKILL.md) 建模工作簿 | 需要市场规模、可比公司或投资回报的 Excel | 赛道口径或本轮条款 | `/jvc-workbook 按投前 3 亿、投 3000 万，算三种退出情景的 MOIC 和 IRR。` | Excel 工作簿 + 一页结论 |
| [/jvc-thesis-test](skills/jvc-thesis-test/SKILL.md) 投资论点 | 把投资逻辑写成可检验的论点，或专门唱反调 | 已有分析材料 | `/jvc-thesis-test 反方模式，攻击星澜的续费假设。` | `04-thesis-test.md`（或 `04-bull-case.md` / `04-bear-case.md`）：论点、命门 |
| [/jvc-dd-report-digest](skills/jvc-dd-report-digest/SKILL.md) 尽调报告消化 | 拿到第三方财务、法律、审计尽调报告 | 尽调报告，建议加 BP | `/jvc-dd-report-digest 看下这份财务尽调，列红旗和条款处理。` | `dd-digest-{类型}.md`：红旗表、口径差异、版本差异、追问 |
| [/jvc-ic-memo](skills/jvc-ic-memo/SKILL.md) 投决备忘录 | 上投决会前 | 前面各 skill 的产出 | `/jvc-ic-memo 基于星澜的材料生成十七章预审版，先停在 review。` | `06-ic-memo-review.md` → 用户明确“预审通过”后生成 `06-ic-memo.md`；另有轻量 `decision-memo.md` |
| [/jvc-portfolio-tracking](skills/jvc-portfolio-tracking/SKILL.md) 投后跟踪 | 被投公司季报、月报到了 | 本期财务报表，加上期记录和目标 | `/jvc-portfolio-tracking 恒川新材 Q2 报表到了，对照年度目标出简报并更新仪表板。` | `投后-{公司}-{季度}.md` + 仪表板三块更新内容 |

内部组件（不单独作为入口）：[研报渲染](skills/jvc-research-report/SKILL.md)和[知识树](skills/jvc-knowledge-tree-builder/SKILL.md)是赛道研究的环节，[证据内核](skills/jvc-research-core/SKILL.md)是可选审查工具。

独立选装：[/jvc-invoice-manager](skills/jvc-invoice-manager/SKILL.md) 只在报销或归档发票时使用，不属于投资研究；OCR（Optical Character Recognition，光学字符识别）结果须人工复核。安装方式见上文。

## 从 3.0 迁移

如果你用过 3.0，旧入口与 4.0 的对应关系如下：

| 3.0 入口 | 4.0 去哪了 |
| --- | --- |
| `jvc-talk-notes` | `/jvc-meeting-notes` 问答式版式 |
| `jvc-claim-audit` | `/jvc-meeting-notes` 工作版的待验证点；材料说法核对放进初筛或投资论点 |
| `jvc-diligence-plan`、`jvc-customer-validation`、`jvc-founder-assessment` | `/jvc-interview-prep`（按访谈对象出题） |
| `jvc-financing-milestones` | `/jvc-business-economics` 的现金跑道一节 |
| `jvc-industry-mechanics`、`jvc-competitive-positioning` | `/jvc-track-research` 机制模式、竞争格局模式 |
| `jvc-market-sizing`、`jvc-comps-dd`、`jvc-roi-modeler`、`jvc-return-underwriting` | `/jvc-workbook` 市场规模、可比公司、投资回报模式 |
| `jvc-bull-case`、`jvc-bear-case` | `/jvc-thesis-test` 正方、反方写法 |
| `jvc-decision-memo` | `/jvc-ic-memo` 轻量模式（判断状态综合） |
| `jvc-deal-flow` | 移除；项目状态由用户自己管理，历史 `STATE.md` 等文件仍可作为 IC memo 素材 |

旧产物文件名（`04-bull-case.md`、`05-market-sizing.xlsx`、`claim-audit.md` 等）都仍被新 skill 读取。

## 日常组合场景

1. **收到 BP：** `/jvc-prescreen` 快筛；值得见就用 `/jvc-interview-prep` 准备问题。
2. **访谈之后：** `/jvc-meeting-notes` 出纪要，工作版里的待验证点就是下一轮的问题。
3. **研究一个新赛道：** `/jvc-track-research` 全景或机制模式；要数字时接 `/jvc-workbook` 市场规模、可比公司。
4. **核对交易：** `/jvc-business-economics` 看单位经济和现金，`/jvc-workbook` 投资回报模式看条款回报，`/jvc-thesis-test` 把逻辑和命门写清楚。
5. **第三方尽调回来：** `/jvc-dd-report-digest` 列红旗和条款处理。
6. **上会：** `/jvc-ic-memo` 预审版，批准后出终版。
7. **投后：** 每季度 `/jvc-portfolio-tracking`。

## 统一提问模板

```text
/jvc-[skill-name]

对象：[公司/赛道/访谈对象]
要回答的问题：[这次要支持什么判断]
材料：[相对路径或已读材料]
范围：[地域、时间、客户/产品边界]
输出：[文件名或格式]
```

不确定的字段写“未知”即可。

## 成熟度

诚实地说明现状，便于你判断能放心用到什么程度：

| 状态 | Skill |
| --- | --- |
| 已在真实项目材料上完成端到端验证 | `/jvc-business-economics` |
| 合同已重写、确定性检查通过，尚未在真实材料上系统复测 | 其余 9 个主要入口 |
| 沿用 3.0 已验证的实现 | 研报渲染、知识树、证据内核、发票工具 |

确定性检查（`bash scripts/check-review-fixes.sh`）只证明文件结构、合同文本和脚本行为符合预期，不代表模型在你的材料上一定输出正确。产出请当作初稿复核，尤其是数字和来源。欢迎通过 Issue 反馈真实使用中的问题。

## Word 模板定制

`jvc-meeting-notes` 不绑定任何基金或机构的 Word 模板。仓库内默认模板是中性公开模板，公众用户可以用自己的 `.docx` 模板覆盖。

默认模板采用内置 meeting-notes 标准版式：A4 页面，页边距为上/下 2.54cm、左/右 3.17cm；标题居中 18pt 加粗；章节标题 10pt 加粗；正文和问答小标题 10pt 常规；段前/段后 0、单倍行距；正文两端对齐，并启用 `doNotExpandShiftReturn` 避免手动换行短行被强行拉满；段落使用 `Normal` 并通过 run 级字体格式呈现，六段式和问答式两种版式视觉一致，只改变文字编排结构。

模板解析顺序：

1. 命令行参数：`--template path/to/template.docx`
2. 环境变量：`JVC_DOCX_TEMPLATE=/path/to/template.docx`
3. 本地放置：`skills/jvc-meeting-notes/templates/custom.docx`
4. 默认模板：`skills/jvc-meeting-notes/templates/访谈纪要模板.docx`

生成器会从模板中保留页面设置、样式、页眉和页脚，清空正文占位内容后写入新的纪要正文。如果模板里有示例段落，脚本会按前几个非空段落抽取标题、章节、正文和子标题样式；如果模板只提供 `Normal` 样式，则按默认 meeting-notes 标准直接写入标题、章节、正文和子标题的字体格式。`templates/custom.docx` 已被 `.gitignore` 忽略，适合放用户自己的机构模板，不会误提交到 public repo。

示例：

```bash
python3 skills/jvc-meeting-notes/scripts/generate_meeting_notes.py data.json \
  --template ~/Documents/my-firm-template.docx \
  --output output
```

## 项目档案目录约定

建档由用户自己控制。推荐结构如下：

```text
projects/{company-slug}/
├── 00-source/                  # 只读区：BP、财务表、逐字稿、尽调报告
├── spec/                       # L1+ 研究规格（可选）
├── 01-prescreen.md             # ← /jvc-prescreen
├── interview-prep-{对象}.md    # ← /jvc-interview-prep
├── 【日期访谈】{对象}.docx      # ← /jvc-meeting-notes（交付版与工作版）
├── business-economics.md       # ← /jvc-business-economics
├── competitive-positioning.md  # ← /jvc-track-research 竞争格局模式
├── 04-thesis-test.md           # ← /jvc-thesis-test
├── 05-market-sizing.xlsx       # ← /jvc-workbook 市场规模
├── 05-comps-dd.xlsx            # ← /jvc-workbook 可比公司
├── 05-roi-modeler.xlsx         # ← /jvc-workbook 投资回报
├── dd-digest-{类型}.md          # ← /jvc-dd-report-digest
├── 06-ic-memo-review.md        # ← /jvc-ic-memo 预审版
├── 06-ic-memo.md               # ← /jvc-ic-memo 终版
└── 99-decision.md              # 用户自己的最终决策

tracks/{track-slug}/
├── landscape.md                # ← /jvc-track-research 全景
├── industry-mechanics.md       # ← /jvc-track-research 机制
├── report.pdf / report.html    # ← 研报渲染
└── knowledge_tree.md 等        # ← 知识树

portfolio/{company-slug}/
└── 投后-{公司}-{YYYYQn}.md      # ← /jvc-portfolio-tracking
```

### 旧项目迁移

旧项目无需搬家，也不要修改 `00-source/`。已有的编号文件继续保留，新 skill 都能读取。

## 仓库结构

```text
.
├── skills/
│   ├── jvc-prescreen/              # 10 个主要入口
│   ├── jvc-interview-prep/
│   ├── jvc-meeting-notes/
│   ├── jvc-business-economics/
│   ├── jvc-track-research/
│   ├── jvc-workbook/
│   ├── jvc-thesis-test/
│   ├── jvc-dd-report-digest/
│   ├── jvc-ic-memo/
│   ├── jvc-portfolio-tracking/
│   ├── jvc-research-report/        # 内部：研报渲染
│   ├── jvc-knowledge-tree-builder/ # 内部：知识树
│   ├── jvc-research-core/          # 内部：可选证据内核
│   └── jvc-invoice-manager/        # 独立选装
├── examples/           # 每个 skill 的虚构范例 + 端到端示例
├── templates/          # Excel 工作簿与项目规格模板
├── evals/              # 路由与输出的确定性测评
├── scripts/            # 自检、Excel 生成与校验
├── reports/            # 发布门控与可信度报告
├── agents/ library/ security/
├── CLAUDE.md           # 在本仓库内工作时的 Agent 规则
└── setup
```

## 维护检查

```bash
bash scripts/check-review-fixes.sh   # 运行全部确定性检查
```

## 许可

[MIT](LICENSE)
