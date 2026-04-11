import os
import sqlite3
from datetime import datetime, timezone
from scheduler.os_engine import normalize_resource_type, get_class_of_service


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "smartdispatch.db")


def _normalize_text(value):
    return str(value or "").strip().lower()


def _to_datetime(value):
    if not value:
        return None

    try:
        # SQLite stores timestamps like "YYYY-MM-DD HH:MM:SS".
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _waiting_time_minutes(created_at):
    created_dt = _to_datetime(created_at)
    if created_dt is None:
        return 0

    delta_seconds = (datetime.now(timezone.utc) - created_dt).total_seconds()
    return max(0, int(delta_seconds // 60))


def _get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_pending_requests():
    conn = _get_db_connection()
    rows = conn.execute(
        """
        SELECT id, complaint_type, priority, estimated_time, created_at
        FROM requests
        WHERE lower(status) = 'pending'
        ORDER BY created_at ASC, id ASC
        """
    ).fetchall()
    conn.close()

    normalized_requests = []
    for row in rows:
        request_id = row["id"]

        try:
            priority_value = int(row["priority"])
        except (TypeError, ValueError):
            priority_value = 0

        raw_estimated_time = row["estimated_time"]
        if raw_estimated_time is None:
            estimated_time_value = 1
        else:
            try:
                estimated_time_value = float(raw_estimated_time)
            except (TypeError, ValueError):
                estimated_time_value = 1

        complaint_type = row["complaint_type"]
        resource_type = normalize_resource_type(complaint_type)
        class_of_service = get_class_of_service(resource_type)
        waiting_time = _waiting_time_minutes(row["created_at"])

        # Keep compatibility aliases while returning the normalized scheduler shape.
        normalized_requests.append(
            {
                "request_id": request_id,
                "priority": priority_value,
                "type": complaint_type,
                "estimated_time": estimated_time_value,
                "execution_time": estimated_time_value,
                "resource_type": resource_type,
                "class_of_service": class_of_service,
                "waiting_time": waiting_time,
                "id": request_id,
                "complaint_type": complaint_type,
                "created_at": row["created_at"],
            }
        )

    return normalized_requests


def get_free_resources():
    conn = _get_db_connection()
    rows = conn.execute(
        """
        SELECT id, resource_type, status
        FROM resources
        WHERE lower(status) = 'free'
        ORDER BY id ASC
        """
    ).fetchall()
    conn.close()

    normalized_resources = []
    for row in rows:
        raw_status = str(row["status"] or "").strip().lower()
        if raw_status != "free":
            continue

        resource_id = row["id"]
        resource_type = row["resource_type"]

        # Keep compatibility aliases while returning normalized resource fields.
        normalized_resources.append(
            {
                "resource_id": resource_id,
                "type": resource_type,
                "status": "free",
                "id": resource_id,
                "resource_type": resource_type,
            }
        )

    return normalized_resources


def update_request_status(request_id, status):
    conn = _get_db_connection()
    cursor = conn.execute(
        "UPDATE requests SET status = ? WHERE id = ?",
        (status, request_id),
    )
    conn.commit()
    updated_rows = cursor.rowcount
    conn.close()
    return updated_rows


def update_resource_status(resource_id, status):
    conn = _get_db_connection()
    cursor = conn.execute(
        "UPDATE resources SET status = ? WHERE id = ?",
        (status, resource_id),
    )
    conn.commit()
    updated_rows = cursor.rowcount
    conn.close()
    return updated_rows


def insert_assignment(request_id, resource_id, algorithm_name):
    conn = _get_db_connection()
    cursor = conn.execute(
        """
        INSERT INTO assignments (request_id, resource_id, algorithm_used)
        VALUES (?, ?, ?)
        """,
        (request_id, resource_id, algorithm_name),
    )
    conn.commit()
    assignment_id = cursor.lastrowid
    conn.close()
    return assignment_id


def insert_log(message):
    conn = _get_db_connection()
    cursor = conn.execute(
        "INSERT INTO logs (message) VALUES (?)",
        (message,),
    )
    conn.commit()
    log_id = cursor.lastrowid
    conn.close()
    return log_id


def get_activity_logs(limit=200):
    conn = _get_db_connection()
    rows = conn.execute(
        """
        SELECT id, message, created_at
        FROM logs
        ORDER BY created_at DESC, id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def apply_scheduler_assignments(assignments, algorithm_name):
    """Apply scheduler results atomically with duplicate protection."""
    if not assignments:
        return {"success": True, "assigned_count": 0, "skipped_count": 0}

    conn = _get_db_connection()
    used_resources = set()
    used_requests = set()
    assigned_count = 0
    skipped_count = 0

    try:
        conn.execute("BEGIN")

        for assignment in assignments:
            request_id = assignment.get("request_id")
            resource_id = assignment.get("resource_id")

            if request_id is None or resource_id is None:
                skipped_count += 1
                continue

            if request_id in used_requests or resource_id in used_resources:
                skipped_count += 1
                continue

            request_cursor = conn.execute(
                "UPDATE requests SET status = ? WHERE id = ? AND lower(status) = 'pending'",
                ("scheduled", request_id),
            )
            if request_cursor.rowcount != 1:
                raise RuntimeError(f"Failed to schedule request {request_id}")

            resource_cursor = conn.execute(
                "UPDATE resources SET status = ? WHERE id = ? AND lower(status) = 'free'",
                ("busy", resource_id),
            )
            if resource_cursor.rowcount != 1:
                raise RuntimeError(f"Failed to reserve resource {resource_id}")

            conn.execute(
                """
                INSERT INTO assignments (request_id, resource_id, algorithm_used)
                VALUES (?, ?, ?)
                """,
                (request_id, resource_id, algorithm_name),
            )
            conn.execute(
                "INSERT INTO logs (message) VALUES (?)",
                (f"Assigned request {request_id} to resource {resource_id} using {algorithm_name}",),
            )

            used_requests.add(request_id)
            used_resources.add(resource_id)
            assigned_count += 1

        conn.commit()
        return {
            "success": True,
            "assigned_count": assigned_count,
            "skipped_count": skipped_count,
        }
    except Exception as exc:
        conn.rollback()
        return {
            "success": False,
            "error": str(exc),
            "assigned_count": 0,
            "skipped_count": skipped_count,
        }
    finally:
        conn.close()


def complete_request_and_release_resource(request_id):
    """Mark request as completed, free assigned resource, and write an activity log atomically."""
    conn = _get_db_connection()

    try:
        conn.execute("BEGIN")

        assignment = conn.execute(
            """
            SELECT resource_id
            FROM assignments
            WHERE request_id = ?
            ORDER BY assigned_at DESC, id DESC
            LIMIT 1
            """,
            (request_id,),
        ).fetchone()

        if not assignment:
            raise RuntimeError(f"No assignment found for request {request_id}")

        resource_id = assignment["resource_id"]

        request_cursor = conn.execute(
            "UPDATE requests SET status = ? WHERE id = ? AND lower(status) = 'scheduled'",
            ("completed", request_id),
        )
        if request_cursor.rowcount != 1:
            raise RuntimeError(f"Request {request_id} is not in scheduled state")

        resource_cursor = conn.execute(
            "UPDATE resources SET status = ? WHERE id = ?",
            ("free", resource_id),
        )
        if resource_cursor.rowcount != 1:
            raise RuntimeError(f"Resource {resource_id} not found")

        conn.execute(
            "INSERT INTO logs (message) VALUES (?)",
            (f"Request {request_id} completed. Resource {resource_id} freed.",),
        )

        conn.commit()
        return {"success": True, "request_id": request_id, "resource_id": resource_id}
    except Exception as exc:
        conn.rollback()
        return {"success": False, "error": str(exc)}
    finally:
        conn.close()
