from flask import (
    Flask, request, jsonify,
    render_template, redirect, url_for, flash
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin,
    login_user, login_required,
    logout_user, current_user
)
from flask_bcrypt import Bcrypt
from model import generate_response
from feature_extractor import extract_features
from classifier import classify_user
from dotenv import load_dotenv
import os

# ─── Load env vars ──────────────────────────────────────────────────────────────
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print("DB URI→", DATABASE_URL or "sqlite:///app.db")

# ─── Flask & Extensions ─────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")      # fallback for local dev
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL or "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# WSGI entrypoint for production
application = app

db     = SQLAlchemy(application)
bcrypt = Bcrypt(application)

login_manager = LoginManager(application)
login_manager.login_view = "login"

# ─── Models ─────────────────────────────────────────────────────────────────────
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    pw_hash  = db.Column(db.String(128), nullable=False)

    def check_password(self, pw):
        return bcrypt.check_password_hash(self.pw_hash, pw)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ─── Routes ─────────────────────────────────────────────────────────────────────
@app.route("/")
@login_required
def chat_ui():
    return render_template("index.html", username=current_user.username)

@app.route("/register", methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("chat_ui"))
    if request.method == "POST":
        u = request.form.get("username", "").strip()
        p = request.form.get("password", "")
        if User.query.filter_by(username=u).first():
            flash("Username taken.", "warning")
        else:
            pw_hash = bcrypt.generate_password_hash(p).decode()
            db.session.add(User(username=u, pw_hash=pw_hash))
            db.session.commit()
            flash("Registered! Please log in.", "success")
            return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("chat_ui"))
    if request.method == "POST":
        u = request.form.get("username", "").strip()
        p = request.form.get("password", "")
        user = User.query.filter_by(username=u).first()
        if user and user.check_password(p):
            login_user(user)
            return redirect(url_for("chat_ui"))
        flash("Invalid credentials.", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json() or {}
    msg  = data.get("message", "").strip()
    if not msg:
        reply = "Say something when you're ready!"
    else:
        # 1) LLM reply
        ai_reply = generate_response(msg, max_new_tokens=128, temperature=0.7)
        # 2) ML prediction
        feats = extract_features(msg)
        anxiety = classify_user(feats)
        # 3) combine
        reply = f"{ai_reply}\n\n*Predicted anxiety level:* {anxiety}"
    return jsonify({"reply": reply})

# ─── Bootstrap & Run ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Create tables before the first request
    with application.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 8000))
    application.run(host="0.0.0.0", port=port)  
