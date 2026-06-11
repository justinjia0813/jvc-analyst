# vc-analyst

`vc-analyst` 是一个本地优先的早期 VC 尽调工具集，面向中国市场人民币基金的 Pre-seed 到 Series B 项目。

这个工具集不替人做投资决策。它负责结构化证据、暴露缺口、准备问题，并让项目档案可以在不同对话中恢复上下文。

## 当前范围

- Pre-seed 到 Series B 项目的档案目录约定
- Markdown 优先的工作流环节：intake、prescreen、模块化 DD、founder sync、bear case、ref check、IC memo、decision archive、retro
- 高频相邻工作的外部 skill 收录表

## 已收录 Skills

| Skill | 来源仓库 | 在本工具集里的作用 |
| --- | --- | --- |
| `prescreen` | 本仓库 | 对项目素材做结构化初筛，输出事实摘要、七维判断、bear case 雏形和问题清单。 |
| `meeting-notes` | <https://github.com/justinjia0813/meeting-notes> | 把访谈逐字稿和用户笔记整理成结构化 Word 纪要，服务 `/intake`、`/founder-sync`、`/ref-check`。 |
| `invoice-manager` | <https://github.com/justinjia0813/invoice-manager> | 作为运营辅助，处理差旅发票 OCR、报销汇总表生成、按行程归档。 |

本地收录入口见 [`library/skill-registry.md`](library/skill-registry.md) 和 [`skills/`](skills/)。

## 仓库结构

```text
.
├── CLAUDE.md
├── WORKFLOW.md
├── examples/
│   └── prescreen-example.md
├── library/
│   └── skill-registry.md
├── scripts/
│   └── check-prescreen-assets.sh
├── skills/
│   ├── invoice-manager/
│   │   └── SKILL.md
│   ├── meeting-notes/
│   │   └── SKILL.md
│   └── prescreen/
│       └── SKILL.md
└── templates/
    └── prescreen-template.md
```

后续项目档案应遵守 [`WORKFLOW.md`](WORKFLOW.md) 定义的结构。保密项目材料应只放在本地 `projects/{company-slug}/00-source/`，不要上传到第三方工具。
