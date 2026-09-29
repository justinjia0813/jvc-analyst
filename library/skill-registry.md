# Skill Registry

这里记录 `jvc-analyst` 收录的 skills：10 个主要入口、3 个内部支持组件，另有 1 个独立选装运营工具。

## Primary skills

| Skill | 事实来源 | 本地入口 | 工具集角色 | 触发位置 |
| --- | --- | --- | --- | --- |
| `jvc-meeting-notes` | 本仓库 | `skills/jvc-meeting-notes/SKILL.md` | 访谈纪要：六段式或问答式 Word，交付版加工作版（待验证点、事实索引、名称对照），自带错别字/逻辑/矛盾三项自查。 | `/jvc-meeting-notes` |
| `jvc-interview-prep` | 本仓库 | `skills/jvc-interview-prep/SKILL.md` | 访谈提纲：按对象（创始人、客户、专家、推荐人）生成可证伪假设、问题、过关与警惕信号。 | `/jvc-interview-prep` |
| `jvc-prescreen` | 本仓库 | `skills/jvc-prescreen/SKILL.md` | 项目初筛：七维度一页判断、最可能不成立的理由、见创始人前的问题。 | `/jvc-prescreen` |
| `jvc-business-economics` | 本仓库 | `skills/jvc-business-economics/SKILL.md` | 商业经济分析：单位贡献桥接、规模与垫资、现金跑道与里程碑。 | `/jvc-business-economics` |
| `jvc-track-research` | 本仓库 | `skills/jvc-track-research/SKILL.md` | 赛道研究：全景、机制、竞争格局三种模式；需要时交给研报渲染或知识树。 | `/jvc-track-research` |
| `jvc-workbook` | 本仓库 | `skills/jvc-workbook/SKILL.md` | 建模工作簿：市场规模、可比公司、投资回报三种模式，每个工作簿附一页结论。 | `/jvc-workbook` |
| `jvc-thesis-test` | 本仓库 | `skills/jvc-thesis-test/SKILL.md` | 投资论点：双向、正方或反方三种写法，每条论点有支持、反驳、何时就错了和最快验证方式。 | `/jvc-thesis-test` |
| `jvc-ic-memo` | 本仓库 | `skills/jvc-ic-memo/SKILL.md` | 投决备忘录：先生成含引用、证据状态、冲突和质量报告的十七章预审版（证据内核 gate 模式）；用户明确预审通过后，再生成干净终版。另有轻量的判断状态综合。 | `/jvc-ic-memo` |
| `jvc-dd-report-digest` | 本仓库 | `skills/jvc-dd-report-digest/SKILL.md` | 尽调报告消化：财务、法律、审计、业务尽调报告的红旗表、口径差异、版本差异和条款处理选项。 | `/jvc-dd-report-digest` |
| `jvc-portfolio-tracking` | 本仓库 | `skills/jvc-portfolio-tracking/SKILL.md` | 投后跟踪：对照上期和投资目标的季度简报，按核心指标、里程碑、风险预警三块更新仪表板；可出组合概览。 | `/jvc-portfolio-tracking` |

## Hidden support components

| Component | 事实来源 | 本地入口 | 工具集角色 | 触发位置 |
| --- | --- | --- | --- | --- |
| `jvc-research-report` | 本仓库 | `skills/jvc-research-report/SKILL.md` | 内部支持：赛道研究的报告渲染环节，只排版不改内容。 | 不提供 slash command |
| `jvc-knowledge-tree-builder` | 本仓库 | `skills/jvc-knowledge-tree-builder/SKILL.md` | 内部支持：赛道研究的知识整理环节。 | 不提供 slash command |
| `jvc-research-core` | 本仓库 | `skills/jvc-research-core/SKILL.md` | 内部支持：证据台账与审查。默认 deliver 模式只给成熟度标签；IC memo、L3 或 --rigor 使用 gate 模式。历史审查身份的配置全部保留。 | 不提供 slash command |

## Operations

| Skill | 事实来源 | 本地入口 | 工具集角色 | 触发位置 |
| --- | --- | --- | --- | --- |
| `jvc-invoice-manager` | 本仓库 | `skills/jvc-invoice-manager/SKILL.md` | 独立选装运营工具：不在默认研究安装中。OCR 识别差旅发票，生成报销汇总 Excel，并按行程/项目归档 PDF。 | `/jvc-invoice-manager` |

## 接入规则

- 原始材料保持本地存放。不要把 BP、逐字稿、财务文件、尽调报告、被投公司报表上传到第三方网页工具。
- 访谈纪要记录的是受访者说法，不等于已核验事实；待验证点写在工作版里。
- 投决备忘录先出预审版，用户明确预审通过后才出干净终版。
- `jvc-invoice-manager` 只作为运营基础设施，不参与投资判断；通过 `./setup --operations` 独立安装。
- 新增 skill 必须使用 `jvc-` 前缀，并通过 `setup` 注册。
