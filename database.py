import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_NAME = "smartdispatch.db"

def init_db():
    db_exists = os.path.exists(DB_NAME)
    with sqlite3.connect(DB_NAME) as conn:
        with open("schema.sql") as f:
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

    if db_exists:
        print("Database schema verified successfully.")
    else:
        print("Database initialized successfully.")