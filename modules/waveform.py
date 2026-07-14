from pathlib import Path
from .audio_utils import generate_waveform
from pathlib import Path
from .audio_utils import generate_waveform

def create_waveform(audio_path: str | Path, output_path: str | Path) -> Path:
    return generate_waveform(audio_path, output_path)