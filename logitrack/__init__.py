"""LogiTrack - Logistics & Delivery Management System."""

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
    generate_fleet_utilization_report,
    manage_destinations,
    process_incoming_batch,
    run_comprehensions,
    sort_parcels_collection,
    validate_fleet_data_relationships,
)
from .repository import ParcelRepository, VehicleRepository

__all__ = [
    # Models
    "Driver",
    "Vehicle",
    "Parcel",
    "StandardParcel",
    "ExpressParcel",
    "ShipmentOrder",
    # Repository
    "ParcelRepository",
    "VehicleRepository",
    # Processing
    "process_incoming_batch",
    "manage_destinations",
    "ShipmentManagerDict",
    "DeliveryWaitlistQueue",
    "PriorityDispatchQueue",
    "run_comprehensions",
    "sort_parcels_collection",
    "validate_fleet_data_relationships",
    "generate_fleet_utilization_report",
    # Iterators & Pipelines
    "ParcelIterator",
    "ParcelCollection",
    "filter_active_vehicles",
    "filter_pending_parcels",
    "build_available_fleet_pipeline",
    "build_urgent_parcels_pipeline",
    # Context Managers
    "FleetDispatchSession",
]
