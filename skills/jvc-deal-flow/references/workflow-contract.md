# JVC Deal Flow 工作流合同

## 边界

固定骨架是：

`intake → data_layer → invest_memo → pre_dd_review → diligence → post_dd_review → insight_layer → ic_memo → ic_review → decision_record`

固定的是阶段顺序、证据纪律和人工闸门，不是每个项目运行全部 Skill。`lifecycle_status`、`workflow_stage`、`research_level`、`research_status`、`decision_status` 五个状态轴保持正交。

本 Skill 拥有：

- 项目身份、事件、派生视图和来源/工件依赖登记；
- `DATA_LAYER.md`、`INVEST_MEMO.md`、`INSIGHT_LAYER.md`；
- 原子 Skill 的选择、停止点和人工闸门。

它不拥有各原子 Skill 的专业研究方法，不复制 `jvc-research-core`，不处理发票，也不代替法律或财务专业机构。

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
| `ic_memo` | L3 | `06-ic-memo.md` 通过自身审查 | `ic_review` |
| `ic_review` | L3 | 用户修改、提交投决或停止 | `decision_record` 或返回修改 |
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
| 固定研报排版 | 已完成研究需要排版时使用 `jvc-research-report` |
| 资料结构视图 | 已有资料需要问题树时使用 `jvc-knowledge-tree-builder` |

法律尽职调查（Legal Due Diligence，LDD，对主体、合同、知识产权和合规风险的专业核验）与财务尽职调查（Financial Due Diligence，FDD，对报表、收入质量、现金流和税务的专业核验）只登记外部结果，不由本 Skill 宣称完成。

## 三个编排自产工件

### `DATA_LAYER.md`

至少覆盖来源版本、公司与融资、产品技术、财务收入、客户采购、供应链、团队、访谈、口径冲突和缺失。它不回答“是否值得投”。

### `INVEST_MEMO.md`

至少覆盖事实摘要、为什么值得继续验证、初步正反论点、3–5 条可证伪假设、每条假设的支持/反驳/未知/证伪条件、尽调轨道与完成标准。标题区写明“尽调前初稿，不是 IC Memo，不含投资建议”。

### `INSIGHT_LAYER.md`

行业论点回答展望、驱动、瓶颈、可持续性；公司论点回答竞争优势、增长机制、产品、团队和经济性。每条论点包含支持与反驳 Claim、边界、置信度、证据状态、推翻条件和受影响段落。

## 人工闸门

以下动作不得自动跨越：研究级别升级、进入尽调、把 AI 候选 Claim 标成人工验证、waiver（豁免）批准、接受尽调发现、提交投决、写最终决定、关闭或归档。

同一条用户指令已经明确授权时无需重复询问，但事件仍须保存 `approval_ref`。

## 暂停和降级

身份或阶段冲突、核心事件/证据链损坏、关键 `blocked`、需要外部专业结果、核心假设被新资料推翻或到达 `stop_at` 时暂停。

资料不足但仍能形成收窄后的可靠输出时设 `partial`，在标题、摘要和下一步中标注；不得把它写成阶段全部完成。

## 首版优化边界

- 不引入 LangGraph、数据库、消息队列、常驻服务或第二份项目数据库。
- 不做语义推断式依赖图；只消费显式 `depends_on`、来源和 Claim 引用。
- 不自动搬迁旧项目或复制外部原始材料。
- 不保留每版业务工件副本；需要逐字恢复时再接 Git 或快照。
