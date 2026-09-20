"""Tests for Font Inspection (Phase 1)."""
from pathlib import Path
import pytest
from backend.app.fonts.font_inspector import inspect_font, FontInspectionReport

FONT_PATH = Path("assets/fonts/Shivaji01 Normal.ttf")


def test_font_file_exists():
    """Verify that Shivaji01 Normal.ttf exists in the target location assets/fonts/."""
    assert FONT_PATH.exists(), f"Target font missing at {FONT_PATH}"
    assert FONT_PATH.stat().st_size > 0


def test_inspect_font_metadata():
    """Verify metadata extraction from Shivaji01 Normal.ttf."""
    report = inspect_font(FONT_PATH)

    assert isinstance(report, FontInspectionReport)
    assert report.font_name == "Shivaji01"
    assert report.font_family == "Shivaji01"
    assert report.subfamily == "Normal"
    assert "Version 1.5" in report.version
    assert report.num_glyphs == 183
    assert report.best_cmap_size == 180
    assert report.units_per_em == 1000


def test_inspect_font_is_legacy_encoded():
    """Verify that Shivaji01 is identified as a legacy/non-Unicode font without GSUB/GPOS tables."""
    report = inspect_font(FONT_PATH)

    # Legacy font: code points are mapped into Latin-1/Windows-1252 slots (0x20 - 0xFF, etc.),
    # NOT in Unicode Devanagari block (U+0900 - U+097F).
    assert report.is_legacy_symbol_encoded is True
    assert report.has_gsub is False  # No OpenType glyph substitution
    assert report.has_gpos is False  # No OpenType glyph positioning


def test_inspect_font_missing_file():
    """Verify proper error handling when font file does not exist."""
    with pytest.raises(FileNotFoundError):
        inspect_font("assets/fonts/non_existent_font.ttf")


def test_font_inspection_to_dict():
    """Verify that the inspection report serializes cleanly to a dictionary."""
    report = inspect_font(FONT_PATH)
    data = report.to_dict()

    assert data["font_name"] == "Shivaji01"
    assert data["num_glyphs"] == 183
    assert data["has_gsub"] is False
    assert "code_point_range" in data
    assert data["code_point_range"] == (32, 8729)
