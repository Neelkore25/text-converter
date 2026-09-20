"""Source Font and Encoding Detection Module (Phase 10 & 11).

Distinguishes between Unicode Devanagari fonts (Mangal, Nirmala UI, etc.)
and legacy non-Unicode fonts (Kruti Dev, DevLys, Kantal). Provides confidence-scored
auto-detection and validation.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import List, Optional, Tuple


class SourceFontType(str, enum.Enum):
    UNICODE_DEVANAGARI = "unicode_devanagari"
    LEGACY_NON_UNICODE = "legacy_non_unicode"
    UNKNOWN = "unknown"


class DetectionConfidence(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"


# The 10 recognized source fonts per specification
SUPPORTED_SOURCE_FONTS = [
    "Auto Detect",
    "Mangala",
    "Mangal",
    "Nirmala UI",
    "Kokila",
    "Utsaah",
    "Devanagari Sangam MN",
    "Cochin",
    "Kruti Dev",
    "DevLys",
    "Kantal",
]

UNICODE_FONTS = {
    "Mangala",
    "Mangal",
    "Nirmala UI",
    "Kokila",
    "Utsaah",
    "Devanagari Sangam MN",
    "Cochin",
}

LEGACY_SOURCE_FONTS = {
    "Kruti Dev",
    "DevLys",
    "Kantal",
}


@dataclass
class SourceDetectionResult:
    detected_font: str
    font_type: SourceFontType
    confidence: DetectionConfidence
    devanagari_char_ratio: float
    message: str
    requires_user_selection: bool = False


def classify_font_name(font_name: str) -> SourceFontType:
    """Classifies a font name as Unicode Devanagari or Legacy."""
    normalized = font_name.strip().lower()
    for uf in UNICODE_FONTS:
        if uf.lower() in normalized:
            return SourceFontType.UNICODE_DEVANAGARI
    for lf in LEGACY_SOURCE_FONTS:
        if lf.lower() in normalized:
            return SourceFontType.LEGACY_NON_UNICODE
    return SourceFontType.UNKNOWN


def detect_source_encoding(
    text: str,
    declared_font_name: Optional[str] = None,
) -> SourceDetectionResult:
    """Detects whether text is Unicode Devanagari or legacy encoded.

    Args:
        text: Sample text string from document.
        declared_font_name: Optional font name extracted from document metadata (e.g. DOCX/PDF).

    Returns:
        SourceDetectionResult with detected font, type, confidence, and message.
    """
    if not text or not text.strip():
        return SourceDetectionResult(
            detected_font="Auto Detect",
            font_type=SourceFontType.UNKNOWN,
            confidence=DetectionConfidence.UNCERTAIN,
            devanagari_char_ratio=0.0,
            message="Source text is empty. Please provide text or select a source font.",
            requires_user_selection=True,
        )

    # If document explicitly declares a recognized font name in metadata
    if declared_font_name:
        font_type = classify_font_name(declared_font_name)
        if font_type != SourceFontType.UNKNOWN:
            # Find the canonical font name
            canonical_name = next(
                (f for f in (UNICODE_FONTS | LEGACY_SOURCE_FONTS) if f.lower() in declared_font_name.lower()),
                declared_font_name,
            )
            return SourceDetectionResult(
                detected_font=canonical_name,
                font_type=font_type,
                confidence=DetectionConfidence.HIGH,
                devanagari_char_ratio=1.0 if font_type == SourceFontType.UNICODE_DEVANAGARI else 0.0,
                message=f"Detected source font '{canonical_name}' from document metadata.",
                requires_user_selection=False,
            )

    # Analyze character distribution in text
    non_space_chars = [c for c in text if not c.isspace()]
    if not non_space_chars:
        return SourceDetectionResult(
            detected_font="Auto Detect",
            font_type=SourceFontType.UNKNOWN,
            confidence=DetectionConfidence.UNCERTAIN,
            devanagari_char_ratio=0.0,
            message="Source font could not be confidently detected. Please select the source font.",
            requires_user_selection=True,
        )

    devanagari_chars = [c for c in non_space_chars if 0x0900 <= ord(c) <= 0x097F]
    ratio = len(devanagari_chars) / len(non_space_chars)

    # If vast majority of characters are in Unicode Devanagari block
    if ratio > 0.40:
        confidence = DetectionConfidence.HIGH if ratio > 0.70 else DetectionConfidence.MEDIUM
        return SourceDetectionResult(
            detected_font="Mangal",  # Standard canonical Unicode Devanagari representation
            font_type=SourceFontType.UNICODE_DEVANAGARI,
            confidence=confidence,
            devanagari_char_ratio=ratio,
            message="Detected Unicode Devanagari text (Mangal / Nirmala UI compatible).",
            requires_user_selection=False,
        )

    # If text is exclusively ASCII/Latin but represents Indian language text,
    # it may be Kruti Dev or DevLys
    if ratio == 0.0:
        # Check characteristic Kruti Dev / DevLys character sequences
        # In Kruti Dev: 'dks' (को), 'esa' (में), 'gS' (है), 'fnukad' (दिनांक)
        kruti_markers = ["dks", "esa", "gS", "fnukad", "izfr", "vkSj", "fd", "gSa", "rFkk"]
        matches = sum(1 for marker in kruti_markers if marker in text)
        if matches >= 2:
            return SourceDetectionResult(
                detected_font="Kruti Dev",
                font_type=SourceFontType.LEGACY_NON_UNICODE,
                confidence=DetectionConfidence.MEDIUM,
                devanagari_char_ratio=0.0,
                message="Detected Kruti Dev legacy encoding based on character patterns.",
                requires_user_selection=False,
            )

    # Uncertain
    return SourceDetectionResult(
        detected_font="Auto Detect",
        font_type=SourceFontType.UNKNOWN,
        confidence=DetectionConfidence.UNCERTAIN,
        devanagari_char_ratio=ratio,
        message="Source font could not be confidently detected. Please select the source font.",
        requires_user_selection=True,
    )
