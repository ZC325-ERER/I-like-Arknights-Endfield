# -*- coding: utf-8 -*-
"""生成实验报告插图与 docx。"""
import os
import re

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

BASE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(BASE, "实验报告_LED中断闪烁.md")
DOCX = os.path.join(BASE, "实验报告_LED中断闪烁.docx")
FIG = os.path.join(BASE, "图2_波形时序.png")
FIG_FLOW = os.path.join(BASE, "图1_中断链路.png")

FONT_YAHEI = "C:/Windows/Fonts/msyh.ttc"
FONT_YAHEI_BD = "C:/Windows/Fonts/msyhbd.ttc"


# ---------------------------------------------------------------- 插图
def rounded(d, box, radius, fill, outline, width=3):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def make_flow():
    W, H = 1240, 1010
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    f_title = ImageFont.truetype(FONT_YAHEI_BD, 28)
    f_box = ImageFont.truetype(FONT_YAHEI, 23)

    d.text((40, 26), "TIM3 更新中断 → LED 翻转 执行链路", font=f_title, fill=(30, 30, 30))

    steps = [
        "TIM3 计数器：32 MHz ÷ 3200 = 10 kHz",
        "计数到 ARR = 2499，产生更新事件 UE",
        "UIF = 1，且 UIE = 1（中断使能）",
        "NVIC：TIM3_IRQn，抢占优先级 1",
        "TIM3_IRQHandler()  →  HAL_TIM_IRQHandler(&htim3)",
        "HAL_TIM_PeriodElapsedCallback(&htim3)",
        "HAL_GPIO_TogglePin(PA9)，板载 PC13 同步翻转",
    ]

    bw, bh, gap = 860, 86, 40
    top = 96
    x0 = (W - bw) // 2
    for i, s in enumerate(steps):
        y = top + i * (bh + gap)
        fill = (0xEA, 0xF1, 0xFB) if i % 2 == 0 else (0xF3, 0xF7, 0xEE)
        rounded(d, (x0, y, x0 + bw, y + bh), 14, fill, (0x1F, 0x3B, 0x63))
        tw = d.textlength(s, font=f_box)
        d.text((W / 2 - tw / 2, y + bh / 2 - 15), s, font=f_box, fill=(0x20, 0x20, 0x20))
        if i < len(steps) - 1:
            cy = y + bh
            d.line([(W / 2, cy + 4), (W / 2, cy + gap - 10)], fill=(0x1F, 0x3B, 0x63), width=4)
            d.polygon([(W / 2 - 9, cy + gap - 14), (W / 2 + 9, cy + gap - 14), (W / 2, cy + gap - 2)],
                      fill=(0x1F, 0x3B, 0x63))
    img.save(FIG_FLOW, "PNG")


def make_figure():
    W, H = 1400, 620
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)

    f_title = ImageFont.truetype(FONT_YAHEI_BD, 30)
    f_lab = ImageFont.truetype(FONT_YAHEI, 24)
    f_small = ImageFont.truetype(FONT_YAHEI, 20)

    left, right = 120, 1340
    y_hi, y_lo = 170, 330
    axis_y = 430

    def X(ms):
        return left + (right - left) * ms / 1000.0

    # 网格与分隔线
    for ms in (250, 500, 750):
        d.line([(X(ms), 110), (X(ms), axis_y)], fill=(210, 210, 210), width=2)
    for ms, txt in ((0, "0"), (250, "250"), (500, "500"), (750, "750"), (1000, "1000 ms")):
        tx = X(ms) - 22
        if ms == 1000:
            tx = X(ms) - 96
        d.text((tx, axis_y + 10), txt, font=f_small, fill=(80, 80, 80))

    # 时间轴
    d.line([(left - 20, axis_y), (right + 10, axis_y)], fill=(60, 60, 60), width=3)
    # 电平轴
    d.line([(left - 20, 110), (left - 20, axis_y)], fill=(60, 60, 60), width=3)

    # 波形：高 0-250，低 250-500，高 500-750，低 750-1000
    seg = [(0, 250, y_hi), (250, 500, y_lo), (500, 750, y_hi), (750, 1000, y_lo)]
    pts = []
    for i, (a, b, y) in enumerate(seg):
        if i == 0:
            pts.append((X(a), y))
        else:
            pts.append((X(a), y))
        pts.append((X(b), y))
    d.line(pts, fill=(214, 48, 49), width=6, joint="curve")

    # 标签
    d.text((X(125) - 60, y_hi - 46), "灭（高电平）", font=f_lab, fill=(180, 30, 30))
    d.text((X(375) - 60, y_lo + 16), "亮（低电平）", font=f_lab, fill=(180, 30, 30))
    d.text((X(625) - 60, y_hi - 46), "灭", font=f_lab, fill=(180, 30, 30))
    d.text((X(875) - 60, y_lo + 16), "亮", font=f_lab, fill=(180, 30, 30))

    # 250 ms 标注
    y_dim = axis_y + 42
    d.line([(X(0), y_dim), (X(250), y_dim)], fill=(40, 90, 200), width=3)
    d.line([(X(0), y_dim - 8), (X(0), y_dim + 8)], fill=(40, 90, 200), width=3)
    d.line([(X(250), y_dim - 8), (X(250), y_dim + 8)], fill=(40, 90, 200), width=3)
    d.text((X(125) - 45, y_dim + 8), "250 ms", font=f_lab, fill=(40, 90, 200))

    # 500 ms 周期标注
    y_dim2 = axis_y + 105
    d.line([(X(0), y_dim2), (X(500), y_dim2)], fill=(30, 140, 90), width=3)
    d.line([(X(0), y_dim2 - 8), (X(0), y_dim2 + 8)], fill=(30, 140, 90), width=3)
    d.line([(X(500), y_dim2 - 8), (X(500), y_dim2 + 8)], fill=(30, 140, 90), width=3)
    d.text((X(250) - 90, y_dim2 + 8), "一个完整周期 500 ms", font=f_lab, fill=(30, 140, 90))

    d.text((left, 40), "PA9 输出波形：亮 250 ms / 灭 250 ms，闪烁周期 500 ms", font=f_title, fill=(30, 30, 30))
    img.save(FIG, "PNG")


# ---------------------------------------------------------------- docx 基础样式
def set_font(run, name="宋体", size=10.5, bold=False, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), name)
    rfonts.set(qn("w:ascii"), name)
    rfonts.set(qn("w:hAnsi"), name)


def shade(paragraph, fill="F2F2F2"):
    ppr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    ppr.append(shd)


def add_inline(paragraph, text, size=10.5, base_font="宋体"):
    """处理 **加粗** 与 `行内代码`。"""
    tokens = re.split(r"(\*\*.+?\*\*|`[^`]+`)", text)
    for tok in tokens:
        if not tok:
            continue
        if tok.startswith("**") and tok.endswith("**") and len(tok) > 4:
            for part in re.split(r"(`[^`]+`)", tok[2:-2]):
                if not part:
                    continue
                if part.startswith("`") and part.endswith("`") and len(part) > 2:
                    r = paragraph.add_run(part[1:-1])
                    set_font(r, "Consolas", size - 1, bold=True)
                    r.font.color.rgb = RGBColor(0xC7, 0x25, 0x4E)
                else:
                    r = paragraph.add_run(part)
                    set_font(r, base_font, size, bold=True)
        elif tok.startswith("`") and tok.endswith("`") and len(tok) > 2:
            r = paragraph.add_run(tok[1:-1])
            set_font(r, "Consolas", size - 1)
            r.font.color.rgb = RGBColor(0xC7, 0x25, 0x4E)
        else:
            r = paragraph.add_run(tok)
            set_font(r, base_font, size)


# ---------------------------------------------------------------- 解析 md
def parse(md_text):
    lines = md_text.splitlines()
    blocks, i = [], 0
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith("```"):
            i += 1
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i].rstrip())
                i += 1
            i += 1
            blocks.append(("code", "\n".join(code)))
            continue
        if s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            blocks.append(("table", rows))
            continue
        if s.startswith("!["):
            m = re.search(r"\((.*?)\)", s)
            blocks.append(("image", m.group(1) if m else ""))
            i += 1
            continue
        for tag, prefix in (("h3", "### "), ("h2", "## "), ("h1", "# ")):
            if s.startswith(prefix):
                blocks.append((tag, s[len(prefix):]))
                break
        else:
            if s.startswith("> "):
                blocks.append(("quote", s[2:]))
            elif s == "---":
                blocks.append(("hr", ""))
            elif s.startswith("- "):
                blocks.append(("bullet", s[2:]))
            elif re.match(r"^\d+\.\s+", s):
                m = re.match(r"^(\d+)\.\s+(.*)$", s)
                blocks.append(("num", "%s\x00%s" % (m.group(1), m.group(2))))
            elif s:
                blocks.append(("p", s))
            i += 1
            continue
        i += 1
    return blocks


# ---------------------------------------------------------------- 生成 docx
def build_docx(blocks):
    doc = Document()

    sec = doc.sections[0]
    sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
    sec.top_margin = sec.bottom_margin = Cm(2.3)
    sec.left_margin = sec.right_margin = Cm(2.5)

    normal = doc.styles["Normal"]
    normal.font.name = "宋体"
    normal.font.size = Pt(10.5)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    normal.paragraph_format.line_spacing = 1.35
    normal.paragraph_format.space_after = Pt(4)

    num_i = 0
    for i, (kind, content) in enumerate(blocks):
        if kind == "h1":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(14)
            r = p.add_run(content)
            set_font(r, "黑体", 18, bold=True, color=(0x1F, 0x3B, 0x63))
        elif kind == "h2":
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.keep_with_next = True
            r = p.add_run(content)
            set_font(r, "黑体", 14, bold=True, color=(0x1F, 0x3B, 0x63))
            pPr = p._p.get_or_add_pPr()
            pbdr = OxmlElement("w:pBdr")
            bottom = OxmlElement("w:bottom")
            bottom.set(qn("w:val"), "single")
            bottom.set(qn("w:sz"), "6")
            bottom.set(qn("w:space"), "2")
            bottom.set(qn("w:color"), "1F3B63")
            pbdr.append(bottom)
            pPr.append(pbdr)
        elif kind == "h3":
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            r = p.add_run(content)
            set_font(r, "黑体", 12, bold=True, color=(0x2E, 0x54, 0x8A))
        elif kind == "p":
            p = doc.add_paragraph()
            if not content.startswith("**实验") and not content.startswith("**开发"):
                p.paragraph_format.first_line_indent = Pt(21)
            p.paragraph_format.line_spacing = 1.35
            add_inline(p, content)
        elif kind == "quote":
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.6)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(6)
            add_inline(p, content, size=10)
            for r in p.runs:
                r.font.color.rgb = RGBColor(0x59, 0x59, 0x59)
        elif kind == "bullet":
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.space_after = Pt(2)
            add_inline(p, content)
        elif kind == "num":
            no, body = content.split("\x00", 1)
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.85)
            p.paragraph_format.first_line_indent = Cm(-0.85)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.3
            add_inline(p, no + ". " + body)
        elif kind == "code":
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.4)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.keep_together = content.count("\n") <= 20
            shade(p)
            r = p.add_run(content)
            set_font(r, "Consolas", 8.5)
        elif kind == "table":
            rows = [r for r in content if not re.match(r"^\|[\s:|-]+\|$", r)]
            cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
            ncol = max(len(r) for r in cells)
            table = doc.add_table(rows=len(cells), cols=ncol)
            table.style = "Table Grid"
            table.alignment = WD_TABLE_ALIGNMENT.CENTER

            # 表头跨页自动重复；每行内容不从中间断开
            trPr = table.rows[0]._tr.get_or_add_trPr()
            hdr = OxmlElement("w:tblHeader")
            hdr.set(qn("w:val"), "true")
            trPr.append(hdr)
            for row_obj in table.rows:
                cant = OxmlElement("w:cantSplit")
                row_obj._tr.get_or_add_trPr().append(cant)

            for ri, row in enumerate(cells):
                for ci in range(ncol):
                    txt = row[ci] if ci < len(row) else ""
                    cell = table.cell(ri, ci)
                    cell.text = ""
                    p = cell.paragraphs[0]
                    p.paragraph_format.space_after = Pt(0)
                    add_inline(p, txt, size=9)
                    if ri == 0:
                        for r in p.runs:
                            r.font.bold = True
                        tcpr = cell._tc.get_or_add_tcPr()
                        shd = OxmlElement("w:shd")
                        shd.set(qn("w:val"), "clear")
                        shd.set(qn("w:fill"), "DCE6F1")
                        tcpr.append(shd)
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
        elif kind == "image":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(8)
            p.add_run().add_picture(os.path.join(BASE, content), width=Cm(15.2))
        elif kind == "hr":
            pass

    doc.save(DOCX)


if __name__ == "__main__":
    make_flow()
    make_figure()
    with open(MD, encoding="utf-8") as f:
        text = f.read()
    build_docx(parse(text))
    print("ok:", DOCX)
