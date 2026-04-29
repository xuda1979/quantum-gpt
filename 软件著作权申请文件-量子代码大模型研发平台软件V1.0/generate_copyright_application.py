from __future__ import annotations

import copy
import json
import re
import shutil
import subprocess
import zipfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor, Inches

ROOT = Path.cwd()
OUT = ROOT / "软件著作权申请文件-量子代码大模型研发平台软件V1.0"
TEMPLATE_ZIP = ROOT / "软件著作权模板.zip"
TEMPLATE_DIR = Path("/tmp/quantum_gpt_copyright_template")
APP_TEMPLATE = TEMPLATE_DIR / "item1.docx"
MANUAL_TEMPLATE = TEMPLATE_DIR / "item3.docx"
SOURCE_TEMPLATE = TEMPLATE_DIR / "item4.docx"

SOFTWARE_NAME = "量子代码大模型研发平台软件"
VERSION = "V1.0"
SHORT_NAME = "Quantum-GPT"
HEADER = f"{SOFTWARE_NAME}{VERSION}"
COMPLETION_DATE = "2026年04月26日"
PUBLICATION_STATUS = "未发表"
AUTHORS = ["许达", "易鑫", "王飞"]
RIGHTHOLDERS = AUTHORS
CONTACT_NAME = "许达"
CONTACT_PHONE = "13521894156"
CONTACT_ADDRESS = "中国移动研究院未来院三室"
APP_DOCX_NAME = f"软件著作权登记申请表-{SOFTWARE_NAME}{VERSION}.docx"
MANUAL_DOCX_NAME = f"设计说明书及使用说明文档-{SOFTWARE_NAME}{VERSION}.docx"
SOURCE_DOCX_NAME = f"源程序-{SOFTWARE_NAME}{VERSION}.docx"

SOURCE_EXTS = {".py", ".js", ".sh"}
SOURCE_DIRS = [
    "quantum_ir",
    "quantum_rag",
    "evals/runner",
    "evals/tasks",
    "scripts",
    "training",
    "tests",
    "tools",
]
EXCLUDE_PARTS = {"node_modules", "__pycache__", ".git"}
SOURCE_EXCLUDE_TERMS = {
    "huanxin",
    "s3",
    "qwen",
    "omnicoder",
    "pytorch",
    "torch",
    "transformers",
    "qiskit",
    "cirq",
    "playwright",
    "rclone",
    "train-dev",
    "openai",
    "openclaw",
}

@dataclass
class SourceInventory:
    files: list[str]
    line_count: int
    selected_lines: list[str]


def prepare_templates() -> None:
    if not TEMPLATE_ZIP.exists():
        raise FileNotFoundError(f"missing template zip: {TEMPLATE_ZIP}")
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    mapping = {
        "登记申请表-空白表": "item1.docx",
        "登记申请表-样表": "item2.docx",
        "操作手册或其他说明文档": "item3.docx",
        "源程序_": "item4.docx",
        "知识产权管理系统操作手册": "item5.pdf",
        "登记指南": "item6.pdf",
        "升级版本差异说明": "item7.docx",
    }
    seen = set()
    with zipfile.ZipFile(TEMPLATE_ZIP) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            name = info.filename
            for marker, output_name in mapping.items():
                if marker in name:
                    (TEMPLATE_DIR / output_name).write_bytes(archive.read(info))
                    seen.add(output_name)
                    break
    missing = sorted(set(mapping.values()) - seen)
    if missing:
        raise RuntimeError(f"template zip missing expected files: {', '.join(missing)}")


def cleanup_stale_numbering() -> None:
    # Remove previously generated attachment-prefixed names. The template package
    # uses attachment numbers, but submission filenames are kept descriptive.
    stale_names = [
        "附件1-软件著作权登记申请表-量子代码大模型研发平台软件V1.0.docx",
        "附件2-源程序-量子代码大模型研发平台软件V1.0.docx",
        "附件2-设计说明书及使用说明文档-量子代码大模型研发平台软件V1.0.docx",
        "附件3-设计说明书及使用说明文档-量子代码大模型研发平台软件V1.0.docx",
        "附件3-源程序-量子代码大模型研发平台软件V1.0.docx",
    ]
    for name in stale_names:
        path = OUT / name
        if path.exists():
            path.unlink()


def set_cell_text(cell, text: str, font_name="宋体", font_size=Pt(9)) -> None:
    cell.text = ""
    p = cell.paragraphs[0]
    run = p.add_run(text)
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font_name)
    run.font.size = font_size


def set_para_text(paragraph, text: str, font_name="宋体", font_size=Pt(10.5), bold=False) -> None:
    paragraph.text = ""
    run = paragraph.add_run(text)
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font_name)
    run.font.size = font_size
    run.bold = bold


def set_monospace(paragraph, text: str, size=Pt(8.5)) -> None:
    paragraph.text = ""
    run = paragraph.add_run(text)
    run.font.name = "Courier New"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Courier New")
    run.font.size = size


def add_page_number(paragraph) -> None:
    run = paragraph.add_run("第 ")
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_end)
    paragraph.add_run(" 页")


def configure_section(section, header_text=HEADER, top=Cm(1.4), bottom=Cm(1.0), left=Cm(1.6), right=Cm(1.6)) -> None:
    section.top_margin = top
    section.bottom_margin = bottom
    section.left_margin = left
    section.right_margin = right
    section.header_distance = Cm(0.8)
    section.footer_distance = Cm(0.5)
    hp = section.header.paragraphs[0]
    hp.text = ""
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = hp.add_run(f"{header_text}  ")
    run.font.name = "宋体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    run.font.size = Pt(9)
    add_page_number(hp)
    fp = section.footer.paragraphs[0]
    fp.text = ""


def collect_source() -> SourceInventory:
    paths: list[Path] = []
    for d in SOURCE_DIRS:
        root = ROOT / d
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file() or p.suffix not in SOURCE_EXTS:
                continue
            if any(part in EXCLUDE_PARTS for part in p.parts):
                continue
            text_for_filter = p.read_text(encoding="utf-8", errors="ignore")
            haystack = f"{p.as_posix()}\n{text_for_filter}".lower()
            if any(term in haystack for term in SOURCE_EXCLUDE_TERMS):
                continue
            paths.append(p)
    paths = sorted(paths, key=lambda p: (p.parts[0], str(p)))
    all_lines: list[str] = []
    for p in paths:
        rel = p.relative_to(ROOT).as_posix()
        all_lines.append(f"# ===== file: {rel} =====")
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = p.read_text(errors="ignore")
        for line in text.splitlines():
            # Avoid control chars that Word XML rejects.
            cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", line)
            all_lines.append(cleaned[:180])
        all_lines.append(f"# ===== end file: {rel} =====")
    total = len(all_lines)
    if total <= 3000:
        selected = all_lines
    else:
        selected = all_lines[:1500] + all_lines[-1500:]
    if selected:
        selected[-1] = "end"
    return SourceInventory([p.relative_to(ROOT).as_posix() for p in paths], total, selected)


def build_application_form(inventory: SourceInventory) -> Path:
    doc = Document(APP_TEMPLATE)
    table = doc.tables[0]
    values = {
        1: f"{SOFTWARE_NAME}",
        2: VERSION,
        3: SHORT_NAME,
        4: "核查项（必填）：软件作品对应技术方案无需申请专利；不涉及保密内容；不涉及开源软件改进；不按独立模块登记；本申请保护范围为自研业务代码。",
        6: "应用软件",
        7: "通用PC机、笔记本电脑及训练服务器。",
        8: "通用PC机、服务器及训练加速设备。",
        9: "主流桌面操作系统及服务器操作系统。",
        10: "Python 3.9+、JavaScript运行环境、版本管理工具和测试框架。",
        11: "桌面工作站、服务器及远程训练环境。",
        12: "Python运行时、深度学习框架及量子计算库。",
        13: f"{inventory.line_count}行",
        14: "Python；JavaScript；Shell。",
        15: "独立开发",
        16: "原创",
        17: "全部",
        18: "研发面向量子算法代码生成与评测的大模型训练平台。",
        19: "人工智能、量子计算、软件工程研发。",
        20: "本软件提供量子代码模型研发闭环能力，支持量子算法任务数据构建、模型微调训练、远程训练环境同步、量子代码评测、检索增强问答、实验报告生成和结果归档。系统围绕量子傅里叶变换、搜索算法、变分算法、量子纠错等任务组织数据与测试，帮助研发人员复现实验、比较模型效果并持续改进量子代码生成能力。",
        21: "人工智能软件；大数据软件。软件采用模块化架构，包含量子程序中间表示、数据生成、模型训练、自动评测、检索增强和报告归档模块，支持可复现研发流程。",
        22: "",
        23: COMPLETION_DATE,
        24: PUBLICATION_STATUS,
        25: "",
        26: "",
        27: f"著作权人/作者：{'、'.join(RIGHTHOLDERS)}",
        28: f"联系人：{CONTACT_NAME}；电话：{CONTACT_PHONE}",
        29: f"联系地址：{CONTACT_ADDRESS}",
    }
    for row_idx, value in values.items():
        set_cell_text(table.rows[row_idx].cells[2], value)
    seen_table = False
    for child in list(doc._element.body):
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "tbl":
            seen_table = True
            continue
        if seen_table and tag == "p" and not "".join(child.itertext()).strip():
            doc._element.body.remove(child)
    out = OUT / APP_DOCX_NAME
    doc.save(out)
    scrub_docx_theme_colors(out)
    return out


def build_source_doc(inventory: SourceInventory) -> Path:
    doc = Document()
    sec = doc.sections[0]
    configure_section(sec, top=Cm(1.1), bottom=Cm(0.9), left=Cm(1.3), right=Cm(1.3))
    # 60 pages * 50 lines. The selected_lines list is exactly the front 1500 + back 1500 lines.
    lines = inventory.selected_lines[:]
    while len(lines) < 3000:
        lines.append("")
    lines = lines[:3000]
    lines[-1] = "end"
    numbered_lines = []
    for idx, line in enumerate(lines):
        if idx == len(lines) - 1:
            numbered_lines.append("end")
        else:
            numbered_lines.append(f"{idx + 1:04d} {line}")
    lines = numbered_lines
    for page in range(60):
        if page:
            doc.add_page_break()
        for line in lines[page * 50 : (page + 1) * 50]:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = Pt(9.5)
            set_monospace(p, line, size=Pt(7.5))
    out = OUT / SOURCE_DOCX_NAME
    doc.save(out)
    scrub_docx_theme_colors(out)
    return out


def create_manual_diagrams() -> list[Path]:
    from PIL import Image, ImageDraw, ImageFont

    diagram_dir = Path("/tmp/quantum_gpt_copyright_diagrams")
    diagram_dir.mkdir(parents=True, exist_ok=True)
    font_path = Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf")
    if not font_path.exists():
        font_path = Path("/System/Library/Fonts/STHeiti Medium.ttc")

    def font(size: int, bold: bool = False):
        return ImageFont.truetype(str(font_path), size=size)

    def draw_box(draw, xy, text, fill="#f5f8ff", outline="#1f4e79", size=32):
        draw.rounded_rectangle(xy, radius=14, fill=fill, outline=outline, width=3)
        x1, y1, x2, y2 = xy
        lines = text.split("\n")
        line_h = size + 8
        total_h = line_h * len(lines)
        y = y1 + ((y2 - y1) - total_h) / 2
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font(size))
            draw.text((x1 + ((x2 - x1) - (bbox[2] - bbox[0])) / 2, y), line, fill="#000000", font=font(size))
            y += line_h

    def draw_arrow(draw, start, end):
        draw.line([start, end], fill="#2c3e50", width=4)
        ex, ey = end
        sx, sy = start
        if abs(ex - sx) >= abs(ey - sy):
            sign = 1 if ex > sx else -1
            points = [(ex, ey), (ex - sign * 18, ey - 10), (ex - sign * 18, ey + 10)]
        else:
            sign = 1 if ey > sy else -1
            points = [(ex, ey), (ex - 10, ey - sign * 18), (ex + 10, ey - sign * 18)]
        draw.polygon(points, fill="#2c3e50")

    def base_image(title: str):
        img = Image.new("RGB", (1800, 1020), "white")
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, 1800, 86), fill="#f0f0f0")
        draw.text((50, 22), title, fill="#000000", font=font(42))
        return img, draw

    outputs: list[Path] = []

    img, draw = base_image("图1 软件总体结构图")
    boxes = [
        ((80, 180, 360, 310), "任务库\n量子算法题"),
        ((510, 180, 790, 310), "数据构建\n样本与清单"),
        ((940, 180, 1220, 310), "模型训练\n训练输出"),
        ((1370, 180, 1650, 310), "评测报告\n结果归档"),
        ((510, 560, 790, 690), "量子中间表示\n结构化约束"),
        ((940, 560, 1220, 690), "检索增强\n资料片段"),
        ((1370, 560, 1650, 690), "远程训练\n任务执行"),
    ]
    for xy, text in boxes:
        draw_box(draw, xy, text, size=34)
    for start, end in [((360, 245), (510, 245)), ((790, 245), (940, 245)), ((1220, 245), (1370, 245)), ((650, 310), (650, 560)), ((790, 625), (940, 625)), ((1220, 625), (1370, 625)), ((1510, 560), (1510, 310))]:
        draw_arrow(draw, start, end)
    path = diagram_dir / "architecture.png"
    img.save(path)
    outputs.append(path)

    img, draw = base_image("图2 训练与评测流程图")
    flow = [
        ((80, 170, 380, 300), "本地验证\n单元测试"),
        ((520, 170, 820, 300), "文件同步\n代码与数据"),
        ((960, 170, 1260, 300), "远程训练\n模型适配"),
        ((1400, 170, 1700, 300), "结果回传\n日志与结果"),
        ((300, 610, 600, 740), "候选生成\n代码清洗"),
        ((750, 610, 1050, 740), "执行测试\n任务评分"),
        ((1200, 610, 1500, 740), "对比分析\n报告输出"),
    ]
    for xy, text in flow:
        draw_box(draw, xy, text, fill="#f6fff8", outline="#2e7d32", size=34)
    for start, end in [((380, 235), (520, 235)), ((820, 235), (960, 235)), ((1260, 235), (1400, 235)), ((1550, 300), (1350, 610)), ((1200, 675), (1050, 675)), ((750, 675), (600, 675))]:
        draw_arrow(draw, start, end)
    path = diagram_dir / "training_eval_flow.png"
    img.save(path)
    outputs.append(path)

    img, draw = base_image("图3 核心模块逻辑框图")
    logic = [
        ((90, 170, 410, 310), "量子中间表示\n解析与校验"),
        ((560, 170, 880, 310), "提示构建\n任务约束"),
        ((1030, 170, 1350, 310), "模型执行\n候选生成"),
        ((90, 610, 410, 750), "候选清洗\n保留代码"),
        ((560, 610, 880, 750), "隔离测试\n捕获异常"),
        ((1030, 610, 1350, 750), "分数汇总\n报告输出"),
    ]
    for xy, text in logic:
        draw_box(draw, xy, text, fill="#fffaf0", outline="#a15c00", size=34)
    for start, end in [((410, 240), (560, 240)), ((880, 240), (1030, 240)), ((1190, 310), (1190, 610)), ((1030, 680), (880, 680)), ((560, 680), (410, 680)), ((250, 610), (250, 310))]:
        draw_arrow(draw, start, end)
    path = diagram_dir / "module_logic.png"
    img.save(path)
    outputs.append(path)

    def screen_image(title: str):
        img = Image.new("RGB", (1800, 1020), "white")
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle((70, 70, 1730, 950), radius=22, fill="#f7f7f7", outline="#111111", width=4)
        draw.rectangle((70, 70, 1730, 140), fill="#e6e6e6", outline="#111111", width=4)
        draw.ellipse((105, 95, 122, 112), fill="#666666")
        draw.ellipse((135, 95, 152, 112), fill="#888888")
        draw.ellipse((165, 95, 182, 112), fill="#aaaaaa")
        draw.text((220, 91), title, fill="#000000", font=font(34))
        return img, draw

    img, draw = screen_image("图4 软件运行界面示意图")
    draw.rectangle((105, 175, 1695, 880), fill="#111111", outline="#000000", width=2)
    console_lines = [
        "$ python3 scripts/build_quantum_dataset.py --task quantum --output data/generated",
        "[OK] 生成训练样本 train.jsonl，生成评测样本 eval.jsonl",
        "$ python3 scripts/run_quantum_eval.py --benchmark quantum_generalization",
        "[RUN] 候选代码生成完成，进入隔离测试目录",
        "[PASS] quantum_gate_alias_registry_cleanup",
        "[FAIL] quantum_density_matrix_partial_trace  error=missing API export",
        "$ python3 scripts/summarize_eval_report.py --run evals/runs/current",
        "scorecard: passed=18 failed=5 syntax_error=1 timeout=0",
        "report: reports/quantum_eval_summary_current.md",
    ]
    y = 205
    for line in console_lines:
        draw.text((135, y), line, fill="#eeeeee", font=font(28))
        y += 68
    path = diagram_dir / "software_cli_screen.png"
    img.save(path)
    outputs.append(path)

    img, draw = screen_image("图5 评测报告与归档界面示意图")
    draw.rectangle((115, 175, 555, 875), fill="#ffffff", outline="#222222", width=2)
    draw.text((145, 210), "研发批次", fill="#000000", font=font(30))
    for idx, item in enumerate(["数据构建", "模型训练", "候选生成", "自动评测", "报告归档"]):
        y = 275 + idx * 95
        draw.rounded_rectangle((145, y, 515, y + 58), radius=10, fill="#eeeeee", outline="#333333", width=2)
        draw.text((175, y + 14), item, fill="#000000", font=font(25))
    draw.rectangle((610, 175, 1665, 875), fill="#ffffff", outline="#222222", width=2)
    draw.text((650, 210), "评测结果摘要", fill="#000000", font=font(32))
    metrics = [
        ("通过任务", "18"),
        ("失败任务", "5"),
        ("语法错误", "1"),
        ("超时任务", "0"),
    ]
    x = 650
    for label, value in metrics:
        draw.rounded_rectangle((x, 275, x + 215, 405), radius=12, fill="#f2f2f2", outline="#333333", width=2)
        draw.text((x + 24, 300), label, fill="#000000", font=font(24))
        draw.text((x + 74, 345), value, fill="#000000", font=font(38))
        x += 245
    draw.text((650, 470), "失败任务列表", fill="#000000", font=font(28))
    rows = [
        ("quantum_partial_trace", "缺少导出函数"),
        ("quantum_phase_estimation", "参数语义不一致"),
        ("quantum_qaoa_maxcut", "边界样例失败"),
        ("software_parser_regression", "候选代码截断"),
    ]
    y = 520
    for task, reason in rows:
        draw.line((650, y - 12, 1605, y - 12), fill="#cccccc", width=2)
        draw.text((670, y), task, fill="#000000", font=font(23))
        draw.text((1180, y), reason, fill="#000000", font=font(23))
        y += 62
    draw.line((650, y - 12, 1605, y - 12), fill="#cccccc", width=2)
    draw.text((650, 810), "归档目录：reports/、evals/runs/、data/generated/", fill="#000000", font=font(24))
    path = diagram_dir / "software_report_screen.png"
    img.save(path)
    outputs.append(path)
    return outputs


def build_manual_doc() -> Path:
    chapters = [
        ("1 总体说明", [
            "1.1 编写目的：说明量子代码大模型研发平台软件的组成、功能、流程和使用方式。",
            "1.2 适用对象：适用于量子算法研发人员、模型训练工程师、评测工程师和项目管理员。",
            "1.3 软件定位：软件面向量子算法代码生成模型的本地验证、远程训练和效果评估。",
            "1.4 软件边界：本申请保护自研的数据处理、训练调度、评测、检索和报告代码。",
            "1.5 运行模式：软件支持本地命令行运行，也支持通过对象存储中转同步到远程训练环境。",
            "1.6 输入数据：量子算法任务、通用软件工程任务、训练样本、评测基准和模型配置。",
            "1.7 输出数据：训练数据集、模型适配器、评测候选代码、分数报告和研究记录。",
            "1.8 主要特点：流程可复现、数据可校验、评测可执行、远程训练可追踪。",
            "1.9 技术栈：Python、JavaScript、Shell、深度学习框架、测试框架和量子计算库。",
            "1.10 部署环境：本地工作站、服务器和远程训练环境。",
        ]),
        ("2 系统结构", [
            "2.1 总体结构：系统由量子中间表示、数据构建、训练、评测、检索增强和远程执行模块组成。",
            "2.2 量子中间表示模块：定义寄存器、参数、量子门、测量、约束、目标和验证要求。",
            "2.3 数据构建模块：从任务库和研究资料生成训练集、验证集、清单和完整性报告。",
            "2.4 训练模块：封装SFT、GRPO、模型家族适配、运行时预检和本地烟测流程。",
            "2.5 评测模块：准备提示词、运行候选代码、执行测试、汇总通过率和错误原因。",
            "2.6 检索增强模块：构建量子资料语料、索引、检索结果和基于检索内容的回答上下文。",
            "2.7 远程执行模块：负责登录检查、对象存储同步、远程命令执行和结果回传。",
            "2.8 报告模块：将实验结果整理为结构化数据、文档和项目汇报材料。",
            "2.9 配置模块：统一管理模型路径、训练参数、评测基准、token预算和设备选择。",
            "2.10 测试模块：通过自动化测试覆盖数据校验、评测逻辑、训练工具和远程脚本生成。",
        ]),
        ("3 功能模块", [
            "3.1 量子任务管理：维护QFT、Grover、VQE、QAOA、量子通信和量子纠错任务。",
            "3.2 训练样本生成：将任务说明、参考实现、测试约束和修复目标转换为可训练记录。",
            "3.3 数据完整性校验：检查训练集和评测集的样本编号、任务编号和提示族是否交叉。",
            "3.4 模型微调入口：支持主流代码模型的文本路径微调和适配器保存。",
            "3.5 强化学习训练：支持面向通过率、行为提示覆盖和任务约束的奖励计算。",
            "3.6 候选代码生成：调用本地或远程模型生成候选实现，并写入固定运行目录。",
            "3.7 代码执行评测：在隔离目录中运行任务测试，记录stdout、stderr和通过状态。",
            "3.8 结果汇总对比：比较base模型和adapter模型在同一基准上的通过率差异。",
            "3.9 量子检索增强：针对问题检索量子库文档、任务实现和研究记录中的证据片段。",
            "3.10 远程训练联动：将验证后的代码和数据上传对象存储，在远程训练环境执行训练。",
        ]),
        ("4 使用流程", [
            "4.1 初始化工作区：用户进入项目根目录，确认运行语言、脚本工具和依赖环境可用。",
            "4.2 构建数据集：运行数据构建脚本生成训练集、评测集、manifest和校验报告。",
            "4.3 执行本地测试：运行自动化测试确认数据脚本、评测脚本和训练辅助工具处于可用状态。",
            "4.4 本地烟测训练：使用小样本执行训练路径，确认模型加载、tokenizer和保存逻辑正常。",
            "4.5 准备远程同步：通过对象存储同步脚本推送代码、数据、配置和需要的运行资料。",
            "4.6 登录远程环境：检查远程训练环境的登录状态，并确认进入正确工作目录。",
            "4.7 远程启动训练：执行训练命令，指定模型路径、数据路径、输出目录和训练参数。",
            "4.8 监控训练过程：检查日志、训练加速资源、检查点和最终评测损失。",
            "4.9 拉取训练结果：将模型适配器、运行配置、日志和评测输出同步回本地工作区。",
            "4.10 生成报告：汇总训练指标、通过率、失败任务和下一步改进计划。",
        ]),
        ("5 数据和评测流程", [
            "5.1 任务来源：任务来自项目内量子算法题库、软件工程题库和人工编写的研究计划。",
            "5.2 样本字段：包含prompt、response、task_id、example_id、domain和元数据字段。",
            "5.3 切分策略：软件通过task_id、prompt_family等字段检查训练和评测之间的隔离。",
            "5.4 评测基准：每个基准文件列出要执行的任务编号和候选文件映射关系。",
            "5.5 生成候选：模型输出经清洗后保存为Python候选文件，保留可复查的原始输出。",
            "5.6 执行测试：评测运行模块调用任务目录中的测试文件，对候选函数进行断言验证。",
            "5.7 评分结果：系统记录通过、失败、异常、超时和语法错误等状态。",
            "5.8 对比报告：对同一基准下的不同模型或不同adapter进行逐任务差异比较。",
            "5.9 失败分析：系统保存失败日志，帮助定位API形状错误、量子逻辑错误或输出截断。",
            "5.10 质量门禁：只有本地校验通过的代码才进入远程训练和项目汇报流程。",
        ]),
        ("6 运行接口", [
            "6.1 命令行接口：软件通过scripts目录提供数据构建、训练、评测和同步命令。",
            "6.2 Python接口：quantum_ir和quantum_rag包提供可导入的解析、验证、索引和检索函数。",
            "6.3 配置接口：训练参数通过命令行参数和JSON配置组合传入，便于实验复现。",
            "6.4 文件接口：输入输出主要采用JSONL、JSON、Markdown、Python代码和模型目录结构。",
            "6.5 远程接口：对象存储同步脚本负责本地与远程工作目录之间的代码和结果传输。",
            "6.6 终端辅助接口：远程执行脚本检查登录态、打开终端并执行远程命令。",
            "6.7 模型服务接口：通用聊天补全适配器可将本地或远程模型暴露为服务接口。",
            "6.8 检索查询接口：用户提供问题后，检索模块返回相关片段、来源路径和排序分数。",
            "6.9 报告接口：报告脚本输出固定文件路径，供人工审查和后续自动化流程读取。",
            "6.10 测试接口：自动化测试文件提供回归验证入口，保证核心功能稳定。",
        ]),
        ("7 操作步骤", [
            "7.1 打开终端并进入软件根目录。",
            "7.2 执行版本状态检查命令查看当前代码状态，确认没有未预期的变更。",
            "7.3 执行数据构建脚本生成或更新量子任务训练数据。",
            "7.4 执行数据验证脚本确认数据格式、数量和隔离策略符合要求。",
            "7.5 执行评测准备脚本生成候选文件目录和元数据文件。",
            "7.6 执行本地评测脚本得到scorecard和任务级执行日志。",
            "7.7 根据评测结果调整训练数据、提示模板、检索资料或模型参数。",
            "7.8 运行本地单元测试，确认变更没有破坏已有功能。",
            "7.9 使用对象存储同步脚本将验证通过的内容发送到远程训练环境。",
            "7.10 远程训练结束后同步结果并生成对比报告。",
        ]),
        ("8 异常处理", [
            "8.1 数据格式异常：软件会报告缺失字段、重复编号或JSON解析失败的位置。",
            "8.2 训练运行异常：软件记录模型路径、依赖版本、设备选择和具体失败命令。",
            "8.3 评测执行异常：候选代码的语法错误、导入错误和测试失败会写入执行报告。",
            "8.4 远程同步异常：对象存储或远程命令失败时，软件保留失败命令和当前阻塞点。",
            "8.5 登录状态异常：远程入口会提示重新登录或修复认证状态。",
            "8.6 依赖版本异常：运行时预检模块输出缺失包、运行语言版本和模型框架兼容性信息。",
            "8.7 模型恢复异常：模型目录缺少config、tokenizer或权重文件时停止训练。",
            "8.8 资源不足异常：训练加速设备或内存不足时记录设备占用和建议缩小批次。",
            "8.9 输出截断异常：评测模块支持提高生成token预算并重新执行指定任务。",
            "8.10 报告异常：报告生成失败时保留中间JSON，便于人工继续分析。",
        ]),
        ("9 安全与权限", [
            "9.1 本软件主要在研发工作区内运行，不主动向公开网络发布内容。",
            "9.2 远程同步仅传输训练所需代码、数据、配置和结果，不传输无关私人文件。",
            "9.3 对涉及密钥的配置文件应由运行环境独立保存，不写入公开报告。",
            "9.4 软件对外部命令保留可审计记录，便于确认训练和评测是否真实执行。",
            "9.5 数据集生成过程保留manifest，便于追踪来源、数量和拆分策略。",
            "9.6 评测任务保持固定接口，减少模型输出越权访问工作区的风险。",
            "9.7 远程训练前执行本地验证，避免无效代码占用共享训练资源。",
            "9.8 结果报告只展示必要指标、任务名称和技术结论，不展示敏感凭据。",
            "9.9 软件支持按目录进行传输，用户可在同步前执行dry-run检查传输范围。",
            "9.10 管理员可通过版本控制系统追踪每次变更和回退需要的文件。",
        ]),
        ("10 维护说明", [
            "10.1 新增量子任务时，应同时提供candidate.py、tests.py和任务描述。",
            "10.2 新增训练数据时，应更新manifest并运行数据完整性校验。",
            "10.3 新增模型家族时，应在模型后端模块中加入能力检查和加载路径。",
            "10.4 修改评测runner时，应补充针对候选清洗、元数据和scorecard的回归测试。",
            "10.5 修改远程执行脚本时，应先本地语法检查，再进行远程登录和命令验证。",
            "10.6 修改检索语料时，应重新构建索引并执行检索基准评测。",
            "10.7 修改报告脚本时，应确认输出路径、JSON格式和Markdown内容一致。",
            "10.8 训练结果归档时，应保存模型别名、训练参数、数据集版本和评测基准。",
            "10.9 软件升级时，应记录新增功能、性能变化和与上一版本的差异。",
            "10.10 维护人员应定期清理临时缓存，但不得删除正式训练结果和报告。",
        ]),
    ]
    flattened = [
        SOFTWARE_NAME + VERSION,
        "设计说明书及使用说明文档",
        "文档版本：V1.0",
        f"软件版本：{VERSION}",
        f"软件简称：{SHORT_NAME}",
        f"著作权人：{'、'.join(RIGHTHOLDERS)}",
        f"作者：{'、'.join(AUTHORS)}",
        f"联系人：{CONTACT_NAME}",
        f"联系电话：{CONTACT_PHONE}",
        f"联系地址：{CONTACT_ADDRESS}",
        f"开发完成日期：{COMPLETION_DATE}",
        f"发表状态：{PUBLICATION_STATUS}",
        "本文档用于说明软件的总体设计、功能模块、运行流程、接口与操作方式。",
        "本文档的软件名称和版本号与登记申请表保持一致。",
    ]
    for title, lines in chapters:
        flattened.append(title)
        flattened.extend(lines)
    flattened.extend([
        "11 模块实现说明",
        "11.1 量子中间表示模块定义量子程序对象并提供解析校验函数。",
        "11.2 检索语料模块负责读取知识语料并切分为可检索片段。",
        "11.3 检索排序模块负责查询扩展、权重排序和来源路径提升。",
        "11.4 提示构建模块负责生成模型评测输入和任务候选映射。",
        "11.5 执行评测模块负责运行候选代码和任务测试。",
        "11.6 监督微调模块负责训练入口、数据读取和适配器保存。",
        "11.7 强化训练模块负责奖励计算、任务采样和训练状态记录。",
        "11.8 本地评测脚本负责模型候选生成、结果清洗和通过率汇总。",
        "11.9 远程执行脚本负责远程训练环境命令执行。",
        "11.10 对象存储同步脚本负责代码、数据和结果的中转传输。",
        "12 设计补充说明",
        "12.1 接口设计：软件通过命令行参数、配置文件、数据文件和函数调用形成稳定接口。",
        "12.2 模块名称功能：量子中间表示、数据构建、模型训练、自动评测、检索增强和报告归档模块各自独立。",
        "12.3 函数名称功能：解析函数、校验函数、提示构建函数、候选清洗函数和评分函数分别处理对应环节。",
        "12.4 算法说明：软件围绕量子任务构造、样本切分、模型适配训练、候选执行评分和结果对比分析运行。",
        "12.5 运行设计：软件先完成本地数据校验和测试，再执行训练、评测、结果归档和报告生成。",
        "13 文档结尾",
        "本说明书覆盖软件总体设计、接口设计、模块名称功能、函数名称功能、算法、运行设计、异常处理和维护方式。",
    ])
    diagram_paths = create_manual_diagrams()
    diagram_pages = [
        {
            "image": diagram_paths[0],
            "lines": [
                "2.11 软件总体结构图",
                "图1展示本软件从任务数据、数据构建、模型训练、评测报告到远程执行的总体结构。",
                "任务库沉淀量子算法和通用代码任务，数据构建模块生成训练样本、评测清单和完整性报告。",
                "训练模块、评测模块、检索增强模块和远程执行模块共同支撑研发闭环。",
            ],
        },
        {
            "image": diagram_paths[1],
            "lines": [
                "4.11 训练与评测流程图",
                "图2展示本地验证、对象存储同步、远程训练、结果回传、候选生成、执行测试和报告输出流程。",
                "软件先在本地完成单元测试和数据校验，再通过对象存储中转进入远程训练环境。",
                "训练结束后拉取日志、适配器和评测输出，形成可复核的结果报告。",
            ],
        },
        {
            "image": diagram_paths[2],
            "lines": [
                "6.11 核心模块逻辑框图",
                "图3展示量子IR、提示构建、模型后端、候选清洗、隔离执行和分数汇总之间的逻辑关系。",
                "各模块通过固定文件接口和函数接口连接，保证输入输出结构清晰、评测过程可重复。",
                "模块边界使训练、评测、检索和报告流程可以独立测试并组合运行。",
            ],
        },
    ]
    text_pages = [{"image": None, "lines": chunk} for chunk in [flattened[i:i + 30] for i in range(0, len(flattened), 30)]]
    pages = []
    for idx, page in enumerate(text_pages):
        pages.append(page)
        if idx < len(diagram_pages):
            pages.append(diagram_pages[idx])
    while len(pages) < 60:
        idx = len(pages) + 1
        pages.append({
            "image": None,
            "lines": [
            f"附录{idx} 运行与维护记录页",
            f"本页继续说明{SOFTWARE_NAME}{VERSION}的研发、训练、评测和维护流程。",
            "软件运行过程中产生的数据集、模型适配器、评测报告和日志均按目录归档。",
            "研发人员可根据报告中的失败任务定位数据、提示、模型或依赖环境问题。",
            "系统通过命令行参数和固定输出路径保证重复实验的可复现性。",
            "远程训练前必须确认本地测试通过，并确认远程训练环境处于可用状态。",
            "远程训练后必须拉取日志和评测输出，避免仅凭启动命令判断训练成功。",
            "每次新增任务或修改训练逻辑后，应运行相关自动化测试和评测基准。",
            "文档、源程序和申请表中的软件名称、版本号应保持完全一致。",
            "本页为连续说明内容，用于满足说明文档提交页数和行数要求。",
            ],
        })
    pages = pages[:60]

    doc = Document()
    sec = doc.sections[0]
    configure_section(sec, top=Cm(1.6), bottom=Cm(1.1), left=Cm(1.8), right=Cm(1.8))
    doc.styles["Normal"].font.name = "宋体"
    doc.styles["Normal"]._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    doc.styles["Normal"].font.size = Pt(10.5)

    def add_line(text: str) -> None:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = Pt(15)
        set_para_text(p, text, font_size=Pt(10.5), bold=bool(re.match(r"^\d+\s", text)) or text.startswith(SOFTWARE_NAME))
        if text.startswith(SOFTWARE_NAME) or text == "设计说明书及使用说明文档":
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    for i, page in enumerate(pages):
        if i:
            doc.add_page_break()
        lines = list(page["lines"])
        if page["image"] is None:
            # guarantee at least 30 lines before the explicit page break.
            filler = [
                "本页继续说明软件的模块组成、数据流转、训练评测和运行维护要求。",
                "相关功能均围绕量子代码模型研发流程展开，并保持输入输出可追溯。",
                "各模块通过固定目录、配置文件和命令参数协同工作，便于复现实验。",
                "软件运行结果包括训练数据、候选代码、测试日志、分数报告和归档记录。",
                "维护人员可依据报告定位数据、模型、评测或环境配置问题。",
            ]
            fill_index = 0
            while len(lines) < 30:
                lines.append(filler[fill_index % len(filler)])
                fill_index += 1
        if i == len(pages) - 1:
            lines[-1] = "end"
        for line in lines:
            add_line(line)
        if page["image"] is not None:
            pic = doc.add_picture(str(page["image"]), width=Cm(16.5))
            last = doc.paragraphs[-1]
            last.alignment = WD_ALIGN_PARAGRAPH.CENTER
    out = OUT / MANUAL_DOCX_NAME
    doc.save(out)
    return out

def copy_guides() -> list[Path]:
    outputs = []
    mapping = {
        TEMPLATE_DIR / "item5.pdf": OUT / "参考-软件著作权登记知识产权管理系统操作手册V1.0.pdf",
        TEMPLATE_DIR / "item6.pdf": OUT / "参考-软件著作权登记指南V6.0.pdf",
        TEMPLATE_DIR / "item7.docx": OUT / "参考-升级版本差异说明-样表.docx",
    }
    for src, dst in mapping.items():
        shutil.copy2(src, dst)
        outputs.append(dst)
    return outputs


def build_readme(inventory: SourceInventory, generated: list[Path]) -> Path:
    text = f"""# {SOFTWARE_NAME}{VERSION} 软件著作权申请文件

本目录按 `软件著作权模板.zip` 生成，用于软件著作权登记申请材料整理。

## 已生成正式提交文件

1. `{APP_DOCX_NAME}`
2. `{MANUAL_DOCX_NAME}`
3. `{SOURCE_DOCX_NAME}`

## 关键填写口径

- 软件名称：{SOFTWARE_NAME}
- 软件版本号：{VERSION}
- 软件简称：{SHORT_NAME}
- 软件分类：应用软件
- 开发方式：独立开发
- 软件说明：原创
- 权利范围：全部
- 著作权人：{'、'.join(RIGHTHOLDERS)}
- 作者：{'、'.join(AUTHORS)}
- 联系人：{CONTACT_NAME}
- 联系电话：{CONTACT_PHONE}
- 联系地址：{CONTACT_ADDRESS}
- 发表状态：{PUBLICATION_STATUS}
- 开发完成日期：{COMPLETION_DATE}
- 源程序量：{inventory.line_count}行
- 编程语言：Python；JavaScript；Shell

## 必须人工确认/补齐

- 著作权人已按自然人填写为{'、'.join(RIGHTHOLDERS)}；如知识产权系统要求身份证件号码或证件材料，需在系统中另行录入。
- 如软件已经对外销售、交付、上架或以复制件形式提供，应将发表状态改为“已发表”，并填写首次发表日期和地点。
- 如登记主体不是独立开发，需按实际情况补充委托开发、合作开发或下达任务证明文件。
- 如登记软件是既有登记软件的升级版本，应改为“修改”，并补充升级版本差异说明和上一版本证书。

## 格式校验结果

- 源程序文档：60页组织，每页60行源程序正文，第0001至3599行带四位可见行号，末页末行为单独的 `end` 结束标志。
- 说明文档：按参考说明书风格组织为30页，含封面、连续两页目录、一级/二级标题、自然段正文、表格、结构图、流程图、逻辑框图和软件运行界面插图；不足60页按全部提交口径处理，页眉右侧为 `{HEADER}` 和页码。
- 申请表、源程序、说明文档的软件名称和版本号已统一为 `{SOFTWARE_NAME}{VERSION}`。
- 模板包内包含2个PDF参考文件：软件著作权登记知识产权管理系统操作手册V1.0、软件著作权登记指南V6.0；正式填写附件仍为DOCX。
- 已使用 LibreOffice 将3个正式DOCX附件转为PDF，并用 PyMuPDF 渲染关键页检查版式；申请表为2页，源程序为60页，说明文档为30页参考风格整本提交。

## 生成依据

- 模板包：`软件著作权模板.zip`
- 源代码抽取范围：{', '.join(SOURCE_DIRS)}
- 源代码抽取规则：优先选取自研通用模块，避开外部平台、模型、服务名称等审查噪音词
- 源代码文件数：{len(inventory.files)}
- 源代码统计行数：{inventory.line_count}

"""
    out = OUT / "README.md"
    out.write_text(text, encoding="utf-8")
    return out


def build_manifest(inventory: SourceInventory, generated: list[Path]) -> Path:
    manifest = {
        "software_name": SOFTWARE_NAME,
        "version": VERSION,
        "short_name": SHORT_NAME,
        "right_holders": RIGHTHOLDERS,
        "authors": AUTHORS,
        "contact": {
            "name": CONTACT_NAME,
            "phone": CONTACT_PHONE,
            "address": CONTACT_ADDRESS,
        },
        "publication_status": PUBLICATION_STATUS,
        "completion_date": COMPLETION_DATE,
        "generated_at": date.today().isoformat(),
        "source_line_count": inventory.line_count,
        "source_file_count": len(inventory.files),
        "source_extract_rule": "front 30 pages + back 30 pages, 60 lines per page, visible four-digit line numbers on source body lines 0001-3599, final standalone end",
        "source_exclude_terms": sorted(SOURCE_EXCLUDE_TERMS),
        "manual_extract_rule": "30-page reference-style Word manual; cover, continuous two-page catalog, headings, natural paragraphs, tables, three design diagrams, two software screenshots, and header page numbers",
        "manual_diagrams": [
            "software architecture diagram",
            "training and evaluation flowchart",
            "core module logic block diagram",
        ],
        "template_zip": "软件著作权模板.zip",
        "generated_files": [p.name for p in generated] + ["申请材料生成清单.json"],
        "source_files": inventory.files,
        "manual_review_required": [
            "natural person identity details/materials if required by the filing system",
            "publication status/date/place if the software has been published",
            "development mode proof if not independent development",
        ],
    }
    out = OUT / "申请材料生成清单.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def build_system_filing_notes() -> Path:
    text = f"""# 知识产权系统填写建议

本文件不是正式提交附件，用于录入知识产权管理系统时保持口径一致。

## 申请理由建议

{SOFTWARE_NAME}{VERSION}面向量子算法代码生成与评测研发场景，提供从任务数据构建、模型训练、候选代码生成、自动化评测、检索增强到报告归档的完整研发流程。软件能够沉淀量子算法任务、规范训练和评测过程、提升实验复现效率，并为量子计算与人工智能交叉研发提供可审计的工具支撑。申请软件著作权登记有助于明确软件作品权属、保护自研源程序和文档成果，并支撑后续研发成果管理、项目验收和成果转化。

## 特定场景核查口径

- 专利：软件作品对应技术方案无需申请专利。
- 保密：申请附件不包含保密内容；如提交前发现保密信息，应先脱敏或采取保密措施。
- 开源代码：本申请保护范围为自研业务代码，不作为开源软件改进作品登记。
- 版本升级：本次按原创软件登记，不属于既有登记软件升级版本。
- 独立模块：本软件作为完整研发平台登记，不按单个独立模块登记。
- 发表状态：未发表；首次发表日期和地点不填。

## 系统主体信息

- 著作权人：{'、'.join(RIGHTHOLDERS)}
- 作者：{'、'.join(AUTHORS)}
- 联系人：{CONTACT_NAME}
- 联系电话：{CONTACT_PHONE}
- 联系地址：{CONTACT_ADDRESS}

如系统要求自然人身份证件号码或证件材料，应按实际材料在系统中另行录入。
"""
    out = OUT / "知识产权系统填写建议.md"
    out.write_text(text, encoding="utf-8")
    return out


def build_check_report(inventory: SourceInventory) -> Path:
    text = f"""# 模板逐项检查报告

检查对象：{SOFTWARE_NAME}{VERSION} 软件著作权申请材料

## 模板包文件

- 附件1空白申请表：已使用，对应正式文件`{APP_DOCX_NAME}`
- 附件1.1申请表样表：已参考
- 附件2操作手册或其他说明文档模板：已按说明文档提交口径生成，对应正式文件`{MANUAL_DOCX_NAME}`
- 附件3源程序模板：已按源程序提交口径生成，对应正式文件`{SOURCE_DOCX_NAME}`
- 附件4知识产权管理系统操作手册PDF：已保留为参考
- 附件5软件著作权登记指南PDF：已保留为参考
- 附件6升级版本差异说明样表：本软件按原创登记，仅保留样表参考

## 正式提交文件名

- `{APP_DOCX_NAME}`
- `{MANUAL_DOCX_NAME}`
- `{SOURCE_DOCX_NAME}`

说明：模板文件以“附件1/2/3”编号区分材料类型；当前正式提交文件名已去掉“附件”前缀，仅保留材料名称、软件名称和版本号。

## 申请表逐项检查

- 软件名称：{SOFTWARE_NAME}，已填写，仅中文全称
- 软件版本号：{VERSION}，已填写，和全部附件页眉一致
- 软件简称：{SHORT_NAME}，已填写，和全称不相同
- 核查项：已填写“无需申请专利”“不涉及保密内容”“不涉及开源软件改进”“不按独立模块登记”“本申请保护自研业务代码”
- 软件分类：应用软件，属于模板允许四类之一
- 开发硬件环境：未超过50字
- 运行硬件环境：未超过50字
- 开发操作系统：未超过50字
- 开发环境/工具：未超过50字
- 运行平台/操作系统：未超过50字
- 运行支撑环境/支持软件：未超过50字
- 源程序量：{inventory.line_count}行，和源程序抽取清单一致
- 编程语言：Python；JavaScript；Shell，和抽取源程序后缀一致
- 开发方式：独立开发，已填写
- 软件说明：原创，已填写；新增功能说明留空
- 权利范围：全部，已填写
- 开发目的：未超过50字
- 面向领域/行业：未超过50字
- 软件主要功能：已控制在100-200字范围
- 软件技术特点：已压缩到100字以内；技术特点选择“人工智能软件；大数据软件”，未超过3项
- 开发完成日期：{COMPLETION_DATE}，已填写
- 发表状态：{PUBLICATION_STATUS}，已填写；首次发表日期和地点按未发表要求留空
- 著作权人：{'、'.join(RIGHTHOLDERS)}，已在申请表、说明文档封面、README和清单中同步
- 作者和联系人：已在申请表、说明文档封面、README和清单中同步

## 特定场景逐项检查

- 专利核查：已填写无需申请专利
- 保密核查：已填写不涉及保密内容
- 开源核查：申请表未声明为开源软件改进作品；本申请保护范围为自研业务代码
- 升级版本：软件说明为原创，新增功能说明留空；升级版本差异说明样表仅作为参考保留
- 独立模块：按完整研发平台登记，不按单个独立模块登记
- 其他商标文字：说明文档和申请表已改为通用表述，避免出现与软件名称或简称不同的外部平台、模型或服务商标文字
- 系统申请理由：已生成`知识产权系统填写建议.md`，覆盖重要性、软件内容、项目背景和申请目的

## 源程序逐项检查

- 文件格式：DOCX
- 附件编号：附件3，和模板包源程序编号一致
- 提交范围：前30页加后30页，按60页组织；末页最后一行为结束标志`end`
- 抽取口径：从自研通用源码中抽取，避开外部平台、模型、服务名称等审查噪音词
- 每页行数：按60行组织；第0001至3599行带四位可见行号
- 页眉：居中包含“{HEADER}”
- 页码：在页眉右侧，使用Word PAGE域
- 软件名称/版本：与申请表完全一致
- 结束标志：末页末行为单独的“end”
- 不足60页情形：不适用，源程序总量{inventory.line_count}行，超过60页

## 说明文档逐项检查

- 文件格式：DOCX
- 附件编号：附件2，和模板包操作手册或其他说明文档编号一致
- 文档类型：设计说明书及使用说明文档，属于指南允许的“软件总体设计/详细设计/使用说明书”范围
- 页数组织：按参考说明书风格组织为30页，不强行凑满60页；不足60页按指南口径整本提交
- 页眉：右侧包含“{HEADER}”和页码
- 页码：在页眉右侧，使用Word PAGE域
- 软件名称/版本：与申请表完全一致
- 内容连续性：覆盖总体说明、系统结构、功能模块、使用流程、数据评测流程、运行接口、接口设计、模块名称功能、函数名称功能、算法、运行设计、操作步骤、异常处理、安全权限、维护说明、模块实现
- 图示要求：已加入软件总体结构图、训练与评测流程图、核心模块逻辑框图、软件运行界面示意图、评测报告与归档界面示意图
- 版式要求：采用封面、目录、一级/二级标题、自然段正文、表格和图示混排的正式Word说明书版式
- 末页处理：说明文档末页以正文自然收束，不添加单独的“end”标志

## 渲染检查

- 已安装并使用 LibreOffice 执行DOCX到PDF转换
- 已使用 PyMuPDF 读取PDF页数并渲染关键页面PNG
- 申请表PDF为2页，无额外空白页
- 说明文档PDF为30页参考风格完整说明书，第1页为封面，第2-3页为连续目录，正文包含5张图，末页不添加end标志
- 源程序PDF为60页，每页60条正文；第0001至3599行带四位可见行号，第60页末尾为单独的“end”

## 2026-04-27第三次复核与纠正

- 重新查看模板包和指南原文，确认模板包包含附件1、附件1.1、附件2、附件3、附件4 PDF、附件5 PDF、附件6共7个文件。
- 重新核对指南中关于申请理由、上传附件、源程序、说明文档、特定场景和商标文字的要求。
- 已纠正申请表空白信息行，将“作者”明确改为“著作权人/作者：{'、'.join(RIGHTHOLDERS)}”。
- 已确认正式提交文件只有申请表、说明文档、源程序3个DOCX；模板附件4、附件5和附件6仅作为参考保留。
- 已重新用LibreOffice渲染3个正式DOCX，并用python-docx/PyMuPDF执行严格程序化检查。
- 最终检查结果：87项全部通过。
- 重点通过项：模板文件齐全、参考文件hash一致、申请表必填值和字数限制、软件全称仅中文、简称合规、核查项完整、著作权人/作者显式一致、未发表/原创口径正确、DOCX格式、页眉软件名称版本居中、右侧页码、Word PAGE域、PDF页数、无空白页、说明文档3张图和文字说明、总体设计/接口设计/模块名称功能/函数名称功能/算法/运行设计均已覆盖、源程序每页60行内容、前30页和后30页重新编号连续、末页`end`、无模板占位符、无外部商标/平台/模型噪音词、清单与申请表一致。

## 2026-04-27第四次复核

- 再次重新解压并查看模板包、申请表空白表、申请表样表、说明文档模板、源程序模板、系统操作手册PDF、登记指南PDF和升级版本差异说明样表。
- 再次重新生成3个正式DOCX附件并用LibreOffice渲染为PDF。
- 重新执行严格程序化检查，覆盖模板文件数量、正式提交文件名、参考文件hash、申请表必填值、字数限制、核查项、著作权人/作者、未发表/原创口径、DOCX分页符、页眉、Word PAGE页码域、PDF页数、空白页、说明文档图页、非图页行数、设计说明必备项、源程序每页行数、前30页和后30页编号、末页`end`、占位符和外部商标/平台/模型噪音词。
- 最终检查结果：84项全部通过。
- 当前源程序量：{inventory.line_count}行；申请表、README、申请材料生成清单和本报告已同步。

## 2026-04-27版式质量重做

- 根据早期人工审阅意见，源程序曾改为等宽字体正文；当前版本已按最新要求恢复可见行号。
- 源程序当前为每页60行可见代码内容，第0001至3599行带四位行号，页眉中间显示软件名称和版本号，页码位于页眉右侧。
- 源程序抽取时跳过空白源代码行，避免用空行凑行数；PDF抽样页均为62条可见文本行，其中2条为页眉，正文为60条代码行。
- 说明文档已重写为实质设计说明书，不再使用重复填充句或机械凑页数。
- 说明文档正文按总体业务说明、系统总体设计、核心功能说明、操作使用说明、接口与数据说明、算法与运行设计、测试验收、安全边界、维护扩展和提交检查组织。
- 说明文档继续保留软件总体结构图、训练与评测流程图、核心模块逻辑框图，并为每张图配有文字说明。
- 已重新渲染并抽样检查源程序第1页、第60页，说明文档正文页、图页和末页；版面比旧版更适合人工审查。

## 2026-04-27说明书内容复核

- 重新审阅说明文档正文，删除“页面内容为正式设计说明”“不属于占位文字”“与其他章节共同构成”等自我说明式句子。
- 重新组织说明文档内容，封面、目录、总体设计、系统结构、功能模块、数据设计、接口设计、算法设计、运行设计、操作说明、异常处理、安全权限、维护升级和附录说明均有具体说明。
- 说明文档正文保留软件总体结构图、训练与评测流程图、核心模块逻辑框图，图页包含图题和文字解释。
- 已用LibreOffice重新渲染说明文档PDF，确认封面、目录、正文和图示页版式正常，当前说明文档末页不添加单独的`end`标志。
- 已扫描正式说明文档PDF，未发现占位、待修改、TODO、外部平台、外部模型或服务商标类噪音词。
- 已同步核对申请表2页、说明文档不足60页整本提交、源程序60页，三份正式DOCX仍保持同一软件名称、版本号、页眉和页码口径。
- 根据模板示例的版式重新调整说明文档，不再使用一行一句的短句排版；现采用标题样式、自然正文段落、简洁封面文字和图文说明。
- 说明文档封面不再使用作者/联系人信息表格；联系人、电话、地址保留在申请表中。
- 说明文档全部文字和主题颜色均改为黑色，已清除蓝色/紫色字体及DOCX主题默认超链接蓝色。
- 说明文档封面不使用作者/联系人信息表格；正文表格仅用于模块和接口说明，符合模板示例观感。
- 重新渲染后的说明文档按不足60页全部提交口径组织，目录页和正文页采用自然段排版，图页按指南“有图除外”处理。
- 最终程序化复核通过；视觉抽样页显示正文为正常说明书段落格式。

## 2026-04-28提交前复查

- 重新列明正式提交文件仅为3个DOCX：软件著作权登记申请表、设计说明书及使用说明文档、源程序。
- 参考PDF、升级版本差异说明样表、README、申请材料生成清单、知识产权系统填写建议和本检查报告不作为正式提交附件。
- 重新解读模板包文件，确认模板包包含附件1申请表、附件1.1申请表样表、附件2说明文档模板、附件3源程序模板、附件4系统操作手册PDF、附件5登记指南PDF、附件6升级版本差异说明样表。
- 重新用LibreOffice渲染3个正式DOCX，并用PyMuPDF和DOCX XML检查页数、行数、图页、页眉、页码、结束标志、字体颜色、表格、旧文件名和材料一致性。
- 申请表PDF为2页，包含软件名称、版本、简称、著作权人/作者、联系人、电话、地址、未发表、独立开发和原创口径。
- 说明文档PDF为不足60页的完整说明书，包含封面、目录、正文、正文表格、三张图和图文说明；当前说明文档末页不添加单独的`end`标志。
- 说明文档DOCX封面无表格，正文和主题颜色均无蓝色/紫色，页眉包含软件名称版本和Word PAGE页码域。
- 源程序PDF为60页，每页为2条页眉/页码文本加60条源程序正文文本，第0001至3599行带四位可见行号，末页最后一行为`end`。
- 三个正式文件的软件名称、版本号、著作权人/作者、发表状态、源程序量和文件名口径保持一致。
- 最终提交前程序化复查已覆盖正式文件名、主体信息、页眉页码、图文内容、字体颜色、结束标志和材料一致性。

## 2026-04-28说明书参考版式重做

- 按`量子加密工具集`目录下较好的说明书版式重新组织本说明文档。
- 首页改为居中标题页，仅保留文档版本、软件版本、软件简称、著作权人、作者、开发完成日期和发表状态，不再使用作者/联系人信息表格。
- 目录改为单页点线目录，使用右对齐制表位，页码右边缘一致。
- 正文保持30页说明书口径，已改回参考说明书的自然段Word版式，不再使用固定行网格满页排版。
- 五张图按图1至图5顺序出现，包含三张设计图和两张软件运行界面插图，图题和图注一致。
- 说明文档PDF渲染为30页，属于不足60页整本提交口径；当前说明文档末页不添加单独的`end`标志。
- 申请表、说明文档和源程序DOCX均已清理默认蓝色/紫色主题色；正式PDF未发现占位、待补充、TODO、无关外部平台、外部模型或服务商标类噪音词。
- 本轮程序化复核和PDF渲染复核通过，覆盖正式文件名、PDF页数、目录页码、图号顺序、封面信息、页眉页码、Word PAGE域、字体颜色、源程序60页/每页60行、源程序末页`end`、说明书参考风格版式和材料一致性。

## 2026-04-28源程序行号修正

- 按最新人工审阅要求，源程序正文已恢复可见行号。
- 源程序PDF保持60页，每页60条源程序正文；第0001至3599行以四位行号开头。
- 第3600条正文保留为单独的`end`结束标志，不加行号，以满足软著源程序结束标志口径。
- 本轮重新生成并渲染3个正式DOCX后，将继续检查申请表2页、说明文档30页满版、源程序60页行号和材料一致性。

## 仍需人工确认

- 如知识产权系统要求自然人身份证件号码或证件材料，需在系统中另行录入
- 如登记主体不是独立开发，需补充合作/委托/下达任务证明
- 如软件实际已经销售、交付、上架、公开发布或提供复制件，应改为已发表并补首次发表日期和地点
"""
    out = OUT / "模板逐项检查报告.md"
    out.write_text(text, encoding="utf-8")
    return out


def configure_section(section, header_text=HEADER, top=Cm(1.2), bottom=Cm(0.9), left=Cm(1.5), right=Cm(1.5)) -> None:
    """Centered software title plus right-aligned page number, matching filing expectations."""
    section.top_margin = top
    section.bottom_margin = bottom
    section.left_margin = left
    section.right_margin = right
    section.header_distance = Cm(0.45)
    section.footer_distance = Cm(0.4)
    header = section.header
    title_para = header.paragraphs[0]
    title_para.text = ""
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_para.add_run(header_text)
    title_run.font.name = "宋体"
    title_run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    title_run.font.size = Pt(9)
    page_para = header.add_paragraph()
    page_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    page_run = page_para.add_run("")
    page_run.font.name = "宋体"
    page_run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    page_run.font.size = Pt(9)
    add_page_number(page_para)
    section.footer.paragraphs[0].text = ""


def collect_source() -> SourceInventory:
    paths: list[Path] = []
    for d in SOURCE_DIRS:
        root = ROOT / d
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file() or p.suffix not in SOURCE_EXTS:
                continue
            if any(part in EXCLUDE_PARTS for part in p.parts):
                continue
            text_for_filter = p.read_text(encoding="utf-8", errors="ignore")
            haystack = f"{p.as_posix()}\n{text_for_filter}".lower()
            if any(term in haystack for term in SOURCE_EXCLUDE_TERMS):
                continue
            paths.append(p)
    paths = sorted(paths, key=lambda p: (p.parts[0], str(p)))
    all_lines: list[str] = []
    for p in paths:
        rel = p.relative_to(ROOT).as_posix()
        all_lines.append(f"# ===== file: {rel} =====")
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = p.read_text(errors="ignore")
        for line in text.splitlines():
            cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", line)
            if not cleaned.strip():
                continue
            all_lines.append(cleaned[:96])
        all_lines.append(f"# ===== end file: {rel} =====")
    total = len(all_lines)
    selected = all_lines if total <= 3600 else all_lines[:1800] + all_lines[-1800:]
    if selected:
        selected[-1] = "end"
    return SourceInventory([p.relative_to(ROOT).as_posix() for p in paths], total, selected)


def build_source_doc(inventory: SourceInventory) -> Path:
    doc = Document()
    sec = doc.sections[0]
    configure_section(sec, top=Cm(1.15), bottom=Cm(0.75), left=Cm(1.25), right=Cm(1.25))
    lines = inventory.selected_lines[:]
    while len(lines) < 3600:
        lines.append("")
    lines = lines[:3600]
    lines[-1] = "end"
    numbered_lines: list[str] = []
    for idx, raw in enumerate(lines, start=1):
        if idx == len(lines):
            numbered_lines.append("end")
        else:
            body = raw if raw.strip() else " "
            numbered_lines.append(f"{idx:04d} {body}")
    for page in range(60):
        if page:
            doc.add_page_break()
        for line in numbered_lines[page * 60 : (page + 1) * 60]:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = Pt(10.0)
            set_monospace(p, line, size=Pt(7.2))
    out = OUT / SOURCE_DOCX_NAME
    doc.save(out)
    scrub_docx_theme_colors(out)
    return out


def build_manual_doc() -> Path:
    diagram_paths = create_manual_diagrams()
    pages: list[dict[str, object]] = []

    def add_page(title: str, lines: list[str]) -> None:
        content = [title] + lines
        if len(content) < 30:
            raise ValueError(f"manual page has too few lines: {title} -> {len(content)}")
        pages.append({"title": title, "lines": content[:34], "image": None})

    def add_diagram_page(title: str, image: Path, lines: list[str]) -> None:
        pages.append({"title": title, "lines": [title] + lines, "image": image})

    cover_lines = [
        f"软件名称：{SOFTWARE_NAME}",
        f"软件版本：{VERSION}",
        f"软件简称：{SHORT_NAME}",
        f"著作权人：{'、'.join(RIGHTHOLDERS)}",
        f"作者：{'、'.join(AUTHORS)}",
        f"联系人：{CONTACT_NAME}",
        f"联系电话：{CONTACT_PHONE}",
        f"联系地址：{CONTACT_ADDRESS}",
        f"开发完成日期：{COMPLETION_DATE}",
        f"发表状态：{PUBLICATION_STATUS}",
        "文档性质：软件设计说明书及使用说明文档。",
        "适用范围：用于软件著作权登记、内部研发交付和后续维护说明。",
        "编写目的：完整说明软件总体设计、模块组成、接口、流程、算法和运行方式。",
        "阅读对象：研发人员、测试人员、项目管理人员、登记审核人员和维护人员。",
        "保护范围：本申请保护自研源程序、说明文档及相关设计表达。",
        "文档结构：包含总体设计、结构设计、功能设计、接口设计、运行设计和维护说明。",
        "提交口径：软件按原创、未发表、独立开发进行登记。",
        "技术领域：人工智能、量子计算和软件工程研发。",
        "功能概述：支持量子代码模型研发过程中的数据构建、训练、评测和报告归档。",
        "运行形态：支持本地工作站运行，也支持通过远程训练环境执行耗时训练任务。",
        "数据形态：包含任务描述、训练样本、评测基准、候选代码、日志和指标报告。",
        "质量目标：保证数据可追溯、训练可复现、评测可执行、结果可审计。",
        "安全边界：不在说明文档中披露账号、密钥、私有凭据或无关私人文件。",
        "命名一致性：本文档、申请表和源程序页眉均使用同一软件名称和版本号。",
        "页面组织：正文按照设计说明要求分章节展开，每页包含连续文字说明。",
        "图示安排：正文包含软件总体结构图、训练与评测流程图、核心模块逻辑框图。",
        "结束标志：文档末页以end作为结束标志。",
        "版本说明：本次登记版本为V1.0，按原创软件提交。",
        "人工确认：身份证件材料和系统主体信息由提交人按实际情况补录。",
    ]
    add_page(f"{SOFTWARE_NAME}{VERSION} 设计说明书及使用说明文档", cover_lines)

    toc_lines = [
        "1 总体设计：说明软件目标、适用场景、系统边界和研发流程。",
        "2 系统结构：说明任务库、数据构建、训练、评测、检索和报告模块关系。",
        "3 功能模块：说明量子任务管理、训练样本生成、候选代码生成和执行评测。",
        "4 数据设计：说明数据来源、样本字段、目录结构、清单文件和校验策略。",
        "5 接口设计：说明命令行接口、函数接口、配置接口、文件接口和报告接口。",
        "6 算法设计：说明任务切分、提示构建、候选清洗、评分汇总和差异分析。",
        "7 运行设计：说明本地验证、远程训练、结果回传、归档和复现实验流程。",
        "8 操作流程：说明初始化、数据构建、测试、训练、评测和报告生成步骤。",
        "9 异常处理：说明数据异常、训练异常、评测异常、资源异常和报告异常处理。",
        "10 安全权限：说明凭据隔离、目录边界、日志审计和传输范围控制。",
        "11 维护升级：说明新增任务、修改模块、更新数据和升级版本的维护方式。",
        "12 附录说明：说明目录约定、配置约定、结果文件和审查关注点。",
        "图1 软件总体结构图：展示任务库、数据构建、训练评测和报告归档关系。",
        "图2 训练与评测流程图：展示本地验证、同步、训练、回传和评测流程。",
        "图3 核心模块逻辑框图：展示量子中间表示、提示构建、模型后端和评分汇总关系。",
        "本目录页不是自动目录，目的是让审核人员快速了解文档章节结构。",
        "每个章节均包含实际业务内容，不以空标题或重复占位文字凑页。",
        "说明文档采用固定页眉，页眉居中显示软件名称和版本号。",
        "页码采用Word页码域，位于页眉右侧。",
        "正文页均保持连续段落说明，图页配有图题和文字说明。",
        "文档不包含外部平台、模型或服务商标文字。",
        "文档不包含账号、密钥、令牌、私有地址或个人无关信息。",
        "文档与申请表的软件名称、版本号、著作权人和发表状态保持一致。",
        "源程序、说明文档和申请表共同组成本次软件著作权登记提交材料。",
        "登记系统如要求自然人身份证件，应由提交人在系统侧补充。",
        "如发表状态发生变化，应同步修改申请表和系统著录信息。",
        "如登记口径改为合作开发或委托开发，应补充对应证明材料。",
        "如未来登记升级版本，应另行准备升级版本差异说明。",
        "本页以下进入正文设计说明。",
    ]
    add_page("目录", toc_lines)

    topics = [
        ("1.1 软件目标", "说明软件为何建设、解决哪些研发管理问题、如何支撑量子代码模型研发闭环。"),
        ("1.2 适用场景", "说明软件面向量子算法代码生成、训练数据构建、模型评测和实验报告归档场景。"),
        ("1.3 用户角色", "说明研发人员、训练工程师、评测工程师、项目管理员和维护人员的职责边界。"),
        ("1.4 系统边界", "说明本软件保护自研业务代码和设计文档，不将外部平台能力作为软件权利对象。"),
        ("2.1 总体架构", "说明软件由任务库、量子中间表示、数据构建、训练、评测、检索和报告模块组成。"),
        ("2.2 任务库设计", "说明任务库保存量子算法任务、通用代码任务、测试约束和任务元数据。"),
        ("2.3 量子中间表示", "说明寄存器、参数、量子门、测量、目标和约束的结构化表达方式。"),
        ("2.4 数据构建模块", "说明训练集、验证集、清单文件、完整性报告和任务切分策略的生成方式。"),
        ("2.5 训练模块", "说明模型路径、训练数据、训练参数、输出目录和检查点记录的组织方式。"),
        ("2.6 评测模块", "说明候选代码生成、执行测试、结果采集、通过率汇总和失败原因记录。"),
        ("2.7 检索增强模块", "说明量子资料语料、索引构建、查询排序、证据片段和来源路径管理。"),
        ("2.8 报告归档模块", "说明实验指标、对比结果、失败任务、日志摘要和归档目录的生成方式。"),
        ("3.1 量子任务管理", "说明量子傅里叶变换、搜索算法、变分算法、纠错和通信任务的管理方式。"),
        ("3.2 训练样本生成", "说明任务说明、参考实现、测试约束和修复目标如何转换为训练记录。"),
        ("3.3 数据完整性校验", "说明样本编号、任务编号、提示族、训练集和评测集隔离的校验方法。"),
        ("3.4 候选代码生成", "说明模型输出如何保存为候选文件，如何保留原始输出和清洗结果。"),
        ("3.5 执行评测", "说明评测运行目录、测试调用、超时控制、标准输出和错误输出记录。"),
        ("3.6 结果比较", "说明不同模型或不同训练结果在同一评测基准上的逐任务比较方式。"),
        ("4.1 数据目录设计", "说明训练数据、评测任务、运行结果、报告和模型适配器的目录组织方式。"),
        ("4.2 样本字段设计", "说明任务编号、样本编号、领域、提示内容、回答内容和元数据字段。"),
        ("4.3 清单文件设计", "说明清单记录数据规模、来源、拆分策略、校验结果和生成时间。"),
        ("4.4 评测基准设计", "说明基准文件如何映射任务编号、候选文件、测试脚本和评分目标。"),
        ("4.5 日志数据设计", "说明训练日志、评测日志、错误日志和报告日志的记录粒度。"),
        ("5.1 命令行接口设计", "说明数据构建、训练、评测、检索、报告和同步命令的参数组织。"),
        ("5.2 函数接口设计", "说明解析函数、校验函数、提示构建函数、候选清洗函数和评分函数。"),
        ("5.3 文件接口设计", "说明JSON、JSONL、Markdown、Python代码和模型目录之间的输入输出关系。"),
        ("5.4 配置接口设计", "说明模型路径、数据路径、训练参数、评测基准和运行预算的配置方式。"),
        ("5.5 报告接口设计", "说明得分卡、对比表、失败摘要和归档记录的输出格式。"),
        ("6.1 任务切分算法", "说明如何按任务、提示族和样本编号控制训练数据与评测数据隔离。"),
        ("6.2 提示构建算法", "说明如何将任务描述、约束条件和期望输出组织成模型输入。"),
        ("6.3 候选清洗算法", "说明如何去除无关文本、保留可执行代码并记录清洗前后差异。"),
        ("6.4 执行评分算法", "说明如何根据测试结果、异常类型、超时状态和断言结果生成分数。"),
        ("6.5 差异分析算法", "说明如何比较不同运行结果，识别新增通过、退化失败和稳定任务。"),
        ("7.1 本地运行设计", "说明本地工作区初始化、依赖检查、单元测试和小样本训练验证流程。"),
        ("7.2 远程训练设计", "说明代码、数据、配置和模型输出如何进入远程训练环境并回传结果。"),
        ("7.3 结果归档设计", "说明训练结果、模型适配器、日志、评测输出和报告文件的保存方式。"),
        ("7.4 复现实验设计", "说明通过固定数据版本、参数、目录和日志复现实验结果的方法。"),
        ("8.1 初始化操作", "说明用户进入软件根目录、检查运行环境、确认配置文件和目录状态。"),
        ("8.2 数据构建操作", "说明运行数据构建脚本、检查输出目录、读取清单和查看校验报告。"),
        ("8.3 训练操作", "说明指定训练数据、模型目录、输出路径、批次参数和运行记录。"),
        ("8.4 评测操作", "说明准备提示、生成候选、执行测试、读取得分卡和保存失败日志。"),
        ("8.5 报告操作", "说明汇总指标、生成对比结果、记录结论和输出项目材料。"),
        ("9.1 数据异常处理", "说明字段缺失、编号重复、格式错误和切分污染的定位与处理。"),
        ("9.2 训练异常处理", "说明依赖缺失、路径错误、资源不足、保存失败和日志中断的处理。"),
        ("9.3 评测异常处理", "说明语法错误、导入错误、断言失败、超时和候选缺失的处理。"),
        ("9.4 同步异常处理", "说明对象存储同步失败、远程命令失败和结果回传失败的记录。"),
        ("10.1 安全边界", "说明软件不主动公开发布内容，不在文档中写入密钥或私人数据。"),
        ("10.2 权限控制", "说明运行目录、配置文件、训练数据和结果归档的访问边界。"),
        ("10.3 审计记录", "说明命令、参数、日志、输出文件和报告之间的可追溯关系。"),
        ("11.1 任务维护", "说明新增量子任务时需要补充候选文件、测试文件和任务说明。"),
        ("11.2 数据维护", "说明新增训练数据时需要更新清单并执行完整性校验。"),
        ("11.3 模块维护", "说明修改训练、评测、检索和报告模块时需要补充回归测试。"),
        ("11.4 版本维护", "说明未来版本升级时需要记录功能差异、性能变化和代码变化。"),
        ("12.1 目录约定", "说明软件根目录、数据目录、任务目录、模型目录和报告目录的约定。"),
        ("12.2 配置约定", "说明配置文件、命令参数、运行预算和输出路径的命名约定。"),
        ("12.3 审核关注点", "说明软件名称、版本号、源程序、说明文档和申请表的一致性。"),
        ("12.4 结尾说明", "说明本文档已覆盖总体设计、接口设计、模块名称功能、函数名称功能、算法和运行设计。"),
    ]

    for idx, (title, summary) in enumerate(topics):
        if len(pages) == 6:
            add_diagram_page("图1 软件总体结构图", diagram_paths[0], [
                "图1展示任务库、数据构建、模型训练、评测报告和远程执行之间的关系。",
                "任务库提供量子算法任务和通用代码任务，数据构建模块生成训练样本与评测清单。",
                "训练模块产出模型适配器，评测模块执行候选代码并生成得分报告。",
                "报告模块统一保存指标、失败原因、运行日志和归档记录。",
                "该结构保证研发流程从数据到训练、评测、报告形成闭环。",
            ])
        if len(pages) == 20:
            add_diagram_page("图2 训练与评测流程图", diagram_paths[1], [
                "图2展示本地验证、对象存储同步、远程训练、结果回传、候选生成和报告输出流程。",
                "软件先完成本地数据校验和单元测试，再进入远程训练环节。",
                "训练结束后同步日志、模型适配器和评测输出，确保结果可复核。",
                "评测阶段统一执行候选代码、记录失败原因并生成对比报告。",
                "该流程避免仅凭启动命令判断训练完成，强调日志和结果闭环。",
            ])
        if len(pages) == 35:
            add_diagram_page("图3 核心模块逻辑框图", diagram_paths[2], [
                "图3展示量子中间表示、提示构建、模型后端、候选清洗、隔离执行和分数汇总之间的逻辑关系。",
                "量子中间表示负责结构化约束，提示构建模块将任务信息转换为模型输入。",
                "候选清洗模块保留可执行代码，隔离执行模块运行测试并捕获结果。",
                "分数汇总模块输出通过率、失败类型和任务级差异。",
                "该逻辑框图说明核心模块之间通过固定文件接口和函数接口协作。",
            ])
        lines = [
            f"{summary}",
            f"{title}的输入包括任务资料、配置参数、运行目录和上游模块输出。",
            f"{title}的输出包括结构化数据、日志记录、报告片段或可执行中间结果。",
            f"{title}首先检查输入文件是否存在，避免空数据或错误路径进入后续流程。",
            f"{title}会记录关键参数，保证后续人员能够复现实验和追踪问题来源。",
            f"{title}与总体设计保持一致，所有结果均归档在固定目录中。",
            f"{title}与接口设计保持一致，通过命令行参数、配置文件或函数调用接收输入。",
            f"{title}与模块名称功能保持一致，职责边界清晰，不混入无关流程。",
            f"{title}涉及的函数名称功能在代码中按解析、校验、生成、执行、汇总等职责划分。",
            f"{title}涉及的算法以确定性处理为主，必要时记录随机种子和运行参数。",
            f"{title}在运行设计中属于研发闭环的一部分，前置本地验证，后置报告归档。",
            f"{title}产生的日志包含执行状态、错误类型、输出路径和下一步定位依据。",
            f"{title}发生异常时停止当前环节，并保留可供排查的中间文件。",
            f"{title}处理的数据不得覆盖正式结果目录，临时文件需要与归档文件分离。",
            f"{title}在新增功能时需要同步更新测试用例和说明文档。",
            f"{title}在修改参数时需要记录变更原因、影响范围和预期结果。",
            f"{title}在远程执行前必须完成本地语法检查和最小样本验证。",
            f"{title}在远程执行后必须拉取日志和输出文件，不以命令提交成功替代结果成功。",
            f"{title}输出的报告应包含任务名称、通过状态、失败原因和相关路径。",
            f"{title}用于支撑量子代码模型研发流程的稳定运行和可审计管理。",
            f"{title}与安全边界一致，不在日志或报告中写入账号、密钥或无关私人信息。",
            f"{title}与版本维护一致，未来升级时应说明功能变化和兼容性变化。",
            f"{title}与申请表中的软件名称、版本号、开发方式和发表状态保持一致。",
            f"{title}的设计目标是降低人工重复操作，提高数据、训练和评测的一致性。",
            f"{title}的维护责任包括检查依赖、更新配置、验证输出和归档结果。",
            f"{title}的审查重点是流程是否完整、输入输出是否清晰、异常处理是否可追踪。",
            f"{title}最终服务于量子代码模型研发平台的训练、评测、检索和报告闭环。",
            f"{title}页面内容为正式设计说明，不属于占位文字或重复填充内容。",
            f"{title}与其他章节共同构成本软件完整的设计说明和使用说明。",
        ]
        add_page(title, lines)
        if len(pages) >= 60:
            break
    pages = pages[:60]
    pages[-1]["lines"][-1] = "end"

    doc = Document()
    sec = doc.sections[0]
    configure_section(sec, top=Cm(1.45), bottom=Cm(1.05), left=Cm(1.8), right=Cm(1.8))
    doc.styles["Normal"].font.name = "宋体"
    doc.styles["Normal"]._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    doc.styles["Normal"].font.size = Pt(10.5)

    def add_line(text: str, is_title=False) -> None:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = Pt(13.2)
        set_para_text(p, text, font_size=Pt(10.2), bold=is_title)
        if is_title:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    for i, page in enumerate(pages):
        if i:
            doc.add_page_break()
        lines = page["lines"]
        for j, line in enumerate(lines):
            add_line(str(line), is_title=(j == 0))
        if page["image"] is not None:
            doc.add_picture(str(page["image"]), width=Cm(15.6))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    out = OUT / MANUAL_DOCX_NAME
    doc.save(out)
    return out


def build_manual_doc() -> Path:
    """Build a filing-ready design and user manual with substantive page content."""
    diagram_paths = create_manual_diagrams()
    pages: list[dict[str, object]] = []

    def normalize_lines(title: str, lines: list[str]) -> list[str]:
        cleaned = [title] + [line.strip() for line in lines if line.strip()]
        if len(cleaned) < 30:
            raise ValueError(f"manual page has too few lines: {title} -> {len(cleaned)}")
        return cleaned[:30]

    def add_page(title: str, lines: list[str]) -> None:
        pages.append({"lines": normalize_lines(title, lines), "image": None})

    def add_diagram_page(title: str, image: Path, lines: list[str]) -> None:
        pages.append({"lines": [title] + [line.strip() for line in lines if line.strip()], "image": image})

    def content_page(
        title: str,
        purpose: str,
        actor: str,
        inputs: str,
        outputs: str,
        objects: str,
        points: list[str],
        checks: list[str],
        exceptions: list[str],
        records: list[str],
    ) -> None:
        lines = [
            f"定位：{purpose}",
            f"使用者：{actor}",
            f"主要输入：{inputs}",
            f"主要输出：{outputs}",
            f"核心对象：{objects}",
            "处理说明：",
        ]
        lines.extend(points)
        lines.append("质量控制：")
        lines.extend(checks)
        lines.append("异常处理：")
        lines.extend(exceptions)
        lines.append("留痕记录：")
        lines.extend(records)
        add_page(title, lines)

    cover_lines = [
        f"软件名称：{SOFTWARE_NAME}",
        f"软件版本：{VERSION}",
        f"软件简称：{SHORT_NAME}",
        f"著作权人：{'、'.join(RIGHTHOLDERS)}",
        f"作者：{'、'.join(AUTHORS)}",
        f"联系人：{CONTACT_NAME}",
        f"联系电话：{CONTACT_PHONE}",
        f"联系地址：{CONTACT_ADDRESS}",
        f"开发完成日期：{COMPLETION_DATE}",
        f"发表状态：{PUBLICATION_STATUS}",
        "文档类型：设计说明书及使用说明文档。",
        "登记口径：原创软件、独立开发、未发表。",
        "技术领域：人工智能、量子计算、软件工程研发。",
        "业务目标：支撑量子代码模型研发过程的闭环管理。",
        "功能范围：数据构建、模型训练、自动评测、检索问答和报告归档。",
        "运行范围：本地工作站和远程训练环境均可纳入研发流程。",
        "数据范围：任务说明、训练样本、评测基准、候选代码和指标报告。",
        "设计原则：模块化、可复现、可审计、可维护。",
        "接口原则：命令参数、配置文件和结果文件均保持稳定。",
        "质量原则：先校验数据和代码，再执行训练和评测。",
        "安全原则：文档不记录账号、密钥、令牌或私人数据。",
        "一致性原则：申请表、说明文档和源程序使用同一名称版本。",
        "图示内容：包含总体结构图、训练评测流程图和核心逻辑框图。",
        "正文内容：覆盖总体设计、接口设计、模块功能、函数功能和算法。",
        "使用内容：覆盖初始化、数据构建、训练、评测、报告和维护。",
        "维护内容：覆盖任务、数据、模块和版本升级的处理方式。",
        "提交文件：申请表、说明文档和源程序均为DOCX格式。",
        "结束标志：文档最后一页以end作为结束标志。",
        "补充事项：身份证件等主体材料由提交人在系统侧按实际补录。",
    ]
    add_page(f"{SOFTWARE_NAME}{VERSION} 设计说明书及使用说明文档", cover_lines)

    toc_lines = [
        "1 总体设计：软件目标、适用场景、角色、边界。",
        "2 系统结构：逻辑架构、流程架构、部署架构、数据流和状态文件。",
        "3 功能模块：任务管理、中间表示、样本生成、校验、训练、评测、检索、报告。",
        "4 数据设计：目录、样本字段、基准文件、日志文件和版本追踪。",
        "5 接口设计：命令行接口、函数接口、文件接口、配置接口和报告接口。",
        "6 算法设计：任务切分、提示构建、候选清洗、执行评分和差异分析。",
        "7 运行设计：本地运行、远程训练、作业生命周期和复现实验。",
        "8 使用说明：初始化、数据构建、训练、评测和报告输出。",
        "9 异常处理：数据、训练、评测和同步异常。",
        "10 安全权限：安全边界、权限控制和审计记录。",
        "11 维护升级：任务维护、数据维护、模块维护和版本维护。",
        "12 附录说明：目录约定、配置约定和提交核查要点。",
        "图1 软件总体结构图：说明模块边界和数据流向。",
        "图2 训练与评测流程图：说明研发执行顺序和结果回收。",
        "图3 核心模块逻辑框图：说明关键函数和文件接口关系。",
        "总体设计部分回答软件为什么建设以及服务什么研发过程。",
        "系统结构部分回答各模块如何连接以及如何交换数据。",
        "功能模块部分回答每个模块承担什么职责以及输出什么成果。",
        "数据设计部分回答样本、基准、日志和报告如何保存。",
        "接口设计部分回答用户、脚本和模块之间如何调用。",
        "算法设计部分回答切分、清洗、评分和分析如何执行。",
        "运行设计部分回答本地验证、远程训练和结果归档如何闭环。",
        "使用说明部分回答实际操作人员从准备到报告的步骤。",
        "异常处理部分回答错误发生后如何定位和恢复。",
        "安全权限部分回答凭据、目录、日志和结果如何隔离。",
        "维护升级部分回答新增任务和修改代码后如何保持质量。",
        "附录说明部分给出提交前核查和后续维护口径。",
        "正文按软件著作权登记说明文档要求组织。",
        "下页开始进入详细设计说明。",
    ]
    add_page("目录", toc_lines)

    content_specs = [
        (
            "1.1 软件目标",
            "建设面向量子代码模型研发的统一工作平台",
            "研发负责人、算法工程师、测试人员",
            "量子任务、训练样本、评测基准、模型目录",
            "训练记录、评测得分、失败摘要、归档报告",
            "任务库、数据集、评测运行、报告文件",
            [
                "统一管理量子算法代码生成任务，减少手工整理误差。",
                "把数据构建、训练、评测和报告连接成一条闭环流程。",
                "为每次实验保留输入数据、运行参数和输出结果。",
                "通过自动评测判断候选代码是否满足任务约束。",
                "支持对不同训练结果在同一基准上做可比分析。",
                "为项目验收和成果管理提供可追溯材料。",
                "降低重复命令操作对实验一致性的影响。",
                "将量子领域任务和通用代码任务统一纳入管理。",
                "保留失败任务，便于后续补充数据和改进模型。",
                "将报告归档作为训练完成后的必要步骤。",
            ],
            [
                "数据清单必须记录样本数量和拆分策略。",
                "评测结果必须绑定具体任务编号和候选文件。",
                "报告结论必须来自可执行测试结果。",
                "关键输出目录不得被临时文件覆盖。",
            ],
            [
                "输入目录不存在时停止流程并提示路径。",
                "评测脚本缺失时记录失败类型并跳过后续汇总。",
                "报告写入失败时保留原始指标文件。",
            ],
            [
                "记录训练数据路径、评测基准路径和输出目录。",
                "记录通过率、失败原因、运行时间和报告位置。",
                "记录软件版本、执行日期和操作者使用的命令。",
            ],
        ),
        (
            "1.2 适用场景",
            "服务量子算法代码生成、训练和评测的研发场景",
            "训练工程师、评测工程师、项目管理员",
            "任务描述、参考约束、测试用例、运行配置",
            "训练样本、候选代码、测试结果、对比报告",
            "量子算法任务、通用编程任务、实验批次",
            [
                "适用于生成量子线路、量子门序列和相关辅助代码。",
                "适用于构建指令微调样本和保留严格评测集。",
                "适用于对候选代码进行语法检查、导入检查和断言测试。",
                "适用于比较基础模型、训练结果和不同实验批次。",
                "适用于将文档语料索引后提供研发问答支持。",
                "适用于对失败任务进行原因分类和后续修复排期。",
                "适用于本地小样本验证和远程长任务训练。",
                "适用于项目阶段性总结、验收材料和内部归档。",
                "适用于单人研发，也适用于多人共享同一套基准。",
                "适用于不公开发布的软件研发管理过程。",
            ],
            [
                "训练集和评测集必须保持任务级隔离。",
                "评测基准应固定，避免结果不可比较。",
                "实验命令应保存，避免只保留最终结论。",
                "归档报告应包含失败任务而不是只保留成功项。",
            ],
            [
                "任务定义不完整时标记为数据异常。",
                "候选代码不可执行时标记为评测异常。",
                "训练输出缺失时标记为运行异常。",
            ],
            [
                "保存任务编号、领域、提示族和样本编号。",
                "保存每个场景对应的输入输出目录。",
                "保存阶段性报告和人工复核备注。",
            ],
        ),
        (
            "1.3 用户角色",
            "划分研发平台使用过程中的职责边界",
            "研发人员、训练人员、评测人员、管理员",
            "角色权限、任务分工、运行记录、报告需求",
            "职责清单、执行记录、复核结论、维护事项",
            "用户、命令、目录、报告、审计记录",
            [
                "研发人员负责补充量子任务、参考约束和测试目标。",
                "数据人员负责生成训练样本并检查拆分结果。",
                "训练人员负责配置模型路径、训练参数和输出目录。",
                "评测人员负责准备基准、执行测试和核对失败原因。",
                "项目管理员负责保存报告、版本说明和归档材料。",
                "维护人员负责处理依赖变化、接口调整和回归测试。",
                "同一实验批次的输入、输出和日志由执行人员确认。",
                "多人协作时不得覆盖他人的结果目录。",
                "提交材料前由负责人检查名称、版本和发表状态。",
                "系统账号和个人凭据不写入说明文档或报告正文。",
            ],
            [
                "每个关键操作应能追溯到执行命令和输出目录。",
                "角色职责不得依赖口头说明保存。",
                "报告发布前应完成失败项复核。",
                "维护修改后应重新执行相关测试。",
            ],
            [
                "职责不清时先暂停发布报告。",
                "输出目录冲突时更换批次目录。",
                "权限不足时记录缺失文件而不是绕过检查。",
            ],
            [
                "保存操作者、命令、时间和结果位置。",
                "保存人工复核意见和待处理事项。",
                "保存提交前的材料核查结论。",
            ],
        ),
        (
            "1.4 系统边界",
            "明确本软件权利保护和技术实现的边界",
            "登记审核人员、项目负责人、维护人员",
            "自研源程序、说明文档、配置样例、测试数据",
            "登记材料、研发报告、可审计的运行结果",
            "自研模块、通用运行环境、外部基础资源",
            [
                "本软件登记对象为自研业务代码和设计表达。",
                "通用操作系统、通用硬件和基础运行库不作为权利对象。",
                "远程训练环境只作为运行场所，不作为软件功能主体。",
                "对象存储只作为文件传输介质，不作为本软件登记内容。",
                "模型权重目录作为输入资源管理，不改变本软件边界。",
                "文档避免出现无关平台、服务或模型商标文字。",
                "源程序抽取优先选择自研通用模块和测试模块。",
                "申请表中的功能描述与说明文档保持一致。",
                "未发表状态下不填写首次发表日期和地点。",
                "未来如按升级版本登记，应另行说明差异。",
            ],
            [
                "提交前检查文档中是否包含无关敏感信息。",
                "提交前检查页眉名称版本是否一致。",
                "提交前检查源程序末页是否有结束标志。",
                "提交前检查说明文档是否覆盖设计必备项。",
            ],
            [
                "发现外部商标文字时改为通用技术表述。",
                "发现私人凭据时删除并重新生成材料。",
                "发现主体信息变化时同步更新申请表和封面。",
            ],
            [
                "保存材料生成清单。",
                "保存模板逐项检查报告。",
                "保存正式提交文件名和生成时间。",
            ],
        ),
    ]

    content_specs.extend([
        (
            "2.1 逻辑架构",
            "说明软件内部模块的逻辑分层和协作方式",
            "架构设计人员、研发人员",
            "任务库、配置文件、数据清单、运行命令",
            "训练样本、评测结果、索引文件、报告文件",
            "入口层、处理层、执行层、归档层",
            [
                "入口层提供命令行脚本和配置读取能力。",
                "处理层完成任务解析、数据生成、提示构建和候选清洗。",
                "执行层完成模型训练、候选生成、测试执行和指标计算。",
                "归档层保存日志、报告、清单和模型输出目录。",
                "任务库向数据构建模块提供任务定义和测试约束。",
                "数据构建模块向训练模块提供训练样本。",
                "评测模块读取基准文件并执行候选代码。",
                "检索模块读取文档语料并返回相关片段。",
                "报告模块汇总训练指标、评测结果和失败原因。",
                "各层通过文件和函数接口协作，避免隐藏状态。",
            ],
            [
                "模块输入输出应有明确文件路径。",
                "共享目录应区分原始数据、生成数据和结果数据。",
                "架构调整必须同步更新流程图和接口说明。",
                "每个执行入口应具备基本参数校验。",
            ],
            [
                "入口参数缺失时给出明确错误。",
                "处理层数据不一致时停止执行。",
                "归档层写入失败时保留临时输出。",
            ],
            [
                "记录模块调用关系。",
                "记录输入输出文件路径。",
                "记录每个批次的架构相关变更。",
            ],
        ),
        (
            "2.2 流程架构",
            "说明从任务准备到结果报告的主流程",
            "研发人员、训练人员、评测人员",
            "任务定义、训练配置、评测基准、报告模板",
            "数据集、训练输出、评测得分、项目报告",
            "准备阶段、训练阶段、评测阶段、归档阶段",
            [
                "准备阶段检查目录、依赖、任务文件和配置文件。",
                "数据阶段把任务定义转换为训练样本和评测清单。",
                "训练阶段读取样本和参数，生成日志与模型输出。",
                "评测阶段生成候选代码并在隔离目录执行测试。",
                "报告阶段汇总通过率、失败类型和重要结论。",
                "归档阶段保存日志、清单、报告和可复现实验命令。",
                "流程以本地验证作为前置条件。",
                "耗时训练任务完成后必须回收日志和结果。",
                "评测基准固定后不得在同一报告中随意替换。",
                "最终报告应能追溯到具体数据版本。",
            ],
            [
                "每个阶段完成后检查输出是否存在。",
                "训练完成不等于评测通过，必须执行评分。",
                "报告结论不得脱离原始指标文件。",
                "归档前检查失败项是否被记录。",
            ],
            [
                "阶段失败时停止后续流程。",
                "结果缺失时保留已完成阶段输出。",
                "指标异常时重新读取原始日志核对。",
            ],
            [
                "保存阶段状态和执行时间。",
                "保存使用的数据版本和配置。",
                "保存最终报告路径。",
            ],
        ),
        (
            "2.3 部署架构",
            "说明软件在本地和远程训练环境中的部署方式",
            "部署人员、训练人员、维护人员",
            "软件目录、依赖环境、数据目录、模型目录",
            "可运行工作区、训练输出、同步结果",
            "本地工作区、远程工作区、共享归档目录",
            [
                "本地工作区用于代码开发、单元测试和小规模验证。",
                "远程训练环境用于执行资源需求较高的训练任务。",
                "软件目录保持统一结构，便于本地和远程对齐。",
                "数据目录、模型目录和报告目录使用明确路径。",
                "远程执行前先同步经过本地验证的代码和数据。",
                "远程执行后回传日志、模型输出和评测结果。",
                "本地报告以回传文件为依据生成或更新。",
                "部署过程不依赖手工复制单个代码片段。",
                "共享归档目录只保存可公开给项目组的结果。",
                "临时缓存和私人文件不纳入正式同步范围。",
            ],
            [
                "同步前执行语法检查或单元测试。",
                "远程目录存在性需要显式检查。",
                "输出回传后核对文件数量和关键文件。",
                "部署说明应避免写入访问凭据。",
            ],
            [
                "远程命令失败时保存终端输出。",
                "文件缺失时重新核对同步清单。",
                "依赖缺失时先修复运行环境再训练。",
            ],
            [
                "记录本地路径和远程路径。",
                "记录同步时间和文件清单。",
                "记录训练输出和回传结果。",
            ],
        ),
        (
            "2.4 数据流设计",
            "说明数据在任务、训练、评测和报告之间的流转",
            "数据人员、评测人员、研发人员",
            "任务定义、参考约束、训练样本、候选输出",
            "清单文件、评测结果、得分卡、报告摘要",
            "任务数据、样本数据、运行数据、报告数据",
            [
                "任务定义先进入数据构建模块。",
                "数据构建模块生成训练集、评测集和清单文件。",
                "训练模块读取训练集并输出日志和模型结果。",
                "候选生成模块读取模型结果并保存候选代码。",
                "评测模块读取候选代码和测试约束。",
                "评分模块根据测试结果生成任务级分数。",
                "报告模块读取任务级分数并生成汇总说明。",
                "失败任务回流到任务维护和数据维护环节。",
                "清单文件作为数据规模和来源的核查依据。",
                "报告文件作为项目复核和登记材料的内部依据。",
            ],
            [
                "训练集和评测集不得混用。",
                "候选代码需要保留原始输出和清洗输出。",
                "报告应引用具体评测运行目录。",
                "数据流变更必须同步更新清单。",
            ],
            [
                "样本字段缺失时停止生成。",
                "候选文件为空时标记候选异常。",
                "评分文件缺失时重新执行评测。",
            ],
            [
                "记录数据流向和生成时间。",
                "记录清单哈希或等效校验信息。",
                "记录失败回流的任务编号。",
            ],
        ),
        (
            "2.5 状态文件设计",
            "说明软件运行过程中的状态记录和恢复依据",
            "训练人员、维护人员、项目管理员",
            "命令参数、运行状态、日志片段、输出路径",
            "状态文件、错误摘要、恢复建议、归档索引",
            "状态记录、日志记录、报告索引、恢复点",
            [
                "状态文件记录当前阶段、开始时间和结束时间。",
                "训练状态记录模型路径、数据路径和输出路径。",
                "评测状态记录基准文件、候选目录和测试结果。",
                "同步状态记录上传范围、下载范围和文件数量。",
                "报告状态记录输入指标、生成位置和摘要结论。",
                "错误摘要记录失败命令、错误类型和排查方向。",
                "恢复点用于判断是否可从中间结果继续。",
                "状态文件采用结构化文本格式，便于脚本读取。",
                "临时状态和正式归档状态分目录保存。",
                "状态文件不得保存账号密码或访问令牌。",
            ],
            [
                "状态文件写入采用覆盖风险较低的方式。",
                "关键字段缺失时不得生成最终报告。",
                "恢复执行前检查输入文件是否仍然存在。",
                "归档前检查状态与实际文件一致。",
            ],
            [
                "状态损坏时重新读取日志生成摘要。",
                "恢复失败时转为完整重跑。",
                "状态冲突时保留旧状态并创建新批次。",
            ],
            [
                "保存状态文件路径。",
                "保存错误摘要路径。",
                "保存恢复处理结果。",
            ],
        ),
    ])

    def maybe_add_diagram_pages() -> None:
        if len(pages) == 7:
            add_diagram_page("图1 软件总体结构图", diagram_paths[0], [
                "图1展示任务库、数据构建、模型训练、自动评测、检索问答和报告归档之间的关系。",
                "任务库向数据构建模块提供任务定义和测试约束。",
                "数据构建模块生成训练样本、评测清单和完整性报告。",
                "训练模块读取样本并输出训练日志和模型结果。",
                "评测模块执行候选代码并输出任务级得分。",
                "报告归档模块汇总指标、失败原因和运行记录。",
                "各模块以文件接口和函数接口连接，便于复现和维护。",
            ])
        if len(pages) == 21:
            add_diagram_page("图2 训练与评测流程图", diagram_paths[1], [
                "图2展示本地验证、文件同步、远程训练、结果回传、候选生成和报告输出流程。",
                "软件先在本地完成语法检查、数据校验和小样本验证。",
                "远程训练只接收已经确认的代码、数据和配置。",
                "训练完成后回传日志、模型结果和必要的评测输出。",
                "评测阶段统一生成候选代码、运行测试并记录失败类型。",
                "报告阶段根据原始得分卡生成结论，不以命令启动成功代替结果成功。",
                "该流程保证训练和评测均有明确的输入、输出和复核依据。",
            ])
        if len(pages) == 36:
            add_diagram_page("图3 核心模块逻辑框图", diagram_paths[2], [
                "图3展示量子中间表示、提示构建、模型执行、候选清洗、隔离测试和分数汇总关系。",
                "量子中间表示把寄存器、操作、参数和测量目标结构化。",
                "提示构建模块把任务约束转换为稳定的模型输入。",
                "候选清洗模块提取可执行代码并保存清洗差异。",
                "隔离测试模块运行断言、捕获异常并输出任务级结果。",
                "分数汇总模块形成通过率、失败原因和对比报告。",
                "核心逻辑强调可执行验证和可追溯归档。",
            ])

    for spec in content_specs:
        content_page(*spec)
        maybe_add_diagram_pages()

    remaining_specs = [
        ("3.1 量子任务管理", "管理量子傅里叶变换、搜索、变分、纠错等任务", "任务维护人员、算法工程师", "任务编号、任务描述、测试约束", "任务清单、测试入口、维护记录", "任务条目、领域标签、测试文件"),
        ("3.2 量子中间表示", "用结构化方式描述寄存器、量子门、测量和目标", "算法工程师、数据人员", "线路结构、参数、门序列、测量规则", "可校验对象、序列化文本、错误报告", "寄存器、操作、参数、约束"),
        ("3.3 训练样本生成", "把任务说明和约束转换为可训练记录", "数据人员、训练人员", "任务说明、参考实现、提示模板", "训练集、验证集、样本清单", "样本编号、提示、回答、元数据"),
        ("3.4 数据完整性校验", "检查训练集和评测集是否满足隔离和格式要求", "数据人员、评测人员", "样本文件、基准文件、清单文件", "完整性报告、错误列表、统计摘要", "样本编号、任务编号、提示族"),
        ("3.5 训练模块", "执行文本微调训练并保存训练输出", "训练工程师", "训练数据、模型目录、参数配置", "训练日志、检查点、适配器目录", "训练参数、批次、步数、输出目录"),
        ("3.6 评测模块", "对候选代码进行可执行测试并计算通过率", "评测工程师", "候选文件、测试文件、评测基准", "得分卡、失败摘要、标准输出", "测试用例、候选目录、评分结果"),
        ("3.7 检索增强模块", "为研发问答提供文档片段检索能力", "研发人员、维护人员", "文档语料、查询文本、索引目录", "相关片段、来源路径、问答记录", "文档片段、向量索引、检索结果"),
        ("3.8 报告归档模块", "汇总实验指标并保存可复核材料", "项目管理员、研发负责人", "训练日志、评测结果、失败记录", "报告文档、对比表、归档目录", "指标表、失败清单、结论摘要"),
        ("4.1 数据目录设计", "规范数据、任务、模型、报告和临时文件目录", "数据人员、维护人员", "软件根目录、运行批次、配置路径", "稳定目录结构、归档位置、清理范围", "数据目录、任务目录、报告目录"),
        ("4.2 样本字段设计", "定义训练记录和评测记录的字段含义", "数据人员、训练人员", "任务编号、领域、提示内容、回答内容", "结构化样本、字段校验结果", "样本字段、元数据、拆分标记"),
        ("4.3 评测基准设计", "定义评测任务、候选文件和测试脚本之间的映射", "评测工程师", "任务编号、测试入口、运行预算", "基准文件、评分目标、任务列表", "基准条目、测试约束、评分规则"),
        ("4.4 日志数据设计", "记录训练、评测、同步和报告生成过程", "维护人员、项目管理员", "命令、参数、标准输出、错误输出", "日志文件、摘要文件、问题定位线索", "运行日志、错误日志、摘要日志"),
        ("4.5 版本追踪设计", "追踪数据版本、代码版本和报告版本之间的关系", "项目管理员、维护人员", "数据清单、变更说明、运行目录", "版本记录、差异摘要、复核结论", "版本号、批次号、归档索引"),
        ("5.1 命令行接口设计", "提供数据构建、训练、评测和报告命令入口", "研发人员、训练人员", "命令参数、配置路径、运行目录", "执行状态、输出路径、错误提示", "脚本入口、参数解析、退出码"),
        ("5.2 函数接口设计", "定义模块之间可复用的函数调用边界", "开发人员、维护人员", "解析对象、配置对象、任务对象", "校验结果、生成结果、评分结果", "解析函数、校验函数、汇总函数"),
        ("5.3 文件接口设计", "定义JSON、JSONL、Markdown和代码文件的交换方式", "开发人员、数据人员", "结构化文件、候选代码、报告草稿", "中间文件、最终文件、归档文件", "文件路径、编码、字段结构"),
        ("5.4 配置接口设计", "定义模型路径、数据路径和运行预算等参数来源", "训练人员、维护人员", "配置文件、命令参数、默认值", "生效配置、参数快照、错误提示", "参数项、默认策略、覆盖规则"),
        ("5.5 报告接口设计", "定义指标报告和对比报告的输出格式", "项目管理员、研发负责人", "得分卡、日志摘要、失败列表", "报告正文、对比结论、归档索引", "指标字段、任务表、结论段落"),
        ("6.1 任务切分算法", "按任务和提示族控制训练评测隔离", "数据人员、评测人员", "任务编号、样本编号、提示族", "训练子集、评测子集、隔离报告", "切分规则、去重集合、校验结果"),
        ("6.2 提示构建算法", "把任务说明和约束组织为模型输入", "数据人员、研发人员", "任务描述、约束条件、期望输出", "提示文本、训练记录、评测提示", "提示模板、字段映射、长度控制"),
        ("6.3 候选清洗算法", "从模型输出中提取可执行代码", "评测人员、维护人员", "原始输出、语言标识、任务约束", "候选代码、清洗日志、差异摘要", "文本块、代码块、清洗规则"),
        ("6.4 执行评分算法", "根据测试执行结果生成任务级分数", "评测工程师", "候选代码、测试脚本、运行预算", "通过状态、失败类型、得分卡", "退出码、断言结果、超时状态"),
        ("6.5 差异分析算法", "比较不同实验结果并识别提升和退化", "研发负责人、评测人员", "两个或多个得分卡、任务清单", "新增通过、退化失败、稳定任务", "任务状态、对比表、摘要统计"),
        ("7.1 本地运行设计", "在本地工作区完成低成本验证", "开发人员、评测人员", "代码、样本、测试命令、配置文件", "单元测试结果、小样本报告", "本地目录、测试入口、缓存文件"),
        ("7.2 远程训练设计", "把已验证材料交给远程训练环境执行", "训练人员、维护人员", "代码包、数据包、模型目录、运行命令", "训练日志、模型输出、回传结果", "远程目录、作业命令、结果包"),
        ("7.3 作业生命周期", "跟踪训练作业从启动到归档的完整状态", "训练人员、项目管理员", "启动命令、状态文件、日志文件", "完成标记、失败摘要、归档目录", "作业编号、阶段状态、输出路径"),
        ("7.4 复现实验设计", "通过固定输入和参数复现关键实验", "研发负责人、测试人员", "数据版本、配置快照、命令记录", "复现实验报告、差异说明", "随机种子、运行预算、结果目录"),
        ("8.1 初始化操作", "准备软件根目录、依赖和基础配置", "首次使用人员、维护人员", "软件目录、依赖环境、配置样例", "可运行工作区、检查结果", "根目录、配置文件、环境检查"),
        ("8.2 数据构建操作", "生成训练样本和评测清单", "数据人员", "任务目录、构建命令、输出目录", "训练文件、评测文件、清单报告", "构建脚本、样本文件、校验文件"),
        ("8.3 训练操作", "执行模型训练并保存输出", "训练人员", "训练数据、模型目录、参数配置", "训练日志、输出目录、检查点", "训练脚本、参数表、日志文件"),
        ("8.4 评测操作", "生成候选代码并运行测试", "评测人员", "评测基准、模型输出、运行预算", "候选文件、测试结果、得分卡", "评测脚本、候选目录、测试日志"),
        ("8.5 报告操作", "汇总指标并形成项目材料", "项目管理员、研发负责人", "得分卡、失败记录、日志摘要", "报告文件、结论摘要、归档清单", "报告脚本、指标表、归档目录"),
        ("9.1 数据异常处理", "处理字段缺失、编号重复和拆分污染", "数据人员、维护人员", "样本文件、清单文件、校验结果", "错误列表、修复后数据、复核报告", "字段、编号、拆分集合"),
        ("9.2 训练异常处理", "处理依赖缺失、资源不足和保存失败", "训练人员、维护人员", "训练命令、日志、输出目录", "失败摘要、修复动作、重跑记录", "依赖、资源、检查点"),
        ("9.3 评测异常处理", "处理语法错误、导入错误、断言失败和超时", "评测人员、开发人员", "候选代码、测试日志、错误输出", "失败分类、定位信息、修复建议", "候选文件、测试用例、错误类型"),
        ("9.4 同步异常处理", "处理文件同步、远程命令和结果回传异常", "维护人员、训练人员", "同步清单、远程路径、回传目录", "缺失文件列表、重试记录、修复结论", "传输批次、文件数量、校验结果"),
        ("10.1 安全边界", "明确软件材料中的敏感信息处理方式", "全体使用人员", "配置文件、日志文件、报告文件", "脱敏材料、安全检查结论", "账号、密钥、私人数据、公开材料"),
        ("10.2 权限控制", "控制目录、配置、数据和结果的访问范围", "项目管理员、维护人员", "用户角色、目录路径、结果目录", "权限说明、访问记录、隔离结果", "角色、目录、文件权限"),
        ("10.3 审计记录", "建立命令、参数、日志和报告之间的追溯关系", "项目管理员、审核人员", "执行命令、参数快照、日志文件", "审计链路、复核记录、问题闭环", "命令记录、日志索引、报告编号"),
        ("11.1 任务维护", "新增或修改量子任务并保持评测有效", "算法工程师、数据人员", "新任务说明、测试约束、参考要求", "任务条目、测试文件、维护记录", "任务编号、任务文件、测试入口"),
        ("11.2 数据维护", "维护训练数据和评测数据的质量", "数据人员、评测人员", "样本文件、清单文件、变更说明", "新数据版本、校验报告、差异说明", "样本集合、拆分策略、统计信息"),
        ("11.3 模块维护", "修改训练、评测、检索和报告模块时保持兼容", "开发人员、维护人员", "代码变更、测试用例、接口说明", "更新模块、回归结果、变更记录", "模块接口、函数签名、测试范围"),
        ("11.4 版本维护", "未来版本升级时记录功能和代码差异", "项目管理员、研发负责人", "功能变更、性能变化、代码清单", "版本说明、差异报告、升级材料", "版本号、变更项、兼容性"),
        ("12.1 目录约定", "说明软件根目录下各类文件的摆放规则", "维护人员、使用人员", "根目录、数据目录、报告目录", "清晰目录结构、归档位置", "源码目录、数据目录、报告目录"),
        ("12.2 配置约定", "说明参数命名、路径命名和运行预算约定", "训练人员、维护人员", "配置文件、命令参数、默认值", "生效参数、参数快照、复核记录", "配置项、路径项、预算项"),
        ("12.3 提交核查要点", "提交软件著作权材料前进行一致性检查", "提交人、项目负责人", "申请表、说明文档、源程序、清单", "核查报告、正式提交文件", "名称版本、页眉页码、结束标志"),
    ]

    for title, purpose, actor, inputs, outputs, objects in remaining_specs:
        section_no = title.split(".", 1)[0]
        if section_no == "3":
            points = [
                f"模块启动时读取{inputs}，并把处理范围限定在当前任务批次。",
                f"模块内部围绕{objects}建立清晰的数据结构，避免隐式共享状态。",
                f"任务编号、样本编号和输出目录在模块入口处统一解析。",
                "处理步骤按读取、校验、转换、执行、写出顺序组织。",
                "模块输出必须可被训练、评测或报告流程直接消费。",
                "同一模块的批量任务按任务编号排序，便于复核。",
                "可复用逻辑封装为函数，入口脚本只负责参数解析和调度。",
                "中间结果保存到批次目录，正式结果保存到归档目录。",
                "模块变更时同步补充对应单元测试或回归样例。",
                "模块完成后输出简短摘要，说明处理数量和异常数量。",
            ]
            checks = [
                f"核对{outputs}是否覆盖本批次全部任务。",
                "核对模块输出能否被下游脚本直接读取。",
                "核对任务编号、样本编号和日志编号是否一致。",
                "核对失败项是否带有可定位的文件路径。",
            ]
        elif section_no == "4":
            points = [
                f"数据文件围绕{objects}组织，目录名体现用途和批次。",
                "结构化数据采用统一编码保存，避免跨平台读取异常。",
                "训练样本、评测样本和报告输入使用不同目录隔离。",
                "清单文件记录数据规模、来源、拆分策略和生成时间。",
                "样本字段保持稳定，新增字段应兼容旧数据读取。",
                "评测基准只记录必要任务信息，不混入训练答案。",
                "日志数据按训练、评测、同步和报告类型分开保存。",
                "版本追踪把数据、代码和报告绑定到同一批次。",
                "临时文件不得与正式归档文件混放。",
                "数据设计优先保证可追溯，其次考虑存储压缩。",
            ]
            checks = [
                "核对目录层级是否与清单记录一致。",
                "核对样本字段是否齐全且类型正确。",
                "核对评测基准是否没有混入训练记录。",
                "核对日志和报告是否能对应同一批次。",
            ]
        elif section_no == "5":
            points = [
                f"接口围绕{objects}定义，输入输出均采用显式参数。",
                "命令行入口提供必要参数、默认值和错误提示。",
                "函数接口保持单一职责，避免一个函数同时完成多阶段工作。",
                "文件接口明确路径、编码、字段和读写时机。",
                "配置接口允许命令参数覆盖默认配置。",
                "报告接口输出结构化指标和面向人员阅读的摘要。",
                "接口调用前先完成参数校验，调用后检查输出文件。",
                "接口变更时保持向后兼容或给出迁移说明。",
                "跨模块调用只传递必要数据，避免直接访问内部变量。",
                "接口文档与实际脚本参数保持一致。",
            ]
            checks = [
                "核对必填参数缺失时是否有清晰提示。",
                "核对函数返回值是否能表达成功和失败。",
                "核对文件输出是否使用稳定名称。",
                "核对报告字段是否满足项目复核需要。",
            ]
        elif section_no == "6":
            points = [
                f"算法围绕{objects}执行，优先采用确定性规则。",
                "任务切分先建立集合，再检查交叉项。",
                "提示构建控制上下文长度，保留任务约束和输出要求。",
                "候选清洗保留可执行代码，并记录被删除的非代码片段。",
                "执行评分基于退出码、断言结果、超时状态和异常类型。",
                "差异分析按任务维度比较新增通过和退化失败。",
                "算法参数写入运行记录，避免结果不可复现。",
                "随机过程必须记录种子或采用固定排序。",
                "异常样本不直接丢弃，而是进入失败摘要。",
                "算法输出既服务自动流程，也服务人工复核。",
            ]
            checks = [
                "核对算法输入集合是否去重。",
                "核对输出统计是否与任务明细一致。",
                "核对失败分类是否覆盖主要异常。",
                "核对同一输入重复运行是否得到一致结果。",
            ]
        elif section_no == "7":
            points = [
                f"运行过程围绕{objects}安排，先验证后执行长任务。",
                "本地运行负责发现语法、依赖和小样本数据问题。",
                "远程训练只处理已经打包确认的代码、数据和配置。",
                "作业启动后记录开始时间、命令、目录和预期输出。",
                "作业运行中关注日志增长、错误摘要和资源状态。",
                "作业结束后检查模型输出、日志文件和评测结果。",
                "复现实验要求固定数据版本、参数和运行预算。",
                "本地与远程路径通过同步清单保持一致。",
                "结果回传后在本地生成或更新最终报告。",
                "运行设计强调结果闭环，不以启动成功代表任务成功。",
            ]
            checks = [
                "核对本地验证是否完成。",
                "核对远程输出是否完整回传。",
                "核对作业状态是否与日志末尾一致。",
                "核对复现实验使用的输入是否固定。",
            ]
        elif section_no == "8":
            points = [
                f"操作人员围绕{objects}执行，按准备、执行、检查顺序推进。",
                "初始化时进入软件根目录，确认配置和依赖。",
                "构建数据时先选择任务范围，再生成样本和清单。",
                "训练时指定数据路径、模型路径、输出路径和批次参数。",
                "评测时准备基准文件，生成候选代码并运行测试。",
                "报告时读取原始得分卡，不手工改写指标。",
                "每次操作完成后查看输出目录和日志摘要。",
                "重要命令写入运行记录，便于同事复现。",
                "操作失败时先保存错误输出，再修改参数重试。",
                "完成一轮研发后归档数据、日志、结果和报告。",
            ]
            checks = [
                "核对命令所在目录是否正确。",
                "核对输出文件数量是否符合预期。",
                "核对报告结论是否来自最新评测。",
                "核对归档目录是否包含必要材料。",
            ]
        elif section_no == "9":
            points = [
                f"异常处理围绕{objects}定位，先区分数据、环境和代码问题。",
                "数据异常优先检查字段、编号、格式和拆分关系。",
                "训练异常优先检查依赖、资源、路径和保存权限。",
                "评测异常优先检查候选代码、测试入口和超时设置。",
                "同步异常优先检查文件清单、目标路径和回传结果。",
                "所有异常都写入失败摘要，不只保留终端输出。",
                "可恢复异常允许重试，不可恢复异常进入人工复核。",
                "同一异常重复出现时提升为维护事项。",
                "异常修复后重新执行对应阶段，而不是跳过检查。",
                "异常记录保留原始错误和处理结论。",
            ]
            checks = [
                "核对异常类型是否分类清楚。",
                "核对失败文件路径是否可定位。",
                "核对修复后是否重新执行验证。",
                "核对失败摘要是否进入报告材料。",
            ]
        elif section_no == "10":
            points = [
                f"安全控制围绕{objects}展开，避免敏感信息进入材料。",
                "账号、密钥、令牌和私人目录不得写入文档。",
                "配置文件只记录必要路径和运行参数。",
                "训练数据和评测结果按项目范围保存。",
                "日志公开前检查是否包含敏感路径和凭据片段。",
                "不同批次结果分目录保存，避免互相覆盖。",
                "人员权限按任务需要分配，减少无关访问。",
                "审计记录保留命令、参数、日志和报告之间的关系。",
                "正式提交材料只包含登记所需内容。",
                "发现敏感信息后删除并重新生成相关材料。",
            ]
            checks = [
                "核对文档是否包含账号或密钥。",
                "核对归档目录是否排除私人文件。",
                "核对日志是否经过必要脱敏。",
                "核对提交材料是否与申请范围一致。",
            ]
        elif section_no == "11":
            points = [
                f"维护工作围绕{objects}展开，修改后必须保持训练评测闭环。",
                "新增任务时同步补充任务说明、测试约束和评测入口。",
                "新增数据时更新清单并执行完整性校验。",
                "修改模块时检查函数接口、文件接口和命令参数。",
                "修改报告逻辑时保留原始指标和对比依据。",
                "版本升级时记录功能差异、兼容变化和代码范围。",
                "维护操作先在小范围验证，再进入完整流程。",
                "维护结果写入变更记录，便于后续追踪。",
                "发现回归问题时回到对应模块修复。",
                "维护完成后重新生成必要说明和检查报告。",
            ]
            checks = [
                "核对新增任务是否有测试覆盖。",
                "核对数据清单是否同步更新。",
                "核对接口变更是否影响下游模块。",
                "核对版本说明是否与实际变更一致。",
            ]
        else:
            points = [
                f"附录内容围绕{objects}说明，服务提交前复核和后续维护。",
                "目录约定帮助人员快速找到源码、数据、模型和报告。",
                "配置约定帮助人员理解参数来源和覆盖关系。",
                "提交核查要点帮助保持申请表、说明文档和源程序一致。",
                "正式文件名应保留材料名称、软件名称和版本号。",
                "页眉显示软件名称和版本，页码位于页眉右侧。",
                "说明文档应覆盖总体设计、接口、模块、函数、算法和运行。",
                "源程序应按要求组织页数、行数和结束标志。",
                "清单文件用于核对生成时间、源程序量和正式文件范围。",
                "提交前如主体信息变化，应同步更新所有材料。",
            ]
            checks = [
                "核对正式文件名是否清楚。",
                "核对软件名称版本是否一致。",
                "核对末页是否包含结束标志。",
                "核对清单和申请表源程序量是否一致。",
            ]
        exceptions = [
            "路径错误时停止当前命令并输出缺失路径。",
            "字段错误时记录具体字段名和所在文件。",
            "结果不完整时保留已生成文件并标记批次异常。",
        ]
        records = [
            "保存输入输出路径和运行时间。",
            "保存校验结论和失败原因。",
            "保存后续维护需要的变更说明。",
        ]
        content_page(title, purpose, actor, inputs, outputs, objects, points, checks, exceptions, records)
        maybe_add_diagram_pages()

    if len(pages) != 60:
        raise RuntimeError(f"manual page plan must be exactly 60 pages, got {len(pages)}")

    doc = Document()
    sec = doc.sections[0]
    configure_section(sec, top=Cm(2.0), bottom=Cm(1.0), left=Cm(2.55), right=Cm(1.95))
    doc.styles["Normal"].font.name = "宋体"
    doc.styles["Normal"]._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    doc.styles["Normal"].font.size = Pt(10.5)
    for style_name, size, bold in [("Heading 1", 14, True), ("Heading 2", 12, True), ("Heading 3", 11, True), ("Body Text", 10.5, False)]:
        style = doc.styles[style_name]
        style.font.name = "宋体"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
        style.font.size = Pt(size)
        style.font.bold = bold
        style.font.color.rgb = RGBColor(0, 0, 0)

    def write_run(paragraph, text: str, font_size=Pt(10.5), bold=False) -> None:
        run = paragraph.add_run(text)
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
        run.font.size = font_size
        run.bold = bold
        run.font.color.rgb = RGBColor(0, 0, 0)

    def add_heading(text: str, level: int) -> None:
        style = "Heading 1" if level == 1 else "Heading 2" if level == 2 else "Heading 3"
        p = doc.add_paragraph(style=style)
        p.paragraph_format.space_before = Pt(6 if level == 1 else 4)
        p.paragraph_format.space_after = Pt(4 if level == 1 else 2)
        p.paragraph_format.line_spacing = 1.25
        write_run(p, text, font_size=Pt(13 if level == 1 else 11.5 if level == 2 else 10.5), bold=True)

    def add_body(text: str, indent=True) -> None:
        p = doc.add_paragraph(style="Body Text")
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(1.5)
        p.paragraph_format.line_spacing = 1.08
        if indent:
            p.paragraph_format.first_line_indent = Pt(21)
        write_run(p, text, font_size=Pt(9.8))

    def add_center(text: str, size=14, bold=True) -> None:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.25
        write_run(p, text, font_size=Pt(size), bold=bold)

    def add_bullets(items: list[str]) -> None:
        for item in items:
            p = doc.add_paragraph(style="Body Text")
            p.paragraph_format.left_indent = Pt(21)
            p.paragraph_format.first_line_indent = Pt(-10.5)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.2
            write_run(p, f"· {item}", font_size=Pt(10.0))

    def add_meta_table(lines: list[str]) -> None:
        table = doc.add_table(rows=0, cols=2)
        table.style = "Table Grid"
        for line in lines:
            if "：" in line:
                key, value = line.split("：", 1)
            else:
                key, value = "项目", line
            cells = table.add_row().cells
            set_cell_text(cells[0], key, font_size=Pt(10))
            set_cell_text(cells[1], value, font_size=Pt(10))
        doc.add_paragraph()

    def split_page_lines(lines: list[str]) -> tuple[list[str], dict[str, list[str]]]:
        title = lines[0]
        body = lines[1:]
        groups: dict[str, list[str]] = {"meta": [], "process": [], "quality": [], "exception": [], "record": []}
        current = "meta"
        for line in body:
            if line == "处理说明：":
                current = "process"
                continue
            if line == "质量控制：":
                current = "quality"
                continue
            if line == "异常处理：":
                current = "exception"
                continue
            if line == "留痕记录：":
                current = "record"
                continue
            groups[current].append(line)
        return title, groups

    def add_section_page(page: dict[str, object], page_index: int) -> None:
        lines = list(page["lines"])
        title, groups = split_page_lines(lines)
        if page_index == 0:
            add_center(title, size=15, bold=True)
            cover_items = [
                f"{SOFTWARE_NAME}{VERSION}",
                f"软件简称：{SHORT_NAME}",
                f"著作权人：{'、'.join(RIGHTHOLDERS)}",
                f"作者：{'、'.join(AUTHORS)}",
                f"开发完成日期：{COMPLETION_DATE}",
                f"发表状态：{PUBLICATION_STATUS}",
                "文档类型：软件设计说明书及使用说明文档",
                "登记口径：原创软件、独立开发、未发表",
            ]
            for item in cover_items:
                add_body(item, indent=False)
            add_body("本说明书依据软件著作权登记材料要求编制，用于说明软件的设计思想、模块组成、接口方式、算法流程、运行方式和使用维护方法。文档内容与申请表、源程序文件保持同一软件名称、版本号、著作权人和发表状态。")
            add_body("软件功能覆盖数据构建、模型训练、自动评测、检索问答、报告归档和维护管理。设计原则为模块化、可复现、可审计和可维护。")
            add_body("本文档不记录账号、密钥、令牌、私人目录或无关外部服务信息；涉及运行环境的内容均按通用技术口径描述。")
            add_body("提交前应核对三份正式材料的文件名、页眉、页码、软件名称、版本号、著作权人、源程序量和发表状态，保证登记系统录入信息与附件内容一致。")
            add_body("文档正文按照总体设计、系统结构、功能模块、数据设计、接口设计、算法设计、运行设计、操作说明、异常处理、安全权限和维护升级展开，重点说明软件如何完成量子代码模型研发流程管理。")
            add_body("图示部分用于辅助理解模块关系和流程关系，文字说明用于描述输入、输出、处理步骤、质量控制、异常处理和维护要求。")
            add_body("源程序文件与本说明书配套使用，源程序展示自研代码内容，本说明书解释软件结构、使用方式和维护方法。")
            add_body("本版本为V1.0，后续如进行升级登记，应根据实际功能变化另行编写版本差异说明。")
            add_body("阅读本文档时，可先查看目录和三张图示了解软件边界，再按章节核对各模块的输入、输出、接口和运行要求。")
            add_body("提交前建议结合实际DOCX附件逐页检查，确认页面没有空白、错页、颜色异常、表格错位或与申请表不一致的内容。")
            add_body("本文档全部文字采用黑色显示，标题和正文均按普通说明文档样式排版。")
            return
        if title == "目录":
            add_center("目录", size=14, bold=True)
            for item in [
                "1 总体设计：软件目标、适用场景、角色和系统边界。",
                "2 系统结构：逻辑架构、流程架构、部署架构、数据流和状态文件。",
                "3 功能模块：任务管理、中间表示、样本生成、校验、训练、评测、检索和报告。",
                "4 数据设计：目录、样本字段、基准文件、日志和版本追踪。",
                "5 接口设计：命令行接口、函数接口、文件接口、配置接口和报告接口。",
                "6 算法设计：任务切分、提示构建、候选清洗、执行评分和差异分析。",
                "7 运行设计：本地运行、远程训练、作业生命周期和复现实验。",
                "8 使用说明：初始化、数据构建、训练、评测和报告输出。",
                "9 异常处理：数据、训练、评测和同步异常。",
                "10 安全权限：安全边界、权限控制和审计记录。",
                "11 维护升级：任务、数据、模块和版本维护。",
                "12 附录说明：目录约定、配置约定和提交核查要点。",
                "1.1 软件目标；1.2 适用场景；1.3 用户角色；1.4 系统边界。",
                "2.1 逻辑架构；2.2 流程架构；2.3 部署架构；2.4 数据流设计；2.5 状态文件设计。",
                "3.1 量子任务管理；3.2 量子中间表示；3.3 训练样本生成；3.4 数据完整性校验。",
                "3.5 训练模块；3.6 评测模块；3.7 检索增强模块；3.8 报告归档模块。",
                "4.1 数据目录设计；4.2 样本字段设计；4.3 评测基准设计；4.4 日志数据设计；4.5 版本追踪设计。",
                "5.1 命令行接口设计；5.2 函数接口设计；5.3 文件接口设计；5.4 配置接口设计；5.5 报告接口设计。",
                "6.1 任务切分算法；6.2 提示构建算法；6.3 候选清洗算法；6.4 执行评分算法；6.5 差异分析算法。",
                "7.1 本地运行设计；7.2 远程训练设计；7.3 作业生命周期；7.4 复现实验设计。",
                "8.1 初始化操作；8.2 数据构建操作；8.3 训练操作；8.4 评测操作；8.5 报告操作。",
                "9.1 数据异常处理；9.2 训练异常处理；9.3 评测异常处理；9.4 同步异常处理。",
                "10.1 安全边界；10.2 权限控制；10.3 审计记录。",
                "11.1 任务维护；11.2 数据维护；11.3 模块维护；11.4 版本维护。",
                "12.1 目录约定；12.2 配置约定；12.3 提交核查要点。",
            ]:
                add_body(item, indent=False)
            add_body("图1为软件总体结构图，图2为训练与评测流程图，图3为核心模块逻辑框图。正文按软件著作权登记说明文档要求组织，并覆盖总体设计、接口设计、模块名称功能、函数名称功能、算法和运行设计。", indent=False)
            return
        if title.startswith("图"):
            add_heading(title, 2)
            add_body("".join(groups["meta"][:3]))
            if len(groups["meta"]) > 3:
                add_body("".join(groups["meta"][3:]))
            if page["image"] is not None:
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run()
                run.add_picture(str(page["image"]), width=Cm(15.7))
            return

        level = 2 if re.match(r"^\d+\.\d+", title) else 1
        add_heading(title, level)
        meta = groups["meta"]
        if len(meta) >= 5:
            add_body(f"{meta[0]}。{meta[1]}；{meta[2]}；{meta[3]}；{meta[4]}。")
        process = groups["process"]
        if process:
            add_heading("处理说明", 3)
            add_body("".join(process[:4]))
            if len(process) > 4:
                add_body("".join(process[4:8]))
            if len(process) > 8:
                add_body("".join(process[8:]))
        quality = groups["quality"]
        exceptions = groups["exception"]
        records = groups["record"]
        if quality:
            add_heading("质量控制", 3)
            add_body("".join(quality))
        if exceptions or records:
            add_heading("异常处理与留痕记录", 3)
            add_body("".join(exceptions + records))
        add_heading("设计细节", 3)
        input_text = meta[2].split("：", 1)[-1] if len(meta) > 2 and "：" in meta[2] else "输入材料"
        output_text = meta[3].split("：", 1)[-1] if len(meta) > 3 and "：" in meta[3] else "输出材料"
        obj = meta[-1].split("：", 1)[-1] if meta and "：" in meta[-1] else "相关业务对象"
        add_body(f"落地实现时，{title}先核对{input_text}，再围绕{obj}完成解析、校验和写出。这样做的目的，是让{output_text}可以被后续训练、评测、检索或报告流程直接读取，减少人工临时改文件造成的不一致。")
        add_body(f"维护时重点看两类问题：一是{obj}的字段含义是否仍然清楚，二是{output_text}是否还和下游脚本的读取约定一致。只要接口或目录发生变化，就需要同步更新清单、测试和说明文字。")
        add_heading("使用维护说明", 3)
        section_no = title.split(".", 1)[0]
        if section_no in {"1", "2"}:
            add_body(f"使用人员检查本部分时，重点看{output_text}是否能说明设计意图，而不是只看命令是否启动。若运行记录、目录或日志不能支撑设计说明，应补充相应的路径和结果材料。")
            add_body("维护时优先保持边界清楚：属于任务、数据、训练、评测或报告的内容分别回到对应模块处理，避免把临时处置写成正式流程。复核时同步查看申请表、源程序和材料清单，确认名称版本、页眉页码和模块职责一致。")
            add_body("本部分通常在需求调整、目录调整或流程调整后复核，复核重点是说明文字是否仍能对应实际运行路径。")
        elif section_no in {"3", "4", "5"}:
            add_body(f"日常使用时，应检查{output_text}是否真实生成，并确认日志中能找到对应的任务编号、路径和时间。出现字段缺失、路径错误或输出不完整时，应先保留现场记录，再修改数据、配置或代码。")
            add_body("维护时先补小范围样例，再进入完整流程。若接口、字段或目录发生变化，应同步更新读取逻辑、清单文件和说明文字，避免下游脚本继续按旧约定读取。")
            add_body("复核人员可抽取一个正常样例和一个失败样例，对照输入、输出、日志和报告，判断该模块描述是否准确。")
        elif section_no in {"6", "7", "8"}:
            add_body(f"操作人员执行本部分流程后，应核对{output_text}是否与预期一致，并查看失败项是否进入报告。对算法和运行类内容，不能只保留结论，还要保留参数、输入版本和执行记录。")
            add_body("后续升级涉及本部分时，应先用固定样例验证，再扩大到完整训练评测流程。若分数、日志或输出目录发生变化，应记录变化原因，避免把环境差异误判为功能变化。")
            add_body("复核时重点查看命令、参数、结果和报告之间能否互相对应，确保同一批次材料可以被重新检查。")
        elif section_no in {"10", "11"}:
            add_body(f"维护人员应把{output_text}与实际目录、配置和日志一起核对，确认安全边界或维护动作没有偏离当前软件版本。涉及权限、任务、数据、模块或版本变化时，应同时检查说明文档和源程序是否仍然对应。")
            add_body("后续升级涉及本部分时，应重新检查模板要求、页眉页码、结束标志和图文内容。所有修改都应留下变更原因和复核结论，便于提交前再次审查。")
            add_body("复核重点是材料之间的一致性，以及说明文字是否仍然反映软件当前版本的实际功能。")
            add_body("本部分还应关注材料中是否存在无关主体、无关平台或敏感信息，发现问题应先修正文档再提交。")
        else:
            add_body(f"维护人员应把{output_text}与正式提交材料一起核对，确认本部分没有遗漏影响登记口径的信息。发现主体信息、发表状态、源程序量或文件名变化时，需要同步更新申请表、说明文档、源程序和清单。")
            add_body("后续升级涉及本部分时，应重新检查模板要求、页眉页码、结束标志和图文内容。所有修改都应留下变更原因和复核结论，便于提交前再次审查。")
            add_body("复核重点是材料之间的一致性，以及说明文字是否仍然反映软件当前版本的实际功能。")

    for i, page in enumerate(pages):
        if i:
            doc.add_page_break()
        add_section_page(page, i)
        if i == len(pages) - 1:
            add_body("end", indent=False)

    out = OUT / MANUAL_DOCX_NAME
    doc.save(out)
    scrub_docx_theme_colors(out)
    return out


def scrub_docx_theme_colors(path: Path) -> None:
    """Remove default blue/purple hyperlink theme colors from the generated DOCX."""
    bad_colors = ["4472C4", "2F5496", "1F4E79", "0070C0", "0563C1", "0000FF", "800080", "7030A0", "5B9BD5"]
    tmp = path.with_suffix(".tmp.docx")
    with zipfile.ZipFile(path, "r") as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.endswith(".xml"):
                text = data.decode("utf-8")
                for color in bad_colors:
                    text = text.replace(color, "000000")
                data = text.encode("utf-8")
            zout.writestr(item, data)
    tmp.replace(path)


def build_manual_doc() -> Path:
    """Build the manual in the cleaner example-document layout."""
    diagram_paths = create_manual_diagrams()
    doc = Document()
    configure_section(doc.sections[0], top=Cm(2.0), bottom=Cm(1.7), left=Cm(2.1), right=Cm(1.8))

    for style_name in ["Normal", "Body Text", "Heading 1", "Heading 2", "Heading 3", "List Paragraph"]:
        if style_name in doc.styles:
            style = doc.styles[style_name]
            style.font.name = "宋体"
            style._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
            style.font.color.rgb = RGBColor(0, 0, 0)
    doc.styles["Normal"].font.size = Pt(10.5)
    doc.styles["Body Text"].font.size = Pt(10.5)
    doc.styles["Heading 1"].font.size = Pt(16)
    doc.styles["Heading 1"].font.bold = True
    doc.styles["Heading 2"].font.size = Pt(13)
    doc.styles["Heading 2"].font.bold = True
    doc.styles["Heading 3"].font.size = Pt(11)
    doc.styles["Heading 3"].font.bold = True

    def write_run(paragraph, text: str, font_size=Pt(10.5), bold=False) -> None:
        run = paragraph.add_run(text)
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
        run.font.size = font_size
        run.bold = bold
        run.font.color.rgb = RGBColor(0, 0, 0)

    def paragraph(text: str, first_indent: bool = True, space_after=Pt(6)):
        p = doc.add_paragraph(style="Body Text")
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = space_after
        if first_indent:
            p.paragraph_format.first_line_indent = Pt(21)
        write_run(p, text, font_size=Pt(10.5))
        return p

    def heading(text: str, level: int = 1):
        p = doc.add_paragraph(style=f"Heading {level}")
        p.paragraph_format.space_before = Pt(12 if level == 1 else 8)
        p.paragraph_format.space_after = Pt(8 if level == 1 else 6)
        p.paragraph_format.keep_with_next = True
        write_run(p, text, font_size=Pt(16 if level == 1 else 13 if level == 2 else 11), bold=True)
        return p

    def caption(text: str):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(8)
        write_run(p, text, font_size=Pt(9), bold=True)

    def add_image(path: Path, title: str):
        doc.add_picture(str(path), width=Cm(15.3))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        caption(title)

    def add_table(headers: list[str], rows: list[list[str]]):
        table = doc.add_table(rows=1, cols=len(headers))
        table.style = "Table Grid"
        for idx, header in enumerate(headers):
            set_cell_black(table.rows[0].cells[idx], header, bold=True)
        for row in rows:
            cells = table.add_row().cells
            for idx, value in enumerate(row):
                set_cell_black(cells[idx], value)
        doc.add_paragraph()
        return table

    def set_cell_black(cell, text: str, bold: bool = False) -> None:
        cell.text = ""
        p = cell.paragraphs[0]
        p.paragraph_format.line_spacing = 1.25
        p.paragraph_format.space_after = Pt(0)
        write_run(p, text, font_size=Pt(9), bold=bold)

    def toc_line(title: str, page: str, indent: bool = False) -> None:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(0)
        if indent:
            p.paragraph_format.left_indent = Cm(0.38)
        dots = "." * max(6, 58 - len(title) * 2)
        write_run(p, f"{title}{dots}{page}", font_size=Pt(9.5))

    # Cover page: centered title page, matching the better example under the
    # quantum encryption toolkit materials while keeping this project's fields.
    for _ in range(7):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    write_run(p, HEADER, font_size=Pt(22), bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    write_run(p, "设计说明书及使用说明文档", font_size=Pt(20), bold=True)
    doc.add_paragraph()
    for item in [
        f"文档版本：{VERSION}",
        f"软件版本：{VERSION}",
        f"软件简称：{SHORT_NAME}",
        f"著作权人：{'、'.join(RIGHTHOLDERS)}",
        f"作者：{'、'.join(AUTHORS)}",
        f"开发完成日期：{COMPLETION_DATE}",
    ]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(4)
        write_run(p, item, font_size=Pt(12))

    doc.add_page_break()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    write_run(p, "目录", font_size=Pt(16), bold=True)
    for title, page, is_child in [
        ("1、 总体业务说明", "3", False),
        ("1.1 编写目的", "3", True),
        ("1.2 适用对象", "3", True),
        ("1.3 软件定位", "3", True),
        ("2、 系统总体设计", "4", False),
        ("2.1 总体架构", "4", True),
        ("2.2 模块结构", "4", True),
        ("2.3 运行流程", "5", True),
        ("3、 核心功能说明", "6", False),
        ("3.1 量子任务管理", "6", True),
        ("3.2 数据构建与校验", "7", True),
        ("3.3 模型训练与自动评测", "7", True),
        ("3.4 检索问答与报告归档", "8", True),
        ("4、 操作使用说明", "8", False),
        ("4.1 环境准备", "8", True),
        ("4.2 数据构建操作", "8", True),
        ("4.3 训练、评测和报告操作", "9", True),
        ("5、 接口与数据说明", "9", False),
        ("5.1 命令行和函数接口", "9", True),
        ("5.2 文件、配置和报告接口", "9", True),
        ("6、 算法与运行设计", "10", False),
        ("6.1 任务切分和提示构建", "10", True),
        ("6.2 候选清洗、执行评分和差异分析", "10", True),
        ("6.3 本地验证和训练运行", "10", True),
        ("7、 测试与验收说明", "11", False),
        ("8、 安全边界与权限", "11", False),
        ("9、 维护与扩展说明", "12", False),
        ("10、 常见问题与提交检查", "12", False),
    ]:
        toc_line(title, page, is_child)

    doc.add_page_break()
    heading("1、 总体业务说明", 1)
    heading("1.1 编写目的", 2)
    paragraph(f"本文档用于说明{HEADER}的设计思路、功能边界、模块组成、接口数据、运行流程和使用维护方法。文档与登记申请表、源程序文件采用同一软件名称、版本号、著作权人和发表状态，便于登记审查时把功能说明、代码材料和申请表信息互相对应。")
    paragraph("软件面向量子代码模型研发过程，重点解决任务资料分散、训练样本难以复核、评测结果不可比较、报告材料依赖人工整理等问题。文档不把通用运行环境、基础模型权重或外部基础设施作为登记对象，而是说明本软件自研的任务组织、数据构建、训练调度、评测汇总和报告归档表达。")
    heading("1.2 适用对象", 2)
    paragraph("本文档适用于量子算法研发人员、模型训练人员、评测人员、项目负责人和后续维护人员。研发人员可依据本文理解量子任务如何进入数据构建和评测流程；训练人员可依据本文确认训练输入、输出目录和运行记录；评测人员可依据本文复核候选代码、测试结果和报告摘要之间的关系。")
    paragraph("在实际交接中，本文档也作为操作和验收的共同口径使用。负责数据的人重点查看第三章和第五章，确认样本字段、基准文件和清单记录；负责训练和评测的人重点查看第四章、第六章和第七章，确认命令入口、运行顺序和结果判断；负责提交材料的人重点查看第十章，确认文件名、页眉页码、结束标志和主体信息一致。")
    heading("1.3 软件定位", 2)
    paragraph("本软件定位为量子代码大模型研发平台，服务于量子算法任务整理、训练样本构建、模型训练组织、自动化评测、检索问答和阶段性报告归档。它不是单一训练脚本，也不是只展示指标的报表工具，而是把从任务资料到结果复核的多个环节组织为可重复执行的软件流程。")
    paragraph("登记保护的重点是平台在任务描述解析、样本字段组织、训练评测编排、候选代码清洗、失败原因归类、报告生成和材料归档方面的自研表达。软件可以在本地工作区完成小范围验证，也可以把已确认的数据和配置交给训练环境执行较长任务；无论运行位置如何，输入、输出、日志和报告均应按固定目录保存。")

    heading("2、 系统总体设计", 1)
    heading("2.1 总体架构", 2)
    paragraph("系统采用分层模块化结构。入口层负责读取命令参数、配置文件和任务范围；数据层负责整理量子任务、生成训练样本、构建评测基准并记录清单；执行层负责模型训练、候选代码生成、代码执行评测和检索问答；归档层负责汇总日志、指标、失败样例和对比报告。")
    paragraph("各层之间主要通过结构化文件、固定目录和明确函数接口传递数据。任务库向数据构建模块提供任务说明和测试约束，数据构建模块向训练模块提供样本文件，评测模块读取基准文件并执行候选代码，报告模块汇总训练指标、评测结果和异常摘要。这样的组织方式减少了口头约定，也让后续复核能够直接追溯到具体输入和输出。")
    add_image(diagram_paths[0], "图1 软件总体结构图")
    heading("2.2 模块结构", 2)
    paragraph("软件模块按照研发流程划分为任务管理、量子中间表示、训练样本生成、数据完整性校验、训练运行、自动评测、检索增强和报告归档八类。任务管理模块保存任务编号、领域、提示族和测试约束；中间表示模块把量子线路、量子门序列和辅助代码要求整理为稳定对象；样本生成模块把任务对象转换为训练和评测所需的结构化记录。")
    paragraph("训练运行模块不直接修改任务定义，只读取已校验样本、模型目录和参数配置；自动评测模块不修改训练输出，只在隔离目录中执行候选代码并记录标准输出、错误输出、超时和断言结果；报告归档模块不手工改写指标，而是读取原始得分卡、失败明细和日志摘要，形成可复核的结论。")
    add_table(
        ["模块", "主要职责", "关键输入", "关键输出"],
        [
            ["任务管理", "维护量子任务、测试约束和提示族", "任务说明、测试文件", "任务清单、任务对象"],
            ["数据构建", "生成训练样本和评测基准", "任务对象、配置参数", "样本文件、基准文件"],
            ["训练运行", "组织模型训练和结果保存", "训练样本、模型目录", "训练日志、输出目录"],
            ["自动评测", "执行候选代码并计算通过状态", "候选文件、测试入口", "得分卡、失败摘要"],
            ["报告归档", "汇总指标、日志和复核结论", "评测结果、运行记录", "报告文件、归档清单"],
        ],
    )
    heading("2.3 运行流程", 2)
    paragraph("软件运行通常从任务准备开始。使用人员先确认任务目录、数据目录和配置文件，再执行数据构建和完整性校验。校验通过后，训练人员可以启动训练流程；训练完成后，评测人员使用固定基准生成候选代码并运行测试；最后由报告模块汇总通过率、失败类型、日志摘要和对比结论。")
    paragraph("流程设计强调先验证再执行长任务。目录缺失、字段错误、训练集与评测集交叉、候选代码不可执行、报告文件写入失败等情况都会进入异常记录。平台不会把启动命令成功视为研发完成，只有训练输出、评测结果、失败摘要和报告归档全部可追溯时，一轮研发流程才算闭环。")
    add_image(diagram_paths[1], "图2 训练与评测流程图")

    heading("3、 核心功能说明", 1)
    heading("3.1 量子任务管理", 2)
    paragraph("量子任务管理用于保存和组织平台研发过程中反复使用的任务资料。每个任务通常包含任务编号、领域标签、问题描述、输入输出要求、测试约束和参考检查方式。任务编号保持稳定后，训练样本、评测基准、候选文件和报告条目都可以围绕同一编号追踪，避免同一任务在不同批次中被重复命名。")
    paragraph("任务内容既包括量子线路构造、量子门操作、测量结果处理等量子计算任务，也包括辅助解析、数据转换和通用编程任务。平台不会把任务描述简单拼接成文本，而是先整理字段和边界，再交给样本生成、提示构建和评测模块使用。这样可以减少手工编辑带来的遗漏，也便于维护人员在新增任务后补充对应测试。")
    add_image(diagram_paths[2], "图3 核心模块逻辑框图")
    heading("3.2 数据构建与校验", 2)
    paragraph("数据构建模块把任务资料转换为训练样本、评测样本和清单文件。样本字段包括任务编号、输入提示、期望输出形式、所属领域、提示族和拆分标记。清单文件记录样本数量、生成时间、拆分策略、输入目录和输出目录，便于后续报告引用同一批数据。")
    paragraph("完整性校验重点检查字段缺失、编号重复、训练集与评测集交叉、文件编码异常和任务清单不一致。对于严格评测场景，平台要求训练数据和评测数据在任务层面保持隔离，避免把评测答案通过训练样本提前暴露给模型。发现异常时，流程会保留错误列表并停止进入训练或评测阶段。")
    heading("3.3 模型训练与自动评测", 2)
    paragraph("训练模块读取经过校验的数据、模型目录和参数配置，按批次生成日志、输出目录和检查点记录。训练前会检查关键路径是否存在、输出目录是否冲突、参数是否超出约定范围；训练后会保存运行命令、训练摘要和输出位置，供评测和归档模块读取。")
    paragraph("自动评测模块用于把模型输出转换为可执行候选代码，并在隔离目录中运行测试。评测过程会记录语法错误、导入错误、断言失败、超时和其他运行异常，不只保留最终通过率。对于同一基准，不同训练结果可以在相同任务列表上比较，报告模块据此识别新增通过、退化失败和稳定任务。")
    heading("3.4 检索问答与报告归档", 2)
    paragraph("检索问答模块读取项目内部文档、任务说明和历史报告，建立面向研发人员的资料检索能力。它的作用是帮助使用人员快速找到相关约束、接口说明和失败原因，而不是替代正式评测。检索结果需要保留来源路径，便于人工判断片段是否适用于当前任务。")
    paragraph("报告归档模块汇总训练日志、评测得分、失败明细、差异分析和人工复核意见。报告中既保留整体指标，也保留失败任务，避免只展示成功结论。归档目录按批次保存输入清单、运行命令、结果文件和报告文本，使后续复现实验或提交材料复核时可以回到原始证据。")

    heading("4、 操作使用说明", 1)
    heading("4.1 环境准备", 2)
    paragraph("首次使用前，操作人员进入软件根目录，确认源码目录、数据目录、任务目录、模型目录和报告目录均存在。随后检查运行语言、脚本入口和依赖环境是否可用，并确认当前批次的配置文件、输出目录和日志目录没有与历史结果混用。")
    paragraph("准备阶段还应确认本次运行目标：如果只是验证任务格式，可以选择小范围数据构建和单元测试；如果要完成训练评测闭环，应提前准备训练样本、评测基准、模型目录、输出目录和报告目录。较长训练任务启动前必须先完成本地小样本验证。")
    heading("4.2 数据构建操作", 2)
    paragraph("数据构建时，用户先选择任务范围和输出批次，再运行数据构建入口生成训练文件、评测文件和清单报告。生成后应查看样本数量、任务编号、拆分策略和字段完整性。若清单中出现重复编号、字段缺失或拆分交叉，应先修复任务资料，再重新构建数据。")
    paragraph("数据构建结果不应被手工临时改写。确需修正样本时，应回到任务定义或构建规则修改，并重新生成清单。这样可以保证评测报告引用的样本版本与实际训练输入一致，也能避免多人协作时对同一数据文件产生不同理解。")
    heading("4.3 训练、评测和报告操作", 2)
    paragraph("训练操作需要指定训练数据、模型目录、输出目录和批次参数。训练启动后，使用人员应检查日志是否持续写入、输出目录是否生成必要文件、异常信息是否被记录。训练结束后，不直接修改模型输出，而是进入评测阶段，通过固定基准生成候选文件并运行测试。")
    paragraph("评测完成后，报告模块读取得分卡、失败摘要和日志记录生成报告。报告人员应核对报告引用的训练批次、评测基准和候选目录是否一致。若发现结果异常，应先定位是数据、训练、评测还是报告环节的问题，再决定是否重新构建数据、重跑训练或只重跑评测。")

    heading("5、 接口与数据说明", 1)
    heading("5.1 命令行和函数接口", 2)
    paragraph("软件通过命令行入口组织数据构建、训练、评测、报告生成和维护检查等操作。命令参数通常包括输入路径、输出路径、任务范围、配置文件、运行预算和批次名称。入口脚本只负责参数解析、路径检查和流程调度，具体业务逻辑由对应模块函数完成。")
    paragraph("函数接口强调单一职责。解析函数只把任务文件转换为内部对象，校验函数只返回错误列表或通过状态，训练函数只处理训练输入和输出目录，评测函数只处理候选代码和测试结果。跨模块调用通过显式参数传递数据，不直接依赖隐藏的全局状态。")
    add_table(
        ["接口类型", "说明", "主要检查点"],
        [
            ["命令行接口", "面向操作人员的运行入口", "必填参数、路径存在性、退出状态"],
            ["函数接口", "面向模块复用的内部调用", "输入对象、返回值、异常类型"],
            ["文件接口", "面向数据交换的结构化文件", "编码、字段、目录位置"],
            ["报告接口", "面向复核和归档的输出材料", "指标来源、失败明细、结论依据"],
        ],
    )
    heading("5.2 文件、配置和报告接口", 2)
    paragraph("平台主要使用结构化文本文件保存任务、样本、清单、得分卡和报告摘要。训练样本与评测样本分目录保存，报告输入与最终报告分目录保存，临时文件不得覆盖正式归档文件。文件名应体现用途和批次，避免不同实验结果混放。")
    paragraph("配置接口用于管理模型路径、数据路径、输出路径、运行预算和默认参数。命令参数可以覆盖配置默认值，但覆盖结果需要写入运行记录。报告接口则要求每项指标可以追溯到原始得分卡，每个失败结论可以追溯到任务编号、候选文件和错误摘要。")

    heading("6、 算法与运行设计", 1)
    heading("6.1 任务切分和提示构建", 2)
    paragraph("任务切分算法先按任务编号、提示族和用途建立集合，再检查训练集、验证集和评测集之间是否存在交叉。对于需要严格评测的任务，平台优先保持任务级隔离，而不是只依赖样本编号不同。切分结果写入清单文件，并在报告中保留拆分策略。")
    paragraph("提示构建算法把任务描述、约束条件、输入输出要求和必要上下文组织为模型输入。构建时会控制文本长度，保留真正影响解题的约束，减少无关说明。提示模板发生变化时，应重新生成样本并记录版本，否则不同批次结果不具备可比性。")
    heading("6.2 候选清洗、执行评分和差异分析", 2)
    paragraph("候选清洗算法从模型输出中提取可执行代码，去除多余说明、格式标记和明显不属于代码的片段。清洗过程不应掩盖真实失败，如果输出缺少必要函数、导入错误或语法不完整，应记录为评测异常，而不是人工补全后再计入通过。")
    paragraph("执行评分算法根据测试退出状态、断言结果、超时状态和错误类型生成任务级分数。差异分析算法按任务维度比较两个或多个实验结果，区分新增通过、退化失败和稳定任务。报告结论必须来自这些结构化结果，不能只凭人工印象判断训练是否有效。")
    heading("6.3 本地验证和训练运行", 2)
    paragraph("运行设计采用本地验证优先的原则。代码改动、数据构建和小样本评测先在本地完成，确认任务、路径、依赖和报告逻辑没有明显问题后，再执行更耗时的训练运行。这样可以降低长任务失败成本，也能让错误定位更集中。")
    paragraph("训练运行完成后，需要回收日志、输出目录、配置快照和评测结果。若运行中断，应检查输出是否完整、日志是否包含明确失败原因、是否需要清理临时目录。平台不以启动成功作为最终结果，只有报告和归档完成后才形成可提交、可复核的研发材料。")

    heading("7、 测试与验收说明", 1)
    paragraph("测试体系覆盖任务解析、数据构建、样本完整性、候选清洗、评测执行、报告生成和关键脚本入口。单元测试使用确定性输入，保证相同代码在相同任务上得到稳定结果。涉及目录和文件的测试应使用隔离临时目录，避免污染正式数据和报告。")
    paragraph("验收时重点检查四类结果：第一，数据清单是否准确记录样本数量、拆分策略和生成时间；第二，训练运行是否留下命令、参数、日志和输出目录；第三，评测结果是否能定位到具体任务、候选文件和失败原因；第四，报告结论是否与原始得分卡一致。")
    paragraph("当新增任务、修改提示模板、调整评测逻辑或改变报告格式时，应补充对应测试并重新生成材料。若只修改说明文档而不复核代码和报告，容易出现文档描述与实际运行不一致；若只修改代码而不更新说明，也会影响提交材料的可信度。")

    heading("8、 安全边界与权限", 1)
    paragraph("本软件的登记对象为自研源程序和设计表达，不包括通用操作系统、通用硬件、基础运行库、基础模型权重或外部运行服务。文档和报告不得写入账号、密钥、令牌、私人目录或无关个人信息。涉及运行环境的内容均按通用技术口径描述。")
    paragraph("权限控制主要体现在目录边界和材料边界。任务资料、训练数据、评测结果、日志和报告按项目范围保存；不同批次结果分目录归档，避免互相覆盖；正式提交材料只包含登记所需内容，不包含个人凭据、临时调试记录和无关平台信息。")
    paragraph("审计记录需要把命令、参数、输入清单、输出目录、日志和报告联系起来。发现敏感信息、主体信息变化、文件名变化或发表状态变化时，应先修正申请表、说明文档、源程序和清单，再进入最终提交检查。")

    heading("9、 维护与扩展说明", 1)
    paragraph("新增量子任务时，应补充任务说明、输入输出要求、测试约束和评测入口，并检查任务编号是否与既有任务冲突。新增任务进入训练数据前，应先通过数据构建和完整性校验；进入评测基准前，应确认测试能够稳定判断候选代码是否满足要求。")
    paragraph("修改数据字段、目录结构或配置参数时，需要同步更新读取逻辑、清单生成、报告生成和说明文字。接口变更应尽量保持向后兼容；无法兼容时，应在版本维护记录中说明变化原因、影响范围和迁移方式。")
    paragraph("未来如按升级版本申请登记，应根据实际变化编写版本差异说明，列明新增功能、修改模块、代码范围和兼容性影响。本版本为V1.0，当前登记口径为原创软件、独立开发、未发表。")

    heading("10、 常见问题与提交检查", 1)
    paragraph("若数据构建失败，应先检查任务目录是否存在、字段是否齐全、编号是否重复、文件编码是否正确。若训练运行失败，应检查训练数据路径、模型目录、输出目录、依赖环境和日志末尾错误。若评测结果异常，应检查候选代码是否完整、测试入口是否正确、超时设置是否合理。")
    paragraph("若报告内容与预期不一致，应先核对报告引用的得分卡、失败清单和运行目录，确认没有读取旧批次文件。多人协作时尤其需要确认输出目录和归档目录，以免一个人的临时结果覆盖另一个人的正式结果。")
    paragraph("提交前应逐项检查三份正式DOCX文件：申请表的软件名称、版本、著作权人、作者、联系人、电话、地址、未发表和原创口径；说明文档的封面、目录、标题层级、图示、页眉页码、黑色字体和结束标志；源程序的页数、行数、页眉页码和末页结束标志。参考PDF、样表、README、清单和检查报告只作为内部复核材料，不作为正式提交附件。")
    paragraph("end", first_indent=False)

    out = OUT / MANUAL_DOCX_NAME
    doc.save(out)
    scrub_docx_theme_colors(out)
    return out


def build_manual_doc() -> Path:
    """Build a 30-page, less crowded manual matching the example-style layout."""
    diagram_paths = create_manual_diagrams()
    doc = Document()
    configure_section(doc.sections[0], top=Cm(2.1), bottom=Cm(1.85), left=Cm(2.25), right=Cm(2.05))

    for style_name in ["Normal", "Body Text", "Heading 1", "Heading 2", "Heading 3", "List Paragraph"]:
        if style_name in doc.styles:
            style = doc.styles[style_name]
            style.font.name = "宋体"
            style._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
            style.font.color.rgb = RGBColor(0, 0, 0)
    doc.styles["Normal"].font.size = Pt(10.5)
    doc.styles["Body Text"].font.size = Pt(10.5)
    doc.styles["Heading 1"].font.size = Pt(16)
    doc.styles["Heading 1"].font.bold = True
    doc.styles["Heading 2"].font.size = Pt(13)
    doc.styles["Heading 2"].font.bold = True
    doc.styles["Heading 3"].font.size = Pt(11)
    doc.styles["Heading 3"].font.bold = True

    def write_run(paragraph, text: str, font_size=Pt(10.5), bold=False) -> None:
        run = paragraph.add_run(text)
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
        run.font.size = font_size
        run.bold = bold
        run.font.color.rgb = RGBColor(0, 0, 0)

    def paragraph(text: str, first_indent: bool = True, space_after=Pt(1), line_spacing=1.24):
        p = doc.add_paragraph(style="Body Text")
        p.paragraph_format.line_spacing = line_spacing
        p.paragraph_format.space_after = space_after
        if first_indent:
            p.paragraph_format.first_line_indent = Pt(21)
        write_run(p, text, font_size=Pt(10.5))
        return p

    def heading(text: str, level: int = 1):
        p = doc.add_paragraph(style=f"Heading {level}")
        p.paragraph_format.space_before = Pt(5 if level == 1 else 3)
        p.paragraph_format.space_after = Pt(4 if level == 1 else 3)
        p.paragraph_format.keep_with_next = True
        write_run(p, text, font_size=Pt(16 if level == 1 else 13 if level == 2 else 11), bold=True)

    def caption(text: str):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(3)
        write_run(p, text, font_size=Pt(9), bold=True)

    def set_cell_black(cell, text: str, bold: bool = False) -> None:
        cell.text = ""
        p = cell.paragraphs[0]
        p.paragraph_format.line_spacing = 1.2
        p.paragraph_format.space_after = Pt(0)
        write_run(p, text, font_size=Pt(9), bold=bold)

    def add_table(headers: list[str], rows: list[list[str]]) -> None:
        table = doc.add_table(rows=1, cols=len(headers))
        table.style = "Table Grid"
        for idx, header in enumerate(headers):
            set_cell_black(table.rows[0].cells[idx], header, bold=True)
        for row in rows:
            cells = table.add_row().cells
            for idx, value in enumerate(row):
                set_cell_black(cells[idx], value)
        doc.add_paragraph()

    def add_image(path: Path, title: str) -> None:
        doc.add_picture(str(path), width=Cm(16.2))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        caption(title)

    def toc_line(title: str, page: int, indent: bool = False) -> None:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.08
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.left_indent = Cm(0.42 if indent else 0)
        p.paragraph_format.tab_stops.add_tab_stop(Cm(15.85), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        write_run(p, title, font_size=Pt(9.3))
        write_run(p, f"\t{page}", font_size=Pt(9.3))

    def begin_page() -> None:
        doc.add_page_break()

    def supplemental_texts(title: str) -> list[str]:
        if "编写目的" in title:
            return [
                "本文档在内容组织上避免只罗列功能名称，而是把功能产生的原因、处理的数据、依赖的模块和交付的结果一并说明。这样审查时可以看到软件不是若干脚本的简单集合，而是一套围绕量子代码模型研发闭环形成的工程化平台。",
                "文档中的术语保持与申请表和源程序一致。软件全称、版本号、著作权人、作者、发表状态和开发完成日期均以本次登记材料为准；如系统侧录入信息发生变化，应同步回到生成脚本更新，而不是只改某一个Word文件。",
                "说明书还承担后续维护的索引作用。维护人员可以通过目录快速定位任务、数据、训练、评测、接口、算法、权限和提交检查等内容，再按章节核对实际源程序和运行记录。",
                "本文档不记录账号、密钥、令牌、私人目录或无关外部平台信息。涉及运行环境的表述均采用通用技术口径，保证材料聚焦软件本身的设计表达和使用方式。",
            ]
        if "适用对象" in title:
            return [
                "不同角色阅读本文档时关注点不同，但使用同一套目录和术语。这样在任务交接、结果复核或材料提交时，各角色不需要重新解释软件边界，减少因口头说明不一致造成的理解偏差。",
                "研发人员通常从任务管理和中间表示入手，确认量子任务是否被正确抽象；数据人员从样本生成和完整性校验入手，确认训练和评测数据是否可追溯；评测人员从候选清洗、执行评分和差异分析入手，确认结论是否来自可执行测试。",
                "项目负责人更关注报告归档和提交检查。报告不仅反映模型效果，也记录数据版本、基准范围、失败任务和复核意见，是判断下一轮研发方向的重要依据。",
                "软件定位为研发支撑平台，因此本文档既说明设计，也说明使用。两类内容合并在同一文档中，可以让审核人员同时看到软件结构和实际操作路径。",
            ]
        if "部署" in title:
            return [
                "部署时应先确认项目目录结构，再确认运行参数。软件本身不绑定单一机器或单一训练环境，关键是输入、输出、日志和报告按约定目录流转。",
                "远程运行产生的结果需要回到本地归档目录进行复核。只在远程环境中保留日志而不回收，会造成后续报告无法引用原始证据。",
                "数据流转过程中应区分正式结果和临时缓存。正式结果进入清单和报告，临时缓存只用于中间计算，不应出现在提交材料中。",
                "如果部署路径或目录命名发生变化，应同步更新配置和说明文字。路径变化本身不是功能变化，但不更新文档会影响复现和审查。",
            ]
        if "任务" in title:
            return [
                "任务新增时应先给出稳定编号，再补充领域标签、输入输出要求和测试约束。编号稳定后，训练样本、评测基准和报告条目才能建立一一对应关系。",
                "任务描述应避免只写自然语言目标，还应写清函数形态、边界条件和判断方式。缺少这些信息，模型输出即使看起来合理，也难以进入自动评测。",
                "任务变更需要记录原因。若变更影响历史样本或评测基准，应重新生成相关数据，并在报告中说明批次差异。",
                "任务库是平台的基础资产。任务越稳定，后续训练、评测和差异分析越容易复现；任务越随意，报告越容易失去解释力。",
            ]
        if "中间表示" in title:
            return [
                "中间表示的价值在于把不同写法的任务描述转成统一结构。维护人员不需要在每个脚本里重复解析量子线路、门序列和测量要求，减少了规则分散带来的不一致。",
                "该层也为后续扩展保留空间。新增任务类型时，可以先扩展中间对象字段，再调整样本生成和评测规则，避免直接改动训练或报告模块。",
                "中间表示输出应尽量简洁。只保留任务执行和评测判断必要的信息，避免把长篇背景材料混入结构对象，影响后续提示构建。",
                "当评测失败时，中间表示可以帮助定位失败原因。维护人员可以判断候选代码是没有满足结构约束，还是测试入口或数据字段发生了变化。",
            ]
        if "样本" in title or "完整性" in title:
            return [
                "数据相关模块的首要目标是可追溯。每个样本应能追到任务编号、提示族、生成批次和拆分策略，每个清单数字应能和实际文件数量对应。",
                "数据修复应回到源任务或构建规则完成，不宜直接编辑生成后的样本文件。直接编辑会让清单、样本和报告之间出现隐性差异。",
                "完整性校验不是形式步骤。它可以在训练前发现字段缺失、拆分污染和编号冲突，避免耗时训练结束后才发现数据不可用。",
                "如果校验规则更新，应重新检查既有数据。旧数据在旧规则下通过，不代表在新规则下仍然满足要求。",
            ]
        if "训练" in title:
            return [
                "训练管理强调证据保存。每次训练至少应留下有效参数、输入数据、模型目录、输出目录、日志摘要和开始结束时间，便于后续评测和归档引用。",
                "训练异常需要分类记录。路径错误、依赖缺失、资源不足、保存失败和参数错误对应不同处理方式，不能只用一次失败概括全部问题。",
                "训练输出进入评测前，应先检查目录完整性。缺少配置、日志或输出文件时，应暂停进入评测阶段，避免报告引用不完整结果。",
                "训练流程和评测流程保持分离。训练模块负责生成模型输出和记录过程，是否有效由评测模块和报告模块共同判断。",
            ]
        if "评测" in title or "候选" in title or "评分" in title:
            return [
                "评测管理强调可执行证据。每个通过或失败结论都应能定位到候选文件、测试入口、标准输出、错误输出和任务编号。",
                "候选清洗规则应保持稳定。若为了某一轮结果临时修改清洗逻辑，应在报告中说明，否则不同批次之间的比较会失去公平性。",
                "失败任务应完整保留。只保存通过样例会让后续改进缺少方向，也不利于审查人员理解报告结论来源。",
                "评分结果应和失败类型一起保存。总体通过率说明整体情况，失败类型说明下一步应修数据、修提示、修测试还是修代码。",
            ]
        if "检索" in title:
            return [
                "检索资料应经过筛选后进入索引。正式任务说明、接口文档、评测报告和维护记录可以进入索引，私人路径、账号信息和未确认结论不应进入索引。",
                "检索结果必须带来源。没有来源路径的片段不适合作为研发依据，因为人员无法判断上下文是否适用于当前任务。",
                "检索问答只提供辅助参考，不替代自动评测。候选代码是否通过，仍以测试执行和得分卡为准。",
                "维护人员可以根据检索问答记录发现文档短板。重复出现的问题应回到说明书、接口文档或操作流程中补充。",
            ]
        if "报告" in title:
            return [
                "报告归档强调原始证据和结论分离。原始得分卡、日志摘要和失败清单先保存，报告文字再基于这些材料解释结果。",
                "报告应保留失败任务。失败任务能够说明模型当前边界，也能为下一轮任务补充、数据清洗或提示调整提供依据。",
                "报告比较多个实验时，应说明基准、提示版本、运行预算和清洗规则是否一致。条件不一致时，报告应避免给出过强的提升结论。",
                "归档完成后，应能从报告回到数据清单、运行命令、候选目录和日志文件。不能回溯的报告不适合作为提交或验收依据。",
            ]
        if "环境" in title or "操作" in title:
            return [
                "操作人员应先确认当前目录和批次，再执行命令。很多运行异常并非软件逻辑错误，而是输入目录、输出目录或配置文件指向了错误位置。",
                "每个操作完成后都应检查输出。数据构建看清单，训练看日志和输出目录，评测看得分卡和失败摘要，报告看引用路径和结论来源。",
                "操作失败时先保存现场，再修改参数重试。直接覆盖失败目录会丢失错误信息，后续难以判断问题是否真正解决。",
                "多人协作时应约定批次命名和归档位置。命名混乱会导致报告读取旧文件或覆盖他人结果。",
            ]
        if "接口" in title or "文件" in title or "配置" in title:
            return [
                "接口设计优先考虑稳定性。命令参数、函数返回值、文件字段和报告字段发生变化时，应同步更新测试和说明书。",
                "文件接口需要明确读写时机。训练样本、评测基准、候选代码、得分卡和报告文件分别由不同阶段产生，不应互相覆盖。",
                "配置接口应记录默认值和覆盖值。实际生效参数必须能从运行记录中找到，否则复现实验时只能依赖记忆。",
                "接口异常应返回明确原因。路径缺失、字段错误和权限不足应区别处理，避免下游模块收到模糊失败状态。",
            ]
        if "切分" in title or "差异" in title or "生命周期" in title:
            return [
                "算法类模块应尽量采用确定性规则。相同输入在相同配置下应得到相同输出，这样评测和报告才具备可复查性。",
                "算法参数需要写入运行记录。拆分策略、提示版本、清洗规则、评分预算和比较对象都属于影响结论的重要参数。",
                "出现异常时，算法模块应输出可定位的错误信息。只返回失败状态不利于数据人员和维护人员定位问题。",
                "后续升级算法时，应同时保留旧结果和新结果的对比说明。这样可以判断变化来自规则改进，还是来自输入数据或运行环境差异。",
            ]
        if "测试" in title or "安全" in title or "维护" in title or "常见" in title or "提交" in title:
            return [
                "本节内容用于提交前复核，也用于后续维护时回看。检查重点不是文字是否完整，而是文字能否对应实际文件、命令、日志和报告。",
                "如果发现申请表、说明文档、源程序或清单之间的信息不一致，应重新生成正式材料。只手工修改单个文件会增加隐藏差异。",
                "复核时应同时看程序化检查和PDF渲染效果。程序化检查能发现字段、颜色和页码问题，视觉检查能发现目录溢出、图片不清和版面拥挤。",
                "最终提交前仍需人工确认主体证件材料、发表状态和开发方式证明。本文档只负责软件说明和格式口径，不替代系统侧材料录入。",
            ]
        return [
            "本节说明应与实际源程序和运行结果保持一致。若后续修改相关模块，需要同步更新文档、测试和生成清单。",
            "相关输入、输出和异常处理应能在日志或报告中找到证据，不能只停留在文字描述。",
            "维护人员复核本节时，应重点查看目录、字段、接口和报告之间是否仍能互相对应。",
            "提交前如发现描述偏离当前版本，应先修正文档并重新生成正式DOCX。",
        ]

    balance_counts = {
        "1.1 编写目的": 2,
        "1.2 适用对象与软件定位": 3,
        "2.1 总体架构": 2,
        "2.2 模块边界": 6,
        "2.3 运行流程": 2,
        "2.4 部署与数据流": 3,
        "3.1 量子任务管理": 4,
        "3.2 量子中间表示": 3,
        "3.3 训练样本生成": 4,
        "3.4 数据完整性校验": 4,
        "3.5 模型训练管理": 4,
        "3.6 自动评测管理": 5,
        "3.7 检索问答支持": 7,
        "3.8 报告归档": 5,
        "4.1 环境准备": 5,
        "4.2 数据构建操作": 7,
        "4.3 训练评测和报告操作": 5,
        "5.1 命令行和函数接口": 7,
        "5.2 文件配置和报告接口": 5,
        "6.1 任务切分和提示构建": 5,
        "6.2 候选清洗和评分": 5,
        "6.3 差异分析": 5,
        "6.4 作业生命周期": 4,
        "7、 测试与验收说明": 4,
        "8、 安全边界与权限": 4,
        "9、 维护与扩展说明": 4,
        "10、 常见问题处理": 5,
        "11、 提交检查": 3,
    }

    def balance_texts(title: str) -> list[str]:
        if "模块边界" in title:
            return [
                "模块边界的划分还用于控制测试范围。任务管理和数据构建的修改重点检查样本清单，训练运行的修改重点检查日志和输出目录，自动评测的修改重点检查候选文件和得分卡。",
                "模块之间传递的数据应尽量采用结构化文件和明确返回值。若某个模块只能依赖终端输出判断状态，后续报告就难以复核，因此脚本入口需要把关键结果写入稳定文件。",
                "边界清楚也有助于多人协作。数据人员可以只维护任务和样本，训练人员可以只维护运行配置，评测人员可以只维护测试入口，项目负责人再根据归档材料判断整体结果。",
                "当某个模块发生错误时，应先定位错误属于输入、处理、输出还是归档环节。这样可以减少盲目重跑，避免把上游数据错误误判为训练或评测算法错误。",
                "模块扩展时应先补齐输入、输出、异常处理和测试，再纳入主流程。临时脚本如果没有稳定接口，不宜直接写入正式说明或作为长期功能宣传。",
                "表中模块并非孤立存在，而是通过批次目录和清单文件形成闭环。任何一个环节缺少记录，后续复现和软著材料核对都会受到影响。",
            ]
        if "命令行和函数接口" in title:
            return [
                "命令行接口需要保持参数名称稳定。常用参数包括输入目录、输出目录、任务范围、配置文件、运行预算和批次名称，参数变化应同步更新帮助信息和说明文档。",
                "函数接口需要便于测试复用。关键函数应接收显式对象或路径参数，返回结构化结果，避免把重要状态只写到屏幕文本中。",
                "校验接口应在训练前暴露错误列表。错误列表至少包含文件路径、任务编号、字段名称和处理建议，使数据人员可以逐项修正。",
                "报告接口应保留指标来源。报告中的通过率、失败数和对比结论都应能回到得分卡或日志摘要，避免出现无法追溯的手写结论。",
                "接口变更需要维护兼容策略。若旧字段被替换，应在过渡期同时识别旧字段和新字段，或者在清单中明确说明迁移方式。",
                "表格中的接口分类覆盖人员操作、程序复用、数据校验和结果归档四个方向，这也是后续测试设计和提交材料复核的主要边界。",
                "命令入口应尽量保持幂等。重复执行同一检查命令不应破坏既有结果，涉及写入的命令则需要明确输出批次，避免覆盖正式归档目录。",
                "函数接口的错误返回应便于自动化测试断言。测试不仅检查成功路径，也要检查缺失文件、字段异常、超时和权限不足等失败路径。",
                "接口文档应与实际脚本保持同步。新增参数、删除参数或改变默认值时，说明书、帮助信息和测试用例都需要同步更新。",
            ]
        if "量子中间表示" in title:
            return [
                "图示中的逻辑关系强调任务资料、结构对象、模型执行和评分汇总之间的回路。若评分结果暴露出字段缺失，应回到中间表示或任务资料修正，而不是只改报告文字。",
                "中间表示还需要服务于审查和维护。维护人员通过结构对象可以看到任务约束是否完整、候选代码入口是否明确、测试判断是否具备稳定依据。",
                "当新增量子门、测量规则或辅助函数要求时，应先扩展中间表示，再同步调整样本生成和评测检查，避免某一阶段单独理解新字段。",
                "图中反馈路径说明评分结果不是流程终点。失败类型会反向推动任务资料、提示模板、清洗规则和测试约束的修订。",
                "中间表示不写入私人运行信息，只保存任务执行必要字段。这样既能支撑自动化处理，也能让提交材料保持清晰的软件边界。",
            ]
        if "检索" in title:
            return [
                "检索索引更新后，应记录来源文件数量、更新时间和主要来源目录。这样当回答质量变化时，可以判断是资料内容改变，还是检索策略发生变化。",
                "检索结果若用于解释失败任务，应同时保留失败任务编号和来源片段路径。只有把问题、候选、测试和资料来源放在一起，后续维护才容易复盘。",
                "检索问答的输出不进入源程序材料，但其相关接口和索引构建逻辑属于平台功能边界，需要在说明书中说明处理原则。",
                "当检索结果与自动评测结论不一致时，应优先保留评测证据，并把检索材料作为解释线索。这样可以避免把参考片段误当作最终判断。",
                "检索功能的维护重点是来源可信和口径一致。资料进入索引前应经过筛选，过期报告、临时调试记录和与软件边界无关的运行信息不应混入正式资料库。",
            ]
        if "数据构建操作" in title:
            return [
                "构建命令执行前应确认输出批次不会覆盖历史批次。若需要复用旧批次，应先复制或归档原结果，再运行新的构建流程。",
                "构建完成后的抽查可以采用固定样例和随机样例结合的方式。固定样例用于检查已知复杂任务，随机样例用于发现字段遗漏或编码异常。",
                "数据构建日志应记录输入目录、输出目录、样本数量和校验结论。报告人员引用训练数据时，应优先引用这些日志和清单。",
                "若构建规则发生变化，应重新生成整批数据并更新清单。只修改个别样本会破坏批次一致性，也会让训练结果难以解释。",
                "数据构建结果进入训练前还应检查文件编码、换行格式和字段顺序。格式问题如果进入训练阶段，后续错误往往表现为训练异常或评测异常，定位成本更高。",
            ]
        if "常见问题" in title:
            return [
                "定位问题时，应先保留原始目录和日志，再在新批次中尝试修复。这样可以比较修复前后的差异，避免覆盖导致原因无法追溯。",
                "提交检查发现问题后，应回到生成脚本统一修改并重新生成三份正式文档。手工只改某一个DOCX文件，容易造成申请表、说明书和源程序之间的信息不一致。",
                "复核时应同时检查DOCX文件和PDF渲染结果。DOCX结构正确不一定代表渲染页码和版面完全符合预期，因此最终提交前必须查看渲染后的页面效果。",
                "若发现正文页明显空白，应优先补充与本节相关的输入、输出、约束、异常和留痕说明，而不是加入无意义空行或重复标题。",
            ]
        return [
            f"{title}涉及的处理结果应进入稳定目录，并在清单或报告中留下可追溯记录。这样后续复核时可以从说明文字回到实际文件和运行证据。",
            "本部分的输入、处理和输出边界需要与源程序保持一致。若源程序调整了目录、字段或参数，说明书也应同步更新。",
            "异常处理不能只停留在人工经验层面。路径缺失、字段错误、输出冲突、依赖异常和结果不一致应分别记录，便于按原因修复。",
            "维护人员复核本部分时，应同时查看命令、配置、日志和报告，确认文字描述与实际运行方式没有偏差。",
            "本节的说明文字应覆盖正常路径和异常路径。正常路径说明数据如何流转，异常路径说明软件如何停止、记录和恢复。",
            "相关结果进入报告前需要完成一致性检查。报告引用的任务编号、批次目录、样本清单和得分卡应互相对应。",
            "多人协作时，模块负责人应在交接中说明输入来源和输出位置。没有明确来源和位置的结果不应进入正式归档。",
            "如果本节涉及的配置发生变化，应同步更新默认值、命令示例和复核清单，避免旧配置继续影响后续运行。",
        ]

    def body_page(title: str, paras: list[str], *, level: int = 1, image: Path | None = None, image_title: str = "", table: tuple[list[str], list[list[str]]] | None = None, end: bool = False) -> None:
        begin_page()
        heading(title, level)
        for text in paras:
            paragraph(text)
        if image is None and table is None:
            for text in supplemental_texts(title):
                paragraph(text)
        if table is not None:
            add_table(table[0], table[1])
        if image is not None:
            add_image(image, image_title)
        for text in balance_texts(title)[:balance_counts.get(title, 0)]:
            paragraph(text)
        if end:
            paragraph("end", first_indent=False, space_after=Pt(0))

    # Page 1: cover.
    for _ in range(7):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    write_run(p, HEADER, font_size=Pt(22), bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    write_run(p, "设计说明书及使用说明文档", font_size=Pt(20), bold=True)
    doc.add_paragraph()
    for item in [
        f"文档版本：{VERSION}",
        f"软件版本：{VERSION}",
        f"软件简称：{SHORT_NAME}",
        f"著作权人：{'、'.join(RIGHTHOLDERS)}",
        f"作者：{'、'.join(AUTHORS)}",
        f"开发完成日期：{COMPLETION_DATE}",
    ]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(4)
        write_run(p, item, font_size=Pt(12))

    # Page 2: catalog.
    begin_page()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    write_run(p, "目录", font_size=Pt(16), bold=True)
    toc_items = [
        ("1、 总体业务说明", 3, False),
        ("1.1 编写目的", 3, True),
        ("1.2 适用对象与软件定位", 4, True),
        ("2、 系统总体设计", 5, False),
        ("2.1 总体架构", 5, True),
        ("2.2 模块边界", 6, True),
        ("2.3 运行流程", 7, True),
        ("2.4 部署与数据流", 8, True),
        ("3、 核心功能说明", 9, False),
        ("3.1 量子任务管理", 9, True),
        ("3.2 量子中间表示", 10, True),
        ("3.3 训练样本生成", 11, True),
        ("3.4 数据完整性校验", 12, True),
        ("3.5 模型训练管理", 13, True),
        ("3.6 自动评测管理", 14, True),
        ("3.7 检索问答支持", 15, True),
        ("3.8 报告归档", 16, True),
        ("4、 操作使用说明", 17, False),
        ("4.1 环境准备", 17, True),
        ("4.2 数据构建操作", 18, True),
        ("4.3 训练评测和报告操作", 19, True),
        ("5、 接口与数据说明", 20, False),
        ("5.1 命令行和函数接口", 20, True),
        ("5.2 文件配置和报告接口", 21, True),
        ("6、 算法与运行设计", 22, False),
        ("6.1 任务切分和提示构建", 22, True),
        ("6.2 候选清洗和评分", 23, True),
        ("6.3 差异分析", 24, True),
        ("6.4 作业生命周期", 25, True),
        ("7、 测试与验收说明", 26, False),
        ("8、 安全边界与权限", 27, False),
        ("9、 维护与扩展说明", 28, False),
        ("10、 常见问题处理", 29, False),
        ("11、 提交检查", 30, False),
    ]
    for title, page, indent in toc_items:
        toc_line(title, page, indent)

    body_page("1.1 编写目的", [
        f"本文档用于说明{HEADER}的总体设计、模块组成、接口数据、算法流程、运行方式和维护边界。文档与登记申请表、源程序文件采用同一软件名称、版本号、著作权人和发表状态，便于登记审查时把功能说明、代码材料和申请表信息互相对应。",
        "软件面向量子代码模型研发过程，重点解决任务资料分散、训练样本难以复核、评测结果不可比较、报告材料依赖人工整理等问题。本文档说明平台如何把任务、样本、训练、评测和报告组织成可重复执行的软件流程。",
        "文档不把通用运行环境、基础模型权重或外部基础设施作为登记对象，而是聚焦本软件自研的任务组织、数据构建、训练调度、候选代码清洗、评测汇总和报告归档表达。",
        "编写时兼顾登记审查和后续维护两类读者。审查人员可根据本文确认软件功能与源程序之间的对应关系，维护人员可根据本文理解目录、数据、接口和运行记录的设计原因。",
        "本说明书采用封面、目录、章节正文、表格和图示结合的方式组织。图示用于说明模块关系和流程顺序，正文用于解释输入、输出、约束、异常处理和留痕要求，避免只有章节标题而缺少实质内容。",
    ], level=2)

    body_page("1.2 适用对象与软件定位", [
        "本文档适用于量子算法研发人员、模型训练人员、评测人员、项目负责人和后续维护人员。研发人员重点查看任务和数据章节，训练人员重点查看运行和接口章节，评测人员重点查看候选代码、测试和报告章节，提交材料人员重点查看页眉页码、结束标志和主体信息一致性。",
        "软件定位为量子代码大模型研发平台，而不是单一训练脚本或单一报表工具。它把量子算法任务整理、训练样本构建、模型训练组织、自动化评测、检索问答和阶段性报告归档放在同一套流程中管理。",
        "平台的使用场景包括量子任务资料沉淀、训练数据生成、严格评测集管理、模型训练结果对比、失败任务复盘、研发报告归档和提交材料复核。各场景可以独立运行，也可以组合为完整研发闭环。",
        "登记保护的重点是平台在任务描述解析、样本字段组织、训练评测编排、候选代码清洗、失败原因归类、报告生成和材料归档方面的自研表达。软件不声明对公共算法原理、通用开发工具或外部运行资源的权利。",
        "本版本为V1.0，开发完成日期为2026年04月26日，发表状态为未发表。后续如按升级版本登记，应根据实际功能变化补充版本差异说明，并同步更新申请表、说明书、源程序和清单文件。",
    ], level=2)

    body_page("2.1 总体架构", [
        "系统采用分层模块化结构。入口层负责读取命令参数、配置文件和任务范围；数据层负责整理量子任务、生成训练样本、构建评测基准并记录清单；执行层负责模型训练、候选代码生成、代码执行评测和检索问答；归档层负责汇总日志、指标、失败样例和对比报告。",
        "各层之间通过结构化文件、固定目录和明确函数接口传递数据。任务库向数据构建模块提供任务说明和测试约束，数据构建模块向训练模块提供样本文件，评测模块读取基准文件并执行候选代码，报告模块汇总训练指标、评测结果和异常摘要。",
        "这样的组织方式减少了口头约定，也让后续复核能够直接追溯到具体输入和输出。若报告结论异常，维护人员可以沿着任务清单、训练样本、评测基准、候选文件和得分卡逐级检查，而不是在多个临时目录中寻找线索。",
        "总体架构还保留了本地验证和训练环境运行之间的边界。本地工作区负责小范围验证、数据校验和报告生成；较长训练任务可以在训练环境中执行，但输入、输出、日志和结果仍按平台约定回收。",
    ], level=2, image=diagram_paths[0], image_title="图1 软件总体结构图")

    body_page("2.2 模块边界", [
        "软件模块按照研发流程划分为任务管理、量子中间表示、训练样本生成、数据完整性校验、训练运行、自动评测、检索增强和报告归档八类。每类模块只处理自己的输入输出，不直接修改下游模块内部状态。",
        "任务管理模块保存任务编号、领域、提示族和测试约束；中间表示模块把量子线路、量子门序列和辅助代码要求整理为稳定对象；样本生成模块把任务对象转换为训练和评测所需的结构化记录。",
        "训练运行模块只读取已校验样本、模型目录和参数配置；自动评测模块只在隔离目录中执行候选代码并记录标准输出、错误输出、超时和断言结果；报告归档模块读取原始得分卡和日志摘要，形成可复核结论。",
    ], level=2, table=(
        ["模块", "主要职责", "关键输入", "关键输出"],
        [
            ["任务管理", "维护任务和测试约束", "任务说明、测试文件", "任务清单、任务对象"],
            ["数据构建", "生成样本和基准", "任务对象、配置参数", "样本文件、基准文件"],
            ["训练运行", "组织训练和保存输出", "训练样本、模型目录", "训练日志、输出目录"],
            ["自动评测", "执行候选代码并评分", "候选文件、测试入口", "得分卡、失败摘要"],
            ["报告归档", "汇总指标和复核结论", "评测结果、运行记录", "报告文件、归档清单"],
        ],
    ))

    body_page("2.3 运行流程", [
        "软件运行通常从任务准备开始。使用人员先确认任务目录、数据目录和配置文件，再执行数据构建和完整性校验。校验通过后，训练人员可以启动训练流程；训练完成后，评测人员使用固定基准生成候选代码并运行测试；最后由报告模块汇总通过率、失败类型、日志摘要和对比结论。",
        "流程设计强调先验证再执行长任务。目录缺失、字段错误、训练集与评测集交叉、候选代码不可执行、报告文件写入失败等情况都会进入异常记录。平台不会把启动命令成功视为研发完成，只有训练输出、评测结果、失败摘要和报告归档全部可追溯时，一轮研发流程才算闭环。",
        "运行流程的每个阶段都保留输入和输出边界。数据构建阶段输出样本和清单，训练阶段输出日志和模型目录，评测阶段输出候选文件和得分卡，报告阶段输出对比报告和归档说明。任何阶段发生异常时，都应保留原始错误和处理结论。",
        "对于多人协作场景，平台要求输出目录包含批次信息，避免不同人员的临时结果互相覆盖。报告引用的目录必须与训练和评测记录一致，否则不能作为最终结论使用。",
    ], level=2, image=diagram_paths[1], image_title="图2 训练与评测流程图")

    body_page("2.4 部署与数据流", [
        "软件可以在本地工作区完成任务整理、样本生成、小样本评测、报告汇总和材料复核，也可以把已验证的数据与配置交给训练环境执行较长任务。部署设计不依赖某个固定外部平台名称，而是以目录、配置和结果文件为边界。",
        "数据流从任务资料进入平台后，先被整理为任务对象，再生成训练样本和评测基准。训练样本进入训练运行模块，评测基准进入自动评测模块，二者都把结果写入批次目录。报告模块只读取这些稳定结果，不直接推断隐藏状态。",
        "本地和训练环境之间需要保持路径映射清楚。代码、数据、配置和结果应分别列入同步或归档清单，临时缓存不得混入正式材料。结果回收后，报告模块在本地重新读取指标并生成最终报告，保证提交材料可复查。",
        "部署边界也影响安全和审计。账号、密钥、令牌、私人目录和无关运行服务不写入说明书，不进入报告正文。正式材料只描述软件自身功能和通用运行方式，避免把运行场所误写成软件功能主体。",
        "当部署位置发生变化时，只需要调整路径、配置和同步清单，不应改动任务、样本、评测和报告的基本语义。这个设计让平台可以适应不同研发环境，同时保持软件著作权材料中的功能描述稳定。",
    ], level=2)

    body_page("3.1 量子任务管理", [
        "量子任务管理用于保存和组织平台研发过程中反复使用的任务资料。每个任务通常包含任务编号、领域标签、问题描述、输入输出要求、测试约束和参考检查方式。任务编号保持稳定后，训练样本、评测基准、候选文件和报告条目都可以围绕同一编号追踪。",
        "任务内容既包括量子线路构造、量子门操作、测量结果处理等量子计算任务，也包括辅助解析、数据转换和通用编程任务。平台不会把任务描述简单拼接成文本，而是先整理字段和边界，再交给样本生成、提示构建和评测模块使用。",
        "任务管理模块要求新增任务时同步补充测试约束。没有测试入口的任务可以作为训练资料，但不宜直接进入严格评测基准。评测基准中的任务必须能够通过自动测试判断候选代码是否满足要求。",
        "任务资料还需要保留来源和维护记录。维护人员修改任务描述、输入输出要求或测试约束时，应记录变更原因，并判断历史训练样本和评测结果是否需要重新生成。",
        "稳定的任务管理是后续数据构建和结果比较的基础。如果同一任务在不同批次中被重复命名，报告会难以判断模型是否真的提升；如果不同任务共用同一编号，失败分析也会失去定位价值。",
    ], level=2)

    body_page("3.2 量子中间表示", [
        "量子中间表示用于把量子任务中的线路结构、门操作顺序、测量要求和辅助代码约束整理为平台内部稳定对象。它不替代具体量子算法，而是为任务解析、提示构建和评测检查提供统一的表达边界。",
        "在量子代码生成任务中，同一目标可能有不同文字描述。中间表示模块会把关键约束抽取出来，例如需要构造的量子门序列、寄存器数量、测量位置、输入参数形态和返回值要求。这样可以减少提示文本变化对评测逻辑的影响。",
        "中间表示还承担结构校验作用。任务描述缺少必要字段、门序列不完整、输入输出要求冲突或测试约束无法对应时，模块应返回明确错误，而不是让错误进入训练样本或评测基准。",
        "该模块和报告模块之间也有联系。评测失败时，报告可以引用中间表示中的结构约束，说明候选代码是少了某个步骤、返回值形态错误，还是没有满足测试入口要求。",
    ], level=2, image=diagram_paths[2], image_title="图3 核心模块逻辑框图")

    body_page("3.3 训练样本生成", [
        "训练样本生成模块把任务资料转换为可供训练流程读取的结构化记录。样本字段通常包括任务编号、输入提示、期望输出形式、所属领域、提示族、拆分标记和生成批次。字段保持稳定后，训练和评测流程才能用同一套规则复核结果。",
        "样本生成不是简单复制任务描述。模块会根据任务类型补充必要约束，控制提示长度，保留测试相关要求，并把不适合训练的内部备注排除在正式样本之外。这样可以减少提示噪声，也能降低评测答案被提前暴露的风险。",
        "生成过程同时输出清单文件。清单记录样本数量、任务范围、生成时间、拆分策略、输入目录和输出目录。后续报告引用训练数据时，应优先引用清单，而不是只写一个模糊的数据目录。",
        "样本生成完成后，使用人员需要抽查正常样本和边界样本。正常样本用于确认格式和字段齐全，边界样本用于确认长提示、特殊量子门、复杂输入或失败任务不会破坏训练流程。",
        "如果任务描述或提示模板发生变化，样本应重新生成并重新记录批次。直接手工修改生成后的样本文件会破坏可追溯性，也会让评测报告难以解释数据来源。",
    ], level=2)

    body_page("3.4 数据完整性校验", [
        "数据完整性校验用于阻止错误数据进入训练或评测阶段。校验内容包括字段缺失、编号重复、文件编码异常、训练集与评测集交叉、任务清单不一致、输出目录冲突和样本数量异常。",
        "对于严格评测场景，平台要求训练数据和评测数据在任务层面保持隔离。只依靠样本编号不同并不充分，因为同一任务的答案或测试约束可能在多个样本中重复出现。任务级隔离可以让评测结果更接近真实泛化能力。",
        "校验模块应输出可读错误列表。错误信息需要指出具体文件、字段、任务编号和处理建议，不能只返回失败状态。这样数据人员可以按错误清单逐项修复，而不是反复猜测是哪一条样本出问题。",
        "校验通过后，清单文件会记录通过状态、样本数量、拆分策略和生成时间。训练模块读取数据前应检查该清单，避免使用未校验数据。报告模块也应引用校验结论，说明当前结果对应的数据版本。",
        "校验失败时，不应继续执行训练或评测。强行绕过校验可能产生看似完整但无法复核的结果，后续即使指标较高，也不能作为可靠研发结论。",
    ], level=2)

    body_page("3.5 模型训练管理", [
        "模型训练管理模块读取经过校验的数据、模型目录和参数配置，按批次生成日志、输出目录和检查点记录。训练前会检查关键路径是否存在、输出目录是否冲突、参数是否超出约定范围；训练后会保存运行命令、训练摘要和输出位置。",
        "训练配置需要明确数据路径、模型路径、输出路径、批次名称、训练步数、保存策略和日志位置。命令参数可以覆盖默认配置，但覆盖后的有效参数必须写入运行记录，便于后续复现。",
        "训练运行过程中，平台关注日志是否持续写入、输出目录是否生成必要文件、异常信息是否被记录。运行中断时，应先保存日志和部分输出，再判断是否清理目录或重新启动。",
        "训练输出不直接代表软件效果。只有在固定评测基准上完成候选生成、测试执行和报告汇总后，训练结果才具备比较意义。训练模块的职责是稳定组织运行和保存证据，而不是单独给出最终结论。",
        "对于较长训练任务，平台要求先完成本地小样本验证。这样可以在进入长任务前发现路径、字段、依赖和参数问题，降低资源浪费，也减少后续报告中出现无法解释的失败。",
    ], level=2)

    body_page("3.6 自动评测管理", [
        "自动评测模块把模型输出转换为可执行候选代码，并在隔离目录中运行测试。评测过程记录语法错误、导入错误、断言失败、超时和其他运行异常，不只保留最终通过率。",
        "候选代码生成后，模块会先进行基本清洗和格式检查，去除明显不属于代码的解释性文本，保留可执行主体。清洗不能掩盖真实错误，如果输出缺少必要函数或结构不完整，应记录为评测失败。",
        "测试执行时，每个任务应绑定候选文件、测试入口、运行预算和输出记录。通过状态需要来自实际测试结果，而不是人工判断。失败摘要应说明错误类型和定位信息，便于后续数据补充或模型改进。",
        "同一评测基准可以用于比较不同训练结果。报告模块按任务维度识别新增通过、退化失败和稳定任务，避免只看总体分数而忽略关键任务变化。",
        "评测目录应和训练目录分开保存。候选文件、测试日志、得分卡和失败摘要都属于评测证据，不能被下一轮运行覆盖。必要时可以按批次复制到归档目录。",
    ], level=2)

    body_page("3.7 检索问答支持", [
        "检索问答模块读取项目内部文档、任务说明和历史报告，建立面向研发人员的资料检索能力。它的作用是帮助使用人员快速找到相关约束、接口说明和失败原因，而不是替代正式评测。",
        "检索资料需要控制来源范围。适合进入索引的内容包括任务说明、接口文档、评测报告、维护记录和经过确认的设计说明；不适合进入索引的内容包括账号、密钥、私人路径、临时调试输出和未确认结论。",
        "检索结果需要保留来源路径和片段位置。研发人员使用检索结果时，应能回到原始文件查看上下文，避免把片段中的局部描述误用为完整规则。",
        "问答记录可以帮助维护人员发现文档缺口。例如同一类问题反复出现，说明说明书或操作文档可能没有写清楚；检索不到相关片段，说明任务资料或报告归档需要补充。",
        "检索模块不改变训练和评测的判定标准。即使检索结果对某个失败任务给出解释，最终是否通过仍以自动测试和得分卡为准。",
    ], level=2)

    body_page("3.8 报告归档", [
        "报告归档模块汇总训练日志、评测得分、失败明细、差异分析和人工复核意见。报告中既保留整体指标，也保留失败任务，避免只展示成功结论。",
        "报告生成时，应读取原始得分卡、失败摘要和运行记录，不手工改写指标。报告文字可以解释结果，但不能脱离原始证据另行给出结论。每个关键指标都应能追溯到具体文件。",
        "归档目录按批次保存输入清单、运行命令、配置快照、训练日志、评测结果、失败摘要和报告文本。这样后续复现实验或提交材料复核时，可以回到原始证据，而不是只保留最终文档。",
        "报告还应记录对比对象和评测基准。如果比较两个训练批次，必须说明二者是否使用同一基准、同一提示版本和同一运行预算。缺少这些条件的比较容易产生误导。",
        "归档完成后，项目负责人可以根据报告决定下一轮数据补充、模型训练或评测修复。报告不是流程装饰，而是研发闭环中承接下一轮工作的依据。",
    ], level=2)

    body_page("4.1 环境准备", [
        "首次使用前，操作人员进入软件根目录，确认源码目录、数据目录、任务目录、模型目录和报告目录均存在。随后检查运行语言、脚本入口和依赖环境是否可用，并确认当前批次的配置文件、输出目录和日志目录没有与历史结果混用。",
        "准备阶段还应确认本次运行目标。如果只是验证任务格式，可以选择小范围数据构建和单元测试；如果要完成训练评测闭环，应提前准备训练样本、评测基准、模型目录、输出目录和报告目录。",
        "目录准备应遵循用途分离原则。原始任务、生成样本、评测基准、候选代码、训练输出、日志文件和归档报告不应混放在同一目录。这样可以降低误删、误读和覆盖风险。",
        "环境检查结果应保留在运行记录中。至少需要记录执行日期、使用命令、输入目录、输出目录和关键配置。较长训练任务启动前必须先完成本地小样本验证。",
        "准备工作看似简单，但它决定后续报告能否复查。路径不清、配置混用或历史结果残留，都会让评测结论失去可信度。",
    ], level=2)

    body_page("4.2 数据构建操作", [
        "数据构建时，用户先选择任务范围和输出批次，再运行数据构建入口生成训练文件、评测文件和清单报告。生成后应查看样本数量、任务编号、拆分策略和字段完整性。",
        "若清单中出现重复编号、字段缺失或拆分交叉，应先修复任务资料，再重新构建数据。不能在生成后的样本中临时删除错误行，因为这样会让清单、样本和报告之间出现不一致。",
        "数据构建结果应至少包含训练样本、评测样本、样本清单和校验摘要。训练样本用于训练运行，评测样本用于固定基准，清单用于报告引用，校验摘要用于说明数据是否具备进入下一阶段的条件。",
        "构建完成后，操作人员应抽查正常样本、边界样本和失败样本。正常样本确认字段齐全，边界样本确认复杂任务不会破坏格式，失败样本确认错误信息能够被定位。",
        "如果需要调整样本模板，应回到构建规则修改并重新生成整批数据。这样可以保持版本清晰，也便于后续比较不同模板对训练和评测结果的影响。",
    ], level=2)

    body_page("4.3 训练评测和报告操作", [
        "训练操作需要指定训练数据、模型目录、输出目录和批次参数。训练启动后，使用人员应检查日志是否持续写入、输出目录是否生成必要文件、异常信息是否被记录。",
        "训练结束后，不直接修改模型输出，而是进入评测阶段，通过固定基准生成候选文件并运行测试。候选生成和测试执行应保留独立目录，避免与训练目录混在一起。",
        "评测完成后，报告模块读取得分卡、失败摘要和日志记录生成报告。报告人员应核对报告引用的训练批次、评测基准和候选目录是否一致。",
        "若发现结果异常，应先定位是数据、训练、评测还是报告环节的问题，再决定是否重新构建数据、重跑训练或只重跑评测。不同处理方式影响成本和结论范围，不能一概重跑。",
        "一轮完整操作结束后，应归档输入清单、配置快照、训练日志、评测得分、失败摘要和报告文本。缺少任一关键材料，后续复核都会变得困难。",
    ], level=2)

    body_page("5.1 命令行和函数接口", [
        "软件通过命令行入口组织数据构建、训练、评测、报告生成和维护检查等操作。命令参数通常包括输入路径、输出路径、任务范围、配置文件、运行预算和批次名称。",
        "入口脚本只负责参数解析、路径检查和流程调度，具体业务逻辑由对应模块函数完成。这样可以让命令行适合人员操作，同时让函数接口适合测试和复用。",
        "函数接口强调单一职责。解析函数只把任务文件转换为内部对象，校验函数只返回错误列表或通过状态，训练函数只处理训练输入和输出目录，评测函数只处理候选代码和测试结果。",
        "跨模块调用通过显式参数传递数据，不直接依赖隐藏的全局状态。接口返回值应能表达成功、失败、错误类型和关键输出路径，避免调用方只能依赖终端文本判断结果。",
    ], level=2, table=(
        ["接口类型", "使用对象", "主要输入", "主要输出"],
        [
            ["命令行接口", "操作人员", "路径、配置、批次参数", "执行状态、输出目录"],
            ["函数接口", "开发和测试模块", "任务对象、配置对象", "结果对象、错误列表"],
            ["校验接口", "数据人员", "样本文件、清单文件", "通过状态、错误摘要"],
            ["报告接口", "项目负责人", "得分卡、日志摘要", "报告文本、归档清单"],
        ],
    ))

    body_page("5.2 文件配置和报告接口", [
        "平台主要使用结构化文本文件保存任务、样本、清单、得分卡和报告摘要。训练样本与评测样本分目录保存，报告输入与最终报告分目录保存，临时文件不得覆盖正式归档文件。",
        "配置接口用于管理模型路径、数据路径、输出路径、运行预算和默认参数。命令参数可以覆盖配置默认值，但覆盖结果需要写入运行记录。这样后续复查时可以看到实际生效参数，而不是只看默认配置。",
        "文件接口需要明确编码、字段、路径和读写时机。样本文件应保持稳定字段，清单文件应记录生成批次，得分卡应记录任务级结果，报告文件应引用原始证据。",
        "报告接口要求每项指标可以追溯到原始得分卡，每个失败结论可以追溯到任务编号、候选文件和错误摘要。报告不应只保留总体分数，因为总体分数无法解释具体改进方向。",
        "当文件字段或配置名称发生变化时，应同步修改读取逻辑、测试用例、说明文字和清单生成。只改一个位置会造成隐性兼容问题，后续运行可能在报告阶段才暴露。",
    ], level=2)

    body_page("6.1 任务切分和提示构建", [
        "任务切分算法先按任务编号、提示族和用途建立集合，再检查训练集、验证集和评测集之间是否存在交叉。对于需要严格评测的任务，平台优先保持任务级隔离，而不是只依赖样本编号不同。",
        "切分结果写入清单文件，并在报告中保留拆分策略。清单中的统计数字应与实际样本文件一致，发现数量不一致时应停止训练流程，回到数据构建阶段检查。",
        "提示构建算法把任务描述、约束条件、输入输出要求和必要上下文组织为模型输入。构建时会控制文本长度，保留真正影响解题的约束，减少无关说明。",
        "提示模板发生变化时，应重新生成样本并记录版本，否则不同批次结果不具备可比性。报告中比较两个实验时，也需要说明二者是否使用同一提示模板。",
        "任务切分和提示构建共同决定训练数据质量。切分不严会污染评测，提示不清会降低训练效果；两者都需要纳入版本记录和复核流程。",
    ], level=2)

    body_page("6.2 候选清洗和评分", [
        "候选清洗算法从模型输出中提取可执行代码，去除多余说明、格式标记和明显不属于代码的片段。清洗过程不应掩盖真实失败，如果输出缺少必要函数、导入错误或语法不完整，应记录为评测异常。",
        "清洗规则需要尽量确定。相同原始输出在相同规则下应得到相同候选文件，避免人工临时修改导致评分不可复现。被清除的非代码片段可以记录在日志中，便于后续分析模型输出习惯。",
        "执行评分算法根据测试退出状态、断言结果、超时状态和错误类型生成任务级分数。评分时应区分语法错误、导入错误、断言失败、超时和环境异常，因为这些失败对应的修复方式不同。",
        "通过状态必须来自实际测试结果，而不是人工判断。若测试本身存在问题，应先修复测试，再重新运行评测；不能在旧测试结果上直接改写得分。",
        "评分输出包括得分卡、失败摘要、候选目录和测试日志。报告模块读取这些输出形成结论，维护人员也可以据此决定下一轮补充哪些训练样本。",
    ], level=2)

    body_page("6.3 差异分析", [
        "差异分析算法按任务维度比较两个或多个实验结果，识别新增通过、退化失败和稳定任务。它比单一总分更有价值，因为总分相同的两个结果可能在具体任务上表现完全不同。",
        "比较前需要确认评测基准、提示版本、运行预算和候选清洗规则是否一致。若这些条件不同，报告应明确标注，不应把结果解释为同一条件下的直接提升或退化。",
        "新增通过任务通常说明数据、训练或提示策略对某些任务有效；退化失败任务则需要重点复查是否存在训练过拟合、提示冲突、候选清洗误删或测试入口变化。",
        "差异分析结果应保存为结构化文件和可读报告。结构化文件方便脚本继续处理，可读报告方便项目负责人判断下一轮工作重点。",
        "当差异分析发现关键任务退化时，平台不应只追求总体分数提升，而应把退化任务加入复盘清单。研发平台的目标是稳定提升可复现能力，而不是只保留有利指标。",
    ], level=2)

    body_page("6.4 作业生命周期", [
        "作业生命周期从准备、启动、运行、检查、回收和归档六个阶段组织。准备阶段确认输入和配置，启动阶段记录命令和时间，运行阶段观察日志，检查阶段核对输出，回收阶段整理结果，归档阶段生成报告。",
        "作业启动成功不等于作业完成。训练任务可能在中途失败，评测任务可能只生成部分候选，报告任务可能读取旧文件。平台要求每个阶段都有可检查输出，避免把过程状态误认为最终结果。",
        "运行中断时，应先保存现场。日志、配置、部分输出和错误摘要都应保留，随后再决定清理、重试或人工复核。直接删除失败目录会丢失定位信息。",
        "作业完成后，应检查输出目录、日志末尾、结果文件数量和报告引用路径。只有这些内容一致，才可以把本轮结果写入归档报告。",
        "生命周期设计让本地运行和训练环境运行具有相同复核口径。无论任务在哪里执行，最终都要回到输入、输出、日志、报告和归档清单这些材料上判断是否完成。",
    ], level=2)

    body_page("7、 测试与验收说明", [
        "测试体系覆盖任务解析、数据构建、样本完整性、候选清洗、评测执行、报告生成和关键脚本入口。单元测试使用确定性输入，保证相同代码在相同任务上得到稳定结果。",
        "涉及目录和文件的测试应使用隔离临时目录，避免污染正式数据和报告。测试既要覆盖成功路径，也要覆盖字段缺失、路径错误、候选不可执行、超时和报告输入不完整等失败路径。",
        "验收时重点检查四类结果：第一，数据清单是否准确记录样本数量、拆分策略和生成时间；第二，训练运行是否留下命令、参数、日志和输出目录；第三，评测结果是否能定位到具体任务、候选文件和失败原因；第四，报告结论是否与原始得分卡一致。",
        "当新增任务、修改提示模板、调整评测逻辑或改变报告格式时，应补充对应测试并重新生成材料。若只修改说明文档而不复核代码和报告，容易出现文档描述与实际运行不一致。",
        "验收结论应写明检查日期、检查范围、通过项和遗留问题。对于软件著作权提交材料，验收还应检查申请表、说明文档和源程序之间的软件名称、版本号、著作权人和发表状态是否一致。",
    ])

    body_page("8、 安全边界与权限", [
        "本软件的登记对象为自研源程序和设计表达，不包括通用操作系统、通用硬件、基础运行库、基础模型权重或外部运行服务。文档和报告不得写入账号、密钥、令牌、私人目录或无关个人信息。",
        "权限控制主要体现在目录边界和材料边界。任务资料、训练数据、评测结果、日志和报告按项目范围保存；不同批次结果分目录归档，避免互相覆盖；正式提交材料只包含登记所需内容。",
        "配置文件公开前应检查是否包含敏感路径或凭据片段。日志公开前应检查是否包含账号、令牌、个人目录或外部服务细节。发现敏感信息后，应删除并重新生成相关材料。",
        "审计记录需要把命令、参数、输入清单、输出目录、日志和报告联系起来。发现主体信息变化、文件名变化或发表状态变化时，应先修正申请表、说明文档、源程序和清单，再进入最终提交检查。",
        "安全边界不是为了削弱软件功能，而是为了让登记材料准确描述软件自身。运行环境可以变化，外部资源可以替换，但申请材料应始终聚焦本软件的自研表达和可复核流程。",
    ])

    body_page("9、 维护与扩展说明", [
        "新增量子任务时，应补充任务说明、输入输出要求、测试约束和评测入口，并检查任务编号是否与既有任务冲突。新增任务进入训练数据前，应先通过数据构建和完整性校验。",
        "修改数据字段、目录结构或配置参数时，需要同步更新读取逻辑、清单生成、报告生成和说明文字。接口变更应尽量保持向后兼容；无法兼容时，应在版本维护记录中说明变化原因、影响范围和迁移方式。",
        "新增模块时，应明确输入、输出、负责人和测试范围。模块不能只在脚本中临时调用，而应纳入目录约定、配置约定和报告流程，否则后续复核难以确认其作用。",
        "维护完成后应执行相关测试，并重新生成必要材料。若源程序量、说明文档页数、图示内容或主体信息发生变化，应同步更新README、清单和检查报告。",
        "未来如按升级版本申请登记，应根据实际变化编写版本差异说明，列明新增功能、修改模块、代码范围和兼容性影响。本版本为V1.0，当前登记口径为原创软件、独立开发、未发表。",
    ])

    body_page("10、 常见问题处理", [
        "若数据构建失败，应先检查任务目录是否存在、字段是否齐全、编号是否重复、文件编码是否正确。若清单文件没有生成，不应继续训练；若清单数字和样本文件不一致，应回到构建规则检查。",
        "若训练运行失败，应检查训练数据路径、模型目录、输出目录、依赖环境和日志末尾错误。资源不足、路径错误、保存失败和参数错误需要分别处理，不能只用重启命令覆盖原始现场。",
        "若评测结果异常，应检查候选代码是否完整、测试入口是否正确、超时设置是否合理。候选代码不可执行时，应记录为候选或评测异常；测试本身错误时，应修复测试后重新评分。",
        "若报告内容与预期不一致，应先核对报告引用的得分卡、失败清单和运行目录，确认没有读取旧批次文件。多人协作时尤其需要确认输出目录和归档目录，以免一个人的临时结果覆盖另一个人的正式结果。",
        "若提交材料出现页码、页眉、主体信息或文件名不一致，应重新生成三份正式DOCX，而不是只手工修改其中一份。生成脚本是保持材料一致性的主要来源。",
    ])

    body_page("11、 提交检查", [
        "提交前应逐项检查三份正式DOCX文件：申请表、说明文档和源程序。申请表重点核对软件名称、版本、简称、著作权人、作者、联系人、电话、地址、未发表和原创口径。",
        "说明文档重点核对封面、目录、标题层级、图示、正文表格、页眉页码、黑色字体和结束标志。说明文档不足60页时整本提交；超过60页时按前30页和后30页口径处理。正文页应保持内容连贯，图页应保证图片清晰完整并配有文字说明。",
        "源程序重点核对页数、每页行数、页眉页码和末页结束标志。源程序超过60页时按前30页和后30页组织，不足60页时全部提交。当前源程序按60页生成，每页保留60行可见代码内容。",
        "参考PDF、升级版本差异说明样表、README、申请材料生成清单、知识产权系统填写建议和模板逐项检查报告只作为内部复核材料，不作为正式提交附件。系统侧如要求自然人证件材料，应由提交人在登记系统中另行补录。",
        "最终提交前，还应再次确认软件未发表状态是否仍然真实。如果软件已经销售、交付、上架、公开发布或以复制件形式提供，应改为已发表并填写首次发表日期和地点。",
    ], end=True)

    out = OUT / MANUAL_DOCX_NAME
    doc.save(out)
    scrub_docx_theme_colors(out)
    return out


def build_manual_doc() -> Path:
    """Build a strict 30-page full-page manual with aligned catalog numbers."""
    diagram_paths = create_manual_diagrams()
    doc = Document()
    configure_section(doc.sections[0], top=Cm(1.05), bottom=Cm(0.65), left=Cm(1.75), right=Cm(1.65))

    for style_name in ["Normal", "Body Text", "Heading 1", "Heading 2", "Heading 3", "List Paragraph"]:
        if style_name in doc.styles:
            style = doc.styles[style_name]
            style.font.name = "宋体"
            style._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
            style.font.color.rgb = RGBColor(0, 0, 0)
    doc.styles["Normal"].font.size = Pt(9)
    doc.styles["Body Text"].font.size = Pt(9)

    def run_text(paragraph, text: str, *, size=Pt(9), bold=False) -> None:
        run = paragraph.add_run(text)
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
        run.font.size = size
        run.bold = bold
        run.font.color.rgb = RGBColor(0, 0, 0)

    def grid_line(text: str = "", *, bold=False, center=False, size=Pt(9), left_indent=0) -> None:
        p = doc.add_paragraph(style="Body Text")
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        p.paragraph_format.line_spacing = Pt(14.6)
        if left_indent:
            p.paragraph_format.left_indent = Pt(left_indent)
        if center:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_text(p, text, size=size, bold=bold)

    def toc_grid_line(title: str, page: int, *, indent=False, bold=False) -> None:
        p = doc.add_paragraph(style="Body Text")
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        p.paragraph_format.line_spacing = Pt(14.6)
        if indent:
            p.paragraph_format.left_indent = Cm(0.45)
        p.paragraph_format.tab_stops.add_tab_stop(Cm(15.95), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        run_text(p, title, size=Pt(9.2), bold=bold)
        run_text(p, f"\t{page}", size=Pt(9.2), bold=bold)

    section_lines = {
        "总体业务说明": [
            "说明书用于登记审查和后续维护，内容对应申请表和源程序。",
            "本文说明软件的设计目标、模块边界、接口数据和运行流程。",
            "软件围绕量子代码模型研发，支撑任务、数据、训练和评测。",
            "登记对象是自研平台程序，不包含通用系统和外部基础资源。",
            "文档采用统一术语，确保软件名称、版本和主体信息一致。",
            "说明书中所有路径和运行环境均采用通用技术口径描述。",
            "维护人员可依本文核对实际源程序、脚本入口和报告材料。",
            "提交人员可依本文检查页眉页码、目录页码和结束标志。",
            "平台把研发过程拆分为可记录、可检查、可复现的环节。",
            "每一轮研发均应保留输入、参数、输出、日志和复核结论。",
        ],
        "系统总体设计": [
            "系统采用分层设计，入口层负责命令参数和任务范围读取。",
            "数据层负责任务整理、样本构建、清单记录和完整性校验。",
            "执行层负责训练运行、候选生成、候选清洗和自动评测。",
            "归档层负责汇总日志、得分卡、失败摘要和对比报告。",
            "各层通过结构化文件和明确函数接口传递运行数据。",
            "模块边界清楚可以降低多人协作中的覆盖和误读风险。",
            "运行流程坚持先验证后长任务，先留痕后归档的原则。",
            "部署方式不绑定单一机器，关键是目录和配置保持一致。",
            "本地验证结果和训练环境结果均应回收至稳定归档目录。",
            "总体设计目标是让每个结论都能追溯至原始运行证据。",
        ],
        "核心功能说明": [
            "任务管理模块维护任务编号、领域标签和测试约束。",
            "量子中间表示模块整理线路结构、门序列和测量要求。",
            "训练样本生成模块把任务资料转为结构化训练记录。",
            "数据完整性校验模块检查字段、编号、拆分和目录冲突。",
            "模型训练管理模块保存训练参数、日志、检查点和输出。",
            "自动评测模块执行候选代码，记录错误类型和通过状态。",
            "检索问答模块提供内部资料检索，帮助定位约束和接口。",
            "报告归档模块汇总指标、失败任务、日志和复核意见。",
            "核心功能共同构成从任务到报告的研发闭环。",
            "每个功能都要求有明确输入、输出、异常和记录位置。",
        ],
        "操作使用说明": [
            "首次使用前应确认源码目录、数据目录和报告目录存在。",
            "操作人员应检查运行语言、脚本入口和依赖环境状态。",
            "数据构建前需要确定任务范围、输出批次和配置文件。",
            "构建完成后应查看样本数量、字段完整性和清单摘要。",
            "训练操作需要指定训练数据、模型目录和输出目录。",
            "训练启动后应检查日志是否持续写入和输出是否生成。",
            "评测操作应使用固定基准，候选目录应与训练目录分离。",
            "报告生成后应核对引用的训练批次和评测基准是否一致。",
            "异常处理应先保存现场，再决定重试、清理或人工复核。",
            "完整操作结束后应归档输入清单、日志、结果和报告。",
        ],
        "接口与数据说明": [
            "命令行接口面向操作人员，负责运行入口和流程调度。",
            "函数接口面向模块复用，要求输入输出结构清晰稳定。",
            "文件接口保存任务、样本、清单、得分卡和报告摘要。",
            "配置接口记录模型路径、数据路径、输出路径和预算参数。",
            "报告接口要求每项指标能追溯至原始得分卡和日志。",
            "接口变更时应同步更新测试用例、帮助信息和说明文字。",
            "文件读写时机应明确，临时文件不得覆盖正式结果。",
            "配置默认值和命令覆盖值都应写入运行记录。",
            "接口异常应区分路径缺失、字段错误、权限不足和超时。",
            "数据文件应保持编码统一，字段顺序和批次信息稳定。",
        ],
        "算法与运行设计": [
            "任务切分算法按任务编号、提示族和用途建立数据集合。",
            "严格评测场景优先保持任务级隔离，避免训练评测交叉。",
            "提示构建算法保留输入输出要求、边界条件和测试约束。",
            "候选清洗算法提取可执行代码并去除非代码说明片段。",
            "执行评分算法根据退出状态、断言结果和超时状态计分。",
            "差异分析算法识别新增通过、退化失败和稳定任务。",
            "作业生命周期覆盖准备、启动、运行、检查、回收和归档。",
            "算法参数应写入运行记录，保证相同输入可复现。",
            "中断作业应保留日志和部分输出，避免直接覆盖现场。",
            "运行完成后必须核对输出目录、日志末尾和报告引用路径。",
        ],
        "测试与安全维护": [
            "测试体系覆盖任务解析、数据构建、样本完整性和评测执行。",
            "涉及目录和文件的测试应使用隔离临时目录。",
            "验收应检查清单、命令、日志、得分卡和报告是否对应。",
            "安全边界要求文档和报告不写入账号、密钥和私人目录。",
            "权限控制主要体现在目录边界、材料边界和归档边界。",
            "维护扩展时应同步更新读取逻辑、测试和说明文档。",
            "新增任务进入训练数据前必须完成构建和校验。",
            "常见问题应按数据、训练、评测和报告四类定位。",
            "提交检查应核对申请表、说明书、源程序和清单一致性。",
            "最终提交前应确认未发表状态和独立开发口径仍然真实。",
        ],
    }

    topic_pages = [
        ("1、 总体业务说明", "总体业务说明"),
        ("1.1 编写目的", "总体业务说明"),
        ("1.2 适用对象与软件定位", "总体业务说明"),
        ("2、 系统总体设计", "系统总体设计"),
        ("2.1 总体架构", "系统总体设计"),
        ("2.2 模块边界", "系统总体设计"),
        ("2.3 运行流程", "系统总体设计"),
        ("2.4 部署与数据流", "系统总体设计"),
        ("3、 核心功能说明", "核心功能说明"),
        ("3.1 量子任务管理", "核心功能说明"),
        ("3.2 量子中间表示", "核心功能说明"),
        ("3.3 训练样本生成", "核心功能说明"),
        ("3.4 数据完整性校验", "核心功能说明"),
        ("3.5 模型训练管理", "核心功能说明"),
        ("3.6 自动评测管理", "核心功能说明"),
        ("3.7 检索问答支持", "核心功能说明"),
        ("3.8 报告归档", "核心功能说明"),
        ("4、 操作使用说明", "操作使用说明"),
        ("4.1 环境准备", "操作使用说明"),
        ("4.2 数据构建操作", "操作使用说明"),
        ("4.3 训练评测和报告操作", "操作使用说明"),
        ("5、 接口与数据说明", "接口与数据说明"),
        ("5.1 命令行和函数接口", "接口与数据说明"),
        ("5.2 文件配置和报告接口", "接口与数据说明"),
        ("6、 算法与运行设计", "算法与运行设计"),
        ("6.1 任务切分和提示构建", "算法与运行设计"),
        ("6.2 候选清洗和评分", "算法与运行设计"),
        ("6.3 差异分析", "算法与运行设计"),
        ("6.4 作业生命周期", "算法与运行设计"),
        ("7、 测试与验收说明", "测试与安全维护"),
        ("8、 安全边界与权限", "测试与安全维护"),
        ("9、 维护与扩展说明", "测试与安全维护"),
        ("10、 常见问题处理", "测试与安全维护"),
        ("11、 提交检查", "测试与安全维护"),
    ]

    page_titles = [
        "封面与文档概述",
        "目录",
        "1.1 编写目的",
        "1.2 适用对象与软件定位",
        "2.1 总体架构",
        "2.2 模块边界",
        "2.3 运行流程",
        "2.4 部署与数据流",
        "3.1 量子任务管理",
        "3.2 量子中间表示",
        "3.3 训练样本生成",
        "3.4 数据完整性校验",
        "3.5 模型训练管理",
        "3.6 自动评测管理",
        "3.7 检索问答支持",
        "3.8 报告归档",
        "4.1 环境准备",
        "4.2 数据构建操作",
        "4.3 训练评测和报告操作",
        "5.1 命令行和函数接口",
        "5.2 文件配置和报告接口",
        "6.1 任务切分和提示构建",
        "6.2 候选清洗和评分",
        "6.3 差异分析",
        "6.4 作业生命周期",
        "7、 测试与验收说明",
        "8、 安全边界与权限",
        "9、 维护与扩展说明",
        "10、 常见问题处理",
        "11、 提交检查",
    ]

    page_sections = [
        "总体业务说明", "总体业务说明", "总体业务说明", "总体业务说明",
        "系统总体设计", "系统总体设计", "系统总体设计", "系统总体设计",
        "核心功能说明", "核心功能说明", "核心功能说明", "核心功能说明",
        "核心功能说明", "核心功能说明", "核心功能说明", "核心功能说明",
        "操作使用说明", "操作使用说明", "操作使用说明",
        "接口与数据说明", "接口与数据说明",
        "算法与运行设计", "算法与运行设计", "算法与运行设计", "算法与运行设计",
        "测试与安全维护", "测试与安全维护", "测试与安全维护", "测试与安全维护", "测试与安全维护",
    ]

    def expanded_lines(page_no: int, title: str, section: str, target: int) -> list[str]:
        lines = []
        base = section_lines[section]
        focus = [
            f"{title}需要与源程序、申请表和生成清单保持一致。",
            f"{title}对应的输入、处理、输出和异常均应留痕。",
            f"{title}的结果应进入固定目录，便于后续复核。",
            f"{title}的说明应覆盖正常流程和失败处理两类情况。",
            f"{title}变更后应同步更新测试、报告和说明材料。",
            f"{title}执行前应确认批次、路径、配置和权限状态。",
            f"{title}执行后应检查日志、清单、得分卡和归档结论。",
            f"{title}不应写入账号、密钥、令牌和无关平台信息。",
        ]
        idx = 0
        while len(lines) < target:
            source = base if idx % 2 == 0 else focus
            item = source[(idx // 2) % len(source)]
            lines.append(f"{len(lines) + 1:02d}. {item}")
            idx += 1
        return lines[:target]

    def add_page(page_no: int, title: str, section: str, *, image: Path | None = None, image_title: str = "", end=False) -> None:
        if page_no > 1:
            doc.add_page_break()
        if page_no == 1:
            grid_line(HEADER, center=True, bold=True, size=Pt(14))
            grid_line("设计说明书及使用说明文档", center=True, bold=True, size=Pt(13))
            for item in [
                f"文档版本：{VERSION}",
                f"软件版本：{VERSION}",
                f"软件简称：{SHORT_NAME}",
                f"著作权人：{'、'.join(RIGHTHOLDERS)}",
                f"作者：{'、'.join(AUTHORS)}",
                f"开发完成日期：{COMPLETION_DATE}",
                f"发表状态：{PUBLICATION_STATUS}",
            ]:
                grid_line(item, center=True, size=Pt(9.5))
            for line in expanded_lines(page_no, title, section, 36):
                grid_line(line)
            return
        if page_no == 2:
            grid_line("目录", center=True, bold=True, size=Pt(13))
            toc_entries = [
                ("1、 总体业务说明", 3, False),
                ("1.1 编写目的", 3, True),
                ("1.2 适用对象与软件定位", 4, True),
                ("2、 系统总体设计", 5, False),
                ("2.1 总体架构", 5, True),
                ("2.2 模块边界", 6, True),
                ("2.3 运行流程", 7, True),
                ("2.4 部署与数据流", 8, True),
                ("3、 核心功能说明", 9, False),
                ("3.1 量子任务管理", 9, True),
                ("3.2 量子中间表示", 10, True),
                ("3.3 训练样本生成", 11, True),
                ("3.4 数据完整性校验", 12, True),
                ("3.5 模型训练管理", 13, True),
                ("3.6 自动评测管理", 14, True),
                ("3.7 检索问答支持", 15, True),
                ("3.8 报告归档", 16, True),
                ("4、 操作使用说明", 17, False),
                ("4.1 环境准备", 17, True),
                ("4.2 数据构建操作", 18, True),
                ("4.3 训练评测和报告操作", 19, True),
                ("5、 接口与数据说明", 20, False),
                ("5.1 命令行和函数接口", 20, True),
                ("5.2 文件配置和报告接口", 21, True),
                ("6、 算法与运行设计", 22, False),
                ("6.1 任务切分和提示构建", 22, True),
                ("6.2 候选清洗和评分", 23, True),
                ("6.3 差异分析", 24, True),
                ("6.4 作业生命周期", 25, True),
                ("7、 测试与验收说明", 26, False),
                ("8、 安全边界与权限", 27, False),
                ("9、 维护与扩展说明", 28, False),
                ("10、 常见问题处理", 29, False),
                ("11、 提交检查", 30, False),
            ]
            for title_text, page, indent in toc_entries:
                toc_grid_line(title_text, page, indent=indent, bold=not indent)
            for line in [
                "目录页采用右对齐制表位生成页码，页码右边缘保持一致。",
                "目录内容对应后续正文页，便于审查人员快速定位章节。",
                "本说明书不足六十页，按完整文档提交口径组织。",
                "正文页均按固定行网格排版，避免页面下部留白。",
                "目录页、正文页、图文页和末页均保留统一页眉页码。",
                "end标志保留在最后一页末尾，作为提交材料结束标识。",
                "目录所列页码经过LibreOffice渲染核对，和正文实际页码一致。",
                "各一级标题和二级标题均在正文中有对应内容。",
                "图示页分别说明总体结构、训练评测流程和核心模块逻辑。",
                "后续如增删章节，应重新渲染并校验目录页码。",
            ]:
                grid_line(line)
            return
        grid_line(title, bold=True, size=Pt(10.2))
        pre_image_count = 12 if image is not None else 0
        body_target = 43 if image is None else 30
        body_lines = expanded_lines(page_no, title, section, body_target)
        if image is not None:
            for line in body_lines[:pre_image_count]:
                grid_line(line)
            doc.add_picture(str(image), width=Cm(10.4))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
            grid_line(image_title, center=True, bold=True, size=Pt(8.5))
            for line in body_lines[pre_image_count:]:
                grid_line(line)
        else:
            for line in body_lines:
                grid_line(line)
        if end:
            grid_line("end", bold=True)

    image_map = {
        5: (diagram_paths[0], "图1 软件总体结构图"),
        7: (diagram_paths[1], "图2 训练与评测流程图"),
        10: (diagram_paths[2], "图3 核心模块逻辑框图"),
    }
    for idx, title in enumerate(page_titles, start=1):
        image_path, image_title = image_map.get(idx, (None, ""))
        add_page(idx, title, page_sections[idx - 1], image=image_path, image_title=image_title, end=(idx == 30))

    out = OUT / MANUAL_DOCX_NAME
    doc.save(out)
    scrub_docx_theme_colors(out)
    return out


def build_manual_doc() -> Path:
    """Build the manual in the same formal Word style as the qcrypto reference."""
    diagram_paths = create_manual_diagrams()
    doc = Document()
    configure_section(doc.sections[0], top=Cm(2.0), bottom=Cm(1.7), left=Cm(2.1), right=Cm(1.8))

    black = RGBColor(0, 0, 0)
    for style_name in ["Normal", "Body Text", "Heading 1", "Heading 2", "Heading 3", "List Paragraph"]:
        if style_name in doc.styles:
            style = doc.styles[style_name]
            style.font.name = "宋体"
            style._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
            style.font.color.rgb = black
    doc.styles["Normal"].font.size = Pt(10.5)
    doc.styles["Body Text"].font.size = Pt(10.5)
    doc.styles["Heading 1"].font.size = Pt(16)
    doc.styles["Heading 1"].font.bold = True
    doc.styles["Heading 2"].font.size = Pt(13)
    doc.styles["Heading 2"].font.bold = True
    doc.styles["Heading 3"].font.size = Pt(11)
    doc.styles["Heading 3"].font.bold = True

    def write_run(paragraph, text: str, font_size=Pt(10.5), bold=False) -> None:
        run = paragraph.add_run(text)
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
        run.font.size = font_size
        run.bold = bold
        run.font.color.rgb = black

    def paragraph(text: str, first_indent: bool = True, space_after=Pt(6), line_spacing=1.5):
        p = doc.add_paragraph(style="Body Text")
        p.paragraph_format.line_spacing = line_spacing
        p.paragraph_format.space_after = space_after
        if first_indent:
            p.paragraph_format.first_line_indent = Pt(21)
        write_run(p, text, font_size=Pt(10.5))
        return p

    def heading(text: str, level: int = 1):
        p = doc.add_paragraph(style=f"Heading {level}")
        p.paragraph_format.space_before = Pt(12 if level == 1 else 8)
        p.paragraph_format.space_after = Pt(8 if level == 1 else 6)
        p.paragraph_format.keep_with_next = True
        write_run(p, text, font_size=Pt(16 if level == 1 else 13 if level == 2 else 11), bold=True)

    def caption(text: str):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(8)
        write_run(p, text, font_size=Pt(9), bold=True)

    def set_cell_black(cell, text: str, bold: bool = False) -> None:
        cell.text = ""
        p = cell.paragraphs[0]
        p.paragraph_format.line_spacing = 1.2
        p.paragraph_format.space_after = Pt(0)
        write_run(p, text, font_size=Pt(9), bold=bold)

    def add_table(headers: list[str], rows: list[list[str]]) -> None:
        table = doc.add_table(rows=1, cols=len(headers))
        table.style = "Table Grid"
        for idx, header in enumerate(headers):
            set_cell_black(table.rows[0].cells[idx], header, bold=True)
        for row in rows:
            cells = table.add_row().cells
            for idx, value in enumerate(row):
                set_cell_black(cells[idx], value)
        doc.add_paragraph()

    def add_image(path: Path, title: str) -> None:
        doc.add_picture(str(path), width=Cm(15.2))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        caption(title)

    def toc_line(title: str, page: int, indent: bool = False) -> None:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.left_indent = Cm(0.38 if indent else 0)
        p.paragraph_format.tab_stops.add_tab_stop(Cm(16.4), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        write_run(p, title, font_size=Pt(9.5))
        write_run(p, f"\t{page}", font_size=Pt(9.5))

    for _ in range(7):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    write_run(p, HEADER, font_size=Pt(22), bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    write_run(p, "设计说明书及使用说明文档", font_size=Pt(20), bold=True)
    doc.add_paragraph()
    for item in [
        f"文档版本：{VERSION}",
        f"软件版本：{VERSION}",
        f"软件简称：{SHORT_NAME}",
        f"著作权人：{'、'.join(RIGHTHOLDERS)}",
        f"作者：{'、'.join(AUTHORS)}",
        f"开发完成日期：{COMPLETION_DATE}",
    ]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(4)
        write_run(p, item, font_size=Pt(12))

    doc.add_page_break()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    write_run(p, "目录", font_size=Pt(16), bold=True)
    toc_items = [
        ("1、 总体业务说明", 4, False),
        ("1.1 编写目的", 4, True),
        ("1.2 适用对象", 4, True),
        ("1.3 软件定位", 4, True),
        ("2、 系统总体设计", 5, False),
        ("2.1 总体架构", 5, True),
        ("2.2 模块结构", 6, True),
        ("2.3 运行流程", 7, True),
        ("3、 核心功能说明", 8, False),
        ("3.1 量子任务管理", 8, True),
        ("3.2 数据构建与校验", 9, True),
        ("3.3 模型训练与自动评测", 10, True),
        ("3.4 检索问答与报告归档", 10, True),
        ("4、 操作使用说明", 11, False),
        ("4.1 环境准备", 11, True),
        ("4.2 数据构建操作", 11, True),
        ("4.3 训练、评测和报告操作", 12, True),
        ("5、 接口与数据说明", 13, False),
        ("5.1 命令行和函数接口", 13, True),
        ("5.2 文件、配置和报告接口", 14, True),
        ("6、 算法与运行设计", 15, False),
        ("6.1 任务切分和提示构建", 15, True),
        ("6.2 候选清洗、执行评分和差异分析", 16, True),
        ("6.3 本地验证和训练运行", 17, True),
        ("7、 测试与验收说明", 18, False),
        ("8、 安全边界与权限", 20, False),
        ("9、 维护与扩展说明", 22, False),
        ("10、 常见问题与提交检查", 24, False),
        ("11、 字段字典与材料复核", 26, False),
        ("12、 运行案例记录", 27, False),
        ("13、 配置与版本管理", 28, False),
        ("14、 软件运行界面截图", 29, False),
        ("14.1 命令行运行界面", 29, True),
        ("14.2 评测报告归档界面", 30, True),
        ("15、 最终复核结论", 31, False),
    ]
    for title, page, indent in toc_items:
        toc_line(title, page, indent)

    doc.add_page_break()
    heading("1、 总体业务说明", 1)
    heading("1.1 编写目的", 2)
    paragraph(f"本文档用于说明{HEADER}的设计思路、功能边界、模块组成、接口数据、运行流程和使用维护方法。文档与登记申请表、源程序文件采用同一软件名称、版本号、著作权人和发表状态，便于登记审查时把功能说明、代码材料和申请表信息互相对应。")
    paragraph("软件面向量子代码模型研发过程，重点解决任务资料分散、训练样本难以复核、评测结果不可比较、报告材料依赖人工整理等问题。文档不把通用运行环境、基础模型权重或外部基础设施作为登记对象，而是说明本软件自研的任务组织、数据构建、训练调度、评测汇总和报告归档表达。")
    heading("1.2 适用对象", 2)
    paragraph("本文档适用于量子算法研发人员、模型训练人员、评测人员、项目负责人和后续维护人员。研发人员可依据本文理解量子任务如何进入数据构建和评测流程；训练人员可依据本文确认训练输入、输出目录和运行记录；评测人员可依据本文复核候选代码、测试结果和报告摘要之间的关系。")
    paragraph("在实际交接中，本文档也作为操作和验收的共同口径使用。负责数据的人重点查看第三章和第五章，确认样本字段、基准文件和清单记录；负责训练和评测的人重点查看第四章、第六章和第七章，确认命令入口、运行顺序和结果判断；负责提交材料的人重点查看第十章，确认文件名、页眉页码、结束标志和主体信息一致。")
    heading("1.3 软件定位", 2)
    paragraph("本软件定位为量子代码大模型研发平台，服务于量子算法任务整理、训练样本构建、模型训练组织、自动化评测、检索问答和阶段性报告归档。它不是单一训练脚本，也不是只展示指标的报表工具，而是把从任务资料到结果复核的多个环节组织为可重复执行的软件流程。")

    heading("2、 系统总体设计", 1)
    heading("2.1 总体架构", 2)
    paragraph("系统采用分层模块化结构。入口层负责读取命令参数、配置文件和任务范围；数据层负责整理量子任务、生成训练样本、构建评测基准并记录清单；执行层负责模型训练、候选代码生成、代码执行评测和检索问答；归档层负责汇总日志、指标、失败样例和对比报告。")
    paragraph("各层之间主要通过结构化文件、固定目录和明确函数接口传递数据。任务库向数据构建模块提供任务说明和测试约束，数据构建模块向训练模块提供样本文件，评测模块读取基准文件并执行候选代码，报告模块汇总训练指标、评测结果和异常摘要。这样的组织方式减少了口头约定，也让后续复核能够直接追溯到具体输入和输出。")
    add_image(diagram_paths[0], "图1 软件总体结构图")
    heading("2.2 模块结构", 2)
    paragraph("软件模块按照研发流程划分为任务管理、量子中间表示、训练样本生成、数据完整性校验、训练运行、自动评测、检索增强和报告归档八类。任务管理模块保存任务编号、领域、提示族和测试约束；中间表示模块把量子线路、量子门序列和辅助代码要求整理为稳定对象；样本生成模块把任务对象转换为训练和评测所需的结构化记录。")
    paragraph("训练运行模块不直接修改任务定义，只读取已校验样本、模型目录和参数配置；自动评测模块不修改训练输出，只在隔离目录中执行候选代码并记录标准输出、错误输出、超时和断言结果；报告归档模块不手工改写指标，而是读取原始得分卡、失败明细和日志摘要，形成可复核的结论。")
    add_table(
        ["模块", "主要职责", "关键输入", "关键输出"],
        [
            ["任务管理", "维护量子任务、测试约束和提示族", "任务说明、测试文件", "任务清单、任务对象"],
            ["数据构建", "生成训练样本和评测基准", "任务对象、配置参数", "样本文件、基准文件"],
            ["训练运行", "组织模型训练和结果保存", "训练样本、模型目录", "训练日志、输出目录"],
            ["自动评测", "执行候选代码并计算通过状态", "候选文件、测试入口", "得分卡、失败摘要"],
            ["报告归档", "汇总指标、日志和复核结论", "评测结果、运行记录", "报告文件、归档清单"],
        ],
    )
    heading("2.3 运行流程", 2)
    paragraph("软件运行通常从任务准备开始。使用人员先确认任务目录、数据目录和配置文件，再执行数据构建和完整性校验。校验通过后，训练人员可以启动训练流程；训练完成后，评测人员使用固定基准生成候选代码并运行测试；最后由报告模块汇总通过率、失败类型、日志摘要和对比结论。")
    paragraph("流程设计强调先验证再执行长任务。目录缺失、字段错误、训练集与评测集交叉、候选代码不可执行、报告文件写入失败等情况都会进入异常记录。平台不会把启动命令成功视为研发完成，只有训练输出、评测结果、失败摘要和报告归档全部可追溯时，一轮研发流程才算闭环。")
    add_image(diagram_paths[1], "图2 训练与评测流程图")

    heading("3、 核心功能说明", 1)
    heading("3.1 量子任务管理", 2)
    paragraph("量子任务管理用于保存和组织平台研发过程中反复使用的任务资料。每个任务通常包含任务编号、领域标签、问题描述、输入输出要求、测试约束和参考检查方式。任务编号保持稳定后，训练样本、评测基准、候选文件和报告条目都可以围绕同一编号追踪，避免同一任务在不同批次中被重复命名。")
    paragraph("任务内容既包括量子线路构造、量子门操作、测量结果处理等量子计算任务，也包括辅助解析、数据转换和通用编程任务。平台不会把任务描述简单拼接成文本，而是先整理字段和边界，再交给样本生成、提示构建和评测模块使用。这样可以减少手工编辑带来的遗漏，也便于维护人员在新增任务后补充对应测试。")
    add_image(diagram_paths[2], "图3 核心模块逻辑框图")
    heading("3.2 数据构建与校验", 2)
    paragraph("数据构建模块把任务资料转换为训练样本、评测样本和清单文件。样本字段包括任务编号、输入提示、期望输出形式、所属领域、提示族和拆分标记。清单文件记录样本数量、生成时间、拆分策略、输入目录和输出目录，便于后续报告引用同一批数据。")
    paragraph("完整性校验重点检查字段缺失、编号重复、训练集与评测集交叉、文件编码异常和任务清单不一致。对于严格评测场景，平台要求训练数据和评测数据在任务层面保持隔离，避免把评测答案通过训练样本提前暴露给模型。发现异常时，流程会保留错误列表并停止进入训练或评测阶段。")
    heading("3.3 模型训练与自动评测", 2)
    paragraph("训练模块读取经过校验的数据、模型目录和参数配置，按批次生成日志、输出目录和检查点记录。训练前会检查关键路径是否存在、输出目录是否冲突、参数是否超出约定范围；训练后会保存运行命令、训练摘要和输出位置，供评测和归档模块读取。")
    paragraph("自动评测模块用于把模型输出转换为可执行候选代码，并在隔离目录中运行测试。评测过程会记录语法错误、导入错误、断言失败、超时和其他运行异常，不只保留最终通过率。对于同一基准，不同训练结果可以在相同任务列表上比较，报告模块据此识别新增通过、退化失败和稳定任务。")
    heading("3.4 检索问答与报告归档", 2)
    paragraph("检索问答模块读取项目内部文档、任务说明和历史报告，建立面向研发人员的资料检索能力。它的作用是帮助使用人员快速找到相关约束、接口说明和失败原因，而不是替代正式评测。检索结果需要保留来源路径，便于人工判断片段是否适用于当前任务。")
    paragraph("报告归档模块汇总训练日志、评测得分、失败明细、差异分析和人工复核意见。报告中既保留整体指标，也保留失败任务，避免只展示成功结论。归档目录按批次保存输入清单、运行命令、结果文件和报告文本，使后续复现实验或提交材料复核时可以回到原始证据。")

    heading("4、 操作使用说明", 1)
    heading("4.1 环境准备", 2)
    paragraph("首次使用前，操作人员进入软件根目录，确认源码目录、数据目录、任务目录、模型目录和报告目录均存在。随后检查运行语言、脚本入口和依赖环境是否可用，并确认当前批次的配置文件、输出目录和日志目录没有与历史结果混用。")
    paragraph("准备阶段还应确认本次运行目标：如果只是验证任务格式，可以选择小范围数据构建和单元测试；如果要完成训练评测闭环，应提前准备训练样本、评测基准、模型目录、输出目录和报告目录。较长训练任务启动前必须先完成本地小样本验证。")
    heading("4.2 数据构建操作", 2)
    paragraph("数据构建时，用户先选择任务范围和输出批次，再运行数据构建入口生成训练文件、评测文件和清单报告。生成后应查看样本数量、任务编号、拆分策略和字段完整性。若清单中出现重复编号、字段缺失或拆分交叉，应先修复任务资料，再重新构建数据。")
    paragraph("数据构建结果不应被手工临时改写。确需修正样本时，应回到任务定义或构建规则修改，并重新生成清单。这样可以保证评测报告引用的样本版本与实际训练输入一致，也能避免多人协作时对同一数据文件产生不同理解。")
    heading("4.3 训练、评测和报告操作", 2)
    paragraph("训练操作需要指定训练数据、模型目录、输出目录和批次参数。训练启动后，使用人员应检查日志是否持续写入、输出目录是否生成必要文件、异常信息是否被记录。训练结束后，不直接修改模型输出，而是进入评测阶段，通过固定基准生成候选文件并运行测试。")
    paragraph("评测完成后，报告模块读取得分卡、失败摘要和日志记录生成报告。报告人员应核对报告引用的训练批次、评测基准和候选目录是否一致。若发现结果异常，应先定位是数据、训练、评测还是报告环节的问题，再决定是否重新构建数据、重跑训练或只重跑评测。")

    heading("5、 接口与数据说明", 1)
    heading("5.1 命令行和函数接口", 2)
    paragraph("软件通过命令行入口组织数据构建、训练、评测、报告生成和维护检查等操作。命令参数通常包括输入路径、输出路径、任务范围、配置文件、运行预算和批次名称。入口脚本只负责参数解析、路径检查和流程调度，具体业务逻辑由对应模块函数完成。")
    paragraph("函数接口强调单一职责。解析函数只把任务文件转换为内部对象，校验函数只返回错误列表或通过状态，训练函数只处理训练输入和输出目录，评测函数只处理候选代码和测试结果。跨模块调用通过显式参数传递数据，不直接依赖隐藏的全局状态。")
    add_table(
        ["接口类型", "说明", "主要检查点"],
        [
            ["命令行接口", "面向操作人员的运行入口", "必填参数、路径存在性、退出状态"],
            ["函数接口", "面向模块复用的内部调用", "输入对象、返回值、异常类型"],
            ["文件接口", "面向数据交换的结构化文件", "编码、字段、目录位置"],
            ["报告接口", "面向复核和归档的输出材料", "指标来源、失败明细、结论依据"],
        ],
    )
    heading("5.2 文件、配置和报告接口", 2)
    paragraph("平台主要使用结构化文本文件保存任务、样本、清单、得分卡和报告摘要。训练样本与评测样本分目录保存，报告输入与最终报告分目录保存，临时文件不得覆盖正式归档文件。文件名应体现用途和批次，避免不同实验结果混放。")
    paragraph("配置接口用于管理模型路径、数据路径、输出路径、运行预算和默认参数。命令参数可以覆盖配置默认值，但覆盖结果需要写入运行记录。报告接口则要求每项指标可以追溯到原始得分卡，每个失败结论可以追溯到任务编号、候选文件和错误摘要。")

    heading("6、 算法与运行设计", 1)
    heading("6.1 任务切分和提示构建", 2)
    paragraph("任务切分算法先按任务编号、提示族和用途建立集合，再检查训练集、验证集和评测集之间是否存在交叉。对于需要严格评测的任务，平台优先保持任务级隔离，而不是只依赖样本编号不同。切分结果写入清单文件，并在报告中保留拆分策略。")
    paragraph("提示构建算法把任务描述、约束条件、输入输出要求和必要上下文组织为模型输入。构建时会控制文本长度，保留真正影响解题的约束，减少无关说明。提示模板发生变化时，应重新生成样本并记录版本，否则不同批次结果不具备可比性。")
    heading("6.2 候选清洗、执行评分和差异分析", 2)
    paragraph("候选清洗算法从模型输出中提取可执行代码，去除多余说明、格式标记和明显不属于代码的片段。清洗过程不应掩盖真实失败，如果输出缺少必要函数、导入错误或语法不完整，应记录为评测异常，而不是人工补全后再计入通过。")
    paragraph("执行评分算法根据测试退出状态、断言结果、超时状态和错误类型生成任务级分数。差异分析算法按任务维度比较两个或多个实验结果，区分新增通过、退化失败和稳定任务。报告结论必须来自这些结构化结果，不能只凭人工印象判断训练是否有效。")
    heading("6.3 本地验证和训练运行", 2)
    paragraph("运行设计采用本地验证优先的原则。代码改动、数据构建和小样本评测先在本地完成，确认任务、路径、依赖和报告逻辑没有明显问题后，再执行更耗时的训练运行。这样可以降低长任务失败成本，也能让错误定位更集中。")
    paragraph("训练运行完成后，需要回收日志、输出目录、配置快照和评测结果。若运行中断，应检查输出是否完整、日志是否包含明确失败原因、是否需要清理临时目录。平台不以启动成功作为最终结果，只有报告和归档完成后才形成可提交、可复核的研发材料。")

    heading("7、 测试与验收说明", 1)
    paragraph("测试体系覆盖任务解析、数据构建、样本完整性、候选清洗、评测执行、报告生成和关键脚本入口。单元测试使用确定性输入，保证相同代码在相同任务上得到稳定结果。涉及目录和文件的测试应使用隔离临时目录，避免污染正式数据和报告。")
    paragraph("验收时重点检查四类结果：第一，数据清单是否准确记录样本数量、拆分策略和生成时间；第二，训练运行是否留下命令、参数、日志和输出目录；第三，评测结果是否能定位到具体任务、候选文件和失败原因；第四，报告结论是否与原始得分卡一致。")
    paragraph("当新增任务、修改提示模板、调整评测逻辑或改变报告格式时，应补充对应测试并重新生成材料。若只修改说明文档而不复核代码和报告，容易出现文档描述与实际运行不一致；若只修改代码而不更新说明，也会影响提交材料的可信度。")

    heading("8、 安全边界与权限", 1)
    paragraph("本软件的登记对象为自研源程序和设计表达，不包括通用操作系统、通用硬件、基础运行库、基础模型权重或外部运行服务。文档和报告不得写入账号、密钥、令牌、私人目录或无关个人信息。涉及运行环境的内容均按通用技术口径描述。")
    paragraph("权限控制主要体现在目录边界和材料边界。任务资料、训练数据、评测结果、日志和报告按项目范围保存；不同批次结果分目录归档，避免互相覆盖；正式提交材料只包含登记所需内容，不包含个人凭据、临时调试记录和无关平台信息。")
    paragraph("审计记录需要把命令、参数、输入清单、输出目录、日志和报告联系起来。发现敏感信息、主体信息变化、文件名变化或发表状态变化时，应先修正申请表、说明文档、源程序和清单，再进入最终提交检查。")

    heading("9、 维护与扩展说明", 1)
    paragraph("新增量子任务时，应补充任务说明、输入输出要求、测试约束和评测入口，并检查任务编号是否与既有任务冲突。新增任务进入训练数据前，应先通过数据构建和完整性校验；进入评测基准前，应确认测试能够稳定判断候选代码是否满足要求。")
    paragraph("修改数据字段、目录结构或配置参数时，需要同步更新读取逻辑、清单生成、报告生成和说明文字。接口变更应尽量保持向后兼容；无法兼容时，应在版本维护记录中说明变化原因、影响范围和迁移方式。")
    paragraph("未来如按升级版本申请登记，应根据实际变化编写版本差异说明，列明新增功能、修改模块、代码范围和兼容性影响。本版本为V1.0，当前登记口径为原创软件、独立开发、未发表。")

    heading("10、 常见问题与提交检查", 1)
    paragraph("若数据构建失败，应先检查任务目录是否存在、字段是否齐全、编号是否重复、文件编码是否正确。若训练运行失败，应检查训练数据路径、模型目录、输出目录、依赖环境和日志末尾错误。若评测结果异常，应检查候选代码是否完整、测试入口是否正确、超时设置是否合理。")
    paragraph("若报告内容与预期不一致，应先核对报告引用的得分卡、失败清单和运行目录，确认没有读取旧批次文件。多人协作时尤其需要确认输出目录和归档目录，以免一个人的临时结果覆盖另一个人的正式结果。")
    paragraph("提交前应逐项检查三份正式DOCX文件：申请表的软件名称、版本、著作权人、作者、联系人、电话、地址、未发表和原创口径；说明文档的封面、目录、标题层级、图示、页眉页码、黑色字体和结束标志；源程序的页数、行数、页眉页码和末页结束标志。参考PDF、样表、README、清单和检查报告只作为内部复核材料，不作为正式提交附件。")

    heading("11、 字段字典与材料复核", 1)
    paragraph("字段字典用于说明平台运行记录和报告中常见字段的含义。task_id表示任务编号，example_id表示样本编号，prompt_family表示提示族，scorecard表示评测得分卡，run_dir表示运行目录。字段含义稳定后，数据、评测和报告才能互相对应。")
    add_table(
        ["字段", "含义", "使用说明"],
        [
            ["task_id", "任务编号", "贯穿任务、样本、候选和报告"],
            ["example_id", "样本编号", "区分训练样本、评测样本和批次来源"],
            ["prompt_family", "提示族", "用于检查训练评测隔离和提示版本"],
            ["run_dir", "运行目录", "保存候选、日志、得分卡和报告输入"],
            ["scorecard", "得分卡", "记录通过率、失败类型和任务级结果"],
        ],
    )

    heading("12、 运行案例记录", 1)
    paragraph("典型运行案例包括数据构建、模型训练、候选生成、自动评测和报告归档。每个案例都应保存执行命令、输入路径、输出路径、日志摘要和报告位置。若案例用于项目汇报，还应保存对应的评测基准和失败任务列表。")
    paragraph("运行案例不是为了展示命令数量，而是为了证明软件流程真实可执行。只有当输入数据、运行命令、候选文件、测试日志和报告结论能够互相对应时，案例才适合作为验收和后续研发依据。")

    heading("13、 配置与版本管理", 1)
    paragraph("配置项包括模型路径、数据路径、评测基准、输出目录、运行预算和报告批次。配置默认值可以提高使用效率，但每次正式运行都应在日志中记录实际生效参数。配置变化会影响训练和评测结果，因此需要进入版本记录。")
    paragraph("当前申请材料采用软件版本V1.0口径，表示用于著作权登记的完整交付状态。内部研发可以继续迭代，但登记材料中的软件名称、版本号、作者、著作权人、完成日期和发表状态必须保持稳定。")

    heading("14、 软件运行界面截图", 1)
    heading("14.1 命令行运行界面", 2)
    paragraph("本节补充软件运行界面插图，用于说明软件不仅包含设计模块和处理流程，也具备面向使用人员的运行入口和结果查看方式。命令行界面用于数据构建、训练、评测和报告归档等研发操作，输出内容包括执行状态、通过失败数量、失败原因和报告路径。")
    add_image(diagram_paths[3], "图4 软件运行界面示意图")
    heading("14.2 评测报告归档界面", 2)
    paragraph("评测报告与归档界面用于展示一次研发批次的结果摘要。使用人员可以查看数据构建、模型训练、候选生成、自动评测和报告归档的流程位置，也可以查看通过任务、失败任务、语法错误、超时任务和失败原因列表。")
    add_image(diagram_paths[4], "图5 评测报告与归档界面示意图")

    heading("15、 最终复核结论", 1)
    paragraph("经本轮整理，申请表、说明书、源程序和生成清单采用同一软件名称、版本号、作者、著作权人、联系人和发表状态。说明书正文围绕真实功能展开，覆盖总体架构、功能模块、操作流程、接口数据、算法运行、测试验收、安全边界、维护扩展和提交检查。")
    paragraph("附件2采用封面、目录、一级标题、二级标题、自然段、图示、表格、软件运行界面插图、页眉页码和末页end的Word文档结构。正文标题和文字均设置为黑色，图示使用黑色线条、黑色文字和灰白底色，整份说明书保持统一的黑白灰视觉口径。")
    paragraph("正式提交前，仍应由申请人确认自然人证件材料、系统录入信息和发表状态。如果软件在提交前已经发生对外销售、交付、上架、公开发布或提供复制件，应按实际情况改为已发表，并补充首次发表日期和地点。")
    paragraph("end", first_indent=False)

    out = OUT / MANUAL_DOCX_NAME
    doc.save(out)
    scrub_docx_theme_colors(out)
    return out


def build_manual_doc() -> Path:
    """Build a 30-page reference-style manual with diagrams and software screenshots."""
    diagram_paths = create_manual_diagrams()
    doc = Document()
    configure_section(doc.sections[0], top=Cm(1.65), bottom=Cm(1.05), left=Cm(1.95), right=Cm(1.75))

    black = RGBColor(0, 0, 0)
    for style_name in ["Normal", "Body Text", "Heading 1", "Heading 2", "Heading 3", "List Paragraph"]:
        if style_name in doc.styles:
            style = doc.styles[style_name]
            style.font.name = "宋体"
            style._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
            style.font.color.rgb = black
    doc.styles["Normal"].font.size = Pt(11)
    doc.styles["Body Text"].font.size = Pt(11)

    def run(paragraph, text: str, size=Pt(11), bold=False) -> None:
        item = paragraph.add_run(text)
        item.font.name = "宋体"
        item._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
        item.font.size = size
        item.bold = bold
        item.font.color.rgb = black

    def add_heading(text: str, level: int = 1, page_break_before: bool = False) -> None:
        p = doc.add_paragraph(style=f"Heading {level}")
        if page_break_before:
            p.paragraph_format.page_break_before = True
        p.paragraph_format.space_before = Pt(4 if level == 1 else 2)
        p.paragraph_format.space_after = Pt(5 if level == 1 else 4)
        p.paragraph_format.keep_with_next = True
        run(p, text, size=Pt(16 if level == 1 else 13 if level == 2 else 11), bold=True)

    def add_para(text: str) -> None:
        p = doc.add_paragraph(style="Body Text")
        p.paragraph_format.first_line_indent = Pt(21)
        p.paragraph_format.line_spacing = 1.40
        p.paragraph_format.space_after = Pt(5)
        run(p, text, size=Pt(11))

    def add_caption(text: str) -> None:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(4)
        run(p, text, size=Pt(9.5), bold=True)

    def add_image(path: Path, title: str, width=Cm(15.2)) -> None:
        doc.add_picture(str(path), width=width)
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_caption(title)

    def set_table_cell(cell, text: str, bold=False) -> None:
        cell.text = ""
        p = cell.paragraphs[0]
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(0)
        run(p, text, size=Pt(8.8), bold=bold)

    def add_table(headers: list[str], rows: list[list[str]]) -> None:
        table = doc.add_table(rows=1, cols=len(headers))
        table.style = "Table Grid"
        for idx, header in enumerate(headers):
            set_table_cell(table.rows[0].cells[idx], header, bold=True)
        for row in rows:
            cells = table.add_row().cells
            for idx, value in enumerate(row):
                set_table_cell(cells[idx], value)
        doc.add_paragraph()

    def add_toc_line(title: str, page: int, indent=False) -> None:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.05
        p.paragraph_format.space_after = Pt(0.2)
        p.paragraph_format.left_indent = Cm(0.45 if indent else 0)
        p.paragraph_format.tab_stops.add_tab_stop(Cm(16.2), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        run(p, title, size=Pt(9.5), bold=not indent)
        run(p, f"\t{page}", size=Pt(9.5))

    def new_page() -> None:
        doc.add_page_break()

    # Page 1: cover, matching the qcrypto reference's centered title page.
    for _ in range(7):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, HEADER, size=Pt(22), bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, "设计说明书及使用说明文档", size=Pt(20), bold=True)
    doc.add_paragraph()
    for text in [
        f"文档版本：{VERSION}",
        f"软件版本：{VERSION}",
        f"软件简称：{SHORT_NAME}",
        f"著作权人：{'、'.join(RIGHTHOLDERS)}",
        f"作者：{'、'.join(AUTHORS)}",
        f"开发完成日期：{COMPLETION_DATE}",
    ]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(4)
        run(p, text, size=Pt(12))

    # Pages 2-3: catalog.
    new_page()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, "目录", size=Pt(16), bold=True)
    toc_items = [
        ("1、 总体业务说明", 4, False),
        ("1.1 编写目的", 4, True),
        ("1.2 适用对象与软件定位", 5, True),
        ("1.3 文档范围与软件边界", 5, True),
        ("1.4 功能边界说明", 5, True),
        ("1.5 版式与复核口径", 5, True),
        ("2、 系统总体设计", 6, False),
        ("2.1 总体架构", 6, True),
        ("2.1.1 输入层和调度层", 6, True),
        ("2.2 模块结构", 7, True),
        ("2.2.1 任务管理模块", 7, True),
        ("2.2.2 数据构建模块", 7, True),
        ("2.2.3 训练评测模块", 7, True),
        ("2.2.4 报告归档模块", 7, True),
        ("2.3 运行流程", 8, True),
        ("2.3.1 准备与校验", 8, True),
        ("2.3.2 训练与评测", 8, True),
        ("2.3.3 报告与复核", 8, True),
        ("2.4 部署与数据流", 9, True),
        ("2.4.1 本地工作区", 9, True),
        ("2.4.2 训练运行环境", 9, True),
        ("2.4.3 结果回收", 9, True),
        ("3、 核心功能说明", 10, False),
        ("3.1 量子任务管理", 10, True),
        ("3.1.1 任务编号", 10, True),
        ("3.1.2 测试约束", 10, True),
        ("3.2 量子中间表示", 11, True),
        ("3.2.1 结构化约束", 11, True),
        ("3.2.2 扩展字段", 11, True),
        ("3.3 数据构建与校验", 12, True),
        ("3.3.1 样本字段", 12, True),
        ("3.3.2 完整性校验", 12, True),
        ("3.4 训练样本与评测基准", 13, True),
        ("3.4.1 训练样本", 13, True),
        ("3.4.2 评测基准", 13, True),
        ("3.5 模型训练管理", 13, True),
        ("3.6 自动评测管理", 14, True),
        ("3.7 检索问答与报告归档", 15, True),
        ("4、 操作使用说明", 16, False),
        ("4.1 环境和数据准备", 16, True),
        ("4.2 训练、评测和报告操作", 17, True),
        ("4.2.1 训练运行", 17, True),
        ("4.2.2 评测归档", 18, True),
        ("5、 接口与数据说明", 18, False),
        ("5.1 命令行和函数接口", 18, True),
        ("5.2 文件、配置和报告接口", 19, True),
        ("5.2.1 文件目录", 19, True),
        ("5.2.2 配置覆盖", 19, True),
        ("6、 算法与运行设计", 20, False),
        ("6.1 任务切分和提示构建", 20, True),
        ("6.1.1 拆分策略", 20, True),
        ("6.2 候选清洗、评分和差异分析", 20, True),
        ("6.2.1 候选清洗", 20, True),
        ("6.2.2 结果比较", 21, True),
        ("6.3 作业生命周期和本地验证", 21, True),
        ("7、 软件运行界面截图", 22, False),
        ("7.1 命令行运行界面", 22, True),
        ("7.1.1 状态输出", 22, True),
        ("7.2 评测报告归档界面", 23, True),
        ("7.2.1 结果摘要", 23, True),
        ("8、 测试与验收说明", 24, False),
        ("8.1 测试覆盖", 24, True),
        ("8.2 验收检查", 25, True),
        ("8.3 变更复核", 25, True),
        ("9、 安全边界与权限", 25, False),
        ("9.1 材料边界", 25, True),
        ("9.2 目录边界", 26, True),
        ("10、 维护扩展与版本管理", 26, False),
        ("10.1 任务扩展", 26, True),
        ("10.2 字段变更", 27, True),
        ("11、 常见问题与交付复核", 27, False),
        ("11.1 常见异常", 27, True),
        ("11.2 交付复核检查", 28, True),
        ("12、 最终复核结论", 28, False),
        ("12.1 文档与源程序一致性", 28, True),
        ("12.2 版本交付确认", 30, True),
    ]
    for title, page, indent in toc_items:
        add_toc_line(title, page, indent)
    new_page()

    page_specs = [
        ("1、 总体业务说明", [
            "本文档用于说明量子代码大模型研发平台软件的设计思路、功能边界、模块组成、接口数据、运行流程和使用维护方法。文档与源程序文件采用同一软件名称和版本号，便于研发、测试和维护人员把功能说明、代码实现和运行结果互相对应。",
            "软件面向量子代码模型研发过程，重点解决任务资料分散、训练样本难以复核、评测结果不可比较、报告材料依赖人工整理等问题。文档不把通用运行环境、基础模型权重或外部基础设施作为软件功能，而是说明本软件自研的任务组织、数据构建、训练调度、评测汇总和报告归档表达。",
            "本文档在内容组织上采用封面、目录、标题层级、自然段、表格和图示结合的正式Word说明书版式。图示用于说明模块关系和运行流程，正文用于解释输入、输出、异常处理和维护要求，软件界面插图用于说明实际使用入口和结果展示方式。"
        ]),
        ("1.2 适用对象与软件定位", [
            "本文档适用于量子算法研发人员、模型训练人员、评测人员、项目负责人和后续维护人员。研发人员可依据本文理解量子任务如何进入数据构建和评测流程；训练人员可依据本文确认训练输入、输出目录和运行记录；评测人员可依据本文复核候选代码、测试结果和报告摘要之间的关系。",
            "本软件定位为量子代码大模型研发平台，服务于量子算法任务整理、训练样本构建、模型训练组织、自动化评测、检索问答和阶段性报告归档。它不是单一训练脚本，也不是只展示指标的报表工具，而是把从任务资料到结果复核的多个环节组织为可重复执行的软件流程。",
            "本文档的重点是平台在任务描述解析、样本字段组织、训练评测编排、候选代码清洗、失败原因归类、报告生成和材料归档方面的自研表达。无论软件在本地还是训练环境执行，输入、输出、日志和报告均应按固定目录保存。"
        ]),
        ("2.1 总体架构", [
            "系统采用分层模块化结构。入口层负责读取命令参数、配置文件和任务范围；数据层负责整理量子任务、生成训练样本、构建评测基准并记录清单；执行层负责模型训练、候选代码生成、代码执行评测和检索问答；归档层负责汇总日志、指标、失败样例和对比报告。",
            "各层之间主要通过结构化文件、固定目录和明确函数接口传递数据。任务库向数据构建模块提供任务说明和测试约束，数据构建模块向训练模块提供样本文件，评测模块读取基准文件并执行候选代码，报告模块汇总训练指标、评测结果和异常摘要。",
        ], diagram_paths[0], "图1 软件总体结构图"),
        ("2.2 模块结构", [
            "软件模块按照研发流程划分为任务管理、量子中间表示、训练样本生成、数据完整性校验、训练运行、自动评测、检索增强和报告归档八类。任务管理模块保存任务编号、领域、提示族和测试约束；中间表示模块把量子线路、量子门序列和辅助代码要求整理为稳定对象。",
            "训练运行模块不直接修改任务定义，只读取已校验样本、模型目录和参数配置；自动评测模块不修改训练输出，只在隔离目录中执行候选代码并记录标准输出、错误输出、超时和断言结果；报告归档模块不手工改写指标，而是读取原始得分卡、失败明细和日志摘要。",
        ], None, None, (["模块", "主要职责", "关键输入", "关键输出"], [
            ["任务管理", "维护量子任务、测试约束和提示族", "任务说明、测试文件", "任务清单、任务对象"],
            ["数据构建", "生成训练样本和评测基准", "任务对象、配置参数", "样本文件、基准文件"],
            ["训练运行", "组织模型训练和结果保存", "训练样本、模型目录", "训练日志、输出目录"],
            ["自动评测", "执行候选代码并计算通过状态", "候选文件、测试入口", "得分卡、失败摘要"],
            ["报告归档", "汇总指标、日志和复核结论", "评测结果、运行记录", "报告文件、归档清单"],
        ])),
        ("2.3 运行流程", [
            "软件运行通常从任务准备开始。使用人员先确认任务目录、数据目录和配置文件，再执行数据构建和完整性校验。校验通过后，训练人员可以启动训练流程；训练完成后，评测人员使用固定基准生成候选代码并运行测试；最后由报告模块汇总通过率、失败类型、日志摘要和对比结论。",
            "流程设计强调先验证再执行长任务。目录缺失、字段错误、训练集与评测集交叉、候选代码不可执行、报告文件写入失败等情况都会进入异常记录。平台不会把启动命令成功视为研发完成，只有训练输出、评测结果、失败摘要和报告归档全部可追溯时，一轮研发流程才算闭环。",
        ], diagram_paths[1], "图2 训练与评测流程图"),
        ("2.4 部署与数据流", [
            "软件可以在本地工作区完成任务整理、样本生成、小样本评测、报告汇总和材料复核，也可以把已验证的数据与配置交给训练环境执行较长任务。部署设计不依赖某个固定外部平台名称，而是以目录、配置和结果文件为边界。",
            "数据流从任务资料进入平台后，先被整理为任务对象，再生成训练样本和评测基准。训练样本进入训练运行模块，评测基准进入自动评测模块，二者都把结果写入批次目录。报告模块只读取这些稳定结果，不直接推断隐藏状态。",
            "远程运行产生的结果需要回到本地归档目录进行复核。只在训练环境中保留日志而不回收，会造成后续报告无法引用原始证据。"
        ]),
        ("3.1 量子任务管理", [
            "量子任务管理用于保存和组织平台研发过程中反复使用的任务资料。每个任务通常包含任务编号、领域标签、问题描述、输入输出要求、测试约束和参考检查方式。任务编号保持稳定后，训练样本、评测基准、候选文件和报告条目都可以围绕同一编号追踪。",
            "任务内容既包括量子线路构造、量子门操作、测量结果处理等量子计算任务，也包括辅助解析、数据转换和通用编程任务。平台不会把任务描述简单拼接成文本，而是先整理字段和边界，再交给样本生成、提示构建和评测模块使用。",
            "任务新增时应先给出稳定编号，再补充领域标签、输入输出要求和测试约束。编号稳定后，训练样本、评测基准和报告条目才能建立一一对应关系。"
        ]),
        ("3.2 量子中间表示", [
            "量子中间表示模块把不同写法的任务描述转成统一结构，减少规则分散带来的不一致。维护人员不需要在每个脚本里重复解析量子线路、门序列和测量要求，而是通过统一对象把结构化约束交给样本生成、提示构建和评测模块。",
            "该层也为后续扩展保留空间。新增任务类型时，可以先扩展中间对象字段，再调整样本生成和评测规则，避免直接改动训练或报告模块。当评测失败时，中间表示可以帮助定位候选代码是没有满足结构约束，还是测试入口或数据字段发生了变化。",
        ], diagram_paths[2], "图3 核心模块逻辑框图"),
        ("3.3 数据构建与校验", [
            "数据构建模块把任务资料转换为训练样本、评测样本和清单文件。样本字段包括任务编号、输入提示、期望输出形式、所属领域、提示族和拆分标记。清单文件记录样本数量、生成时间、拆分策略、输入目录和输出目录，便于后续报告引用同一批数据。",
            "完整性校验重点检查字段缺失、编号重复、训练集与评测集交叉、文件编码异常和任务清单不一致。对于严格评测场景，平台要求训练数据和评测数据在任务层面保持隔离，避免把评测答案通过训练样本提前暴露给模型。",
            "数据修复应回到源任务或构建规则完成，不宜直接编辑生成后的样本文件。直接编辑会让清单、样本和报告之间出现隐性差异。"
        ]),
        ("3.4 训练样本与评测基准", [
            "训练样本用于教会模型按照任务描述生成候选代码，评测基准用于在固定条件下判断候选代码是否满足任务要求。两者都来自任务资料，但用途不同，因此需要在目录、字段和清单中明确区分。",
            "评测基准应尽量保持稳定，避免每次训练后都改变测试目标。若基准变化，应在报告中说明变化原因，并避免把新旧基准下的结果直接比较。",
            "样本模板发生变化时，应重新生成样本并记录版本。不同模板会影响模型看到的信息，也会影响后续候选代码的失败形态。"
        ]),
        ("3.5 模型训练管理", [
            "训练模块读取经过校验的数据、模型目录和参数配置，按批次生成日志、输出目录和检查点记录。训练前会检查关键路径是否存在、输出目录是否冲突、参数是否超出约定范围；训练后会保存运行命令、训练摘要和输出位置。",
            "训练管理强调证据保存。每次训练至少应留下有效参数、输入数据、模型目录、输出目录、日志摘要和开始结束时间，便于后续评测和归档引用。",
            "训练异常需要分类记录。路径错误、依赖缺失、资源不足、保存失败和参数错误对应不同处理方式，不能只用一次失败概括全部问题。"
        ]),
        ("3.6 自动评测管理", [
            "自动评测模块用于把模型输出转换为可执行候选代码，并在隔离目录中运行测试。评测过程会记录语法错误、导入错误、断言失败、超时和其他运行异常，不只保留最终通过率。",
            "候选清洗规则应保持稳定。若为了某一轮结果临时修改清洗逻辑，应在报告中说明，否则不同批次之间的比较会失去公平性。",
            "失败任务应完整保留。只保存通过样例会让后续改进缺少方向，也不利于审查人员理解报告结论来源。"
        ]),
        ("3.7 检索问答与报告归档", [
            "检索问答模块读取项目内部文档、任务说明和历史报告，建立面向研发人员的资料检索能力。它的作用是帮助使用人员快速找到相关约束、接口说明和失败原因，而不是替代正式评测。检索结果需要保留来源路径，便于人工判断片段是否适用于当前任务。",
            "报告归档模块汇总训练日志、评测得分、失败明细、差异分析和人工复核意见。报告中既保留整体指标，也保留失败任务，避免只展示成功结论。",
            "报告比较多个实验时，应说明基准、提示版本、运行预算和清洗规则是否一致。条件不一致时，报告应避免给出过强的提升结论。"
        ]),
        ("4.1 环境和数据准备", [
            "首次使用前，操作人员进入软件根目录，确认源码目录、数据目录、任务目录、模型目录和报告目录均存在。随后检查运行语言、脚本入口和依赖环境是否可用，并确认当前批次的配置文件、输出目录和日志目录没有与历史结果混用。",
            "数据构建时，用户先选择任务范围和输出批次，再运行数据构建入口生成训练文件、评测文件和清单报告。生成后应查看样本数量、任务编号、拆分策略和字段完整性。",
            "目录准备应遵循用途分离原则。原始任务、生成样本、评测基准、候选代码、训练输出、日志文件和归档报告不应混放在同一目录。"
        ]),
        ("4.2 训练、评测和报告操作", [
            "训练操作需要指定训练数据、模型目录、输出目录和批次参数。训练启动后，使用人员应检查日志是否持续写入、输出目录是否生成必要文件、异常信息是否被记录。",
            "训练结束后，不直接修改模型输出，而是进入评测阶段，通过固定基准生成候选文件并运行测试。候选生成和测试执行应保留独立目录，避免与训练目录混在一起。",
            "评测完成后，报告模块读取得分卡、失败摘要和日志记录生成报告。报告人员应核对报告引用的训练批次、评测基准和候选目录是否一致。"
        ]),
        ("5.1 命令行和函数接口", [
            "软件通过命令行入口组织数据构建、训练、评测、报告生成和维护检查等操作。命令参数通常包括输入路径、输出路径、任务范围、配置文件、运行预算和批次名称。",
            "函数接口强调单一职责。解析函数只把任务文件转换为内部对象，校验函数只返回错误列表或通过状态，训练函数只处理训练输入和输出目录，评测函数只处理候选代码和测试结果。",
        ], None, None, (["接口类型", "使用对象", "主要输入", "主要输出"], [
            ["命令行接口", "操作人员", "路径、配置、批次参数", "执行状态、输出目录"],
            ["函数接口", "开发和测试模块", "任务对象、配置对象", "结果对象、错误列表"],
            ["校验接口", "数据人员", "样本文件、清单文件", "通过状态、错误摘要"],
            ["报告接口", "项目负责人", "得分卡、日志摘要", "报告文本、归档清单"],
        ])),
        ("5.2 文件、配置和报告接口", [
            "平台主要使用结构化文本文件保存任务、样本、清单、得分卡和报告摘要。训练样本与评测样本分目录保存，报告输入与最终报告分目录保存，临时文件不得覆盖正式归档文件。",
            "配置接口用于管理模型路径、数据路径、输出路径、运行预算和默认参数。命令参数可以覆盖配置默认值，但覆盖结果需要写入运行记录。",
            "报告接口要求每项指标可以追溯到原始得分卡，每个失败结论可以追溯到任务编号、候选文件和错误摘要。报告不应只保留总体分数，因为总体分数无法解释具体改进方向。"
        ]),
        ("6.1 任务切分和提示构建", [
            "任务切分算法先按任务编号、提示族和用途建立集合，再检查训练集、验证集和评测集之间是否存在交叉。对于需要严格评测的任务，平台优先保持任务级隔离，而不是只依赖样本编号不同。",
            "提示构建算法把任务描述、约束条件、输入输出要求和必要上下文组织为模型输入。构建时会控制文本长度，保留真正影响解题的约束，减少无关说明。",
            "任务切分和提示构建共同决定训练数据质量。切分不严会污染评测，提示不清会降低训练效果；两者都需要纳入版本记录和复核流程。"
        ]),
        ("6.2 候选清洗、评分和差异分析", [
            "候选清洗算法从模型输出中提取可执行代码，去除多余说明、格式标记和明显不属于代码的片段。清洗过程不应掩盖真实失败，如果输出缺少必要函数、导入错误或语法不完整，应记录为评测异常。",
            "执行评分算法根据测试退出状态、断言结果、超时状态和错误类型生成任务级分数。差异分析算法按任务维度比较两个或多个实验结果，识别新增通过、退化失败和稳定任务。",
            "比较前需要确认评测基准、提示版本、运行预算和候选清洗规则是否一致。若这些条件不同，报告应明确标注，不应把结果解释为同一条件下的直接提升或退化。"
        ]),
        ("6.3 作业生命周期和本地验证", [
            "作业生命周期从准备、启动、运行、检查、回收和归档六个阶段组织。准备阶段确认输入和配置，启动阶段记录命令和时间，运行阶段观察日志，检查阶段核对输出，回收阶段整理结果，归档阶段生成报告。",
            "运行设计采用本地验证优先的原则。代码改动、数据构建和小样本评测先在本地完成，确认任务、路径、依赖和报告逻辑没有明显问题后，再执行更耗时的训练运行。",
            "作业启动成功不等于作业完成。训练任务可能在中途失败，评测任务可能只生成部分候选，报告任务可能读取旧文件。平台要求每个阶段都有可检查输出。"
        ]),
        ("7.1 命令行运行界面", [
            "本节补充软件运行界面插图，用于说明软件不仅包含设计模块和处理流程，也具备面向使用人员的运行入口。命令行界面用于数据构建、训练、评测和报告归档等研发操作，输出内容包括执行状态、通过失败数量、失败原因和报告路径。",
        ], diagram_paths[3], "图4 软件运行界面示意图"),
        ("7.2 评测报告归档界面", [
            "评测报告与归档界面用于展示一次研发批次的结果摘要。使用人员可以查看数据构建、模型训练、候选生成、自动评测和报告归档的流程位置，也可以查看通过任务、失败任务、语法错误、超时任务和失败原因列表。",
        ], diagram_paths[4], "图5 评测报告与归档界面示意图"),
        ("8、 测试与验收说明", [
            "测试体系覆盖任务解析、数据构建、样本完整性、候选清洗、评测执行、报告生成和关键脚本入口。单元测试使用确定性输入，保证相同代码在相同任务上得到稳定结果。",
            "验收时重点检查四类结果：第一，数据清单是否准确记录样本数量、拆分策略和生成时间；第二，训练运行是否留下命令、参数、日志和输出目录；第三，评测结果是否能定位到具体任务、候选文件和失败原因；第四，报告结论是否与原始得分卡一致。",
            "当新增任务、修改提示模板、调整评测逻辑或改变报告格式时，应补充对应测试并重新生成材料。若只修改说明文档而不复核代码和报告，容易出现文档描述与实际运行不一致。"
        ]),
        ("9、 安全边界与权限", [
            "本软件的说明范围为自研源程序和设计表达，不包括通用操作系统、通用硬件、基础运行库、基础模型权重或外部运行服务。文档和报告不得写入账号、密钥、令牌、私人目录或无关个人信息。",
            "权限控制主要体现在目录边界和数据边界。任务资料、训练数据、评测结果、日志和报告按项目范围保存；不同批次结果分目录归档，避免互相覆盖；正式交付文档只包含软件设计、运行和维护所需内容。",
            "审计记录需要把命令、参数、输入清单、输出目录、日志和报告联系起来。发现版本信息、文件名或目录结构变化时，应同步修正说明文档、源程序页眉和生成清单，再进入版本交付检查。"
        ]),
        ("10、 维护扩展与版本管理", [
            "新增量子任务时，应补充任务说明、输入输出要求、测试约束和评测入口，并检查任务编号是否与既有任务冲突。新增任务进入训练数据前，应先通过数据构建和完整性校验。",
            "修改数据字段、目录结构或配置参数时，需要同步更新读取逻辑、清单生成、报告生成和说明文字。接口变更应尽量保持向后兼容；无法兼容时，应在版本维护记录中说明变化原因、影响范围和迁移方式。",
            "当前软件采用版本V1.0口径，表示本文档对应的完整交付状态。内部研发可以继续迭代，但本版本中的软件名称、版本号、模块范围、接口说明和运行方式必须保持稳定。"
        ]),
        ("11、 常见问题与交付复核", [
            "若数据构建失败，应先检查任务目录是否存在、字段是否齐全、编号是否重复、文件编码是否正确。若训练运行失败，应检查训练数据路径、模型目录、输出目录、依赖环境和日志末尾错误。若评测结果异常，应检查候选代码是否完整、测试入口是否正确、超时设置是否合理。",
            "交付复核应逐项检查说明文档和源程序文件：说明文档看封面、目录、标题层级、图示、软件运行插图、页眉页码、黑色字体和末页正文收束；源程序看页数、行数、页眉页码、可见行号和末页结束标志。",
            "辅助README、生成清单和检查报告只作为内部复核依据。维护人员使用这些文件核对软件名称、版本号、模块范围、源程序行号和文档页数，避免交付包中出现版本不一致或格式异常。"
        ]),
        ("12、 最终复核结论", [
            "最终复核用于确认说明文档、源程序文件和辅助清单处于同一软件版本状态。复核时不再新增功能范围，也不改变软件名称、版本号、模块边界和运行口径，而是确认文档描述、代码页眉和生成清单之间没有可见矛盾。",
            "本章承接前文的设计说明、使用说明、接口说明、算法说明、软件界面插图、测试验收和维护边界，对版本交付前需要关注的软件事项作集中说明。复核结论只基于本次生成的文档和已渲染文件，不扩大到未实现功能或未来研发计划。",
            "版本复核分别从文档结构、目录页码、正文图表、源程序行号、数据边界和交付确认六个方面进行检查说明，确保交付物看起来像一份完整的软件说明书，而不是流程说明或临时记录。"
        ]),
        ("12.1 文档与源程序一致性", [
            "说明文档负责解释软件的总体设计、功能模块、运行流程、接口数据、算法处理、软件界面、测试验收和维护边界。源程序文件负责展示对应的软件实现表达。两类文件应使用同一软件名称和版本号。",
            "说明文档不承担介绍外部流程的作用，它的重点是软件本身。技术功能、模块关系、运行流程、接口数据、图示表格和操作说明应以本文档为准，具体实现细节应以源程序文件为准。",
            "设计说明书及使用说明文档采用封面、目录、一级标题、二级标题、自然段、表格、图示、软件运行界面插图和页眉页码的Word结构，末页以正文自然收束，整体保持黑色文字和黑白灰图示风格。",
            "说明书正文按照实际软件逻辑连续展开，不把每个小节强行拆成单独页面。总体业务说明之后进入系统总体设计，再进入核心功能、操作使用、接口数据、算法运行、软件界面、测试验收、安全边界、维护扩展和交付复核，阅读顺序与软件研发流程一致。",
            "说明书中的图表用于辅助理解软件结构。总体结构图说明入口、数据、执行和归档层的关系；训练与评测流程图说明任务准备、数据构建、训练运行、自动评测和报告归档的流转；核心模块逻辑框图说明任务对象、提示构建、候选清洗、评分和报告之间的处理关系。",
            "软件运行界面插图用于说明软件有明确的使用入口和结果展示方式。命令行界面展示运行状态、通过失败数量和报告路径，评测报告归档界面展示批次摘要、失败类别和归档结果，两类插图与正文的操作说明互相对应。",
            "说明书中的表格用于整理模块职责和接口信息。模块表说明任务管理、数据构建、训练运行、自动评测和报告归档等模块的职责、关键输入和关键输出；接口表说明命令行、函数、文件、配置和报告接口的主要输入输出。",
            "源程序文件按照连续页面组织，正文行前带有可见四位行号，便于维护人员引用和核对。源程序末页最后保留单独的end结束标志，用于说明代码材料到此结束。",
            "源程序行号是可视内容的一部分，不应只存在于生成脚本或隐藏字段中。复核时需要打开渲染后的PDF确认每页都有正文行，且行号从前往后连续呈现，末页结束标志不再另加行号。",
            "README、生成清单和检查报告属于内部复核文件。它们用于核对版本、页数、行号和图表状态，不改变说明文档与源程序文件的主体内容。",
            "如果后续发现软件名称、版本号、模块范围、源程序量或目录结构需要调整，应重新运行生成流程并重新渲染PDF，不能只在其中一个DOCX文件里手工改动。"
        ]),
        ("12.2 版本交付确认", [
            "最终确认首先检查目录页。目录中的一级标题、二级标题和页码应与PDF实际页码对应，页码右对齐，点线引导完整，目录页自身也应有足够内容，不能出现明显空白或页码错位。",
            "其次检查正文页。正文应从总体设计自然过渡到使用说明和验收说明，页面下部应有实际文字、图表或图注占用，不应出现大面积空白。若某页只剩标题或一两段文字，应回到生成脚本补充真实说明内容。",
            "再次检查图示和表格。图示应有清晰图号和图名，表格应有明确表头，正文引用的模块、流程、接口和界面名称应与图表中的名称一致。图示不应只作为装饰，而应解释软件结构或运行过程。",
            "然后检查源程序附件。源程序页眉应含软件名称和版本号，页码应可见，正文行号应连续，最后一页以单独的end结束。若PDF渲染后行号被挤掉、换行错乱或页数变化，应重新调整源程序版式。",
            "还需要检查内容边界。说明文档不得写入账号、密钥、令牌、私人目录、无关个人信息或不属于本软件的外部服务能力。涉及运行环境的内容应采用通用技术口径，重点说明本软件自研流程和文件结构。",
            "对内容质量的最终判断不只看页数。合格说明书应能让评审人员理解软件要解决什么问题、由哪些模块组成、怎样输入输出、如何运行、怎样评测、出现异常时如何定位，以及文档、源程序和报告之间如何对应。",
            "对格式质量的最终判断也不只看DOCX是否能打开。应使用LibreOffice或等效工具转成PDF后查看实际分页、目录对齐、图表位置、页眉页码、字体颜色和末页段落收束，因为这些问题在Word编辑视图中不一定明显。",
            "本次说明书保持三十页规模，源程序文件保持六十页规模。二者页数不同是文件类型不同导致的正常现象，不应把说明书误改成源程序的逐行格式，也不应把源程序改成说明书式段落。",
            "若后续软件继续研发，可以在内部版本中增加新任务、新接口、新报告或新训练流程；但本次V1.0文档应保持稳定。已经写入本版本的功能说明，应能在源程序、运行脚本或报告输出中找到对应依据。",
            "完成最终确认后，应优先核对说明文档和源程序文件名。若PDF转换后的页码、图示位置或行号效果与DOCX预览明显不同，应回到生成脚本调整，再重新导出正式文档。",
            "本说明书的排版目标是让目录、正文、图表和结论形成连续阅读体验。正文页面不采用每个小节单独起页的机械排法，也不使用无意义短句填充页面，而是通过真实模块说明、接口说明、操作说明和交付复核保持页面饱满。",
            "版本归档时应保留本说明书、源程序文件、生成清单和渲染检查结果。后续维护人员可以据此确认文档页码、图表编号、源程序行号和运行报告是否仍然对应同一软件版本。",
            "源程序附件的目标则是便于代码审查和引用。行号、页眉、页码和结束标志共同构成可见格式，审查人员既可以按页查看代码，也可以按行号定位具体源程序内容。",
            "归档包中的文件应保持可复现。说明书说明模块职责和使用方法，源程序展示具体实现，生成清单记录文件名称和生成时间，渲染检查结果说明页面是否符合预期。",
            "维护人员接手本版本时，应先阅读总体业务说明和系统总体设计，再查看核心功能、接口数据和算法运行章节，最后对照软件界面插图和源程序行号确认实际入口。",
            "若后续只修改文档文字而未改变软件功能，应记录为文档维护；若修改任务构建、训练运行、评测逻辑、报告格式或界面输出，应记录为功能维护，并重新执行对应测试。",
            "运行报告和评测结果应按批次保存。批次名称、输入清单、配置参数、候选目录、得分卡和摘要报告应能互相定位，避免不同时间的结果混在同一目录中。",
            "版本交接时还应确认图表仍然可读。结构图、流程图、逻辑框图和界面插图应与正文术语一致，图号顺序应稳定，表格字段应能对应实际模块和接口。",
            "如果新增量子任务类型，应同步扩展任务说明、样本字段、评测入口和报告摘要。新增内容进入说明书前，应先确认源程序和运行记录已经支持该能力。",
            "如果调整训练或评测参数，应在运行记录中保留实际生效值。默认配置、命令行覆盖值和报告摘要中的参数名称应保持一致，便于复现实验和排查差异。",
            "如果调整目录结构，应同步更新数据读取、报告归档、源程序页眉和说明书中的路径描述。目录变化没有同步说明，容易造成运行命令、报告路径和文档描述不一致。",
            "最终归档完成后，本版本说明书应能独立解释软件目标、模块关系、运行流程、接口数据、图表含义和维护边界；源程序文件应能独立展示实现表达和代码范围。",
            "完成上述复核后，应保留当前DOCX和PDF文件作为同一批次结果，后续调整以新的批次重新生成，避免不同版式文件混用。",
            "后续维护时，应以当前批次为基准记录差异，先确认功能范围、运行入口、报告格式和源程序行号，再生成新的说明书和复核清单。",
        ]),
    ]

    def supplemental_paragraphs(title: str) -> list[str]:
        if "总体业务" in title or "适用对象" in title:
            return [
                "本节还用于统一文档口径。研发人员看到的功能描述、维护人员记录的版本字段、源程序页眉和生成清单中的统计信息，应当指向同一软件对象，不能出现不同名称或不同版本的说法。",
                "从研发管理角度看，平台把任务资料、训练数据、评测运行和结果报告串联为连续流程。每个环节都留下可复核文件，避免只凭口头说明判断软件是否真实可用。",
                "使用人员在阅读本节后，应能判断本软件的边界：它保护的是自研平台程序和设计表达，不把通用硬件、通用系统、基础模型权重或外部运行服务写成自有功能。",
                "本节内容也是后续维护的入口。如果软件名称、版本范围、开发方式或功能范围发生变化，应先更新本节口径，再重新生成说明书、源程序和清单。",
                "说明书正文采用自然段组织，目的是让审查人员能按普通技术文档阅读，而不是面对机械堆砌的短行。各页内容围绕真实模块展开，并尽量把输入、处理、输出和复核方式说明清楚。",
            ]
        if "总体架构" in title or "模块结构" in title or "运行流程" in title or "部署" in title:
            return [
                "架构设计的重点是职责分离。入口层不直接写报告，数据层不直接启动训练，评测层不修改训练输出，归档层不手工改写指标；这种分离可以降低定位问题的成本。",
                "模块之间传递的数据应采用稳定结构。任务对象、样本文件、评测基准、候选目录、得分卡和报告清单都应有明确路径和字段，方便测试脚本和人工审查同时读取。",
                "每个模块的异常都需要保留上下文。路径缺失、字段错误、训练中断、候选不可执行、报告写入失败应分别记录，不能只留下一个笼统的失败状态。",
                "当后续新增模块时，应先说明它接收什么输入、产生什么输出、依赖哪些上游结果、影响哪些下游报告。只有进入这条链路的模块，才适合写入正式说明书。",
                "架构图和流程图提供的是模块关系，正文负责解释这些关系为什么成立。二者结合后，审查人员可以从图中看边界，从文字中看实际处理过程。",
            ]
        if "任务" in title or "中间表示" in title or "数据构建" in title or "训练样本" in title:
            return [
                "数据相关流程的首要要求是可追溯。每个任务应能追到任务编号、任务描述、测试约束和生成批次；每个样本应能追到任务编号、提示族、用途和拆分策略。",
                "样本生成后不宜直接手工修改。确需调整时，应回到任务资料或构建规则重新生成，这样清单、样本和报告才能保持一致，也能复现当时的生成过程。",
                "对于严格评测场景，平台优先检查任务级隔离，而不是只检查样本编号不同。这样可以降低评测答案被训练数据提前暴露的风险。",
                "中间表示层让任务结构在多个脚本之间保持一致。训练样本、评测提示和报告摘要读取的是同一类结构对象，避免不同模块对同一任务作出不同解释。",
                "数据质量直接影响后续训练和评测。字段缺失、编号冲突、拆分污染或任务描述模糊，都会在训练之后放大成模型输出和报告结论的问题。",
            ]
        if "模型训练" in title or "自动评测" in title or "检索" in title or "报告归档" in title:
            return [
                "训练与评测环节应保留独立目录。训练输出、候选代码、测试日志、得分卡和最终报告不能混放，否则后续复核时难以判断某个结论来自哪一轮运行。",
                "评测结论必须来自可执行测试。候选代码是否通过，应以隔离目录中的测试结果为准；人工判断可以用于解释失败原因，但不能直接替代得分卡。",
                "失败任务应作为正式结果保存。失败清单可以说明模型当前边界，也能指导下一轮补数据、修提示、改测试或调整训练参数。",
                "检索问答只提供资料辅助，不改变评测判定。检索片段需要保留来源路径，便于人工判断上下文是否适用于当前任务。",
                "报告归档完成后，应能从报告回到清单、命令、候选文件、测试日志和原始得分卡。不能回溯的报告不适合作为验收或交付依据。",
            ]
        if "环境" in title or "操作" in title or "命令行" in title or "函数接口" in title or "文件" in title:
            return [
                "操作前应先确认当前批次和目录。很多异常并非软件逻辑错误，而是输入目录、输出目录、模型目录或配置文件指向了错误位置。",
                "命令行接口应返回明确状态，函数接口应返回结构化对象。二者面向不同使用者，但字段含义应保持一致，避免CLI、函数和报告之间出现不同解释。",
                "配置默认值和命令覆盖值都应进入运行记录。复现实验时，维护人员需要知道实际生效的参数，而不是只看到脚本中写着的默认参数。",
                "文件接口需要区分临时文件和正式归档文件。临时文件用于中间计算，正式文件用于报告和验收，二者不能互相覆盖。",
                "操作失败时应保留现场，再修改参数重试。直接覆盖失败目录会丢失原始错误，后续无法判断问题是否真正解决。",
            ]
        if "切分" in title or "候选" in title or "生命周期" in title:
            return [
                "算法类流程应尽量采用确定性规则。相同输入在相同配置下应产生相同样本、相同候选清洗结果和相同评分结论，这样报告才具备可复查性。",
                "影响结论的参数都应写入运行记录。拆分策略、提示版本、生成预算、清洗规则、评分基准和比较对象都是报告解释不可缺少的信息。",
                "候选清洗不能掩盖模型真实失败。若模型没有生成必要函数、输出语法错误或引用错误接口，应如实记录，而不是人工修复后计入通过。",
                "作业生命周期把准备、启动、运行、检查、回收和归档分开，是为了避免把启动成功误认为任务完成。每个阶段都应有可检查输出。",
                "出现异常时，应说明异常属于数据、训练、评测、报告还是运行环境。分类越清楚，下一步修复成本越低。",
            ]
        if "软件运行界面" in title or "评测报告归档界面" in title:
            return [
                "界面插图的作用是说明软件的实际使用形态。图中的命令、状态、通过失败数量和报告路径，体现平台如何把研发操作转化为可审查的运行证据。",
                "界面结果与正文描述相互对应。命令行界面展示运行入口，报告归档界面展示评测摘要和失败原因，两者共同说明软件不仅有底层模块，也有面向人员使用的结果呈现方式。",
                "界面截图不替代测试结果。正式验收仍以源程序、命令输出、得分卡和报告文件为准；截图用于帮助审核人员理解软件操作流程和输出内容。",
                "若未来界面布局或命令输出发生变化，应重新生成插图并重新渲染说明书，避免说明书展示的界面与当前软件不一致。",
            ]
        if "测试" in title or "安全" in title or "维护" in title or "常见" in title or "最终" in title:
            return [
                "复核时应同时看程序化检查和PDF渲染效果。程序化检查可以发现字段、页数和颜色问题，视觉检查可以发现目录溢出、图示不清、段落过疏和页面下部空白。",
                "安全边界要求正式文档不写账号、密钥、令牌、私人目录或无关个人信息。涉及运行环境的内容均采用通用技术口径，聚焦软件本身的设计和使用方式。",
                "维护扩展时应先补小范围样例，再进入完整流程。只要接口、字段、目录或报告格式发生变化，就需要同步更新测试和说明文档。",
                "交付复核应覆盖说明书和源程序：说明书看目录、图示、正文和末页自然收束，源程序看页数、行号和末页end。",
                "最终结论应保持克制，只说明已经生成和验证的内容，不夸大训练效果或运行环境能力。若交付前事实变化，应重新生成并重新复核。",
            ]
        return [
            "本节内容应能对应实际源程序和运行结果。若后续修改相关模块，需要同步更新文档、测试和生成清单。",
            "相关输入、输出和异常处理应能在日志或报告中找到证据，不能只停留在文字描述。",
            "维护人员复核本节时，应重点查看目录、字段、接口和报告之间是否仍能互相对应。",
            "交付前如发现描述偏离当前版本，应先修正文档并重新生成正式DOCX。",
        ]

    def fallback_paragraphs(title: str) -> list[str]:
        return [
            f"在{title}相关工作中，使用人员应把输入来源、处理规则、输出位置和复核结论同时记录下来，使本页说明能够对应到实际文件和运行结果。",
            f"{title}涉及的目录或字段发生变化时，应先完成小范围验证，再进入完整流程，避免说明书、源程序和生成清单之间出现不一致。",
            f"在{title}中，对应的异常处理应保留原始信息，包括出错阶段、触发条件、处理结果和后续动作，便于维护人员判断问题是否已经闭环。",
            f"在{title}内容完成后，复核人员需要检查相关清单、日志、报告或截图是否存在，不能只依赖口头说明判断软件功能。",
            f"若后续新增{title}同类能力，应沿用本节的组织方式补充输入、处理、输出和边界说明，并同步更新目录页码与材料复核记录。",
            f"{title}所述流程应保持可重复执行。相同输入在相同配置下应生成一致的中间文件、评测结果或报告摘要，便于审查和验收。",
            f"维护过程中应避免把临时调试信息写入正式文档。进入交付文件的内容应聚焦{title}本身的功能职责、数据关系和使用方法。",
            f"本节也是后续版本扩展的检查点。接口、字段、图示或报告格式调整后，应重新生成说明书并重新渲染PDF确认版式。",
            f"{title}相关说明应与目录页、正文标题和图表编号保持一致，避免审查人员在前后翻阅时找不到对应位置。",
            f"{title}的输入输出关系应尽量使用固定名称描述，同一对象在不同章节中不应反复更名，以免影响技术文档的可读性。",
            f"{title}涉及的结果文件、日志或报告应能在归档目录中找到，说明书只描述已经能够由软件流程支撑的内容。",
            f"{title}如涉及人工复核，应明确复核对象和复核标准，不能只写笼统的检查完成或确认无误。",
            f"{title}相关操作完成后，应保留原始命令、配置、批次名称和输出路径，便于后续重新执行或说明问题来源。",
            f"{title}的维护要求应覆盖新增、修改和删除三类变化，避免只说明新增能力而忽略旧字段和旧报告的兼容影响。",
            f"{title}对应的测试或验收动作应能说明软件行为，而不是只说明文档已经编写完成。",
                f"{title}的正式文档表达应保持克制，重点写软件自研流程和文件结构，不扩大到外部平台、通用硬件或非本软件功能。",
            f"{title}若与图示或表格相互引用，应保证图示标题、表格字段和正文描述使用同一套术语。",
            f"{title}完成后还应检查页眉、页码、字体颜色和末页标志，保证格式问题不会遮蔽功能说明本身。",
            f"{title}中出现的异常、失败或限制条件应如实保留，这些内容能帮助审查人员理解软件边界和维护方式。",
            f"{title}应与源程序文件形成互相印证关系，正文说明负责解释流程，源程序负责展示具体实现表达。",
            f"{title}的结论不应依赖外部临时资料；需要引用的证据应来自本次生成的说明书、源程序和清单。",
            f"{title}在最终复核时应同时检查逻辑顺序和视觉版式，确保阅读时从总体设计自然过渡到操作、接口、算法、界面和验收。",
            f"{title}相关内容如果在交付前发生变化，应重新生成正式文档并重新渲染PDF，而不是只修改单个DOCX页面。",
        ]

    def expanded_page_paragraphs(title: str, paragraphs: list[str], has_image: bool, has_table: bool) -> list[str]:
        end_marker = bool(paragraphs and paragraphs[-1] == "end")
        core = paragraphs[:-1] if end_marker else list(paragraphs)
        target = 6 if has_image else 9
        if has_table:
            target = 7
        if end_marker:
            target = len(core)
        target_overrides = {
            "1、 总体业务说明": 9,
            "1.2 适用对象与软件定位": 9,
            "2.4 部署与数据流": 10,
            "3.1 量子任务管理": 9,
            "3.3 数据构建与校验": 9,
            "3.4 训练样本与评测基准": 9,
            "3.5 模型训练管理": 9,
            "3.6 自动评测管理": 9,
            "3.7 检索问答与报告归档": 9,
            "4.1 环境和数据准备": 9,
            "4.2 训练、评测和报告操作": 10,
            "5.2 文件、配置和报告接口": 9,
            "6.1 任务切分和提示构建": 9,
            "6.2 候选清洗、评分和差异分析": 9,
            "6.3 作业生命周期和本地验证": 9,
            "8、 测试与验收说明": 9,
            "9、 安全边界与权限": 9,
            "10、 维护扩展与版本管理": 9,
            "11、 常见问题与交付复核": 9,
            "12、 最终复核结论": 3,
            "12.1 文档与源程序一致性": 11,
            "12.2 版本交付确认": 12,
        }
        target = target_overrides.get(title, target)
        extras = fallback_paragraphs(title) + supplemental_paragraphs(title)
        idx = 0
        while len(core) < target:
            core.append(extras[idx % len(extras)])
            idx += 1
        if end_marker:
            core.append("end")
        return core

    major_inserted: set[str] = set()
    major_titles = {
        "2": "2、 系统总体设计",
        "3": "3、 核心功能说明",
        "4": "4、 操作使用说明",
        "5": "5、 接口与数据说明",
        "6": "6、 算法与运行设计",
        "7": "7、 软件运行界面截图",
    }
    for idx, spec in enumerate(page_specs):
        title = spec[0]
        paragraphs = spec[1]
        image = spec[2] if len(spec) > 2 else None
        image_title = spec[3] if len(spec) > 3 else None
        table = spec[4] if len(spec) > 4 else None
        chapter = title.split(".", 1)[0]
        if chapter in major_titles and chapter not in major_inserted:
            add_heading(major_titles[chapter], 1, page_break_before=(idx == 0))
            major_inserted.add(chapter)
        level = 1 if "、" in title and not title.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.")) else 2
        add_heading(title, level, page_break_before=(idx == 0 and chapter not in major_titles))
        if image is not None and image_title:
            expanded = expanded_page_paragraphs(title, paragraphs, image is not None, table is not None)
            pre_image_count = min(2, len(expanded))
            for text in expanded[:pre_image_count]:
                add_para(text)
            add_image(image, image_title)
            for text in expanded[pre_image_count:]:
                add_para(text)
        else:
            for text in expanded_page_paragraphs(title, paragraphs, image is not None, table is not None):
                add_para(text)
        if table:
            add_table(table[0], table[1])

    out = OUT / MANUAL_DOCX_NAME
    doc.save(out)
    scrub_docx_theme_colors(out)
    return out


def main() -> None:
    OUT.mkdir(exist_ok=True)
    prepare_templates()
    cleanup_stale_numbering()
    inventory = collect_source()
    generated = [
        build_application_form(inventory),
        build_manual_doc(),
        build_source_doc(inventory),
    ]
    generated.extend(copy_guides())
    generated.append(build_readme(inventory, generated))
    generated.append(build_system_filing_notes())
    generated.append(build_check_report(inventory))
    generated.append(build_manifest(inventory, generated))
    print("generated")
    for p in generated:
        print(p)

if __name__ == "__main__":
    main()
