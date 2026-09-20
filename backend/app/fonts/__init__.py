"""Fonts package exports."""
from backend.app.fonts.font_inspector import FontInspectionReport, inspect_font
from backend.app.fonts.glyph_catalog import (
    GlyphCategory,
    GlyphEntry,
    find_by_code,
    find_by_unicode,
    get_entries_by_category,
    get_glyph_catalog,
)
from backend.app.fonts.legacy_font_manager import (
    UNAVAILABLE_NOTICE,
    LegacyFontStatus,
    check_legacy_source_availability,
    list_all_source_fonts_status,
)
from backend.app.fonts.source_font_detector import (
    LEGACY_SOURCE_FONTS,
    SUPPORTED_SOURCE_FONTS,
    UNICODE_FONTS,
    DetectionConfidence,
    SourceDetectionResult,
    SourceFontType,
    classify_font_name,
    detect_source_encoding,
)

__all__ = [
    "FontInspectionReport",
    "inspect_font",
    "GlyphCategory",
    "GlyphEntry",
    "find_by_code",
    "find_by_unicode",
    "get_entries_by_category",
    "get_glyph_catalog",
    "SourceFontType",
    "DetectionConfidence",
    "SourceDetectionResult",
    "SUPPORTED_SOURCE_FONTS",
    "UNICODE_FONTS",
    "LEGACY_SOURCE_FONTS",
    "classify_font_name",
    "detect_source_encoding",
    "LegacyFontStatus",
    "UNAVAILABLE_NOTICE",
    "check_legacy_source_availability",
    "list_all_source_fonts_status",
]
