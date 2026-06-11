---
name: invoice-manager
description: OCR 识别 PDF 发票，生成报销汇总 Excel，并归档差旅票据。在 vc-analyst 中，它是运营辅助，不进入投资决策流程。
source_repo: https://github.com/justinjia0813/invoice-manager
---

# Invoice Manager

`invoice-manager` 是 `vc-analyst` 收录的外部 skill，用于出差后或月底报销周期的 VC 运营工作。

## 事实来源

- 仓库：<https://github.com/justinjia0813/invoice-manager>
- 作用：PDF 发票 OCR -> 复核后的发票 JSON -> 报销汇总 Excel + PDF 自动归档
- 系统依赖：`poppler`、`tesseract`、`tesseract-lang`
- Python 依赖：`openpyxl`、`pdf2image`、`pytesseract`

## vc-analyst 接入方式

这个 skill 只用于运营报销整理。

标准链路：

1. 将发票 PDF 放入上游 skill 的 `input/` 目录。
2. 运行 OCR，得到中间态发票 JSON。
3. 复核日期、金额、地点、费用类型、销售方、项目名。
4. 生成月度报销汇总表，并归档 PDF。
5. 如果某次出差对应已跟踪项目，归档命名使用同一个 `projects/{company-slug}` slug。

## 边界

这个 skill 不属于投资决策流程。

它可以帮助维护差旅和项目运营记录，但发票数据不应被当作尽调证据。除非用户明确把它作为项目原始素材提供，并复制进对应项目的 `00-source/` 归档。
