from .models import Driver, Vehicle


class FleetDispatchSession:
    """Context Manager for atomic driver-to-vehicle dispatch sessions.

    Ensures that if any exception occurs during the dispatch preparation
    or shipment loading, the driver and vehicle states are safely rolled back
    to their original availability status (transactional rollback).
    """

    def __init__(self, vehicle: Vehicle, driver: Driver):
        self.vehicle = vehicle
        self.driver = driver
        self._original_driver = vehicle.assigned_driver
        self._original_availability = driver.is_available

    def __enter__(self) -> Vehicle:
        """Assign the driver to the vehicle upon entering the context."""
        self.vehicle.assign_driver(self.driver)
        return self.vehicle

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Roll back driver and vehicle assignments if an error occurred inside the block."""
        if exc_type is not None:
            self.vehicle.assigned_driver = self._original_driver
            self.driver.is_available = self._original_availability
            return False
        return False
