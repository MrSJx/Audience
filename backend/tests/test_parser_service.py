import json

from app.models.analysis import AudienceReactionReport
from app.services.parser_service import parse_report_payload


def _example_payload() -> dict[str, object]:
    return {
        "platform": "instagram_reels",
        "content_summary": "A sharp short-form clip with a strong hook and a softer middle.",
        "hook_score": 74,
        "engagement_score": 67,
        "boring_rate": 31,
        "peak_moments": [
            {"timestamp": "0:01", "event": "quick stop-scroll opener"},
        ],
        "simulated_comments": [
            "The first second is doing the heavy lifting.",
            "The middle could tighten up a little.",
        ],
        "final_verdict": "Good concept with enough hook to test, but pacing still needs refinement.",
        "improvements": [
            "Trim the weaker middle beat.",
            "Move the clearest payoff earlier.",
        ],
    }


def test_parse_report_payload_accepts_raw_json_string() -> None:
    report = parse_report_payload(json.dumps(_example_payload()))

    assert isinstance(report, AudienceReactionReport)
    assert report.platform.value == "instagram_reels"


def test_parse_report_payload_accepts_fenced_json_string() -> None:
    fenced_payload = "```json\n" + json.dumps(_example_payload(), indent=2) + "\n```"

    report = parse_report_payload(fenced_payload)

    assert isinstance(report, AudienceReactionReport)
    assert report.peak_moments[0].timestamp == "0:01"
