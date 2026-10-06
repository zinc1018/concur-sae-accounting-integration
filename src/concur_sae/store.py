import sqlite3
from datetime import datetime


def initialize(db_path: str) -> None:
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS file_manifest (
                checksum TEXT PRIMARY KEY,
                file_name TEXT NOT NULL,
                status TEXT NOT NULL,
                processed_at TEXT NOT NULL,
                message TEXT NOT NULL
            )
            """
        )


def find_success(db_path: str, checksum: str) -> tuple[str, str] | None:
    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            "SELECT status, message FROM file_manifest WHERE checksum = ? AND status = 'COMPLETED'",
            (checksum,),
        ).fetchone()
    return row if row else None


def record_result(db_path: str, checksum: str, file_name: str, status: str, message: str) -> None:
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO file_manifest
            (checksum, file_name, status, processed_at, message)
            VALUES (?, ?, ?, ?, ?)
            """,
            (checksum, file_name, status, datetime.now().isoformat(timespec="seconds"), message),
        )
