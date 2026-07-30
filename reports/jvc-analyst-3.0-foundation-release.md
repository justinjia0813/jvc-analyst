# JVC Analyst 3.0 第一阶段发布说明

日期：2026-07-30

状态：`foundation_ready_with_manual_gates`

## 本次完成

- 建立 L0–L3（Research Level 0–3，研究级别 0–3，用于按决策场景控制流程密度）四级研究分级，并写入仓库与全部 13 个用户 Skill。
- README 采用唯一项目目录合同；旧项目只在升级级别时增量补 `spec/`、`evidence/`、`STATE.md` 和 `decision-journal.md`，不迁移或修改 `00-source/`。
- 全部用户 Skill 增加任务特定的反合理化约束；运营类 `/jvc-invoice-manager` 明确不进入投资研究分级。
- 新增 `project-context-template.md` 与 `hypotheses-template.md`，假设格式对齐 Claim（可验证主张）的认识论类型、证据状态、证伪条件、支持/反驳证据和 `motive_check`。
- 新增 `scripts/check-v3-foundation.py`，以安装包公开合同验证版本、级别、模板和反合理化覆盖。

## 复用与边界

- 复用 2.0 的 `jvc-research-core`，未新建证据运行时。
- 本次仅完成 `inspired-design.md` 路线图第一阶段；`/jvc-compound`、决策日志提醒、验证 lint、虚拟投委会、Research Loop、DAG（Directed Acyclic Graph，有向无环图，用于表达研究任务依赖）和实体图谱仍按后续阶段推进。
- 2.0 的路由、产物和盲审报告继续作为历史基线，不改写为 3.0 新证据。

## 尚待人工验收

- 当前仓库没有可迁移的真实 `projects/` 档案，因此未用虚构 fixture 冒充“真实项目归档”指标。
- 当前检查可证明 Skill 合同存在且既有产物未回归；尚未运行模型生成的 V3 输出抽查，不能把字符串检查表述为反合理化行为已经在真实任务中生效。

## 可复核检查

```bash
python3 scripts/check-v3-foundation.py
python3 scripts/check-skill-evals.py
python3 scripts/check-governance.py
```

以上检查通过且治理哈希刷新后，只能称 3.0 代码基础就绪；真实项目迁移与模型输出抽查两个人工 gate 通过后，才能称第一阶段完整验收。
