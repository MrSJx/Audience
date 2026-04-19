from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from uuid import uuid5, NAMESPACE_URL
from typing import Iterator

from app.core.config import settings


def initialize_database() -> None:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)

    with get_connection() as connection:
        _create_reports_table(connection)
        _create_simulation_tables(connection)
        _create_indexes(connection)
        _backfill_legacy_reports(connection)
        connection.commit()


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(settings.database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
    finally:
        connection.close()


def _create_reports_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
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


def _create_simulation_tables(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS media_assets (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            filename TEXT NOT NULL,
            mime_type TEXT NOT NULL,
            media_type TEXT NOT NULL,
            file_size_bytes INTEGER NOT NULL,
            duration_seconds REAL,
            source_path TEXT,
            sha256 TEXT,
            technical_metadata_json TEXT,
            analysis_snapshot_json TEXT
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS simulation_runs (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            schema_version TEXT NOT NULL,
            status TEXT NOT NULL,
            run_mode TEXT NOT NULL,
            target_platform TEXT NOT NULL,
            media_asset_id TEXT,
            legacy_report_id TEXT UNIQUE,
            runtime_model TEXT,
            request_json TEXT,
            combined_report_json TEXT,
            combined_scorecard_json TEXT,
            evidence_snapshot_json TEXT,
            FOREIGN KEY (media_asset_id) REFERENCES media_assets(id) ON DELETE SET NULL,
            FOREIGN KEY (legacy_report_id) REFERENCES reports(id) ON DELETE SET NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS run_targets (
            id TEXT PRIMARY KEY,
            simulation_run_id TEXT NOT NULL,
            platform TEXT NOT NULL,
            media_type TEXT NOT NULL,
            creator_goal TEXT,
            notes_json TEXT,
            FOREIGN KEY (simulation_run_id) REFERENCES simulation_runs(id) ON DELETE CASCADE
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS agent_profiles (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            label TEXT NOT NULL,
            preset_key TEXT,
            age_band TEXT NOT NULL,
            gender TEXT NOT NULL,
            experience_level TEXT NOT NULL,
            market_context TEXT,
            sensitive_lenses_json TEXT,
            custom_traits_json TEXT
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS agent_runs (
            id TEXT PRIMARY KEY,
            simulation_run_id TEXT NOT NULL,
            agent_profile_id TEXT NOT NULL,
            position_index INTEGER NOT NULL,
            status TEXT NOT NULL,
            prompt_json TEXT,
            raw_output_text TEXT,
            parsed_output_json TEXT,
            scorecard_json TEXT,
            created_at TEXT NOT NULL,
            completed_at TEXT,
            FOREIGN KEY (simulation_run_id) REFERENCES simulation_runs(id) ON DELETE CASCADE,
            FOREIGN KEY (agent_profile_id) REFERENCES agent_profiles(id) ON DELETE CASCADE
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS emotion_samples (
            id TEXT PRIMARY KEY,
            agent_run_id TEXT NOT NULL,
            timestamp_seconds REAL NOT NULL,
            happiness_score INTEGER,
            sadness_score INTEGER,
            laughter_score INTEGER,
            surprise_score INTEGER,
            confusion_score INTEGER,
            tension_score INTEGER,
            boredom_score INTEGER,
            notes_json TEXT,
            FOREIGN KEY (agent_run_id) REFERENCES agent_runs(id) ON DELETE CASCADE
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS timeline_events (
            id TEXT PRIMARY KEY,
            simulation_run_id TEXT NOT NULL,
            agent_run_id TEXT,
            timestamp_seconds REAL NOT NULL,
            event_type TEXT NOT NULL,
            event_label TEXT NOT NULL,
            polarity TEXT,
            intensity_score INTEGER,
            evidence_json TEXT,
            FOREIGN KEY (simulation_run_id) REFERENCES simulation_runs(id) ON DELETE CASCADE,
            FOREIGN KEY (agent_run_id) REFERENCES agent_runs(id) ON DELETE SET NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS consent_records (
            id TEXT PRIMARY KEY,
            simulation_run_id TEXT NOT NULL,
            consent_key TEXT NOT NULL,
            subject TEXT NOT NULL,
            granted INTEGER NOT NULL,
            disclosure_text TEXT NOT NULL,
            created_at TEXT NOT NULL,
            metadata_json TEXT,
            FOREIGN KEY (simulation_run_id) REFERENCES simulation_runs(id) ON DELETE CASCADE
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS report_exports (
            id TEXT PRIMARY KEY,
            simulation_run_id TEXT NOT NULL,
            export_format TEXT NOT NULL,
            export_path TEXT,
            created_at TEXT NOT NULL,
            metadata_json TEXT,
            FOREIGN KEY (simulation_run_id) REFERENCES simulation_runs(id) ON DELETE CASCADE
        )
        """
    )


def _create_indexes(connection: sqlite3.Connection) -> None:
    statements = [
        "CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports(created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_media_assets_created_at ON media_assets(created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_media_assets_sha256 ON media_assets(sha256)",
        "CREATE INDEX IF NOT EXISTS idx_simulation_runs_created_at ON simulation_runs(created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_simulation_runs_target_platform ON simulation_runs(target_platform)",
        "CREATE INDEX IF NOT EXISTS idx_simulation_runs_media_asset_id ON simulation_runs(media_asset_id)",
        "CREATE INDEX IF NOT EXISTS idx_run_targets_run_id ON run_targets(simulation_run_id)",
        "CREATE INDEX IF NOT EXISTS idx_agent_runs_run_id ON agent_runs(simulation_run_id)",
        "CREATE INDEX IF NOT EXISTS idx_agent_runs_profile_id ON agent_runs(agent_profile_id)",
        "CREATE INDEX IF NOT EXISTS idx_emotion_samples_agent_run_id ON emotion_samples(agent_run_id)",
        "CREATE INDEX IF NOT EXISTS idx_timeline_events_run_id ON timeline_events(simulation_run_id)",
        "CREATE INDEX IF NOT EXISTS idx_timeline_events_agent_run_id ON timeline_events(agent_run_id)",
        "CREATE INDEX IF NOT EXISTS idx_consent_records_run_id ON consent_records(simulation_run_id)",
        "CREATE INDEX IF NOT EXISTS idx_report_exports_run_id ON report_exports(simulation_run_id)",
    ]
    for statement in statements:
        connection.execute(statement)


def _backfill_legacy_reports(connection: sqlite3.Connection) -> None:
    rows = connection.execute(
        """
        SELECT
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
        FROM reports
        WHERE id NOT IN (
            SELECT legacy_report_id
            FROM simulation_runs
            WHERE legacy_report_id IS NOT NULL
        )
        ORDER BY created_at ASC
        """
    ).fetchall()

    for row in rows:
        media_asset_id = str(uuid5(NAMESPACE_URL, f"audience:legacy-media:{row['id']}"))
        simulation_run_id = str(uuid5(NAMESPACE_URL, f"audience:legacy-run:{row['id']}"))
        run_target_id = str(uuid5(NAMESPACE_URL, f"audience:legacy-target:{row['id']}"))

        connection.execute(
            """
            INSERT OR IGNORE INTO media_assets (
                id,
                created_at,
                filename,
                mime_type,
                media_type,
                file_size_bytes,
                duration_seconds,
                source_path,
                sha256,
                technical_metadata_json,
                analysis_snapshot_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                media_asset_id,
                row["created_at"],
                row["filename"],
                row["mime_type"],
                row["media_type"],
                row["file_size_bytes"],
                row["duration_seconds"],
                None,
                None,
                None,
                row["analysis_json"],
            ),
        )

        connection.execute(
            """
            INSERT OR IGNORE INTO simulation_runs (
                id,
                created_at,
                schema_version,
                status,
                run_mode,
                target_platform,
                media_asset_id,
                legacy_report_id,
                runtime_model,
                request_json,
                combined_report_json,
                combined_scorecard_json,
                evidence_snapshot_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                simulation_run_id,
                row["created_at"],
                "legacy_mvp_report_v1",
                "completed",
                "legacy_single_report",
                row["platform"],
                media_asset_id,
                row["id"],
                "llama3.2_or_heuristic_mvp",
                json.dumps(
                    {
                        "platform": row["platform"],
                        "media_type": row["media_type"],
                        "filename": row["filename"],
                        "mime_type": row["mime_type"],
                        "caption": row["caption"],
                        "file_size_bytes": row["file_size_bytes"],
                        "duration_seconds": row["duration_seconds"],
                    }
                ),
                row["report_json"],
                None,
                row["analysis_json"],
            ),
        )

        connection.execute(
            """
            INSERT OR IGNORE INTO run_targets (
                id,
                simulation_run_id,
                platform,
                media_type,
                creator_goal,
                notes_json
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                run_target_id,
                simulation_run_id,
                row["platform"],
                row["media_type"],
                None,
                json.dumps(
                    {
                        "source": "legacy_reports_backfill",
                        "legacy_report_id": row["id"],
                    }
                ),
            ),
        )
