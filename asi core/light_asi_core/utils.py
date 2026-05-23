from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Dict, List, Optional

TOKEN_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_\-]{2,}")


def sha1_hex(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()


def read_text_limited(path: Path, max_bytes: int) -> str:
    if path.stat().st_size > max_bytes:
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="latin-1")
        except UnicodeDecodeError:
            return ""


def tokenize(text: str) -> List[str]:
    return [m.group(0).lower() for m in TOKEN_PATTERN.finditer(text)]


def trim_text(text: str, max_chars: int) -> str:
    normalized = text.strip()
    if len(normalized) <= max_chars:
        return normalized
    return normalized[: max_chars - 3] + "..."


def extract_json_object(raw_text: str) -> Optional[Dict]:
    text = raw_text.strip()
    if not text:
        return None
    try:
        decoded = json.loads(text)
        if isinstance(decoded, dict):
            return decoded
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    for index in range(start, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                candidate = text[start : index + 1]
                try:
                    decoded = json.loads(candidate)
                    if isinstance(decoded, dict):
                        return decoded
                except json.JSONDecodeError:
                    return None
    return None
