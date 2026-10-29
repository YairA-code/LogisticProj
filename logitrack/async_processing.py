import asyncio
import time
import logging
from typing import List, Dict, Any

logger = logging.getLogger("logitrack.async_processing")


async def fetch_weather_simulated(destination: str, latitude: float, longitude: float) -> Dict[str, Any]:
    logger.info(f"Start fetching weather for {destination}")

    await asyncio.sleep(0.5)

    windspeed = 40.0 if destination == "Haifa" else 15.0

    logger.info(f"Finished fetching weather for {destination}")

    return {
        "destination": destination,
        "windspeed": windspeed,
        "temperature": 22.0
    }


async def run_sequential_fetch(destinations: List[dict]) -> List[Dict[str, Any]]:
    start_time = time.time()
    results = []

    for item in destinations:
        result = await fetch_weather_simulated(item["city"], item["lat"], item["lon"])
        results.append(result)

    elapsed = time.time() - start_time
    logger.info(f"Sequential fetch completed in {elapsed:.2f} seconds")
    return results


async def run_async_fetch(destinations: List[dict]) -> List[Dict[str, Any]]:
    start_time = time.time()

    tasks = [
        fetch_weather_simulated(item["city"], item["lat"], item["lon"])
        for item in destinations
    ]

    results = await asyncio.gather(*tasks)

    elapsed = time.time() - start_time
    logger.info(f"Async fetch completed in {elapsed:.2f} seconds")
    return results


async def verify_async_versions() -> None:
    destinations = [
        {"city": "Tel Aviv", "lat": 32.08, "lon": 34.78},
        {"city": "Haifa", "lat": 32.79, "lon": 34.98},
        {"city": "Eilat", "lat": 29.55, "lon": 34.95}
    ]

    seq_results = await run_sequential_fetch(destinations)
    async_results = await run_async_fetch(destinations)

    is_identical = seq_results == async_results
    logger.info(f"Are results identical and in the same order? {is_identical}")
