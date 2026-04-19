from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

from app.core.database import get_connection
from app.models.analysis import AnalyzeRequest, AudienceReactionReport, MediaAnalysisResult
from app.models.api import ReportListItem, ReportListResponse, StoredReportResponse


def save_report(
    request: AnalyzeRequest,
    analysis: MediaAnalysisResult,
    report: AudienceReactionReport,
) -> StoredReportResponse:

    report_id = uuid4().hex
    created_at = datetime.now(timezone.utc)

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO reports (
                id,
                created_at,
                platform,
                media_type,
                filename,
                mime_type,
                caption,
                file_size_bytes,
                duration_seconds,
                report_json,
                analysis_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report_id,
                created_at.isoformat(),
                request.platform.value,
                request.media_type.value,
                request.filename,
                request.mime_type,
                request.caption,
                request.file_size_bytes,
                request.duration_seconds,
                report.model_dump_json(),
                analysis.model_dump_json(),
            ),
        )
        connection.commit()

    return StoredReportResponse(
        id=report_id,
        created_at=created_at,
        report=report,
        analysis=analysis,
    )


def get_report(report_id: str) -> StoredReportResponse | None:

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, created_at, report_json, analysis_json
            FROM reports
            WHERE id = ?
            """,
            (report_id,),
        ).fetchone()

    if row is None:
        return None

    return StoredReportResponse(
        id=row["id"],
        created_at=datetime.fromisoformat(row["created_at"]),
        report=AudienceReactionReport.model_validate(json.loads(row["report_json"])),
        analysis=MediaAnalysisResult.model_validate(json.loads(row["analysis_json"])),
    )


def list_reports(limit: int = 20) -> ReportListResponse:

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, created_at, platform, media_type, filename
            FROM reports
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    items = [
        ReportListItem(
            id=row["id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            platform=row["platform"],
            media_type=row["media_type"],
            filename=row["filename"],
        )
        for row in rows
    ]
    return ReportListResponse(reports=items)
