import os
import sqlite3


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "smartdispatch.db")


def _get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_pending_requests():
    conn = _get_db_connection()
    rows = conn.execute(
        """
        SELECT id, user_id, complaint_type, priority, description, location, status, created_at
        FROM requests
        WHERE lower(status) = 'pending'
        ORDER BY created_at ASC, id ASC
        """
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_free_resources():
    conn = _get_db_connection()
    rows = conn.execute(
        """
        SELECT id, name, resource_type, status, current_request_id
        FROM resources
        WHERE lower(status) = 'free'
        ORDER BY id ASC
        """
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


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
