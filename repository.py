import json
from models import StandardParcel, ExpressParcel


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
                if parcel_id in seen_ids:
                    raise ValueError(f"Line {line_number}: Duplicate parcel_id found: '{parcel_id}'")
                seen_ids.add(parcel_id)

                parcel_obj = self._instantiate_parcel(data_dict, line_number)
                yield parcel_obj

    def _instantiate_parcel(self, data: dict, line_num: int):

        required_keys = {"id", "type", "weight", "destination"}
        missing_keys = required_keys - data.keys()
        if missing_keys:
            raise ValueError(f"Line {line_num}: Missing required fields: {missing_keys}")

        if data["weight"] <= 0:
            raise ValueError(f"Line {line_num}: Weight must be positive, got {data['weight']}")


        parcel_type = data["type"].lower()
        if parcel_type == "standard":
            return StandardParcel.from_dict(data)
        elif parcel_type == "express":
            return ExpressParcel.from_dict(data)
        else:
            raise ValueError(f"Line {line_num}: Unsupported parcel type: '{parcel_type}'")