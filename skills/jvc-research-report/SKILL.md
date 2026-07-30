---
name: jvc-research-report
description: Use when the user already has a local fixed-structure industry or track research Markdown file and wants it validated and rendered as a branded printable report plus browser preview without rewriting the research content. Do not use for first-pass research, content rewriting, chart generation, investment-committee memo drafting, or arbitrary Markdown conversion.
metadata:
  author: jvc-analyst
user_invocable: true
version: "3.0.0"
---

# /jvc-research-report — lustinus RESEARCH 行业研报生成

把已完成的固定格式行业研究 Markdown 校验并编译为 PDF（Portable Document Format，可移植文档格式，用于固定版式）和 HTML（HyperText Markup Language，超文本标记语言，用于浏览器预览）。

## 3.0 适用级别

最低适用级别：**L2+**（Level 2 or above，二级及以上尽调，用于验证关键假设）。

- 输入研究内容至少完成 L2 的来源、反证和覆盖缺口检查；本 Skill 只排版，不把低级别草稿自动升级为正式研报。
- 内容未达到 L2 时，返回缺口并路由到 `/jvc-track-research`，不代建项目规格。
- 构建成功后必须渲染检查全部页面；文件存在不等于视觉交付完成。

## 反合理化约束

- “排版专业可以弥补内容缺口” → 样式不改变证据强度；缺来源或结构不完整就停止构建。
- “PDF 已生成，所以可以交付” → 逐页检查布局、裁切、间距、缺失内容和一致性。
- “修一句正文能让版面更好看” → 不改研究内容；只能调整版式，内容问题退回上游。
- “远程图片临时可用” → 只接受本地资源；不引入隐式网络依赖。

## 输入

- 固定章节的 `report.md`
- 可选：用户自定义的 `brand.yml`；未提供时使用 skill 内置默认品牌
- Markdown 引用的本地图片

内容不完整时回到 `/jvc-track-research`；本 skill 不补研究、不改观点。

## 前置条件

先从实际加载的 `SKILL.md` 绝对路径解析其所在目录，并把该目录设为 `SKILL_ROOT`；它不是自动存在的环境变量。将下方占位路径替换为真实路径后安装 Python 依赖：

```bash
SKILL_ROOT="/absolute/path/to/jvc-research-report"
python3 -m pip install -r "$SKILL_ROOT/requirements.txt"
```

本机还必须提供 `fc-match`、`fc-query` 和 `fc-scan`，它们属于 Fontconfig（字体配置系统，用于查询和验证本机字体）。仓库根目录的 `./setup` 只注册 skill，不安装 Python 依赖或 Fontconfig。

## 执行

1. 解析 `SKILL_ROOT`，并取得用户给定的 `report.md` 与输出目录绝对路径；不要依赖当前工作目录。
2. 将下列三个占位路径替换为真实绝对路径。未提供自定义品牌时，命令仍显式指向内置默认品牌：

```bash
SKILL_ROOT="/absolute/path/to/jvc-research-report"
REPORT="/absolute/path/to/report.md"
OUTPUT="/absolute/path/to/output"
python3 "$SKILL_ROOT/scripts/build_report.py" "$REPORT" \
  --brand "$SKILL_ROOT/assets/brand.yml" \
  --output "$OUTPUT"
```

使用自定义品牌时，仅将 `--brand` 的值替换为该 `brand.yml` 的绝对路径。

3. 构建失败时原样返回具体错误，不猜测、不覆盖上一版成功产物。
4. 成功后检查 `build-report.txt`，再渲染并检查全部 PDF 页面。
5. 交付 `report.pdf`、`report.html` 和 `build-report.txt`。

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
