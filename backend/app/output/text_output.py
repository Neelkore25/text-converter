"""TXT document output generator (Phase 12).

Writes converted Shivaji text to plain TXT files with full encoding support,
preserving paragraphs, line breaks, and whitespace structure.
"""
from __future__ import annotations

from pathlib import Path


def write_converted_txt(
    converted_text: str,
    output_path: str | Path,
    encoding: str = "utf-8",
) -> Path:
    """Writes converted Shivaji-compatible text to a .txt file.

    Args:
        converted_text: Converted legacy Shivaji string.
        output_path: Destination file path.
        encoding: Output file encoding (defaults to utf-8).

    Returns:
        Resolved Path to the created output file.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding=encoding, newline="") as f:
        f.write(converted_text)
    return path.resolve()
