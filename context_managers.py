from models import Vehicle, Driver

class FleetDispatchSession:


    def __init__(self, vehicle: Vehicle, driver: Driver):
        self.vehicle = vehicle
        self.driver = driver

        self._original_driver = vehicle.assigned_driver
        self._original_availability = driver.is_available

    def __enter__(self) -> Vehicle:

        self.vehicle.assign_driver(self.driver)
        return self.vehicle

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is not None:

            self.vehicle.assigned_driver = self._original_driver
            self.driver.is_available = self._original_availability
            return False

        return False