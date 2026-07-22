# Trust Report

日期：2026-07-22

证据边界：这是 production governance 的本地 trust report，不是 public governed release 的完整安全认证。

## 缩写说明

| 缩写 | 英文全称 | 中文全称 | 含义 |
| --- | --- | --- | --- |
| CLI | Command-Line Interface | 命令行接口 | 脚本通过终端命令运行的接口 |
| OCR | Optical Character Recognition | 光学字符识别 | 从 PDF 发票中识别文字 |
| PDF | Portable Document Format | 便携式文档格式 | 发票和归档票据格式 |
| HTML | HyperText Markup Language | 超文本标记语言 | 浏览器预览使用的页面结构格式 |
| DOCX | Office Open XML Word Document | Word 文档格式 | 访谈纪要输出格式 |
| URI | Uniform Resource Identifier | 统一资源标识符 | 标识资源位置或内嵌数据的字符串；`data:` URI 用于内嵌本地资源 |
| SVG | Scalable Vector Graphics | 可缩放矢量图形 | 本地矢量图片格式；渲染前检查外部资源和不安全元素 |
| SHA-256 | Secure Hash Algorithm 256-bit | 256 位安全哈希算法 | package source contract 的内容指纹 |

## Source Contract Hash

`51acb7f4dfa18502b692181f2e38446f83f430f4dabdbeb1b3b7a61da7fc9f50`

Hash scope: `manifest`、`agents`、`security`、`skills`、`templates`、`scripts`、`evals`、`library`、`README`、`CLAUDE`、`setup`。生成报告和本地 telemetry 不进入 hash。

## Gate Summary

| Gate | Status | Evidence |
| --- | --- | --- |
| Secret scan | pass | No obvious secret patterns are expected in package files |
| Network scripts | pass | `security/network_policy.json` declares no shipped network-capable scripts |
| Permission approvals | pass | `security/permission_policy.json` approves file read, file write, subprocess |
| Dependency review | warn | `jvc-research-report` Python dependencies are pinned; some other Python and OCR dependencies remain incompletely machine-pinned |
| Script help surface | warn | Invoice scripts use manual `sys.argv`; governance, workbook, DOCX, and report-builder scripts use `argparse` |
| Runtime permission probes | warn | Packaged adapter probes are missing evidence because no `dist` package is generated |

## Pinned Report Dependencies

| Dependency | Version |
| --- | --- |
| `markdown-it-py` | `4.0.0` |
| `Pillow` | `12.1.1` |
| `PyYAML` | `6.0.3` |
| `WeasyPrint` | `68.1` |

## Research Report Evidence

证据范围是完全虚构的本地 fixture `examples/research-report-example/report.md`；它用于确定性排版回归，不包含真实市场主张。

| Control or check | Result |
| --- | --- |
| Local-only inputs | pass：只读本地 Markdown、YAML、图片和字体；本地二进制资源以 `data:` URI 内嵌进 HTML |
| Resource guards | pass：拒绝远程或绝对资源、路径逃逸、不安全 SVG 外部资源和未解析来源编号 |
| Transactional outputs | pass：`report.pdf`、`report.html`、`build-report.txt` 先暂存再整体发布；失败构建保留上一版成功产物 |
| PDF metadata and text | pass：真实构建为 A4 纸张规格、13 页；`pdftotext` 提取到标题、固定章节、后续工作交接包和来源索引 |
| Page rendering | pass：`pdftoppm` 生成 13/13 张页面图 |
| Visual inspection | pass：逐页检查全部 13 页，并重点复核封面、目录、callout、密集表格、图和来源索引；未见裁切、横向溢出、缺字、caption 脱离、意外空白页或页眉页脚不一致 |
| Resolved issue | pass：首轮样例把正文技术路线图重复用于封面；已将 `cover_image` 设为 `null`，最终视觉复核使用修正版 |

这些检查提高了本地渲染可信度，但仍是 self-check evidence，不是 model-executed evidence 或 blind-review evidence，也不证明 public governed release readiness。

## Script Surface

| Script | Interface | Capabilities |
| --- | --- | --- |
| `scripts/check-governance.py` | argparse CLI | file read, file write |
| `scripts/check-skill-evals.py` | CLI | file read |
| `scripts/generate-workbook.py` | argparse CLI | file read, file write |
| `scripts/validate-workbook.py` | argparse CLI | file read |
| `skills/jvc-knowledge-tree-builder/scripts/collect_sources.py` | argparse CLI | file read, file write |
| `skills/jvc-knowledge-tree-builder/scripts/check_package.py` | CLI | file read |
| `skills/jvc-research-report/scripts/build_report.py` | argparse CLI | file read, file write, subprocess |
| `skills/jvc-research-report/scripts/check_package.py` | CLI | file read, file write, subprocess |
| `skills/jvc-meeting-notes/scripts/generate_meeting_notes.py` | argparse CLI | file read, file write |
| `skills/jvc-invoice-manager/scripts/process_invoices.py` | manual CLI | file read, file write, OCR |
| `skills/jvc-invoice-manager/scripts/generate_summary.py` | manual CLI | file read, file write, PDF copy |

## Release Rule

No high-risk secrets or unrestricted remote inline execution are documented. This supports production governance with visible warnings. It does not support claiming full governed public release readiness.
