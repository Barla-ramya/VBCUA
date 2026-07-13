from modules.helper import count_fillers
from modules.scoring_engine import calculate_score


def test_filler_detection_handles_phrases() -> None:
    result = count_fillers("Um, you know, this is actually like a test.")
    assert result["total_fillers"] == 4
    assert result["filler_counts"]["you know"] == 1


def test_scoring_is_bounded_and_classified() -> None:
    result = calculate_score(85, {"pause_ratio": .1, "rms_energy": .06, "speech_rate_wpm": 130}, "This is a clear explanation of the concept.")
    assert 0 <= result["overall_score"] <= 100
    assert result["understanding_level"] == "Strong"
