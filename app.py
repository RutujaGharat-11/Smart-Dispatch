import os
from flask import Flask
from flask_cors import CORS
from auth import auth_bp
from database import init_db

app = Flask(__name__)

init_db()

# Secret key for session
app.secret_key = os.environ.get("SECRET_KEY", "smartdispatch-secret-key")
app.config["SESSION_COOKIE_SAMESITE"] = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE", "False").lower() in ("true", "1", "yes")
app.config["SESSION_COOKIE_HTTPONLY"] = True

# Allow origins from environment variable, fallback to localhost:3000
frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
allowed_origins = [origin.strip() for origin in frontend_url.split(",")]

# Allow Next.js requests with credentials (cookies)
CORS(
    app,
    supports_credentials=True,
    origins=allowed_origins,
)

# Register routes
app.register_blueprint(auth_bp)

@app.route("/")
def home():
    return {"message": "SmartDispatch Backend Running"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)