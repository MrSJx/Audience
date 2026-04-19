from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import ValidationError

from app.models.analysis import AnalyzeRequest
from app.models.api import ReportListResponse, StoredReportResponse
from app.models.platforms import TargetPlatform
from app.services.repository_service import get_report, list_reports
from app.services.report_service import (
    get_phase_eleven_contract_snapshot,
    get_phase_three_and_four_snapshot,
    get_phase_two_contract,
    get_starter_report_shape,
)
from app.services.llm_service import LLMServiceError
from app.services.storage_service import persist_upload
from app.services.workflow_service import run_analysis_workflow
from app.utils.media import detect_media_type, probe_video_duration_seconds


router = APIRouter()


@router.get("/", tags=["meta"])
def read_root() -> dict[str, object]:
    return {
        "message": "Audience backend foundation is running.",
        "phase": 12,
        "next_step": "Use the frozen Simulation 2.0 contract and multi-agent persistence foundation to build the runtime phases safely.",
        "starter_report_shape": get_starter_report_shape(),
    }


@router.get("/health", tags=["meta"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/contract", tags=["meta"])
def get_contract() -> dict[str, object]:
    return get_phase_two_contract()


@router.get("/report-schema", tags=["meta"])
def get_report_schema() -> dict[str, object]:
    return get_phase_three_and_four_snapshot()


@router.get("/simulation-schema", tags=["meta"])
def get_simulation_schema() -> dict[str, object]:
    return get_phase_eleven_contract_snapshot()


@router.post(
    "/analyze",
    tags=["analysis"],
    response_model=StoredReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def analyze_upload(
    file: UploadFile = File(...),
    platform: TargetPlatform = Form(default=TargetPlatform.INSTAGRAM_REELS),
    caption: str | None = Form(default=None),
    duration_seconds: float | None = Form(default=None),
) -> StoredReportResponse:
    try:
        stored_path = persist_upload(file)
        mime_type = file.content_type or _guess_mime_type(file.filename or stored_path.name)
        media_type = detect_media_type(file.filename or stored_path.name, mime_type)
        file_size_bytes = Path(stored_path).stat().st_size
        effective_duration = duration_seconds
        if media_type.value == "short_video" and effective_duration is None:
            effective_duration = probe_video_duration_seconds(stored_path)
        request = AnalyzeRequest(
            platform=platform,
            media_type=media_type,
            filename=file.filename or stored_path.name,
            mime_type=mime_type,
            file_size_bytes=file_size_bytes,
            caption=caption,
            duration_seconds=effective_duration if media_type.value == "short_video" else None,
        )
        return run_analysis_workflow(stored_path, request)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    except ValidationError as error:
        message = "; ".join(issue["msg"] for issue in error.errors())
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message) from error
    except FileNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except LLMServiceError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error


@router.get("/report/{report_id}", tags=["analysis"], response_model=StoredReportResponse)
def read_report(report_id: str) -> StoredReportResponse:
    stored_report = get_report(report_id)
    if stored_report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report not found: {report_id}",
        )
    return stored_report


@router.get("/reports", tags=["analysis"], response_model=ReportListResponse)
def read_reports() -> ReportListResponse:
    return list_reports()


def _guess_mime_type(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".png":
        return "image/png"
    if suffix == ".webp":
        return "image/webp"
    if suffix == ".mp4":
        return "video/mp4"
    if suffix == ".mov":
        return "video/quicktime"
    if suffix == ".webm":
        return "video/webm"
    return "application/octet-stream"
