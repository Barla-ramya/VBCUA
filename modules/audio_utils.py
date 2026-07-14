import librosa
import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def normalize_audio(audio_path, output_path):
    """
    Normalize audio volume and save processed file
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
    Extract audio characteristics
    """

    audio, sr = librosa.load(
        str(audio_path),
        sr=16000,
        mono=True
    )


    duration = librosa.get_duration(
        y=audio,
        sr=sr
    )


    rms_energy = float(
        np.mean(
            librosa.feature.rms(
                y=audio
            )
        )
    )


    silence = librosa.effects.split(
        audio,
        top_db=30
    )


    speech_duration = sum(
        end-start
        for start,end in silence
    ) / sr


    pause_ratio = 1 - (
        speech_duration / duration
    )


    return {

        "duration": round(duration,2),

        "rms_energy": round(
            rms_energy,
            4
        ),

        "pause_ratio": round(
            pause_ratio,
            4
        ),

        "sample_rate": sr
    }



def generate_waveform(audio_path, output_path):

    audio, sr = librosa.load(
        str(audio_path),
        sr=16000
    )


    plt.figure(figsize=(10,3))

    plt.plot(audio)

    plt.title(
        "Audio Waveform"
    )

    plt.xlabel(
        "Samples"
    )

    plt.ylabel(
        "Amplitude"
    )


    plt.tight_layout()


    plt.savefig(
        output_path
    )

    plt.close()


    return output_path