"""Streamlit entry point for the Voice-Based Concept Understanding Analyser."""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from config import (
    ALLOWED_EXTENSIONS,
    APP_NAME,
    LOGO_FILE,
    MAX_UPLOAD_MB,
    REFERENCE_FILE,
    REPORT_DIR,
    SAMPLE_AUDIO_DIR,
    UPLOAD_DIR,
    WAVEFORM_DIR,
)
from modules.audio_utils import extract_audio_features, normalize_audio
from modules.helper import validate_audio_file
from modules.report_generator import generate_pdf_report
from modules.scoring_engine import calculate_score
from modules.semantic_eval import semantic_similarity
from modules.session_manager import initialize_session_state
from modules.speech_to_text import transcribe_audio
from modules.waveform import create_waveform

st.set_page_config(page_title="VBCUA", page_icon="🎙️", layout="wide")
initialize_session_state(st)
st.markdown(
    """<style>
    .block-container {max-width: 1150px; padding-top: 2rem;}
    [data-testid="stMetricValue"] {color: #2563eb;}
    </style>""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_concepts() -> list[dict[str, Any]]:
    """Load the curated reference concepts once per Streamlit cache cycle."""
    try:
        with REFERENCE_FILE.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("Reference concept data is unavailable or invalid.") from exc
    if not isinstance(data, list) or not data:
        raise RuntimeError("No reference concepts are configured.")
    return data


def analyse_audio(audio_name: str, audio_data: bytes, concept: dict[str, Any]) -> None:
    """Persist, transcribe, measure, score, and retain one audio recording."""
    validate_audio_file(audio_name, ALLOWED_EXTENSIONS)
    if len(audio_data) > MAX_UPLOAD_MB * 1024 * 1024:
        raise ValueError(f"Audio must be smaller than {MAX_UPLOAD_MB} MB.")

    identifier = uuid.uuid4().hex
    suffix = Path(audio_name).suffix.lower()
    audio_path = UPLOAD_DIR / f"{identifier}{suffix}"
    normalized_path = UPLOAD_DIR / f"{identifier}_normalized.wav"
    audio_path.write_bytes(audio_data)

    try:
        normalized_path = normalize_audio(audio_path, normalized_path)
        transcript = transcribe_audio(normalized_path)
        metrics = extract_audio_features(normalized_path)
        waveform_path = create_waveform(normalized_path, WAVEFORM_DIR / f"{identifier}.png")
        semantic_score = semantic_similarity(
            transcript, concept["reference_explanation"]
        )
        score = calculate_score(semantic_score, metrics, transcript)
    except Exception:
        audio_path.unlink(missing_ok=True)
        normalized_path.unlink(missing_ok=True)
        raise

    st.session_state.audio_path = str(audio_path)
    st.session_state.waveform_path = str(waveform_path)
    st.session_state.pdf_path = None
    st.session_state.analysis = {
        "transcript": transcript,
        "metrics": metrics,
        "score": score,
        "topic": concept["title"],
    }


def render_analysis(data: dict[str, Any], detailed: bool = True) -> None:
    """Render analysis fields consistently in the Analysis, Results, and Report views."""
    score, metrics = data["score"], data["metrics"]
    print("DEBUG METRICS:", metrics)
    st.subheader(f"Analysis: {data['topic']}")
    columns = st.columns(4)
    columns[0].metric("Overall score", f"{score['overall_score']:.1f}%")
    columns[1].metric("Semantic similarity", f"{score['semantic_score']:.1f}%")
    columns[2].metric("Pause ratio", f"{metrics['pause_ratio'] * 100:.1f}%")
    columns[3].metric("Filler words", score["total_fillers"])
    if not detailed:
        return

    left, right = st.columns([1.2, 1])
    with left:
        st.image(st.session_state.waveform_path, caption="Audio waveform")
        st.markdown("#### Transcript")
        st.write(data["transcript"])
    with right:
        st.markdown(f"#### Understanding level: {score['understanding_level']}")
        st.progress(int(round(score["overall_score"])))
        st.markdown("#### Audio metrics")
        st.dataframe(
            {
                "Metric": ["Duration", "Silence", "Speech rate", "RMS energy", "Fluency"],
                "Value": [
                    f"{metrics['duration_seconds']} seconds",
                    f"{metrics['silence_seconds']} seconds",
                    f"{metrics['speech_rate_wpm']} WPM",
                    metrics["rms_energy"],
                    f"{score['fluency_score']}%",
                ],
            },
            hide_index=True,
            use_container_width=True,
        )
        st.markdown("#### Delivery score breakdown")
        st.bar_chart(
            {
                "Score": {
                    "Semantic": score["semantic_score"],
                    "Fluency": score["fluency_score"],
                    "Energy": score["energy_score"],
                    "Pace": score["pace_score"],
                }
            },
            use_container_width=True,
        )
        st.markdown("#### Feedback")
        for item in score["feedback"]:
            st.write(f"• {item}")


st.title(f"🎙️ {APP_NAME}")
st.caption("APSCHE Internship Project · Turn spoken explanations into actionable feedback.")
if LOGO_FILE.is_file():
    st.sidebar.image(str(LOGO_FILE), width=90)
page = st.sidebar.radio("Navigate", ["Home", "Upload Audio", "Analysis", "Results", "Report"])

if page == "Home":
    st.header("Assess conceptual understanding through speech")
    st.write(
        "Select a technical concept and upload a spoken explanation. VBCUA transcribes "
        "the response, measures delivery, assesses conceptual alignment, and creates a PDF report."
    )
    st.info("On first use, the Whisper and Sentence-BERT models may download. FFmpeg must be on PATH.")
elif page == "Upload Audio":
    entries = load_concepts()
    selected = st.selectbox("Concept", entries, format_func=lambda item: item["title"])
    with st.expander("Reference explanation"):
        st.write(selected["reference_explanation"])
        st.caption("Keywords: " + ", ".join(selected["keywords"]))
    input_mode = st.radio(
        "Audio source",
        ["Use Default Sample Audio", "Upload Your Own Audio"],
        horizontal=True,
    )

    if input_mode == "Use Default Sample Audio":
        sample_files = sorted(SAMPLE_AUDIO_DIR.glob("*.wav"), key=lambda path: path.name.lower())
        if not sample_files:
            st.warning("No .wav files are available in the sample_audio folder.")
        else:
            sample_file = st.selectbox(
                "Default sample audio",
                sample_files,
                format_func=lambda path: path.name,
            )
            sample_data = sample_file.read_bytes()
            st.audio(sample_data, format="audio/wav")
            source_key = f"sample:{sample_file.resolve()}:{sample_file.stat().st_mtime_ns}:{selected['title']}"
            if st.session_state.analysis_source != source_key:
                with st.spinner("Transcribing, extracting features, and evaluating meaning..."):
                    try:
                        analyse_audio(sample_file.name, sample_data, selected)
                    except Exception as exc:
                        st.error(str(exc))
                    else:
                        st.session_state.analysis_source = source_key
                        st.success("Default sample analysis complete. Open the Analysis or Results page to review it.")
    else:
        uploaded = st.file_uploader("Upload your spoken explanation", type=sorted(ALLOWED_EXTENSIONS))
        if uploaded is not None:
            st.audio(uploaded)
        if uploaded is not None and st.button("Analyse explanation", type="primary"):
            with st.spinner("Transcribing, extracting features, and evaluating meaning..."):
                try:
                    analyse_audio(uploaded.name, uploaded.getvalue(), selected)
                except Exception as exc:
                    st.error(str(exc))
                else:
                    st.session_state.analysis_source = None
                    st.success("Analysis complete. Open the Analysis or Results page to review it.")
elif page == "Analysis":
    if st.session_state.analysis:
        render_analysis(st.session_state.analysis)
    else:
        st.info("Upload and analyse an audio explanation first.")
elif page == "Results":
    if st.session_state.analysis:
        render_analysis(st.session_state.analysis, detailed=False)
        score = st.session_state.analysis["score"]
        st.markdown(f"### {score['understanding_level']} conceptual understanding")
        for item in score["feedback"]:
            st.write(f"• {item}")
    else:
        st.info("Upload and analyse an audio explanation first.")
else:
    data = st.session_state.analysis
    if not data:
        st.info("Generate an analysis before creating a report.")
    else:
        render_analysis(data, detailed=False)
        student_name = st.text_input("Student name", max_chars=100)
        if st.button("Create PDF report", type="primary"):
            destination = REPORT_DIR / f"vbcu_report_{datetime.now():%Y%m%d_%H%M%S}.pdf"
            try:
                generate_pdf_report(
                    destination, student_name, data["topic"], data["transcript"],
                    data["metrics"], data["score"], st.session_state.waveform_path,
                )
            except Exception as exc:
                st.error(f"Could not create the PDF report: {exc}")
            else:
                st.session_state.pdf_path = str(destination)
                st.success("PDF report created.")
        if st.session_state.pdf_path:
            pdf_path = Path(st.session_state.pdf_path)
            if pdf_path.is_file():
                st.download_button(
                    "Download PDF report",
                    data=pdf_path.read_bytes(),
                    file_name=pdf_path.name,
                    mime="application/pdf",
                )
