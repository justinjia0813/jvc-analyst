---
name: jvc-research-report
description: Use when the user has audited track-level upstream artifacts (Track Research, Knowledge Tree, Market Sizing, optional Comps/DD) and wants them assembled into a canonical research-report.md and rendered as a branded printable PDF plus browser preview, or already has a complete canonical research-report.md and wants it validated and rendered. The assembler only reorganizes audited upstream content: it preserves source identifiers, inherits upstream claims, exposes coverage gaps, and never researches new facts online. Do not use for first-pass research, content rewriting, chart generation, investment-committee memo drafting, or arbitrary Markdown conversion.
metadata:
  author: jvc-analyst
user_invocable: true
version: "4.0.0"
---

# /jvc-research-report — lustinus RESEARCH 行业研报（组装 + 发布两阶段）

把已审计的赛道级上游产物组装为固定格式 `research-report.md`，再校验并编译为 PDF（Portable Document Format，可移植文档格式，用于固定版式）和 HTML（HyperText Markup Language，超文本标记语言，用于浏览器预览）。本 Skill 是输出组装器：只重组经审查的内容，不新增事实或数字，不联网补研究。

## 3.0 适用级别

最低适用级别：**L2+**（Level 2 or above，二级及以上尽调，用于验证关键假设）。

- 上游输入至少完成 L2 的来源、反证和覆盖缺口检查；本 Skill 只组装与排版，不把低级别草稿自动升级为正式研报。
- 内容未达到 L2 时，返回缺口并路由到 `/jvc-track-research`、`/jvc-market-sizing` 或 `/jvc-knowledge-tree-builder`，不代建项目规格。
- 构建成功后必须渲染检查全部页面；文件存在不等于视觉交付完成。

## 反合理化约束

- “组装时可以顺手补一点数据” → 禁止新增事实或数字；报告数字必须继承上游，缺失就写进覆盖缺口。
- “报告缺来源可以联网补” → 禁止联网研究；只消费已提供的本地上游产物，来源标识必须继承。
- “排版专业可以弥补内容缺口” → 样式不改变证据强度；缺来源或结构不完整就停止构建。
- “PDF 已生成，所以可以交付” → 逐页检查布局、裁切、间距、缺失内容和一致性。
- “修一句正文能让版面更好看” → 不改研究内容；只能调整版式，内容问题退回上游。
- “远程图片临时可用” → 只接受本地资源；不引入隐式网络依赖。

## 输入

- 上游产物（组装模式）：
  - `tracks/{track-slug}/landscape.md`（Track Research，赛道研究）
  - Knowledge Tree 五文件包或主入口 `knowledge_tree.md`（Knowledge Tree Builder）
  - `market-sizing.csv`（Market Sizing 唯一活跃模型）
  - 可选：`03-comps-dd.md`（Comps/DD，可比公司分析/尽职调查；仅在必要的比较信息时提供）
- 或已完成的完整 canonical `research-report.md`（直接发布模式）
- 可选：用户自定义的 `brand.yml`；未提供时使用 skill 内置默认品牌
- Markdown 引用的本地图片

上游缺失时在 `未核实与待补证据` 章节列出覆盖缺口，不调用网页搜索补齐。

## 前置条件

先从实际加载的 `SKILL.md` 绝对路径解析其所在目录，并把该目录设为 `SKILL_ROOT`；它不是自动存在的环境变量。将下方占位路径替换为真实路径后安装 Python 依赖：

```bash
SKILL_ROOT="/absolute/path/to/jvc-research-report"
python3 -m pip install -r "$SKILL_ROOT/requirements.txt"
```

本机还必须提供 `fc-match`、`fc-query` 和 `fc-scan`，它们属于 Fontconfig（字体配置系统，用于查询和验证本机字体）。仓库根目录的 `./setup` 只注册 skill，不安装 Python 依赖或 Fontconfig。

## 执行（两阶段，顺序执行）

### 阶段一：组装 canonical research-report.md

1. 解析 `SKILL_ROOT`，收集用户提供的上游产物与输出目录绝对路径；不要依赖当前工作目录。
2. 按 `references/output-contract.md` 的「上游到章节映射」重组 `research-report.md`：
   - 保留全部来源标识 `[S<n>]`（只使用上游已出现的编号）；
   - 继承上游主张与证据状态标签（`[推测]`、`[未核实]`、`[模型估算]` 等只能沿用上游已有标签，半角 `[...]` 与全角 `【...】` 等价，不得新造）；
   - 不新增任何事实、数字或判断；数字只能继承上游（四位年份 `N`/`N年` 等价；亿/万 不做换算）；
   - 在 `未核实与待补证据` 章节列出覆盖缺口，包括缺失的可选上游（如 Comps/DD）。
3. 运行只读组装校验器（本机纯标准库，不联网）：

```bash
SKILL_ROOT="/absolute/path/to/jvc-research-report"
python3 "$SKILL_ROOT/scripts/validate_assembly.py" \
  --track-research "/absolute/path/to/tracks/{slug}/landscape.md" \
  --knowledge-tree "/absolute/path/to/knowledge-tree-package-or-knowledge_tree.md" \
  --market-sizing "/absolute/path/to/market-sizing.csv" \
  --comps-dd "/absolute/path/to/03-comps-dd.md" \
  --report "/absolute/path/to/research-report.md"
```

   Comps/DD 未提供时省略 `--comps-dd`；校验器要求报告在覆盖缺口章节显式列出该可选输入未提供。校验失败时按错误原样返回，不猜测、不覆盖。

### 阶段二：发布（校验 + 渲染）

用户已经提供完整 canonical `research-report.md`（直接发布模式）或阶段一校验通过后：

```bash
SKILL_ROOT="/absolute/path/to/jvc-research-report"
REPORT="/absolute/path/to/research-report.md"
OUTPUT="/absolute/path/to/output"
python3 "$SKILL_ROOT/scripts/build_report.py" "$REPORT" \
  --brand "$SKILL_ROOT/assets/brand.yml" \
  --output "$OUTPUT"
```

使用自定义品牌时，仅将 `--brand` 的值替换为该 `brand.yml` 的绝对路径。

> 直接发布边界：直接发布信任用户对 canonical 的声明，`build_report.py` 只运行
> renderer 内部一致性校验（章节/来源索引内自洽/本地资源），不比对上游，**不证明**
> assembly 继承或 Research Core 审计。需要证据继承时，必须提供上游产物并运行
> `validate_assembly.py`；校验器是 set-based token 继承，不能证明重组句子的语义
> 等价，主张级审计仍需上游 claim 与人工复核。

4. 构建失败时原样返回具体错误，不猜测、不覆盖上一版成功产物。
5. 成功后检查 `build-report.txt`，再渲染并检查全部 PDF 页面。
6. 交付 `research-report.md`（组装产物）、`report.pdf`、`report.html` 和 `build-report.txt`。

## 规则

- 不重写、摘要、重排或补充上游正文；渲染器不修改正文、不访问网络。
- 只读取本地 Markdown、CSV、YAML、图片和字体；远程图片直接报错。
- `[S<n>]` 必须在来源索引中有唯一条目，且必须已存在于上游产物。
- frontmatter 只允许 title/subtitle/date/authors/sector/region/classification/cover_image/disclaimer 顶层键（组装路径校验；直接发布由 build_report 兼容接受）。
- 表格和图片只排版，不生成新图表；Mermaid 等渲染器不支持的语法退回为本地静态图片。
- 英文缩写首次出现时给出英文全称、中文全称和一句解释。

## Reference Map

- `references/output-contract.md` — 输入结构、上游到章节映射、品牌字段、卡片语法和失败规则。
- `assets/brand.yml` — 默认品牌配置。
- `templates/industry-report.md` — 固定格式模板与组装指引。
- `scripts/validate_assembly.py` — 只读组装校验器（来源继承、数字继承、标签继承、覆盖缺口）。
- `scripts/build_report.py` — 确定性校验和渲染器。
