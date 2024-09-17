from flask import Flask, render_template, request, jsonify
from chatbot import chatbot
from weather_data import update_weather_data  # Import the weather update function

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    user_message = request.json.get("message")

    # Debugging: Print the incoming user message
    print(f"Received user message: {user_message}")

    if user_message:
        # Get the response from the ChatterBot instance
        bot_response = chatbot.get_response(user_message)

        # Debugging: Print the bot response
        print(f"Bot response: {bot_response.text}")

        # Return the bot's response directly without confidence check
        return jsonify({"response": bot_response.text})

    return jsonify({"response": "I didn't quite catch that. Could you try again?"})

# Call the function to update the weather data (this can be done once when the app starts)
update_weather_data()

if __name__ == "__main__":
    app.run(debug=True)
