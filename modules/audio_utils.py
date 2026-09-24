import librosa
import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def normalize_audio(audio_path, output_path):
    """
    Normalize audio volume and save processed file.
    """
    audio, sr = librosa.load(
        str(audio_path),
        sr=16000,
        mono=True
    )

    peak = np.max(np.abs(audio))

    if peak > 0:
        audio = audio / peak

    sf.write(
        str(output_path),
        audio,
        sr
    )

    return output_path


def extract_audio_features(audio_path):
    """
    Extract audio features required by app.py.
    """
    audio, sr = librosa.load(
        str(audio_path),
        sr=16000,
        mono=True
    )

    # Duration
    duration_seconds = librosa.get_duration(
        y=audio,
        sr=sr
    )

    # RMS Energy
    rms_energy = float(
        np.mean(
            librosa.feature.rms(y=audio)
        )
    )

    # Zero Crossing Rate
    zcr = float(
        np.mean(
            librosa.feature.zero_crossing_rate(y=audio)
        )
    )

    # Silence Detection
    threshold = 0.02

    silent_samples = np.sum(
        np.abs(audio) < threshold
    )

    silence_seconds = silent_samples / sr

    pause_ratio = (
        silence_seconds / duration_seconds
        if duration_seconds > 0
        else 0
    )

    # Estimate Speech Rate
    speech_rate_wpm = max(
        80,
        min(
            180,
            int((1 - pause_ratio) * 140)
        )
    )

    # Tempo
    tempo, _ = librosa.beat.beat_track(
        y=audio,
        sr=sr
    )
    tempo = float(np.asarray(tempo).reshape(-1)[0])

    return {
        "duration_seconds": float(duration_seconds),
        "sample_rate": int(sr),
        "rms_energy": rms_energy,
        "zero_crossing_rate": zcr,
        "tempo": tempo,
        "silence_seconds": float(silence_seconds),
        "pause_ratio": float(pause_ratio),
        "speech_rate_wpm": int(speech_rate_wpm)
    }


def generate_waveform(audio_path, output_path):
    """
    Generate and save an audio waveform image.
    """
    audio, sr = librosa.load(
        str(audio_path),
        sr=16000,
        mono=True
    )

    plt.figure(figsize=(10, 3))
    plt.plot(audio)
    plt.title("Audio Waveform")
    plt.xlabel("Samples")
    plt.ylabel("Amplitude")
    plt.tight_layout()

    output_path = Path(output_path)
    plt.savefig(output_path)
    plt.close()

    return output_path
