"""Tests for Source Font Detection and Legacy Font Management (Phases 10 & 11)."""
import pytest
from backend.app.fonts.source_font_detector import (
    DetectionConfidence,
    SourceFontType,
    classify_font_name,
    detect_source_encoding,
    UNICODE_FONTS,
    LEGACY_SOURCE_FONTS,
)
from backend.app.fonts.legacy_font_manager import (
    UNAVAILABLE_NOTICE,
    check_legacy_source_availability,
    list_all_source_fonts_status,
    get_source_fonts_dir,
)


def test_classify_all_supported_fonts():
    """Verify classification of all 10 supported source fonts."""
    for uf in UNICODE_FONTS:
        assert classify_font_name(uf) == SourceFontType.UNICODE_DEVANAGARI, f"Failed for {uf}"

    for lf in LEGACY_SOURCE_FONTS:
        assert classify_font_name(lf) == SourceFontType.LEGACY_NON_UNICODE, f"Failed for {lf}"

    assert classify_font_name("Arial") == SourceFontType.UNKNOWN


def test_detect_unicode_devanagari_text():
    """Verify auto-detection of Unicode Marathi text."""
    marathi_sample = "महाराष्ट्र माझा देश आहे. मला मराठी भाषा आवडते."
    res = detect_source_encoding(marathi_sample)

    assert res.font_type == SourceFontType.UNICODE_DEVANAGARI
    assert res.confidence == DetectionConfidence.HIGH
    assert res.devanagari_char_ratio > 0.70
    assert res.detected_font == "Mangal"
    assert not res.requires_user_selection


def test_detect_declared_source_font_metadata():
    """Verify detection when document metadata declares a recognized font."""
    text = "महाराष्ट्र"
    res = detect_source_encoding(text, declared_font_name="Nirmala UI Regular")

    assert res.detected_font == "Nirmala UI"
    assert res.font_type == SourceFontType.UNICODE_DEVANAGARI
    assert res.confidence == DetectionConfidence.HIGH


def test_uncertain_detection_triggers_user_selection():
    """Verify uncertain detection returns the required fallback notice."""
    empty_res = detect_source_encoding("")
    assert empty_res.requires_user_selection is True
    assert empty_res.confidence == DetectionConfidence.UNCERTAIN

    latin_generic = detect_source_encoding("This is purely english text without any marathi markers.")
    assert latin_generic.requires_user_selection is True
    assert "Source font could not be confidently detected" in latin_generic.message


def test_legacy_font_manager_unavailable_notice():
    """Verify missing legacy source fonts return the exact required message."""
    for lf in ["Kruti Dev", "DevLys", "Kantal"]:
        status = check_legacy_source_availability(lf)
        assert status.is_supported_font is True
        assert status.is_mapping_data_available is False
        assert status.status_message == UNAVAILABLE_NOTICE


def test_source_fonts_directory_created():
    """Verify assets/fonts/source exists."""
    source_dir = get_source_fonts_dir()
    assert source_dir.exists()
    assert source_dir.is_dir()


def test_list_all_source_fonts_status():
    """Verify listing all 3 legacy source fonts."""
    all_status = list_all_source_fonts_status()
    assert "Kruti Dev" in all_status
    assert "DevLys" in all_status
    assert "Kantal" in all_status
