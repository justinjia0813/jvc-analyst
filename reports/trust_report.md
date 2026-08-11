# Trust Report

日期：2026-08-10

证据边界：这是 production governance（生产治理）的本地 trust report（信任报告），不是 public governed release（受治理的公开发布）的完整安全认证。

## 缩写说明

| 缩写 | 英文全称 | 中文全称 | 含义 |
| --- | --- | --- | --- |
| CLI | Command-Line Interface | 命令行接口 | 脚本通过终端命令运行的接口 |
| OCR | Optical Character Recognition | 光学字符识别 | 从发票中识别文字 |
| PDF | Portable Document Format | 便携式文档格式 | 发票和归档票据格式 |
| HTML | HyperText Markup Language | 超文本标记语言 | 浏览器预览使用的页面结构格式 |
| DOCX | Office Open XML Word Document | Word 文档格式 | 访谈纪要输出格式 |
| ROI | Return on Investment | 投资回报率 | 衡量投入相对回报水平的指标 |
| CSV | Comma-Separated Values | 逗号分隔值 | 用逗号分隔字段的纯文本表格格式 |
| URI | Uniform Resource Identifier | 统一资源标识符 | 标识资源位置或内嵌数据的字符串；`data:` URI 用于内嵌本地资源 |
| SVG | Scalable Vector Graphics | 可缩放矢量图形 | 本地矢量图片格式；渲染前检查外部资源和不安全元素 |
| PNG | Portable Network Graphics | 便携式网络图形 | 无损位图图像格式，用于研报与知识树的逐页页面图 |
| SHA-256 | Secure Hash Algorithm 256-bit | 256 位安全哈希算法 | package source contract 的内容指纹 |

## Source Contract Hash

`63913d375920fe2c5b04d9169a46cf7cbee3ff462eef498ef2c3b7688b8f4d3c`

Hash scope: `manifest`、`inspired-design.md`、`agents`、`security`、`skills`、`templates`、`scripts`、`evals`、`library`、`README`、`CLAUDE`、`setup`。生成报告和本地 telemetry 不进入 hash。

## Gate Summary

| Gate | Status | Evidence |
| --- | --- | --- |
| Secret scan | pass | 本地治理检查未发现预设的高风险凭据模式 |
| Network scripts | pass | `security/network_policy.json` 声明脚本网络默认拒绝，清单为空 |
| Packaged-script network | pass | deal-flow controller、research core、review-kit renderer、research-report renderer、IC memo validator 和 IC memo package check 均无网络能力；Pre-Screen validator and package check 均无网络能力；Knowledge Tree 与 Market Sizing validator/package check 均无网络能力；Research Report assembly validator 无网络能力；report 只内嵌本地 `data:` URI |
| Permission approvals | pass | 本地 file read、file write、subprocess 已按范围批准 |
| Dependency review | warn | research core、Pre-Screen validator/package check、ROI Modeler CSV validator、Market Sizing validator/package check 和 IC memo validator/package check 仅使用 Python 标准库；Knowledge Tree validator 仅使用标准库，package check 另调用本地 Quarto 与 Poppler；report Python 依赖已锁定；既有 DOCX/发票依赖仍有未固定版本项 |
| Script help surface | warn | research core、report renderer 与其他生成器有明确接口；既有发票脚本仍使用手工 `sys.argv` |
| Runtime permission probes | warn | 本轮没有生成分发包，因此没有适配器运行时权限探针 |

Pre-Screen validator/package check 仅使用 Python 标准库；生产 validator 只读目标文件，package check 仅在临时目录写 fixture 并启动本地子进程，两者均无网络能力。IC memo validator/package check 仅使用 Python 标准库。Research Report 组装校验器仅使用 Python 标准库（数字归一化复用 IC 终版校验器语义），只读上游与报告，无网络能力。Knowledge Tree 与 Market Sizing validator/package check 均无网络能力；两套生产 validator 都只读目标文件，两套 package check 都只在临时目录写 fixture，其中 Knowledge Tree package check 还调用本地 Quarto 与 Poppler，Market Sizing validator/package check 仅使用 Python 标准库。

## Pinned Report Dependencies

| Dependency | Version |
| --- | --- |
| `markdown-it-py` | `4.0.0` |
| `Pillow` | `12.1.1` |
| `PyYAML` | `6.0.3` |
| `WeasyPrint` | `68.1` |

## Research Report Evidence

证据范围是完全虚构的本地 fixture `examples/research-report-example/research-report.md`（canonical，由已审计的上游虚构样例组装）；它用于确定性组装与排版回归，不包含真实市场主张。旧 fixture `examples/research-report-example/report.md` 已降级为历史样例，不再被活跃合同引用。

| Control or check | Result |
| --- | --- |
| Assembly inheritance | pass：`validate_assembly.py` 校验来源 ID、数字与标签继承；1a–1h 对抗反例（新来源、新数字、未知标签、全角括号、frontmatter 未知键、单位不一致、不可读文件、带引号 CSV 逗号）全部按预期拒绝 |
| Local-only inputs | pass：只读本地 Markdown、YAML、图片和字体；本地二进制资源以 `data:` URI 内嵌进 HTML |
| Resource guards | pass：拒绝远程或绝对资源、路径逃逸、不安全 SVG 外部资源和未解析来源编号 |
| Transactional outputs | pass：`report.pdf`、`report.html`、`build-report.txt` 先暂存再整体发布；失败构建保留上一版成功产物 |
| PDF metadata and text | pass：真实构建为 A4 纸张规格、14 页；`pdftotext` 提取到标题、固定章节、覆盖缺口章节和来源索引 |
| Page rendering | pass：`pdftoppm` 生成 14/14 张页面图（`reports/task9-visual/research-report-page-01.png` … `page-14.png`） |
| Visual inspection | pass：主 Agent 已于 2026-08-10 用 `view_image` 逐页目检 `reports/task9-visual/research-report-page-01.png` … `page-14.png` 与 `knowledge-tree-page-01.png`，无裁切、缺字、丢标签或跨页不一致；第 7 页图与图注、第 13 页缺口表、第 14 页七列来源表通过（记录：`reports/task9-visual/MAIN-VISUAL-INSPECTION.md`）。这是视觉检查，不代替 `validate_assembly.py` 等机械校验 |
| Resolved issue | pass：首轮样例把正文技术路线图重复用于封面；已将 `cover_image` 设为 `null`，最终渲染使用修正版 |

这些检查提高了本地组装与渲染可信度，但仍是 self-check evidence，不是 model-executed evidence 或 blind-review evidence，也不证明 public governed release readiness。旧盲审产物已归档为 `reports/legacy/`（historical legacy workbook），不作为新 CSV 合同通过的证明。

## Script Surface

| Script | Interface | Capabilities |
| --- | --- | --- |
| `skills/jvc-deal-flow/scripts/dealflowctl.py` | argparse CLI | file read, file write；无网络 |
| `skills/jvc-deal-flow/scripts/check_package.py` | self-check | file read, file write, subprocess；仅使用临时项目库 |
| `skills/jvc-ic-memo/scripts/validate_final.py` | argparse CLI | file read；无网络 |
| `skills/jvc-ic-memo/scripts/check_package.py` | self-check | file read, file write, subprocess；仅使用临时目录 |
| `skills/jvc-prescreen/scripts/validate_output.py` | CLI | file read；无网络 |
| `skills/jvc-prescreen/scripts/check_package.py` | self-check | file read, file write, subprocess；仅使用临时目录；无网络 |
| `scripts/check-governance.py` | argparse CLI | file read, file write |
| `scripts/check-skill-evals.py` | CLI | file read, file write, subprocess；仅使用临时目录 |
| `scripts/check-v3-foundation.py` | self-check | file read |
| `scripts/check-research-core-install.py` | self-check | file read, file write, subprocess；仅在临时目录模拟安装与回滚 |
| `scripts/render-output-review-kit.py` | argparse CLI | file read, file write；无网络 |
| `scripts/generate-workbook.py` | argparse CLI | file read, file write |
| `scripts/validate-workbook.py` | argparse CLI | file read |
| `skills/jvc-roi-modeler/scripts/validate_csv.py` | CLI | file read；无网络 |
| `skills/jvc-knowledge-tree-builder/scripts/collect_sources.py` | argparse CLI | file read, file write |
| `skills/jvc-knowledge-tree-builder/scripts/validate_output.py` | CLI | file read；无网络 |
| `skills/jvc-knowledge-tree-builder/scripts/check_package.py` | self-check | file read, file write, subprocess；仅使用临时目录；调用本地 Quarto 与 Poppler；无网络 |
| `skills/jvc-market-sizing/scripts/validate_csv.py` | CLI | file read；无网络 |
| `skills/jvc-market-sizing/scripts/check_package.py` | self-check | file read, file write, subprocess；仅使用临时目录；无网络 |
| `skills/jvc-research-report/scripts/build_report.py` | argparse CLI | file read, file write, subprocess |
| `skills/jvc-research-report/scripts/check_package.py` | CLI | file read, file write, subprocess |
| `skills/jvc-research-report/scripts/validate_assembly.py` | CLI | file read；无网络 |
| `skills/jvc-meeting-notes/scripts/generate_meeting_notes.py` | argparse CLI | file read, file write |
| `skills/jvc-invoice-manager/scripts/process_invoices.py` | manual CLI | file read, file write, OCR |
| `skills/jvc-invoice-manager/scripts/generate_summary.py` | manual CLI | file read, file write, PDF copy |
| `skills/jvc-research-core/scripts/researchctl.py` | argparse CLI | file read, file write；无网络 |
| `skills/jvc-research-core/scripts/check_package.py` | self-check | file read, file write, subprocess；无网络 |
| `scripts/check-docx-filename-rule.py` | self-check | file read, subprocess；无网络 |
| `scripts/check-docx-format-consistency.py` | self-check | file read, subprocess；无网络 |
| `scripts/check-docx-template-customization.py` | self-check | file read, subprocess；无网络 |

## Release Rule

未发现高风险凭据或不受限的远程内联执行。证据支持仓库内 production governance with warnings（带警告的生产治理），不支持声称完整的公开受治理发布就绪。
