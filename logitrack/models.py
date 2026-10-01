from abc import ABC, abstractmethod


class Driver:
    """Represents a delivery driver."""

    def __init__(self, driver_id: str, name: str, is_available: bool = True):
        if not driver_id or not isinstance(driver_id, str):
            raise ValueError("Driver ID must be a non-empty string.")
        if not name or not isinstance(name, str):
            raise ValueError("Driver name must be a non-empty string.")

        self.driver_id = driver_id
        self.name = name
        self.is_available = is_available

    @classmethod
    def from_dict(cls, data: dict) -> "Driver":
        return cls(data["driver_id"], data["name"], data.get("is_available", True))

    def __str__(self) -> str:
        status = "Available" if self.is_available else "Not Available"
        return f"Driver {self.name} (ID: {self.driver_id}) - {status}"

    def __repr__(self) -> str:
        return f"Driver(driver_id='{self.driver_id}', name='{self.name}', is_available={self.is_available})"


class Vehicle:
    """Represents a fleet vehicle used for deliveries."""

    def __init__(self, license_plate: str, max_weight_capacity: float, mechanical_status: str = "OK"):
        if not license_plate or not isinstance(license_plate, str):
            raise ValueError("License plate must be a non-empty string.")

        self.license_plate = license_plate
        self.max_weight_capacity = max_weight_capacity
        self.mechanical_status = mechanical_status
        self.assigned_driver: Driver | None = None

    @property
    def max_weight_capacity(self) -> float:
        return self._max_weight_capacity

    @max_weight_capacity.setter
    def max_weight_capacity(self, value: float) -> None:
        if value <= 0:
            raise ValueError("Vehicle max weight capacity must be greater than 0.")
        self._max_weight_capacity = float(value)

    @property
    def mechanical_status(self) -> str:
        return self._mechanical_status

    @mechanical_status.setter
    def mechanical_status(self, value: str) -> None:
        valid_statuses = ["OK", "In Maintenance"]
        if value not in valid_statuses:
            raise ValueError(f"Invalid mechanical status '{value}'. Must be one of {valid_statuses}")
        self._mechanical_status = value

    def assign_driver(self, driver: Driver) -> None:
        if self.mechanical_status != "OK":
            raise ValueError("Cannot assign a driver to a vehicle in maintenance.")
        if not driver.is_available:
            raise ValueError(f"Driver {driver.name} is currently not available.")
        self.assigned_driver = driver
        driver.is_available = False

    def release_driver(self) -> None:
        if self.assigned_driver:
            self.assigned_driver.is_available = True
            self.assigned_driver = None

    def __str__(self) -> str:
        driver_str = f" | Driver: {self.assigned_driver.name}" if self.assigned_driver else ""
        return f"Vehicle {self.license_plate} | Status: {self.mechanical_status} | Capacity: {self.max_weight_capacity}kg{driver_str}"

    def __repr__(self) -> str:
        return f"Vehicle(license_plate='{self.license_plate}', max_weight={self.max_weight_capacity}, status='{self.mechanical_status}')"


class Parcel(ABC):
    """Abstract base class for all parcels."""

    def __init__(self, parcel_id: str, weight: float, destination: str, status: str = "Pending"):
        if not parcel_id or not isinstance(parcel_id, str):
            raise ValueError("Parcel ID must be a non-empty string.")
        if not destination or not isinstance(destination, str):
            raise ValueError("Destination must be a non-empty string.")

        self.parcel_id = parcel_id
        self.weight = weight
        self.destination = destination
        self.status = status

    @property
    def weight(self) -> float:
        return self._weight

    @weight.setter
    def weight(self, value: float) -> None:
        if value <= 0:
            raise ValueError("Parcel weight must be greater than 0.")
        self._weight = float(value)

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        valid_statuses = ["Pending", "In Transit", "Delivered"]
        if value not in valid_statuses:
            raise ValueError(f"Status '{value}' is not valid. Must be one of {valid_statuses}")
        self._status = value

    @abstractmethod
    def calculate_cost(self) -> float:
        """Calculate and return delivery cost (polymorphic across parcel types)."""
        pass

    @staticmethod
    def create_from_dict(data: dict) -> "Parcel":
        parcel_type = data.get("type", "standard").lower()
        if parcel_type == "express":
            return ExpressParcel(data["id"], data["weight"], data["destination"], data.get("status", "Pending"))
        return StandardParcel(data["id"], data["weight"], data["destination"], data.get("status", "Pending"))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Parcel):
            return self.parcel_id == other.parcel_id
        return False

    def __hash__(self) -> int:
        return hash(self.parcel_id)

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.parcel_id} to {self.destination} ({self.status}, {self.weight}kg)"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id='{self.parcel_id}', weight={self.weight}, status='{self.status}')"


class StandardParcel(Parcel):
    """Standard shipping parcel with base pricing per kg."""

    def calculate_cost(self) -> float:
        return self.weight * 15.0


class ExpressParcel(Parcel):
    """Express shipping parcel with express surcharge."""

    def calculate_cost(self) -> float:
        return (self.weight * 15.0) + 50.0


class ShipmentOrder:
    """Represents a grouped order composed of multiple parcels dispatched together."""

    def __init__(self, order_id: str):
        if not order_id or not isinstance(order_id, str):
            raise ValueError("Order ID must be a non-empty string.")
        self.order_id = order_id
        self.parcels: list[Parcel] = []
        self.assigned_vehicle: Vehicle | None = None

    def add_parcel(self, parcel: Parcel) -> None:
        if parcel in self.parcels:
            raise ValueError(f"Parcel {parcel.parcel_id} is already in the shipment order.")
        self.parcels.append(parcel)

    def remove_parcel(self, parcel_id: str) -> bool:
        parcel = self.get_parcel(parcel_id)
        if parcel:
            self.parcels.remove(parcel)
            return True
        return False

    def get_parcel(self, parcel_id: str) -> Parcel | None:
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

    def dispatch(self, vehicle: Vehicle) -> None:
        if vehicle.mechanical_status != "OK":
            raise ValueError(f"Cannot dispatch. Vehicle {vehicle.license_plate} is in maintenance.")
        if vehicle.assigned_driver is None:
            raise ValueError(f"Cannot dispatch. Vehicle {vehicle.license_plate} has no assigned driver.")
        if self.total_weight > vehicle.max_weight_capacity:
            raise ValueError(
                f"Shipment weight ({self.total_weight}kg) exceeds vehicle capacity ({vehicle.max_weight_capacity}kg)."
            )

        self.assigned_vehicle = vehicle
        for p in self.parcels:
            p.status = "In Transit"

    def __len__(self) -> int:
        return len(self.parcels)

    def __str__(self) -> str:
        vehicle_info = f" (Vehicle: {self.assigned_vehicle.license_plate})" if self.assigned_vehicle else " (Unassigned)"
        return f"Shipment Order {self.order_id} | {len(self.parcels)} Parcels | Total Weight: {self.total_weight:.2f}kg{vehicle_info}"

    def __repr__(self) -> str:
        return f"ShipmentOrder(order_id='{self.order_id}', parcels_count={len(self.parcels)}, assigned={self.assigned_vehicle is not None})"
