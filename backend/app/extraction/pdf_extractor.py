"""PDF document extraction module (Phase 13).

Extracts text from multi-page PDFs, detects font hints, handles mixed
Marathi/English text, and detects scanned/image-only PDFs.
"""
from __future__ import annotations

from pathlib import Path
from pypdf import PdfReader
from backend.app.extraction import DocumentContent


def extract_text_from_pdf(file_path: str | Path) -> DocumentContent:
    """Extracts text from a PDF file using pypdf.

    Detects whether the PDF contains text or is a scanned image-only PDF.

    Args:
        file_path: Path to the .pdf file.

    Returns:
        DocumentContent containing extracted text, page count, and scanned status.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        ValueError: If file is corrupted or unreadable.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"PDF file not found: {path}")

    try:
        reader = PdfReader(str(path))
    except Exception as e:
        raise ValueError(f"Failed to read PDF file '{path}': {e}") from e

    total_pages = len(reader.pages)
    extracted_pages: list[str] = []
    has_images = False
    detected_font_hints: set[str] = set()

    for idx, page in enumerate(reader.pages):
        try:
            page_text = page.extract_text() or ""
            extracted_pages.append(page_text)
        except Exception:
            extracted_pages.append("")

        # Check for images
        if page.images and len(page.images) > 0:
            has_images = True

        # Inspect fonts in page resources if available
        try:
            if "/Resources" in page and "/Font" in page["/Resources"]:
                fonts_dict = page["/Resources"]["/Font"]
                for f_key in fonts_dict:
                    font_obj = fonts_dict[f_key]
                    if "/BaseFont" in font_obj:
                        base_font_name = str(font_obj["/BaseFont"]).replace("/", "")
                        detected_font_hints.add(base_font_name)
        except Exception:
            pass

    full_text = "\n\n".join(extracted_pages).strip()
    total_chars = len(full_text)

    # Scanned/image-only detection:
    # If the document has pages, but extracted text is empty or virtually empty (< 10 chars),
    # while images are present or pages exist.
    is_scanned = (total_pages > 0 and total_chars < 10)

    font_hint = ", ".join(sorted(detected_font_hints)) if detected_font_hints else None

    return DocumentContent(
        text=full_text,
        format="pdf",
        file_path=str(path.resolve()),
        font_hint=font_hint,
        page_count=total_pages,
        character_count=total_chars,
        is_scanned_image_only=is_scanned,
        metadata={
            "page_count": total_pages,
            "has_images": has_images,
            "font_hints": list(detected_font_hints),
            "notice": (
                "This PDF appears to contain scanned/image-only content. "
                "OCR is required for text extraction."
                if is_scanned
                else ""
            ),
        },
    )
