import logging
import time
import requests
from typing import Any, Dict

try:
    from config import MAX_RETRIES, REQUEST_TIMEOUT, RETRY_DELAY, WEATHER_API_URL
except (ImportError, ValueError):
    from config import MAX_RETRIES, REQUEST_TIMEOUT, RETRY_DELAY, WEATHER_API_URL

logger = logging.getLogger("logitrack.api_client")


class WeatherApiClient:
    def __init__(self, api_url: str = WEATHER_API_URL, timeout: float = REQUEST_TIMEOUT):
        self.api_url = api_url
        self.timeout = timeout

    def fetch_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": "true"
        }

        last_exception = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                logger.info(
                    f"Fetching weather from API (Attempt {attempt}/{MAX_RETRIES}) for lat={latitude}, lon={longitude}")
                response = requests.get(self.api_url, params=params, timeout=self.timeout)
                response.raise_for_status()

                data = response.json()
                if "current_weather" not in data:
                    raise ValueError("Invalid API response format: missing 'current_weather' field.")

                return data

            except (requests.Timeout, requests.ConnectionError) as err:
                last_exception = err
                logger.warning(f"Connection/Timeout error on attempt {attempt}: {err}")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY * attempt)
            except requests.HTTPError as err:
                logger.error(f"HTTP error occurred: {err} (Status code: {err.response.status_code})")
                raise
            except (ValueError, KeyError) as err:
                logger.error(f"Data validation or JSON decode error: {err}")
                raise

        logger.error(f"Failed to fetch weather after {MAX_RETRIES} retries due to connection/timeout issues.")
        raise ConnectionError(f"API unreachable after {MAX_RETRIES} attempts: {last_exception}")