import pytest
from logitrack.models import StandardParcel, ExpressParcel, Vehicle, Driver

def test_file_reading_with_tmp_path(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "env_test.txt"
    config_file.write_text("WEATHER_API_KEY=dummy_key")
    content = config_file.read_text()
    assert "dummy_key" in content

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