# Skill Registry

这里记录 `vc-analyst` 已收录的外部 skills。

外部仓库仍然是实现代码的事实来源。本仓库只保存工作流层面的接入说明，避免复制一份未来会漂移的代码。

| Skill | 事实来源 | 本地入口 | 工具集角色 | 触发位置 |
| --- | --- | --- | --- | --- |
| `prescreen` | 本仓库 | `skills/prescreen/SKILL.md` | 对项目素材做结构化初筛，输出事实摘要、七维判断、bear case 雏形和问题清单。 | `/prescreen` |
| `ic-memo` | 本仓库 | `skills/ic-memo/SKILL.md` | 将项目素材合成为 IC memo Markdown 初稿，保留风险、待决事项和来源索引。 | `/ic-memo` |
| `meeting-notes` | <https://github.com/justinjia0813/meeting-notes> | `skills/meeting-notes/SKILL.md` | 把逐字稿和用户笔记整理成结构化 `.docx` 访谈纪要。 | `/intake`, `/founder-sync`, `/ref-check` |
| `invoice-manager` | <https://github.com/justinjia0813/invoice-manager> | `skills/invoice-manager/SKILL.md` | OCR 识别差旅发票，生成报销汇总 Excel，并按行程/项目归档 PDF。 | 运营辅助，不进入投资决策流程 |

## 接入规则

- 原始材料保持本地存放。不要把 BP、逐字稿、财务文件、创始人沟通记录上传到第三方网页工具。
- `meeting-notes` 的输出视为事实层材料。任何解读、不确定性、回避回答、尽调缺口，都写入对应项目 Markdown 文件。
- `invoice-manager` 只作为运营基础设施。它可以在归档命名中引用项目 slug，但不参与投资判断。
- 外部 skill 实现发生变化时，只更新 registry 和 `WORKFLOW.md` 的链接/说明，不把上游代码粘贴进本仓库。
