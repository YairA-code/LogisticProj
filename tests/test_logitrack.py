import pytest
import asyncio
from unittest.mock import patch, MagicMock

from logitrack.models import StandardParcel, ExpressParcel, Vehicle, Driver, ShipmentOrder
from logitrack.api_client import WeatherApiClient
from logitrack.strategy import StandardPricingStrategy, ExtremeWeatherPricingStrategy, WeatherAdjustedCapacityStrategy
from logitrack.observer import FleetSafetyObserver, DelayStatisticsObserver
from logitrack.services import WeatherShippingService
from logitrack.async_processing import gather_weather_for_destinations
from logitrack.threaded_processing import FleetResourceManager
from logitrack.reports import generate_integrated_fleet_report


def test_standard_parcel_cost():
    parcel = StandardParcel("P1", 10.0, "Tel Aviv")
    assert parcel.calculate_cost() == 150.0


def test_express_parcel_cost():
    parcel = ExpressParcel("P2", 10.0, "Haifa")
    assert parcel.calculate_cost() == 200.0


def test_vehicle_capacity_validation():
    with pytest.raises(ValueError):
        Vehicle("11-222-33", -50.0, "OK")


def test_driver_availability_toggle():
    driver = Driver("D1", "Yair")
    assert driver.is_available is True
    driver.set_availability(False)
    assert driver.is_available is False


def test_shipment_order_weight():
    order = ShipmentOrder("O1")
    order.add_parcel(StandardParcel("P1", 5.0, "Tel Aviv"))
    order.add_parcel(ExpressParcel("P2", 2.5, "Haifa"))
    assert order.total_weight == 7.5


def test_shipment_order_dispatch_success():
    order = ShipmentOrder("O1")
    order.add_parcel(StandardParcel("P1", 5.0, "Tel Aviv"))
    vehicle = Vehicle("11-222-33", 100.0, "OK")
    driver = Driver("D1", "Yair")
    vehicle.assign_driver(driver)
    order.dispatch(vehicle)
    assert order.assigned_vehicle == vehicle
    assert order.parcels[0].status == "In Transit"


def test_shipment_order_dispatch_fail_maintenance():
    order = ShipmentOrder("O1")
    vehicle = Vehicle("11-222-33", 100.0, "In Maintenance")
    with pytest.raises(ValueError):
        order.dispatch(vehicle)


def test_shipment_order_dispatch_fail_capacity():
    order = ShipmentOrder("O1")
    order.add_parcel(StandardParcel("P1", 150.0, "Tel Aviv"))
    vehicle = Vehicle("11-222-33", 100.0, "OK")
    driver = Driver("D1", "Yair")
    vehicle.assign_driver(driver)
    with pytest.raises(ValueError):
        order.dispatch(vehicle)


@patch("logitrack.api_client.requests.get")
def test_weather_api_client_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"current_weather": {"windspeed": 20.0, "temperature": 25.0}}
    mock_get.return_value = mock_response
    client = WeatherApiClient()
    result = client.fetch_weather(32.0, 34.0)
    assert result["current_weather"]["windspeed"] == 20.0


@patch("logitrack.api_client.time.sleep", return_value=None)
@patch("logitrack.api_client.requests.get")
def test_weather_api_client_timeout_retry(mock_get, mock_sleep):
    import requests
    mock_get.side_effect = requests.Timeout("Timeout")
    client = WeatherApiClient(timeout=0.1)
    with pytest.raises(ConnectionError):
        client.fetch_weather(32.0, 34.0)
    assert mock_get.call_count == 3


def test_standard_pricing_strategy():
    strategy = StandardPricingStrategy()
    assert strategy.calculate_final_cost(100.0, {"windspeed": 40.0}) == 100.0


def test_extreme_weather_pricing_strategy():
    strategy = ExtremeWeatherPricingStrategy()
    assert strategy.calculate_final_cost(100.0, {"windspeed": 40.0}) == 150.0
    assert strategy.calculate_final_cost(100.0, {"windspeed": 20.0}) == 100.0


def test_weather_adjusted_capacity_normal():
    strategy = WeatherAdjustedCapacityStrategy()
    vehicle = Vehicle("11-222-33", 100.0)
    assert strategy.calculate_effective_capacity(vehicle, {"windspeed": 20.0}) == 100.0


def test_weather_adjusted_capacity_extreme():
    strategy = WeatherAdjustedCapacityStrategy()
    vehicle = Vehicle("11-222-33", 100.0)
    assert strategy.calculate_effective_capacity(vehicle, {"windspeed": 40.0}) == 80.0


def test_fleet_safety_observer_notified():
    observer = FleetSafetyObserver()
    with patch("logitrack.observer.logger.warning") as mock_logger:
        observer.update("HIGH_WIND_WARNING", {"vehicle": Vehicle("11-222-33", 100.0), "windspeed": 45.0})
        mock_logger.assert_called_once()


def test_delay_statistics_observer_notified():
    observer = DelayStatisticsObserver()
    observer.update("DISPATCH_BLOCKED", {"order_id": "O1"})
    assert observer.delayed_shipments_count == 1


@patch.object(WeatherApiClient, "fetch_weather", side_effect=Exception("API Down"))
def test_weather_shipping_service_fallback(mock_fetch):
    service = WeatherShippingService()
    order = ShipmentOrder("O1")
    vehicle = Vehicle("11-222-33", 100.0)

    result = service.evaluate_shipment(order, vehicle, 32.0, 34.0)

    assert result["fallback_mode"] is True
    assert result["is_weight_safe"] is True


def test_async_weather_fetch_order():
    destinations = [
        {"city": "Tel Aviv", "lat": 32.08, "lon": 34.78},
        {"city": "Haifa", "lat": 32.79, "lon": 34.98},
        {"city": "Eilat", "lat": 29.55, "lon": 34.95}
    ]

    results = asyncio.run(gather_weather_for_destinations(destinations))

    assert len(results) == 3
    assert results[0]["destination"] == "Tel Aviv"
    assert results[1]["destination"] == "Haifa"
    assert results[2]["destination"] == "Eilat"


def test_fleet_resource_manager_lock_success():
    manager = FleetResourceManager(100.0)
    order = ShipmentOrder("O1")
    order.add_parcel(StandardParcel("P1", 40.0, "Tel Aviv"))
    success = manager.assign_shipment("Worker1", order)
    assert success is True
    assert manager.available_capacity == 60.0


def test_fleet_resource_manager_lock_fail():
    manager = FleetResourceManager(30.0)
    order = ShipmentOrder("O1")
    order.add_parcel(StandardParcel("P1", 40.0, "Tel Aviv"))
    success = manager.assign_shipment("Worker1", order)
    assert success is False
    assert manager.available_capacity == 30.0


def test_integrated_fleet_report_generation():
    vehicles = [Vehicle("11-222-33", 100.0), Vehicle("44-555-66", 100.0, "In Maintenance")]
    order = ShipmentOrder("O1")
    order.add_parcel(StandardParcel("P1", 40.0, "Tel Aviv"))
    driver = Driver("D1", "Yair")
    vehicles[0].assign_driver(driver)
    order.dispatch(vehicles[0])

    evaluations = [{"windspeed": 40.0}]

    report = generate_integrated_fleet_report(vehicles, [order], evaluations)
    assert report["total_vehicles"] == 2
    assert report["active_vehicles"] == 1
    assert report["weather_affected_shipments_count"] == 1
    assert report["effective_weather_adjusted_capacity_kg"] == 80.0