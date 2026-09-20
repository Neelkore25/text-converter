"""Shivaji01 Mapping Tables (Phase 6, 7, 8, 9).

Contains ground-truth mappings from Unicode Devanagari characters and combinations
to legacy Shivaji01 character sequences.
"""
from __future__ import annotations

from typing import Dict, Optional, Tuple

# 1. Independent Vowels
INDEPENDENT_VOWELS: Dict[str, str] = {
    "\u0905": "A",          # अ
    "\u0906": "Aa",         # आ
    "\u0907": "[",          # इ
    "\u0908": "\u0161",     # ई (scaron)
    "\u0909": "]",          # उ
    "\u090A": "}",          # ऊ
    "\u090B": "?",          # ऋ
    "\u090F": "e",          # ए
    "\u0910": "eo",         # ऐ
    "\u0913": "A\u00DC",    # ओ (A + Ü)
    "\u0914": "A\u00DD",    # औ (A + Ý)
    "\u090D": "e^",         # ऍ
    "\u0911": "Aa^",        # ऑ
}

# 2. Consonants:
# Distinction between:
# - inherent-stem consonants (e.g. क 'k', त 't', द 'd', प 'p', र 'r', ह 'h', ळ 'L', ट 'T', ठ 'z', ड 'D', ढ 'Z')
# - vertical-stem consonants (formed by half-form + 'a', e.g. ग 'ga', म 'ma', न 'na', स 'sa', etc.)
FULL_CONSONANTS: Dict[str, str] = {
    "\u0915": "k",          # क
    "\u0916": "K",          # ख
    "\u0917": "ga",         # ग
    "\u0918": "Ga",         # घ
    "\u0919": "=",          # ङ
    "\u091A": "ca",         # च
    "\u091B": "C",          # छ
    "\u091C": "ja",         # ज
    "\u091D": "Ja",         # झ
    "\u091E": "Ha",         # ञ
    "\u091F": "T",          # ट
    "\u0920": "z",          # ठ
    "\u0921": "D",          # ड
    "\u0922": "Z",          # ढ
    "\u0923": "Na",         # ण
    "\u0924": "t",          # त
    "\u0925": "qa",         # थ
    "\u0926": "d",          # द
    "\u0927": "Qa",         # ध
    "\u0928": "na",         # न
    "\u092A": "p",          # प
    "\u092B": "fa",         # फ
    "\u092C": "ba",         # ब
    "\u092D": "Ba",         # भ
    "\u092E": "ma",         # म
    "\u092F": "ya",         # य
    "\u0930": "r",          # र
    "\u0931": "r",          # ऱ (Marathi RRA)
    "\u0932": "la",         # ल
    "\u0933": "L",          # ळ
    "\u0935": "va",         # व
    "\u0936": "Sa",         # श
    "\u0937": "Ya",         # ष
    "\u0938": "sa",         # स
    "\u0939": "h",          # ह
    # Nukta consonants
    "\u0958": "k,",         # क़
    "\u0959": "K,",         # ख़
    "\u095A": "ga,",        # ग़
    "\u095B": "ja,",        # ज़
    "\u095C": "D,",         # ड़
    "\u095D": "Z,",         # ढ़
    "\u095E": "fa,",        # फ़
}

# 3. Half-form Consonants (with virama / halant)
HALF_CONSONANTS: Dict[str, str] = {
    "\u0915\u094D": "@",           # क्
    "\u0916\u094D": "#",           # ख्
    "\u0917\u094D": "g",           # ग्
    "\u0918\u094D": "G",           # घ्
    "\u091A\u094D": "c",           # च्
    "\u091C\u094D": "j",           # ज्
    "\u091D\u094D": "J",           # झ्
    "\u091E\u094D": "H",           # ञ्
    "\u0923\u094D": "N",           # ण्
    "\u0924\u094D": "%",           # त्
    "\u0925\u094D": "q",           # थ्
    "\u0927\u094D": "Q",           # ध्
    "\u0928\u094D": "n",           # न्
    "\u092A\u094D": "\u00E1",      # प् (Shivaji halffm_PA: 0xE1 / 'á')
    "\u092B\u094D": "F",           # फ्
    "\u092C\u094D": "b",           # ब्
    "\u092D\u094D": "B",           # भ्
    "\u092E\u094D": "m",           # म्
    "\u092F\u094D": "y",           # य्
    "\u0930\u094D": "-",           # र् (Reph)
    "\u0932\u094D": "l",           # ल्
    "\u0935\u094D": "v",           # व्
    "\u0936\u094D": "S",           # श्
    "\u0937\u094D": "Y",           # ष्
    "\u0938\u094D": "s",           # स्
    "\u0939\u094D": "*",           # ह्
    "\u0936\u094D\u0930\u094D": "E",  # श्र्
    "\u0915\u094D\u0937\u094D": "x",  # क्ष्
    "\u0924\u094D\u0924\u094D": "<",  # त्त्
}

# 4. Preformed Dedicated Conjuncts & Special Combinations
DEDICATED_CONJUNCTS: Dict[str, str] = {
    "\u0915\u094D\u0924": ">",          # क्त
    "\u0915\u094D\u0930": "\u00CB",     # क्र
    "\u091C\u094D\u091E": "&",          # ज्ञ
    "\u0924\u094D\u0930": "~",          # त्र
    "\u0915\u094D\u0937": "xa",         # क्ष
    "\u0936\u094D\u0930": "Ea",         # श्र
    "\u091F\u094D\u091F": "+",          # ट्ट
    "\u0920\u094D\u0920": "{",          # ठ्ठ
    "\u0924\u094D\u0924": "<a",         # त्त
    "\u0926\u094D\u0926": "_",          # द्द
    "\u0926\u094D\u0927": "w",          # द्ध
    "\u0926\u094D\u092F": "V",          # द्य
    "\u0926\u094D\u0935": "W",          # द्व
    "\u092B\u094D\u0930": "\u00CD",     # फ्र
    "\u0939\u094D\u0930": "\u0153",     # ह्र
    "\u0939\u094D\u092F": "(",          # ह्य
    # Special Consonant + Vowel Combos
    "\u0930\u0941": "\u00C9",           # रु
    "\u0930\u0942": "$",                # रू
    "\u0915\u0943": "\u00CC",           # कृ
    "\u092B\u0943": "\u00CE",           # फृ
    "\u0939\u0943": ")",                # हृ
}

# 5. Dependent Vowels (Matras)
# Note: Short I (\u093F) is prefix; others are suffix / attachment
MATRAS: Dict[str, str] = {
    "\u093E": "a",          # ा (AA)
    "\u093F": "i",          # ि (Short I - Prefix)
    "\u0940": "I",          # ी (Long II)
    "\u0941": "u",          # ु (Short U)
    "\u0942": "U",          # ू (Long UU)
    "\u0943": "R",          # ृ (Vocalic R)
    "\u0947": "o",          # े (E)
    "\u0948": "O",          # ै (AI)
    "\u094B": "\u00DC",     # ो (O)
    "\u094C": "\u00DD",     # ौ (AU)
    "\u0945": "^",          # ॅ (Candra E)
    "\u0949": "a^",         # ॉ (Candra O)
}

# 6. Modifiers
MODIFIERS: Dict[str, str] = {
    "\u0902": "M",          # Anusvara (ं)
    "\u0903": ":",          # Visarga (ः)
    "\u0901": "\u00D0",     # Candrabindu (ँ)
    "\u094D": "\\",         # Explicit Virama (्)
    "\u093C": ",",          # Nukta (़)
    "\u093D": "|",          # Avagraha (ऽ)
}

# 7. Digits: Devanagari ०-९ -> Shivaji digits 0-9
DEVANAGARI_DIGITS_MAP: Dict[str, str] = {
    "\u0966": "0",
    "\u0967": "1",
    "\u0968": "2",
    "\u0969": "3",
    "\u096A": "4",
    "\u096B": "5",
    "\u096C": "6",
    "\u096D": "7",
    "\u096E": "8",
    "\u096F": "9",
}

# 8. Punctuation
PUNCTUATION_MAP: Dict[str, str] = {
    "\u0964": ".",          # Danda
    "\u0965": "..",         # Double Danda
}

# Consonants that require inverted-v rakar (`) instead of diagonal slash (/)
ROUND_CONSONANTS_FOR_RAKAR = {"\u091F", "\u0920", "\u0921", "\u0922"}  # ट, ठ, ड, ढ
RAKAR_SLASH = "/"
RAKAR_INVERTED_V = "`"
REPH_GLYPH = "-"
