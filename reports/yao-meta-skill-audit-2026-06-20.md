# jvc skills meta-skill audit

日期：2026-06-20

依据：`yao-meta-skill` 的 Skill Engineering Method、Operating Modes、Resource Boundary Spec、Skill IR Method、Output Eval Method、Review Studio Method。

## 术语缩写说明

| 缩写 | 英文全称 | 中文全称 | 本报告中的含义 |
| --- | --- | --- | --- |
| AI | Artificial Intelligence | 人工智能 | 辅助整理材料和生成结构化输出的模型能力 |
| VC | Venture Capital | 风险投资 | 本工具箱服务的早期投资工作流 |
| BP | Business Plan | 商业计划书 | 创始人或项目方提供的融资材料 |
| DOCX | Office Open XML Word Document | Word 文档格式 | `jvc-meeting-notes` 和 `jvc-talk-notes` 的输出格式 |
| PDF | Portable Document Format | 便携式文档格式 | deck、发票和归档票据的常见输入或输出格式 |
| OCR | Optical Character Recognition | 光学字符识别 | `jvc-invoice-manager` 从发票 PDF 中提取文字的能力 |
| LP | Limited Partner | 有限合伙人 | `jvc-bear-case` 中从基金出资人角度审视回报风险 |
| CEO | Chief Executive Officer | 首席执行官 | `jvc-bear-case` 中从竞品经营者角度攻击项目弱点 |
| IC | Investment Committee | 投资委员会 | `jvc-bear-case` 和 `jvc-ic-memo` 面向的投决会审查场景 |
| IP | Intellectual Property | 知识产权 | 技术资产、代码、专利、软著和发明转让的权属问题 |
| TAM | Total Addressable Market | 总可触达市场 | 最大理论市场空间 |
| SAM | Serviceable Available Market | 可服务市场 | 当前产品和地域约束下可服务的市场 |
| SOM | Serviceable Obtainable Market | 可获得市场 | 在一定时间内可实际获取的市场份额 |
| MOIC | Multiple on Invested Capital | 投资资本倍数 | 投资回款与投入资本的倍数 |
| IRR | Internal Rate of Return | 内部收益率 | 按时间折现后的年化回报率 |
| IR | Intermediate Representation | 中间表示 | 跨平台包装前保留 skill 语义契约的结构化描述 |
| Eval | Evaluation | 评估 | 对路由触发和输出质量进行可复查测试 |
| Q&A | Question and Answer | 问答 | `jvc-talk-notes` 的问题和回答式纪要结构 |
| PR | Public Relations | 公共关系 | 公司新闻稿、融资稿或营销稿，不能直接当作技术事实 |

## 总体判断

`jvc-*` 当前是一个 Production 形态的本地优先 VC 尽调 skill suite：重复使用真实存在，输出契约清楚，脚本和模板已经承担了部分确定性逻辑，安装路径也可验证。现在已补第一版 route eval 和 output eval 的 deterministic fixture evidence。它还不是 Library 或 Governed 形态，因为 model-executed eval、blind holdout、Skill IR、trust report、Review Studio 和 package registry evidence 仍是 `missing evidence`。

这次不建议把每个 `SKILL.md` 扩写成更长的知识库。更好的方向是保持入口轻量，把评估、风险、示例和治理证据放进 `reports/`、`examples/`、`templates/`、`scripts/` 和未来的 `evals/`。

## 本次修正

| 修正 | 原因 | 文件 |
| --- | --- | --- |
| `jvc-bear-case` 模板和示例补齐第四角色 `IC boss` | `SKILL.md` 已要求四角色，但模板和示例仍是三角色，会引导旧版输出 | `templates/bear-case-template.md`, `examples/bear-case-example.md` |
| Excel 模板输出文件名补 `jvc-` 前缀 | `SKILL.md` 要求 `{项目或赛道}_jvc-*_{YYYYMMDD}.xlsx`，模板仍是旧短名 | `templates/comps-dd-template.md`, `templates/market-sizing-template.md`, `templates/roi-modeler-template.md` |
| 资产检查新增上述漂移断言 | 防止后续回归时脚本仍然通过 | `scripts/check-jvc-assets.sh` |
| 新增 route eval 第一版 | 覆盖 `meeting-notes` vs `talk-notes`、`bull-case` vs `ic-memo`、`track-research` vs `comps-dd` 等近邻混淆 | `evals/trigger_cases.json`, `reports/route_scorecard.md` |
| 新增 output eval 第一版 | 覆盖 Markdown、Excel、DOCX、Excel + PDF archive 四类输出契约 | `evals/output/cases.json`, `reports/output_quality_scorecard.md` |
| 新增本地 eval 检查脚本 | 让 route/output fixture 纳入总回归，避免只写报告不可执行 | `scripts/check-skill-evals.py`, `scripts/check-review-fixes.sh` |
| 新增治理资产 | 补 `manifest`、`agents/interface.yaml`、Skill IR、security policy、trust report、Review Studio 和治理检查 | `manifest.json`, `agents/interface.yaml`, `reports/skill-ir.json`, `reports/trust_report.md`, `reports/review-studio.md`, `scripts/check-governance.py` |

## 模式划分

| Skill | 建议模式 | 依据 | 当前缺口 |
| --- | --- | --- | --- |
| `jvc-prescreen` | Production | 高频入口，输出事实摘要、七维判断、bear case 雏形和问题清单 | 已有 v0 输出契约 fixture；缺真实输入和模型执行证据 |
| `jvc-bull-case` | Production | 可复用的正向论点提炼，已要求来源和待验证项 | 已有近邻路由 fixture；缺 model-executed route evidence |
| `jvc-bear-case` | Production | 决策前反方压力测试，角色边界清楚 | 已修四角色资产并纳入 output fixture；缺真实项目样例评分 |
| `jvc-track-research` | Production | 联网研究、来源分层和技术路线拆解风险较高 | 已有路由和示例输出 fixture；缺 citation risk 的真实检索样例 |
| `jvc-comps-dd` | Production | Excel workbook 有模板、生成和校验脚本 | 已有 workbook sheet fixture；缺真实 file-backed fixture |
| `jvc-market-sizing` | Production | TAM/SAM/SOM 与正交检查可复用，已有 workbook 校验 | 已有 workbook sheet fixture；缺真实市场口径案例 |
| `jvc-roi-modeler` | Production | MOIC/IRR、逐轮稀释和敏感性分析有结构化 workbook | 已有 workbook sheet fixture；缺条款边界和缺失输入场景样例 |
| `jvc-ic-memo` | Production | 汇总前序材料，明确不替代投决 | 已有近邻路由 fixture；缺风险篇幅、来源追溯的自动输出检查 |
| `jvc-meeting-notes` | Production | 文件生成真实存在，DOCX 版式和命名有回归检查 | 已有 DOCX 契约 fixture；缺脱敏逐字稿 fixture |
| `jvc-talk-notes` | Production | 与 meeting-notes 共享生成器，Q&A 输出契约明确 | 已有 Q&A DOCX 契约 fixture；缺 transcript-to-Q&A 真实输出样例 |
| `jvc-invoice-manager` | Production-ops | 运营辅助，OCR/PDF/Excel 脚本真实存在，边界清楚 | 因涉及票据和金额，若外部分发需 trust report |

## Gate 状态

| Gate | 状态 | 证据 |
| --- | --- | --- |
| Resource boundary | pass | `SKILL.md` 入口较轻，模板、脚本、示例分离；长逻辑集中在 `scripts/` 和 `templates/` |
| Install path | pass | `setup` 注册 11 个 `jvc-*` skills；`library/skill-registry.md` 记录入口 |
| Deterministic checks | pass | `scripts/check-jvc-assets.sh`、`scripts/check-review-fixes.sh`、workbook 校验、DOCX 命名/版式检查 |
| Trigger lab | warn | 已有 `evals/trigger_cases.json` 和 `reports/route_scorecard.md`；仍缺 model-executed route run、blind holdout 和 adversarial holdout |
| Output lab | warn | 已有 `evals/output/cases.json` 和 `reports/output_quality_scorecard.md`；仍缺 baseline vs with-skill delta、file-backed fixture 和 blind A/B review |
| Context budget | pass | 当前单个 `SKILL.md` 约 57-115 行，没有把长政策塞进入口 |
| Trust report | warn | 脚本面较清楚，但没有 secret scan、依赖 pinning、permission ledger 或 package hash |
| Skill IR / target compiler | missing evidence | 当前没有 suite-level Skill IR、manifest 或 `agents/interface.yaml`；若只作为本地 skill suite，这不是阻塞项 |
| Review Studio | missing evidence | 未生成 `reports/review-studio.*`，不应声称已完成 Library/Governed release |

## 输出风险画像

| 输出族 | 主要风险 | 当前防线 | 下一步 |
| --- | --- | --- | --- |
| Markdown 尽调材料 | 空泛结论、无来源数字、过早投资建议 | `SKILL.md` 硬约束、示例模板和 output fixture | 增加真实脱敏输入和模型输出评分 |
| 联网赛道研究 | 把公司 PR 当技术事实、把融资报道当商业化证据 | `jvc-track-research` 已要求来源分层和术语消歧，并有 route/output fixture | 增加 citation risk 的真实检索样例 |
| Excel workbook | 表结构漂移、公式丢失、文件名不一致 | `generate-workbook.py`、`validate-workbook.py`、文件名修正和 workbook sheet fixture | 增加真实脱敏 workbook fixture |
| DOCX 纪要 | 模板错用、版式不一致、手动换行拉伸、文件名回退旧格式 | DOCX 三个检查脚本、共享生成器和 DOCX 契约 fixture | 增加脱敏 transcript fixture 和打开抽查记录 |
| 发票归档 | OCR 误读金额、误删原件、把运营票据混入投资判断 | 人工确认、只复制 PDF、非投资流程边界 | 若分发给团队，补 trust report 和权限说明 |

## 下一步建议

1. 把当前 deterministic fixture 升级为 file-backed fixture：为 prescreen、track-research、meeting-notes、talk-notes 各补 1 个脱敏输入和期望输出。
2. 加 model-executed eval runner：记录 baseline vs with-skill delta、失败 taxonomy 和 blind A/B review pack。
3. 若要团队分发或对外发布，再补 Skill IR、`agents/interface.yaml`、manifest、trust report、Review Studio；否则当前本地工具箱不需要为了形式增加重资产治理。
