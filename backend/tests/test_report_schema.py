from fastapi.testclient import TestClient

from app.main import app
from app.models.analysis import AudienceReactionReport, MediaAnalysisResult


client = TestClient(app)


def test_report_schema_endpoint_returns_examples() -> None:
    response = client.get("/report-schema")

    assert response.status_code == 200
    payload = response.json()
    assert payload["phase"] == 4
    assert "analysis_result_example" in payload
    assert "report_schema_example" in payload


def test_phase_four_models_expose_schema_examples() -> None:
    report_schema = AudienceReactionReport.model_json_schema()
    analysis_schema = MediaAnalysisResult.model_json_schema()

    assert "example" in report_schema
    assert "example" in analysis_schema
