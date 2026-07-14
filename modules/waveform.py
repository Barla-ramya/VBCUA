from pathlib import Path

import librosa
import matplotlib.pyplot as plt


def create_waveform(audio_path: str | Path, output_path: str | Path) -> Path:
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
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(output_path)
    plt.close()

    return output_path