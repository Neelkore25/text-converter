"""Tests for Unicode to Shivaji01 Conversion Engine (Phases 6, 7, 8, 9)."""
import pytest
from backend.app.conversion.unicode_to_shivaji import convert_unicode_to_shivaji


def test_independent_vowels_conversion():
    """Phase 6: Verify conversion of independent vowels."""
    assert convert_unicode_to_shivaji("अ").converted_text == "A"
    assert convert_unicode_to_shivaji("आ").converted_text == "Aa"
    assert convert_unicode_to_shivaji("इ").converted_text == "["
    assert convert_unicode_to_shivaji("उ").converted_text == "]"
    assert convert_unicode_to_shivaji("ऊ").converted_text == "}"
    assert convert_unicode_to_shivaji("ऋ").converted_text == "?"
    assert convert_unicode_to_shivaji("ए").converted_text == "e"
    assert convert_unicode_to_shivaji("ऐ").converted_text == "eo"
    assert convert_unicode_to_shivaji("ओ").converted_text == "A\u00DC"
    assert convert_unicode_to_shivaji("औ").converted_text == "A\u00DD"


def test_basic_consonants_conversion():
    """Phase 6: Verify base consonants."""
    assert convert_unicode_to_shivaji("क").converted_text == "k"
    assert convert_unicode_to_shivaji("ख").converted_text == "K"
    assert convert_unicode_to_shivaji("ग").converted_text == "ga"
    assert convert_unicode_to_shivaji("घ").converted_text == "Ga"
    assert convert_unicode_to_shivaji("च").converted_text == "ca"
    assert convert_unicode_to_shivaji("त").converted_text == "t"
    assert convert_unicode_to_shivaji("द").converted_text == "d"
    assert convert_unicode_to_shivaji("म").converted_text == "ma"
    assert convert_unicode_to_shivaji("र").converted_text == "r"
    assert convert_unicode_to_shivaji("स").converted_text == "sa"
    assert convert_unicode_to_shivaji("ह").converted_text == "h"
    assert convert_unicode_to_shivaji("ळ").converted_text == "L"


def test_matra_series_ka():
    """Phase 7: Verify complete 12-matra series for क."""
    assert convert_unicode_to_shivaji("का").converted_text == "ka"
    assert convert_unicode_to_shivaji("कि").converted_text == "ik"  # Prefix Short-I
    assert convert_unicode_to_shivaji("की").converted_text == "kI"
    assert convert_unicode_to_shivaji("कु").converted_text == "ku"
    assert convert_unicode_to_shivaji("कू").converted_text == "kU"
    assert convert_unicode_to_shivaji("के").converted_text == "ko"
    assert convert_unicode_to_shivaji("कै").converted_text == "kO"
    assert convert_unicode_to_shivaji("को").converted_text == "k\u00DC"
    assert convert_unicode_to_shivaji("कौ").converted_text == "k\u00DD"
    assert convert_unicode_to_shivaji("कं").converted_text == "kM"
    assert convert_unicode_to_shivaji("कः").converted_text == "k:"


def test_critical_short_i_prefix_reordering():
    """Phase 7: Critical requirement - Short-I (ि) must precede consonant cluster in legacy output."""
    assert convert_unicode_to_shivaji("कि").converted_text == "ik"
    assert convert_unicode_to_shivaji("गि").converted_text == "iga"
    assert convert_unicode_to_shivaji("ति").converted_text == "it"
    assert convert_unicode_to_shivaji("नि").converted_text == "ina"
    assert convert_unicode_to_shivaji("मि").converted_text == "ima"
    assert convert_unicode_to_shivaji("शि").converted_text == "iSa"
    assert convert_unicode_to_shivaji("प्रि").converted_text == "ip/"
    assert convert_unicode_to_shivaji("क्रि").converted_text == "i\u00CB"


def test_dedicated_conjuncts():
    """Phase 8: Verify preformed conjunct ligatures."""
    assert convert_unicode_to_shivaji("क्त").converted_text == ">"
    assert convert_unicode_to_shivaji("क्र").converted_text == "\u00CB"
    assert convert_unicode_to_shivaji("ज्ञ").converted_text == "&"
    assert convert_unicode_to_shivaji("त्र").converted_text == "~"
    assert convert_unicode_to_shivaji("क्ष").converted_text == "xa"
    assert convert_unicode_to_shivaji("श्र").converted_text == "Ea"
    assert convert_unicode_to_shivaji("द्य").converted_text == "V"
    assert convert_unicode_to_shivaji("द्व").converted_text == "W"
    assert convert_unicode_to_shivaji("द्ध").converted_text == "w"
    assert convert_unicode_to_shivaji("द्द").converted_text == "_"


def test_general_conjuncts_and_halants():
    """Phase 8: Verify multi-consonant clusters and halants."""
    # स्त (half SA + TA)
    assert convert_unicode_to_shivaji("स्त").converted_text == "st"
    # स्त्र (half SA + TR)
    assert convert_unicode_to_shivaji("स्त्र").converted_text == "s~"
    # स्त्री (half SA + TR + II)
    assert convert_unicode_to_shivaji("स्त्री").converted_text == "s~I"


def test_reph_handling():
    """Phase 9: Verify Reph (र् + consonant)."""
    # र्क -> k-
    assert convert_unicode_to_shivaji("र्क").converted_text == "k-"
    # र्कि -> ik- (prefix short-i before consonant, reph after)
    assert convert_unicode_to_shivaji("र्कि").converted_text == "ik-"
    # कर्म -> kma-
    assert convert_unicode_to_shivaji("कर्म").converted_text == "kma-"
    # धर्म -> Qama-
    assert convert_unicode_to_shivaji("धर्म").converted_text == "Qama-"
    # सूर्य -> saUya-
    assert convert_unicode_to_shivaji("सूर्य").converted_text == "saUya-"


def test_rakar_handling():
    """Phase 9: Verify Rakar (consonant + ्र)."""
    # प्र -> p/
    assert convert_unicode_to_shivaji("प्र").converted_text == "p/"
    # ग्र -> ga/
    assert convert_unicode_to_shivaji("ग्र").converted_text == "ga/"
    # द्र -> d/
    assert convert_unicode_to_shivaji("द्र").converted_text == "d/"
    # ट्र -> T` (round consonant with inverted-v rakar)
    assert convert_unicode_to_shivaji("ट्र").converted_text == "T`"
    # ड्र -> D` (round consonant with inverted-v rakar)
    assert convert_unicode_to_shivaji("ड्र").converted_text == "D`"


def test_marathi_digits_and_punctuation():
    """Verify Devanagari digits and danda punctuation."""
    res = convert_unicode_to_shivaji("०१२३४५६७८९।")
    assert res.converted_text == "0123456789."
    assert res.warning_count == 0


def test_real_marathi_sentences():
    """Verify conversion of real Marathi sentences without unmapped characters."""
    sentences = [
        "महाराष्ट्र माझा देश आहे.",
        "माझे नाव नील आहे.",
        "मला संगणक अभियांत्रिकी शिकायला आवडते.",
        "महाराष्ट्र भारतातील एक राज्य आहे.",
    ]
    for s in sentences:
        res = convert_unicode_to_shivaji(s)
        assert res.warning_count == 0, f"Unmapped characters in '{s}': {res.unmapped_characters}"
        assert len(res.converted_text) > 0
