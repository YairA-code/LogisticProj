import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

logger = logging.getLogger("logitrack.observers")

class DispatchObserver(ABC):
    @abstractmethod
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        pass

class FleetSafetyObserver(DispatchObserver):
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        if event_type == "HIGH_WIND_WARNING":
            vehicle = data.get("vehicle")
            windspeed = data.get("windspeed")
            if vehicle:
                logger.warning(f"[Safety Alert] Vehicle {vehicle.license_plate} is facing {windspeed} km/h winds. Driver notified to reduce speed.")

class DelayStatisticsObserver(DispatchObserver):
    def __init__(self):
        self.delayed_shipments_count = 0

    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        if event_type == "DISPATCH_BLOCKED":
            order_id = data.get("order_id")
            self.delayed_shipments_count += 1
            logger.info(f"[Analytics] Shipment {order_id} delayed. Total delayed today: {self.delayed_shipments_count}")