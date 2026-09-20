"""Source Font Management and Detection Engine (Phases 10 & 11).

Handles cataloging, status tracking, and detection for:
- Unicode Devanagari fonts: Mangala, Mangal, Nirmala UI, Kokila, Utsaah, Devanagari Sangam MN, Cochin
- Legacy source fonts: Kruti Dev, DevLys, Kantal
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

SOURCE_FONTS_DIR = Path("assets/fonts/source")


class SourceFontType(str, enum.Enum):
    UNICODE_DEVANAGARI = "unicode_devanagari"
    LEGACY_ENCODED = "legacy_encoded"


class SourceFontStatus(str, enum.Enum):
    UNICODE_SUPPORTED = "✓ Unicode supported"
    LEGACY_REQUIRES_FONT = "⚠ Legacy mapping requires font"
    LEGACY_AVAILABLE = "✓ Legacy font verified"
    NOT_INSTALLED = "○ Not installed"


@dataclass
class SourceFontInfo:
    id: str
    display_name: str
    font_type: SourceFontType
    aliases: List[str]
    description: str
    expected_filenames: List[str] = field(default_factory=list)

    @property
    def is_installed_in_assets(self) -> bool:
        """Checks whether any matching font file is present in assets/fonts/source/."""
        if not SOURCE_FONTS_DIR.exists():
            return False
        for fname in self.expected_filenames:
            if (SOURCE_FONTS_DIR / fname).exists():
                return True
        return False

    @property
    def font_file_available(self) -> bool:
        """Indicates if font file is present in assets/fonts/source/."""
        if self.font_type == SourceFontType.UNICODE_DEVANAGARI:
            return True  # System/Standard Unicode font
        return self.is_installed_in_assets

    @property
    def mapping_table_available(self) -> bool:
        """Indicates whether Unicode <-> legacy mapping table is present in code."""
        if self.font_type == SourceFontType.UNICODE_DEVANAGARI:
            return True
        # Legacy fonts require both font file and mapping table data
        return False

    @property
    def status(self) -> SourceFontStatus:
        """Determines the operational status of the source font."""
        if self.font_type == SourceFontType.UNICODE_DEVANAGARI:
            return SourceFontStatus.UNICODE_SUPPORTED
        # Legacy font
        if self.font_file_available and self.mapping_table_available:
            return SourceFontStatus.LEGACY_AVAILABLE
        return SourceFontStatus.LEGACY_REQUIRES_FONT


# 10 Supported Source Fonts per specification
SOURCE_FONTS_REGISTRY: List[SourceFontInfo] = [
    SourceFontInfo(
        id="mangal",
        display_name="Mangal",
        font_type=SourceFontType.UNICODE_DEVANAGARI,
        aliases=["mangal", "mangala"],
        description="Standard Windows Unicode Devanagari font designed by R. K. Joshi.",
    ),
    SourceFontInfo(
        id="mangala",
        display_name="Mangala",
        font_type=SourceFontType.UNICODE_DEVANAGARI,
        aliases=["mangala"],
        description="Unicode Devanagari variant of Mangal.",
    ),
    SourceFontInfo(
        id="nirmala_ui",
        display_name="Nirmala UI",
        font_type=SourceFontType.UNICODE_DEVANAGARI,
        aliases=["nirmala ui", "nirmala", "nirmalaui"],
        description="Modern Microsoft Windows UI Unicode Indic font family.",
    ),
    SourceFontInfo(
        id="kokila",
        display_name="Kokila",
        font_type=SourceFontType.UNICODE_DEVANAGARI,
        aliases=["kokila"],
        description="Microsoft Windows Unicode Devanagari typeface.",
    ),
    SourceFontInfo(
        id="utsaah",
        display_name="Utsaah",
        font_type=SourceFontType.UNICODE_DEVANAGARI,
        aliases=["utsaah"],
        description="Microsoft Windows Unicode Devanagari typeface.",
    ),
    SourceFontInfo(
        id="devanagari_sangam_mn",
        display_name="Devanagari Sangam MN",
        font_type=SourceFontType.UNICODE_DEVANAGARI,
        aliases=["devanagari sangam mn", "sangam mn", "devanagari sangam"],
        description="Apple macOS standard Unicode Devanagari system font.",
    ),
    SourceFontInfo(
        id="cochin",
        display_name="Cochin",
        font_type=SourceFontType.UNICODE_DEVANAGARI,
        aliases=["cochin", "cochin devanagari"],
        description="macOS / iOS font family supporting Unicode Devanagari text.",
    ),
    SourceFontInfo(
        id="kruti_dev",
        display_name="Kruti Dev",
        font_type=SourceFontType.LEGACY_ENCODED,
        aliases=["kruti dev", "krutidev", "kruti_dev", "kruti dev 010"],
        description="Widely used legacy Remington keyboard layout Hindi font.",
        expected_filenames=["KrutiDev.ttf", "Kruti_Dev.ttf", "KrutiDev010.ttf", "kruti.ttf"],
    ),
    SourceFontInfo(
        id="devlys",
        display_name="DevLys",
        font_type=SourceFontType.LEGACY_ENCODED,
        aliases=["devlys", "devlys 010"],
        description="Remington layout legacy font family closely related to Kruti Dev.",
        expected_filenames=["DevLys.ttf", "DevLys010.ttf", "devlys.ttf"],
    ),
    SourceFontInfo(
        id="kantal",
        display_name="Kantal",
        font_type=SourceFontType.LEGACY_ENCODED,
        aliases=["kantal", "kantal normal"],
        description="Legacy Marathi non-Unicode printing font.",
        expected_filenames=["Kantal.ttf", "kantal.ttf", "KantalNormal.ttf"],
    ),
]

_FONTS_BY_ID: Dict[str, SourceFontInfo] = {f.id: f for f in SOURCE_FONTS_REGISTRY}


@dataclass
class SourceDetectionResult:
    detected_font: Optional[SourceFontInfo]
    confidence: float  # 0.0 to 1.0
    is_unicode: bool
    is_supported: bool
    message: str


def get_all_source_fonts() -> List[SourceFontInfo]:
    """Returns the complete registry of 10 supported source fonts."""
    return list(SOURCE_FONTS_REGISTRY)


def get_source_font_by_id(font_id: str) -> Optional[SourceFontInfo]:
    """Looks up a source font by its identifier."""
    return _FONTS_BY_ID.get(font_id.lower())


def detect_source_font(
    text: str,
    font_name_hint: Optional[str] = None,
) -> SourceDetectionResult:
    """Attempts to identify the source encoding/font from text and document metadata hints.

    Args:
        text: Sample or full text extracted from the document.
        font_name_hint: Optional font face name from DOCX/PDF run properties.

    Returns:
        SourceDetectionResult with detected font, confidence, and readiness status.
    """
    cleaned_hint = (font_name_hint or "").strip().lower()

    # Match hint against registry aliases
    matched_font: Optional[SourceFontInfo] = None
    if cleaned_hint:
        for font in SOURCE_FONTS_REGISTRY:
            if any(alias in cleaned_hint for alias in font.aliases):
                matched_font = font
                break

    # Analyze character distribution in text
    devanagari_count = sum(1 for c in text if 0x0900 <= ord(c) <= 0x097F)
    total_non_ws = sum(1 for c in text if not c.isspace())

    is_devanagari_unicode = (
        (devanagari_count / total_non_ws) > 0.15 if total_non_ws > 0 else False
    )

    # Case 1: Text is Unicode Devanagari
    if is_devanagari_unicode:
        # If hint matched a known Unicode font, use that; otherwise default to Mangal
        if matched_font and matched_font.font_type == SourceFontType.UNICODE_DEVANAGARI:
            return SourceDetectionResult(
                detected_font=matched_font,
                confidence=0.95,
                is_unicode=True,
                is_supported=True,
                message=f"Detected Unicode Devanagari font: {matched_font.display_name}",
            )
        # Default Unicode font is Mangal
        default_unicode = _FONTS_BY_ID["mangal"]
        return SourceDetectionResult(
            detected_font=default_unicode,
            confidence=0.90,
            is_unicode=True,
            is_supported=True,
            message="Detected Unicode Devanagari text (using Mangal pipeline)",
        )

    # Case 2: Hint matched a legacy font (Kruti Dev, DevLys, Kantal)
    if matched_font and matched_font.font_type == SourceFontType.LEGACY_ENCODED:
        if matched_font.is_installed_in_assets:
            return SourceDetectionResult(
                detected_font=matched_font,
                confidence=0.85,
                is_unicode=False,
                is_supported=True,
                message=f"Detected legacy font: {matched_font.display_name} (Font file available in assets)",
            )
        else:
            return SourceDetectionResult(
                detected_font=matched_font,
                confidence=0.80,
                is_unicode=False,
                is_supported=False,
                message="Source font mapping unavailable. Please provide the corresponding font/mapping data.",
            )

    # Case 3: Uncertain detection
    return SourceDetectionResult(
        detected_font=None,
        confidence=0.0,
        is_unicode=False,
        is_supported=False,
        message="Source font could not be confidently detected. Please select the source font.",
    )
