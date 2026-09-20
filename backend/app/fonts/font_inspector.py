"""Font inspection module for legacy and Unicode Devanagari fonts."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from fontTools.ttLib import TTFont


class FontInspectionReport:
    """Detailed inspection report for a font file."""

    def __init__(
        self,
        file_path: str,
        font_name: str,
        font_family: str,
        subfamily: str,
        version: str,
        num_glyphs: int,
        has_gsub: bool,
        has_gpos: bool,
        is_legacy_symbol_encoded: bool,
        cmap_tables_count: int,
        best_cmap_size: int,
        character_code_points: List[int],
        sample_mappings: Dict[str, str],
        units_per_em: int,
        bbox: tuple[int, int, int, int],
    ):
        self.file_path = file_path
        self.font_name = font_name
        self.font_family = font_family
        self.subfamily = subfamily
        self.version = version
        self.num_glyphs = num_glyphs
        self.has_gsub = has_gsub
        self.has_gpos = has_gpos
        self.is_legacy_symbol_encoded = is_legacy_symbol_encoded
        self.cmap_tables_count = cmap_tables_count
        self.best_cmap_size = best_cmap_size
        self.character_code_points = character_code_points
        self.sample_mappings = sample_mappings
        self.units_per_em = units_per_em
        self.bbox = bbox

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "font_name": self.font_name,
            "font_family": self.font_family,
            "subfamily": self.subfamily,
            "version": self.version,
            "num_glyphs": self.num_glyphs,
            "has_gsub": self.has_gsub,
            "has_gpos": self.has_gpos,
            "is_legacy_symbol_encoded": self.is_legacy_symbol_encoded,
            "cmap_tables_count": self.cmap_tables_count,
            "best_cmap_size": self.best_cmap_size,
            "code_points_count": len(self.character_code_points),
            "code_point_range": (
                (min(self.character_code_points), max(self.character_code_points))
                if self.character_code_points
                else (0, 0)
            ),
            "sample_mappings": self.sample_mappings,
            "units_per_em": self.units_per_em,
            "bbox": self.bbox,
        }


def inspect_font(font_path: str | Path) -> FontInspectionReport:
    """Inspects a TrueType/OpenType font file and extracts comprehensive metadata.

    Args:
        font_path: Path to the .ttf or .otf file.

    Returns:
        FontInspectionReport containing metadata and cmap details.

    Raises:
        FileNotFoundError: If the font file does not exist.
        ValueError: If the file is not a valid font.
    """
    path = Path(font_path)
    if not path.is_file():
        raise FileNotFoundError(f"Font file not found: {path}")

    try:
        tt = TTFont(str(path))
    except Exception as e:
        raise ValueError(f"Failed to parse font file '{path}': {e}") from e

    # Extract name records
    name_table = tt.get("name")
    names: Dict[int, str] = {}
    if name_table:
        for record in name_table.names:
            try:
                # nameID 1: Family, 2: Subfamily, 4: Full name, 5: Version, 6: PostScript name
                names[record.nameID] = record.toUnicode()
            except Exception:
                pass

    font_family = names.get(1, "Unknown")
    subfamily = names.get(2, "Regular")
    font_name = names.get(4, font_family)
    version = names.get(5, "Unknown")

    num_glyphs = tt["maxp"].numGlyphs if "maxp" in tt else 0
    has_gsub = "GSUB" in tt
    has_gpos = "GPOS" in tt

    # Cmap analysis
    cmap_table = tt.get("cmap")
    cmap_tables_count = len(cmap_table.tables) if cmap_table else 0
    best_cmap = tt.getBestCmap() or {}
    best_cmap_size = len(best_cmap)
    code_points = sorted(best_cmap.keys())

    # Check whether it's legacy encoded (Devanagari glyphs mapped in 0x20..0xFF or symbol area instead of U+0900..U+097F)
    has_devanagari_unicode = any(0x0900 <= cp <= 0x097F for cp in code_points)
    is_legacy = not has_devanagari_unicode

    # Sample mappings
    sample_mappings: Dict[str, str] = {}
    for cp in code_points[:20]:
        glyph_name = best_cmap[cp]
        char_repr = chr(cp) if (32 <= cp <= 126 or cp >= 160) else f"U+{cp:04X}"
        sample_mappings[f"0x{cp:02X} ({char_repr})"] = glyph_name

    # Head / metrics
    head = tt.get("head")
    units_per_em = head.unitsPerEm if head else 1000
    bbox = (
        (head.xMin, head.yMin, head.xMax, head.yMax)
        if head
        else (0, 0, 0, 0)
    )

    tt.close()

    return FontInspectionReport(
        file_path=str(path.resolve()),
        font_name=font_name,
        font_family=font_family,
        subfamily=subfamily,
        version=version,
        num_glyphs=num_glyphs,
        has_gsub=has_gsub,
        has_gpos=has_gpos,
        is_legacy_symbol_encoded=is_legacy,
        cmap_tables_count=cmap_tables_count,
        best_cmap_size=best_cmap_size,
        character_code_points=code_points,
        sample_mappings=sample_mappings,
        units_per_em=units_per_em,
        bbox=bbox,
    )
