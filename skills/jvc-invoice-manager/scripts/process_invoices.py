#!/usr/bin/env python3
"""
发票处理脚本：OCR识别PDF发票，提取关键信息，输出JSON
"""
import sys
import os
import json
from pdf2image import convert_from_path
import pytesseract

def ocr_pdf(pdf_path):
    """OCR识别PDF发票，返回文本"""
    images = convert_from_path(pdf_path, dpi=300)
    texts = []
    for img in images:
        # 使用中英文混合识别
        text = pytesseract.image_to_string(img, lang='chi_sim+eng')
        texts.append(text)
    return '\n'.join(texts)

def extract_invoice_info(text, filename):
    """从OCR文本中提取发票关键信息"""
    import re

    info = {
        'original_filename': filename,
        'amount': None,
        'date': None,
        'invoice_type': None,  # 发票类型（餐饮/交通/住宿等）
        'invoice_number': None,
        'seller': None,
        'location': None,
    }

    # 提取金额
    amount_patterns = [
        r'¥\s*([\d,]+\.?\d*)',
        r'金额[：:]\s*([\d,]+\.?\d*)',
        r'合计[：:]\s*([\d,]+\.?\d*)',
        r'总金额[：:]\s*([\d,]+\.?\d*)',
        r'价税合计[：:]\s*¥?\s*([\d,]+\.?\d*)',
        r'小写[：:]\s*¥?\s*([\d,]+\.?\d*)',
        r'¥\s*([0-9]+\.?[0-9]*)',
    ]
    for p in amount_patterns:
        m = re.search(p, text)
        if m:
            amt = m.group(1).replace(',', '')
            try:
                info['amount'] = float(amt)
            except:
                pass
            break

    # 提取日期
    date_patterns = [
        r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日',
        r'(\d{4})-(\d{2})-(\d{2})',
        r'开票日期[：:]\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日',
    ]
    for p in date_patterns:
        m = re.search(p, text)
        if m:
            info['date'] = f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
            break

    # 提取发票号码
    inv_patterns = [
        r'发票号码[：:]\s*(\d{8,20})',
        r'No[.:]?\s*(\d{8,20})',
        r'编号[：:]\s*(\d{8,20})',
    ]
    for p in inv_patterns:
        m = re.search(p, text)
        if m:
            info['invoice_number'] = m.group(1)
            break

    # 提取销售方/开票方
    seller_patterns = [
        r'销售方[：:名称]*\s*(.+?)(?:\n|$)',
        r'开票方[：:名称]*\s*(.+?)(?:\n|$)',
        r'名称[：:]\s*(.+?)(?:\n|$)',
        r'收款方[：:]\s*(.+?)(?:\n|$)',
        r'服务提供方[：:]\s*(.+?)(?:\n|$)',
    ]
    for p in seller_patterns:
        m = re.search(p, text)
        if m:
            seller = m.group(1).strip()[:50]
            if seller and len(seller) > 2:
                info['seller'] = seller
                break

    # 提取地点（从销售方名称或地址中猜测）
    cities = ['北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '重庆',
              '武汉', '西安', '苏州', '天津', '长沙', '郑州', '青岛', '大连',
              '宁波', '厦门', '福州', '合肥', '济南', '昆明', '贵阳', '南昌',
              '石家庄', '太原', '沈阳', '哈尔滨', '长春', '兰州', '海口',
              '衢州', '温州', '无锡', '常州', '佛山', '东莞', '珠海', '嘉兴',
              '绍兴', '台州', '金华', '徐州', '南通', '烟台', '中山', '惠州']
    for city in cities:
        if city in text:
            info['location'] = city
            break

    # 判断费用类型
    type_keywords = {
        '餐费': ['餐饮', '餐费', '食品', '饭店', '餐厅', '外卖', '餐饮服务', '食品', '饮品'],
        '住宿费': ['住宿', '酒店', '宾馆', '旅店', '旅馆', '民宿'],
        '市内交通费（含路桥费）': ['出租', '网约车', '滴滴', '地铁', '公交', '加油', '停车', '高速', '过路费', '路桥', '出租车'],
        '通讯费': ['通讯', '电话', '手机', '宽带', '电信', '移动', '联通'],
        '快递费用': ['快递', '物流', '顺丰', '中通', '圆通', '韵达'],
        '信息服务费': ['信息服务', '技术服务', '咨询服务', '技术服务费', '服务费'],
        '差旅费用': ['火车', '高铁', '机票', '航空', '携程', '去哪儿', '12306'],
        '招待费/礼品费': ['礼品', '招待', '礼品费'],
    }

    for ftype, keywords in type_keywords.items():
        for kw in keywords:
            if kw in text:
                info['invoice_type'] = ftype
                break
        if info['invoice_type']:
            break

    return info

def main():
    if len(sys.argv) < 2:
        print("用法: python3 process_invoices.py <文件夹路径> [--output <输出json路径>]")
        sys.exit(1)

    folder = sys.argv[1]
    output_path = None

    for i, arg in enumerate(sys.argv):
        if arg == '--output' and i + 1 < len(sys.argv):
            output_path = sys.argv[i + 1]

    if not os.path.isdir(folder):
        print(f"错误: {folder} 不是有效目录")
        sys.exit(1)

    pdfs = [f for f in os.listdir(folder) if f.lower().endswith('.pdf')]
    if not pdfs:
        print(f"错误: {folder} 中没有PDF文件")
        sys.exit(1)

    print(f"找到 {len(pdfs)} 个PDF发票，开始识别...")

    results = []
    for pdf in pdfs:
        pdf_path = os.path.join(folder, pdf)
        print(f"\n📄 处理: {pdf}")

        try:
            text = ocr_pdf(pdf_path)
            info = extract_invoice_info(text, pdf)
            results.append(info)
            print(f"   日期: {info['date'] or '未识别'}")
            print(f"   金额: {info['amount'] or '未识别'}")
            print(f"   类型: {info['invoice_type'] or '未识别'}")
            print(f"   地点: {info['location'] or '未识别'}")
            print(f"   销售方: {info['seller'] or '未识别'}")
        except Exception as e:
            print(f"   ❌ 识别失败: {e}")
            results.append({'original_filename': pdf, 'error': str(e)})

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 结果已保存到: {output_path}")
    else:
        print("\n" + json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
