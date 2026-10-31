from __future__ import annotations

import os
import secrets
import sqlite3
from datetime import datetime, timezone
from typing import Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "human_rights.db"))


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row else None


def create_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reference TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                email TEXT NOT NULL DEFAULT '',
                phone TEXT NOT NULL DEFAULT '',
                location TEXT NOT NULL DEFAULT '',
                issue TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL DEFAULT 'Medium',
                status TEXT NOT NULL DEFAULT 'Open',
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_cases_reference
            ON cases(reference)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_cases_status
            ON cases(status)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_cases_category
            ON cases(category)
            """
        )


def generate_reference() -> str:
    date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
    random_part = secrets.token_hex(3).upper()
    return f"HRA-{date_part}-{random_part}"


def create_case(
    *,
    name: str,
    email: str,
    phone: str,
    location: str,
    description: str,
    category: str,
    issue: str,
    priority: str,
) -> dict[str, Any]:
    created_at = utc_now()

    with get_connection() as connection:
        reference = generate_reference()

        while connection.execute(
            "SELECT 1 FROM cases WHERE reference = ?",
            (reference,),
        ).fetchone():
            reference = generate_reference()

        cursor = connection.execute(
            """
            INSERT INTO cases (
                reference,
                name,
                email,
                phone,
                location,
                issue,
                description,
                category,
                priority,
                status,
                notes,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Open', '', ?, ?)
            """,
            (
                reference,
                name,
                email,
                phone,
                location,
                issue,
                description,
                category,
                priority,
                created_at,
                created_at,
            ),
        )

        case_id = cursor.lastrowid

    case = get_case(case_id)

    if case is None:
        raise RuntimeError("The case was saved but could not be retrieved.")

    return case


def get_case(case_id: int) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM cases WHERE id = ?",
            (case_id,),
        ).fetchone()

    return row_to_dict(row)


def get_cases(
    *,
    search: str = "",
    status: str = "",
    category: str = "",
) -> list[dict[str, Any]]:
    query = "SELECT * FROM cases WHERE 1 = 1"
    parameters: list[Any] = []

    if search:
        query += """
            AND (
                reference LIKE ?
                OR name LIKE ?
                OR issue LIKE ?
                OR description LIKE ?
                OR location LIKE ?
            )
        """
        term = f"%{search}%"
        parameters.extend([term, term, term, term, term])

    if status:
        query += " AND status = ?"
        parameters.append(status)

    if category:
        query += " AND category = ?"
        parameters.append(category)

    query += " ORDER BY created_at DESC"

    with get_connection() as connection:
        rows = connection.execute(query, parameters).fetchall()

    return [dict(row) for row in rows]


def update_case(
    *,
    case_id: int,
    status: str | None = None,
    priority: str | None = None,
    notes: str | None = None,
) -> dict[str, Any] | None:
    fields: list[str] = []
    parameters: list[Any] = []

    if status is not None:
        fields.append("status = ?")
        parameters.append(status)

    if priority is not None:
        fields.append("priority = ?")
        parameters.append(priority)

    if notes is not None:
        fields.append("notes = ?")
        parameters.append(notes)

    if not fields:
        return get_case(case_id)

    fields.append("updated_at = ?")
    parameters.append(utc_now())
    parameters.append(case_id)

    with get_connection() as connection:
        cursor = connection.execute(
            f"""
            UPDATE cases
            SET {", ".join(fields)}
            WHERE id = ?
            """,
            parameters,
        )

        if cursor.rowcount == 0:
            return None

    return get_case(case_id)


def delete_case(case_id: int) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM cases WHERE id = ?",
            (case_id,),
        )

    return cursor.rowcount > 0


def get_dashboard_statistics() -> dict[str, Any]:
    with get_connection() as connection:
        total = connection.execute(
            "SELECT COUNT(*) FROM cases"
        ).fetchone()[0]

        open_cases = connection.execute(
            """
            SELECT COUNT(*)
            FROM cases
            WHERE status IN ('Open', 'In Review', 'Referred')
            """
        ).fetchone()[0]

        resolved = connection.execute(
            """
            SELECT COUNT(*)
            FROM cases
            WHERE status IN ('Resolved', 'Closed')
            """
        ).fetchone()[0]

        critical = connection.execute(
            """
            SELECT COUNT(*)
            FROM cases
            WHERE priority = 'Critical'
            """
        ).fetchone()[0]

        categories = connection.execute(
            """
            SELECT category, COUNT(*) AS count
            FROM cases
            GROUP BY category
            ORDER BY count DESC, category ASC
            """
        ).fetchall()

    return {
        "total": total,
        "open": open_cases,
        "resolved": resolved,
        "critical": critical,
        "categories": [dict(row) for row in categories],
    }
