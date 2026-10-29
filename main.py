from pathlib import Path
import sys
import asyncio
import json
from unittest.mock import MagicMock

_current_dir = Path(__file__).resolve().parent
if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))
_logitrack_dir = _current_dir / "logitrack"
if str(_logitrack_dir) not in sys.path:
    sys.path.insert(0, str(_logitrack_dir))

from logitrack.models import StandardParcel, Vehicle, Driver, ShipmentOrder
from logitrack.api_client import WeatherApiClient
from logitrack.strategy import ExtremeWeatherPricingStrategy, WeatherAdjustedCapacityStrategy
from logitrack.observer import FleetSafetyObserver, DelayStatisticsObserver
from logitrack.services import WeatherShippingService
from logitrack.async_processing import run_async_fetch
from logitrack.threaded_processing import run_threaded_simulation
from logitrack.reports import generate_integrated_fleet_report


def print_header(title: str) -> None:
    print(f"\n{'=' * 25} {title} {'=' * 25}")


def load_demo_data():
    data_path = _current_dir / "data" / "demo_data.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_service_demo(service: WeatherShippingService, data: dict, use_real_api: bool = False):
    vehicle = Vehicle(data["vehicle_plate"], data["vehicle_capacity"], "OK")
    driver = Driver(data["driver_id"], data["driver_name"])
    vehicle.assign_driver(driver)

    order = ShipmentOrder(data["order_id"])
    for p in data["parcels"]:
        order.add_parcel(StandardParcel(p["id"], p["weight"], p["destination"]))

    mode_text = "REAL API (LIVE NETWORK)" if use_real_api else "MOCKED API (OFFLINE)"
    print(f"\n--- Running Evaluation: {mode_text} ---")

    result = service.evaluate_shipment(order, vehicle, data["dest_lat"], data["dest_lon"])

    for key, value in result.items():
        print(f"  {key}: {value}")


def main() -> None:
    print_header("LogiTrack Logistics System - Stage 2 Demonstration")

    demo_data = load_demo_data()

    print_header("1. Asynchronous Weather Fetching")
    asyncio.run(run_async_fetch([
        {"city": "Tel Aviv", "lat": 32.08, "lon": 34.78},
        {"city": "Haifa", "lat": 32.79, "lon": 34.98},
        {"city": "Eilat", "lat": 29.55, "lon": 34.95}
    ]))

    print_header("2. Thread-Safe Fleet Resource Management")
    run_threaded_simulation()

    print_header("3. Design Patterns and Integrated Service")

    mock_api = MagicMock(spec=WeatherApiClient)
    mock_api.fetch_weather.return_value = {"current_weather": {"windspeed": 40.0, "temperature": 22.0}}

    mocked_service = WeatherShippingService(
        api_client=mock_api,
        capacity_strategy=WeatherAdjustedCapacityStrategy(),
        pricing_strategy=ExtremeWeatherPricingStrategy()
    )

    delay_observer = DelayStatisticsObserver()
    mocked_service.attach_observer(FleetSafetyObserver())
    mocked_service.attach_observer(delay_observer)

    run_service_demo(mocked_service, demo_data, use_real_api=False)

    print_header("4. Real External Service Connection")
    real_api = WeatherApiClient()
    real_service = WeatherShippingService(
        api_client=real_api,
        capacity_strategy=WeatherAdjustedCapacityStrategy(),
        pricing_strategy=ExtremeWeatherPricingStrategy()
    )
    run_service_demo(real_service, demo_data, use_real_api=True)


if __name__ == "__main__":
    main()