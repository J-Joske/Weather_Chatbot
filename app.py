from flask import Flask, render_template, request, jsonify
from chatbot import chatbot
import sqlite3
import re
from weather_data import update_weather_data  # Import the weather update function

app = Flask(__name__)


# Check if the user message is a weather-related query
def is_weather_query(message):
    # different types of weather queries
    return re.search(r'weather in (\w+)', message.lower()) is not None or \
           re.search(r'temperature in (\w+)', message.lower()) is not None or \
           re.search(r'forecast for (\w+)', message.lower()) is not None or \
           re.search(r'is it raining in (\w+)', message.lower()) is not None or \
           re.search(r'windy in (\w+)', message.lower()) is not None or \
           re.search(r'humidity in (\w+)', message.lower()) is not None



# Get weather data from the database for a city
def get_weather_data_for_city(city):
    conn = sqlite3.connect('weather.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM weather_forecast WHERE city = ? ORDER BY date ASC
    ''', (city,))
    data = cursor.fetchall()
    conn.close()

    if data:
        forecast = []
        for row in data:
            forecast.append({
                "date": row[2],
                "temperature_day": row[3],
                "temperature_night": row[4],
                "description": row[5],
                "humidity": row[6],
                "wind_speed": row[7]
            })
        return forecast
    else:
        return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_response", methods=["POST"])
def get_response():
    user_message = request.json.get("message")

    if user_message:
        # Check if the message is asking for weather information
        weather_match = re.search(r'\b(weather|forecast|raining|rain|hot|cold)\s+(for|in|will be)\s+([\w\s]+)\b',
                                  user_message.lower())
        if weather_match:
            query_type = weather_match.group(1)  # "weather", "forecast", "raining", "rain", "hot", or "cold"
            city = weather_match.group(3).strip().capitalize()  # Extract and clean the city name
            weather_data = get_weather_data_for_city(city)

            if weather_data:
                response_message = f"🌤️ Weather Forecast for {city}:\n\n"

                if query_type in ["weather", "forecast"]:
                    for day in weather_data:
                        response_message += (
                            f"📅 Date: {day['date']}\n"
                            f"🌞 Day Temp: {day['temperature_day']}°C\n\n"
                            f"🌙 Night Temp: {day['temperature_night']}°C\n\n"
                            f"☁️ Condition: {day['description']}\n"
                            f"💧 Humidity: {day['humidity']}%\n"
                            f"💨 Wind Speed: {day['wind_speed']} m/s\n\n\n\n\n\n\n"
                        )
                elif query_type in ["raining", "rain"]:
                    current_condition = weather_data[0]['description'].lower()
                    if 'rain' in current_condition:
                        response_message = f"🌧️ Yes, it is currently raining in {city}."
                    else:
                        response_message = f"☀️ No, it is not raining in {city} right now."
                elif query_type == "hot":
                    current_temp = weather_data[0]['temperature_day']
                    if current_temp > 30:
                        response_message = f"🔥 Yes, it is quite hot in {city} right now with a temperature of {current_temp}°C."
                    else:
                        response_message = f"🌡️ No, it is not very hot in {city} right now with a temperature of {current_temp}°C."
                elif query_type == "cold":
                    current_temp = weather_data[0]['temperature_day']
                    if current_temp < 20:
                        response_message = f"❄️ Yes, it is quite cold in {city} right now with a temperature of {current_temp}°C."
                    else:
                        response_message = f"🌡️ No, it is not very cold in {city} right now with a temperature of {current_temp}°C."

                return jsonify({"response": response_message})
            else:
                return jsonify({"response": f"Sorry, I don't have weather data for {city}."})

        # Default to ChatterBot response if it's not a weather query
        bot_response = chatbot.get_response(user_message)

        # If the bot's confidence is below a threshold, return a fallback response
        if bot_response.confidence < 0.4:
            return jsonify(
                {"response": "Sorry, I don't know how to answer that. I can only answer questions about the weather. "
                             "Can you please rephrase or ask something else?"})
        else:
            return jsonify({"response": str(bot_response)})

    return jsonify({"response": "I didn't quite catch that. Could you try again?"})


# Call the function to update the weather data (this can be done once when the app starts)
update_weather_data()

if __name__ == "__main__":
    app.run(debug=True)
