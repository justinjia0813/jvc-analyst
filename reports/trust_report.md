# Trust Report

日期：2026-07-31

证据边界：这是 production governance（生产治理）的本地 trust report（信任报告），不是 public governed release（受治理的公开发布）的完整安全认证。

## 缩写说明

| 缩写 | 英文全称 | 中文全称 | 含义 |
| --- | --- | --- | --- |
| CLI | Command-Line Interface | 命令行接口 | 脚本通过终端命令运行的接口 |
| OCR | Optical Character Recognition | 光学字符识别 | 从发票中识别文字 |
| PDF | Portable Document Format | 便携式文档格式 | 发票和归档票据格式 |
| HTML | HyperText Markup Language | 超文本标记语言 | 浏览器预览使用的页面结构格式 |
| DOCX | Office Open XML Word Document | Word 文档格式 | 访谈纪要输出格式 |
| URI | Uniform Resource Identifier | 统一资源标识符 | 标识资源位置或内嵌数据的字符串；`data:` URI 用于内嵌本地资源 |
| SVG | Scalable Vector Graphics | 可缩放矢量图形 | 本地矢量图片格式；渲染前检查外部资源和不安全元素 |
| SHA-256 | Secure Hash Algorithm 256-bit | 256 位安全哈希算法 | package source contract 的内容指纹 |

## Source Contract Hash

`61aaf57553d75855f0341357bb2d026aba50f1031ba4f30508c2a3228ab66ed9`

Hash scope: `manifest`、`agents`、`security`、`skills`、`templates`、`scripts`、`evals`、`library`、`README`、`CLAUDE`、`setup`。生成报告和本地 telemetry 不进入 hash。

## Gate Summary

| Gate | Status | Evidence |
| --- | --- | --- |
| Secret scan | pass | 本地治理检查未发现预设的高风险凭据模式 |
| Network scripts | pass | `security/network_policy.json` 声明脚本网络默认拒绝，清单为空 |
| Packaged-script network | pass | deal-flow controller、research core、review-kit renderer 和 research-report renderer 均无网络能力；report 只内嵌本地 `data:` URI |
| Permission approvals | pass | 本地 file read、file write、subprocess 已按范围批准 |
| Dependency review | warn | research core 为标准库，report Python 依赖已锁定；既有 DOCX/发票依赖仍有未固定版本项 |
| Script help surface | warn | research core、report renderer 与其他生成器有明确接口；既有发票脚本仍使用手工 `sys.argv` |
| Runtime permission probes | warn | 本轮没有生成分发包，因此没有适配器运行时权限探针 |

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
| `skills/jvc-deal-flow/scripts/dealflowctl.py` | argparse CLI | file read, file write；无网络 |
| `skills/jvc-deal-flow/scripts/check_package.py` | self-check | file read, file write, subprocess；仅使用临时项目库 |
| `scripts/check-governance.py` | argparse CLI | file read, file write |
| `scripts/check-skill-evals.py` | CLI | file read |
| `scripts/check-v3-foundation.py` | self-check | file read |
| `scripts/check-research-core-install.py` | self-check | file read, file write, subprocess；仅在临时目录模拟安装与回滚 |
| `scripts/render-output-review-kit.py` | argparse CLI | file read, file write；无网络 |
| `scripts/generate-workbook.py` | argparse CLI | file read, file write |
| `scripts/validate-workbook.py` | argparse CLI | file read |
| `skills/jvc-knowledge-tree-builder/scripts/collect_sources.py` | argparse CLI | file read, file write |
| `skills/jvc-knowledge-tree-builder/scripts/check_package.py` | CLI | file read |
| `skills/jvc-research-report/scripts/build_report.py` | argparse CLI | file read, file write, subprocess |
| `skills/jvc-research-report/scripts/check_package.py` | CLI | file read, file write, subprocess |
| `skills/jvc-meeting-notes/scripts/generate_meeting_notes.py` | argparse CLI | file read, file write |
| `skills/jvc-invoice-manager/scripts/process_invoices.py` | manual CLI | file read, file write, OCR |
| `skills/jvc-invoice-manager/scripts/generate_summary.py` | manual CLI | file read, file write, PDF copy |
| `skills/jvc-research-core/scripts/researchctl.py` | argparse CLI | file read, file write；无网络 |
| `skills/jvc-research-core/scripts/check_package.py` | self-check | file read, file write；无网络 |

## Release Rule

未发现高风险凭据或不受限的远程内联执行。证据支持仓库内 production governance with warnings（带警告的生产治理），不支持声称完整的公开受治理发布就绪。
