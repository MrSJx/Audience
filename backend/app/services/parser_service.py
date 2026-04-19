from __future__ import annotations

import json
from json import JSONDecodeError

from app.models.analysis import AudienceReactionReport


def parse_report_payload(payload: dict[str, object] | str) -> AudienceReactionReport:
    if isinstance(payload, str):
        payload = _extract_json_object(payload)
    return AudienceReactionReport.model_validate(payload)


def _extract_json_object(raw_text: str) -> dict[str, object]:
    normalized = raw_text.strip()
    if normalized.startswith("```"):
        lines = normalized.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        normalized = "\n".join(lines).strip()

    try:
        parsed = json.loads(normalized)
    except JSONDecodeError:
        start = normalized.find("{")
        end = normalized.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("Could not find a valid JSON object in the model response.") from None
        parsed = json.loads(normalized[start : end + 1])

    if not isinstance(parsed, dict):
        raise ValueError("Model response must be a JSON object.")
    return parsed
