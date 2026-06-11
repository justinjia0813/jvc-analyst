---
name: meeting-notes
description: Use when 需要根据逐字稿和用户笔记生成结构化 Word 访谈纪要，作为创始人访谈、客户访谈、背调电话的事实层入口
source_repo: https://github.com/justinjia0813/meeting-notes
---

# Meeting Notes

`meeting-notes` 是 `vc-analyst` 收录的外部 skill，用作可复用的事实层生成器。

## 事实来源

- 仓库：<https://github.com/justinjia0813/meeting-notes>
- 作用：AI 转写逐字稿 + 用户笔记 -> 结构化访谈纪要 `.docx`
- 依赖：`python-docx`
- 输出命名：`{YYYYMMDD}_{project}_访谈纪要.docx`

## vc-analyst 接入方式

当投资工作流从会议逐字稿、创始人电话、客户访谈、背调对话开始时，使用这个 skill。

标准链路：

1. 如果输入是音频或视频，先用 `/asr` 转成逐字稿。
2. 用 `meeting-notes` 生成结构化 `.docx` 纪要。
3. 将 `.docx` 放入 `projects/{company-slug}/00-source/`。
4. 只把相关事实提取到当前 Markdown 文件：
   - `/intake` -> project fact card
   - `/founder-sync` -> `03-founder-sync.md`
   - `/ref-check` -> `05-ref-check.md`

## 边界

`.docx` 输出是事实层，不要在里面静默加入投资结论。

解读应写入项目档案，并保留来源标签：

- `[创始人自述]`：未经外部验证的创始人说法
- `[客户访谈]`：客户访谈中的陈述
- `[待交叉验证]`：单一信源声明
- `[推测]`：分析者推断
