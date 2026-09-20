"""Master Unicode Devanagari to Shivaji01 Conversion Engine.

Implements cluster-aware Devanagari conversion to legacy Shivaji01 text,
handling prefix Short-I (ि) reordering, Reph (र्), Rakar (्र), dedicated ligatures,
half-forms, matras, modifiers, and digits.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from backend.app.conversion.cluster_parser import (
    ClusterType,
    DevanagariCluster,
    parse_devanagari_clusters,
)
from backend.app.conversion.devanagari_normalizer import normalize_devanagari
from backend.app.conversion.shivaji_mapping import (
    DEDICATED_CONJUNCTS,
    DEVANAGARI_DIGITS_MAP,
    FULL_CONSONANTS,
    HALF_CONSONANTS,
    INDEPENDENT_VOWELS,
    MATRAS,
    MODIFIERS,
    PUNCTUATION_MAP,
    RAKAR_INVERTED_V,
    RAKAR_SLASH,
    REPH_GLYPH,
    ROUND_CONSONANTS_FOR_RAKAR,
)


@dataclass
class ConversionResult:
    converted_text: str
    total_characters: int
    converted_characters: int
    warning_count: int
    unmapped_characters: List[str] = field(default_factory=list)


def convert_unicode_to_shivaji(text: str) -> ConversionResult:
    """Converts a Unicode Devanagari / Marathi string into legacy Shivaji01 text.

    Args:
        text: Input string (Devanagari, Marathi, or mixed text).

    Returns:
        ConversionResult containing converted text and diagnostic statistics.
    """
    if not text:
        return ConversionResult(
            converted_text="",
            total_characters=0,
            converted_characters=0,
            warning_count=0,
        )

    # Step 1: Unicode Normalization
    normalized = normalize_devanagari(text)

    # Step 2: Cluster Segmentation
    clusters = parse_devanagari_clusters(normalized)

    # Step 3: Cluster Conversion
    output_parts: List[str] = []
    unmapped: List[str] = []

    for cluster in clusters:
        converted_chunk = _convert_cluster(cluster)
        output_parts.append(converted_chunk)

        # Check for any remaining unmapped Devanagari characters in the converted chunk
        for ch in converted_chunk:
            if 0x0900 <= ord(ch) <= 0x097F:
                unmapped.append(ch)

    full_output = "".join(output_parts)
    total_chars = len(text)
    warning_count = len(unmapped)
    converted_chars = max(0, total_chars - warning_count)

    return ConversionResult(
        converted_text=full_output,
        total_characters=total_chars,
        converted_characters=converted_chars,
        warning_count=warning_count,
        unmapped_characters=unmapped,
    )


def _convert_cluster(cluster: DevanagariCluster) -> str:
    # 1. Whitespace & Non-Devanagari passthrough
    if cluster.cluster_type in (ClusterType.WHITESPACE, ClusterType.NON_DEVANAGARI):
        return cluster.raw_text

    # 2. Devanagari Digits (०-९)
    if cluster.cluster_type == ClusterType.DIGIT:
        return DEVANAGARI_DIGITS_MAP.get(cluster.raw_text, cluster.raw_text)

    # 3. Punctuation (।, ॥)
    if cluster.cluster_type == ClusterType.PUNCTUATION:
        return PUNCTUATION_MAP.get(cluster.raw_text, cluster.raw_text)

    # 4. Independent Vowels (अ, आ, इ, etc.)
    if cluster.cluster_type == ClusterType.INDEPENDENT_VOWEL:
        base_vowel = INDEPENDENT_VOWELS.get(cluster.base_consonant or "", cluster.base_consonant or "")
        mods = "".join(MODIFIERS.get(m, m) for m in cluster.modifiers)
        return base_vowel + mods

    # 5. Consonant Syllables & Conjuncts
    if cluster.cluster_type == ClusterType.CONSONANT_SYLLABLE:
        return _convert_consonant_syllable(cluster)

    return cluster.raw_text


def _convert_consonant_syllable(cluster: DevanagariCluster) -> str:
    # Check for dedicated combos first (e.g. रु, रू, कृ, फृ, हृ)
    combo_key = (cluster.base_consonant or "") + (cluster.vowel_sign or "")
    if not cluster.half_consonants and combo_key in DEDICATED_CONJUNCTS:
        core_str = DEDICATED_CONJUNCTS[combo_key]
        # Append modifiers and reph if any
        mods = "".join(MODIFIERS.get(m, m) for m in cluster.modifiers)
        reph = REPH_GLYPH if cluster.has_reph else ""
        return core_str + reph + mods

    # Check for dedicated conjuncts (e.g. क्त, क्र, ज्ञ, त्र, क्ष, श्र, द्य, द्व, etc.)
    full_consonant_cluster = "".join(cluster.half_consonants) + (cluster.base_consonant or "")
    has_dedicated_conjunct = full_consonant_cluster in DEDICATED_CONJUNCTS

    is_short_i = cluster.vowel_sign == "\u093F"
    prefix_i = "i" if is_short_i else ""

    # Build core consonant representation
    if has_dedicated_conjunct:
        consonant_part = DEDICATED_CONJUNCTS[full_consonant_cluster]
    else:
        # Check if trailing parts match a dedicated conjunct (e.g. स्त्र -> s + त्र -> s~)
        matched_trailing = False
        consonant_part = ""
        for split_idx in range(1, len(cluster.half_consonants) + 1):
            tail_cluster = "".join(cluster.half_consonants[split_idx:]) + (cluster.base_consonant or "")
            if tail_cluster in DEDICATED_CONJUNCTS:
                head_parts = [HALF_CONSONANTS.get(hc, hc) for hc in cluster.half_consonants[:split_idx]]
                consonant_part = "".join(head_parts) + DEDICATED_CONJUNCTS[tail_cluster]
                matched_trailing = True
                break

        if not matched_trailing:
            # Build half-consonants + base consonant
            half_parts = []
            for hc in cluster.half_consonants:
                half_parts.append(HALF_CONSONANTS.get(hc, hc))

            # Base consonant or rakar
            base = cluster.base_consonant or ""
            base_mapped = FULL_CONSONANTS.get(base, base)

            # Check for Rakar on base consonant (e.g. base = र preceded by a half consonant)
            if base == "\u0930" and cluster.half_consonants:
                # Last half consonant gets rakar attached
                prev_hc = cluster.half_consonants[-1]
                prev_consonant = prev_hc.replace("\u094D", "")

                # Choose inverted-v rakar (`) for round consonants, slash (/) for others
                rakar = RAKAR_INVERTED_V if prev_consonant in ROUND_CONSONANTS_FOR_RAKAR else RAKAR_SLASH

                # Pop the last half consonant from half_parts
                half_parts.pop()
                # If prev_consonant is a full consonant in Shivaji, use full + rakar
                base_full = FULL_CONSONANTS.get(prev_consonant, prev_consonant)
                consonant_part = "".join(half_parts) + base_full + rakar
            else:
                consonant_part = "".join(half_parts) + base_mapped

    # Build Matra (if not short-i)
    matra_part = ""
    if cluster.vowel_sign and not is_short_i:
        matra_part = MATRAS.get(cluster.vowel_sign, cluster.vowel_sign)

    # Build Reph
    reph_part = REPH_GLYPH if cluster.has_reph else ""

    # Build Modifiers (Anusvara, Visarga, etc.)
    mod_part = "".join(MODIFIERS.get(m, m) for m in cluster.modifiers)

    # Standalone halant if explicit
    halant_part = MODIFIERS["\u094D"] if cluster.has_explicit_halant else ""

    # In Shivaji01 legacy sequence:
    # Prefix-I precedes the entire consonant block!
    # Followed by consonant(s) -> Matra -> Reph -> Modifiers -> Halant
    return prefix_i + consonant_part + matra_part + reph_part + mod_part + halant_part
