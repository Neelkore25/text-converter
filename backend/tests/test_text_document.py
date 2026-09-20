"""Tests for TXT Document Extraction and Output (Phase 12)."""
from pathlib import Path
import pytest

from backend.app.conversion.unicode_to_shivaji import convert_unicode_to_shivaji
from backend.app.extraction.text_extractor import extract_text_from_txt
from backend.app.output.text_output import write_converted_txt


@pytest.fixture
def sample_marathi_txt(tmp_path: Path) -> Path:
    content = (
        "महाराष्ट्र माझा देश आहे.\n\n"
        "मला संगणक अभियांत्रिकी शिकायला आवडते.\n"
        "माझे नाव नील आहे.\n"
    )
    p = tmp_path / "sample_marathi.txt"
    p.write_text(content, encoding="utf-8")
    return p


@pytest.fixture
def sample_utf8_bom_txt(tmp_path: Path) -> Path:
    content = "महाराष्ट्र भारतातील एक राज्य आहे.\n"
    p = tmp_path / "sample_bom.txt"
    p.write_text(content, encoding="utf-8-sig")
    return p


def test_extract_utf8_txt(sample_marathi_txt: Path):
    """Verify clean extraction of UTF-8 Marathi text with line breaks and blank lines."""
    doc = extract_text_from_txt(sample_marathi_txt)
    assert doc.format == "txt"
    assert doc.character_count > 0
    assert "महाराष्ट्र" in doc.text
    assert doc.metadata["blank_lines"] == 1
    assert doc.metadata["total_lines"] == 4


def test_extract_utf8_bom_txt(sample_utf8_bom_txt: Path):
    """Verify clean extraction of UTF-8 with BOM."""
    doc = extract_text_from_txt(sample_utf8_bom_txt)
    assert doc.metadata["encoding"] == "utf-8-sig"
    assert doc.text.startswith("महाराष्ट्र")


def test_extract_empty_file(tmp_path: Path):
    """Verify empty file handling."""
    empty_p = tmp_path / "empty.txt"
    empty_p.write_text("", encoding="utf-8")
    doc = extract_text_from_txt(empty_p)
    assert doc.character_count == 0
    assert doc.text == ""


def test_extract_non_existent_file():
    """Verify FileNotFoundError on missing file."""
    with pytest.raises(FileNotFoundError):
        extract_text_from_txt("non_existent_file_path_123.txt")


def test_txt_conversion_and_output_roundtrip(sample_marathi_txt: Path, tmp_path: Path):
    """Phase 12 End-to-End: Extract -> Convert -> Write TXT -> Verify file contents."""
    # 1. Extract
    doc = extract_text_from_txt(sample_marathi_txt)

    # 2. Convert
    conversion_res = convert_unicode_to_shivaji(doc.text)
    assert conversion_res.warning_count == 0

    # 3. Output
    out_file = tmp_path / "output_shivaji.txt"
    written_path = write_converted_txt(conversion_res.converted_text, out_file)
    assert written_path.exists()
    assert written_path.stat().st_size > 0

    # 4. Reopen and verify
    with open(written_path, "r", encoding="utf-8", newline="") as f:
        reopened_text = f.read()
    assert reopened_text == conversion_res.converted_text
    # Verify line breaks and blank line structure remained intact
    assert "\n\n" in reopened_text or "\r\n\r\n" in reopened_text
