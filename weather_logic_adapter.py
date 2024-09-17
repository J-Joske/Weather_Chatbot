from chatterbot.logic import LogicAdapter
from chatterbot.conversation import Statement
import sqlite3
import re

class WeatherLogicAdapter(LogicAdapter):
    def __init__(self, chatbot, **kwargs):
        # Initialize the base LogicAdapter class
        super().__init__(chatbot, **kwargs)

    def can_process(self, statement):
        # Print the statement to debug if this method is called
        print(f"can_process called with statement: {statement.text}")
        # Check if the statement contains any weather-related keywords
        return re.search(r'\b(weather|forecast|raining|rain|hot|cold|temperature|sunny|wind)\b',
                         statement.text.lower()) is not None

    def process(self, statement, additional_response_selection_parameters=None):
        # Convert the statement text to lowercase for processing
        message = statement.text.lower()
        print(f"Processing message: {message}")

        # Extract query type and city from the message using regex
        query_type_match = re.search(r'\b(weather|forecast|raining|rain|hot|cold|temperature|sunny|wind)\b', message)
        city_match = re.search(r'(in|for)\s+([\w\s]+)\b', message)

        # Print debug information about the query type and city found
        if query_type_match:
            print(f"Query type found: {query_type_match.group(0)}")
        else:
            print("No query type found")

        if city_match:
            print(f"City found: {city_match.group(2)}")
        else:
            print("No city found")

        # Process the query if both query type and city are found
        if query_type_match and city_match:
            query_type = query_type_match.group(1)  # Get the query type
            city = city_match.group(2).strip().capitalize()  # Clean and capitalize the city name

            # Fetch weather data for the city
            weather_data = self.get_weather_data_for_city(city)

            if weather_data:
                # Generate a response based on the query type and weather data
                response_message = self.generate_response_for_query(query_type, weather_data, city)
                # Set high confidence for the response
                print(f"Weather response generated: {response_message}")
                return Statement(text=response_message, confidence=0.9)
            else:
                # Handle case where no weather data is found
                print(f"No weather data found for {city}")  # Log when no weather data is found
                return Statement(text=f"Sorry, I don't have weather data for {city}.", confidence=0.3)
        else:
            # Return a fallback response if query type or city is not found
            print("Returning fallback response.")
            return Statement(text="I'm not sure how to respond to that.", confidence=0.1)

    def generate_response_for_query(self, query_type, weather_data, city):
        # Generate a response based on the type of weather query
        if query_type in ["weather", "forecast", "temperature", "sunny", "wind"]:
            response_message = f"🌤️ Weather Forecast for {city}:\n\n"
            for day in weather_data:
                response_message += (
                    f"📅 Date: {day['date']}\n"
                    f"🌞 Day Temp: {day['temperature_day']}°C\n"
                    f"🌙 Night Temp: {day['temperature_night']}°C\n"
                    f"☁️ Condition: {day['description']}\n"
                    f"💧 Humidity: {day['humidity']}%\n"
                    f"💨 Wind Speed: {day['wind_speed']} m/s\n\n"
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

        return response_message

    def get_weather_data_for_city(self, city):
        try:
            # Connect to the SQLite database
            conn = sqlite3.connect('weather.db')
            cursor = conn.cursor()

            # Query the database for weather data for the given city
            cursor.execute('''
                SELECT * FROM weather_forecast WHERE LOWER(city) = LOWER(?) ORDER BY date ASC
            ''', (city,))
            data = cursor.fetchall()
            conn.close()

            print(f"Weather data fetched for {city}: {data}")

            if data:
                # Process the fetched data into a list of dictionaries
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
                # Handle case where no data is found for the city
                print(f"No data found for {city}")
                return None

        except sqlite3.Error as e:
            # Print any database errors encountered
            print(f"Database error: {e}")
            return None
