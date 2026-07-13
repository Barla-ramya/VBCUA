def normalize_audio(audio_path, output_path):
    try:
        import librosa
        import soundfile as sf
        from pathlib import Path
        import numpy as np

        print("Reading:", audio_path)

        audio, sample_rate = librosa.load(
            str(audio_path),
            sr=16000,
            mono=True
        )

        print("Loaded successfully")
        print("Sample Rate:", sample_rate)
        print("Shape:", audio.shape)

        peak = np.max(np.abs(audio))

        normalized = audio * (0.95 / peak)

        destination = Path(output_path)

        sf.write(
            destination,
            normalized,
            sample_rate,
            subtype="PCM_16"
        )

        print("Saved:", destination)

        return destination

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise