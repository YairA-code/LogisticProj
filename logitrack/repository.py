import json
from pathlib import Path
from typing import Iterator

from .models import Parcel, Vehicle


class ParcelRepository:
    """Repository for loading and querying parcels from a JSONL file."""

    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)

    def load_parcels(self) -> Iterator[Parcel]:
        """Lazy generator that reads sample_data.jsonl line-by-line, converts dicts to Parcel instances,

        and yields them. Enforces ID uniqueness and field validation.
        """
        if not self.filepath.exists():
            raise FileNotFoundError(f"Data file not found at: {self.filepath}")

        seen_ids = set()

        with open(self.filepath, mode="r", encoding="utf-8") as file:
            for line_number, raw_line in enumerate(file, start=1):
                clean_line = raw_line.strip()
                if not clean_line:
                    continue

                try:
                    data_dict = json.loads(clean_line)
                except json.JSONDecodeError as err:
                    raise ValueError(f"Line {line_number}: Invalid JSON format - {err}")

                parcel_id = data_dict.get("id")
                if not parcel_id:
                    raise ValueError(f"Line {line_number}: Missing parcel 'id'")
                if parcel_id in seen_ids:
                    raise ValueError(f"Line {line_number}: Duplicate parcel_id '{parcel_id}'")
                seen_ids.add(parcel_id)

                if "weight" in data_dict and data_dict["weight"] <= 0:
                    raise ValueError(f"Line {line_number}: Weight must be > 0")

                parcel_obj = Parcel.from_dict(data_dict)
                yield parcel_obj

    def find_by_id(self, parcel_id: str) -> Parcel | None:
        """Finds and returns a Parcel object by its unique ID. Returns None if not found."""
        for parcel in self.load_parcels():
            if parcel.parcel_id == parcel_id:
                return parcel
        return None

    def get_all(self) -> list[Parcel]:
        """Loads and returns all parcels as a list."""
        return list(self.load_parcels())


class VehicleRepository:
    """Repository for loading vehicle records from JSONL."""

    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)

    def load_vehicles(self) -> Iterator[Vehicle]:
        """Lazy generator that reads vehicles JSONL line-by-line."""
        if not self.filepath.exists():
            raise FileNotFoundError(f"Vehicle data file not found at: {self.filepath}")

        with open(self.filepath, mode="r", encoding="utf-8") as file:
            for line_number, raw_line in enumerate(file, start=1):
                clean_line = raw_line.strip()
                if not clean_line:
                    continue
                try:
                    data = json.loads(clean_line)
                    yield Vehicle.from_dict(data)
                except Exception as err:
                    raise ValueError(f"Line {line_number}: Invalid vehicle record - {err}")
