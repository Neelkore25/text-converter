"""Tests for Devanagari Cluster Parser (Phase 5)."""
import pytest
from backend.app.conversion.cluster_parser import (
    ClusterType,
    DevanagariCluster,
    parse_devanagari_clusters,
)


def test_parse_independent_vowels():
    """Verify parsing of independent vowels."""
    clusters = parse_devanagari_clusters("अ आ इ ई उ ऊ ऋ ए ऐ ओ औ")
    # Filter out whitespace
    vowel_clusters = [c for c in clusters if c.cluster_type == ClusterType.INDEPENDENT_VOWEL]
    assert len(vowel_clusters) == 11
    assert vowel_clusters[0].raw_text == "अ"
    assert vowel_clusters[1].raw_text == "आ"
    assert vowel_clusters[2].raw_text == "इ"
    assert vowel_clusters[3].raw_text == "ई"


def test_parse_simple_consonants():
    """Verify parsing single consonants without matras."""
    clusters = parse_devanagari_clusters("कमळ")
    assert len(clusters) == 3
    assert clusters[0].base_consonant == "क"
    assert clusters[0].vowel_sign is None
    assert clusters[1].base_consonant == "म"
    assert clusters[2].base_consonant == "ळ"


def test_parse_matra_series():
    """Verify consonants with matras are parsed as single cohesive clusters."""
    text = "कि की कु कू के कै को कौ कं कः"
    clusters = [c for c in parse_devanagari_clusters(text) if c.is_devanagari]
    assert len(clusters) == 10

    # ki (कि)
    ki = clusters[0]
    assert ki.base_consonant == "क"
    assert ki.vowel_sign == "ि"
    assert not ki.has_reph
    assert not ki.half_consonants

    # kii (की)
    kii = clusters[1]
    assert kii.base_consonant == "क"
    assert kii.vowel_sign == "ी"

    # kam (कं)
    kam = clusters[8]
    assert kam.base_consonant == "क"
    assert kam.modifiers == ["ं"]

    # kah (कः)
    kah = clusters[9]
    assert kah.base_consonant == "क"
    assert kah.modifiers == ["ः"]


def test_parse_conjunct_clusters():
    """Verify parsing multi-consonant conjuncts like क्त, स्त, स्त्र."""
    # क्त (क + ् + त)
    clusters = parse_devanagari_clusters("क्त")
    assert len(clusters) == 1
    kt = clusters[0]
    assert kt.half_consonants == ["क्"]
    assert kt.base_consonant == "त"

    # स्त्र (स् + त् + र)
    clusters = parse_devanagari_clusters("स्त्र")
    assert len(clusters) == 1
    str_c = clusters[0]
    assert str_c.half_consonants == ["स्", "त्"]
    assert str_c.base_consonant == "र"

    # स्त्री (स् + त् + र + ी)
    clusters = parse_devanagari_clusters("स्त्री")
    assert len(clusters) == 1
    stree = clusters[0]
    assert stree.half_consonants == ["स्", "त्"]
    assert stree.base_consonant == "र"
    assert stree.vowel_sign == "ी"


def test_parse_reph():
    """Verify leading reph (र्) is correctly identified and separated from base consonant."""
    # र्क (र् + क)
    clusters = parse_devanagari_clusters("र्क")
    assert len(clusters) == 1
    rk = clusters[0]
    assert rk.has_reph is True
    assert rk.base_consonant == "क"
    assert rk.vowel_sign is None

    # र्कि (र् + क + ि)
    clusters = parse_devanagari_clusters("र्कि")
    assert len(clusters) == 1
    rki = clusters[0]
    assert rki.has_reph is True
    assert rki.base_consonant == "क"
    assert rki.vowel_sign == "ि"

    # सूर्य (स + ू + र् + य) -> 'सू', 'र्य'
    clusters = [c for c in parse_devanagari_clusters("सूर्य") if c.is_devanagari]
    assert len(clusters) == 2
    su, rya = clusters[0], clusters[1]
    assert su.base_consonant == "स"
    assert su.vowel_sign == "ू"
    assert rya.has_reph is True
    assert rya.base_consonant == "य"


def test_parse_digits_and_punctuation():
    """Verify digits and danda punctuation."""
    clusters = parse_devanagari_clusters("१२३।")
    assert len(clusters) == 4
    assert clusters[0].cluster_type == ClusterType.DIGIT
    assert clusters[0].raw_text == "१"
    assert clusters[1].cluster_type == ClusterType.DIGIT
    assert clusters[1].raw_text == "२"
    assert clusters[2].cluster_type == ClusterType.DIGIT
    assert clusters[2].raw_text == "३"
    assert clusters[3].cluster_type == ClusterType.PUNCTUATION
    assert clusters[3].raw_text == "।"


def test_sentence_roundtrip_coverage():
    """Verify that concatenating all cluster raw_text reconstructs the exact original sentence."""
    sentence = "महाराष्ट्र भारतातील एक महत्त्वाचे राज्य आहे. त्याचे क्षेत्रफळ ३,०७,७१३ चौ. किमी आहे!"
    clusters = parse_devanagari_clusters(sentence)
    reconstructed = "".join(c.raw_text for c in clusters)
    assert reconstructed == sentence, "Cluster parser dropped or corrupted characters"
