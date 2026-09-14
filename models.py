class Parcel:
    def __init__(self, parcel_id, weight, destination, status="Pending"):
        self.parcel_id = parcel_id
        self.weight = weight
        self.destination = destination
        self.status = status

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, value):
        if value <= 0:
            raise ValueError("Weight must be greater than 0")
        self._weight = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        valid_statuses = ["Pending", "In Transit", "Delivered"]
        if value not in valid_statuses:
            raise ValueError("Status is not valid")
        self._status = value

    def calculate_cost(self):
        pass

    @classmethod
    def from_dict(cls, data):
        return cls(data['id'], data['weight'], data['destination'], data.get('status', 'Pending'))

    def __str__(self):
        return f"Parcel {self.parcel_id} to {self.destination}"

    def __repr__(self):
        return f"Parcel(id={self.parcel_id}, weight={self.weight})"


class StandardParcel(Parcel):
    def calculate_cost(self):
        return self.weight * 15.0


class ExpressParcel(Parcel):
    def calculate_cost(self):
        return (self.weight * 15.0) + 50.0


class ShipmentOrder:
    def __init__(self, order_id):
        self.order_id = order_id
        self.parcels = []

    def add_parcel(self, parcel):
        self.parcels.append(parcel)

    def remove_parcel(self, parcel_id):
        for p in self.parcels:
            if p.parcel_id == parcel_id:
                self.parcels.remove(p)
                break

    def get_parcel(self, parcel_id):
        for p in self.parcels:
            if p.parcel_id == parcel_id:
                return p
        return None

    @property
    def total_cost(self):
        total = 0
        for p in self.parcels:
            total += p.calculate_cost()
        return total

    def __len__(self):
        return len(self.parcels)

    def __str__(self):
        return f"Shipment Order {self.order_id} with {len(self.parcels)} parcels"

    def __repr__(self):
        return f"ShipmentOrder(order_id={self.order_id}, parcels_count={len(self.parcels)})"