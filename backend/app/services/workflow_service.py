from __future__ import annotations

from pathlib import Path

from app.models.analysis import AnalyzeRequest
from app.models.api import StoredReportResponse
from app.services.analyzer_service import analyze_media
from app.services.report_service import generate_report_from_analysis
from app.services.repository_service import save_report


def run_analysis_workflow(file_path: str | Path, request: AnalyzeRequest) -> StoredReportResponse:
    analysis = analyze_media(file_path, request)
    report = generate_report_from_analysis(analysis)
    return save_report(request, analysis, report)
