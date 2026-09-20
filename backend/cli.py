"""Command Line Interface for Shivaji01 Converter (Phases 18 & 22).

Usage:
    python -m backend.cli convert <file> [--output <path>] [--format <txt|docx|pdf>] [--source <font>]
    python -m backend.cli text "<marathi_text>"
    python -m backend.cli benchmark
    python -m backend.cli serve [--port 8000]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from backend.app.conversion.test_lab import BENCHMARK_SUITES, run_suite
from backend.app.conversion.unicode_to_shivaji import convert_unicode_to_shivaji
from backend.app.extraction.docx_extractor import extract_text_from_docx
from backend.app.extraction.pdf_extractor import extract_text_from_pdf
from backend.app.extraction.text_extractor import extract_text_from_txt
from backend.app.fonts.source_fonts import detect_source_font
from backend.app.output.docx_output import write_converted_docx
from backend.app.output.pdf_output import write_converted_pdf
from backend.app.output.text_output import write_converted_txt
from backend.app.validation.validator import validate_conversion

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def handle_convert(args):
    in_path = Path(args.file)
    if not in_path.exists():
        print(f"Error: Input file not found: {in_path}", file=sys.stderr)
        sys.exit(1)

    ext = in_path.suffix.lower()
    print(f"[*] Extracting document: {in_path.name} ({ext})")

    if ext == ".txt":
        doc = extract_text_from_txt(in_path)
    elif ext == ".pdf":
        doc = extract_text_from_pdf(in_path)
        if doc.is_scanned_image_only:
            print(f"[!] Error: {doc.metadata['notice']}", file=sys.stderr)
            sys.exit(2)
    elif ext == ".docx":
        doc = extract_text_from_docx(in_path)
    else:
        print(f"Error: Unsupported format {ext}", file=sys.stderr)
        sys.exit(1)

    source_hint = doc.font_hint if args.source == "auto" else args.source
    detection = detect_source_font(doc.text, font_name_hint=source_hint)
    detected_name = detection.detected_font.display_name if detection.detected_font else "Mangal"
    print(f"[*] Detected Source Font: {detected_name} (Confidence: {int(detection.confidence * 100)}%)")

    print("[*] Converting Devanagari clusters to Shivaji01 format...")
    res = convert_unicode_to_shivaji(doc.text)

    out_format = args.format.lower() if args.format else ext[1:]
    out_path = Path(args.output) if args.output else Path("output") / f"converted_{in_path.stem}.{out_format}"

    print(f"[*] Writing output document: {out_path} ({out_format.upper()})")
    if out_format == "txt":
        write_converted_txt(res.converted_text, out_path)
    elif out_format == "docx":
        write_converted_docx(res.converted_text, out_path)
    elif out_format == "pdf":
        write_converted_pdf(res.converted_text, out_path)

    val_report = validate_conversion(
        input_text=doc.text,
        converted_text=res.converted_text,
        input_filename=in_path.name,
        source_font=detected_name,
        pages=doc.page_count,
    )

    print("\n" + val_report.to_formatted_report())


def handle_text(args):
    res = convert_unicode_to_shivaji(args.text)
    print("--- Converted Shivaji01 Text ---")
    print(res.converted_text)
    print("--------------------------------")
    print(f"Total: {res.total_characters} | Converted: {res.converted_characters} | Warnings: {res.warning_count}")


def handle_benchmark(args):
    print("==================================================")
    print("  Shivaji01 Converter Test Lab Benchmark Suite    ")
    print("==================================================")
    for suite_name in BENCHMARK_SUITES:
        report = run_suite(suite_name, lambda s: convert_unicode_to_shivaji(s).converted_text)
        print(f"Suite: {suite_name:<24} | Total: {report.total_cases:2d} | Passed: {report.passed_cases:2d} | Accuracy: {report.accuracy:6.1f}%")
    print("==================================================")


def handle_serve(args):
    import uvicorn
    from backend.app.api.server import app

    print(f"[*] Starting Shivaji Converter Server at http://localhost:{args.port}")
    uvicorn.run(app, host="127.0.0.1", port=args.port)


def main():
    parser = argparse.ArgumentParser(description="Marathi / Devanagari Multi-Font to Shivaji01 Converter")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Convert file
    p_conv = subparsers.add_parser("convert", help="Convert document file (TXT, DOCX, PDF)")
    p_conv.add_argument("file", help="Path to input document")
    p_conv.add_argument("-o", "--output", help="Output file path")
    p_conv.add_argument("-f", "--format", choices=["txt", "docx", "pdf"], default="docx", help="Output format")
    p_conv.add_argument("-s", "--source", default="auto", help="Source font name or auto")
    p_conv.set_defaults(func=handle_convert)

    # Convert text
    p_text = subparsers.add_parser("text", help="Convert text string directly")
    p_text.add_argument("text", help="Input Unicode Marathi string")
    p_text.set_defaults(func=handle_text)

    # Benchmark
    p_bench = subparsers.add_parser("benchmark", help="Run conversion benchmark test suites")
    p_bench.set_defaults(func=handle_benchmark)

    # Serve UI
    p_serve = subparsers.add_parser("serve", help="Launch web UI and REST API server")
    p_serve.add_argument("-p", "--port", type=int, default=8000, help="Port to bind (default: 8000)")
    p_serve.set_defaults(func=handle_serve)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
