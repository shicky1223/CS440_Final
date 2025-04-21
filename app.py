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
from dotenv import load_dotenv
import os

load_dotenv()
print("DB URI→", os.getenv("DATABASE_URL"))

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db    = SQLAlchemy(app)
bcrypt= Bcrypt(app)

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = "login"   # where @login_required redirects

class User(db.Model, UserMixin):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    pw_hash  = db.Column(db.String(128), nullable=False)

    def check_password(self, pw):
        return bcrypt.check_password_hash(self.pw_hash, pw)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# @app.before_first_request
# def create_tables():
#     db.create_all()


@app.route("/register", methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("chat_ui"))
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        if User.query.filter_by(username=u).first():
            flash("Username taken.", "warning")
        else:
            pw_hash = bcrypt.generate_password_hash(p).decode()
            user = User(username=u, pw_hash=pw_hash)
            db.session.add(user)
            db.session.commit()
            flash("Registered! Please log in.", "success")
            return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("chat_ui"))
    if request.method=="POST":
        u = request.form["username"]
        p = request.form["password"]
        user = User.query.filter_by(username=u).first()
        if user and user.check_password(p):
            login_user(user)
            return redirect(url_for("chat_ui"))
        flash("Invalid creds.", "danger")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def chat_ui():
    # main chat page
    return render_template("index.html", username=current_user.username)


@app.route("/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json()
    msg  = data.get("message", "").strip()
    if not msg:
        reply = "Say something when you’re ready!"
    else:
        reply = generate_response(
            msg,
            max_new_tokens=128,
            temperature=0.7,
        )
    return jsonify({"reply": reply})


if __name__ == "__main__":
    # this makes sure Flask has an application context so SQLAlchemy knows where to bind
    with app.app_context():
        db.create_all()
    app.run(debug=True)
