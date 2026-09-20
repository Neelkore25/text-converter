# 🚀 Marathi / Devanagari Multi-Font → Shivaji01 Converter

A production-quality Marathi/Devanagari document conversion system engineered from scratch in Python. It accurately converts Unicode Devanagari documents (TXT, DOCX, and text-based PDFs) into **legacy Shivaji01-compatible text**, rendered with the supplied **`Shivaji01 Normal.ttf`** font.

Built with a linguistic Devanagari cluster parser, prefix short-i (`ि`) visual reordering engine, conjunct and reph handler, source font detector, local document processing, and a modern 2026 SaaS dark-theme dashboard.

---

## 📑 Table of Contents

- [Project Overview](#project-overview)
- [Architecture Pipeline](#architecture-pipeline)
- [Supported Source Fonts](#supported-source-fonts)
- [Target Font Setup](#target-font-setup)
- [Conversion Pipeline Deep-Dive](#conversion-pipeline-deep-dive)
  - [Prefix Short-I (`ि`) Handling](#prefix-short-i--handling)
  - [Conjunct Ligatures](#conjunct-ligatures)
  - [Reph (`र्`) and Rakar (`्र`)](#reph--and-rakar-)
  - [Devanagari Digits](#devanagari-digits)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
  - [1. Modern Web Dashboard](#1-modern-web-dashboard)
  - [2. Command-Line Interface (CLI)](#2-command-line-interface-cli)
  - [3. Python Programmatic API](#3-python-programmatic-api)
- [Testing & Quality Assurance](#testing--quality-assurance)
- [Security & Local Privacy Guarantee](#security--local-privacy-guarantee)
- [Known Limitations](#known-limitations)
- [Troubleshooting](#troubleshooting)

---

## 🌟 Project Overview

Legacy Devanagari fonts such as **Shivaji01** do not adhere to modern Unicode codepoints (`U+0900`–`U+097F`). Instead, they map Marathi/Devanagari glyphs, half-forms, matras, and ligatures into ASCII (`0x20`–`0x7E`) and Windows-1252 ANSI slots (`0xA0`–`0xFF`).

Simply changing the font face name in a document processor fails completely, producing unreadable Latin characters. Furthermore, naive character-by-character replacements (`text.replace`) fail catastrophically on combinations like **कि, की, क्र, र्क, र्कि, क्ष, त्र, ज्ञ, श्र, क्त, स्त, स्त्र**.

This application solves the challenge by:
1. **Normalizing Unicode text** (NFC canonicalization, repairing malformed composite vowels, fixing misordered nuktas).
2. **Decomposing text into linguistic orthographic clusters** (Aksharas: Base consonant, Half consonants, Matra, Reph, Modifiers).
3. **Reordering the glyph sequences** to conform to the legacy visual layout of Shivaji01.
4. **Exporting to editable DOCX** (with `Shivaji01 Normal` run styling), **embedded PDF**, or **plain TXT**.

---

## 🏛️ Architecture Pipeline

```text
                    ┌───────────────────────────────┐
                    │ Input Document (TXT/PDF/DOCX) │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │ Format Detection & Extraction │
                    │ (Text, Multipage, Font Hints) │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │      Source Font Detector     │
                    │   (Unicode vs Legacy Source)  │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │  Unicode Devanagari Normalizer│
                    │ (Composite Vowels, Nukta Fix) │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │    Devanagari Cluster Parser  │
                    │  (Akshara Tokenizer: Consonants,│
                    │   Halants, Matras, Modifiers) │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │    Shivaji01 Mapping Engine   │
                    │ - Prefix Short-I (ि) Reorder  │
                    │ - Half-Form & Conjunct Solver │
                    │ - Reph (र्) & Rakar (्र) Formatter │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │  Validation & Diagnostic Audit│
                    │  (Unmapped Detection, Reports)│
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │     Output Document Writer    │
                    │  (DOCX Styled / PDF / TXT)    │
                    └───────────────────────────────┘
```

---

## 🔤 Supported Source Fonts

The converter distinguishes between Unicode and Legacy source formats:

| # | Font Name | Encoding Type | Operational Status | Pipeline Used |
|---|-----------|---------------|--------------------|---------------|
| 1 | **Mangal** | Unicode | `✓ Unicode supported` | Unicode Cluster Parser $\rightarrow$ Shivaji01 |
| 2 | **Mangala** | Unicode | `✓ Unicode supported` | Unicode Cluster Parser $\rightarrow$ Shivaji01 |
| 3 | **Nirmala UI** | Unicode | `✓ Unicode supported` | Unicode Cluster Parser $\rightarrow$ Shivaji01 |
| 4 | **Kokila** | Unicode | `✓ Unicode supported` | Unicode Cluster Parser $\rightarrow$ Shivaji01 |
| 5 | **Utsaah** | Unicode | `✓ Unicode supported` | Unicode Cluster Parser $\rightarrow$ Shivaji01 |
| 6 | **Devanagari Sangam MN** | Unicode | `✓ Unicode supported` | Unicode Cluster Parser $\rightarrow$ Shivaji01 |
| 7 | **Cochin** | Unicode | `✓ Unicode supported` | Unicode Cluster Parser $\rightarrow$ Shivaji01 |
| 8 | **Kruti Dev** | Legacy Reming. | `⚠ Requires Font` | Source font in `assets/fonts/source/` |
| 9 | **DevLys** | Legacy Reming. | `⚠ Requires Font` | Source font in `assets/fonts/source/` |
| 10| **Kantal** | Legacy Marathi | `⚠ Requires Font` | Source font in `assets/fonts/source/` |

> **Integrity Rule**: As required, legacy source font conversion (Kruti Dev, DevLys, Kantal) is only enabled when genuine source font files or verified mapping data are placed in `assets/fonts/source/`. The system never fabricates unverified legacy conversions.

---

## 📦 Target Font Setup

The primary target font is **`Shivaji01 Normal.ttf`**, located in:
```text
assets/fonts/Shivaji01 Normal.ttf
```
The application loads and embeds this font directly from the project directory rather than relying on system-wide font installations.

---

## ⚙️ Conversion Pipeline Deep-Dive

### Prefix Short-I (`ि`) Handling
In Unicode Devanagari, the short-i matra follows the consonant logically (`क + ि` $\rightarrow$ `\u0915\u093F`). In Shivaji01, however, the short-i glyph (`i` / `0x69`) is typed **before** the consonant cluster.
- `कि` $\rightarrow$ `ik`
- `गि` $\rightarrow$ `iga`
- `नि` $\rightarrow$ `ina`
- `मि` $\rightarrow$ `ima`
- `शि` $\rightarrow$ `iSa`
- `प्रि` $\rightarrow$ `ip/`
- `क्रि` $\rightarrow$ `i\u00CB`
- `र्कि` $\rightarrow$ `ik-` (Prefix short-i precedes the consonant, while reph suffix follows it)

### Conjunct Ligatures
Shivaji01 uses preformed ligatures for key conjuncts:
- **क्त** $\rightarrow$ `>`
- **क्र** $\rightarrow$ `\u00CB`
- **ज्ञ** $\rightarrow$ `&`
- **त्र** $\rightarrow$ `~`
- **क्ष** $\rightarrow$ `xa`
- **श्र** $\rightarrow$ `Ea`
- **द्य** $\rightarrow$ `V`, **द्व** $\rightarrow$ `W`, **द्ध** $\rightarrow$ `w`, **द्द** $\rightarrow$ `_`
- **स्त** $\rightarrow$ `st`, **स्त्र** $\rightarrow$ `s~`, **स्त्री** $\rightarrow$ `s~I`

### Reph (`र्`) and Rakar (`्र`)
- **Reph** (`र् + consonant`): Placed as suffix `-` on the syllable (e.g. `कर्म` $\rightarrow$ `kma-`, `धर्म` $\rightarrow$ `Qama-`, `सूर्य` $\rightarrow$ `saUya-`).
- **Rakar** (`consonant + ्र`):
  - Diagonal slash `/` for vertical stem consonants (e.g. `प्र` $\rightarrow$ `p/`, `ग्र` $\rightarrow$ `ga/`, `द्र` $\rightarrow$ `d/`).
  - Inverted-V `` ` `` for round consonants (e.g. `ट्र` $\rightarrow$ `T``, `ड्र` $\rightarrow$ `D``, `महाराष्ट्र` $\rightarrow$ `mharaYT``).

### Devanagari Digits
Devanagari numerals `०, १, २, ३, ४, ५, ६, ७, ८, ९` are converted into character codes `0x30`–`0x39` (`0`–`9`), which in the Shivaji01 font render directly as Marathi numerals.

---

## 💻 Installation & Setup

### Prerequisites
- Python 3.10+ (tested on Python 3.12)
- Git

### Installation
```bash
# Clone the repository
git clone https://github.com/Neelkore25/text-converter.git
cd text-converter

# Install dependencies
pip install -r requirements.txt
```

---

## 🖥️ Usage

### 1. Modern Web Dashboard
Launch the local web application:
```bash
python -m backend.cli serve --port 8000
```
Open your browser to:
```text
http://localhost:8000
```

Features included in the web interface:
- **Main Dashboard**: Real Bento-grid statistics (Files converted, clean conversions, reviews flagged).
- **Document Converter**: Drag-and-drop workspace for PDF, DOCX, TXT with live progress bar and split-pane side-by-side preview.
- **Interactive Font Test Lab**: Live Devanagari input box with real-time conversion and font-rendered output.
- **Font Inventory**: Status overview of target font and all 10 source fonts.
- **History Viewer**: Local SQLite history table with direct download buttons.

### 2. Command-Line Interface (CLI)

#### Convert Documents
```bash
# Convert TXT to Shivaji DOCX
python -m backend.cli convert samples/sample_mangal.txt -f docx -o output/mangal.docx

# Convert DOCX to Shivaji TXT
python -m backend.cli convert samples/sample_kokila.docx -f txt -o output/kokila.txt

# Convert to PDF with embedded Shivaji01 font
python -m backend.cli convert samples/sample_mangal.txt -f pdf -o output/mangal.pdf
```

#### Test Live Text String
```bash
python -m backend.cli text "महाराष्ट्र माझा देश आहे."
```

#### Run Benchmark Test Suites
```bash
python -m backend.cli benchmark
```

### 3. Python Programmatic API
```python
from backend.app.conversion.unicode_to_shivaji import convert_unicode_to_shivaji

result = convert_unicode_to_shivaji("महाराष्ट्र माझा देश आहे.")
print(result.converted_text)
# Output: maharaYT` maaJaa doSa Aaho.
print(f"Warnings: {result.warning_count}")
```

---

## 🧪 Testing & Quality Assurance

All features are covered by automated tests using `pytest`:

```bash
python -m pytest -v
```

### Current Test Suite Results (68 Tests Passing):
```text
backend/tests/test_font_inspector.py         5 passed
backend/tests/test_glyph_catalog.py          6 passed
backend/tests/test_devanagari_normalizer.py   7 passed
backend/tests/test_cluster_parser.py         7 passed
backend/tests/test_unicode_to_shivaji.py     10 passed
backend/tests/test_test_lab.py               5 passed
backend/tests/test_source_fonts.py           6 passed
backend/tests/test_text_document.py          5 passed
backend/tests/test_pdf_and_docx.py           5 passed
backend/tests/test_validator.py              3 passed
backend/tests/test_real_documents.py         3 passed
backend/tests/test_api_server.py             6 passed
======================== 68 passed in 2.31s ========================
```

---

## 🔒 Security & Local Privacy Guarantee

- **Zero Cloud Uploads**: All file extractions, conversions, and font rendering take place strictly on the user's local machine.
- **Path Traversal Sanitization**: All file download and upload routes use strict basename extraction, preventing directory traversal attacks.
- **Ephemeral Storage**: Uploaded temporary files in `scratch/uploads` are deleted immediately upon conversion completion.
- **No Remote Code Execution**: No `eval()`, `exec()`, or dynamic imports of user data.

---

## ⚠️ Known Limitations

1. **Scanned / Image-Only PDFs**: Text cannot be extracted directly from raster image scans. The system detects scanned PDFs and warns:
   ```text
   This PDF appears to contain scanned/image-only content. OCR is required for text extraction.
   ```
2. **Legacy Source Fonts Without Files**: Kruti Dev, DevLys, and Kantal require their TrueType font files placed in `assets/fonts/source/` for verification before conversion is allowed.

---

## 🛠️ Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `Font file not found` | Font missing from `assets/fonts/` | Verify `assets/fonts/Shivaji01 Normal.ttf` exists. |
| `DOCX characters unreadable in Word` | Recipient PC lacks `Shivaji01 Normal` font | Install `Shivaji01 Normal.ttf` on the viewing computer, or export as PDF. |
| `Scanned PDF error` | PDF contains images of text rather than extractable text | Run the PDF through an OCR tool before conversion. |

---

## 📄 License

MIT License. Designed and developed from scratch for Marathi and Devanagari typography preservation.
