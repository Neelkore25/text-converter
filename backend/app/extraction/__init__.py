"""Document extraction package."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class DocumentContent:
    text: str
    format: str
    file_path: Optional[str] = None
    font_hint: Optional[str] = None
    page_count: int = 1
    character_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_scanned_image_only: bool = False
