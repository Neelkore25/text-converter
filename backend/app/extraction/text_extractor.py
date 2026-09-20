"""TXT document extraction module (Phase 12).

Extracts text from TXT files with full support for UTF-8 (with/without BOM),
preserving exact line breaks, paragraph structure, and blank lines.
"""
from __future__ import annotations

from pathlib import Path
from backend.app.extraction import DocumentContent


def extract_text_from_txt(file_path: str | Path) -> DocumentContent:
    """Extracts raw text from a text file, preserving paragraphs and formatting.

    Args:
        file_path: Path to the .txt file.

    Returns:
        DocumentContent containing the file text, character count, and metadata.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If file is empty or decoding fails.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Text file not found: {path}")

    raw_bytes = path.read_bytes()
    if not raw_bytes:
        return DocumentContent(
            text="",
            format="txt",
            file_path=str(path.resolve()),
            page_count=1,
            character_count=0,
            metadata={"encoding": "empty"},
        )

    # Attempt decodings: UTF-8 with BOM, UTF-8, then UTF-16
    encodings = ["utf-8-sig", "utf-8", "utf-16", "cp1252"]
    decoded_text: str | None = None
    used_encoding: str = "utf-8"

    for enc in encodings:
        try:
            decoded_text = raw_bytes.decode(enc)
            used_encoding = enc
            break
        except UnicodeDecodeError:
            continue

    if decoded_text is None:
        raise ValueError(f"Failed to decode text file '{path}' using supported encodings.")

    # Count paragraphs and lines
    lines = decoded_text.splitlines()
    blank_lines = sum(1 for line in lines if not line.strip())

    return DocumentContent(
        text=decoded_text,
        format="txt",
        file_path=str(path.resolve()),
        page_count=1,
        character_count=len(decoded_text),
        metadata={
            "encoding": used_encoding,
            "total_lines": len(lines),
            "blank_lines": blank_lines,
        },
    )
