from flask import Flask, request, jsonify, render_template
from model import generate_response  # if using your AI generation function

app = Flask(__name__)

@app.route("/")
def index():
    # This will look for 'index.html' in the 'templates' folder.
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    if not user_message:
        reply = "I'm here to listen."
    else:
        reply = generate_response(user_message)
    return jsonify({'reply': reply})

# if __name__ == '__main__':
#     app.run(debug=True)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
