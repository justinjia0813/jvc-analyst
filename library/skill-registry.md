# Skill Registry

这里记录 `jvc-analyst` 已收录的 skills。

`meeting-notes` 和 `invoice-manager` 的原始实现已经并入本仓库。旧 GitHub 仓库只作为来源记录，当前实现和安装入口以本仓库为准。

| Skill | 事实来源 | 本地入口 | 工具集角色 | 触发位置 |
| --- | --- | --- | --- | --- |
| `jvc-prescreen` | 本仓库 | `skills/jvc-prescreen/SKILL.md` | 对项目素材做结构化初筛，输出事实摘要、七维判断、bear case 雏形和问题清单。 | `/jvc-prescreen` |
| `jvc-bull-case` | 本仓库 | `skills/jvc-bull-case/SKILL.md` | 从行业趋势、技术节点、团队优势、商业化进展四个层面提炼投资亮点。 | `/jvc-bull-case` |
| `jvc-bear-case` | 本仓库 | `skills/jvc-bear-case/SKILL.md` | 从挑剔 LP、竞品 CEO、怀疑论同行三个视角提炼反方论证和可证伪风险假设。 | `/jvc-bear-case` |
| `jvc-track-research` | 本仓库 | `skills/jvc-track-research/SKILL.md` | 快速构建产业知识图谱，梳理行业简史、技术路线、产业趋势和关键玩家。 | `/jvc-track-research` |
| `jvc-comps-dd` | 本仓库 | `skills/jvc-comps-dd/SKILL.md` | 调研竞争对手和可比公司，输出上市公司与初创公司对比 Excel。 | `/jvc-comps-dd` |
| `jvc-market-sizing` | 本仓库 | `skills/jvc-market-sizing/SKILL.md` | 针对细分赛道做自上而下和自下而上市场规模建模，输出 Excel。 | `/jvc-market-sizing` |
| `jvc-roi-modeler` | 本仓库 | `skills/jvc-roi-modeler/SKILL.md` | 根据五年财务预测、融资稀释和退出情形计算投资回报，输出 Excel。 | `/jvc-roi-modeler` |
| `jvc-ic-memo` | 本仓库 | `skills/jvc-ic-memo/SKILL.md` | 将项目素材合成为 IC memo Markdown 初稿，保留风险、待决事项和来源索引。 | `/jvc-ic-memo` |
| `jvc-meeting-notes` | 本仓库，整合自 <https://github.com/justinjia0813/meeting-notes> | `skills/jvc-meeting-notes/SKILL.md` | 把逐字稿和用户笔记整理成结构化 `.docx` 访谈纪要。 | `/jvc-meeting-notes` |
| `jvc-invoice-manager` | 本仓库，整合自 <https://github.com/justinjia0813/invoice-manager> | `skills/jvc-invoice-manager/SKILL.md` | OCR 识别差旅发票，生成报销汇总 Excel，并按行程/项目归档 PDF。 | `/jvc-invoice-manager` |

## 接入规则

- 原始材料保持本地存放。不要把 BP、逐字稿、财务文件、创始人沟通记录上传到第三方网页工具。
- `jvc-meeting-notes` 的输出视为事实层材料。任何解读、不确定性、回避回答、尽调缺口，都写入对应项目 Markdown 文件。
- `jvc-invoice-manager` 只作为运营基础设施。它可以在归档命名中引用项目 slug，但不参与投资判断。
- 新增 skill 必须使用 `jvc-` 前缀，并通过 `setup` 注册。
