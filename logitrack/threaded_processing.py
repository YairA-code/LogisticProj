import threading
import logging
import time

try:
    from .models import ShipmentOrder, StandardParcel
except (ImportError, ValueError):
    from models import ShipmentOrder, StandardParcel

logger = logging.getLogger("logitrack.threaded_processing")

RACE_CONDITION_EXPLANATION = """
Without a lock, a race condition occurs when two threads check the available capacity simultaneously.
Thread A checks if capacity >= weight and sees it is True.
Before Thread A subtracts the weight, a context switch happens.
Thread B checks if capacity >= weight, also sees it is True, and subtracts the weight.
Then Thread A resumes and subtracts its weight.
This results in negative capacity or exceeding the maximum fleet limit, causing an operational failure.
"""


class FleetResourceManager:
    def __init__(self, initial_capacity: float):
        self.available_capacity = initial_capacity
        self._lock = threading.Lock()
        self.successful_assignments = 0

    def assign_shipment(self, worker_name: str, shipment: ShipmentOrder) -> bool:
        logger.info(f"{worker_name} attempting assignment for {shipment.order_id}")

        with self._lock:
            if self.available_capacity >= shipment.total_weight:
                time.sleep(0.05)
                self.available_capacity -= shipment.total_weight
                self.successful_assignments += 1
                logger.info(f"{worker_name} SUCCESS. Remaining: {self.available_capacity}")
                return True
            else:
                logger.warning(f"{worker_name} FAILED. Remaining: {self.available_capacity}")
                return False


def run_threaded_simulation() -> None:
    manager = FleetResourceManager(initial_capacity=100.0)

    order1 = ShipmentOrder("ORD-1")
    order1.add_parcel(StandardParcel("P1", 60.0, "Tel Aviv"))

    order2 = ShipmentOrder("ORD-2")
    order2.add_parcel(StandardParcel("P2", 70.0, "Jerusalem"))

    thread1 = threading.Thread(target=manager.assign_shipment, args=("Worker-A", order1))
    thread2 = threading.Thread(target=manager.assign_shipment, args=("Worker-B", order2))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    logger.info(f"Final state - Successful assignments: {manager.successful_assignments}")
    logger.info(f"Final state - Remaining capacity: {manager.available_capacity}")
    logger.info(RACE_CONDITION_EXPLANATION)