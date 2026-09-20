"""Legacy Source Font Manager (Phase 11).

Manages verification and mapping status for non-Unicode legacy source fonts:
Kruti Dev, DevLys, and Kantal.
Per project requirements: Do not invent mappings. If unavailable, explicitly report:
'Source font mapping unavailable. Please provide the corresponding font/mapping data.'
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

SOURCE_FONTS_DIR = Path("assets/fonts/source")

UNAVAILABLE_NOTICE = (
    "Source font mapping unavailable. Please provide the corresponding font/mapping data."
)


@dataclass
class LegacyFontStatus:
    font_name: str
    is_supported_font: bool
    is_font_file_present: bool
    is_mapping_data_available: bool
    font_file_path: Optional[str]
    status_message: str


# Filename patterns recognized in assets/fonts/source/
KNOWN_LEGACY_FILENAMES: Dict[str, List[str]] = {
    "Kruti Dev": ["krutidev.ttf", "kruti dev.ttf", "kruti_dev.ttf", "kdev.ttf"],
    "DevLys": ["devlys.ttf", "devlys 010.ttf", "devlys_010.ttf"],
    "Kantal": ["kantal.ttf", "kantal normal.ttf"],
}


def get_source_fonts_dir() -> Path:
    """Returns the path to assets/fonts/source, ensuring it exists."""
    SOURCE_FONTS_DIR.mkdir(parents=True, exist_ok=True)
    return SOURCE_FONTS_DIR


def check_legacy_source_availability(font_name: str) -> LegacyFontStatus:
    """Checks whether the requested legacy source font and its mapping data are available.

    Args:
        font_name: Name of the font (e.g. 'Kruti Dev', 'DevLys', 'Kantal').

    Returns:
        LegacyFontStatus with availability details and standard user notification.
    """
    source_dir = get_source_fonts_dir()

    # Find matching font canonical key
    canonical_key = None
    for key in KNOWN_LEGACY_FILENAMES:
        if key.lower() in font_name.lower():
            canonical_key = key
            break

    if not canonical_key:
        return LegacyFontStatus(
            font_name=font_name,
            is_supported_font=False,
            is_font_file_present=False,
            is_mapping_data_available=False,
            font_file_path=None,
            status_message=f"Font '{font_name}' is not a recognized legacy source font.",
        )

    # Check if a matching .ttf file is present in assets/fonts/source/
    patterns = KNOWN_LEGACY_FILENAMES[canonical_key]
    found_path: Optional[Path] = None

    if source_dir.exists():
        for f in source_dir.iterdir():
            if f.is_file() and f.name.lower() in patterns:
                found_path = f
                break

    file_present = found_path is not None

    # Even if file is present, mapping data must be verified
    # Per specification: If mapping data is not yet verified, do not invent.
    mapping_available = False

    status_message = UNAVAILABLE_NOTICE if not mapping_available else "Font and mapping verified."

    return LegacyFontStatus(
        font_name=canonical_key,
        is_supported_font=True,
        is_font_file_present=file_present,
        is_mapping_data_available=mapping_available,
        font_file_path=str(found_path.resolve()) if found_path else None,
        status_message=status_message,
    )


def list_all_source_fonts_status() -> Dict[str, LegacyFontStatus]:
    """Returns the status of all recognized legacy source fonts."""
    return {
        font_name: check_legacy_source_availability(font_name)
        for font_name in KNOWN_LEGACY_FILENAMES
    }
