from chatterbot.logic import LogicAdapter
from chatterbot.conversation import Statement
import sqlite3
import re

class WeatherLogicAdapter(LogicAdapter):
    def __init__(self, chatbot, **kwargs):
        # Initialise the custom logic adapter
        super().__init__(chatbot, **kwargs)

    def can_process(self, statement):
        # Check if the input message contains any weather-related keywords
        print(f"can_process called with statement: {statement.text}")
        return re.search(r'\b(weather|forecast|raining|rain|hot|cold|temperature|sunny|wind)\b',
                         statement.text.lower()) is not None

    def process(self, statement, additional_response_selection_parameters=None):
        # Process the input message if it contains weather keywords
        message = statement.text.lower()
        print(f"Processing message: {message}")

        # Match weather-related keywords in the user's message
        query_type_match = re.search(r'\b(weather|forecast|raining|rain|hot|cold|temperature|sunny|wind)\b',
                                     message)
        # Match the city mentioned in the user's message
        city_match = re.search(r'(in|for)\s+([\w\s]+)\b', message)

        # print information for potentially error handling
        if query_type_match:
            print(f"Query type found: {query_type_match.group(0)}")
        else:
            print("No query type found")

        if city_match:
            print(f"City found: {city_match.group(2)}")
        else:
            print("No city found")

        # If both query type and city are found, generate a weather response
        if query_type_match and city_match:
            query_type = query_type_match.group(1)
            city = city_match.group(2).strip().capitalize()

            # get weather data for the city from the SQLite database
            weather_data = self.get_weather_data_for_city(city)

            if weather_data:
                # Generate a response based on the query type and weather data
                response_message = self.generate_response_for_query(query_type, weather_data, city)
                print(f"Weather response generated: {response_message}")
                return Statement(text=response_message, confidence=0.9)
            else:
                # If no weather data is found, return a low-confidence response
                print(f"No weather data found for {city}")
                return Statement(text=f"Sorry, I don't have weather data for {city}.", confidence=0.3)
        else:
            # Return a fallback response if no city or query type is found
            print("Returning fallback response.")
            return Statement(text="I'm not sure how to respond to that.", confidence=0.1)

    def generate_response_for_query(self, query_type, weather_data, city):
        # Generate the appropriate response based on the query type and weather data
        if query_type in ["weather", "forecast", "temperature", "sunny", "wind"]:
            # Generate a detailed weather forecast response
            response_message = f"🌤️ Weather Forecast for {city}:\n\n"
            for day in weather_data:
                response_message += (
                    f"📅 Date: {day['date']}\n"
                    f"🌞 Day Temp: {day['temperature_day']}°C\n"
                    f"🌙 Night Temp: {day['temperature_night']}°C\n"
                    f"☁️ Condition: {day['description']}\n"
                    f"💧 Humidity: {day['humidity']}%\n"
                    f"💨 Wind Speed: {day['wind_speed']} m/s.\n\n"
                )
        elif query_type in ["raining", "rain"]:
            # Check if it is currently raining in the city
            current_condition = weather_data[0]['description'].lower()
            if 'rain' in current_condition:
                response_message = f"🌧️ Yes, it is currently raining in {city}."
            else:
                response_message = f"☀️ No, it is not raining in {city} right now."
        elif query_type == "hot":
            # Check if the temperature is above 30°C
            current_temp = weather_data[0]['temperature_day']
            if current_temp > 30:
                response_message = (f"🔥 Yes, it is quite hot in {city} right now with a temperature of {current_temp}°C. "
                                    f"Make sure you wear loose clothing.")
            else:
                response_message = f"🌡️ No, it is not very hot in {city} right now with a temperature of {current_temp}°C."
        elif query_type == "cold":
            # Check if the temperature is below 20°C
            current_temp = weather_data[0]['temperature_day']
            if current_temp < 20:
                response_message = (f"❄️ Yes, it is quite cold in {city} right now with a temperature of {current_temp}°C. "
                                    f"Make sure you wear warm clothing!")
            else:
                response_message = f"🌡️ No, it is not very cold in {city} right now with a temperature of {current_temp}°C."

        # Add activity recommendations based on the weather
        recommendations = self.get_recommendations_based_on_weather(weather_data[0])
        response_message += f"\n📝 Recommendations for {city}:\n{recommendations}"

        return response_message

    def get_recommendations_based_on_weather(self, current_weather):
        # Provide activity recommendations based on current weather conditions
        condition = current_weather['description'].lower()
        temp_day = current_weather['temperature_day']
        recommendations = ""

        if 'rain' in condition:
            # Suggest indoor activities if it's raining
            recommendations = ("It's raining! 🌧️ How about visiting a museum, watching a movie indoors, or reading a "
                               "good book at a cozy cafe?")
        elif 'sunny' in condition or temp_day >= 25:
            # Suggest outdoor activities if it's sunny or warm
            recommendations = ("It's sunny and warm! ☀️ Perfect for outdoor activities like going to the beach, "
                               "hiking, or having a picnic.")
        elif temp_day < 15:
            # Suggest indoor activities if it's cold
            recommendations = ("It's a bit chilly! 🧥 Maybe visit an indoor gallery, try a hot chocolate at a cafe, "
                               "or go to the cinema.")
        elif 'wind' in condition:
            # Suggest indoor activities if it's windy
            recommendations = ("It's quite windy! 🌬️ Indoor activities such as visiting a museum or staying at home "
                               "with a good book are great options.")
        else:
            # Suggest moderate outdoor activities for normal weather
            recommendations = ("It's a moderate day! 😊 Why not go for a walk, visit a local market, or enjoy a meal "
                               "outdoors?")

        return recommendations

    def get_weather_data_for_city(self, city):
        # Retrieve weather data from the SQLite database for the specified city
        try:
            conn = sqlite3.connect('weather.db')  # Connect to the SQLite database
            cursor = conn.cursor()

            # Query the database for weather data for the specified city
            cursor.execute('''
                SELECT * FROM weather_forecast WHERE LOWER(city) = LOWER(?) ORDER BY date ASC
            ''', (city,))
            data = cursor.fetchall()  # Fetch all rows of the query result
            conn.close()  # Close the database connection

            print(f"Weather data fetched for {city}: {data}")

            if data:
                # Process and format the weather data into a list of dictionaries
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
                # Return None if no weather data is found for the city
                print(f"No data found for {city}")
                return None

        except sqlite3.Error as e:
            # Handle any database errors
            print(f"Database error: {e}")
            return None
