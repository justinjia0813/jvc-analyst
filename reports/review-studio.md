# Review Studio

日期：2026-09-29｜版本：4.0.0

Decision: `reviewable_with_warnings`

本页记录发布门控的确定性检查结果。确定性检查只证明文件结构、合同文本和脚本行为符合预期，不代表模型在真实材料上的输出质量。

## 门控

| 门控 | 状态 | 证据 | 待办 |
| --- | --- | --- | --- |
| Intent Canvas | pass | `reports/skill-ir.json` |  |
| Trigger Lab | warn | `evals/trigger_cases.json` | Run model-executed routing on blind and adversarial holdouts before claiming real routing accuracy. |
| Output Lab | warn | `evals/output/cases.json`；`examples/research-report-example/report.md`；`skills/jvc-research-report/scripts/check_package.py` | Retain deterministic checks separately from model output quality; development rerun 2/2 and locked holdout 1/3 do not establish reliable autonomous execution. |
| Context Budget | pass | `README.md` |  |
| Runtime Matrix | warn | `agents/interface.yaml` | Generate and run packaged adapters on each target platform before external distribution. |
| Trust Report | warn | `reports/trust_report.md`；`reports/trust_report.json` | Keep report dependencies pinned, pin remaining suite dependencies, and retain the documented invoice command-line warnings before broader distribution. |
| Permission Gates | pass | `security/permission_policy.json`；`security/network_policy.json` |  |
| Runtime Permission Probes | warn | `agents/interface.yaml` | Run packaged adapter permission probes after a distribution package exists. |
| Skill Atlas | warn | `reports/skill-ir.json`；`evals/trigger_cases.json` | Add model-executed collision and stale-skill evidence before claiming a complete route atlas. |
| Operations Loop | warn | `README.md` | Add adoption and drift reporting only after real team usage data exists; do not fabricate telemetry. |
| Review Waivers | pass | `reports/review-studio.md` |  |
| Registry Audit | pass | `manifest.json`；`scripts/check-research-core-install.py` |  |
| Release Notes | pass | `reports/review-studio.md` |  |

## 成熟度说明

- 10 个主要入口的合同均为 4.0 新写或重写。
- 已在真实项目材料上完成一次端到端验证的：商业经济分析。其余入口尚未在真实材料上系统复测。
- 复现全部确定性检查：`bash scripts/check-review-fixes.sh`。
