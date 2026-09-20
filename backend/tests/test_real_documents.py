"""Tests for Real Document Processing (Phase 17)."""
from pathlib import Path
import pytest
from docx import Document

from backend.app.conversion.unicode_to_shivaji import convert_unicode_to_shivaji
from backend.app.extraction.docx_extractor import extract_text_from_docx
from backend.app.extraction.pdf_extractor import extract_text_from_pdf
from backend.app.extraction.text_extractor import extract_text_from_txt
from backend.app.fonts.source_fonts import detect_source_font
from backend.app.output.docx_output import TARGET_FONT_NAME, write_converted_docx
from backend.app.output.pdf_output import write_converted_pdf
from backend.app.output.text_output import write_converted_txt
from backend.app.validation.validator import validate_conversion

SAMPLES_DIR = Path("samples")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def test_process_real_mangal_txt():
    """Phase 17: Process real Marathi Mangal text document."""
    txt_path = SAMPLES_DIR / "sample_mangal.txt"
    assert txt_path.exists()

    # 1. Extract
    doc = extract_text_from_txt(txt_path)
    assert doc.character_count > 100

    # 2. Detect
    detection = detect_source_font(doc.text)
    assert detection.is_unicode is True
    assert detection.is_supported is True

    # 3. Convert
    res = convert_unicode_to_shivaji(doc.text)
    assert res.warning_count == 0

    # 4. Output
    out_file = OUTPUT_DIR / "converted_sample_mangal.txt"
    written = write_converted_txt(res.converted_text, out_file)
    assert written.exists()
    assert written.stat().st_size > 0

    # 5. Validate & Report
    report = validate_conversion(
        input_text=doc.text,
        converted_text=res.converted_text,
        input_filename=txt_path.name,
        source_font=detection.detected_font.display_name,
        pages=doc.page_count,
    )
    assert report.warning_count == 0
    assert report.status == "Completed successfully"


def test_process_real_kokila_docx():
    """Phase 17: Process real Marathi Kokila DOCX document."""
    docx_path = SAMPLES_DIR / "sample_kokila.docx"
    assert docx_path.exists()

    # 1. Extract
    doc = extract_text_from_docx(docx_path)
    assert doc.character_count > 50
    assert "Kokila" in (doc.font_hint or "")

    # 2. Detect font with hint
    detection = detect_source_font(doc.text, font_name_hint=doc.font_hint)
    assert detection.detected_font.id == "kokila"

    # 3. Convert
    res = convert_unicode_to_shivaji(doc.text)
    assert res.warning_count == 0

    # 4. Output DOCX styled with Shivaji01 Normal
    out_file = OUTPUT_DIR / "converted_sample_kokila.docx"
    written = write_converted_docx(res.converted_text, out_file)
    assert written.exists()

    # Verify run font in generated document
    reopened = Document(str(written))
    for p in reopened.paragraphs:
        for r in p.runs:
            assert r.font.name == TARGET_FONT_NAME


def test_process_real_scanned_pdf():
    """Phase 17: Detect scanned PDF and produce exact user warning notice."""
    pdf_path = SAMPLES_DIR / "sample_scanned.pdf"
    assert pdf_path.exists()

    doc = extract_text_from_pdf(pdf_path)
    assert doc.is_scanned_image_only is True
    assert "OCR is required for text extraction." in doc.metadata["notice"]
