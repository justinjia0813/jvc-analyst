# JVC Deal Flow 工作流合同

## 边界

固定骨架是：

`intake → data_layer → invest_memo → pre_dd_review → diligence → post_dd_review → insight_layer → ic_memo → ic_review → decision_record`

固定的是阶段顺序、证据纪律和人工闸门，不是每个项目运行全部 Skill。`lifecycle_status`、`workflow_stage`、`research_level`、`research_status`、`decision_status` 五个状态轴保持正交。

本 Skill 拥有：

- 作为唯一项目总控，拥有项目身份、状态、事件、派生视图和来源/工件依赖登记；
- `DATA_LAYER.md`、`INVEST_MEMO.md`、`INSIGHT_LAYER.md`；
- 受编排模式下按阶段与已确认缺口执行的最小调度、增量重跑、停止点和人工闸门。

原子 Skill 始终可以独立调用。本 Skill 不拥有各原子 Skill 的专业研究方法，不解析或重算其研究结果，不复制 `jvc-research-core`，不处理发票，也不代替法律或财务专业机构。`jvc-research-core` 只维护证据台账、主张继承和产物审计，不推进业务阶段。

## 阶段与完成锚点

| 阶段 | 最低级别 | 完成锚点 | 下一步 |
| --- | --- | --- | --- |
| `intake` | L0 | 身份唯一、来源已登记 | `data_layer` |
| `data_layer` | L1；L0 可只快筛 | `DATA_LAYER.md` 区分第三方事实、公司自述、用户观察、模型估算、代理推断和未知 | `invest_memo` |
| `invest_memo` | L1 | `INVEST_MEMO.md` 含 3–5 条可证伪假设、验证轨道和不覆盖范围 | `pre_dd_review` |
| `pre_dd_review` | L1 | 用户 `approve`、`revise` 或 `stop` | `diligence` 或返回修改 |
| `diligence` | L2 | 被选轨道均有真实产物、明确缺口或阻塞原因 | `post_dd_review` |
| `post_dd_review` | L2 | 用户确认哪些发现进入论点层 | `insight_layer` 或补证据 |
| `insight_layer` | L2 | 每条论点有支持、反驳、边界、状态和推翻条件 | `ic_memo` 或继续尽调 |
| `ic_memo` | L3 | `06-ic-memo-review.md` 通过自身证据审查 | `ic_review` |
| `ic_review` | L3 | 用户修改/停止/批准预审，批准后生成 `06-ic-memo.md` | `decision_record` 或返回修改 |
| `decision_record` | L3 | 仅记录用户明确决定 | 关闭、监控或保持 |

`paused`、`closed`、`archived` 是生命周期，不是工作流阶段。暂停后恢复原阶段。

## 最小路由

| 缺口 | 调用 |
| --- | --- |
| L0 快筛 | `jvc-prescreen` |
| 访谈事实 | `jvc-meeting-notes` 或 `jvc-talk-notes` |
| 行业与产业链 | `jvc-track-research` |
| 竞品/可比公司 | `jvc-comps-dd` |
| 市场空间 | `jvc-market-sizing` |
| 正反论证 | L2+ 使用 `jvc-bull-case` 与 `jvc-bear-case`，保留冲突 |
| 回报与条款 | 输入充分时使用 `jvc-roi-modeler` |
| 投决材料 | L3 使用 `jvc-ic-memo` |
| 研报组装与发布 | 赛道级上游已审计、需要研究报告时使用 `jvc-research-report`（两阶段：组装 canonical `research-report.md`，再渲染 PDF/HTML） |
| 资料结构视图 | 已有资料需要问题树时使用 `jvc-knowledge-tree-builder` |

法律尽职调查（Legal Due Diligence，LDD，对主体、合同、知识产权和合规风险的专业核验）与财务尽职调查（Financial Due Diligence，FDD，对报表、收入质量、现金流和税务的专业核验）只登记外部结果，不由本 Skill 宣称完成。

## 显式依赖边

- `jvc-track-research` → `jvc-knowledge-tree-builder`：固定上游产物为 `tracks/{track-slug}/landscape.md`；`tracks/{track-slug}/landscape.md` → 五文件知识包，即 visual-first（视觉优先，先用图和树展示结构）的 `knowledge_tree.md` 主入口，以及 `knowledge_graph.mmd`、`nodes.json`、`evidence_index.md`、`open_questions.md`。五文件必须通过 validator 和 package check。
- `jvc-track-research` → `jvc-market-sizing`：市场规模模型继承赛道定义、边界与关键假设；唯一活跃模型固定为单表 `market-sizing.csv`，并必须通过 validator 和 package check。
- 项目产物 → `jvc-ic-memo`：投决备忘录只汇总已存在且完成相应审查的项目材料；活跃上游输入为 `01-prescreen.md`、Bull/Bear Case、`03-comps-dd.md`、`market-sizing.csv`、`05-roi-modeler.csv`、会议与访谈纪要，以及必要的赛道研究与知识树。预审版 → 用户明确批准 → 干净终版的闸门不因输入格式而放松。
- 赛道产物 → `jvc-research-report`：研究报告两阶段组装：从 Track Research、Knowledge Tree、Market Sizing 和可选 Comps/DD 组装 canonical `research-report.md`（保留来源标识、继承上游主张、展示覆盖缺口、不联网补研究），再用渲染器发布；已有完整 canonical Markdown 时直接发布。

依赖边只用于判断受影响工件和最小重跑范围，不把下游 Skill 变成自动任务。上游变化只显式标记受影响或 `stale` 的下游工件，不得自动重跑。新增来源事件不得自动调用 Skill 或推进阶段；它只登记来源，随后由独立 `artifact_marked_stale` 事件把有显式依赖的工件标为 `stale`。任何重跑执行仍需用户批准。

## 三个编排自产工件

### `DATA_LAYER.md`

至少覆盖来源版本、公司与融资、产品技术、财务收入、客户采购、供应链、团队、访谈、口径冲突和缺失。它不回答“是否值得投”。

### `INVEST_MEMO.md`

至少覆盖事实摘要、为什么值得继续验证、初步正反论点、3–5 条可证伪假设、每条假设的支持/反驳/未知/证伪条件、尽调轨道与完成标准。标题区写明“尽调前初稿，不是 IC Memo，不含投资建议”。

### `INSIGHT_LAYER.md`

行业论点回答展望、驱动、瓶颈、可持续性；公司论点回答竞争优势、增长机制、产品、团队和经济性。每条论点包含支持与反驳 Claim、边界、置信度、证据状态、推翻条件和受影响段落。

## 人工闸门

以下动作不得自动跨越：研究级别升级、进入尽调、把 AI 候选 Claim 标成人工验证、waiver（豁免）批准、接受尽调发现、提交 IC、生成干净终版、写最终决定、关闭或归档。

同一条用户指令已经明确授权时无需重复询问，但事件仍须保存 `approval_ref`。

## 暂停和降级

身份或阶段冲突、核心事件/证据链损坏、关键 `blocked`、需要外部专业结果、核心假设被新资料推翻或到达 `stop_at` 时暂停。

资料不足但仍能形成收窄后的可靠输出时设 `partial`，在标题、摘要和下一步中标注；不得把它写成阶段全部完成。

## 首版优化边界

- 不引入 LangGraph、数据库、消息队列、常驻服务或第二份项目数据库。
- 不做语义推断式依赖图；只消费显式 `depends_on`、来源和 Claim 引用。
- 不自动搬迁旧项目或复制外部原始材料。
- 不保留每版业务工件副本；需要逐字恢复时再接 Git 或快照。
