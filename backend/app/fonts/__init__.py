"""Fonts package."""
from backend.app.fonts.font_inspector import FontInspectionReport, inspect_font
from backend.app.fonts.glyph_catalog import (
    GlyphCategory,
    GlyphEntry,
    find_by_code,
    find_by_unicode,
    get_entries_by_category,
    get_glyph_catalog,
)
from backend.app.fonts.source_fonts import (
    SourceDetectionResult,
    SourceFontInfo,
    SourceFontStatus,
    SourceFontType,
    detect_source_font,
    get_all_source_fonts,
    get_source_font_by_id,
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
    "SourceDetectionResult",
    "SourceFontInfo",
    "SourceFontStatus",
    "SourceFontType",
    "detect_source_font",
    "get_all_source_fonts",
    "get_source_font_by_id",
]
