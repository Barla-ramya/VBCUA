"""Whisper transcription service with lazy, cached loading."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import os
import shutil
from config import FFMPEG_BIN_DIR, MODEL_CACHE_DIR, WHISPER_MODEL

_MODEL: Any | None = None


def configure_ffmpeg() -> None:
    """Expose imageio's managed FFmpeg executable to Whisper's subprocesses."""
    try:
        import imageio_ffmpeg

        source = Path(imageio_ffmpeg.get_ffmpeg_exe())
        # Whisper invokes the command specifically as ``ffmpeg``. The managed
        # binary has a platform-specific filename, so expose a stable alias.
        target = FFMPEG_BIN_DIR / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
        if not target.exists():
            shutil.copy2(source, target)
        ffmpeg_directory = str(FFMPEG_BIN_DIR)
        current_path = os.environ.get("PATH", "")
        if ffmpeg_directory not in current_path.split(os.pathsep):
            os.environ["PATH"] = ffmpeg_directory + os.pathsep + current_path
    except Exception as exc:
        raise RuntimeError(
            "FFmpeg is unavailable. Install imageio-ffmpeg or add FFmpeg to PATH."
        ) from exc


def load_model(model_name: str = WHISPER_MODEL) -> Any:
    """Load Whisper only once; download occurs on the first real analysis."""
    global _MODEL
    if _MODEL is None:
        try:
            import whisper
            configure_ffmpeg()
            _MODEL = whisper.load_model(model_name, download_root=str(MODEL_CACHE_DIR))
        except Exception as exc:
            raise RuntimeError("Unable to load Whisper. Check FFmpeg, internet access, and model dependencies.") from exc
    return _MODEL


def transcribe_audio(audio_path: str | Path, model_name: str = WHISPER_MODEL) -> str:
    """Transcribe supported audio and return a clean transcript."""
    path = Path(audio_path)
    if not path.is_file():
        raise FileNotFoundError("Audio file was not found.")
    try:
        # Whisper handles resampling/normalization internally via FFmpeg.
        model = load_model(model_name)
        result = model.transcribe(str(path), fp16=False, verbose=False)
        text = str(result.get("text", "")).strip()
    except RuntimeError:
        raise
    except Exception as exc:
        raise RuntimeError("Audio transcription failed. The file may be corrupted or FFmpeg may be unavailable.") from exc
    if not text:
        raise ValueError("No speech was detected. Please upload a clearer spoken explanation.")
    return text
