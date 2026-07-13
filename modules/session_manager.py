"""Small Streamlit session-state abstraction."""


def initialize_session_state(st) -> None:
    """Populate all application state values once per browser session."""
    defaults = {
        "analysis": None,
        "audio_path": None,
        "waveform_path": None,
        "pdf_path": None,
        "analysis_source": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
