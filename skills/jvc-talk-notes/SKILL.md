---
name: jvc-talk-notes
description: Use when user says '高管访谈', '客户访谈', '专家访谈', '问答纪要', 'talk notes', 'Q&A notes', or asks to turn a transcript into a Q&A Word DOCX interview note.
---

# jvc-talk-notes — 问答式访谈纪要

`/jvc-talk-notes` 是 `/jvc-meeting-notes` 的问答式版本。用于高管访谈、客户访谈、专家访谈和用户访谈：当材料最适合按“问题 → 回答 → 待验证点”阅读时，用这个 skill，而不是六段式公司访谈纪要。

它仍然是事实层生成器：记录问了什么、答了什么、用户观察到什么、哪些地方还要交叉验证。不要加入投资结论。

## 输入

- AI 转写逐字稿或会议纯文本。
- 用户随笔、现场观察、会后补充判断。
- 会议日期、线上/线下、公司或项目名称、受访人角色；如已知，可加入访谈人。
- 可选：用户希望重点保留的问题、必须保留的原话、希望按主题归并的部分。

## 输出

生成 `.docx` Word 文件，命名规则：

`{YYYYMMDD}_{项目名称}_{受访人角色}_问答纪要.docx`

复用现有 meeting-notes 资产：

- `skills/jvc-meeting-notes/scripts/generate_meeting_notes.py`
- `skills/jvc-meeting-notes/templates/访谈纪要模板.docx`
- `skills/jvc-meeting-notes/requirements.txt`

默认 Word 模板是中性公开模板。用户可用三种方式替换成自己的机构模板：

1. 运行时传 `--template path/to/template.docx`
2. 设置 `JVC_DOCX_TEMPLATE=/path/to/template.docx`
3. 放置本地文件 `skills/jvc-meeting-notes/templates/custom.docx`

生成器会保留用户模板的页面设置、样式、页眉和页脚，再写入新的问答纪要正文。如果模板里有示例段落，会按前几个非空段落抽取标题、章节、正文和子标题样式；否则使用模板的 `Normal` 样式。

## 结构

默认四段式：

1. `一、访谈基本信息`
2. `二、问答纪要`
3. `三、用户观察与待交叉验证`
4. `四、后续追问清单`

每个问答条目包含：

- `问题`：保留原始问题意图；不要凭空补问题。
- `回答摘要`：把回答压缩成可复核的事实、主张和口径。
- `关键原话`：重要措辞、承诺、犹豫和反常表达要保留。
- `事实标签`：标注 `[受访者自述]`、`[客户自述]`、`[用户观察]`、`[未核实]` 或 `[推测]`。
- `待验证点`：标出回避、矛盾、数字不清、需要外部证据的问题。

## 生成流程

1. 从逐字稿和用户随笔中抽取问答对。只有语义相同的问题才合并。
2. 默认保留访谈顺序；如果按主题归并更利于复盘，可以重组，但不能丢失原问题意图。
3. 整理为 `generate_meeting_notes.py` 可消费的 JSON：

```json
{
  "title": "2026/06/12 线上 客户访谈{项目名称}",
  "filename": "20260612_项目名称_客户_问答纪要.docx",
  "sections": [
    {"heading": "一、访谈基本信息", "content": "日期、形式、项目、受访人角色、访谈目的。"},
    {
      "heading": "二、问答纪要",
      "subsections": [
        {
          "heading": "Q1：客户当前如何解决这个问题？",
          "content": "问题：...\n回答摘要：...\n关键原话：...\n事实标签：[客户自述]\n待验证点：..."
        }
      ]
    },
    {"heading": "三、用户观察与待交叉验证", "content": "..."},
    {"heading": "四、后续追问清单", "content": "..."}
  ]
}
```

4. 运行生成器并确认 `.docx` 文件存在：

```bash
python3 skills/jvc-meeting-notes/scripts/generate_meeting_notes.py data.json \
  --output output/20260612_项目名称_客户_问答纪要.docx
```

## 质量红线

- 受访者陈述不是已验证事实，除非用户提供外部证据。
- 客户需求必须区分当前使用、试点、意向和假设性需求。
- 模糊回答、回避、前后矛盾和无来源数字都要标出。
- 用户疑问和观察必须和受访者回答分开记录。
- 不要把个人或机构专属 Word 模板提交为 public 默认模板。
- 不要把它写成销售会议总结、投资 memo 或投资建议。

## 依赖

```bash
python3 -m pip install -r skills/jvc-meeting-notes/requirements.txt
```
