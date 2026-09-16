from models import Parcel

class ParcelProcessingLock:

    def __init__(self, parcel: Parcel, mark_completed_on_success: bool = True):
        self.parcel = parcel
        self.mark_completed_on_success = mark_completed_on_success

        self._original_status = parcel.status

    def __enter__(self) -> Parcel:

        self.parcel.status = "Processing"
        return self.parcel

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:

        if exc_type is not None:

            self.parcel.status = self._original_status

            return False

        if self.mark_completed_on_success:
            self.parcel.status = "In Transit"

        return False