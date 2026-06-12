---
name: jvc-meeting-notes
description: |
  访谈纪要生成：根据会议逐字稿、用户随笔和会议基本信息生成结构化 Word 访谈纪要，作为创始人访谈、客户访谈、专家访谈和背调电话的事实层入口。
  Use when user says '访谈纪要', '会议纪要', '整理逐字稿', 'meeting notes', '生成纪要'.
integrated_from: https://github.com/justinjia0813/meeting-notes
---

# /jvc-meeting-notes — 访谈纪要生成

`/jvc-meeting-notes` 是 `jvc-analyst` 内置的事实层生成器。它把 AI 转写逐字稿和用户随笔融合成结构化 `.docx`，供后续 `/jvc-prescreen`、项目访谈笔记或 `/jvc-ic-memo` 引用。

## 输入

- AI 转写逐字稿或会议纯文本
- 用户随笔、补充判断、现场观察
- 会议日期、线上/线下、项目名称
- 可选：希望强调的章节或必须保留的原话

## 输出

`.docx` Word 文件，命名规则：

`{YYYYMMDD}_{项目名称}_访谈纪要.docx`

默认模板是中性公开模板，不包含任何基金或机构品牌：

`skills/jvc-meeting-notes/templates/访谈纪要模板.docx`

默认模板采用内置 meeting-notes 标准版式：A4 页面，页边距为上/下 2.54cm、左/右 3.17cm；标题居中 18pt 加粗；章节标题 10pt 加粗；正文和子标题 10pt 常规；正文两端对齐，并启用 `doNotExpandShiftReturn` 避免手动换行短行被强行拉满；段落使用 `Normal` 并通过 run 级字体格式呈现。

用户可自定义 `.docx` 模板。生成器会抽取模板中的页面设置、样式、页眉和页脚，清空正文占位内容后写入新的纪要正文。如果模板里有示例段落，脚本会按前几个非空段落抽取标题、章节、正文和子标题样式；如果模板只提供 `Normal` 样式，则按默认 meeting-notes 标准直接写入标题、章节、正文和子标题的字体格式。模板解析顺序：

1. 命令行 `--template path/to/template.docx`
2. 环境变量 `JVC_DOCX_TEMPLATE=/path/to/template.docx`
3. 放置本地文件 `skills/jvc-meeting-notes/templates/custom.docx`
4. 使用中性默认模板 `skills/jvc-meeting-notes/templates/访谈纪要模板.docx`

## 结构

默认六段式：

1. 公司基本情况
2. 公司核心技术
3. 公司核心团队
4. 公司核心产品
5. 商业化进展
6. 融资情况

## 生成流程

1. 先把逐字稿和随笔整理成 JSON，保留事实、原话和不确定项。
2. 确认 JSON 中包含 `title`、`filename`、`sections`。
3. 运行：

```bash
python3 skills/jvc-meeting-notes/scripts/generate_meeting_notes.py data.json \
  --output output/20260611_项目名称_访谈纪要.docx
```

如需显式指定用户自己的模板：

```bash
python3 skills/jvc-meeting-notes/scripts/generate_meeting_notes.py data.json \
  --template path/to/your-template.docx \
  --output output/20260611_项目名称_访谈纪要.docx
```

## JSON 骨架

```json
{
  "title": "2026/06/11 线上 访谈{项目名称}",
  "filename": "20260611_项目名称_访谈纪要.docx",
  "sections": [
    {
      "heading": "一、公司基本情况",
      "content": "公司简介..."
    },
    {
      "heading": "二、公司核心技术",
      "subsections": [
        {"heading": "技术路线", "content": "..."}
      ]
    }
  ]
}
```

## 质量红线

- `.docx` 是事实层材料，不要静默加入投资结论。
- 创始人未经验证的陈述保留为事实来源，不改写成已验证事实。
- 用户随笔中的疑问、迟疑、反常观察不能丢，必要时标 `[用户观察]` 或 `[待交叉验证]`。
- 输出文件必须是 `.docx` 文件，不要把 `--output` 传成目录后误以为目录就是交付物。
- 不要把任何个人或机构专属模板当作 public 默认模板；用户模板只通过 `--template`、`JVC_DOCX_TEMPLATE` 或本地 `custom.docx` 引入。
- 生成后应确认文件存在；重要纪要建议抽查打开。

## 依赖

```bash
python3 -m pip install -r skills/jvc-meeting-notes/requirements.txt
```
