"""Shared validation and text helpers."""
import re
from pathlib import Path
from typing import Iterable

FILLER_PATTERNS = ("you know", "sort of", "kind of", "actually", "basically", "like", "well", "um", "uh")


def validate_audio_file(name: str, allowed_extensions: Iterable[str]) -> None:
    """Raise a helpful error when an uploaded filename is unsupported."""
    if not name or "." not in name or Path(name).suffix[1:].lower() not in allowed_extensions:
        allowed = ", ".join(sorted(allowed_extensions))
        raise ValueError(f"Unsupported audio file. Use one of: {allowed}.")


def count_fillers(transcript: str) -> dict[str, float | int | dict[str, int]]:
    """Count common speech fillers using word boundaries."""
    normalized = re.sub(r"\s+", " ", transcript.lower()).strip()
    counts = {term: len(re.findall(rf"(?<!\w){re.escape(term)}(?!\w)", normalized)) for term in FILLER_PATTERNS}
    total_words = len(re.findall(r"\b[\w']+\b", normalized))
    total = sum(counts.values())
    return {"total_fillers": total, "filler_ratio": total / max(total_words, 1), "filler_counts": counts, "word_count": total_words}
