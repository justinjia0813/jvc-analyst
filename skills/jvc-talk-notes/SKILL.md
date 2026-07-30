---
name: jvc-talk-notes
description: |
  问答式访谈纪要：将高管访谈、客户访谈、专家访谈的逐字稿转为 Q&A 格式的结构化 Word 访谈纪要，按「问题→回答→待验证点」组织，记录事实层信息并标出待交叉验证项。
  Use when user says '/jvc-talk-notes', '高管访谈', '客户访谈', '专家访谈', '问答纪要', 'talk notes', 'Q&A notes', or asks to turn a transcript into a Q&A Word DOCX interview note.
user_invocable: true
version: "2.0.0"
---

# jvc-talk-notes — 问答式访谈纪要

`/jvc-talk-notes` 是 `/jvc-meeting-notes` 的问答式版本。用于高管访谈、客户访谈、专家访谈和用户访谈：当材料最适合按“问题 → 回答 → 待验证点”阅读时，用这个 skill，而不是六段式公司访谈纪要。

它仍然是事实层生成器：记录问了什么、答了什么、用户观察到什么、哪些地方还要交叉验证。不要加入投资结论。

## 输入

- AI 转写逐字稿或会议纯文本。
- 用户随笔、现场观察、会后补充判断。
- 会议日期、线上/线下、公司或项目名称、受访人角色；如已知，可加入访谈人。
- 可选：用户希望重点保留的问题、必须保留的原话、希望按主题归并的部分。

## 2.0 证据内核（必须）

从本 `SKILL.md` 的实际目录解析同级 `../jvc-research-core/scripts/researchctl.py`，并使用绝对路径执行；不要依赖当前工作目录。

执行前必须读取同级 `../jvc-research-core/references/evidence-contract.md` 和当前 profile `../jvc-research-core/profiles/jvc-talk-notes.json`。

1. 新研究先准备完整 `scope` JSON，再运行 `init --skill jvc-talk-notes --run-dir <研究目录> --scope-file <scope.json>`；初始 `scope` 只能通过 `init --scope-file` 创建。
2. 复用已有研究链时运行 `init --skill jvc-talk-notes --run-dir <研究目录> --resume`。后续 `scope` 更正必须通过 `record --run-dir <研究目录> --input <records.jsonl>` 登记，并用 `supersedes` 指向当前 effective scope；问题、检索、来源、主张和更正也只能通过该命令登记，不得直接编辑 `evidence_registry.jsonl`，generic `record` 不得创建 waiver。
3. 跨 skill 消费已有主张时，在新主张的 `derived_from_claim_ids` 中登记上游主张编号；缺失或失效的上游审计会阻断下游完成。
4. 最终产物中的本阶段支持与反证来源统一写为 `[S编号]`；Markdown 写在对应主张后，工作簿写入 `sources` 表，DOCX 写入来源附注，多文件产物至少在 `evidence_index.md` 建立映射。
5. 完成现有产物生成与格式校验后，运行 `audit --run-dir <研究目录> --skill jvc-talk-notes --artifact <最终产物>`；多文件产物重复传入 `--artifact`。每次 audit 必须同时读取命令退出状态和 `audit.json`。
6. 只有 status 为 `blocked`、findings 中唯一 block 是 `partial_label_missing`，且至少一个 finding 为 `partial` 时，才按产物补写 `研究状态：partial`：Markdown 写入标题与结论，XLSX 在 `sources` 表表头和列结构不变的前提下追加一条可见状态数据行，DOCX 写入首段与来源附注，多文件产物至少写入 `knowledge_tree.md` 与 `evidence_index.md`；任何类型写回标签后，必须先重新运行原有产物格式校验/validator，确认结构仍有效，再重跑 audit；存在其他 block 时不得用标签绕过。重跑得到 `partial` / exit `10` 才可 partial 交付；`ready` / exit `0` 才能称为完成；其他 `blocked` / exit `20` 只能交付证据缺口和下一步，不能形成受影响的判断；exit `1` 必须修复后重跑。
7. 只有用户明确批准、且 blocker 与同 skill 最新有效 blocked audit 精确匹配时，才可运行 `waive --run-dir <研究目录> --skill jvc-talk-notes --rule <阻断规则> --reason <批准理由> --scope <批准范围> --approved-by <批准人> --residual-risk <剩余风险>`；不得自我批准，waiver 最多降级为 partial。

找不到内核、profile 不兼容、账本损坏或终审异常时，不得退回纯 prompt 模式。

本 skill 登记逐字稿、用户随笔和问答纪要来源，区分受访者自述、用户观察和原始文本。

## 输出

生成 `.docx` Word 文件，命名规则：

`【YYYY年MM月DD日访谈】{访谈对象}.docx`

这里的 `{访谈对象}` 优先写具体受访人；如果只知道公司、项目或客户名称，就写该公司/项目/客户名称。用户口头说的 `year/month/day` 在真实文件名中落为 `YYYY年MM月DD日`，不要使用 `/`，避免被系统识别为路径分隔符。

复用现有 meeting-notes 资产：

- `skills/jvc-meeting-notes/scripts/generate_meeting_notes.py`
- `skills/jvc-meeting-notes/templates/访谈纪要模板.docx`
- `skills/jvc-meeting-notes/requirements.txt`

默认 Word 模板是中性公开模板。用户可用三种方式替换成自己的机构模板：

1. 运行时传 `--template path/to/template.docx`
2. 设置 `JVC_DOCX_TEMPLATE=/path/to/template.docx`
3. 放置本地文件 `skills/jvc-meeting-notes/templates/custom.docx`

生成器会保留用户模板的页面设置、样式、页眉和页脚，再写入新的问答纪要正文。如果模板里有示例段落，会按前几个非空段落抽取标题、章节、正文和子标题样式；否则使用模板的 `Normal` 样式。

默认模板沿用 `jvc-meeting-notes` 的标准 Word 版式：A4 页面，页边距为上/下 2.54cm、左/右 3.17cm；标题居中 18pt 加粗；章节标题 10pt 加粗；正文和 Q&A 小标题 10pt 常规；段前/段后 0、单倍行距；正文两端对齐，并启用 `doNotExpandShiftReturn` 避免手动换行短行被强行拉满；段落使用 `Normal` 并通过 run 级字体格式呈现。`jvc-talk-notes` 只改变内容编排为一问一答，不改变视觉版式和信息抽取强度。

## 结构

默认五段式：

1. `一、访谈基本信息`
2. `二、问答纪要`
3. `三、事实层索引`
4. `四、用户观察与待交叉验证`
5. `五、后续追问清单`

每个问答条目必须作为 `二、问答纪要` 下的 `subsections`，不要把 `Q1/Q2` 混在正文 `content` 里。每个 `subsection.heading` 使用 `Qn：问题原意`，问题本身只放在标题里，正文不要再重复 `问题：`。

每个 `subsection.content` 包含：

- `完整回答`：在保留核心信息、关键数字、因果链条、例子和不确定性的前提下，整理成完整回答；做必要提炼，但不要压成短摘要；筛去重复表达、口头禅、自我修正、寒暄和无信息量 ad-libs。
- `对应事实层维度`：标注公司基本情况 / 技术 / 团队 / 产品 / 商业化 / 融资 / 客户 / 财务 / 风险 / 其他。
- `待验证点`：标出回避、矛盾、数字不清、需要外部证据的问题；如果没有，写 `无明显待验证点`。

不要输出 `问题：`、`回答摘要：`、`关键原话：`、`事实标签：` 这些字段。重要原话如确有保留价值，应自然融入 `完整回答`，不要单列。

## 生成流程

1. 从逐字稿和用户随笔中抽取问答对。只有语义相同的问题才合并。
2. 默认保留访谈顺序；如果按主题归并更利于复盘，可以重组，但不能丢失原问题意图。
3. 整理为 `generate_meeting_notes.py` 可消费的 JSON：

```json
{
  "title": "2026/06/12 线上 客户访谈{项目名称}",
  "interviewee": "访谈对象",
  "filename": "【2026年06月12日访谈】访谈对象.docx",
  "sections": [
    {"heading": "一、访谈基本信息", "content": "日期、形式、项目、受访人角色、访谈目的。"},
    {
      "heading": "二、问答纪要",
      "subsections": [
        {
          "heading": "Q1：客户当前如何解决这个问题？",
          "content": "完整回答：...\n对应事实层维度：客户 / 商业化\n待验证点：..."
        }
      ]
    },
    {"heading": "三、事实层索引", "content": "按公司基本情况 / 技术 / 团队 / 产品 / 商业化 / 融资 / 客户 / 财务 / 风险归类索引 Q&A 中已出现的信息。"},
    {"heading": "四、用户观察与待交叉验证", "content": "..."},
    {"heading": "五、后续追问清单", "content": "..."}
  ]
}
```

4. 运行生成器并确认 `.docx` 文件存在：

```bash
python3 skills/jvc-meeting-notes/scripts/generate_meeting_notes.py data.json \
  --output output
```

## 质量红线

- 受访者陈述不是已验证事实，除非用户提供外部证据。
- 客户需求必须区分当前使用、试点、意向和假设性需求。
- 模糊回答、回避、前后矛盾和无来源数字都要放入 `待验证点`。
- 用户疑问和观察必须和受访者回答分开记录。
- 不得因为采用问答形式而降低信息抽取完整度；凡逐字稿中出现的公司、技术、团队、产品、商业化、融资、客户、财务、风险信息，都必须在 Q&A 或事实层索引中保留。
- `Q1/Q2` 必须写入 JSON `subsections.heading`，不要写成正文段落，否则会破坏和 `jvc-meeting-notes` 的视觉一致性。
- Q&A 正文统一使用 `完整回答 / 对应事实层维度 / 待验证点` 三类信息，不要恢复 `问题 / 回答摘要 / 关键原话 / 事实标签`。
- 不要把个人或机构专属 Word 模板提交为 public 默认模板。
- 不要把它写成销售会议总结、投资 memo 或投资建议。

## 依赖

```bash
python3 -m pip install -r skills/jvc-meeting-notes/requirements.txt
```
