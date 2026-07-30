---
name: jvc-meeting-notes
description: |
  访谈纪要生成：根据会议逐字稿、用户随笔和会议基本信息生成结构化 Word 访谈纪要，作为创始人访谈、客户访谈、专家访谈和背调电话的事实层入口。
  Use when user says '/jvc-meeting-notes', '访谈纪要', '会议纪要', '整理逐字稿', 'meeting notes', '生成纪要'.
integrated_from: meeting-notes
user_invocable: true
version: "2.0.0"
---

# /jvc-meeting-notes — 访谈纪要生成

`/jvc-meeting-notes` 是 `jvc-analyst` 内置的事实层生成器。它把 AI 转写逐字稿和用户随笔融合成结构化 `.docx`，供后续 `/jvc-prescreen`、项目访谈笔记或 `/jvc-ic-memo` 引用。

## 输入

- AI 转写逐字稿或会议纯文本
- 用户随笔、补充判断、现场观察
- 会议日期、线上/线下、项目名称
- 可选：希望强调的章节或必须保留的原话

## 2.0 证据内核（必须）

从本 `SKILL.md` 的实际目录解析同级 `../jvc-research-core/scripts/researchctl.py`，并使用绝对路径执行；不要依赖当前工作目录。

执行前必须读取同级 `../jvc-research-core/references/evidence-contract.md` 和当前 profile `../jvc-research-core/profiles/jvc-meeting-notes.json`。

1. 新研究先准备完整 `scope` JSON，再运行 `init --skill jvc-meeting-notes --run-dir <研究目录> --scope-file <scope.json>`；初始 `scope` 只能通过 `init --scope-file` 创建。
2. 复用已有研究链时运行 `init --skill jvc-meeting-notes --run-dir <研究目录> --resume`。后续 `scope` 更正必须通过 `record --run-dir <研究目录> --input <records.jsonl>` 登记，并用 `supersedes` 指向当前 effective scope；问题、检索、来源、主张和更正也只能通过该命令登记，不得直接编辑 `evidence_registry.jsonl`，generic `record` 不得创建 waiver。
3. 跨 skill 消费已有主张时，在新主张的 `derived_from_claim_ids` 中登记上游主张编号；缺失或失效的上游审计会阻断下游完成。
4. 最终产物中的本阶段支持与反证来源统一写为 `[S编号]`；Markdown 写在对应主张后，工作簿写入 `sources` 表，DOCX 写入来源附注，多文件产物至少在 `evidence_index.md` 建立映射。
5. 完成现有产物生成与格式校验后，运行 `audit --run-dir <研究目录> --skill jvc-meeting-notes --artifact <最终产物>`；多文件产物重复传入 `--artifact`。每次 audit 必须同时读取命令退出状态和 `audit.json`。
6. 只有 status 为 `blocked`、findings 中唯一 block 是 `partial_label_missing`，且至少一个 finding 为 `partial` 时，才按产物补写 `研究状态：partial`：Markdown 写入标题与结论，XLSX 在 `sources` 表表头和列结构不变的前提下追加一条可见状态数据行，DOCX 写入首段与来源附注，多文件产物至少写入 `knowledge_tree.md` 与 `evidence_index.md`；任何类型写回标签后，必须先重新运行原有产物格式校验/validator，确认结构仍有效，再重跑 audit；存在其他 block 时不得用标签绕过。重跑得到 `partial` / exit `10` 才可 partial 交付；`ready` / exit `0` 才能称为完成；其他 `blocked` / exit `20` 只能交付证据缺口和下一步，不能形成受影响的判断；exit `1` 必须修复后重跑。
7. 只有用户明确批准、且 blocker 与同 skill 最新有效 blocked audit 精确匹配时，才可运行 `waive --run-dir <研究目录> --skill jvc-meeting-notes --rule <阻断规则> --reason <批准理由> --scope <批准范围> --approved-by <批准人> --residual-risk <剩余风险>`；不得自我批准，waiver 最多降级为 partial。

找不到内核、profile 不兼容、账本损坏或终审异常时，不得退回纯 prompt 模式。

本 skill 登记逐字稿、用户随笔和纪要来源，区分受访者自述、用户观察和原始文本。

## 输出

`.docx` Word 文件，命名规则：

`【YYYY年MM月DD日访谈】{访谈对象}.docx`

这里的 `{访谈对象}` 通常是项目、公司或受访人名称；如果用户给的是 `year/month/day`，在真实文件名中使用 `YYYY年MM月DD日`，不要使用 `/`，避免被系统识别为路径分隔符。

默认模板是中性公开模板，不包含任何基金或机构品牌：

`skills/jvc-meeting-notes/templates/访谈纪要模板.docx`

默认模板采用内置 meeting-notes 标准版式：A4 页面，页边距为上/下 2.54cm、左/右 3.17cm；标题居中 18pt 加粗；章节标题 10pt 加粗；正文和子标题 10pt 常规；段前/段后 0、单倍行距；正文两端对齐，并启用 `doNotExpandShiftReturn` 避免手动换行短行被强行拉满；段落使用 `Normal` 并通过 run 级字体格式呈现。

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
2. 确认 JSON 中包含 `title`、`interviewee`、`filename`、`sections`；`filename` 使用 `【YYYY年MM月DD日访谈】{访谈对象}.docx`。
3. 运行：

```bash
python3 skills/jvc-meeting-notes/scripts/generate_meeting_notes.py data.json \
  --output output
```

如需显式指定用户自己的模板：

```bash
python3 skills/jvc-meeting-notes/scripts/generate_meeting_notes.py data.json \
  --template path/to/your-template.docx \
  --output output
```

## JSON 骨架

```json
{
  "title": "2026/06/11 线上 访谈{项目名称}",
  "interviewee": "项目名称或访谈对象",
  "filename": "【2026年06月11日访谈】项目名称或访谈对象.docx",
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
- 输出文件必须是 `.docx` 文件；如果 `--output` 传目录，生成器会按 `【YYYY年MM月DD日访谈】{访谈对象}.docx` 在目录内生成具体文件，生成后必须确认该 `.docx` 存在。
- 不要把任何个人或机构专属模板当作 public 默认模板；用户模板只通过 `--template`、`JVC_DOCX_TEMPLATE` 或本地 `custom.docx` 引入。
- 生成后应确认文件存在；重要纪要建议抽查打开。

## 依赖

```bash
python3 -m pip install -r skills/jvc-meeting-notes/requirements.txt
```
