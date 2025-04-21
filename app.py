# app.py (excerpt)
from dotenv import load_dotenv
load_dotenv()  # pip install python-dotenv
from flask import Flask, request, jsonify, render_template
from model import generate_response

app    = Flask(__name__)
# keep a tiny in‑memory history per session (for demo only)
chat_history: list[tuple[str,str]] = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data["message"].strip()
    if not user_msg:
        reply = "Say something whenever you’re ready!"
    else:
        # pass history into your generator
        reply = generate_response(

            user_msg,
            history=chat_history[-5:],      # last 5 turns max
            max_new_tokens=128,
            temperature=0.7
        )
        # record it
        chat_history.append((user_msg, reply))

    return jsonify({"reply": reply})


if __name__ == '__main__':
    app.run(debug=True)

# if __name__ == '__main__':
#     import os
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host='0.0.0.0', port=port, debug=False)
