import pytest
import asyncio
from unittest.mock import patch, MagicMock

from logitrack.models import StandardParcel, ExpressParcel, Vehicle, Driver, ShipmentOrder
from logitrack.api_client import WeatherApiClient
from logitrack.strategy import StandardPricingStrategy, ExtremeWeatherPricingStrategy, WeatherAdjustedCapacityStrategy
from logitrack.observer import FleetSafetyObserver, DelayStatisticsObserver
from logitrack.services import WeatherShippingService
from logitrack.async_processing import run_async_fetch
from logitrack.threaded_processing import FleetResourceManager
from logitrack.reports import generate_integrated_fleet_report

@pytest.fixture
def sample_vehicle():
    return Vehicle("11-222-33", 100.0, "OK")

@pytest.fixture
def sample_order():
    order = ShipmentOrder("O1")
    order.add_parcel(StandardParcel("P1", 10.0, "Tel Aviv"))
    return order

def test_file_reading_with_tmp_path(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "env_test.txt"
    config_file.write_text("WEATHER_API_KEY=dummy_key")
    content = config_file.read_text()
    assert "dummy_key" in content

@pytest.mark.parametrize("windspeed, expected_cost", [
    (20.0, 100.0),
    (36.0, 150.0),
    (45.0, 150.0)
])
def test_extreme_weather_pricing_strategy_parametrize(windspeed, expected_cost):
    strategy = ExtremeWeatherPricingStrategy()
    assert strategy.calculate_final_cost(100.0, {"windspeed": windspeed}) == expected_cost

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

def test_shipment_order_weight(sample_order):
    sample_order.add_parcel(ExpressParcel("P2", 2.5, "Haifa"))
    assert sample_order.total_weight == 12.5

def test_shipment_order_dispatch_success(sample_order, sample_vehicle):
    driver = Driver("D1", "Yair")
    sample_vehicle.assign_driver(driver)
    sample_order.dispatch(sample_vehicle)
    assert sample_order.assigned_vehicle == sample_vehicle
    assert sample_order.parcels[0].status == "In Transit"

def test_shipment_order_dispatch_fail_maintenance(sample_order):
    vehicle = Vehicle("11-222-33", 100.0, "In Maintenance")
    with pytest.raises(ValueError):
        sample_order.dispatch(vehicle)

def test_shipment_order_dispatch_fail_capacity(sample_order, sample_vehicle):
    sample_order.add_parcel(StandardParcel("P3", 150.0, "Tel Aviv"))
    driver = Driver("D1", "Yair")
    sample_vehicle.assign_driver(driver)
    with pytest.raises(ValueError):
        sample_order.dispatch(sample_vehicle)

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
    client = WeatherApiClient(timeout=0.1, max_retries=3)
    with pytest.raises(ConnectionError):
        client.fetch_weather(32.0, 34.0)
    assert mock_get.call_count == 3

def test_weather_adjusted_capacity_normal(sample_vehicle):
    strategy = WeatherAdjustedCapacityStrategy()
    assert strategy.calculate_effective_capacity(sample_vehicle, {"windspeed": 20.0}) == 100.0

def test_weather_adjusted_capacity_extreme(sample_vehicle):
    strategy = WeatherAdjustedCapacityStrategy()
    assert strategy.calculate_effective_capacity(sample_vehicle, {"windspeed": 40.0}) == 80.0

def test_fleet_safety_observer_notified(sample_vehicle):
    observer = FleetSafetyObserver()
    with patch("logitrack.observer.logger.warning") as mock_logger:
        observer.update("HIGH_WIND_WARNING", {"vehicle": sample_vehicle, "windspeed": 45.0})
        mock_logger.assert_called_once()

def test_delay_statistics_observer_notified():
    observer = DelayStatisticsObserver()
    observer.update("DISPATCH_BLOCKED", {"order_id": "O1"})
    assert observer.delayed_shipments_count == 1

@patch.object(WeatherApiClient, "fetch_weather", side_effect=Exception("API Down"))
def test_weather_shipping_service_fallback(mock_fetch, sample_order, sample_vehicle):
    service = WeatherShippingService()
    result = service.evaluate_shipment(sample_order, sample_vehicle, 32.0, 34.0)
    assert result["fallback_mode"] is True
    assert result["is_weight_safe"] is True

def test_async_weather_fetch_order():
    destinations = [
        {"city": "Tel Aviv", "lat": 32.08, "lon": 34.78},
        {"city": "Haifa", "lat": 32.79, "lon": 34.98},
        {"city": "Eilat", "lat": 29.55, "lon": 34.95}
    ]
    results = asyncio.run(run_async_fetch(destinations))
    assert len(results) == 3
    assert results[0]["destination"] == "Tel Aviv"

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

def test_integrated_fleet_report_generation(sample_vehicle, sample_order):
    driver = Driver("D1", "Yair")
    sample_vehicle.assign_driver(driver)
    sample_order.dispatch(sample_vehicle)
    evaluations = [{"windspeed": 40.0}]
    report = generate_integrated_fleet_report([sample_vehicle], [sample_order], evaluations)
    assert report["total_vehicles"] == 1
    assert report["active_vehicles"] == 1
    assert report["weather_affected_shipments_count"] == 1
    assert report["effective_weather_adjusted_capacity_kg"] == 80.0