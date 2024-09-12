from flask import Flask, render_template, request, jsonify
from chatbot import chatbot

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    user_message = request.json.get("message")
    if user_message:
        bot_response = chatbot.get_response(user_message)
        return jsonify({"response": str(bot_response)})
    return jsonify({"response": "Sorry, I didn't understand that."})

if __name__ == "__main__":
    app.run(debug=True)
