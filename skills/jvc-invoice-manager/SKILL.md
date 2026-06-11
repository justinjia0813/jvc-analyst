---
name: jvc-invoice-manager
description: |
  发票整理：OCR 识别 PDF 发票，生成报销汇总 Excel，并按月份、地点、项目自动归档差旅票据；这是运营辅助，不进入投资决策流程。
  Use when user says '整理发票', '处理发票', '报销归档', '发票汇总', 'invoice manager'.
integrated_from: https://github.com/justinjia0813/invoice-manager
---

# /jvc-invoice-manager — 发票管理器

`/jvc-invoice-manager` 是 `jvc-analyst` 内置的运营辅助 skill，用于出差后或月底报销周期。它处理 PDF 发票 OCR、人工复核后的发票 JSON、报销汇总 Excel 和 PDF 归档。

它不属于投资决策流程。除非用户明确把发票作为项目原始素材提供，否则发票数据不得进入尽调判断。

## 输入

- PDF 发票目录
- 用户确认后的归属项目、报销人、费用类型、地点、金额
- 可选：月份，例如 `2026-06`

## 目录

- `skills/jvc-invoice-manager/input/`：待处理发票 PDF，已被 `.gitignore` 忽略
- `skills/jvc-invoice-manager/archive/`：报销汇总和归档输出，已被 `.gitignore` 忽略
- `skills/jvc-invoice-manager/templates/报销模板.xlsx`：汇总表模板

## 流程

### 1. OCR 识别

```bash
python3 skills/jvc-invoice-manager/scripts/process_invoices.py \
  skills/jvc-invoice-manager/input \
  --output /tmp/jvc_invoice_results.json
```

OCR 会尽量提取：

- 金额
- 日期
- 费用类型
- 地点
- 销售方
- 发票号

### 2. 人工确认

生成汇总表前必须让用户确认：

- 归属项目
- 报销人
- 费用类型、金额、地点是否正确
- 行程归类是否合理
- PDF 重命名是否符合规则

### 3. 生成汇总表和归档

用确认后的 JSON 运行：

```bash
python3 skills/jvc-invoice-manager/scripts/generate_summary.py \
  /tmp/jvc_invoice_confirmed.json \
  --month 2026-06
```

输出：

- `skills/jvc-invoice-manager/archive/{YYYY-MM}_报销汇总.xlsx`
- `skills/jvc-invoice-manager/archive/{YYYY-MM}{出差地}{项目名称}差旅/`

## JSON 骨架

```json
[
  {
    "original": "invoice.pdf",
    "start": "2026-06-11",
    "end": "2026-06-11",
    "location": "上海",
    "amount": 88.0,
    "type": "餐费",
    "project": "项目名称",
    "new_name": "20260611_餐费_销售方.pdf",
    "folder": "2026-06上海项目名称差旅",
    "reimburser": "报销人"
  }
]
```

## 质量红线

- OCR 结果必须复核，不要直接把未确认数据写入报销表。
- 每次必须确认归属项目和报销人，不能沿用上次默认值。
- 归档命名可以引用 `projects/{company-slug}`，但发票本身不是尽调证据。
- PDF 原件只复制到归档目录，不在脚本中删除原件。

## 依赖

```bash
brew install poppler tesseract tesseract-lang
python3 -m pip install -r skills/jvc-invoice-manager/requirements.txt
```
