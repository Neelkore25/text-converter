"""Tests for Shivaji01 Glyph Catalog (Phase 2)."""
from pathlib import Path
from fontTools.ttLib import TTFont
import pytest

from backend.app.fonts.glyph_catalog import (
    GlyphCategory,
    find_by_code,
    find_by_unicode,
    get_entries_by_category,
    get_glyph_catalog,
)

FONT_PATH = Path("assets/fonts/Shivaji01 Normal.ttf")


@pytest.fixture(scope="module")
def font_cmap():
    """Load the font's best cmap table."""
    tt = TTFont(str(FONT_PATH))
    cmap = tt.getBestCmap()
    tt.close()
    return cmap


def test_all_catalog_entries_exist_in_font(font_cmap):
    """Verify that every character defined in the catalog actually exists in the font binary."""
    catalog = get_glyph_catalog()
    assert len(catalog) >= 70, f"Expected comprehensive catalog, got {len(catalog)} items"

    missing_in_font = []
    mismatched_glyph_names = []

    for entry in catalog:
        if entry.code_point not in font_cmap:
            missing_in_font.append((entry.code_point, entry.description))
        else:
            actual_gname = font_cmap[entry.code_point]
            if actual_gname != entry.glyph_name:
                mismatched_glyph_names.append(
                    (entry.code_point, entry.glyph_name, actual_gname)
                )

    assert not missing_in_font, f"Catalog has code points missing in font: {missing_in_font}"
    assert not mismatched_glyph_names, f"Glyph names mismatch: {mismatched_glyph_names}"


def test_devanagari_digits_mapped():
    """Verify that 0x30 to 0x39 are mapped to Marathi/Devanagari digits ० through ९."""
    digits = get_entries_by_category(GlyphCategory.DIGIT)
    assert len(digits) == 10

    expected_chars = ["०", "१", "२", "३", "४", "५", "६", "७", "८", "९"]
    for i, exp in enumerate(expected_chars):
        cp = 0x30 + i
        entry = find_by_code(cp)
        assert entry is not None, f"Digit {i} (0x{cp:02X}) not found"
        assert entry.unicode_seq == exp
        assert entry.category == GlyphCategory.DIGIT


def test_matra_catalog_entries():
    """Verify essential matras are in the catalog and have correct semantics."""
    matras = get_entries_by_category(GlyphCategory.MATRA)
    matra_unicodes = {m.unicode_seq for m in matras}

    # Verify short i (ि), aa (ा), ii (ी), u (ु), uu (ू), e (े), ai (ै), oo (ो), au (ौ)
    expected_matras = {"\u093E", "\u093F", "\u0940", "\u0941", "\u0942", "\u0947", "\u0948", "\u094B", "\u094C"}
    for exp in expected_matras:
        assert exp in matra_unicodes, f"Missing matra {repr(exp)} in catalog"

    # Verify short i is specifically mapped to 'i' (0x69)
    short_i = find_by_code(0x69)
    assert short_i is not None
    assert short_i.unicode_seq == "\u093F"


def test_reph_and_rakar():
    """Verify reph and rakar entries in the catalog."""
    reph = find_by_code(0x2D)  # hyphen '-'
    assert reph is not None
    assert reph.unicode_seq == "\u0930\u094D"  # र्

    rakar_slash = find_by_code(0x2F)  # '/'
    assert rakar_slash is not None
    assert rakar_slash.unicode_seq == "\u094D\u0930"  # ्र

    rakar_inv_v = find_by_code(0x60)  # '`'
    assert rakar_inv_v is not None
    assert rakar_inv_v.unicode_seq == "\u094D\u0930"


def test_conjuncts_catalog():
    """Verify core conjuncts exist in the catalog."""
    # क्त (>)
    kt = find_by_code(0x3E)
    assert kt is not None and kt.unicode_seq == "क्त"

    # क्र (0xCB)
    kr = find_by_code(0xCB)
    assert kr is not None and kr.unicode_seq == "क्र"

    # ज्ञ (&)
    jny = find_by_code(0x26)
    assert jny is not None and jny.unicode_seq == "ज्ञ"

    # त्र (~)
    tr = find_by_code(0x7E)
    assert tr is not None and tr.unicode_seq == "त्र"

    # द्य (V)
    dy = find_by_code(0x56)
    assert dy is not None and dy.unicode_seq == "द्य"

    # द्व (W)
    dv = find_by_code(0x57)
    assert dv is not None and dv.unicode_seq == "द्व"


def test_lookup_functions():
    """Verify lookup helpers find_by_code and find_by_unicode."""
    # Find by code
    entry = find_by_code(0x6B)  # 'k'
    assert entry is not None
    assert entry.char == "k"
    assert entry.unicode_seq == "क"

    # Find by unicode
    entry_u = find_by_unicode("क")
    assert entry_u is not None
    assert entry_u.code_point == 0x6B

    # Non-existent
    assert find_by_code(0xFFFF) is None
    assert find_by_unicode("XYZ") is None
