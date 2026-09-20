"""Font and Mapping Test Lab for Shivaji01 Converter.

Allows testing Unicode Devanagari text conversion, inspecting legacy output,
and rendering visual verification samples using the actual Shivaji01 Normal font.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = Path("assets/fonts/Shivaji01 Normal.ttf")


# Standard benchmark test suites per project specification
BENCHMARK_SUITES: Dict[str, List[str]] = {
    "vowels": ["अ", "आ", "इ", "ई", "उ", "ऊ", "ए", "ऐ", "ओ", "औ"],
    "consonants": [
        "क", "ख", "ग", "घ", "ङ",
        "च", "छ", "ज", "झ", "ञ",
        "ट", "ठ", "ड", "ढ", "ण",
        "त", "थ", "द", "ध", "न",
        "प", "फ", "ब", "भ", "म",
        "य", "र", "ल", "व",
        "श", "ष", "स", "ह", "ळ",
    ],
    "matra_series_ka": [
        "क", "का", "कि", "की", "कु", "कू", "के", "कै", "को", "कौ", "कं", "कः",
    ],
    "critical_short_i": [
        "कि", "की", "गि", "ति", "नि", "मि", "शि", "प्रि", "क्रि",
    ],
    "conjuncts_and_rakar": [
        "क्र", "ग्र", "प्र", "ब्र", "द्र", "त्र",
        "क्ष", "ज्ञ", "श्र", "क्त", "स्त", "स्त्र",
        "द्व", "द्य", "द्ध", "द्द",
    ],
    "marathi_sentences": [
        "महाराष्ट्र माझा देश आहे.",
        "माझे नाव नील आहे.",
        "मला संगणक अभियांत्रिकी शिकायला आवडते.",
        "महाराष्ट्र भारतातील एक राज्य आहे.",
    ],
}


@dataclass
class LabCaseResult:
    input_unicode: str
    output_shivaji: str
    char_codes: List[int]
    unmapped_chars: List[str]
    is_success: bool
    notes: str = ""


@dataclass
class LabReport:
    suite_name: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    results: List[LabCaseResult] = field(default_factory=list)

    @property
    def accuracy(self) -> float:
        return (self.passed_cases / self.total_cases * 100.0) if self.total_cases > 0 else 0.0


def load_shivaji_font(size: int = 28) -> ImageFont.FreeTypeFont:
    """Loads the Shivaji01 Normal font at the specified point size."""
    if not FONT_PATH.exists():
        raise FileNotFoundError(f"Shivaji01 font not found at {FONT_PATH}")
    return ImageFont.truetype(str(FONT_PATH), size)


def render_shivaji_text(
    shivaji_text: str,
    font_size: int = 32,
    padding: int = 20,
    bg_color: tuple = (255, 255, 255),
    text_color: tuple = (0, 0, 0),
) -> Image.Image:
    """Renders converted Shivaji legacy text onto an image using Shivaji01 font."""
    font = load_shivaji_font(font_size)

    # Temporary canvas to measure text bounding box
    tmp_img = Image.new("RGB", (1, 1), bg_color)
    tmp_draw = ImageDraw.Draw(tmp_img)
    bbox = tmp_draw.textbbox((0, 0), shivaji_text, font=font)
    text_w = max(bbox[2] - bbox[0], 10)
    text_h = max(bbox[3] - bbox[1], 10)

    img_w = text_w + 2 * padding
    img_h = text_h + 2 * padding

    img = Image.new("RGB", (img_w, img_h), bg_color)
    draw = ImageDraw.Draw(img)
    draw.text((padding - bbox[0], padding - bbox[1]), shivaji_text, fill=text_color, font=font)
    return img


def run_suite(
    suite_name: str,
    converter_func: Callable[[str], str],
    expected_mappings: Optional[Dict[str, str]] = None,
) -> LabReport:
    """Runs a benchmark suite through a conversion function and returns a detailed report."""
    cases = BENCHMARK_SUITES.get(suite_name, [])
    report = LabReport(suite_name=suite_name, total_cases=len(cases), passed_cases=0, failed_cases=0)

    for word in cases:
        converted = converter_func(word)
        codes = [ord(c) for c in converted]

        # Check for unmapped Unicode characters (codepoints still in U+0900..U+097F)
        unmapped = [c for c in converted if 0x0900 <= ord(c) <= 0x097F]
        is_success = len(unmapped) == 0

        # If an expected mapping dictionary was provided, verify exact equality
        if expected_mappings and word in expected_mappings:
            expected = expected_mappings[word]
            if converted != expected:
                is_success = False

        if is_success:
            report.passed_cases += 1
        else:
            report.failed_cases += 1

        report.results.append(
            LabCaseResult(
                input_unicode=word,
                output_shivaji=converted,
                char_codes=codes,
                unmapped_chars=unmapped,
                is_success=is_success,
            )
        )

    return report
