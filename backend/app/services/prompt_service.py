from __future__ import annotations

import json

from app.models.analysis import MediaAnalysisResult


def build_report_prompt(analysis: MediaAnalysisResult) -> str:
    prompt_payload = {
        "system_role": (
            "You are Audience, a brutally honest but constructive content feedback assistant."
        ),
        "instruction": (
            "Generate an honest Instagram Reels audience reaction report in strict JSON using "
            "the required fields only. Return only one raw JSON object with no markdown, no "
            "code fences, and no explanation."
        ),
        "required_fields": [
            "platform",
            "content_summary",
            "hook_score",
            "engagement_score",
            "boring_rate",
            "peak_moments",
            "simulated_comments",
            "final_verdict",
            "improvements",
        ],
        "analysis": analysis.model_dump(mode="json"),
        "rules": [
            "Keep scores between 0 and 100.",
            "Keep the tone direct, useful, and creator-focused.",
            "Use short, concrete comments and improvements.",
            "Do not claim guaranteed virality or certainty.",
            "Reflect pacing, contrast, brightness, and text cues in the output.",
            "Do not invent unsupported platforms, media types, or sections.",
        ],
    }
    return (
        "Use the following structured context to produce the final report.\n"
        "Return JSON only.\n\n"
        f"{json.dumps(prompt_payload, indent=2)}"
    )
