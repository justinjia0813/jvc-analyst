#!/usr/bin/env python3
"""
会议纪要Word生成脚本
用法：python3 generate_meeting_notes.py <sections.json> --output <output.docx> --template <template.docx>

sections.json 格式：
{
  "title": "2026/03/23 线上 访谈{深安锂能}",
  "sections": [
    {
      "heading": "一、公司基本情况",
      "content": "一个长句介绍..."
    },
    {
      "heading": "二、公司核心技术",
      "subsections": [
        {"heading": "技术路线", "content": "..."},
        {"heading": "核心技术", "content": "..."},
        {"heading": "达成的性能指标", "content": "..."}
      ]
    },
    ...
  ]
}
"""
import sys, json, copy
from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

BASE = Path(__file__).resolve().parent.parent
DEFAULT_TEMPLATE = BASE / 'templates' / '访谈纪要模板.docx'
DEFAULT_OUTPUT = BASE / 'output'

def set_run_font(run, cn_font='KaiTi', en_font='Times New Roman', size=Pt(10), bold=False):
    """设置 run 的中英文字体"""
    run.font.size = size
    run.font.bold = bold
    run.font.name = en_font
    # 设置中文字体
    r = run._element
    rPr = r.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = rPr.makeelement(qn('w:rFonts'), {})
        rPr.insert(0, rFonts)
    rFonts.set(qn('w:eastAsia'), cn_font)

def create_document(data, template_path, output_path):
    """基于模板创建会议纪要文档"""
    doc = Document(template_path)

    # 清空正文段落（保留页眉页脚和样式）
    for p in doc.paragraphs:
        p._element.getparent().remove(p._element)

    # 添加标题
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(data['title'])
    set_run_font(run, size=Pt(18), bold=True)

    # 添加各板块
    for section in data['sections']:
        # 章节标题
        heading = doc.add_paragraph()
        heading.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        run = heading.add_run(section['heading'])
        set_run_font(run, size=Pt(10), bold=True)

        # 正文内容
        if 'content' in section and section['content']:
            content_p = doc.add_paragraph()
            content_p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run = content_p.add_run(section['content'])
            set_run_font(run, size=Pt(10))

        # 子章节
        if 'subsections' in section:
            for sub in section['subsections']:
                sub_heading = doc.add_paragraph()
                sub_heading.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                run = sub_heading.add_run(sub['heading'])
                set_run_font(run, size=Pt(10))

                if 'content' in sub and sub['content']:
                    sub_content = doc.add_paragraph()
                    sub_content.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    run = sub_content.add_run(sub['content'])
                    set_run_font(run, size=Pt(10))

    doc.save(output_path)
    print(f'✅ 纪要已生成: {output_path}')

def main():
    if len(sys.argv) < 2:
        print("用法: python3 generate_meeting_notes.py <sections.json> [--output path] [--template path]")
        sys.exit(1)

    json_path = sys.argv[1]
    output = str(DEFAULT_OUTPUT)
    template = str(DEFAULT_TEMPLATE)

    for i, arg in enumerate(sys.argv):
        if arg == '--output' and i + 1 < len(sys.argv):
            output = sys.argv[i + 1]
        if arg == '--template' and i + 1 < len(sys.argv):
            template = sys.argv[i + 1]

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    import os

    # 如果 output 是目录（不以 .docx 结尾），拼接 filename
    if output.endswith('.docx'):
        output_path = output
    else:
        os.makedirs(output, exist_ok=True)
        filename = data.get('filename', '访谈纪要.docx')
        output_path = os.path.join(output, filename)

    create_document(data, template, output_path)

if __name__ == '__main__':
    main()
