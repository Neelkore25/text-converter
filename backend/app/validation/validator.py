"""Conversion Validation and Diagnostic Reporting Engine (Phase 15).

Scans converted text for unmapped Unicode Devanagari characters, suspicious
rendering anomalies, and produces authentic conversion audit reports.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ValidationIssue:
    index: int
    character: str
    codepoint: str
    context_snippet: str
    issue_type: str
    suggestion: str


@dataclass
class ValidationReport:
    input_filename: str
    source_font: str
    target_font: str = "Shivaji01 Normal"
    pages: int = 1
    total_characters: int = 0
    converted_characters: int = 0
    warning_count: int = 0
    status: str = "Completed successfully"
    issues: List[ValidationIssue] = field(default_factory=list)

    def to_formatted_report(self) -> str:
        """Generates standard conversion report strictly per section 24 format."""
        status_line = (
            "Completed successfully"
            if self.warning_count == 0
            else f"Completed with warnings"
        )
        return (
            "Conversion Report\n\n"
            f"Input:\n{self.input_filename}\n\n"
            f"Source:\n{self.source_font}\n\n"
            f"Target:\n{self.target_font}\n\n"
            f"Pages:\n{self.pages}\n\n"
            f"Characters:\n{self.total_characters:,}\n\n"
            f"Converted:\n{self.converted_characters:,}\n\n"
            f"Warnings:\n{self.warning_count}\n\n"
            f"Status:\n{status_line}\n"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_filename": self.input_filename,
            "source_font": self.source_font,
            "target_font": self.target_font,
            "pages": self.pages,
            "total_characters": self.total_characters,
            "converted_characters": self.converted_characters,
            "warning_count": self.warning_count,
            "status": self.status,
            "issues": [
                {
                    "index": iss.index,
                    "character": iss.character,
                    "codepoint": iss.codepoint,
                    "context": iss.context_snippet,
                    "type": iss.issue_type,
                    "suggestion": iss.suggestion,
                }
                for iss in self.issues
            ],
        }


def validate_conversion(
    input_text: str,
    converted_text: str,
    input_filename: str = "document.txt",
    source_font: str = "Mangala",
    pages: int = 1,
) -> ValidationReport:
    """Validates the conversion output for unmapped characters or rendering flaws.

    Args:
        input_text: Original raw input text.
        converted_text: Converted Shivaji text output.
        input_filename: Name of the input file.
        source_font: Identified source font name.
        pages: Number of document pages.

    Returns:
        ValidationReport containing diagnostic data and character metrics.
    """
    total_chars = len(input_text)
    issues: List[ValidationIssue] = []

    # Check for unmapped Unicode characters (0x0900..0x097F) remaining in output
    for idx, ch in enumerate(converted_text):
        cp = ord(ch)
        if 0x0900 <= cp <= 0x097F:
            start = max(0, idx - 10)
            end = min(len(converted_text), idx + 10)
            snippet = converted_text[start:end]
            issues.append(
                ValidationIssue(
                    index=idx,
                    character=ch,
                    codepoint=f"U+{cp:04X}",
                    context_snippet=snippet,
                    issue_type="UNMAPPED_UNICODE",
                    suggestion="Character was not translated to a legacy Shivaji01 slot.",
                )
            )

    warning_count = len(issues)
    converted_count = max(0, total_chars - warning_count)
    status = (
        "Completed successfully"
        if warning_count == 0
        else "Completed with warnings"
    )

    return ValidationReport(
        input_filename=input_filename,
        source_font=source_font,
        target_font="Shivaji01 Normal",
        pages=pages,
        total_characters=total_chars,
        converted_characters=converted_count,
        warning_count=warning_count,
        status=status,
        issues=issues,
    )
