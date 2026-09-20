"""DOCX document output generator (Phase 14).

Generates editable Word documents (.docx) with the text styled in the
Shivaji01 Normal font.
"""
from __future__ import annotations

from pathlib import Path
from docx import Document
from docx.shared import Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

TARGET_FONT_NAME = "Shivaji01 Normal"


def set_run_font(run, font_name: str) -> None:
    """Explicitly sets font name for ascii, hAnsi, eastAsia, and complex script (cs) elements."""
    run.font.name = font_name
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), font_name)
    rFonts.set(qn("w:hAnsi"), font_name)
    rFonts.set(qn("w:eastAsia"), font_name)
    rFonts.set(qn("w:cs"), font_name)


def write_converted_docx(
    converted_text: str,
    output_path: str | Path,
    font_size: int = 14,
) -> Path:
    """Creates an editable Word document with Shivaji01 Normal font styling.

    Args:
        converted_text: Converted legacy Shivaji string.
        output_path: Destination .docx file path.
        font_size: Point size for text runs (default: 14pt).

    Returns:
        Resolved Path to the created DOCX file.
    """
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    doc = Document()

    # Normalize newlines
    normalized_text = converted_text.replace("\r\n", "\n").replace("\r", "\n")
    paragraphs = normalized_text.split("\n\n")

    for para_text in paragraphs:
        p = doc.add_paragraph()
        lines = para_text.split("\n")
        for idx, line in enumerate(lines):
            if idx > 0:
                p.add_run().add_break()
            run = p.add_run(line)
            run.font.size = Pt(font_size)
            set_run_font(run, TARGET_FONT_NAME)

    doc.save(str(out_p))
    return out_p.resolve()


def transform_existing_docx(
    source_path: str | Path,
    output_path: str | Path,
) -> Path:
    """Modifies an existing DOCX document in-place, preserving 100% of formatting,
    margins, styles, tables, headers, and footers while converting all text runs
    to Shivaji01 Normal font and mapping Devanagari text.
    """
    from backend.app.conversion.unicode_to_shivaji import convert_unicode_to_shivaji

    src_p = Path(source_path)
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    doc = Document(str(src_p))

    def process_paragraph(p):
        for run in p.runs:
            if run.text:
                res = convert_unicode_to_shivaji(run.text)
                run.text = res.converted_text
                set_run_font(run, TARGET_FONT_NAME)

    # 1. Body paragraphs
    for p in doc.paragraphs:
        process_paragraph(p)

    # 2. Tables (including nested cells)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    process_paragraph(p)

    # 3. Headers and Footers across all sections
    for section in doc.sections:
        for p in section.header.paragraphs:
            process_paragraph(p)
        for table in section.header.tables:
            for row in table.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        process_paragraph(p)

        for p in section.footer.paragraphs:
            process_paragraph(p)
        for table in section.footer.tables:
            for row in table.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        process_paragraph(p)

    doc.save(str(out_p))
    return out_p.resolve()

