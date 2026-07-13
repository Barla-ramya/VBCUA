from modules.report_generator import generate_pdf_report


def test_pdf_report_is_created(tmp_path) -> None:
    """A report can be produced without optional waveform input."""
    report = generate_pdf_report(
        tmp_path / "report.pdf",
        "Student <One>",
        "Machine Learning",
        "A <safe> explanation.",
        {"duration_seconds": 12, "pause_ratio": 0.1, "speech_rate_wpm": 125},
        {
            "semantic_score": 80,
            "overall_score": 82,
            "understanding_level": "Strong",
            "total_fillers": 1,
            "feedback": ["Clear explanation."],
        },
    )
    assert report.is_file()
    assert report.stat().st_size > 500
