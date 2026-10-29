import pytest
from unittest.mock import patch
from logitrack.strategy import ExtremeWeatherPricingStrategy, WeatherAdjustedCapacityStrategy
from logitrack.observer import FleetSafetyObserver, DelayStatisticsObserver

@pytest.mark.parametrize("windspeed, expected_cost", [
    (20.0, 100.0),
    (36.0, 150.0),
    (45.0, 150.0)
])
def test_extreme_weather_pricing_strategy_parametrize(windspeed, expected_cost):
    strategy = ExtremeWeatherPricingStrategy()
    assert strategy.calculate_final_cost(100.0, {"windspeed": windspeed}) == expected_cost

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