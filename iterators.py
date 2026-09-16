from models import Parcel,ExpressParcel
from typing import Iterable, Iterator

class ParcelIterator:

    def __init__(self, parcels: list[Parcel]):
        self._parcels = parcels
        self._index = 0

    def __iter__(self) -> "ParcelIterator":
        return self

    def __next__(self) -> Parcel:

        if self._index >= len(self._parcels):
            raise StopIteration


        current_parcel = self._parcels[self._index]
        self._index += 1
        return current_parcel


class ParcelCollection:

    def __init__(self, parcels: list[Parcel] = None):
        self._parcels = list(parcels) if parcels else []

    def add(self, parcel: Parcel) -> None:
        self._parcels.append(parcel)

    def __iter__(self) -> ParcelIterator:
        return ParcelIterator(self._parcels)

    def __len__(self) -> int:
        return len(self._parcels)




def filter_pending_parcels(parcels: Iterable) -> Iterator:

    for parcel in parcels:
        if parcel.status == "Pending":
            yield parcel


def build_heavy_express_pipeline(parcels):
    stage_1_express_only = (p for p in parcels if isinstance(p, ExpressParcel))

    stage_2_heavy_only = (p for p in stage_1_express_only if p.weight > 1.5)

    stage_3_summary = (
        {
            "parcel_id": p.parcel_id,
            "destination": p.destination,
            "cost": p.calculate_cost()
        }
        for p in stage_2_heavy_only
    )

    return stage_3_summary