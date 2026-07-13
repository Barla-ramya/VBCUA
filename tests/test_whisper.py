import pytest
from modules import speech_to_text


def test_missing_audio_is_reported() -> None:
    with pytest.raises(FileNotFoundError):
        speech_to_text.transcribe_audio("does-not-exist.wav")


def test_managed_ffmpeg_can_be_configured() -> None:
    """Whisper receives a usable FFmpeg location without a system installation."""
    speech_to_text.configure_ffmpeg()
