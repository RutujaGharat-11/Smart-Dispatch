import os
import sqlite3
import traceback
from datetime import datetime, timezone
from flask import Blueprint, request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from scheduler.service import (
    get_pending_requests,
    get_free_resources,
    update_resource_status,
    apply_scheduler_assignments,
    complete_request_and_release_resource,
    get_activity_logs,
)
from scheduler.os_engine import (
    priority_scheduler,
    sjf_scheduler,
    greedy_scheduler,
    determine_highest_class,
    normalize_resource_type,
    get_class_of_service,
)

auth_bp = Blueprint("auth", __name__)

DB_PATH = os.environ.get(
    "DATABASE_PATH",
    os.path.join(os.path.dirname(__file__), "smartdispatch.db"),
)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Temporary admin user (later DB)
ADMIN_USER = {
    "username": "admin",
    "password": "admin123"
}

PRIORITY_TO_LEVEL = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}

LEVEL_TO_PRIORITY = {
    1: "Low",
    2: "Medium",
    3: "High",
    4: "Critical",
}


def _to_datetime(value):
    if not value:
        return None

    try:
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


def normalize_priority(priority_value):
    if isinstance(priority_value, int):
        return max(1, min(priority_value, 4))

    if isinstance(priority_value, str):
        stripped = priority_value.strip().lower()
        if stripped.isdigit():
            return max(1, min(int(stripped), 4))
        return PRIORITY_TO_LEVEL.get(stripped, 2)

    return 2


def resolve_current_user_id(conn):
    username = session.get("user")
    if not username:
        return None

    user = conn.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,),
    ).fetchone()

    if user:
        return user["id"]

    if username == ADMIN_USER["username"]:
        password_hash = generate_password_hash(ADMIN_USER["password"])
        conn.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            ("admin", "admin@smartdispatch.local", password_hash),
        )
        conn.commit()
        new_user = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            ("admin",),
        ).fetchone()
        if new_user:
            return new_user["id"]

    return None


def get_or_create_admin_user_id(conn, username):
    user = conn.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,),
    ).fetchone()

    if user:
        return user["id"]

    password_hash = generate_password_hash(ADMIN_USER["password"])
    cursor = conn.execute(
        "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
        (username, f"{username}@smartdispatch.local", password_hash, "ADMIN"),
    )
    conn.commit()
    return cursor.lastrowid


@auth_bp.route("/api/register", methods=["POST"])
def register():
    if session.get("role") == "ADMIN":
        return jsonify({"error": "Admins cannot create accounts through signup"}), 403

    data = request.get_json(silent=True) or {}

    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required"}), 400

    conn = get_db_connection()
    existing_user = conn.execute(
        "SELECT id FROM users WHERE username = ? OR email = ?",
        (username, email),
    ).fetchone()

    if existing_user:
        conn.close()
        return jsonify({"error": "User already exists"}), 409

    password_hash = generate_password_hash(password)
    conn.execute(
        "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
        (username, email, password_hash, "USER"),
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Registration successful"}), 201


@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    identifier = (data.get("username") or data.get("email") or "").strip()
    password = (data.get("password") or "").strip()
    selected_role = (data.get("selected_role") or "").strip().upper()

    if not identifier or not password or not selected_role:
        return jsonify({"error": "Username/email, password, and role are required"}), 400

    conn = get_db_connection()
    user = conn.execute(
        "SELECT id, username, password_hash, role FROM users WHERE username = ? OR lower(email) = ?",
        (identifier, identifier.lower()),
    ).fetchone()
    conn.close()

    if user and check_password_hash(user["password_hash"], password):
        user_db_role = (user["role"] or "").strip().upper()
        if user_db_role != selected_role:
            return jsonify({"error": "Invalid role selection"}), 403
            
        session["user"] = user["username"]
        session["user_id"] = user["id"]
        session["role"] = user_db_role
        return jsonify({"message": "Login successful", "role": user_db_role}), 200

    if identifier == ADMIN_USER["username"] and password == ADMIN_USER["password"]:
        if selected_role != "ADMIN":
            return jsonify({"error": "Invalid role selection"}), 403

        conn = get_db_connection()
        admin_user_id = get_or_create_admin_user_id(conn, identifier)
        conn.close()

        session["user"] = identifier
        session["user_id"] = admin_user_id
        session["role"] = "ADMIN"
        return jsonify({"message": "Login successful", "role": "ADMIN"}), 200

    return jsonify({"error": "Invalid credentials"}), 401


@auth_bp.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200


@auth_bp.route("/api/check-auth", methods=["GET"])
def check_auth():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"authenticated": False}), 401

    return jsonify({"authenticated": True, "role": session.get("role")}), 200


@auth_bp.route("/api/requests", methods=["GET"])
def get_requests():
    if session.get("role") != "ADMIN":
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT
            r.id,
            r.complaint_type,
            r.priority,
            r.estimated_time,
            r.description,
            r.location,
            r.status,
            r.created_at,
            u.username
        FROM requests r
        LEFT JOIN users u ON u.id = r.user_id
        ORDER BY r.created_at DESC, r.id DESC
        """
    ).fetchall()
    conn.close()

    requests_payload = []
    for row in rows:
        priority_level = row["priority"] if isinstance(row["priority"], int) else normalize_priority(row["priority"])
        execution_time = row["estimated_time"] if row["estimated_time"] is not None else 1
        resource_type = normalize_resource_type(row["complaint_type"])
        class_of_service = get_class_of_service(resource_type)
        waiting_time = _waiting_time_minutes(row["created_at"])

        requests_payload.append(
            {
                "id": row["id"],
                "request_id": f"REQ-{row['id']:03d}",
                "name": row["username"] or "Unknown",
                "type": row["complaint_type"],
                "priority": LEVEL_TO_PRIORITY.get(priority_level, "Medium"),
                "priority_level": priority_level,
                "execution_time": execution_time,
                "resource_type": resource_type,
                "class_of_service": class_of_service,
                "waiting_time": waiting_time,
                "location": row["location"] or "N/A",
                "description": row["description"] or "",
                "status": (row["status"] or "pending").strip().lower(),
                "created_at": row["created_at"],
            }
        )

    return jsonify({"requests": requests_payload}), 200


@auth_bp.route("/api/requests/pending", methods=["GET"])
def get_pending_requests_route():
    if session.get("role") != "ADMIN":
        return jsonify({"error": "Unauthorized"}), 403

    pending_requests = get_pending_requests()
    return jsonify({"requests": pending_requests}), 200


@auth_bp.route("/api/resources", methods=["GET"])
def get_resources():
    if session.get("role") != "ADMIN":
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT id, name, resource_type, status
        FROM resources
        ORDER BY id ASC
        """
    ).fetchall()
    conn.close()

    resources_payload = []
    for row in rows:
        raw_status = (row["status"] or "free").strip().lower()
        if raw_status not in {"free", "busy", "maintenance"}:
            raw_status = "maintenance"

        resources_payload.append(
            {
                "id": row["id"],
                "resource_id": f"RES-{row['id']:02d}",
                "name": row["name"],
                "resource_type": row["resource_type"],
                "type": row["resource_type"],
                "zone": "N/A",
                "status": raw_status,
            }
        )

    return jsonify({"resources": resources_payload}), 200


@auth_bp.route("/api/assignments", methods=["GET"])
def get_assignments():
    if session.get("role") != "ADMIN":
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT
            a.id,
            a.request_id,
            a.resource_id,
            a.algorithm_used,
            a.assigned_at,
            r.complaint_type,
            r.status AS request_status,
            res.status AS resource_status,
            res.name AS resource_name
        FROM assignments a
        LEFT JOIN requests r ON r.id = a.request_id
        LEFT JOIN resources res ON res.id = a.resource_id
        ORDER BY a.assigned_at DESC, a.id DESC
        """
    ).fetchall()
    conn.close()

    assignments_payload = []
    for row in rows:
        assignments_payload.append(
            {
                "id": row["id"],
                "request_id": row["request_id"],
                "resource_id": row["resource_id"],
                "algorithm": row["algorithm_used"] or "N/A",
                "algorithm_used": row["algorithm_used"] or "N/A",
                "assigned_at": row["assigned_at"],
                "request_type": row["complaint_type"] or "N/A",
                "resource_name": row["resource_name"] or "N/A",
                "request_status": (row["request_status"] or "pending").strip().lower(),
                "resource_status": (row["resource_status"] or "maintenance").strip().lower(),
            }
        )

    return jsonify({"assignments": assignments_payload}), 200


@auth_bp.route("/api/request", methods=["POST"])
def create_request():
    data = request.get_json(silent=True) or {}

    if session.get("role") != "USER":
        return jsonify({"error": "Unauthorized"}), 403

    complaint_type = (data.get("complaint_type") or "").strip()
    description = (data.get("description") or "").strip()
    location = (data.get("location") or "").strip()
    priority_level = normalize_priority(data.get("priority"))

    raw_estimated_time = data.get("estimated_time", 1)
    try:
        estimated_time = int(raw_estimated_time)
    except (TypeError, ValueError):
        estimated_time = 1
    if estimated_time <= 0:
        estimated_time = 1

    if not complaint_type or not description or not location:
        return jsonify({"error": "complaint_type, description, and location are required"}), 400

    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()

    cursor = conn.execute(
        """
        INSERT INTO requests (user_id, complaint_type, priority, estimated_time, description, location, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, complaint_type, priority_level, estimated_time, description, location, "pending"),
    )
    conn.commit()
    created_id = cursor.lastrowid
    conn.close()

    return jsonify({"message": "Request submitted", "id": created_id}), 201


@auth_bp.route("/api/run_scheduler", methods=["POST"])
def run_scheduler():
    if session.get("role") != "ADMIN":
        return jsonify({"error": "Unauthorized"}), 403

    try:
        payload = request.get_json(silent=True) or {}
        algorithm = (payload.get("algorithm") or "priority").strip().lower()

        scheduler_map = {
            "priority": priority_scheduler,
            "sjf": sjf_scheduler,
            "greedy": greedy_scheduler,
        }

        scheduler_fn = scheduler_map.get(algorithm)
        if scheduler_fn is None:
            return jsonify({"error": "Unsupported algorithm", "supported": list(scheduler_map.keys())}), 400

        pending_requests = get_pending_requests()
        free_resources = get_free_resources()
        selected_class = determine_highest_class(pending_requests)
        selected_class_request_count = len(
            [req for req in pending_requests if req.get("class_of_service") == selected_class]
        ) if selected_class else 0

        assignments = scheduler_fn(pending_requests, free_resources)

        if not assignments:
            return jsonify(
                {
                    "message": "No assignments generated",
                    "algorithm": algorithm,
                    "selected_class": selected_class,
                    "selected_class_request_count": selected_class_request_count,
                }
            ), 200

        result = apply_scheduler_assignments(assignments, algorithm)
        if not result.get("success"):
            return jsonify({"error": "Scheduler transaction failed", "details": result.get("error")}), 500

        return (
            jsonify(
                {
                    "message": "Success",
                    "algorithm": algorithm,
                    "selected_class": selected_class,
                    "selected_class_request_count": selected_class_request_count,
                    "assigned_count": result.get("assigned_count", 0),
                    "skipped_count": result.get("skipped_count", 0),
                }
            ),
            200,
        )
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Scheduler failed", "details": str(e)}), 500


@auth_bp.route("/api/requests/complete", methods=["POST"])
def complete_request():
    if session.get("role") != "ADMIN":
        return jsonify({"error": "Unauthorized"}), 403

    payload = request.get_json(silent=True) or {}
    request_value = payload.get("request_id")

    if request_value is None:
        return jsonify({"error": "request_id is required"}), 400

    request_id = None
    if isinstance(request_value, int):
        request_id = request_value
    elif isinstance(request_value, str):
        stripped = request_value.strip()
        if stripped.upper().startswith("REQ-"):
            numeric_part = stripped[4:]
            if numeric_part.isdigit():
                request_id = int(numeric_part)
        elif stripped.isdigit():
            request_id = int(stripped)

    if request_id is None:
        return jsonify({"error": "invalid request_id"}), 400

    result = complete_request_and_release_resource(request_id)
    if not result.get("success"):
        return jsonify({"error": "Unable to complete request", "details": result.get("error")}), 400

    return jsonify({"message": "Success", "request_id": request_id, "resource_id": result.get("resource_id")}), 200


@auth_bp.route("/api/logs", methods=["GET"])
def get_logs():
    if session.get("role") != "ADMIN":
        return jsonify({"error": "Unauthorized"}), 403

    logs = get_activity_logs()
    return jsonify({"logs": logs}), 200


@auth_bp.route("/api/resources/update-status", methods=["POST"])
def resources_update():
    if session.get("role") != "ADMIN":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json(silent=True) or {}
    resource_value = data.get("resource_id")
    status_value = (data.get("status") or "").strip().lower()

    if resource_value is None:
        return jsonify({"error": "resource_id is required"}), 400

    if status_value not in {"free", "busy", "maintenance"}:
        return jsonify({"error": "status must be free, busy, or maintenance"}), 400

    resource_id = None
    if isinstance(resource_value, int):
        resource_id = resource_value
    elif isinstance(resource_value, str):
        stripped = resource_value.strip()
        if stripped.upper().startswith("RES-"):
            numeric_part = stripped[4:]
            if numeric_part.isdigit():
                resource_id = int(numeric_part)
        elif stripped.isdigit():
            resource_id = int(stripped)

    if resource_id is None:
        return jsonify({"error": "invalid resource_id"}), 400

    updated_rows = update_resource_status(resource_id, status_value)

    if updated_rows == 0:
        return jsonify({"error": "resource not found"}), 404

    return jsonify({"message": "Success"}), 200


@auth_bp.route("/api/all-requests", methods=["GET"])
def all_requests():
    if session.get("role") != "ADMIN":
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify({"message": "Success"}), 200


@auth_bp.route("/api/my-requests", methods=["GET"])
def get_my_requests():
    if session.get("role") != "USER":
        return jsonify({"error": "Unauthorized"}), 403

    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT
            r.id,
            r.complaint_type,
            r.priority,
            r.description,
            r.location,
            r.status,
            r.created_at,
            u.username
        FROM requests r
        LEFT JOIN users u ON u.id = r.user_id
        WHERE r.user_id = ?
        ORDER BY r.created_at DESC, r.id DESC
        """,
        (user_id,)
    ).fetchall()
    conn.close()

    requests_payload = []
    for row in rows:
        priority_level = row["priority"] if isinstance(row["priority"], int) else normalize_priority(row["priority"])
        requests_payload.append(
            {
                "id": row["id"],
                "request_id": f"REQ-{row['id']:03d}",
                "name": row["username"] or "Unknown",
                "type": row["complaint_type"],
                "priority": LEVEL_TO_PRIORITY.get(priority_level, "Medium"),
                "priority_level": priority_level,
                "location": row["location"] or "N/A",
                "description": row["description"] or "",
                "status": (row["status"] or "pending").strip().lower(),
                "created_at": row["created_at"],
            }
        )

    return jsonify({"requests": requests_payload}), 200