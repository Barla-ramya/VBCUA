"""Waveform service kept as a dedicated public module for integrations."""
from pathlib import Path

from .audio_utils import generate_waveform

__all__ = ["create_waveform"]


def create_waveform(audio_path: str | Path, output_path: str | Path) -> Path:
    """Generate and return the waveform PNG for an audio recording."""
    return generate_waveform(audio_path, output_path)
