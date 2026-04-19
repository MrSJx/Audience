from __future__ import annotations

import socket
from urllib.parse import urlparse

import httpx
from pydantic import ValidationError

from app.core.config import settings
from app.models.analysis import AudienceReactionReport, MediaAnalysisResult
from app.services.parser_service import parse_report_payload
from app.services.prompt_service import build_report_prompt


class LLMServiceError(RuntimeError):
    """Raised when the configured local LLM is unavailable or returns invalid output."""


def generate_report_with_llama(analysis: MediaAnalysisResult) -> AudienceReactionReport:
    model_name = settings.ollama_model.strip()
    if not model_name.startswith("llama3.2"):
        raise LLMServiceError(
            "Audience is configured to use Llama 3.2 only. "
            f"Current model setting is '{model_name}'."
        )

    if not _ollama_is_reachable(settings.ollama_base_url):
        raise LLMServiceError(
            "Local Ollama is not reachable. Start Ollama and run "
            f"`ollama run {model_name}` first."
        )

    prompt = build_report_prompt(analysis)

    try:
        response = httpx.post(
            f"{settings.ollama_base_url.rstrip('/')}/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                },
            },
            timeout=settings.ollama_timeout_seconds,
        )
        response.raise_for_status()
    except httpx.HTTPError as error:
        raise LLMServiceError(f"Failed to reach Ollama for Llama 3.2 generation: {error}") from error

    payload = response.json()
    model_response = str(payload.get("response", "")).strip()
    if not model_response:
        raise LLMServiceError("Ollama returned an empty response for the Llama 3.2 report.")

    try:
        return parse_report_payload(model_response)
    except (ValueError, ValidationError) as error:
        raise LLMServiceError(f"Llama 3.2 returned invalid JSON output: {error}") from error


def _ollama_is_reachable(base_url: str) -> bool:
    parsed = urlparse(base_url)
    host = parsed.hostname
    if not host:
        return False

    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        with socket.create_connection(
            (host, port),
            timeout=settings.ollama_healthcheck_seconds,
        ):
            return True
    except OSError:
        return False
