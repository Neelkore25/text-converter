"""Shivaji01 Font Glyph Catalog.

Provides a structured, verified inventory of all character codes and glyphs
in Shivaji01 Normal.ttf, mapped to their Unicode Devanagari equivalents.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class GlyphCategory(str, Enum):
    VOWEL = "vowel"
    CONSONANT = "consonant"
    HALF_FORM = "half_form"
    MATRA = "matra"
    MODIFIER = "modifier"
    CONJUNCT = "conjunct"
    DIGIT = "digit"
    PUNCTUATION = "punctuation"
    SPECIAL = "special"


@dataclass(frozen=True)
class GlyphEntry:
    code_point: int
    char: str
    glyph_name: str
    unicode_seq: str
    category: GlyphCategory
    description: str


# Catalog of Shivaji01 characters and their Devanagari associations
SHIVAJI01_GLYPH_TABLE: List[GlyphEntry] = [
    # --- Independent Vowels ---
    GlyphEntry(0x41, "A", "A", "\u0905", GlyphCategory.VOWEL, "Vowel A (अ)"),
    GlyphEntry(0x5B, "[", "bracketleft", "\u0907", GlyphCategory.VOWEL, "Vowel I (इ)"),
    GlyphEntry(0x161, "\u0161", "scaron", "\u0908", GlyphCategory.VOWEL, "Vowel II (ई)"),
    GlyphEntry(0x5D, "]", "bracketright", "\u0909", GlyphCategory.VOWEL, "Vowel U (उ)"),
    GlyphEntry(0x7D, "}", "braceright", "\u090A", GlyphCategory.VOWEL, "Vowel UU (ऊ)"),
    GlyphEntry(0x3F, "?", "question", "\u090B", GlyphCategory.VOWEL, "Vowel Vocalic R (ऋ)"),
    GlyphEntry(0x65, "e", "e", "\u090F", GlyphCategory.VOWEL, "Vowel E (ए)"),

    # --- Consonants (Base / Full forms) ---
    GlyphEntry(0x6B, "k", "k", "\u0915", GlyphCategory.CONSONANT, "Consonant KA (क)"),
    GlyphEntry(0x4B, "K", "K", "\u0916", GlyphCategory.CONSONANT, "Consonant KHA (ख)"),
    GlyphEntry(0x3D, "=", "equal", "\u0919", GlyphCategory.CONSONANT, "Consonant NGA (ङ)"),
    GlyphEntry(0x43, "C", "C", "\u091B", GlyphCategory.CONSONANT, "Consonant CHA (छ)"),
    GlyphEntry(0x54, "T", "T", "\u091F", GlyphCategory.CONSONANT, "Consonant TTA (ट)"),
    GlyphEntry(0x7A, "z", "z", "\u0920", GlyphCategory.CONSONANT, "Consonant TTHA (ठ)"),
    GlyphEntry(0x44, "D", "D", "\u0921", GlyphCategory.CONSONANT, "Consonant DDA (ड)"),
    GlyphEntry(0x5A, "Z", "Z", "\u0922", GlyphCategory.CONSONANT, "Consonant DDHA (ढ)"),
    GlyphEntry(0x74, "t", "t", "\u0924", GlyphCategory.CONSONANT, "Consonant TA (त)"),
    GlyphEntry(0x64, "d", "d", "\u0926", GlyphCategory.CONSONANT, "Consonant DA (द)"),
    GlyphEntry(0x70, "p", "p", "\u092A", GlyphCategory.CONSONANT, "Consonant PA (प)"),
    GlyphEntry(0x72, "r", "r", "\u0930", GlyphCategory.CONSONANT, "Consonant RA (र)"),
    GlyphEntry(0x68, "h", "h", "\u0939", GlyphCategory.CONSONANT, "Consonant HA (ह)"),
    GlyphEntry(0x4C, "L", "L", "\u0933", GlyphCategory.CONSONANT, "Consonant LLA (ळ)"),

    # --- Half-forms (Used before consonants or with matra AA 'a' to form full consonants) ---
    GlyphEntry(0x40, "@", "at", "\u0915\u094D", GlyphCategory.HALF_FORM, "Half KA (क्)"),
    GlyphEntry(0x23, "#", "numbersign", "\u0916\u094D", GlyphCategory.HALF_FORM, "Half KHA (ख्)"),
    GlyphEntry(0x67, "g", "g", "\u0917\u094D", GlyphCategory.HALF_FORM, "Half GA (ग्)"),
    GlyphEntry(0x47, "G", "G", "\u0918\u094D", GlyphCategory.HALF_FORM, "Half GHA (घ्)"),
    GlyphEntry(0x63, "c", "c", "\u091A\u094D", GlyphCategory.HALF_FORM, "Half CA (च्)"),
    GlyphEntry(0x6A, "j", "j", "\u091C\u094D", GlyphCategory.HALF_FORM, "Half JA (ज्)"),
    GlyphEntry(0x4A, "J", "J", "\u091D\u094D", GlyphCategory.HALF_FORM, "Half JHA (झ्)"),
    GlyphEntry(0x48, "H", "H", "\u091E\u094D", GlyphCategory.HALF_FORM, "Half NYA (ञ्)"),
    GlyphEntry(0x4E, "N", "N", "\u0923\u094D", GlyphCategory.HALF_FORM, "Half NNA (ण्)"),
    GlyphEntry(0x25, "%", "percent", "\u0924\u094D", GlyphCategory.HALF_FORM, "Half TA (त्)"),
    GlyphEntry(0x71, "q", "q", "\u0925\u094D", GlyphCategory.HALF_FORM, "Half THA (थ्)"),
    GlyphEntry(0x51, "Q", "Q", "\u0927\u094D", GlyphCategory.HALF_FORM, "Half DHA (ध्)"),
    GlyphEntry(0x6E, "n", "n", "\u0928\u094D", GlyphCategory.HALF_FORM, "Half NA (न्)"),
    GlyphEntry(0x50, "P", "P", "\u092A\u094D", GlyphCategory.HALF_FORM, "Half PA Shusha (प्)"),
    GlyphEntry(0xE1, "\u00E1", "aacute", "\u092A\u094D", GlyphCategory.HALF_FORM, "Half PA Shivaji (प्)"),
    GlyphEntry(0x46, "F", "F", "\u092B\u094D", GlyphCategory.HALF_FORM, "Half PHA (फ्)"),
    GlyphEntry(0x62, "b", "b", "\u092C\u094D", GlyphCategory.HALF_FORM, "Half BA (ब्)"),
    GlyphEntry(0x42, "B", "B", "\u092D\u094D", GlyphCategory.HALF_FORM, "Half BHA (भ्)"),
    GlyphEntry(0x6D, "m", "m", "\u092E\u094D", GlyphCategory.HALF_FORM, "Half MA (म्)"),
    GlyphEntry(0x79, "y", "y", "\u092F\u094D", GlyphCategory.HALF_FORM, "Half YA (य्)"),
    GlyphEntry(0x2D, "-", "hyphen", "\u0930\u094D", GlyphCategory.HALF_FORM, "Reph (र्)"),
    GlyphEntry(0x6C, "l", "l", "\u0932\u094D", GlyphCategory.HALF_FORM, "Half LA (ल्)"),
    GlyphEntry(0x76, "v", "v", "\u0935\u094D", GlyphCategory.HALF_FORM, "Half VA (व्)"),
    GlyphEntry(0x53, "S", "S", "\u0936\u094D", GlyphCategory.HALF_FORM, "Half SHA style 1 (श्)"),
    GlyphEntry(0x58, "X", "X", "\u0936\u094D", GlyphCategory.HALF_FORM, "Half SHA style 2 (श्)"),
    GlyphEntry(0xCF, "\u00CF", "Idieresis", "\u0936\u094D", GlyphCategory.HALF_FORM, "Half SHA style 3 (श्)"),
    GlyphEntry(0x59, "Y", "Y", "\u0937\u094D", GlyphCategory.HALF_FORM, "Half SSA (ष्)"),
    GlyphEntry(0x73, "s", "s", "\u0938\u094D", GlyphCategory.HALF_FORM, "Half SA (स्)"),
    GlyphEntry(0x2A, "*", "asterisk", "\u0939\u094D", GlyphCategory.HALF_FORM, "Half HA (ह्)"),
    GlyphEntry(0x45, "E", "E", "\u0936\u094D\u0930\u094D", GlyphCategory.HALF_FORM, "Half SHR (श्र्)"),
    GlyphEntry(0x78, "x", "x", "\u0915\u094D\u0937\u094D", GlyphCategory.HALF_FORM, "Half KSH (क्ष्)"),
    GlyphEntry(0x3C, "<", "less", "\u0924\u094D\u0924\u094D", GlyphCategory.HALF_FORM, "Half TT (त्त्)"),

    # --- Matras (Vowel Signs) ---
    GlyphEntry(0x61, "a", "a", "\u093E", GlyphCategory.MATRA, "Matra AA (ा)"),
    GlyphEntry(0x69, "i", "i", "\u093F", GlyphCategory.MATRA, "Matra I [Prefix] (ि)"),
    GlyphEntry(0x49, "I", "I", "\u0940", GlyphCategory.MATRA, "Matra II (ी)"),
    GlyphEntry(0x75, "u", "u", "\u0941", GlyphCategory.MATRA, "Matra U (ु)"),
    GlyphEntry(0x55, "U", "U", "\u0942", GlyphCategory.MATRA, "Matra UU (ू)"),
    GlyphEntry(0x52, "R", "R", "\u0943", GlyphCategory.MATRA, "Matra Vocalic R (ृ)"),
    GlyphEntry(0x6F, "o", "o", "\u0947", GlyphCategory.MATRA, "Matra E (े)"),
    GlyphEntry(0x4F, "O", "O", "\u0948", GlyphCategory.MATRA, "Matra AI (ै)"),
    GlyphEntry(0xDC, "\u00DC", "Udieresis", "\u094B", GlyphCategory.MATRA, "Matra OO (ो)"),
    GlyphEntry(0xDD, "\u00DD", "Yacute", "\u094C", GlyphCategory.MATRA, "Matra AU (ौ)"),
    GlyphEntry(0x5E, "^", "asciicircum", "\u0945", GlyphCategory.MATRA, "Matra Candra E (ॅ)"),

    # --- Modifiers ---
    GlyphEntry(0x4D, "M", "M", "\u0902", GlyphCategory.MODIFIER, "Anusvara (ं)"),
    GlyphEntry(0x3A, ":", "colon", "\u0903", GlyphCategory.MODIFIER, "Visarga (ः)"),
    GlyphEntry(0xD0, "\u00D0", "Eth", "\u0901", GlyphCategory.MODIFIER, "Candrabindu (ँ)"),
    GlyphEntry(0x5C, "\\", "backslash", "\u094D", GlyphCategory.MODIFIER, "Virama / Halant (्)"),
    GlyphEntry(0x2C, ",", "comma", "\u093C", GlyphCategory.MODIFIER, "Nukta (़)"),
    GlyphEntry(0x7C, "|", "bar", "\u093D", GlyphCategory.MODIFIER, "Avagraha (ऽ)"),

    # --- Conjuncts & Ligatures ---
    GlyphEntry(0x3E, ">", "greater", "\u0915\u094D\u0924", GlyphCategory.CONJUNCT, "Conjunct KT (क्त)"),
    GlyphEntry(0xCB, "\u00CB", "Edieresis", "\u0915\u094D\u0930", GlyphCategory.CONJUNCT, "Conjunct KR (क्र)"),
    GlyphEntry(0x26, "&", "ampersand", "\u091C\u094D\u091E", GlyphCategory.CONJUNCT, "Conjunct JNY (ज्ञ)"),
    GlyphEntry(0x7E, "~", "asciitilde", "\u0924\u094D\u0930", GlyphCategory.CONJUNCT, "Conjunct TR (त्र)"),
    GlyphEntry(0x2B, "+", "plus", "\u091F\u094D\u091F", GlyphCategory.CONJUNCT, "Conjunct TTTT (ट्टा)"),
    GlyphEntry(0x7B, "{", "braceleft", "\u0920\u094D\u0920", GlyphCategory.CONJUNCT, "Conjunct TTHTTH (ठ्ठ)"),
    GlyphEntry(0x5F, "_", "underscore", "\u0926\u094D\u0926", GlyphCategory.CONJUNCT, "Conjunct DD (द्द)"),
    GlyphEntry(0x77, "w", "w", "\u0926\u094D\u0927", GlyphCategory.CONJUNCT, "Conjunct D_DH (द्ध)"),
    GlyphEntry(0x56, "V", "V", "\u0926\u094D\u092F", GlyphCategory.CONJUNCT, "Conjunct DY (द्य)"),
    GlyphEntry(0x57, "W", "W", "\u0926\u094D\u0935", GlyphCategory.CONJUNCT, "Conjunct DV (द्व)"),
    GlyphEntry(0xCD, "\u00CD", "Iacute", "\u092B\u094D\u0930", GlyphCategory.CONJUNCT, "Conjunct PHR (फ्र)"),
    GlyphEntry(0x153, "\u0153", "oe", "\u0939\u094D\u0930", GlyphCategory.CONJUNCT, "Conjunct HR (ह्र)"),
    GlyphEntry(0x28, "(", "parenleft", "\u0939\u094D\u092F", GlyphCategory.CONJUNCT, "Conjunct HY (ह्य)"),
    GlyphEntry(0xC9, "\u00C9", "Eacute", "\u0930\u0941", GlyphCategory.CONJUNCT, "Combo RU (रु)"),
    GlyphEntry(0x24, "$", "dollar", "\u0930\u0942", GlyphCategory.CONJUNCT, "Combo RUU (रू)"),
    GlyphEntry(0xCC, "\u00CC", "Igrave", "\u0915\u0943", GlyphCategory.CONJUNCT, "Combo K+R (कृ)"),
    GlyphEntry(0xCE, "\u00CE", "Icircumflex", "\u092B\u0943", GlyphCategory.CONJUNCT, "Combo PH+R (फृ)"),
    GlyphEntry(0x29, ")", "parenright", "\u0939\u0943", GlyphCategory.CONJUNCT, "Combo H+R (हृ)"),
    GlyphEntry(0x2F, "/", "slash", "\u094D\u0930", GlyphCategory.CONJUNCT, "Rakar slash (्र)"),
    GlyphEntry(0x60, "`", "grave", "\u094D\u0930", GlyphCategory.CONJUNCT, "Rakar inverted-v (्र)"),

    # --- Shivaji01 Devanagari Digits ---
    GlyphEntry(0x30, "0", "zero", "\u0966", GlyphCategory.DIGIT, "Devanagari Digit 0 (०)"),
    GlyphEntry(0x31, "1", "one", "\u0967", GlyphCategory.DIGIT, "Devanagari Digit 1 (१)"),
    GlyphEntry(0x32, "2", "two", "\u0968", GlyphCategory.DIGIT, "Devanagari Digit 2 (२)"),
    GlyphEntry(0x33, "3", "three", "\u0969", GlyphCategory.DIGIT, "Devanagari Digit 3 (३)"),
    GlyphEntry(0x34, "4", "four", "\u096A", GlyphCategory.DIGIT, "Devanagari Digit 4 (४)"),
    GlyphEntry(0x35, "5", "five", "\u096B", GlyphCategory.DIGIT, "Devanagari Digit 5 (५)"),
    GlyphEntry(0x36, "6", "six", "\u096C", GlyphCategory.DIGIT, "Devanagari Digit 6 (६)"),
    GlyphEntry(0x37, "7", "seven", "\u096D", GlyphCategory.DIGIT, "Devanagari Digit 7 (७)"),
    GlyphEntry(0x38, "8", "eight", "\u096E", GlyphCategory.DIGIT, "Devanagari Digit 8 (८)"),
    GlyphEntry(0x39, "9", "nine", "\u096F", GlyphCategory.DIGIT, "Devanagari Digit 9 (९)"),

    # --- Punctuation & Special Symbols ---
    GlyphEntry(0x20, " ", "space", " ", GlyphCategory.PUNCTUATION, "Space"),
    GlyphEntry(0x2E, ".", "period", "\u0964", GlyphCategory.PUNCTUATION, "Devanagari Danda (।)"),
    GlyphEntry(0x21, "!", "exclam", "\u0950", GlyphCategory.SPECIAL, "OM (ॐ)"),
]

# Quick lookup indexes
_BY_CODE_POINT: Dict[int, GlyphEntry] = {e.code_point: e for e in SHIVAJI01_GLYPH_TABLE}
_BY_UNICODE: Dict[str, GlyphEntry] = {e.unicode_seq: e for e in SHIVAJI01_GLYPH_TABLE}


def get_glyph_catalog() -> List[GlyphEntry]:
    """Returns the full list of verified Shivaji01 glyph catalog entries."""
    return list(SHIVAJI01_GLYPH_TABLE)


def find_by_code(code_point: int) -> Optional[GlyphEntry]:
    """Finds a glyph entry by its character code point."""
    return _BY_CODE_POINT.get(code_point)


def find_by_unicode(unicode_seq: str) -> Optional[GlyphEntry]:
    """Finds a glyph entry by its exact Unicode Devanagari sequence."""
    return _BY_UNICODE.get(unicode_seq)


def get_entries_by_category(category: GlyphCategory) -> List[GlyphEntry]:
    """Returns all entries belonging to a specified category."""
    return [e for e in SHIVAJI01_GLYPH_TABLE if e.category == category]
