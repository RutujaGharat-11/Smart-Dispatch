import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_NAME = os.environ.get("DATABASE_PATH", "smartdispatch.db")


def should_run_one_time_cleanup():
    cleanup_enabled = os.environ.get("CLEAN_PREDEPLOY_TEST_DATA", "False").strip().lower() in (
        "true",
        "1",
        "yes",
        "on",
    )
    if not cleanup_enabled:
        return False, ""

    db_dir = os.path.dirname(DB_NAME) or "."
    marker_path = os.path.join(db_dir, ".cleanup_predeploy_done")
    return not os.path.exists(marker_path), marker_path


def run_one_time_cleanup(conn):
    cursor = conn.cursor()

    # Remove transactional test data from pre-deployment runs.
    cursor.execute("DELETE FROM assignments")
    cursor.execute("DELETE FROM requests")
    cursor.execute("DELETE FROM logs")

    # Keep admin users and remove regular user test accounts.
    cursor.execute("DELETE FROM users WHERE upper(coalesce(role, 'USER')) != 'ADMIN'")

    # Ensure all resources are reset to free state.
    cursor.execute("UPDATE resources SET status = 'free', current_request_id = NULL")
    conn.commit()


def seed_emergency_sample_requests(conn):
    cursor = conn.cursor()

    admin_row = cursor.execute(
        "SELECT id FROM users WHERE upper(coalesce(role, 'USER')) = 'ADMIN' ORDER BY id ASC LIMIT 1"
    ).fetchone()
    if not admin_row:
        return

    user_id = admin_row[0]

    sample_requests = [
        (
            "Police",
            3,
            2,
            "Sample police dispatch request",
            "Zone-Sample-Police",
        ),
        (
            "Fire Service",
            4,
            3,
            "Sample fire service emergency request",
            "Zone-Sample-Fire",
        ),
    ]

    for complaint_type, priority, estimated_time, description, location in sample_requests:
        exists = cursor.execute(
            """
            SELECT 1
            FROM requests
            WHERE lower(complaint_type) = lower(?) AND location = ?
            LIMIT 1
            """,
            (complaint_type, location),
        ).fetchone()

        if exists:
            continue

        cursor.execute(
            """
            INSERT INTO requests (user_id, complaint_type, priority, estimated_time, description, location, status)
            VALUES (?, ?, ?, ?, ?, ?, 'pending')
            """,
            (user_id, complaint_type, priority, estimated_time, description, location),
        )

    conn.commit()

def init_db():
    db_exists = os.path.exists(DB_NAME)
    with sqlite3.connect(DB_NAME) as conn:
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schema_path) as f:
            conn.executescript(f.read())
            
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'role' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'USER'")
            conn.commit()

        cursor.execute("PRAGMA table_info(requests)")
        request_columns = [col[1] for col in cursor.fetchall()]
        if "estimated_time" not in request_columns:
            cursor.execute("ALTER TABLE requests ADD COLUMN estimated_time INTEGER DEFAULT 1")
            conn.commit()

        cursor.execute("UPDATE requests SET estimated_time = 1 WHERE estimated_time IS NULL")
        conn.commit()
            
        # Insert 3 default admin accounts safely
        admins = [
            ("admin1", "admin1@smartdispatch.local", "admin123", "ADMIN"),
            ("admin2", "admin2@smartdispatch.local", "admin123", "ADMIN"),
            ("admin3", "admin3@smartdispatch.local", "admin123", "ADMIN"),
        ]
        
        for username, email, password, role in admins:
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if not cursor.fetchone():
                # Password must be hashed using generate_password_hash
                password_hash = generate_password_hash(password)
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                    (username, email, password_hash, role)
                )

        conn.commit()
        seed_emergency_sample_requests(conn)

        cursor.execute(
            """
            UPDATE resources
            SET status = CASE
                WHEN lower(status) IN ('free', 'busy', 'maintenance') THEN lower(status)
                ELSE 'maintenance'
            END
            """
        )
        conn.commit()

        should_cleanup, marker_path = should_run_one_time_cleanup()
        if should_cleanup:
            run_one_time_cleanup(conn)
            with open(marker_path, "w", encoding="utf-8") as marker_file:
                marker_file.write("cleanup completed\n")

    if db_exists:
        print("Database schema verified successfully.")
    else:
        print("Database initialized successfully.")