# jvc-analyst

`jvc-analyst` 是一个本地优先的早期 VC 尽调工具集，面向中国市场人民币基金的 Pre-seed 到 Series B 项目。

这个工具集不替人做投资决策。它负责结构化证据、暴露缺口、准备问题，并把访谈纪要、竞品表、市场规模、回报模型、IC memo 和报销归档放到同一个可安装的 skill 工具集中。

## 安装

```bash
git clone https://github.com/justinjia0813/jvc-analyst.git
cd jvc-analyst
./setup
```

`setup` 会把 `skills/jvc-*` 注册到本机已检测到的平台 skill 目录中，例如 `~/.codex/skills/` 和 `~/.claude/skills/`。

## 当前范围

- Pre-seed 到 Series B 项目的档案目录约定
- Markdown 与 Excel 并行的投资工作流：prescreen、bull-case、bear-case、track-research、comps-dd、market-sizing、roi-modeler、IC memo
- 内置会议纪要生成：原 `meeting-notes` repo 已整合为 `/jvc-meeting-notes`，高管/客户访谈可用 `/jvc-talk-notes` 输出问答纪要
- 内置发票整理：原 `invoice-manager` repo 已整合为 `/jvc-invoice-manager`

## Skills

| Skill | 作用 | 输出 |
| --- | --- | --- |
| `jvc-prescreen` | 对项目素材做结构化初筛，输出事实摘要、七维判断、bear case 雏形和问题清单。 | Markdown |
| `jvc-bull-case` | 从行业趋势、技术节点、团队优势、商业化进展四个层面提炼投资亮点。 | Markdown |
| `jvc-bear-case` | 从挑剔 LP、竞品 CEO、怀疑论同行、IC boss 四个视角提炼反方论证和可证伪风险假设。 | Markdown |
| `jvc-track-research` | 快速构建产业知识图谱，梳理行业简史、技术路线、产业趋势和关键玩家。 | Markdown |
| `jvc-comps-dd` | 调研竞争对手和可比公司，输出上市公司与初创公司对比表。 | Excel |
| `jvc-market-sizing` | 针对细分赛道做自上而下和自下而上市场规模建模。 | Excel |
| `jvc-roi-modeler` | 根据五年财务预测、融资稀释和退出情形计算投资回报。 | Excel |
| `jvc-ic-memo` | 将项目素材合成为 IC memo Markdown 初稿，保留风险、待决事项和来源索引。 | Markdown |
| `jvc-meeting-notes` | 把逐字稿和用户笔记整理成结构化 Word 访谈纪要。 | DOCX |
| `jvc-talk-notes` | 把高管访谈、客户访谈和专家访谈整理成问答式 Word 纪要。 | DOCX |
| `jvc-invoice-manager` | OCR 识别差旅发票，生成报销汇总 Excel，并按行程/项目归档 PDF。 | Excel + PDF archive |

## 仓库结构

```text
.
├── CLAUDE.md
├── WORKFLOW.md
├── examples/
├── library/
│   └── skill-registry.md
├── scripts/
│   ├── check-jvc-assets.sh
│   ├── check-excel-workbooks.sh
│   ├── generate-workbook.py
│   └── validate-workbook.py
├── skills/
│   ├── jvc-bear-case/
│   ├── jvc-bull-case/
│   ├── jvc-comps-dd/
│   ├── jvc-ic-memo/
│   ├── jvc-invoice-manager/
│   ├── jvc-market-sizing/
│   ├── jvc-meeting-notes/
│   ├── jvc-prescreen/
│   ├── jvc-roi-modeler/
│   ├── jvc-talk-notes/
│   └── jvc-track-research/
├── templates/
└── setup
```

后续项目档案应遵守 [`WORKFLOW.md`](WORKFLOW.md) 定义的结构。保密项目材料只放在本地 `projects/{company-slug}/00-source/`，不要上传到第三方工具。
