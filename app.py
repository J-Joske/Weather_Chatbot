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

        # If the bot's confidence is below a threshold (e.g., 0.5), return a fallback response
        if bot_response.confidence < 0.5:
            return jsonify(
                {"response": "Sorry, I don't know how to answer that. I can only answer questions about the weather. "
                             "Can you please rephrase or ask something else?"})
        else:
            return jsonify({"response": str(bot_response)})

    return jsonify({"response": "I didn't quite catch that. Could you try again?"})


if __name__ == "__main__":
    app.run(debug=True)
