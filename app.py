from flask import Flask
from flask_cors import CORS
from auth import auth_bp
from database import init_db

app = Flask(__name__)

init_db()

# Secret key for session
app.secret_key = "smartdispatch-secret-key"
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_HTTPONLY"] = True

# Allow Next.js (port 3000)
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:3000"],
)

# Register routes
app.register_blueprint(auth_bp)

@app.route("/")
def home():
    return {"message": "SmartDispatch Backend Running"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)