# Review Studio

日期：2026-08-09

Decision: `reviewable_with_warnings`

## 缩写说明

| 缩写 | 英文全称 | 中文全称 | 含义 |
| --- | --- | --- | --- |
| IR | Intermediate Representation | 中间表示 | `reports/skill-ir.json` 中的 skill 语义契约 |
| Eval | Evaluation | 评估 | 路由和输出质量检查 |
| A/B | A/B Test | A/B 对照测试 | 隐藏来源的双版本输出比较 |
| CLI | Command-Line Interface | 命令行接口 | 脚本运行接口 |
| PDF | Portable Document Format | 便携式文档格式 | 固定版式研究报告的可打印文件格式 |
| URI | Uniform Resource Identifier | 统一资源标识符 | 标识资源位置或内嵌数据的字符串；`data:` URI 用于内嵌本地资源 |
| JSON | JavaScript Object Notation | JavaScript 对象表示法 | 机器可读报告格式 |
| YAML | YAML Ain't Markup Language | YAML 不是标记语言 | 人可读配置格式 |
| CSV | Comma-Separated Values | 逗号分隔值 | 用逗号分隔字段的纯文本表格格式 |
| HTML | HyperText Markup Language | 超文本标记语言 | 浏览器预览使用的页面结构格式 |

## Gate Summary

| Gate | Status | Evidence | Review Action |
| --- | --- | --- | --- |
| Intent Canvas | pass | `reports/skill-ir.json`；`manifest.json` |  |
| Trigger Lab | warn | `evals/trigger_cases.json`；`scripts/check-skill-evals.py`（15 个 deterministic trigger cases） | 补模型实际运行的盲测和对抗路由保留集 |
| Output Lab | pass | 16 个输出契约；deal-flow 临时项目库端到端自检；5 个 core 真实路径案例；Research Report canonical `research-report.md` 组装示例与渲染产物；旧 2 基线/候选案例与盲审结果：顶层 11 份原件保留，带 historical legacy workbook 标记副本归档于 `reports/legacy/`，两者均不作为新 CSV 合同的证据 |  |
| Context Budget | pass | `reports/skill-ir.json`；`agents/interface.yaml` |  |
| Runtime Matrix | warn | `agents/interface.yaml` | 外部分发前生成并运行各目标平台适配器 |
| Trust Report | warn | `reports/trust_report.md`；report 依赖已锁定 | 固定其余依赖版本并保留发票命令行警告 |
| Permission Gates | pass | 本地读写/子进程审批；脚本网络默认拒绝 |  |
| Runtime Permission Probes | warn | 没有 dist package | 分发包存在后运行适配器权限探针 |
| Skill Atlas | warn | Skill IR + 15 个静态路由案例 | 补模型实际的冲突和 stale-skill 证据 |
| Operations Loop | warn | `skills/jvc-deal-flow/references/workflow-contract.md`；`skills/jvc-research-core/references/evidence-contract.md` | 有真实使用数据后再做采用率和漂移报告 |
| Review Waivers | pass | 5 个真实案例 waiver=0 |  |
| Registry Audit | pass | `check-research-core-install.py` 临时目录安装/回滚模拟 |  |
| Release Notes | pass | `reports/output_quality_scorecard.md`；`README.md`；`manifest.json`；`reports/review-studio.md` |  |

## Release Notes

- 3.0 第一阶段新增 L0–L3 研究分级、权威项目目录、项目上下文/假设模板，以及全部 14 个用户 skill 的反合理化合同。
- 14 个用户可调用 skill 与 1 个 hidden core 均有确定性路由/输出覆盖；其中 11 个原子研究 skill 与薄编排 `jvc-deal-flow` 通过固定 `jvc-research-core` 命令协议获得记录与审计能力。
- `jvc-deal-flow` 只管理项目身份、事件、状态、人工闸门和三个编排自产 Markdown 工件；没有把全部原子 Skill 固定捆绑，也没有引入数据库或 LangGraph。
- `jvc-research-report` 采用“组装 + 发布”两阶段：从已审计的赛道级上游组装 canonical `research-report.md`，再校验并渲染为 PDF/HTML；不新增事实、不联网补研究。虚构样例完成 A4 14 页文本、渲染与机械校验；主 Agent 已于 2026-08-10 用 `view_image` 逐页目检通过（记录：`reports/task9-visual/MAIN-VISUAL-INSPECTION.md`）。
- P1 完成 Track Research / Knowledge Tree / Market Sizing 的 CSV 与 visual-first 迁移；P2 完成 Comps/DD 的 Markdown 迁移与 IC Memo 的 CSV/Markdown 输入映射，预审 → 用户批准 → 干净终版闸门未放松。
- 5 个真实路径案例得到 4 `ready` 和 1 个预期 `blocked`（exit 20），无 waiver。
- 当前状态仅支持仓库内 `3.0.0` 的 `foundation_ready_with_manual_gates`；2.0 输出评测与人工盲审产物已标注 historical legacy workbook 并移出活跃治理证据。真实项目迁移与模型输出抽查通过前，不声称第一阶段完整验收；本证据也不支持声称完整 V3 路线图、governed public release（受治理的公开发布）或跨平台质量已完成。
