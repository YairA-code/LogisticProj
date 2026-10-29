import pytest
from logitrack.reports import generate_integrated_fleet_report
from logitrack.models import Driver

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