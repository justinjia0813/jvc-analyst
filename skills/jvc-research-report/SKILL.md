---
name: jvc-research-report
description: Use when the user already has a local fixed-structure industry or track research Markdown file and wants it validated and rendered as a branded printable report plus browser preview. Do not use for first-pass research, content rewriting, chart generation, investment-committee memo drafting, or arbitrary Markdown conversion.
metadata:
  author: jvc-analyst
---

# /jvc-research-report — lustinus RESEARCH 行业研报生成

把已完成的固定格式行业研究 Markdown 校验并编译为 PDF（Portable Document Format，可移植文档格式，用于固定版式）和 HTML（HyperText Markup Language，超文本标记语言，用于浏览器预览）。

## 输入

- 固定章节的 `report.md`
- 可复用的 `brand.yml`
- Markdown 引用的本地图片

内容不完整时回到 `/jvc-track-research`；本 skill 不补研究、不改观点。

## 执行

1. 运行 `python3 scripts/build_report.py report.md --brand brand.yml --output output`。
2. 构建失败时原样返回具体错误，不猜测、不覆盖上一版成功产物。
3. 成功后检查 `build-report.txt`，再渲染并检查全部 PDF 页面。
4. 交付 `report.pdf`、`report.html` 和 `build-report.txt`。

## 规则

- 不重写、摘要、重排或补充正文。
- 只读取本地 Markdown、YAML、图片和字体；远程图片直接报错。
- `[S<n>]` 必须在来源索引中有唯一条目。
- 表格和图片只排版，不生成新图表。
- 英文缩写首次出现时给出英文全称、中文全称和一句解释。

## Reference Map

- `references/output-contract.md` — 输入结构、品牌字段、卡片语法和失败规则。
- `assets/brand.yml` — 默认品牌配置。
- `templates/industry-report.md` — 固定格式模板。
- `scripts/build_report.py` — 确定性校验和渲染器。
