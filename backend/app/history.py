"""Local conversion history and audit logging engine (Phase 19).

Uses local SQLite database to persist conversion metadata, characters,
warnings, and statuses without sending any documents off the local machine.
"""
from __future__ import annotations

import sqlite3
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_DIR = Path("storage")
DB_PATH = DB_DIR / "history.db"


@dataclass
class HistoryRecord:
    id: Optional[int]
    filename: str
    timestamp: str
    source_font: str
    target_font: str
    characters_processed: int
    warnings_count: int
    status: str
    output_format: str
    output_path: Optional[str] = None
    report_text: Optional[str] = None


class HistoryManager:
    """Manages local conversion audit records and statistics in SQLite."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversion_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    source_font TEXT NOT NULL,
                    target_font TEXT NOT NULL,
                    characters_processed INTEGER NOT NULL,
                    warnings_count INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    output_format TEXT NOT NULL,
                    output_path TEXT,
                    report_text TEXT
                )
                """
            )
            conn.commit()

    def add_record(self, record: HistoryRecord) -> int:
        """Adds a conversion record and returns its primary key ID."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO conversion_history (
                    filename, timestamp, source_font, target_font,
                    characters_processed, warnings_count, status,
                    output_format, output_path, report_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.filename,
                    record.timestamp or datetime.now(timezone.utc).isoformat(),
                    record.source_font,
                    record.target_font,
                    record.characters_processed,
                    record.warnings_count,
                    record.status,
                    record.output_format,
                    record.output_path,
                    record.report_text,
                ),
            )
            conn.commit()
            return cursor.lastrowid or 0

    def get_all_records(self, limit: int = 50) -> List[HistoryRecord]:
        """Retrieves recent history records in descending chronological order."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, filename, timestamp, source_font, target_font,
                       characters_processed, warnings_count, status,
                       output_format, output_path, report_text
                FROM conversion_history
                ORDER BY id DESC LIMIT ?
                """,
                (limit,),
            )
            rows = cursor.fetchall()
            return [
                HistoryRecord(
                    id=row["id"],
                    filename=row["filename"],
                    timestamp=row["timestamp"],
                    source_font=row["source_font"],
                    target_font=row["target_font"],
                    characters_processed=row["characters_processed"],
                    warnings_count=row["warnings_count"],
                    status=row["status"],
                    output_format=row["output_format"],
                    output_path=row["output_path"],
                    report_text=row["report_text"],
                )
                for row in rows
            ]

    def get_statistics(self) -> Dict[str, Any]:
        """Computes real dashboard statistics without any fabrication."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM conversion_history")
            total_converted = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM conversion_history WHERE warnings_count = 0")
            successful = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM conversion_history WHERE warnings_count > 0")
            needs_review = cursor.fetchone()[0]

            cursor.execute("SELECT COALESCE(SUM(characters_processed), 0) FROM conversion_history")
            total_chars = cursor.fetchone()[0]

            return {
                "files_converted": total_converted,
                "successful": successful,
                "needs_review": needs_review,
                "total_characters_processed": total_chars,
            }
