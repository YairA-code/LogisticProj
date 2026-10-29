import requests
import time
import logging
from typing import Dict, Any

logger = logging.getLogger("logitrack.api_client")


class WeatherApiClient:
    def __init__(self, timeout: float = 5.0, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    def fetch_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": "true"
        }

        attempt = 0
        while attempt < self.max_retries:
            try:
                response = requests.get(self.base_url, params=params, timeout=self.timeout)
                response.raise_for_status()
                return response.json()

            except (requests.Timeout, requests.ConnectionError) as e:
                attempt += 1
                logger.warning(f"Connection failed. Attempt {attempt} of {self.max_retries}")
                if attempt == self.max_retries:
                    logger.error("Max retries reached. API unavailable.")
                    raise ConnectionError("Weather API unavailable") from e
                time.sleep(1.0)

            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP Error: {e}")
                raise

            except ValueError as e:
                logger.error(f"Invalid JSON received: {e}")
                raise