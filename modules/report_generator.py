"""Professional PDF report generation."""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image


def generate_pdf_report(output_path: str | Path, student_name: str, topic: str, transcript: str, metrics: dict, score: dict, waveform_path: str | Path | None = None) -> Path:
    """Create an evaluable, self-contained analysis report."""
    destination = Path(output_path); destination.parent.mkdir(parents=True, exist_ok=True)
    safe_name, safe_topic, safe_transcript = map(escape, (student_name, topic, transcript))
    styles = getSampleStyleSheet(); styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=9, leading=12))
    story = [Paragraph("Voice-Based Concept Understanding Analyser", styles["Title"]), Spacer(1, 10),
             Paragraph("APSCHE Internship Project — Analysis Report", styles["Heading2"]), Spacer(1, 10),
             Paragraph(f"<b>Student:</b> {safe_name or 'Not provided'}<br/><b>Topic:</b> {safe_topic}<br/><b>Generated:</b> {datetime.now().strftime('%d %b %Y, %I:%M %p')}", styles["BodyText"]), Spacer(1, 12),
             Paragraph("Transcript", styles["Heading2"]), Paragraph(safe_transcript, styles["Small"]), Spacer(1, 12)]
    if waveform_path and Path(waveform_path).is_file(): story += [Paragraph("Waveform", styles["Heading2"]), Image(str(waveform_path), width=6.5*inch, height=1.56*inch), Spacer(1, 10)]
    rows = [["Metric", "Value"], ["Semantic similarity", f"{score['semantic_score']:.2f}%"], ["Overall score", f"{score['overall_score']:.2f}%"], ["Understanding level", score["understanding_level"]], ["Duration", f"{metrics['duration_seconds']:.2f} s"], ["Pause ratio", f"{metrics['pause_ratio'] * 100:.1f}%"], ["Speech rate", f"{metrics['speech_rate_wpm']:.1f} WPM"], ["Fillers", str(score['total_fillers'])]]
    table = Table(rows, colWidths=[2.8*inch, 3.7*inch]); table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1d4ed8")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("GRID", (0,0), (-1,-1), .4, colors.HexColor("#cbd5e1")), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#eff6ff")]), ("PADDING", (0,0), (-1,-1), 7)]))
    story += [Paragraph("Scores", styles["Heading2"]), table, Spacer(1, 12), Paragraph("Feedback", styles["Heading2"])]
    story += [Paragraph(f"• {item}", styles["BodyText"]) for item in score["feedback"]]
    try: SimpleDocTemplate(str(destination), pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40).build(story)
    except Exception as exc: raise RuntimeError("PDF generation failed.") from exc
    return destination
