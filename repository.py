import json
from models import Parcel

class ParcelRepository:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def load_parcels(self):

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

                parcel_obj = Parcel.create_from_dict(data_dict)
                yield parcel_obj