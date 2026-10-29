import threading
import logging
import time

try:
    from .models import ShipmentOrder
except (ImportError, ValueError):
    from models import ShipmentOrder

logger = logging.getLogger("logitrack.threaded_processing")


class FleetResourceManager:
    def __init__(self, initial_capacity: float):
        self.available_capacity = initial_capacity
        self._lock = threading.Lock()
        self.successful_assignments = 0

    def assign_shipment(self, worker_name: str, shipment: ShipmentOrder) -> bool:
        logger.info(f"{worker_name} attempting to assign shipment {shipment.order_id} ({shipment.total_weight}kg)...")

        with self._lock:
            if self.available_capacity >= shipment.total_weight:
                time.sleep(0.05)
                self.available_capacity -= shipment.total_weight
                self.successful_assignments += 1
                logger.info(
                    f"{worker_name} SUCCESS: Assigned {shipment.order_id}. Remaining capacity: {self.available_capacity}kg.")
                return True
            else:
                logger.warning(
                    f"{worker_name} FAILED: Not enough capacity for {shipment.order_id}. Available: {self.available_capacity}kg.")
                return False
