"""Tests for Conversion Validation and Diagnostic Reporting (Phase 15)."""
from backend.app.validation.validator import validate_conversion


def test_validation_successful_conversion():
    """Verify clean validation when no unmapped characters exist."""
    input_marathi = "महाराष्ट्र माझा देश आहे."
    converted_shivaji = "maharaYT` maaJaa doSa Aaho."

    report = validate_conversion(
        input_text=input_marathi,
        converted_text=converted_shivaji,
        input_filename="sample.txt",
        source_font="Mangal",
        pages=1,
    )

    assert report.warning_count == 0
    assert report.status == "Completed successfully"
    assert report.converted_characters == len(input_marathi)
    assert report.total_characters == len(input_marathi)
    assert len(report.issues) == 0


def test_validation_detects_unmapped_characters():
    """Verify unmapped characters are flagged with snippet and warning count."""
    input_text = "क ख ग अनमैप्ड"
    # Suppose converted text still has 2 Unicode characters left
    partially_converted = "k K ga \u0905\u0928"

    report = validate_conversion(
        input_text=input_text,
        converted_text=partially_converted,
        input_filename="test.docx",
        source_font="Nirmala UI",
        pages=2,
    )

    assert report.warning_count == 2
    assert report.status == "Completed with warnings"
    assert len(report.issues) == 2
    assert report.issues[0].character == "\u0905"
    assert report.issues[0].codepoint == "U+0905"
    assert report.issues[1].character == "\u0928"
    assert report.issues[1].codepoint == "U+0928"


def test_formatted_report_strictly_matches_format():
    """Verify text report matches section 24 format requirements."""
    report = validate_conversion(
        input_text="A" * 12458,
        converted_text=("B" * 12420) + ("\u0905" * 38),
        input_filename="example.pdf",
        source_font="Mangala",
        pages=5,
    )

    formatted = report.to_formatted_report()
    assert "Conversion Report" in formatted
    assert "Input:\nexample.pdf" in formatted
    assert "Source:\nMangala" in formatted
    assert "Target:\nShivaji01 Normal" in formatted
    assert "Pages:\n5" in formatted
    assert "Characters:\n12,458" in formatted
    assert "Converted:\n12,420" in formatted
    assert "Warnings:\n38" in formatted
    assert "Status:\nCompleted with warnings" in formatted
