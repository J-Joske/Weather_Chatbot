from flask import Flask, render_template, request, jsonify
from chatbot import chatbot
from weather_data import update_weather_data  # Import the weather update function
import re

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

        # Format the bot response by manually splitting into paragraphs
        formatted_response = format_weather_response(bot_response.text)

        # Return the formatted bot's response
        return jsonify({"response": formatted_response})

    return jsonify({"response": "I didn't quite catch that. Could you try again?"})


def format_weather_response(response_text):
    """
    Formats a long response into multiple HTML paragraphs, specifically for weather forecasts and recommendations.
    """
    # Split the response at each forecast (before the '📅 Date:' marker) and the recommendation section ('📝 Recommendations')
    weather_parts = re.split(r'(📅 Date:)', response_text)

    paragraphs = []

    # Re-add the '📅 Date:' marker to the start of each forecast, and wrap each in <p> tags
    for i in range(1, len(weather_parts), 2):
        date_marker = weather_parts[i]
        forecast = weather_parts[i + 1]
        paragraphs.append(f"<p>{date_marker}{forecast.strip()}</p>")

    # Handle the recommendations part if present (starts with '📝 Recommendations')
    recommendation_split = response_text.split('📝 Recommendations')

    if len(recommendation_split) > 1:
        recommendation_text = recommendation_split[1].strip()
        paragraphs.append(f"<p>📝 Recommendations{recommendation_text}</p>")

    # Join all the paragraphs into a single formatted response
    formatted_response = ''.join(paragraphs)
    return formatted_response


# Call the function to update the weather data (this can be done once when the app starts)
update_weather_data()

if __name__ == "__main__":
    app.run(debug=True)
