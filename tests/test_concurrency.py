import pytest
import asyncio
from logitrack.async_processing import run_async_fetch
from logitrack.threaded_processing import FleetResourceManager
from logitrack.models import ShipmentOrder, StandardParcel

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