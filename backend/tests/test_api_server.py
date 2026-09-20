"""Tests for FastAPI Web Server & REST Endpoints (Phases 18 & 19)."""
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.app.api.server import app

client = TestClient(app)


def test_serve_index_page():
    """Verify root / serves modern HTML single-page application."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Shivaji Converter" in response.text


def test_api_fonts_endpoint():
    """Verify /api/fonts returns target font and 10 source fonts."""
    response = client.get("/api/fonts")
    assert response.status_code == 200
    data = response.json()
    assert "target_font" in data
    assert data["target_font"]["name"] == "Shivaji01 Normal"
    assert len(data["source_fonts"]) == 10


def test_api_stats_endpoint():
    """Verify /api/stats returns accurate metrics."""
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "files_converted" in data
    assert "successful" in data
    assert "needs_review" in data
    assert data["supported_fonts_count"] == 10


def test_api_convert_text_live():
    """Verify live text conversion for Test Lab."""
    payload = {"text": "महाराष्ट्र माझा देश आहे.", "source_font": "auto"}
    response = client.post("/api/convert/text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_supported"] is True
    assert data["converted_text"] == "maharaYT` maaJaa doSa Aaho."
    assert data["warning_count"] == 0
    assert "elapsed_ms" in data


def test_api_convert_file_and_download(tmp_path: Path):
    """Verify multi-part file conversion and subsequent download."""
    marathi_text = "महाराष्ट्र भारत देशातील एक राज्य आहे."
    file_bytes = marathi_text.encode("utf-8")

    files = {"file": ("test_doc.txt", file_bytes, "text/plain")}
    data = {"source_font": "auto", "output_format": "txt"}

    # 1. Convert file
    response = client.post("/api/convert/file", files=files, data=data)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["output_filename"].startswith("converted_test_doc.txt")
    assert res_data["warning_count"] == 0
    assert "download_url" in res_data

    # 2. Download converted file
    dl_resp = client.get(res_data["download_url"])
    assert dl_resp.status_code == 200
    assert len(dl_resp.content) > 0


def test_api_download_path_traversal_prevention():
    """Phase 20 Security: Verify path traversal attempt is sanitized and blocked."""
    response = client.get("/api/download/../../etc/passwd")
    # Should safely return 404
    assert response.status_code == 404
