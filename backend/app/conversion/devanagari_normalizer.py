"""Unicode Devanagari Normalization Engine (Phase 4).

Handles canonicalization, composite vowel reconstitution, nukta placement,
combining character cleanup, and Marathi-specific glyph standardization.
"""
from __future__ import annotations

import re
import unicodedata
from typing import NamedTuple


# Common anomalous typed sequences -> Canonical Unicode independent vowels
COMPOSITE_VOWEL_REPLACEMENTS = [
    # Candra O: अ + ा + ॅ / अ + ॉ -> ऑ
    ("\u0905\u093E\u0945", "\u0911"),
    ("\u0905\u0949", "\u0911"),
    # AU: अ + ा + ै / अ + ौ -> औ
    ("\u0905\u093E\u0948", "\u0914"),
    ("\u0905\u094C", "\u0914"),
    # OO: अ + ा + े / अ + ो -> ओ
    ("\u0905\u093E\u0947", "\u0913"),
    ("\u0905\u094B", "\u0913"),
    # AA: अ + ा -> आ
    ("\u0905\u093E", "\u0906"),
    # AI: ए + े / ए + ै -> ऐ
    ("\u090F\u0947", "\u0910"),
    ("\u090F\u0948", "\u0910"),
    # Candra E: ए + ॅ -> ऍ
    ("\u090F\u0945", "\u090D"),
    # II: इ + ी -> ई
    ("\u0907\u0940", "\u0908"),
    # UU: उ + ु / उ + ू -> ऊ
    ("\u0909\u0941", "\u090A"),
    ("\u0909\u0942", "\u090A"),
]

# Decomposed nukta consonants -> Precomposed or normalized
# In Unicode:
# क़ = U+0958, ख़ = U+0959, ग़ = U+095A, ज़ = U+095B
# ड़ = U+095C, ढ़ = U+095D, फ़ = U+095E, य़ = U+095F
NUKTA = "\u093C"
VIRAMA = "\u094D"
ZWJ = "\u200D"
ZWNJ = "\u200C"


class NormalizationResult(NamedTuple):
    normalized_text: str
    modifications_made: int


def normalize_devanagari(text: str, preserve_zwj_zwnj: bool = True) -> str:
    """Normalizes Unicode Devanagari text into canonical representation.

    Args:
        text: Input Devanagari / Marathi string.
        preserve_zwj_zwnj: If True, retains ZWJ/ZWNJ used for eyelash-ra and explicit virama.

    Returns:
        Cleaned, canonicalized Unicode Devanagari string.
    """
    if not text:
        return ""

    # Step 1: Initial Unicode NFC normalization
    normalized = unicodedata.normalize("NFC", text)

    # Step 2: Fix pseudo-independent vowels typed as base vowel + matra
    for anomalous, canonical in COMPOSITE_VOWEL_REPLACEMENTS:
        if anomalous in normalized:
            normalized = normalized.replace(anomalous, canonical)

    # Step 3: Reorder misordered Nukta (e.g. Consonant + Matra + Nukta -> Consonant + Nukta + Matra)
    # Matras: 0x093E to 0x094C, 0x094F, 0x0956, 0x0957
    normalized = re.sub(
        r"([\u0915-\u0939\u0958-\u095F])([\u093E-\u094C\u094D\u0956\u0957])\u093C",
        r"\g<1>" + NUKTA + r"\g<2>",
        normalized,
    )

    # Step 4: Deduplicate redundant combining marks (e.g. multiple nuktas or repeated matras)
    # Deduplicate nuktas
    normalized = re.sub(r"\u093C+", "\u093C", normalized)
    # Deduplicate viramas
    normalized = re.sub(r"\u094D+", "\u094D", normalized)
    # Deduplicate anusvaras
    normalized = re.sub(r"\u0902+", "\u0902", normalized)

    # Step 5: Clean space between consonant/nukta and vowel matra (e.g. "क  ा" -> "का")
    normalized = re.sub(
        r"([\u0915-\u0939\u0958-\u095F]\u093C?)[ \t]+([\u093E-\u094C\u094D])",
        r"\g<1>\g<2>",
        normalized,
    )

    # Step 6: Handle ZWJ / ZWNJ
    if not preserve_zwj_zwnj:
        # Strip all joiners
        normalized = normalized.replace(ZWJ, "").replace(ZWNJ, "")
    else:
        # Clean up stray joiners not adjacent to virama
        # Valid patterns: Virama + ZWJ (half form / eyelash ra), Virama + ZWNJ (explicit halant)
        # Remove standalone ZWJ/ZWNJ preceding or following whitespace
        normalized = re.sub(r"\s+[\u200C\u200D]+", " ", normalized)
        normalized = re.sub(r"[\u200C\u200D]+\s+", " ", normalized)

    # Step 7: Final NFC canonicalization
    return unicodedata.normalize("NFC", normalized)


def normalize_with_stats(text: str) -> NormalizationResult:
    """Normalizes text and returns change count information."""
    res = normalize_devanagari(text)
    modifications = 0 if res == text else sum(1 for a, b in zip(text, res) if a != b) + abs(len(text) - len(res))
    return NormalizationResult(normalized_text=res, modifications_made=modifications)
