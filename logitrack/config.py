import os
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_URL = os.getenv("WEATHER_API_URL", "https://api.open-meteo.com/v1/forecast")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")