# jvc-analyst 工具包整体优化建议稿

- 日期：2026-08-09
- 状态：用户已授权按建议与既定优先级顺序推进；书面规格经独立审查后进入实现
- 推进顺序：Priority 0–2（P0–P2，优先级 0–2，数字越小表示越优先）
- 已完成基线：`jvc-roi-modeler` 4.0 单表模型

## 1. 用户可见结果

本轮优化完成后，`jvc-analyst` 应成为一套边界清楚、产物可复用、能够按项目状态增量调度的投资研究工具包：

1. 用户可以按赛道研究、项目研究、最终输出和日常工具理解全部 Skill。
2. Flow 是唯一的项目总控与调度中心；Research Core 是所有研究 Skill 共享的证据与审查引擎。
3. Pre-Screen 能在约 30–60 分钟内完成商业模式、上下游、赛道有效性、市场空间、五年收入和投资回报的低精度初筛。
4. Track Research 负责首次赛道研究，Knowledge Tree Builder 把既有研究转成以可视化为主的知识结构，Market Sizing 提供可审计的单表市场模型。
5. Investment Committee（IC，投资决策委员会，负责审议投资项目）Memo 和 Research Report 只消费经审查的上游材料，不在输出阶段静默创造新事实。
6. 叙事型研究默认使用 Markdown；需要公式和勾稽关系的模型使用 Comma-Separated Values（CSV，逗号分隔值，一种可由表格软件读取并便于公式审计的文本表格格式）。
7. 每个关键产物都有明确输入、文件名、来源继承、验证方式和失败行为。

Return on Investment（ROI，投资回报率，用于衡量投资回报相对投入资本的水平）Modeler 已按用户模板完成，不在本轮重新设计，只作为定量产物和接口治理的基线。

## 2. 现状与主要矛盾

当前仓库已经具备可复用的主体能力：

- `jvc-deal-flow` 已有项目身份、追加式事件、阶段状态、最小重跑和人工闸门；
- `jvc-research-core` 已有证据台账、跨 Skill 主张继承、审计状态和产物审查；
- Track Research 已能形成完整赛道底稿；
- Knowledge Tree Builder 已能输出知识树、Mermaid 图、结构化节点、证据索引和开放问题；
- IC Memo 已采用证据丰富预审版与干净终版的双阶段合同；
- ROI Modeler 已迁移为带公式和勾稽关系的 CSV。

真正需要修正的是以下契约冲突，而不是重写一套平台：

1. README 和各 Skill 仍以旧列表展示能力，没有形成用户确认的赛道级、项目级、输出级分类。
2. Flow 与 Research Core 的实际边界基本正确，但全仓术语和下游依赖没有统一。
3. Pre-Screen 当前禁止估算市场规模，与“低精度、Top-down 快筛”的新定位直接冲突。
4. Track Research 与 Knowledge Tree Builder 虽然能够衔接，但没有定义唯一的赛道底稿、可视化主产物和更新边界。
5. Market Sizing 当前输出六工作表 Excel，与新 CSV 产物原则冲突。
6. Research Report 当前更接近排版器，还没有完整承担“消费赛道级材料形成输出”的职责。
7. Comparable Companies Analysis / Due Diligence（Comps/DD，可比公司分析/尽职调查，指比较相似公司并验证项目事实、风险与关键假设）仍以 Excel 为主，和叙事研究默认 Markdown 的原则不一致。
8. 注册表、清单、示例、评测、信任报告和维护脚本会随上述迁移产生连锁变化，需要统一收口。

## 3. 路线比较与结论

### 路线 A：契约先行、增量迁移

保留 Flow、Research Core 和现有原子 Skill，只修正职责、产物和交接合同，再按优先级迁移验证器和全仓治理。

优点：复用最多、变更可分批验证、最符合当前仓库结构。缺点：迁移期间需要同时检查旧引用是否清干净。

### 路线 B：整体重写

重新设计项目工作流、证据内核和全部 Skill，再一次性切换。

优点：表面上一致。缺点：会重复实现已有可靠能力，回归面过大，且无法从真实项目中定位是哪一层退化。

### 路线 C：只改文档和分类

只统一 README、注册表和命名，不修改实际产物。

优点：改动小。缺点：Pre-Screen、Market Sizing 和输出级接口仍然不符合用户目标。

结论：采用路线 A。本文后续设计均以增量迁移为准，不新增第二个总控、第二套证据内核或通用 Agent 平台。

## 4. 目标架构与分类

### 4.1 控制与引擎

| 层级 | 组成 | 拥有的职责 | 不拥有的职责 |
| --- | --- | --- | --- |
| 总控层 | `jvc-deal-flow`，用户侧简称 Flow | 项目身份、状态、阶段、依赖、最小调度、增量重跑、人工闸门 | 研究内容、证据判级、投资决定 |
| 引擎层 | `jvc-research-core`，用户侧简称 Research Core | 证据台账、来源与主张继承、产物类型审查、`ready` / `partial` / `blocked` 状态 | 项目阶段、Skill 选择、业务流程编排 |

Flow 只根据阶段、缺口和产物依赖决定调用哪个原子 Skill，不解析或重算专业研究内容。Research Core 只审查范围、来源、主张和产物，不主动推进项目阶段。二者不得互相复制能力。

### 4.2 赛道级 Skill

| Skill | 职责 | 主产物 |
| --- | --- | --- |
| Track Research | 首次联网研究、赛道定义、生命周期、技术路线、产业链、周期、玩家和投资问题 | `tracks/{track-slug}/landscape.md` |
| Knowledge Tree Builder | 消费已有赛道资料，形成问题树、关系图、证据索引和开放问题 | `knowledge_tree.md`，以可视化总览为首屏 |
| Market Sizing | 以 Top-down 和 Bottom-up 两种路径估算市场并对账 | `market-sizing.csv` |

Top-down 指从宏观市场或上位市场逐层收窄；Bottom-up 指从客户数、用量、单价或产能等底层变量逐项汇总。两种方法必须使用尽量独立的输入，不能只是同一假设的不同写法。

### 4.3 项目级 Skill

| Skill | 职责 | 主产物 |
| --- | --- | --- |
| Pre-Screen | 低精度商业、市场、收入和交易回报快筛 | `01-prescreen.md` |
| Bull Case | 形成正向投资假设及验证条件 | Markdown |
| Bear Case | 形成反向论证、风险和证伪条件 | Markdown |
| Comps/DD | 完成可比公司、竞品、上下游和海外标杆研究 | `03-comps-dd.md` |
| Meeting Notes | 形成结构化会议纪要 | Word 文档，作为办公协作例外 |
| Talk Notes | 形成问答式访谈纪要 | Word 文档，作为办公协作例外 |
| ROI Modeler | 根据交易、稀释和退出假设形成回报模型 | `05-roi-modeler.csv` |

Comps/DD 在本工具包中由同一项目级 Skill 承担竞品及可比部分。

### 4.4 输出级 Skill

| Skill | 消费的主要输入 | 输出 |
| --- | --- | --- |
| IC Memo | 项目级产物、交易条款、经审查的行业材料和用户判断 | `06-ic-memo-review.md`；用户批准后生成 `06-ic-memo.md` |
| Research Report | Track Research、Knowledge Tree、Market Sizing、必要的 Comps/DD | `research-report.md` 及其渲染结果 |

IC Memo 保留现有双阶段合同：`ready` 只代表 Research Core 审查通过，不代表用户批准；用户没有明确批准预审版时，不得生成或覆盖干净终版。

### 4.5 日常工具

Invoice Manager 独立处理发票识别、报销汇总和归档。它不进入研究证据链，也不被 Flow 自动调度。其 Excel 和 Portable Document Format（PDF，可移植文档格式，用于保持固定版式）产物属于业务工具例外，不改变研究产物的 Markdown / CSV 原则。

## 5. 统一产物原则

### 5.1 内容母版

- 叙事、判断、来源解释和研究结论：Markdown（`.md`）。
- 需要单元格公式、三情景和横纵勾稽的模型：CSV。
- Word、网页和固定版式文件：办公协作或发布结果，不作为研究事实的唯一母版。
- Research Core 内部的结构化台账继续使用现有格式，不暴露为用户主产物。

### 5.2 共同字段与标签

Markdown 产物必须区分：

- `【第三方事实】`
- `【公司自述】`
- `【用户观察】`
- `【模型估算】`
- `【未知/待验证】`

所有关键数字必须紧邻来源编号或模型公式。CSV 模型至少保留项目、单位、情景、公式或来源、置信度和备注。无法得到可信输入时，应缩小结论或保留空缺，不能用无来源的行业常数填充。

### 5.3 来源继承

下游 Skill 消费上游产物时，必须在 Research Core 中登记 `derived_from_claim_ids`。下游可以重组表达，但不能把上游的 `partial` 或 `blocked` 主张升级为确定事实。

## 6. Pre-Screen 新合同

### 6.1 定位

Pre-Screen 保持 Research Level 0（L0，研究级别 0，指约 30–60 分钟完成、用于决定是否继续投入研究资源的快筛）。目标不是给出精确模型，而是回答：商业链条是否说得通、赛道是否真实、五年后可能做到什么规模、当前交易是否存在可接受的回报空间，以及下一步最该验证什么。

### 6.2 输入

- 项目材料或用户描述；
- 可选的融资金额、投前或投后估值、拟持股比例和交易工具；
- 可选的市场预测、经营数据和财务预测；
- 默认全球与中国、未来五年、早期股权投资语境；用户有明确口径时以用户口径为准。

### 6.3 输出结构

`01-prescreen.md` 固定包含：

1. 快筛结论：继续研究、等待关键材料或暂不继续；这是研究资源判断，不替用户作投资决定。
2. 商业模式：客户、付费者、产品、收入方式、交付方式和单位经济线索。
3. 上下游：关键供给、核心环节、最终客户、价值分配、议价权和可能的卡点。
4. 赛道有效性：需求证据、付费证据、替代逻辑、产业阶段和反向信号。
5. 市场粗算：口径、Top-down 公式、低/中/高区间和关键敏感变量。
6. 五年收入：按市场份额、客户数乘单客收入、产能乘售价或其他最贴近业务的单一路径估算三情景。
7. 交易回报：投资金额、进入估值、初始持股、稀释、退出收入、退出倍数、回款和回报区间。
8. 风险与证伪：前三项风险、使模型失效的条件和下一轮验证动作。
9. 来源、模型假设与未知项。

### 6.4 计算边界

允许低精度估算，但必须满足：

- 公开事实、公司自述、用户输入和模型估算分开；
- 先写公式和单位，再写结果；
- 默认使用区间或三情景，不输出无依据的小数精度；
- 市场规模与五年收入至少有一条可解释的因果路径；
- 缺少交易条款时只给条件式结果，例如“若投后估值为 X、五年后退出估值为 Y”；
- 数据足以进行完整融资轮次和退出建模时，交给 ROI Modeler，不在 Pre-Screen 复制完整模型。

快速回报只要求投入资本倍数和年化回报区间。Multiple on Invested Capital（MOIC，投入资本倍数，指退出回款除以投入资本）和 Internal Rate of Return（IRR，内部收益率，指使投资现金流净现值为零的年化收益率）使用与 ROI Modeler 相同的基本定义，但不在 Markdown 中复刻完整逐轮稀释表。

### 6.5 失败与停止

- 无法识别客户、付费者或产品：停止收入和回报测算，只交付商业模式缺口。
- 没有任何市场锚点：允许列公式，不输出伪造的市场数字。
- 没有估值或投资额：只给回报敏感性框架，不给单点回报。
- 任一单位无法勾稽：标为 `【未知/待验证】`，不继续传播该数字。

## 7. Track Research 与 Knowledge Tree Builder

### 7.1 唯一赛道底稿

Track Research 的 `tracks/{track-slug}/landscape.md` 是首次赛道研究的权威人类可读底稿。它继续负责联网研究、来源核验、行业边界、生命周期、技术路线、产业链、周期位置、玩家和投资问题。

Track Research 的交接包必须明确：

- 建议进入知识树的根问题与主要分支；
- 已确认的关键实体和关系；
- 来源编号与有效主张编号；
- 需要 Market Sizing 的变量、单位和缺口；
- 开放问题和反证条件。

### 7.2 可视化主产物

Knowledge Tree Builder 不重新承担首次网页研究。它读取 `landscape.md`、Research Core 台账及用户指定的本地材料，并继续输出现有五个文件，避免增加新的兼容层：

- `knowledge_tree.md`：主要用户产物，首屏包含 Mermaid 可视化、图例、关键关系和开放问题概览；
- `knowledge_graph.mmd`：可复用的 Mermaid 图源；
- `nodes.json`：机器可读节点；
- `evidence_index.md`：节点、关系与来源映射；
- `open_questions.md`：待补研究问题。

`knowledge_tree.md` 不追求把所有节点画在一张不可读的大图中。主图只保留影响投资理解的核心关系，分支细节进入子图或问题树。

### 7.3 更新与失败行为

- 上游 Track Research 发生实质变化时，Flow 标记知识树为受影响，不自动全量重跑。
- Knowledge Tree Builder 只更新受影响节点、关系和开放问题；是否执行由用户批准。
- 无来源关系必须标为推断或开放问题。
- 图无法渲染、孤立节点、循环父子关系、重复节点编号或来源断链均视为校验失败。

## 8. Market Sizing 单表合同

### 8.1 文件与列

主产物固定为 `market-sizing.csv`，采用单表纵向分区：

```text
section,row_id,item,year,unit,conservative,base,optimistic,source_or_formula,confidence,notes
```

`section` 只允许：

- `assumptions`
- `top_down`
- `bottom_up`
- `reconciliation`
- `orthogonality_check`
- `sources`

情景单元格可以是数值或以 `=` 开头的可计算公式。`source_or_formula` 保存来源编号、公式解释或来源定位；`confidence` 只允许预定义等级，不使用自由发挥的营销性措辞。

### 8.2 最小勾稽

1. Top-down 与 Bottom-up 分别计算保守、基准和乐观情景。
2. 每个结果保留单位和年份。
3. `reconciliation` 显示两种方法的绝对差和相对差，并解释口径差异。
4. `orthogonality_check` 逐项判断两个模型是否共享关键输入；共享时披露，不能声称独立验证。
5. `sources` 保存模型使用的全部来源索引。
6. 任何总量、增长率、渗透率、价格、客户数或用量必须能追溯到来源或明确的模型假设。

### 8.3 校验

新增一个只使用 Python 标准库的 CSV 校验器，检查：

- 编码、表头、必需分区和唯一 `row_id`；
- 公式与数值单元格是否合法；
- 三情景顺序没有反转，反转有明确业务解释时可在备注披露；
- 单位和年份没有缺失；
- 两种方法、对账和正交检查都存在；
- 来源编号能够在 `sources` 分区找到；
- 关键汇总行公式与输入行勾稽。

不保留 Excel 与 CSV 两套并行权威模板。迁移完成后，旧工作簿模板和只服务于旧格式的检查引用应删除或明确归档为非权威案例。

## 9. 输出级接口

### 9.1 IC Memo

现有双阶段工作流保持不变，只更新上游映射：

- `01-prescreen.md`
- Bull Case、Bear Case 和 `03-comps-dd.md`
- `market-sizing.csv`
- `05-roi-modeler.csv`
- 会议与访谈纪要
- 必要的赛道研究与知识树

预审版必须暴露来源、冲突、模型假设和缺口。终版只能使用用户已批准的预审内容；不得因为输入格式迁移而放松现有校验器和人工闸门。

### 9.2 Research Report

Research Report 保留一个 Skill，但明确两个顺序阶段：

1. 组装：从 Track Research、Knowledge Tree、Market Sizing 和必要的 Comps/DD 生成 `research-report.md`；只重组经审查内容，不新增事实或数字。
2. 发布：校验固定章节、引用、本地图片和样式后，生成网页及固定版式结果。

如果用户已经提供完成的标准报告 Markdown，可以直接进入发布阶段。上游材料缺失时，组装阶段列出覆盖缺口，不调用网页搜索补齐。

## 10. Flow 与 Research Core 接口

### 10.1 Flow 的依赖视图

Flow 的工作流合同应登记以下最小依赖：

```text
Track Research → Knowledge Tree Builder
Track Research → Market Sizing
Pre-Screen → Bull Case / Bear Case / 项目尽调
Market Sizing + ROI Modeler + 项目级研究 → IC Memo
Track Research + Knowledge Tree + Market Sizing → Research Report
```

这不是固定全跑流水线。Flow 只在用户选择受编排模式且当前阶段确有缺口时调用最少的 Skill；升级研究级别、进入尽调、提交 IC 和生成干净终版继续保留人工批准。

### 10.2 Research Core 的产物类型

Research Core 至少支持：

- 单一 Markdown；
- 单一 CSV；
- 多文件知识树包；
- Word 纪要和发布型产物的现有审查方式。

各 profile 负责业务必需项，Research Core 只负责通用证据与产物完整性，不吸收 Market Sizing 或 ROI 的具体计算公式。

## 11. P0–P2 实施顺序

P0–P2 必须按批次验收，前一批没有通过相关检查时不进入下一批合并。

### P0：架构、总控与快速筛选

1. 将本文分类同步到 README、Skill 注册表和相关清单。
2. 在 Flow 与 Research Core 合同中固化总控/引擎边界和 Markdown / CSV 产物接口。
3. 重构 Pre-Screen 的提示、模板、profile、示例和评测。
4. 验证 ROI Modeler 作为现有 CSV 基线仍通过全部检查。

P0 验收：用户从 README 能正确选择 Skill；Pre-Screen 能完成一组有数据案例和一组缺数据案例；Flow 不自动升级研究级别；Research Core 能审查 Pre-Screen Markdown 和 ROI CSV。

### P1：赛道研究链与 Market Sizing

1. 增加 Track Research 的标准知识树与 Market Sizing 交接包。
2. 把 Knowledge Tree Builder 的 `knowledge_tree.md` 改成可视化优先的主产物并补图结构校验。
3. 将 Market Sizing 从 Excel 迁移为单一权威 CSV 模板和校验器。
4. 更新三者的 profile、示例、来源继承和 Flow 依赖。

P1 验收：同一赛道底稿能够生成可读图谱和可审计市场模型；来源编号不断链；旧 Excel 不再被任何活跃合同声明为主产物。

### P2：输出级接口与全仓治理

1. 将 Comps/DD 的主产物迁移为 Markdown。
2. 为 Research Report 增加上游组装阶段和 `research-report.md` 母版。
3. 更新 IC Memo 的 Markdown / CSV 输入映射，保留现有双阶段审批。
4. 同步 README、manifest、`reports/skill-ir.json`、注册表、示例、评测、信任报告和维护脚本。
5. 删除或降级失效模板、旧输出说明和只服务于旧合同的检查。
6. 运行全仓治理、格式、示例、产物和差异检查。

P2 验收：用户文档、Skill 合同、profile、模板、示例、评测和治理报告对每个活跃 Skill 的分类与主产物说法一致；输出级 Skill 不制造上游没有的新事实；全仓检查通过且没有意外生成文件。

## 12. pi agent 编排原则

实现阶段按 P0、P1、P2 顺序推进；同一批次内只并行无文件重叠或接口已经冻结的任务。

- 主代理：冻结接口、维护计划、审查子任务、处理交叉文件、运行批次验收。
- Flow / Research Core 子任务：只修改总控与引擎合同及必要通用检查。
- 单 Skill 子任务：修改 Skill、模板、profile、示例和专属验证器。
- 治理子任务：在接口稳定后统一更新注册表、清单、评测和报告。

子代理不得提交、推送、创建远程事项或扩大范围。每个子任务返回改动文件、验证命令、已知限制和与其他任务的接口假设；主代理在共享工作区检查实际差异，不直接相信完成声明。

## 13. 风险与控制

| 风险 | 控制 |
| --- | --- |
| 格式迁移后文档和检查仍引用旧产物 | 使用全仓搜索、注册表校验和负向评测收口 |
| Pre-Screen 因允许估算而产生伪精确数字 | 强制来源/公式/单位/区间/置信度；缺输入时失败收窄 |
| Knowledge Tree 变成不可读的大图 | 主图只保留关键关系，细节拆入子图和问题树 |
| Market Sizing 两种方法实际共享假设 | 在正交检查分区逐项披露共享输入 |
| Research Report 在组装时偷偷补研究 | 禁止联网补齐；只消费有效上游主张 |
| 输出格式变化削弱 IC Memo 证据纪律 | 预审/终版合同和人工批准闸门保持不变 |
| 多代理同时修改全仓清单导致覆盖 | 专属文件并行，共享治理文件由主代理最后统一修改 |

## 14. 非目标

- 不开发新的桌面应用或通用 Agent 平台。
- 不增加第二套 Flow、证据内核或数据库。
- 不把所有 Skill 强制串成固定流水线。
- 不在本轮修改 Invoice Manager 的业务逻辑。
- 不替用户作投资、否决、等待或提交投决的最终决定。
- 不修改用户放入仓库的 ROI Excel 原始模板。
- 不为暂时没有观察到的需求增加插件系统、配置框架或兼容层。

## 15. 完成标准

只有以下证据全部成立，本轮整体优化才算完成：

1. 分类、Flow / Research Core 边界和产物原则在所有活跃文档中一致。
2. Pre-Screen 实际输出覆盖商业模式、上下游、赛道有效性、市场、五年收入和交易回报，并通过有数据与缺数据案例。
3. Track Research 与 Knowledge Tree Builder 有可执行交接，知识树的人类主产物以可视化为先且证据可追溯。
4. Market Sizing 的唯一权威主产物为通过公式和来源校验的 `market-sizing.csv`。
5. ROI Modeler 既有模型、样例和勾稽校验继续通过。
6. IC Memo 和 Research Report 能消费新的上游主产物；IC Memo 终版审批边界没有退化。
7. Comps/DD、注册表、模板、示例、评测、信任报告、manifest 和维护脚本不存在活跃的旧合同残留。
8. 每一批的专属检查、Research Core 包检查、Skill 评测、治理检查、全仓差异检查均通过。
9. 最终工作区状态经过人工复核，没有覆盖用户无关改动，没有意外生成物，也没有未经授权的远程写入。

## 16. 已确认的实现口径

按用户“就按它来、需要修正的就修正、按这个顺序推进”的授权，本轮采用以下口径：

1. Market Sizing 采用本文定义的单个标准化 CSV，而不是六个 CSV 文件包。
2. Comps/DD 在 P2 改为 Markdown 主产物；Word 纪要、Invoice Manager 和发布型渲染文件继续作为明确例外。

实施阶段允许在不改变用户可见结果、证据纪律和完成标准的前提下，选择文件数最少、复用现有能力最多的实现。若实现发现这两项会造成无法接受的数据损失或现有项目不兼容，再停止并向用户报告具体证据。
