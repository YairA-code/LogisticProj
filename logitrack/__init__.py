from pathlib import Path
import sys

_pkg_dir = Path(__file__).resolve().parent
if str(_pkg_dir) not in sys.path:
    sys.path.insert(0, str(_pkg_dir))

from .context_managers import FleetDispatchSession
from .iterators import (
    ParcelCollection,
    ParcelIterator,
    build_available_fleet_pipeline,
    build_urgent_parcels_pipeline,
    filter_active_vehicles,
    filter_pending_parcels,
)
from .models import (
    Driver,
    ExpressParcel,
    Parcel,
    ShipmentOrder,
    StandardParcel,
    Vehicle,
)
from .processing import (
    DeliveryWaitlistQueue,
    PriorityDispatchQueue,
    ShipmentManagerDict,
    manage_destinations,
    process_incoming_batch,
    run_comprehensions,
    sort_parcels_collection,
    validate_fleet_data_relationships,
)
from .reports import (
    detect_operational_anomalies,
    generate_fleet_utilization_report,
)
from .repository import ParcelRepository, VehicleRepository

__all__ = [
    "Driver",
    "Vehicle",
    "Parcel",
    "StandardParcel",
    "ExpressParcel",
    "ShipmentOrder",
    "ParcelRepository",
    "VehicleRepository",
    "process_incoming_batch",
    "manage_destinations",
    "ShipmentManagerDict",
    "DeliveryWaitlistQueue",
    "PriorityDispatchQueue",
    "run_comprehensions",
    "sort_parcels_collection",
    "validate_fleet_data_relationships",
    "generate_fleet_utilization_report",
    "detect_operational_anomalies",
    "ParcelIterator",
    "ParcelCollection",
    "filter_active_vehicles",
    "filter_pending_parcels",
    "build_available_fleet_pipeline",
    "build_urgent_parcels_pipeline",
    "FleetDispatchSession",
]
