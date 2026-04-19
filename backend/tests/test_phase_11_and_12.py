from __future__ import annotations

import json
import sqlite3
from dataclasses import replace

from fastapi.testclient import TestClient

from app.core import database as database_module
from app.core.config import settings as app_settings
from app.main import app
from app.models.simulation import SimulationRunContract


client = TestClient(app)


def test_simulation_schema_endpoint_returns_phase_eleven_snapshot() -> None:
    response = client.get("/simulation-schema")

    assert response.status_code == 200
    payload = response.json()
    assert payload["phase"] == 11
    assert payload["contract_name"] == "Simulation 2.0"
    assert "custom" in payload["supported_run_modes"]
    assert payload["response_example"]["schema_version"] == "simulation_run_v2"
    assert "consent_requirements" in payload["response_example"]


def test_phase_eleven_models_expose_schema_examples() -> None:
    simulation_schema = SimulationRunContract.model_json_schema()

    assert "example" in simulation_schema


def test_initialize_database_creates_phase_twelve_tables_and_backfills_legacy_reports(
    tmp_path, monkeypatch
) -> None:
    data_dir = tmp_path / "data"
    uploads_dir = tmp_path / "uploads"
    database_path = data_dir / "audience.db"
    data_dir.mkdir(parents=True, exist_ok=True)

    test_settings = replace(
        app_settings,
        data_dir=data_dir,
        uploads_dir=uploads_dir,
        database_path=database_path,
    )
    monkeypatch.setattr(database_module, "settings", test_settings)

    connection = sqlite3.connect(database_path)
    connection.execute(
        """
        CREATE TABLE reports (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            platform TEXT NOT NULL,
            media_type TEXT NOT NULL,
            filename TEXT NOT NULL,
            mime_type TEXT NOT NULL,
            caption TEXT,
            file_size_bytes INTEGER NOT NULL,
            duration_seconds REAL,
            report_json TEXT NOT NULL,
            analysis_json TEXT NOT NULL
        )
        """
    )
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
            "legacy-report-1",
            "2026-04-20T00:00:00+00:00",
            "instagram_reels",
            "short_video",
            "legacy.mp4",
            "video/mp4",
            "legacy caption",
            4096,
            12.5,
            json.dumps({"final_verdict": "legacy"}),
            json.dumps({"pacing_hint": "moderate pacing"}),
        ),
    )
    connection.commit()
    connection.close()

    database_module.initialize_database()

    verification = sqlite3.connect(database_path)
    tables = {
        row[0]
        for row in verification.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }

    assert {
        "reports",
        "media_assets",
        "simulation_runs",
        "run_targets",
        "agent_profiles",
        "agent_runs",
        "emotion_samples",
        "timeline_events",
        "consent_records",
        "report_exports",
    }.issubset(tables)

    simulation_run = verification.execute(
        """
        SELECT legacy_report_id, target_platform, run_mode
        FROM simulation_runs
        WHERE legacy_report_id = ?
        """,
        ("legacy-report-1",),
    ).fetchone()
    assert simulation_run == ("legacy-report-1", "instagram_reels", "legacy_single_report")

    media_asset = verification.execute(
        """
        SELECT filename, mime_type, media_type
        FROM media_assets
        """
    ).fetchone()
    assert media_asset == ("legacy.mp4", "video/mp4", "short_video")

    run_target = verification.execute(
        """
        SELECT platform, media_type
        FROM run_targets
        """
    ).fetchone()
    assert run_target == ("instagram_reels", "short_video")

    verification.close()
