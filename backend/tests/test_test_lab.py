"""Tests for Font Test Lab (Phase 3)."""
import pytest
from PIL import Image

from backend.app.conversion.test_lab import (
    BENCHMARK_SUITES,
    LabReport,
    load_shivaji_font,
    render_shivaji_text,
    run_suite,
)


def test_benchmark_suites_defined():
    """Verify that all required benchmark suites exist and are non-empty."""
    required_suites = [
        "vowels",
        "consonants",
        "matra_series_ka",
        "critical_short_i",
        "conjuncts_and_rakar",
        "marathi_sentences",
    ]
    for suite in required_suites:
        assert suite in BENCHMARK_SUITES, f"Missing suite: {suite}"
        assert len(BENCHMARK_SUITES[suite]) > 0, f"Suite {suite} is empty"


def test_load_shivaji_font():
    """Verify loading Shivaji01 Normal font at various sizes."""
    font_24 = load_shivaji_font(24)
    font_48 = load_shivaji_font(48)
    assert font_24 is not None
    assert font_48 is not None
    assert font_24.size == 24
    assert font_48.size == 48


def test_render_shivaji_text_image():
    """Verify that rendering legacy text produces a valid PIL image."""
    # Test rendering Shivaji characters for "k" (क)
    img = render_shivaji_text("k", font_size=28)
    assert isinstance(img, Image.Image)
    assert img.width > 20
    assert img.height > 20
    assert img.mode == "RGB"


def test_run_suite_detects_unmapped_unicode():
    """Verify run_suite detects unmapped Unicode characters."""
    # Dummy converter that leaves Unicode untouched
    def dummy_identity_converter(text: str) -> str:
        return text

    report = run_suite("vowels", dummy_identity_converter)
    assert isinstance(report, LabReport)
    assert report.total_cases == len(BENCHMARK_SUITES["vowels"])
    # Since dummy does not map to Shivaji slots, all should fail unmapped check
    assert report.failed_cases == report.total_cases
    assert report.passed_cases == 0
    assert report.accuracy == 0.0


def test_run_suite_success_with_mapped_text():
    """Verify run_suite counts success when all characters are mapped to ASCII/legacy range."""
    # Mock converter that outputs dummy ASCII
    def mock_ascii_converter(text: str) -> str:
        return "abc"

    report = run_suite("vowels", mock_ascii_converter)
    assert report.passed_cases == report.total_cases
    assert report.failed_cases == 0
    assert report.accuracy == 100.0
