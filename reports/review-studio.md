# Review Studio

日期：2026-07-22

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

## Gate Summary

| Gate | Status | Evidence | Review Action |
| --- | --- | --- | --- |
| Intent Canvas | pass | `reports/skill-ir.json` |  |
| Trigger Lab | warn | `evals/trigger_cases.json`, `reports/route_scorecard.md` | Add model-executed route evidence plus blind/adversarial holdout |
| Output Lab | warn | 13 个 output cases；`jvc-research-report` 的 file-backed fixture 实际生成 A4 13 页 PDF，`pdftotext` 提取预期文本，`pdftoppm` 与逐页视觉检查覆盖 13/13 页；首轮重复封面图已移除并复核 | 保留 `warn`；继续补其余产物 fixture、baseline vs with-skill、model-executed evidence 和 blind A/B review |
| Context Budget | pass | `reports/yao-meta-skill-audit-2026-06-20.md` |  |
| Runtime Matrix | warn | `agents/interface.yaml` | Generate packaged adapters and conformance matrix before external distribution |
| Trust Report | warn | `reports/trust_report.md`；报告依赖已锁定，local-only、`data:` URI、resource guards 与 transactional outputs 有本地证据 | Pin remaining suite dependencies where needed and convert invoice CLIs to argparse |
| Permission Gates | pass | `security/permission_policy.json` |  |
| Runtime Permission Probes | warn | `agents/interface.yaml` | Run packaged adapter permission probes after a dist package exists |
| Skill Atlas | warn | `reports/skill-ir.json` | Generate full route atlas before library release |
| Operations Loop | warn | audit report | Add drift reporting only after real team usage data exists |
| Review Waivers | pass | this file | No warning waivers accepted in this pass |
| Registry Audit | warn | `manifest.json` | Add package/install simulation before external registry release |
| Release Notes | pass | this file |  |

## Release Notes

- Added production governance assets: `manifest.json`, `agents/interface.yaml`, Skill IR, security policies, trust report, and Review Studio.
- Added local deterministic eval coverage for 13 `jvc-*` skills: 14 trigger cases and 13 output cases.
- Added a fictional file-backed report fixture and real A4 13-page PDF text, page-rendering, and visual evidence; the initial duplicate cover artwork was fixed before final inspection.
- This fixture evidence is self-check evidence, not model-executed or blind-review evidence.
- Current release posture is production governance with warnings, not governed public release readiness.
