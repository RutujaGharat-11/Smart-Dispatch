import os
from flask import Flask
from flask_cors import CORS
from auth import auth_bp
from database import init_db

app = Flask(__name__)

init_db()


def parse_bool_env(value, default):
    if value is None:
        return default
    return value.strip().lower() in ("true", "1", "yes", "on")

# Secret key for session
app.secret_key = os.environ.get("SECRET_KEY", "smartdispatch-secret-key")
app.config["SESSION_COOKIE_HTTPONLY"] = True

# Allow origins from environment variable.
# FRONTEND_URL can be comma-separated values.
frontend_url = os.environ.get("FRONTEND_URL", "")
allowed_origins = []

if frontend_url:
    for origin in frontend_url.split(","):
        cleaned_origin = origin.strip()
        if not cleaned_origin:
            continue
        if "your-frontend-url" in cleaned_origin:
            continue
        allowed_origins.append(cleaned_origin)

if not allowed_origins:
    allowed_origins = ["http://localhost:3000", r"https://.*\.vercel\.app"]

session_cookie_secure = parse_bool_env(
    os.environ.get("SESSION_COOKIE_SECURE"),
    default=any(origin.startswith("https://") or "vercel" in origin for origin in allowed_origins),
)
app.config["SESSION_COOKIE_SECURE"] = session_cookie_secure

session_cookie_samesite = os.environ.get("SESSION_COOKIE_SAMESITE")
if session_cookie_samesite:
    app.config["SESSION_COOKIE_SAMESITE"] = session_cookie_samesite
else:
    app.config["SESSION_COOKIE_SAMESITE"] = "None" if session_cookie_secure else "Lax"

# Allow Next.js requests with credentials (cookies)
CORS(
    app,
    supports_credentials=True,
    origins=allowed_origins,
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Register routes
app.register_blueprint(auth_bp)

@app.route("/")
def home():
    return {"message": "SmartDispatch Backend Running"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)