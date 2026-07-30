# Review Studio

日期：2026-07-30

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
| Trigger Lab | warn | 14 个 deterministic trigger cases | 补模型实际运行的盲测和对抗路由保留集 |
| Output Lab | pass | 14 个输出契约；5 个 core 真实路径案例；2 个基线/候选案例；2 个已裁决盲审案例；report 的 13 页文件渲染与视觉检查 |  |
| Context Budget | pass | Yao resource boundary check |  |
| Runtime Matrix | warn | `agents/interface.yaml` | 外部分发前生成并运行各目标平台适配器 |
| Trust Report | warn | `reports/trust_report.md`；report 依赖已锁定 | 固定其余依赖版本并保留发票命令行警告 |
| Permission Gates | pass | 本地读写/子进程审批；脚本网络默认拒绝 |  |
| Runtime Permission Probes | warn | 没有 dist package | 分发包存在后运行适配器权限探针 |
| Skill Atlas | warn | Skill IR + 14 个静态路由案例 | 补模型实际的冲突和 stale-skill 证据 |
| Operations Loop | warn | 无真实团队使用 telemetry | 有真实使用数据后再做采用率和漂移报告 |
| Review Waivers | pass | 5 个真实案例 waiver=0 |  |
| Registry Audit | pass | `check-research-core-install.py` 临时目录安装/回滚模拟 |  |
| Release Notes | pass | `reports/research-core-2.0-release.md` |  |

## Release Notes

- 13 个用户可调用 skill 与 1 个 hidden core 均有确定性路由/输出覆盖；其中 11 个研究业务 skill 通过固定 `jvc-research-core` 命令协议获得记录与审计能力。
- `jvc-research-report` 保持只校验、排版、不改正文的边界；虚构样例已完成 A4 13 页文本、渲染和逐页视觉检查。
- 确定性输出对照为 64.09% → 100.00%，delta +35.91 个百分点，0 regression。
- 5 个真实路径案例得到 4 `ready` 和 1 个预期 `blocked`（exit 20），无 waiver。
- Justin 的 n=2 人工盲审一胜一负：玻璃案例支持 2.0 的实用性；市场案例低置信度偏好 1.0 的格式。
- 当前状态支持仓库内 `2.0.0` 发布，不支持 governed public release（受治理的公开发布）或跨平台质量声明。
