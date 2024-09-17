# Weather Chatbot Flask Application - README

## Overview

This Flask-based web application integrates a chatbot, named **Misty**, that provides weather forecasts, weather-related advice, and activity recommendations for several cities. 
The chatbot uses the OpenWeather API to fetch the latest weather data and an SQLite database to store it. Users can interact with the chatbot to get responses about weather conditions in different cities,
and the bot will also offer activity suggestions based on the current weather.

## Features

- **Weather Forecasts:** Users can ask the chatbot for weather updates in supported cities.
- **Custom Weather Logic Adapter:** Handles weather-related queries, offering a variety of responses, such as current temperatures, forecasts, rain conditions, and hot/cold weather queries.
- **Activity Recommendations:** The chatbot suggests activities based on weather conditions (e.g., rainy days suggest indoor activities, sunny days suggest outdoor activities).
- **Data Storage:** Weather data is fetched daily from the OpenWeather API and stored in an SQLite database, reducing redundant API calls.
- **Flask Frontend:** A simple interface built using Flask for user interaction with the chatbot.

## Prerequisites

Before running the application, make sure you have the following installed:

- Python 3.7+
- Flask
- ChatterBot
- SQLite3
- Requests library
- OpenWeather API key

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/your-repo/weather-chatbot.git
cd weather-chatbot
```

### 2. Install Dependencies
Make sure all required libraries are installed by running:
```bash
pip install -r requirements.txt
```
> Note: Create a `requirements.txt` file containing:
```txt
Flask
chatterbot
chatterbot_corpus
requests
PyYAML
schedule
```

### 3. OpenWeather API Key
To use the OpenWeather API, create a `weather_api_key.txt` file and insert your OpenWeather API key in the file:
```txt
your_openweather_api_key
```

### 4. Create the SQLite Database
Run the following command to create the SQLite database for weather data:
```bash
python -c "import weather_data; weather_data.create_database()"
```

### 5. Fetch Initial Weather Data
Run the following command to populate the database with initial weather data for predefined cities:
```bash
python -c "import weather_data; weather_data.update_weather_data()"
```

### 6. Running the Application
Start the Flask app:
```bash
python app.py
```
The app will be running at `http://127.0.0.1:5000/`.

## Application Structure

- **app.py**: Main Flask application that handles routing, chatbot interactions, and response formatting.
- **weather_logic_adapter.py**: Custom logic adapter for handling weather-related queries in the chatbot.
- **chatbot.py**: Initializes the chatbot with logic adapters, including the custom weather logic, and trains it with predefined conversations.
- **weather_data.py**: Handles fetching and storing weather data from the OpenWeather API into the SQLite database.
- **weather.db**: SQLite database where weather forecasts are stored.
- **weather_corpus.yml**: Custom YAML file containing weather-related conversations for training the chatbot.

## Key Files

### app.py
Handles routes for the Flask web interface. Includes:
- `/`: Renders the main page of the app.
- `/get_response`: Receives user messages and returns a response from the chatbot.

### weather_logic_adapter.py
Contains the **WeatherLogicAdapter**, a custom ChatterBot adapter for processing weather-related queries. It connects to the SQLite database, retrieves weather data for a given city, and generates responses based on the query type (temperature, rain, etc.).

### chatbot.py
Initialises the chatbot and loads custom conversations from `weather_corpus.yml`. Includes training logic for weather-related responses.

### weather_data.py
Defines functions to:
- Fetch weather data from the OpenWeather API.
- Store the forecast in an SQLite database.
- Periodically update the weather data.

## Usage

1. **Ask for Weather**: Type a question like "What is the weather in Cambridge?" or "Is it raining in Bristol?".
2. **Get Recommendations**: Based on the weather conditions, Misty will also suggest activities suitable for the weather.
3. **Daily Updates**: The weather data is updated once daily using the OpenWeather API to ensure the chatbot has accurate information.

## Adding More Cities
You can expand the supported cities by adding new city names and their latitude/longitude coordinates in the `load_cities()` function in `weather_data.py`.

## Future Improvements
- Add more robust error handling for API failures.
- Expand chatbot training for more diverse weather-related queries.
- Integrate more granular weather data like hourly forecasts.
- Remove hardcoding of cities and either use a csv upload or create an admin front end.

Thanks for looking at my app!
