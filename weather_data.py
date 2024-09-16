import requests
import sqlite3
from datetime import datetime
import schedule
import time

# Load API key from text file
def load_api_key(filename):
    with open(filename, 'r') as file:
        return file.read().strip()

OPENWEATHER_API_KEY = load_api_key('weather_api_key.txt')

# Create the SQLite database and table
def create_database():
    conn = sqlite3.connect('weather.db')
    cursor = conn.cursor()

    # Store the 7-day forecast, with separate entries for each day
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_forecast (
            city TEXT,
            country TEXT,
            date TEXT,
            temperature_day REAL,
            temperature_night REAL,
            description TEXT,
            humidity INTEGER,
            wind_speed REAL,
            PRIMARY KEY (city, country, date)
        )
    ''')
    conn.commit()
    conn.close()

# Fetch 7-day forecast from OpenWeather using lat, lon
def fetch_weather_data(lat, lon, city, country):
    url = f"http://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly,alerts&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        forecast_data = []
        for day in data['daily']:
            forecast_data.append({
                "city": city,
                "country": country,
                "date": datetime.fromtimestamp(day['dt']).strftime('%Y-%m-%d'),
                "temperature_day": day['temp']['day'],
                "temperature_night": day['temp']['night'],
                "description": day['weather'][0]['description'],
                "humidity": day['humidity'],
                "wind_speed": day['wind_speed']
            })
        return forecast_data
    else:
        print(f"Failed to fetch data for {city}. Error: {data['message']}")
        return None

# Save weather forecast data to the SQLite database
def save_to_database(forecast_data):
    conn = sqlite3.connect('weather.db')
    cursor = conn.cursor()

    for day_data in forecast_data:
        cursor.execute('''
            INSERT OR REPLACE INTO weather_forecast (city, country, date, temperature_day, temperature_night, description, humidity, wind_speed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (day_data['city'], day_data['country'], day_data['date'], day_data['temperature_day'], day_data['temperature_night'],
              day_data['description'], day_data['humidity'], day_data['wind_speed']))

    conn.commit()
    conn.close()

# Define cities with lat and lon directly
def load_cities():
    cities = [
        {"city": "Cumbria", "country": "UK", "lat": 54.4934, "lon": -3.1227},
        {"city": "Corfe Castle", "country": "UK", "lat": 50.635, "lon": -2.06},
        {"city": "The Cotswolds", "country": "UK", "lat": 51.799, "lon": -1.992},
        {"city": "Cambridge", "country": "UK", "lat": 52.2044, "lon": 0.1218},
        {"city": "Bristol", "country": "UK", "lat": 51.4545, "lon": -2.5879},
        {"city": "Oxford", "country": "UK", "lat": 51.7548, "lon": -1.2544},
        {"city": "Norwich", "country": "UK", "lat": 52.6309, "lon": 1.2961},
        {"city": "Stonehenge", "country": "UK", "lat": 51.1789, "lon": -1.8262},
        {"city": "Watergate Bay", "country": "UK", "lat": 50.4221, "lon": -5.0912},
        {"city": "Birmingham", "country": "UK", "lat": 52.4862, "lon": -1.8904},
        {"city": "Sydney", "country": "AU", "lat": -33.8688, "lon": 151.2093},
        {"city": "Melbourne", "country": "AU", "lat": -37.8136, "lon": 144.9631},
        {"city": "Brisbane", "country": "AU", "lat": -27.4698, "lon": 153.0251},
        {"city": "Perth", "country": "AU", "lat": -31.9505, "lon": 115.8605},
        {"city": "Adelaide", "country": "AU", "lat": -34.9285, "lon": 138.6007},
        {"city": "Hobart", "country": "AU", "lat": -42.8821, "lon": 147.3272},
        {"city": "Darwin", "country": "AU", "lat": -12.4634, "lon": 130.8456},
        {"city": "Canberra", "country": "AU", "lat": -35.2809, "lon": 149.13},
        {"city": "New York City", "country": "US", "lat": 40.7128, "lon": -74.006},
        {"city": "Tokyo", "country": "JP", "lat": 35.6824, "lon": 139.759},
        {"city": "Paris", "country": "FR", "lat": 48.8566, "lon": 2.3522},
        {"city": "Los Angeles", "country": "US", "lat": 34.0522, "lon": -118.2437},
        {"city": "Shanghai", "country": "CN", "lat": 31.2304, "lon": 121.4737},
        {"city": "Berlin", "country": "DE", "lat": 52.52, "lon": 13.405},
        {"city": "Toronto", "country": "CA", "lat": 43.651, "lon": -79.347},
        {"city": "Moscow", "country": "RU", "lat": 55.7558, "lon": 37.6173}
    ]
    return cities

cities = load_cities()
print(f"Loaded cities: {cities}")

# Main function to fetch and store weather data for all cities
def update_weather_data():
    print("Updating weather data...")
    cities = load_cities()
    for city_info in cities:
        forecast_data = fetch_weather_data(city_info['lat'], city_info['lon'], city_info['city'], city_info['country'])
        if forecast_data:
            save_to_database(forecast_data)
    print("Weather data updated successfully!")

# Schedule the weather update to run once a day
def schedule_daily_update():
    schedule.every().day.at("00:00").do(update_weather_data)

    while True:
        schedule.run_pending()
        time.sleep(1)

# Main entry point
if __name__ == "__main__":
    create_database()
    update_weather_data()  # Initial fetch
    schedule_daily_update()  # Schedule daily updates