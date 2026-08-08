---
name: jvc-deal-flow
description: Use when the user wants to initialize, resume, inspect, pause, advance, close, or archive a local JVC deal project; orchestrate an existing project from Data Layer through Invest Memo, selected diligence tracks, Insight Layer, and IC Memo; add new source material and identify the smallest affected rerun; or list projects waiting for review. Do not use for a single standalone research artifact, invoice work, automatic investment decisions, or silently upgrading research depth.
metadata:
  author: jvc-analyst
user_invocable: true
version: "3.0.0"
---

# /jvc-deal-flow — 投前工作流编排

把现有 `/jvc-*` 原子 Skill 组织成可暂停、可恢复、可审计的本地项目流程。它只拥有项目身份、状态、事件、`DATA_LAYER.md`、`INVEST_MEMO.md` 和 `INSIGHT_LAYER.md`；专业研究仍由对应 Skill 完成。

## 3.0 适用级别

最低适用级别：**L0+**（Level 0 or above，零级及以上研究，用于从受编排快筛按需升级）。

- 用户调用本 Skill，表示选择“受编排项目”模式；L0 也可创建最小状态元数据。
- 始终选择最低充分级别；升级 L0→L1、L1→L2、L2→L3 前必须取得用户明确批准。
- 不替用户决定进入尽调、提交 IC（Investment Committee，投资决策委员会，负责审议投资项目）、关闭、归档或最终投/不投/等待。

## 反合理化约束

- “工作流完整，所以全部 Skill 都应运行” → 只选择当前假设缺口所需的轨道。
- “状态写在回复里就够了” → 状态只能从 `project_events.jsonl` 派生。
- “新资料来了，全部重跑更保险” → 先按显式依赖标记受影响工件，再请求最小重跑批准。
- “IC Memo 的语气等于用户决定” → `decision_status` 只能记录用户原话或确认。
- “事件脚本失败，可以手改 JSONL” → 失败关闭并报告；绝不直接编辑或重排事件链。

## 开始

1. 读取 `references/workflow-contract.md`；首次写事件或排障时再读 `references/project-event-contract.md`。
2. 按以下顺序定位项目库：用户给定的绝对 `library_root` → 当前工作区 `.jvc-library.json` → 向上唯一标记；无法唯一定位就暂停询问。
3. 从本 Skill 的实际目录解析 `scripts/dealflowctl.py`，始终使用绝对路径。
4. 新建或恢复：

```bash
python3 "<skill-root>/scripts/dealflowctl.py" init \
  --library-root "<library-root>" \
  --project-name "<项目名>"
```

已知 `project_id` 时优先加 `--project-id "<uuid>"` 精确恢复。若命令返回近似名称候选，先让用户确认；仅当用户确认是新项目后才加 `--confirm-new` 重试。

5. 已有项目先运行 `check --project-dir "<project-dir>"`，再读取 `STATE.md`、相关工件和最新事件；查询项目库使用 `list --library-root "<library-root>"`，不得启动研究。

开始或继续时只说明：新建/恢复结果、当前阶段与级别、本轮停止点。

## 执行

1. 按 `workflow-contract.md` 选择当前阶段的最小动作。需要调用原子 Skill 时，先读取其同级 `SKILL.md` 并遵守其输入、证据和输出合同。
2. L1+ 初始化或恢复同项目的 `jvc-research-core`；所有 scope、来源、问题、Claim（主张，指可被证据支持或反驳的明确陈述）和更正都通过 `researchctl.py` 写入，绝不直接编辑 `evidence_registry.jsonl`。
3. 编排自产 Markdown 在尽调前同时审查 `DATA_LAYER.md` 与 `INVEST_MEMO.md`；尽调后再加入 `INSIGHT_LAYER.md`。调用 profile `jvc-deal-flow`，同时读取命令退出状态与 `audit.json`。
4. 每次来源、工件、审查、阶段、级别、生命周期或闸门发生业务变化时，准备一个事件输入 JSON，再运行：

```bash
python3 "<skill-root>/scripts/dealflowctl.py" event \
  --project-dir "<project-dir>" \
  --input "<event-input.json>"
```

5. 到 `pre_dd_review`、`post_dd_review` 或 `ic_review` 时追加 `gate_requested`，设为 `paused` 并停止。只有用户明确决定后才追加 `gate_decided` 并继续。
   - `ic_memo` 只生成并审查 `06-ic-memo-review.md`，通过自身证据审查后进入 `ic_review`。
   - `ic_review` 请求人工闸门，等待用户修改、停止或批准预审。
   - 仅当 `gate_decided=approve` 时调用 `jvc-ic-memo` 生成并校验发布 `06-ic-memo.md`，然后进入 `decision_record`。
6. 新资料先登记来源和指纹；只根据事件中已有的 `depends_on` / Claim 引用标记 `artifact_marked_stale`。依赖不明确时列出候选影响，不猜测、不自动重写。
7. 每轮结束前运行 `check`，实际读取 `STATE.md`、`CHANGELOG.md`、`PROJECTS.md` 与本轮研究工件。

## 完成与停止

- `ready` 才能称研究完成；`partial` 必须显式标注缺口；`blocked` 只交付缺口与下一步。
- 身份冲突、阶段冲突、未获级别升级、事件链损坏、核心审查异常、外部法律/财务结果缺失或到达用户 `stop_at` 时，保存现有有效状态并暂停。
- 阶段交付只报告工件、研究状态、当前状态、新增事件和一个待用户决定的问题。

## Reference Map

- `references/workflow-contract.md` — 阶段、原子 Skill 路由、工件、人工闸门与停止规则。
- `references/project-event-contract.md` — 四个命令、事件字段、状态变化、幂等、完整性和故障处理。
- `scripts/dealflowctl.py` — 项目身份、事件链、状态机和派生视图的确定性实现。
