"""PDF document output generator (Phase 13).

Generates PDF documents with the true Shivaji01 Normal font embedded,
ensuring high-fidelity typesetting of legacy Devanagari text.
"""
from __future__ import annotations

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

FONT_PATH = Path("assets/fonts/Shivaji01 Normal.ttf")
FONT_NAME = "Shivaji01"

_FONT_REGISTERED = False


def ensure_font_registered() -> None:
    """Registers Shivaji01 TrueType font with ReportLab."""
    global _FONT_REGISTERED
    if not _FONT_REGISTERED:
        if not FONT_PATH.exists():
            raise FileNotFoundError(f"Shivaji font not found at {FONT_PATH}")
        pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_PATH)))
        _FONT_REGISTERED = True


def write_converted_pdf(
    converted_text: str,
    output_path: str | Path,
    font_size: int = 14,
    leading: int = 20,
) -> Path:
    """Generates an editable/viewable PDF embedding the Shivaji01 font.

    Args:
        converted_text: Converted legacy Shivaji text.
        output_path: Destination .pdf file path.
        font_size: Body font size in points.
        leading: Line height / leading in points.

    Returns:
        Resolved Path to the created PDF file.
    """
    ensure_font_registered()

    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(out_p),
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()
    shivaji_style = ParagraphStyle(
        name="ShivajiBody",
        parent=styles["Normal"],
        fontName=FONT_NAME,
        fontSize=font_size,
        leading=leading,
        spaceAfter=12,
    )

    story = []
    # Split text into paragraphs
    paragraphs = converted_text.split("\n\n")
    for para in paragraphs:
        clean_para = para.strip().replace("\n", "<br/>")
        if clean_para:
            story.append(Paragraph(clean_para, shivaji_style))
            story.append(Spacer(1, 8))

    doc.build(story)
    return out_p.resolve()
