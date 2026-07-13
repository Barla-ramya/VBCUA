"""Application configuration and workspace paths."""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
SAMPLE_AUDIO_DIR = BASE_DIR / "sample_audio"
REPORT_DIR = BASE_DIR / "reports"
WAVEFORM_DIR = BASE_DIR / "waveform"
MODEL_CACHE_DIR = BASE_DIR / ".model_cache"
NLTK_DATA_DIR = BASE_DIR / ".nltk_data"
FFMPEG_BIN_DIR = BASE_DIR / ".ffmpeg_bin"
LOGO_FILE = BASE_DIR / "assets" / "logo.png"
REFERENCE_FILE = BASE_DIR / "reference_data" / "concepts.json"
MAX_UPLOAD_MB = 100
ALLOWED_EXTENSIONS = {"wav", "mp3", "m4a", "ogg", "flac"}
WHISPER_MODEL = "base"
SENTENCE_MODEL = "all-MiniLM-L6-v2"
APP_NAME = "Voice-Based Concept Understanding Analyser"
APP_VERSION = "1.0.0"

for directory in (UPLOAD_DIR, SAMPLE_AUDIO_DIR, REPORT_DIR, WAVEFORM_DIR, MODEL_CACHE_DIR, NLTK_DATA_DIR, FFMPEG_BIN_DIR):
    directory.mkdir(parents=True, exist_ok=True)

# Some restricted Windows profiles do not permit Matplotlib to use its default
# home-directory cache. Keep its small cache inside the project instead.
os.environ.setdefault("MPLCONFIGDIR", str(BASE_DIR / ".matplotlib"))
