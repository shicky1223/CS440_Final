from flask import (
    Flask, request, jsonify,
    render_template, redirect, url_for,
    flash, session
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin,
    login_user, login_required,
    logout_user, current_user
)
from flask_bcrypt import Bcrypt
from model import generate_response
from feature_extractor import extract_features_spacy
from classifier import classify_user
from dotenv import load_dotenv
import os
from word2number import w2n

# ─── Load environment variables ─────────────────────────────────────────────────
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# ─── Flask & Extensions ─────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL or "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db            = SQLAlchemy(app)
bcrypt        = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# ─── User Model ─────────────────────────────────────────────────────────────────
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

# ─── Questionnaire Fields ───────────────────────────────────────────────────────
PARAM_QUESTIONS = [
    ("Age",                     "How old are you?"),
    ("Sleep_Hours",             "On average, how many hours of sleep do you get per night?"),
    ("Physical_Activity_Hrs",   "How many hours per week do you spend exercising?"),
    ("Social_Support_Score",    "On a scale 0–10, how supported do you feel by friends/family?"),
    ("Depression_Score",        "On a scale 0–21, how would you rate your current depression symptoms?"),
    ("Stress_Level",            "On a scale 0–21, how stressed do you feel?"),
    ("Self_Esteem_Score",       "On a scale 0–10, how would you rate your self-esteem?"),
    ("Life_Satisfaction_Score", "On a scale 0–10, how satisfied are you with your life overall?"),
    ("Loneliness_Score",        "On a scale 0–10, how lonely do you feel?")
]

# ─── Routes ─────────────────────────────────────────────────────────────────────
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            u, p = data.get('username','').strip(), data.get('password','')
        else:
            u, p = request.form.get('username','').strip(), request.form.get('password','')
        if not u or not p:
            flash("Username and password required.", "warning")
            return render_template('register.html'), 400
        if User.query.filter_by(username=u).first():
            flash("Username already taken.", "danger")
            return render_template('register.html'), 409

        pw_hash = bcrypt.generate_password_hash(p).decode()
        user    = User(username=u, pw_hash=pw_hash)
        db.session.add(user)
        db.session.commit()

        if request.is_json:
            return jsonify(success=True), 201
        flash("Registered! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('setup'))
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            u, p = data.get('username','').strip(), data.get('password','')
        else:
            u, p = request.form.get('username','').strip(), request.form.get('password','')
        user = User.query.filter_by(username=u).first()
        if user and user.check_password(p):
            login_user(user)
            if request.is_json:
                return jsonify(success=True)
            return redirect(url_for('setup'))
        if request.is_json:
            return jsonify(error="Invalid credentials"), 401
        flash("Invalid credentials.", "danger")

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/setup', methods=['GET','POST'])
@login_required
def setup():
    # require full questionnaire each login
    if request.method == 'POST':
        answers = {}
        for key, _ in PARAM_QUESTIONS:
            raw = request.form.get(key, '').strip()
            try:
                val = float(raw)
            except:
                feats, _ = extract_features_spacy(raw)
                val = feats.get(key)
            answers[key] = val

        session['answers']       = answers
        # wrap in a 2-tuple so classify_user((features, confidences)) works
        session['anxiety_label'] = classify_user((answers, {}))
        return redirect(url_for('chat_ui'))

    return render_template('setup.html', fields=PARAM_QUESTIONS)


@app.route('/', methods=['GET'])
@login_required
def chat_ui():
    if 'answers' not in session:
        return redirect(url_for('setup'))
    return render_template(
        'index.html',
        username=current_user.username,
        anxiety=session.get('anxiety_label')
    )


@app.route('/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json() or {}
    msg  = data.get('message', '').strip()
    reply = generate_response(
        msg,
        max_new_tokens=128,
        temperature=0.7
    )
    return jsonify({'reply': reply})


# ─── Bootstrap & Run ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
