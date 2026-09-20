"""Tests for Source Font Registry and Detection (Phases 10 & 11)."""
import pytest
from backend.app.fonts.source_fonts import (
    SourceFontStatus,
    SourceFontType,
    detect_source_font,
    get_all_source_fonts,
    get_source_font_by_id,
)


def test_all_ten_source_fonts_registered():
    """Phase 10: Verify all 10 source fonts specified in project requirements exist."""
    expected_fonts = [
        ("mangal", SourceFontType.UNICODE_DEVANAGARI),
        ("mangala", SourceFontType.UNICODE_DEVANAGARI),
        ("nirmala_ui", SourceFontType.UNICODE_DEVANAGARI),
        ("kokila", SourceFontType.UNICODE_DEVANAGARI),
        ("utsaah", SourceFontType.UNICODE_DEVANAGARI),
        ("devanagari_sangam_mn", SourceFontType.UNICODE_DEVANAGARI),
        ("cochin", SourceFontType.UNICODE_DEVANAGARI),
        ("kruti_dev", SourceFontType.LEGACY_ENCODED),
        ("devlys", SourceFontType.LEGACY_ENCODED),
        ("kantal", SourceFontType.LEGACY_ENCODED),
    ]

    all_fonts = get_all_source_fonts()
    assert len(all_fonts) == 10

    for fid, ftype in expected_fonts:
        font = get_source_font_by_id(fid)
        assert font is not None, f"Font {fid} not found in registry"
        assert font.font_type == ftype, f"Font {fid} type mismatch"


def test_unicode_source_fonts_status():
    """Phase 10: All Unicode Devanagari fonts report '✓ Unicode supported'."""
    unicode_ids = ["mangal", "mangala", "nirmala_ui", "kokila", "utsaah", "devanagari_sangam_mn", "cochin"]
    for fid in unicode_ids:
        font = get_source_font_by_id(fid)
        assert font.status == SourceFontStatus.UNICODE_SUPPORTED


def test_legacy_source_fonts_status_when_uninstalled():
    """Phase 11: Legacy fonts report '⚠ Legacy mapping requires font' when file missing."""
    legacy_ids = ["kruti_dev", "devlys", "kantal"]
    for fid in legacy_ids:
        font = get_source_font_by_id(fid)
        assert font.status == SourceFontStatus.LEGACY_REQUIRES_FONT


def test_detect_unicode_text_with_hints():
    """Phase 10: Detection of Unicode Devanagari with font name hint."""
    sample_text = "महाराष्ट्र माझा देश आहे."

    # Hint matches Nirmala UI
    res_nirmala = detect_source_font(sample_text, font_name_hint="Nirmala UI")
    assert res_nirmala.is_unicode is True
    assert res_nirmala.is_supported is True
    assert res_nirmala.detected_font.id == "nirmala_ui"

    # Hint matches Kokila
    res_kokila = detect_source_font(sample_text, font_name_hint="Kokila")
    assert res_kokila.is_unicode is True
    assert res_kokila.detected_font.id == "kokila"

    # No hint defaults to Mangal
    res_default = detect_source_font(sample_text, font_name_hint=None)
    assert res_default.is_unicode is True
    assert res_default.detected_font.id == "mangal"


def test_detect_legacy_font_unavailable():
    """Phase 11: When legacy font is specified but font data is missing, display exact required error message."""
    res = detect_source_font("random legacy ascii text", font_name_hint="Kruti Dev 010")
    assert res.is_unicode is False
    assert res.is_supported is False
    assert res.detected_font.id == "kruti_dev"
    assert res.message == "Source font mapping unavailable. Please provide the corresponding font/mapping data."


def test_detect_uncertain_source_font():
    """Phase 11: Uncertain auto-detection displays exact required prompt message."""
    res = detect_source_font("12345 Hello World", font_name_hint=None)
    assert res.detected_font is None
    assert res.confidence == 0.0
    assert res.message == "Source font could not be confidently detected. Please select the source font."
