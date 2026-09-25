from abc import ABC, abstractmethod


class Driver:
    def __init__(self, driver_id: str, name: str, is_available: bool = True):
        self.driver_id = driver_id
        self.name = name
        self.is_available = is_available

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data['driver_id'], data['name'], data.get('is_available', True))

    def __str__(self):
        status = "Available" if self.is_available else "Not Available"
        return f"Driver {self.name} (ID: {self.driver_id}) - {status}"

    def __repr__(self):
        return f"Driver(driver_id='{self.driver_id}', name='{self.name}', is_available={self.is_available})"


class Vehicle:
    def __init__(self, license_plate: str, max_weight_capacity: float, mechanical_status: str = "OK"):
        self.license_plate = license_plate
        self.max_weight_capacity = max_weight_capacity
        self.mechanical_status = mechanical_status
        self.assigned_driver = None

    @property
    def max_weight_capacity(self):
        return self._max_weight_capacity

    @max_weight_capacity.setter
    def max_weight_capacity(self, value):
        if value <= 0:
            raise ValueError("Vehicle max weight capacity must be greater than 0.")
        self._max_weight_capacity = value

    @property
    def mechanical_status(self):
        return self._mechanical_status

    @mechanical_status.setter
    def mechanical_status(self, value):
        valid_statuses = ["OK", "In Maintenance"]
        if value not in valid_statuses:
            raise ValueError(f"Invalid mechanical status. Must be one of {valid_statuses}")
        self._mechanical_status = value

    def assign_driver(self, driver: Driver):
        if self.mechanical_status != "OK":
            raise ValueError("Cannot assign a driver to a vehicle in maintenance.")
        if not driver.is_available:
            raise ValueError(f"Driver {driver.name} is currently not available.")
        self.assigned_driver = driver
        driver.is_available = False

    def __str__(self):
        return f"Vehicle {self.license_plate} | Status: {self.mechanical_status} | Capacity: {self.max_weight_capacity}kg"

    def __repr__(self):
        return f"Vehicle(license_plate='{self.license_plate}', max_weight={self.max_weight_capacity}, status='{self.mechanical_status}')"


class Parcel(ABC):
    def __init__(self, parcel_id: str, weight: float, destination: str, status: str = "Pending"):
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
            raise ValueError("Parcel weight must be greater than 0")
        self._weight = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        valid_statuses = ["Pending", "In Transit", "Delivered"]
        if value not in valid_statuses:
            raise ValueError(f"Status '{value}' is not valid. Must be one of {valid_statuses}")
        self._status = value

    @abstractmethod
    def calculate_cost(self) -> float:
        pass

    @staticmethod
    def create_from_dict(data: dict):
        parcel_type = data.get('type', 'standard')
        if parcel_type == 'express':
            return ExpressParcel(data['id'], data['weight'], data['destination'], data.get('status', 'Pending'))
        return StandardParcel(data['id'], data['weight'], data['destination'], data.get('status', 'Pending'))

    def __eq__(self, other):
        if isinstance(other, Parcel):
            return self.parcel_id == other.parcel_id
        return False

    def __str__(self):
        return f"Parcel {self.parcel_id} to {self.destination} ({self.status})"

    def __repr__(self):
        return f"{self.__class__.__name__}(id='{self.parcel_id}', weight={self.weight}, status='{self.status}')"


class StandardParcel(Parcel):
    def calculate_cost(self) -> float:
        return self.weight * 15.0


class ExpressParcel(Parcel):
    def calculate_cost(self) -> float:
        return (self.weight * 15.0) + 50.0


class ShipmentOrder:
    def __init__(self, order_id: str):
        self.order_id = order_id
        self.parcels = []
        self.assigned_vehicle = None

    def add_parcel(self, parcel: Parcel):
        if parcel in self.parcels:
            raise ValueError(f"Parcel {parcel.parcel_id} is already in the shipment order.")
        self.parcels.append(parcel)

    def remove_parcel(self, parcel_id: str):
        parcel = self.get_parcel(parcel_id)
        if parcel:
            self.parcels.remove(parcel)
            return True
        return False

    def get_parcel(self, parcel_id: str) -> Parcel:
        for p in self.parcels:
            if p.parcel_id == parcel_id:
                return p
        return None

    @property
    def total_weight(self) -> float:
        return sum(p.weight for p in self.parcels)

    @property
    def total_cost(self) -> float:
        return sum(p.calculate_cost() for p in self.parcels)

    def dispatch(self, vehicle: Vehicle):
        if vehicle.mechanical_status != "OK":
            raise ValueError(f"Cannot dispatch. Vehicle {vehicle.license_plate} is in maintenance.")
        if vehicle.assigned_driver is None:
            raise ValueError(f"Cannot dispatch. Vehicle {vehicle.license_plate} has no assigned driver.")
        if self.total_weight > vehicle.max_weight_capacity:
            raise ValueError(
                f"Shipment weight ({self.total_weight}) exceeds vehicle capacity ({vehicle.max_weight_capacity}).")

        self.assigned_vehicle = vehicle
        for p in self.parcels:
            p.status = "In Transit"

    def __len__(self):
        return len(self.parcels)

    def __str__(self):
        vehicle_info = f" (Vehicle: {self.assigned_vehicle.license_plate})" if self.assigned_vehicle else " (Unassigned)"
        return f"Shipment Order {self.order_id} | {len(self.parcels)} Parcels | Total Weight: {self.total_weight}kg{vehicle_info}"

    def __repr__(self):
        return f"ShipmentOrder(order_id='{self.order_id}', parcels_count={len(self.parcels)}, assigned={self.assigned_vehicle is not None})"