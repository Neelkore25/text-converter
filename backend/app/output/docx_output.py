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
    """Explicitly sets font name for both ascii and complex script (hAnsi, cs) elements."""
    run.font.name = font_name
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), font_name)
    rFonts.set(qn("w:hAnsi"), font_name)
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

    # Split text into paragraphs
    paragraphs = converted_text.split("\n\n")
    for para_text in paragraphs:
        lines = para_text.split("\n")
        p = doc.add_paragraph()
        for idx, line in enumerate(lines):
            if idx > 0:
                p.add_run().add_break()
            run = p.add_run(line)
            run.font.size = Pt(font_size)
            set_run_font(run, TARGET_FONT_NAME)

    doc.save(str(out_p))
    return out_p.resolve()
