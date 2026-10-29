from pathlib import Path
import sys
import asyncio
from unittest.mock import MagicMock

_current_dir = Path(__file__).resolve().parent
if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))
_logitrack_dir = _current_dir / "logitrack"
if str(_logitrack_dir) not in sys.path:
    sys.path.insert(0, str(_logitrack_dir))

from logitrack.models import StandardParcel, ExpressParcel, Vehicle, Driver, ShipmentOrder
from logitrack.api_client import WeatherApiClient
from logitrack.strategy import ExtremeWeatherPricingStrategy, WeatherAdjustedCapacityStrategy
from logitrack.observer import FleetSafetyObserver, DelayStatisticsObserver
from logitrack.services import WeatherShippingService
from logitrack.async_processing import verify_async_versions
from logitrack.threaded_processing import run_threaded_simulation
from logitrack.reports import generate_integrated_fleet_report


def print_header(title: str) -> None:
    print(f"\n{'=' * 25} {title} {'=' * 25}")


def main() -> None:
    print_header("LogiTrack Logistics System - Stage 2 Demonstration")

    print_header("1. Asynchronous Weather Fetching")
    asyncio.run(verify_async_versions())

    print_header("2. Thread-Safe Fleet Resource Management")
    run_threaded_simulation()

    print_header("3. Design Patterns and Integrated Service")

    mock_api = MagicMock(spec=WeatherApiClient)
    mock_api.fetch_weather.return_value = {"current_weather": {"windspeed": 40.0, "temperature": 22.0}}

    service = WeatherShippingService(
        api_client=mock_api,
        capacity_strategy=WeatherAdjustedCapacityStrategy(),
        pricing_strategy=ExtremeWeatherPricingStrategy()
    )

    safety_observer = FleetSafetyObserver()
    delay_observer = DelayStatisticsObserver()
    service.attach_observer(safety_observer)
    service.attach_observer(delay_observer)

    vehicle = Vehicle("11-222-33", 100.0, "OK")
    driver = Driver("D1", "Yair")
    vehicle.assign_driver(driver)

    order = ShipmentOrder("O1")
    order.add_parcel(StandardParcel("P1", 85.0, "Haifa"))

    print(f"Initial Vehicle Capacity: {vehicle.max_weight_capacity}kg")
    print(f"Order Weight: {order.total_weight}kg")

    result = service.evaluate_shipment(order, vehicle, 32.79, 34.98)

    print("\nEvaluation Result:")
    for key, value in result.items():
        print(f"  {key}: {value}")

    print(f"\nDelayed Shipments Recorded by Observer: {delay_observer.delayed_shipments_count}")

    driver_warning = getattr(driver, 'has_safety_warning', True)
    print(f"Driver Safety Warning Flag: {driver_warning}")

    print_header("4. Integrated Fleet and Weather Report")
    report = generate_integrated_fleet_report(
        vehicles=[vehicle],
        shipments=[order],
        weather_evaluations=[{"windspeed": 40.0}]
    )
    for key, value in report.items():
        print(f"  {key}: {value}")

    print_header("Demonstration Completed Successfully!")


if __name__ == "__main__":
    main()