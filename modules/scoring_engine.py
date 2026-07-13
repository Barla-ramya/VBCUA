"""Transparent weighted scoring for conceptual understanding."""
from __future__ import annotations
from .helper import count_fillers


def calculate_score(semantic_score: float, audio_metrics: dict[str, float], transcript: str) -> dict:
    """Combine semantic and delivery indicators into an explainable result."""
    fillers = count_fillers(transcript)
    pause = float(audio_metrics.get("pause_ratio", 1))
    energy = float(audio_metrics.get("rms_energy", 0))
    rate = float(audio_metrics.get("speech_rate_wpm", 0))
    fluency = max(0.0, 100 - pause * 100 * 0.65 - float(fillers["filler_ratio"]) * 100 * 1.4)
    energy_score = min(100.0, energy / 0.06 * 100)
    rate_score = max(0.0, 100 - min(abs(rate - 135) / 135 * 100, 100)) if rate else 45.0
    overall = round(semantic_score * .60 + fluency * .20 + energy_score * .10 + rate_score * .10, 2)
    level = "Strong" if overall >= 75 else "Moderate" if overall >= 50 else "Poor"
    feedback = []
    feedback.append("Your explanation aligns well with the reference concept." if semantic_score >= 70 else "Cover more key ideas from the reference explanation.")
    if pause > .35: feedback.append("Reduce long pauses by briefly planning your explanation before recording.")
    if fillers["filler_ratio"] > .05: feedback.append("Use fewer filler words to make the explanation more confident.")
    if rate and (rate < 80 or rate > 190): feedback.append("Aim for a steady pace of roughly 100–170 words per minute.")
    if not feedback: feedback.append("Clear, balanced delivery. Keep this structure for future explanations.")
    return {"overall_score": overall, "understanding_level": level, "semantic_score": semantic_score,
            "fluency_score": round(fluency, 2), "energy_score": round(energy_score, 2), "pace_score": round(rate_score, 2),
            "feedback": feedback, **fillers}
