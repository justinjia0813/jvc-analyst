# 项目事件合同

## 事实源

`<project-dir>/.jvc/project_events.jsonl` 是项目身份、工作流、来源、工件和人工闸门的唯一操作历史。不得直接编辑、删除、插入或重排。

`evidence_registry.jsonl` 回答“研究主张为什么成立”；`project_events.jsonl` 回答“项目何时发生了什么”；`decision-journal.md` 保存人的决定与理由。三者不合并。

## 四个命令

```bash
python3 dealflowctl.py init --library-root <path> --project-name <name>
python3 dealflowctl.py event --project-dir <path> --input <event.json>
python3 dealflowctl.py check --project-dir <path>
python3 dealflowctl.py list --library-root <path>
```

- `init` 创建 `.jvc-library.json`、不可变 `project_id`、首事件和派生视图；名称或别名唯一匹配时恢复，不重复建档。已知项目标识时可加 `--project-id <uuid>` 精确恢复；遇到近似名称会停下列出候选，只有用户确认确属新项目后才能加 `--confirm-new`。
- `event` 校验事件、当前 `from`、状态转换、人工批准、引用指纹和哈希链，再原子追加并重建视图。
- `check` 校验 sequence、事件标识、项目标识、前序哈希、事件哈希、工件指纹和派生视图；缺失视图可重建，手工改写的视图只报 drift（漂移），不覆盖。
- `list` 只扫描事件链并重建 `PROJECTS.md`；不运行研究、不写业务事件。

## 事件输入

最小示例：

```json
{
  "event_id": "evt_stable_caller_id",
  "event_type": "workflow_transitioned",
  "actor": "codex",
  "trigger": "用户要求推进至尽调前审核",
  "reason": "Data Layer 与 Invest Memo 已审查",
  "from": {"workflow_stage": "invest_memo"},
  "to": {
    "workflow_stage": "pre_dd_review",
    "next_action": "请求用户审核是否进入尽调"
  },
  "input_refs": [],
  "output_refs": [],
  "approval_ref": null,
  "supersedes": null
}
```

脚本补齐 `schema_version`、`sequence`、`occurred_at`、`project_id`、`run_id`、`producer`、`previous_event_hash` 和 `event_hash`。同一 `event_id` 与同一输入重放返回已有事件；内容不同则按碰撞失败。

引用可以是路径字符串或对象。文件存在时脚本写入 SHA-256（Secure Hash Algorithm 256-bit，256 位安全哈希算法，用于内容完整性指纹）；它不证明内容真实。

## 事件类型与权限

支持：

- 身份与来源：`project_initialized`、`project_renamed`、`source_registered`、`source_superseded`
- 工件：`artifact_created`、`artifact_updated`、`artifact_marked_stale`、`artifact_audited`
- 状态：`workflow_transitioned`、`research_level_changed`、`lifecycle_changed`
- 人工闸门：`gate_requested`、`gate_decided`、`decision_recorded`
- 故障与更正：`error_recorded`、`project_reconciled`

研究级别变化、项目改名、闸门决定、最终决定、恢复/关闭/归档和状态更正必须带非空 `approval_ref`。`decision_status` 只允许 `undecided`、`invest`、`pass`、`wait`，且只有 `decision_recorded` 可写终局值。

## 状态转换

正常前进遵循工作流合同。审查阶段向前必须已有同一闸门的 `approve`；返回修改必须已有 `revise`；两者在后续 `workflow_transitioned` 中再次携带 `approval_ref`。进入 `diligence` 至少 L2，进入 `ic_memo` 至少 L3。

`gate_requested` 必须与当前 review 阶段相同，并把生命周期设为 `paused`。`gate_decided=approve` 清空当前闸门、记录 `last_approved_gate` 并恢复 `active`。

`project_reconciled` 可以在用户批准下更正当前状态，但仍须保持跨轴不变量：阶段满足最低研究级别；打开的闸门与当前审查阶段一致且项目为 `paused`；终局决定只存在于 `decision_record`。更正 `workflow_stage` 或 `current_gate` 会立即作废旧闸门决定，回到审查阶段后必须重新请求和批准。

## 工件与依赖

`artifact_created` / `artifact_updated` 的 `output_refs` 至少含：

```json
{
  "path": "INVEST_MEMO.md",
  "producer": "jvc-deal-flow",
  "depends_on": ["evt_source_1", "C12"]
}
```

新证据只对显式依赖它的工件追加 `artifact_marked_stale`。没有显式依赖时报告候选影响并停下，不创建伪精确关系。

`artifact_audited` 只接受已登记且状态为 `current` 的工件，并要求当前文件指纹与登记指纹一致；审查事件不得刷新工件指纹。工件内容变化必须先通过 `artifact_updated` 登记。

## 故障

- 项目事件链和项目库索引分别使用单写者锁；跨项目改名同时持有项目锁与项目库锁。任何锁冲突都失败关闭。
- 先完整校验再追加；事件追加后视图生成中断，可由 `check` 重建。
- 哈希链损坏、事件标识重复、旧 `from`、非法状态或指纹不符时不写任何新事件。
- 手工修改工件或派生视图只报告漂移；需要接受变化时由用户批准 `project_reconciled`，不改写旧行。
- 日志不得包含密钥、支付信息、完整 prompt、隐藏推理或大段敏感原文。
