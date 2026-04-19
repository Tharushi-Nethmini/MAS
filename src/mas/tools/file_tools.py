from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json_file(path: str) -> dict[str, Any]:
    """Load and parse a JSON file from local disk.

    Args:
        path: Path to the JSON file.

    Returns:
        Parsed JSON object as a dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If JSON content is invalid or root object is not a dictionary.
    """

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with file_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object at the root level.")
    return data


def save_markdown_file(path: str, content: str) -> str:
    """Save markdown content to local disk and return absolute path."""

    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return str(file_path.resolve())
