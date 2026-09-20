"""FastAPI Backend Server for Shivaji Converter (Phase 18 & 19).

Exposes REST APIs for file conversion, real-time test lab conversion,
history audit logging, font inventory, and document downloads.
"""
from __future__ import annotations

import os
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.app.conversion.unicode_to_shivaji import convert_unicode_to_shivaji
from backend.app.extraction.docx_extractor import extract_text_from_docx
from backend.app.extraction.pdf_extractor import extract_text_from_pdf
from backend.app.extraction.text_extractor import extract_text_from_txt
from backend.app.fonts.source_fonts import (
    SourceFontStatus,
    SourceFontType,
    detect_source_font,
    get_all_source_fonts,
    get_source_font_by_id,
)
from backend.app.history import HistoryManager, HistoryRecord
from backend.app.output.docx_output import write_converted_docx
from backend.app.output.pdf_output import write_converted_pdf
from backend.app.output.text_output import write_converted_txt
from backend.app.validation.validator import validate_conversion

app = FastAPI(
    title="Shivaji01 Document Converter API",
    version="1.0.0",
    description="Marathi / Devanagari Multi-Font to Shivaji01 Conversion API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("scratch/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR = Path("assets")
FRONTEND_DIR = Path("frontend")

history_mgr = HistoryManager()


# Mount static assets for fonts
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")


class TextConversionRequest(BaseModel):
    text: str
    source_font: Optional[str] = "auto"


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend index.html not found.")
    return HTMLResponse(content=index_file.read_text(encoding="utf-8"))


@app.get("/api/fonts")
async def get_fonts():
    """Returns target font info and all 10 source fonts with their operational status."""
    fonts = get_all_source_fonts()
    return {
        "target_font": {
            "name": "Shivaji01 Normal",
            "file": "Shivaji01 Normal.ttf",
            "status": "✓ Verified & Active",
        },
        "source_fonts": [
            {
                "id": f.id,
                "display_name": f.display_name,
                "font_type": f.font_type.value,
                "status": f.status.value,
                "description": f.description,
            }
            for f in fonts
        ],
    }


@app.get("/api/stats")
async def get_stats():
    """Returns real dashboard statistics."""
    stats = history_mgr.get_statistics()
    stats["supported_fonts_count"] = len(get_all_source_fonts())
    return stats


@app.get("/api/history")
async def get_history(limit: int = 50):
    """Returns local conversion history records with download links."""
    records = history_mgr.get_all_records(limit=limit)
    res = []
    for r in records:
        out_name = Path(r.output_path).name if r.output_path else f"converted_{Path(r.filename).stem}.{r.output_format.lower()}"
        dl_url = f"/api/download/{out_name}" if r.output_path else "#"
        res.append({
            "id": r.id,
            "filename": r.filename,
            "timestamp": r.timestamp,
            "source_font": r.source_font,
            "target_font": r.target_font,
            "characters_processed": r.characters_processed,
            "warnings_count": r.warnings_count,
            "status": r.status,
            "output_format": r.output_format,
            "output_path": r.output_path,
            "output_filename": out_name,
            "download_url": dl_url,
            "report_text": r.report_text,
        })
    return res


@app.post("/api/convert/text")
async def convert_text(req: TextConversionRequest):
    """Converts a text string in real-time for the Test Lab."""
    t0 = time.perf_counter()
    detection = detect_source_font(
        req.text,
        font_name_hint=None if req.source_font == "auto" else req.source_font,
    )

    if not detection.is_supported and detection.detected_font and detection.detected_font.font_type == SourceFontType.LEGACY_ENCODED:
        return {
            "is_supported": False,
            "message": detection.message,
            "detected_font": detection.detected_font.display_name,
            "converted_text": "",
        }

    res = convert_unicode_to_shivaji(req.text)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    report = validate_conversion(
        input_text=req.text,
        converted_text=res.converted_text,
        input_filename="live_test.txt",
        source_font=detection.detected_font.display_name if detection.detected_font else "Mangal",
    )

    return {
        "is_supported": True,
        "converted_text": res.converted_text,
        "detected_font": detection.detected_font.display_name if detection.detected_font else "Mangal",
        "total_characters": res.total_characters,
        "converted_characters": res.converted_characters,
        "warning_count": res.warning_count,
        "unmapped_characters": res.unmapped_characters,
        "elapsed_ms": round(elapsed_ms, 2),
        "report": report.to_formatted_report(),
    }


@app.post("/api/convert/file")
async def convert_file(
    file: UploadFile = File(...),
    source_font: str = Form("auto"),
    output_format: str = Form("docx"),
    preserve_paragraphs: bool = Form(True),
    preserve_line_breaks: bool = Form(True),
):
    """Processes an uploaded TXT, PDF, or DOCX document and outputs converted document."""
    t0 = time.perf_counter()
    filename = Path(file.filename or "uploaded_doc").name
    ext = Path(filename).suffix.lower()

    if ext not in (".txt", ".pdf", ".docx"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported document format '{ext}'. Allowed formats: .txt, .docx, .pdf",
        )

    # Save uploaded file to scratch
    saved_path = UPLOAD_DIR / f"{int(time.time())}_{filename}"
    with open(saved_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        # Step 1: Extract text
        if ext == ".txt":
            doc = extract_text_from_txt(saved_path)
        elif ext == ".pdf":
            doc = extract_text_from_pdf(saved_path)
            if doc.is_scanned_image_only:
                raise HTTPException(
                    status_code=422,
                    detail=doc.metadata["notice"],
                )
        elif ext == ".docx":
            doc = extract_text_from_docx(saved_path)

        # Step 2: Source Font Detection
        font_hint = doc.font_hint if source_font == "auto" else source_font
        detection = detect_source_font(doc.text, font_name_hint=font_hint)

        if not detection.is_supported and detection.detected_font and detection.detected_font.font_type == SourceFontType.LEGACY_ENCODED:
            raise HTTPException(
                status_code=422,
                detail=detection.message,
            )

        detected_name = detection.detected_font.display_name if detection.detected_font else "Mangal"

        # Step 3: Convert text
        res = convert_unicode_to_shivaji(doc.text)

        # Step 4: Generate Output Document
        stem = Path(filename).stem
        out_ext = output_format.lower()
        if out_ext not in ("txt", "docx", "pdf"):
            out_ext = "docx"

        out_filename = f"converted_{stem}.{out_ext}"
        target_out_path = OUTPUT_DIR / out_filename

        if out_ext == "txt":
            write_converted_txt(res.converted_text, target_out_path)
        elif out_ext == "docx":
            write_converted_docx(res.converted_text, target_out_path)
        elif out_ext == "pdf":
            write_converted_pdf(res.converted_text, target_out_path)

        # Step 5: Validate and generate Report
        val_report = validate_conversion(
            input_text=doc.text,
            converted_text=res.converted_text,
            input_filename=filename,
            source_font=detected_name,
            pages=doc.page_count,
        )

        elapsed_ms = (time.perf_counter() - t0) * 1000

        # Step 6: Record in History
        rec = HistoryRecord(
            id=None,
            filename=filename,
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
            source_font=detected_name,
            target_font="Shivaji01 Normal",
            characters_processed=res.total_characters,
            warnings_count=res.warning_count,
            status=val_report.status,
            output_format=out_ext.upper(),
            output_path=str(target_out_path),
            report_text=val_report.to_formatted_report(),
        )
        rec_id = history_mgr.add_record(rec)

        return {
            "record_id": rec_id,
            "filename": filename,
            "output_filename": out_filename,
            "download_url": f"/api/download/{out_filename}",
            "source_font": detected_name,
            "target_font": "Shivaji01 Normal",
            "pages": doc.page_count,
            "total_characters": res.total_characters,
            "converted_characters": res.converted_characters,
            "warning_count": res.warning_count,
            "status": val_report.status,
            "elapsed_ms": round(elapsed_ms, 2),
            "report": val_report.to_formatted_report(),
            "preview_source": doc.text[:500],
            "preview_converted": res.converted_text[:500],
        }

    finally:
        # Clean up temporary uploaded file
        if saved_path.exists():
            try:
                saved_path.unlink()
            except Exception:
                pass


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Safely serves converted output documents."""
    # Prevent path traversal
    safe_name = Path(filename).name
    file_path = OUTPUT_DIR / safe_name
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Converted file not found.")

    media_type = "application/octet-stream"
    if safe_name.endswith(".docx"):
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif safe_name.endswith(".pdf"):
        media_type = "application/pdf"
    elif safe_name.endswith(".txt"):
        media_type = "text/plain; charset=utf-8"

    return FileResponse(
        str(file_path),
        media_type=media_type,
        filename=safe_name,
    )
