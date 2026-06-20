# Review Studio

日期：2026-06-20

Decision: `reviewable_with_warnings`

## 缩写说明

| 缩写 | 英文全称 | 中文全称 | 含义 |
| --- | --- | --- | --- |
| IR | Intermediate Representation | 中间表示 | `reports/skill-ir.json` 中的 skill 语义契约 |
| Eval | Evaluation | 评估 | 路由和输出质量检查 |
| A/B | A/B Test | A/B 对照测试 | 隐藏来源的双版本输出比较 |
| CLI | Command-Line Interface | 命令行接口 | 脚本运行接口 |
| JSON | JavaScript Object Notation | JavaScript 对象表示法 | 机器可读报告格式 |
| YAML | YAML Ain't Markup Language | YAML 不是标记语言 | 人可读配置格式 |

## Gate Summary

| Gate | Status | Evidence | Review Action |
| --- | --- | --- | --- |
| Intent Canvas | pass | `reports/skill-ir.json` |  |
| Trigger Lab | warn | `evals/trigger_cases.json`, `reports/route_scorecard.md` | Add model-executed route evidence plus blind/adversarial holdout |
| Output Lab | warn | `evals/output/cases.json`, `reports/output_quality_scorecard.md` | Add file-backed fixtures, baseline vs with-skill runs, blind A/B review |
| Context Budget | pass | `reports/yao-meta-skill-audit-2026-06-20.md` |  |
| Runtime Matrix | warn | `agents/interface.yaml` | Generate packaged adapters and conformance matrix before external distribution |
| Trust Report | warn | `reports/trust_report.md` | Pin dependencies and convert invoice CLIs to argparse |
| Permission Gates | pass | `security/permission_policy.json` |  |
| Runtime Permission Probes | warn | `agents/interface.yaml` | Run packaged adapter permission probes after a dist package exists |
| Skill Atlas | warn | `reports/skill-ir.json` | Generate full route atlas before library release |
| Operations Loop | warn | audit report | Add drift reporting only after real team usage data exists |
| Review Waivers | pass | this file | No warning waivers accepted in this pass |
| Registry Audit | warn | `manifest.json` | Add package/install simulation before external registry release |
| Release Notes | pass | this file |  |

## Release Notes

- Added production governance assets: `manifest.json`, `agents/interface.yaml`, Skill IR, security policies, trust report, and Review Studio.
- Added full local eval coverage for 11 `jvc-*` skills.
- Current release posture is production governance with warnings, not governed public release readiness.
