from typing import Iterable, Iterator, Dict, Any
from models import Parcel, Vehicle

class ParcelIterator:
    def __init__(self, parcels: list[Parcel]):
        self._parcels = parcels
        self._index = 0

    def __iter__(self) -> "ParcelIterator":
        return self

    def __next__(self) -> Parcel:
        if self._index >= len(self._parcels):
            raise StopIteration
        item = self._parcels[self._index]
        self._index += 1
        return item

class ParcelCollection:
    def __init__(self, parcels: Iterable[Parcel] = None):
        self._parcels = list(parcels) if parcels else []

    def add(self, parcel: Parcel) -> None:
        self._parcels.append(parcel)

    def __iter__(self) -> ParcelIterator:
        return ParcelIterator(self._parcels)

    def __len__(self) -> int:
        return len(self._parcels)

def filter_active_vehicles(vehicles: Iterable[Vehicle]) -> Iterator[Vehicle]:

    for vehicle in vehicles:
        if vehicle.mechanical_status == "OK":
            yield vehicle

def build_available_fleet_pipeline(vehicles: Iterable[Vehicle]) -> Iterator[Dict[str, Any]]:

    stage_1_ok = (v for v in vehicles if v.mechanical_status == "OK")
    stage_2_unassigned = (v for v in stage_1_ok if v.assigned_driver is None)
    stage_3_summary = (
        {
            "license_plate": v.license_plate,
            "available_capacity_kg": v.max_weight_capacity
        }
        for v in stage_2_unassigned
    )
    return stage_3_summary