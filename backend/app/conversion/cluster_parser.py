"""Devanagari Cluster Parser (Phase 5).

Parses Devanagari text into logical orthographic syllables (Aksharas),
extracting Reph, Half-consonants, Base consonant, Vowel signs (Matras),
and Modifiers (Anusvara, Visarga, Candrabindu).
"""
from __future__ import annotations

import enum
import re
from dataclasses import dataclass, field
from typing import List, Optional


class ClusterType(str, enum.Enum):
    INDEPENDENT_VOWEL = "independent_vowel"
    CONSONANT_SYLLABLE = "consonant_syllable"
    DIGIT = "digit"
    PUNCTUATION = "punctuation"
    WHITESPACE = "whitespace"
    NON_DEVANAGARI = "non_devanagari"


# Unicode Ranges & Constants
DEVANAGARI_VOWELS = set("\u0904\u0905\u0906\u0907\u0908\u0909\u090A\u090B\u090C\u090D\u090E\u090F\u0910\u0911\u0912\u0913\u0914\u0960\u0961")
DEVANAGARI_CONSONANTS = set(
    "\u0915\u0916\u0917\u0918\u0919"  # Velar
    "\u091A\u091B\u091C\u091D\u091E"  # Palatal
    "\u091F\u0920\u0921\u0922\u0923"  # Retroflex
    "\u0924\u0925\u0926\u0927\u0928"  # Dental
    "\u0929"                          # NNNA
    "\u092A\u092B\u092C\u092D\u092E"  # Labial
    "\u092F\u0930\u0931\u0932\u0933\u0934\u0935"  # Approximants & Marathi RRA/LLA
    "\u0936\u0937\u0938\u0939"        # Fricatives
    "\u0958\u0959\u095A\u095B\u095C\u095D\u095E\u095F"  # Precomposed nukta consonants
)
DEVANAGARI_MATRAS = set("\u093E\u093F\u0940\u0941\u0942\u0943\u0944\u0945\u0946\u0947\u0948\u0949\u094A\u094B\u094C\u0962\u0963")
DEVANAGARI_MODIFIERS = set("\u0901\u0902\u0903\u093C\u093D")
DEVANAGARI_DIGITS = set("\u0966\u0967\u0968\u0969\u096A\u096B\u096C\u096D\u096E\u096F")
VIRAMA = "\u094D"
NUKTA = "\u093C"
RA = "\u0930"
ZWJ = "\u200D"
ZWNJ = "\u200C"


@dataclass
class DevanagariCluster:
    raw_text: str
    is_devanagari: bool
    cluster_type: ClusterType
    has_reph: bool = False
    half_consonants: List[str] = field(default_factory=list)
    base_consonant: Optional[str] = None
    vowel_sign: Optional[str] = None
    modifiers: List[str] = field(default_factory=list)
    has_explicit_halant: bool = False


# Regex pattern to segment Devanagari text into orthographic syllables
# 1. Whitespace
# 2. Devanagari digits
# 3. Independent vowels + optional modifiers
# 4. Consonant clusters: (Consonant + [Nukta] + Virama)* + Consonant + [Nukta] + [Matra] + [Modifiers] + [Virama]
# 5. Danda / Devanagari punctuation
# 6. Any other single non-Devanagari character
CLUSTER_REGEX = re.compile(
    r"("
    r"[ \t\r\n]+"                                                # Whitespace
    r"|[\u0966-\u096F]"                                          # Devanagari digits
    r"|[\u0964\u0965]"                                           # Danda, Double Danda
    r"|[\u0904-\u0914\u0960\u0961][\u0901\u0902\u0903\u093D]*"     # Independent Vowel + Modifiers
    r"|(?:(?:[\u0915-\u0939\u0958-\u095F]\u093C?\u094D[\u200C\u200D]?)+[\u0915-\u0939\u0958-\u095F]\u093C?[\u093E-\u094C\u0945-\u0948\u0949-\u094C\u0962\u0963]?[\u0901\u0902\u0903\u093D]*)" # Complex Consonant Cluster
    r"|(?:[\u0915-\u0939\u0958-\u095F]\u093C?\u094D[\u200C\u200D]?)"  # Standalone Half Consonant with Halant
    r"|[\u0915-\u0939\u0958-\u095F]\u093C?[\u093E-\u094C\u0945-\u0948\u0949-\u094C\u0962\u0963]?[\u0901\u0902\u0903\u093D]*"  # Single Consonant + Matra + Modifiers
    r"|[\u0901\u0902\u0903\u093C\u093D\u094D]"                   # Isolated combining marks
    r"|[^\u0900-\u097F]"                                         # Any other non-Devanagari character
    r")"
)


def parse_devanagari_clusters(text: str) -> List[DevanagariCluster]:
    """Parses a normalized Devanagari string into a list of DevanagariCluster objects."""
    if not text:
        return []

    tokens = [m for m in CLUSTER_REGEX.findall(text) if m]
    clusters: List[DevanagariCluster] = []

    for token in tokens:
        cluster = _analyze_token(token)
        clusters.append(cluster)

    return clusters


def _analyze_token(token: str) -> DevanagariCluster:
    # 1. Check whitespace
    if token.isspace():
        return DevanagariCluster(
            raw_text=token,
            is_devanagari=False,
            cluster_type=ClusterType.WHITESPACE,
        )

    # 2. Check digits
    if len(token) == 1 and token in DEVANAGARI_DIGITS:
        return DevanagariCluster(
            raw_text=token,
            is_devanagari=True,
            cluster_type=ClusterType.DIGIT,
        )

    # 3. Check punctuation
    if token in ("\u0964", "\u0965"):
        return DevanagariCluster(
            raw_text=token,
            is_devanagari=True,
            cluster_type=ClusterType.PUNCTUATION,
        )

    # 4. Check Non-Devanagari characters (ASCII, Latin, etc.)
    if not any(0x0900 <= ord(c) <= 0x097F for c in token):
        return DevanagariCluster(
            raw_text=token,
            is_devanagari=False,
            cluster_type=ClusterType.NON_DEVANAGARI,
        )

    # 5. Check Independent Vowel
    if token[0] in DEVANAGARI_VOWELS:
        base_vowel = token[0]
        mods = [c for c in token[1:] if c in DEVANAGARI_MODIFIERS]
        return DevanagariCluster(
            raw_text=token,
            is_devanagari=True,
            cluster_type=ClusterType.INDEPENDENT_VOWEL,
            base_consonant=base_vowel,
            modifiers=mods,
        )

    # 6. Check Consonant Cluster / Syllable
    # Check for leading Reph (र् = RA + VIRAMA at the beginning, followed by another consonant)
    has_reph = False
    working_token = token
    if working_token.startswith(RA + VIRAMA) and len(working_token) > 2:
        # Verify there is a consonant following
        has_reph = True
        working_token = working_token[2:]

    # Separate any trailing modifiers (anusvara, visarga, candrabindu)
    modifiers: List[str] = []
    while working_token and working_token[-1] in DEVANAGARI_MODIFIERS:
        modifiers.insert(0, working_token[-1])
        working_token = working_token[:-1]

    # Separate any trailing vowel sign (matra)
    vowel_sign: Optional[str] = None
    if working_token and working_token[-1] in DEVANAGARI_MATRAS:
        vowel_sign = working_token[-1]
        working_token = working_token[:-1]

    # Check for standalone halant at the very end
    has_explicit_halant = False
    if working_token.endswith(VIRAMA):
        has_explicit_halant = True
        working_token = working_token[:-1]

    # Now decompose working_token into half-consonants and base consonant
    # Tokens split by VIRAMA
    parts = working_token.split(VIRAMA)
    half_consonants: List[str] = []
    base_consonant: Optional[str] = None

    if len(parts) > 1:
        # All parts except last are half consonants
        for p in parts[:-1]:
            if p:
                half_consonants.append(p + VIRAMA)
        base_consonant = parts[-1] if parts[-1] else None
    elif len(parts) == 1 and parts[0]:
        base_consonant = parts[0]

    return DevanagariCluster(
        raw_text=token,
        is_devanagari=True,
        cluster_type=ClusterType.CONSONANT_SYLLABLE,
        has_reph=has_reph,
        half_consonants=half_consonants,
        base_consonant=base_consonant,
        vowel_sign=vowel_sign,
        modifiers=modifiers,
        has_explicit_halant=has_explicit_halant,
    )
