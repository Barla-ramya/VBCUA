# Voice-Based Concept Understanding Analyser (VBCUA)

VBCUA is an APSCHE Internship Project that evaluates a student's spoken explanation of a technical concept. It combines Whisper transcription, Sentence-BERT semantic comparison, Librosa delivery metrics, an explainable scoring rubric, and a downloadable PDF report.

> The score is an educational indicator for reflection and feedback; it is not a clinical speech or cognitive assessment.

## Features

- Upload and play WAV, MP3, M4A, OGG, or FLAC recordings up to 100 MB.
- Transcribe speech with OpenAI Whisper (`base` model).
- Compare explanations with `all-MiniLM-L6-v2` Sentence-BERT embeddings.
- Measure duration, RMS energy, silence/pause ratio, speaking rate, and waveform.
- Detect common filler words, including *um*, *uh*, *like*, and *you know*.
- Produce semantic, fluency, pace, energy, overall, and understanding-level feedback.
- Export a professional PDF report containing the transcript, waveform, metrics, score, and timestamp.
- Cache heavy models so they are loaded only once per running process.

## Requirements

- Python 3.10 or newer
- Internet access for the first Whisper, Sentence-BERT, and NLTK resource download

`imageio-ffmpeg` supplies a managed FFmpeg binary for Whisper. A separately installed system FFmpeg is therefore optional.

## Installation

```powershell
python -m venv vbcu_env
.\vbcu_env\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run

```powershell
streamlit run app.py
```

Open the local URL printed by Streamlit. Choose **Upload Audio**, select a concept, upload a spoken explanation, then visit **Analysis**, **Results**, and **Report**.

## Architecture

```text
Audio upload -> Whisper transcript -> Sentence-BERT similarity
      |                 |
      v                 v
Librosa features -> scoring engine -> Streamlit dashboard / PDF report
```

The overall score is weighted as follows: semantic alignment 60%, fluency 20%, vocal energy 10%, and speaking pace 10%. Scores of 75 and above are **Strong**, 50–74 are **Moderate**, and lower scores are **Poor**.

## Project structure

```text
VBCUA/
├── app.py                       # Streamlit UI
├── config.py                    # Central runtime configuration
├── modules/
│   ├── speech_to_text.py        # Whisper service
│   ├── semantic_eval.py         # Sentence-BERT similarity
│   ├── audio_utils.py           # Audio features and waveform generation
│   ├── waveform.py              # Public waveform service
│   ├── scoring_engine.py        # Rubric and feedback
│   ├── report_generator.py      # ReportLab PDF export
│   ├── helper.py                # Validation and filler detection
│   └── session_manager.py       # Streamlit state defaults
├── reference_data/concepts.json # Ten curated concepts
├── tests/                       # Offline unit tests
├── uploads/ reports/ waveform/  # Runtime output directories
├── sample_audio/ assets/ docs/
└── requirements.txt
```

## Testing

```powershell
pytest -q
```

The test suite deliberately avoids live model downloads. It validates malformed/missing input handling, audio analysis, waveform creation, semantic-score calculation with a mock model, filler detection, scoring bounds, and PDF output.

## Deployment notes

For deployment, install FFmpeg on the target host, persist the `reports/` directory if reports must survive restarts, and set resource limits appropriate for the Whisper model. Keep uploaded recordings private and periodically remove them in production.

## Screenshots

Add screenshots of the Home, Analysis, and PDF report views under `docs/` before submitting a project report or presentation.

## Future improvements

- Instructor authentication and cohort analytics
- Additional languages and customized reference rubrics
- Keyword coverage and plagiarism-aware feedback
- Background job processing for long recordings

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
