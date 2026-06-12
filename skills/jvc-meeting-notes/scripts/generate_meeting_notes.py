#!/usr/bin/env python3
"""
会议纪要 Word 生成脚本
用法：python3 generate_meeting_notes.py <sections.json> --output <output.docx> [--template <template.docx>]

模板解析顺序：
1. 命令行 `--template`
2. 环境变量 `JVC_DOCX_TEMPLATE`
3. `skills/jvc-meeting-notes/templates/custom.docx`
4. 中性默认模板 `skills/jvc-meeting-notes/templates/访谈纪要模板.docx`

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
import argparse
import json
import os
import sys
from pathlib import Path
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

BASE = Path(__file__).resolve().parent.parent
DEFAULT_TEMPLATE = BASE / 'templates' / '访谈纪要模板.docx'
CUSTOM_TEMPLATE = BASE / 'templates' / 'custom.docx'
DEFAULT_OUTPUT = BASE / 'output'
TEMPLATE_ENV = 'JVC_DOCX_TEMPLATE'


def resolve_template_path(explicit_template=None):
    """Resolve the template without falling back silently from bad user input."""
    if explicit_template:
        path = Path(explicit_template).expanduser()
        if not path.exists():
            raise FileNotFoundError(f'指定模板不存在: {path}')
        return path

    env_template = os.environ.get(TEMPLATE_ENV)
    if env_template:
        path = Path(env_template).expanduser()
        if not path.exists():
            raise FileNotFoundError(f'{TEMPLATE_ENV} 指向的模板不存在: {path}')
        return path

    if CUSTOM_TEMPLATE.exists():
        return CUSTOM_TEMPLATE

    if not DEFAULT_TEMPLATE.exists():
        raise FileNotFoundError(f'默认模板不存在: {DEFAULT_TEMPLATE}')
    return DEFAULT_TEMPLATE


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


def _style_exists(doc, style_name):
    if not style_name:
        return False
    try:
        doc.styles[style_name]
    except KeyError:
        return False
    return True


def extract_style_hints(doc):
    """Use existing template paragraphs as style hints before clearing them."""
    paragraphs = [p for p in doc.paragraphs if p.text.strip()]
    hints = {
        'title': paragraphs[0].style.name if len(paragraphs) > 0 else None,
        'section': paragraphs[1].style.name if len(paragraphs) > 1 else None,
        'body': paragraphs[2].style.name if len(paragraphs) > 2 else None,
        'subsection': paragraphs[5].style.name if len(paragraphs) > 5 else None,
    }
    return {key: value for key, value in hints.items() if _style_exists(doc, value)}


def add_paragraph(doc, text, style_hints, style_key, alignment, fallback_size, fallback_bold=False):
    style_name = style_hints.get(style_key)
    if not style_name and _style_exists(doc, 'Normal'):
        style_name = 'Normal'
    paragraph = doc.add_paragraph(style=style_name) if style_name else doc.add_paragraph()
    paragraph.alignment = alignment
    run = paragraph.add_run(text)
    if not style_name:
        set_run_font(run, size=fallback_size, bold=fallback_bold)
    return paragraph


def create_document(data, template_path, output_path):
    """基于模板创建会议纪要文档"""
    doc = Document(template_path)
    style_hints = extract_style_hints(doc)

    # 清空正文段落（保留页眉页脚和样式）
    for p in doc.paragraphs:
        p._element.getparent().remove(p._element)

    # 添加标题
    add_paragraph(
        doc,
        data['title'],
        style_hints,
        'title',
        WD_ALIGN_PARAGRAPH.CENTER,
        Pt(18),
        fallback_bold=True,
    )

    # 添加各板块
    for section in data['sections']:
        # 章节标题
        add_paragraph(
            doc,
            section['heading'],
            style_hints,
            'section',
            WD_ALIGN_PARAGRAPH.JUSTIFY,
            Pt(10),
            fallback_bold=True,
        )

        # 正文内容
        if 'content' in section and section['content']:
            add_paragraph(
                doc,
                section['content'],
                style_hints,
                'body',
                WD_ALIGN_PARAGRAPH.JUSTIFY,
                Pt(10),
            )

        # 子章节
        if 'subsections' in section:
            for sub in section['subsections']:
                add_paragraph(
                    doc,
                    sub['heading'],
                    style_hints,
                    'subsection',
                    WD_ALIGN_PARAGRAPH.JUSTIFY,
                    Pt(10),
                )

                if 'content' in sub and sub['content']:
                    add_paragraph(
                        doc,
                        sub['content'],
                        style_hints,
                        'body',
                        WD_ALIGN_PARAGRAPH.JUSTIFY,
                        Pt(10),
                    )

    doc.save(output_path)
    print(f'✅ 纪要已生成: {output_path}')
    print(f'模板: {template_path}')


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description='Generate a meeting-note DOCX from sections JSON.'
    )
    parser.add_argument('json_path', help='sections JSON path')
    parser.add_argument('--output', default=str(DEFAULT_OUTPUT), help='output .docx path or output directory')
    parser.add_argument('--template', help='custom .docx template path')
    return parser.parse_args(argv)


def main():
    args = parse_args(sys.argv[1:])

    with open(args.json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    template = resolve_template_path(args.template)

    # 如果 output 是目录（不以 .docx 结尾），拼接 filename
    if args.output.endswith('.docx'):
        output_path = args.output
    else:
        os.makedirs(args.output, exist_ok=True)
        filename = data.get('filename', '访谈纪要.docx')
        output_path = os.path.join(args.output, filename)

    create_document(data, template, output_path)

if __name__ == '__main__':
    main()
