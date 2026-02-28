import os
import sqlite3
from flask import Blueprint, request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "smartdispatch.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()

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
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (username, email, password_hash),
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
                "status": (row["status"] or "pending").title(),
                "created_at": row["created_at"],
            }
        )

    return jsonify({"requests": requests_payload}), 200


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
        status = "Available" if raw_status in {"free", "available"} else "Unavailable"
        resources_payload.append(
            {
                "id": row["id"],
                "resource_id": f"RES-{row['id']:02d}",
                "name": row["name"],
                "type": row["resource_type"],
                "zone": "N/A",
                "status": status,
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
                "algorithm_used": row["algorithm_used"] or "N/A",
                "assigned_at": row["assigned_at"],
                "request_type": row["complaint_type"] or "N/A",
                "resource_name": row["resource_name"] or "N/A",
            }
        )

    return jsonify({"assignments": assignments_payload}), 200


@auth_bp.route("/api/request", methods=["POST"])
def create_request():
    data = request.get_json(silent=True) or {}

    complaint_type = (data.get("complaint_type") or "").strip()
    description = (data.get("description") or "").strip()
    location = (data.get("location") or "").strip()
    priority_level = normalize_priority(data.get("priority"))

    if not complaint_type or not description or not location:
        return jsonify({"error": "complaint_type, description, and location are required"}), 400

    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()

    cursor = conn.execute(
        """
        INSERT INTO requests (user_id, complaint_type, priority, description, location, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, complaint_type, priority_level, description, location, "pending"),
    )
    conn.commit()
    created_id = cursor.lastrowid
    conn.close()

    return jsonify({"message": "Request submitted", "id": created_id}), 201


@auth_bp.route("/api/run_scheduler", methods=["POST", "GET"])
def run_scheduler():
    if session.get("role") != "ADMIN":
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify({"message": "Success"}), 200


@auth_bp.route("/api/resources/update", methods=["POST", "PUT"])
def resources_update():
    if session.get("role") != "ADMIN":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json(silent=True) or {}
    resource_value = data.get("resource_id")
    status_value = (data.get("status") or "").strip().lower()

    if resource_value is None:
        return jsonify({"error": "resource_id is required"}), 400

    if status_value not in {"available", "unavailable"}:
        return jsonify({"error": "status must be Available or Unavailable"}), 400

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

    db_status = "available" if status_value == "available" else "unavailable"

    conn = get_db_connection()
    cursor = conn.execute(
        "UPDATE resources SET status = ? WHERE id = ?",
        (db_status, resource_id),
    )
    conn.commit()
    updated_rows = cursor.rowcount
    conn.close()

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
                "status": (row["status"] or "pending").title(),
                "created_at": row["created_at"],
            }
        )

    return jsonify({"requests": requests_payload}), 200