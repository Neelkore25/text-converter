"""Tests for Unicode Devanagari Normalizer (Phase 4)."""
import pytest
from backend.app.conversion.devanagari_normalizer import (
    normalize_devanagari,
    normalize_with_stats,
    ZWJ,
    ZWNJ,
)


def test_empty_and_ascii_passthrough():
    """Verify that empty strings and ASCII text pass through unharmed."""
    assert normalize_devanagari("") == ""
    assert normalize_devanagari("Hello World! 123") == "Hello World! 123"


def test_canonical_independent_vowels_restoration():
    """Verify reconstitution of anomalous typed independent vowels."""
    # अ + ा -> आ
    assert normalize_devanagari("\u0905\u093E") == "आ"
    # अ + ो -> ओ
    assert normalize_devanagari("\u0905\u094B") == "ओ"
    # अ + ा + े -> ओ
    assert normalize_devanagari("\u0905\u093E\u0947") == "ओ"
    # अ + ौ -> औ
    assert normalize_devanagari("\u0905\u094C") == "औ"
    # अ + ा + ै -> औ
    assert normalize_devanagari("\u0905\u093E\u0948") == "औ"
    # ए + े -> ऐ
    assert normalize_devanagari("\u090F\u0947") == "ऐ"
    # ए + ॅ -> ऍ
    assert normalize_devanagari("\u090F\u0945") == "ऍ"
    # अ + ा + ॅ -> ऑ
    assert normalize_devanagari("\u0905\u093E\u0945") == "ऑ"


def test_nukta_reordering():
    """Verify misordered nukta is moved to attach immediately to consonant."""
    # 'क' + 'ा' + '़' -> 'क' + '़' + 'ा' (i.e. क़ा)
    misordered = "\u0915\u093E\u093C"
    expected = "\u0915\u093C\u093E"
    assert normalize_devanagari(misordered) == expected


def test_deduplication_of_combining_marks():
    """Verify that multiple consecutive viramas, nuktas, or anusvaras are deduplicated."""
    # Multiple viramas
    assert normalize_devanagari("क्" + "\u094D" + "\u094D") == "क्"
    # Multiple nuktas
    assert normalize_devanagari("क" + "\u093C" + "\u093C") == "क\u093C"
    # Multiple anusvaras
    assert normalize_devanagari("मं" + "\u0902") == "मं"


def test_space_between_consonant_and_matra_cleaned():
    """Verify accidental space between consonant and matra is stripped."""
    assert normalize_devanagari("क  ा") == "का"
    assert normalize_devanagari("म \tि") == "मि"


def test_marathi_sentences_preserved():
    """Verify standard Marathi sentences retain full semantic integrity."""
    sentence = "महाराष्ट्र भारतातील एक महत्त्वाचे राज्य आहे."
    res = normalize_devanagari(sentence)
    assert res == sentence


def test_normalize_with_stats():
    """Verify stats reporting."""
    res = normalize_with_stats("\u0905\u093E")
    assert res.normalized_text == "आ"
    assert res.modifications_made > 0

    clean_res = normalize_with_stats("महाराष्ट्र")
    assert clean_res.normalized_text == "महाराष्ट्र"
    assert clean_res.modifications_made == 0
