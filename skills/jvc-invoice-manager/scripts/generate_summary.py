#!/usr/bin/env python3
"""
发票汇总生成脚本：根据JSON数据生成报销Excel + 归档PDF
用法：python3 generate_summary.py <发票数据JSON> [--month 2026-03]
JSON格式见下方 invoices 列表
"""
import sys, os, json, shutil, uuid, openpyxl
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
TEMPLATE = BASE / 'templates' / '报销模板.xlsx'
ARCHIVE = BASE / 'archive'
INPUT = BASE / 'input'

def generate(invoices_data, month):
    """生成汇总表和归档"""
    archive_month = ARCHIVE / f'{month}_报销汇总.xlsx'

    # 如果汇总表已存在，追加行
    if archive_month.exists():
        wb = openpyxl.load_workbook(archive_month)
        ws = wb['报销明细']
        start_row = ws.max_row + 1
    else:
        wb = openpyxl.load_workbook(TEMPLATE)
        ws = wb['报销明细']
        start_row = 2

    for i, inv in enumerate(invoices_data):
        row = start_row + i
        ws[f'A{row}'] = str(uuid.uuid4())[:8]
        ws[f'B{row}'] = inv.get('start', '')
        ws[f'C{row}'] = inv.get('end', inv.get('start', ''))
        ws[f'D{row}'] = inv.get('location', '')
        ws[f'E{row}'] = inv.get('amount') if inv.get('amount') else ''
        ws[f'F{row}'] = inv.get('type', '')
        ws[f'I{row}'] = inv.get('project', '')
        ws[f'J{row}'] = inv.get('remark', '')
        ws[f'K{row}'] = inv.get('new_name', '')
        ws[f'L{row}'] = inv.get('reimburser', '')

    ARCHIVE.mkdir(parents=True, exist_ok=True)
    wb.save(archive_month)
    print(f'✅ 汇总表: {archive_month}')

    # 归档PDF
    for inv in invoices_data:
        folder_name = inv.get('folder')
        if not folder_name:
            print(f'⚠️ 跳过 {inv.get("original")} — 缺少 folder')
            continue

        trip_dir = ARCHIVE / folder_name
        trip_dir.mkdir(parents=True, exist_ok=True)

        original = inv.get('original', '')
        new_name = inv.get('new_name', '')

        src = INPUT / original
        dst = trip_dir / new_name

        if src.exists():
            shutil.copy2(src, dst)
            print(f'📁 {original} → {trip_dir.name}/{new_name}')
        else:
            print(f'⚠️ 文件不存在: {src}')

def main():
    if len(sys.argv) < 2:
        print("用法: python3 generate_summary.py <invoices.json> [--month 2026-03]")
        sys.exit(1)

    json_path = sys.argv[1]
    month = '2026-03'

    for i, arg in enumerate(sys.argv):
        if arg == '--month' and i + 1 < len(sys.argv):
            month = sys.argv[i + 1]

    with open(json_path, 'r', encoding='utf-8') as f:
        invoices_data = json.load(f)

    generate(invoices_data, month)
    print('\n🎉 完成！')

if __name__ == '__main__':
    main()
