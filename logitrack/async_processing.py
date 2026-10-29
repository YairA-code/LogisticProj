import asyncio
import time
import logging
from typing import List, Dict, Any

logger = logging.getLogger("logitrack.async_processing")


async def fetch_weather_async(destination: str, latitude: float, longitude: float) -> Dict[str, Any]:
    logger.info(f"Start fetching weather for {destination}...")
    await asyncio.sleep(0.5)

    windspeed = 40.0 if destination == "Haifa" else 15.0

    logger.info(f"Finished fetching weather for {destination}.")
    return {
        "destination": destination,
        "windspeed": windspeed,
        "temperature": 22.0
    }


async def gather_weather_for_destinations(destinations_coords: List[dict]) -> List[Dict[str, Any]]:
    start_time = time.time()

    tasks = [
        fetch_weather_async(item["city"], item["lat"], item["lon"])
        for item in destinations_coords
    ]

    results = await asyncio.gather(*tasks)

    elapsed = time.time() - start_time
    logger.info(f"Async fetch for {len(destinations_coords)} destinations completed in {elapsed:.2f} seconds.")

    return results