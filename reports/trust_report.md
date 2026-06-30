# Trust Report

日期：2026-06-21

证据边界：这是 production governance 的本地 trust report，不是 public governed release 的完整安全认证。

## 缩写说明

| 缩写 | 英文全称 | 中文全称 | 含义 |
| --- | --- | --- | --- |
| CLI | Command-Line Interface | 命令行接口 | 脚本通过终端命令运行的接口 |
| OCR | Optical Character Recognition | 光学字符识别 | 从 PDF 发票中识别文字 |
| PDF | Portable Document Format | 便携式文档格式 | 发票和归档票据格式 |
| DOCX | Office Open XML Word Document | Word 文档格式 | 访谈纪要输出格式 |
| SHA-256 | Secure Hash Algorithm 256-bit | 256 位安全哈希算法 | package source contract 的内容指纹 |

## Source Contract Hash

`77c4e9bf97b2acb452c6ac54ef1da6aa5813488b20bd6577b1c16d164b125713`

Hash scope: `manifest`、`agents`、`security`、`skills`、`templates`、`scripts`、`evals`、`library`、`README`、`CLAUDE`、`setup`。生成报告和本地 telemetry 不进入 hash。

## Gate Summary

| Gate | Status | Evidence |
| --- | --- | --- |
| Secret scan | pass | No obvious secret patterns are expected in package files |
| Network scripts | pass | `security/network_policy.json` declares no shipped network-capable scripts |
| Permission approvals | pass | `security/permission_policy.json` approves file read, file write, subprocess |
| Dependency review | warn | Some Python and OCR dependencies are documented but not fully version-pinned |
| Script help surface | warn | Invoice scripts use manual `sys.argv`; workbook and DOCX scripts use `argparse` |
| Runtime permission probes | warn | Packaged adapter probes are missing evidence because no `dist` package is generated |

## Script Surface

| Script | Interface | Capabilities |
| --- | --- | --- |
| `scripts/check-governance.py` | CLI | file read |
| `scripts/check-skill-evals.py` | CLI | file read |
| `scripts/generate-workbook.py` | argparse CLI | file read, file write |
| `scripts/validate-workbook.py` | argparse CLI | file read |
| `skills/jvc-knowledge-tree-builder/scripts/collect_sources.py` | argparse CLI | file read, file write |
| `skills/jvc-knowledge-tree-builder/scripts/check_package.py` | CLI | file read |
| `skills/jvc-meeting-notes/scripts/generate_meeting_notes.py` | argparse CLI | file read, file write |
| `skills/jvc-invoice-manager/scripts/process_invoices.py` | manual CLI | file read, file write, OCR |
| `skills/jvc-invoice-manager/scripts/generate_summary.py` | manual CLI | file read, file write, PDF copy |

## Release Rule

No high-risk secrets or unrestricted remote inline execution are documented. This supports production governance with visible warnings. It does not support claiming full governed public release readiness.
