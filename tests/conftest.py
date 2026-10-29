import pytest
from logitrack.models import Vehicle, ShipmentOrder, StandardParcel

@pytest.fixture
def sample_vehicle():
    return Vehicle("11-222-33", 100.0, "OK")

@pytest.fixture
def sample_order():
    order = ShipmentOrder("O1")
    order.add_parcel(StandardParcel("P1", 10.0, "Tel Aviv"))
    return order