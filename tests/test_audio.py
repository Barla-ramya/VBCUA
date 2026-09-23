import numpy as np
import soundfile as sf
import pytest
from modules.audio_utils import extract_audio_features, generate_waveform, normalize_audio


def test_audio_metrics_and_waveform(tmp_path) -> None:
    audio = tmp_path / "sample.wav"
    sf.write(audio, .1 * np.sin(2 * np.pi * 220 * np.linspace(0, 1, 16000)), 16000)
    metrics = extract_audio_features(audio)
    image = generate_waveform(audio, tmp_path / "wave.png")
    assert metrics["duration_seconds"] == 1.0
    assert 0 <= metrics["pause_ratio"] <= 1
    assert image.is_file()


def test_audio_normalization_and_invalid_audio(tmp_path) -> None:
    audio = tmp_path / "quiet.wav"
    sf.write(audio, .01 * np.sin(2 * np.pi * 220 * np.linspace(0, 1, 16000)), 16000)
    normalized = normalize_audio(audio, tmp_path / "normalized.wav")
    data, _ = sf.read(normalized)
    assert normalized.is_file()
    assert np.max(np.abs(data)) > 0.9
    invalid = tmp_path / "invalid.wav"
    invalid.write_text("not audio", encoding="utf-8")
    with pytest.raises(RuntimeError):
        extract_audio_features(invalid)
