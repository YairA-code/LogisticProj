import logging
from typing import List, Protocol
from dataclasses import dataclass

from logitrack.api_client import WeatherApiClient
from logitrack.models import Vehicle, Driver, ShipmentOrder

logger = logging.getLogger("logitrack.services")


@dataclass
class WeatherCondition:
    temperature: float
    wind_speed: float
    weather_code: int

    @property
    def is_severe(self) -> bool:

        return self.weather_code >= 71


class DispatchObserver(Protocol):
    def on_severe_weather(self, vehicle: Vehicle, driver: Driver, destination: str) -> None:
        pass


class FleetSafetyObserver:
    def on_severe_weather(self, vehicle: Vehicle, driver: Driver, destination: str) -> None:
        logger.warning(f"[Safety Alert] Severe weather detected for destination: {destination}!")

        driver.has_safety_warning = True
        vehicle.requires_safety_check = True


class PricingStrategy(Protocol):
    def calculate_cost(self, base_cost: float) -> float:
        pass


class NormalWeatherPricing:
    def calculate_cost(self, base_cost: float) -> float:
        return base_cost


class SevereWeatherPricing:
    def calculate_cost(self, base_cost: float) -> float:

        return base_cost * 1.20



class WeatherDispatchService:
    def __init__(self, api_client: WeatherApiClient):
        self.api_client = api_client
        self.observers: List[DispatchObserver] = []

    def add_observer(self, observer: DispatchObserver) -> None:
        self.observers.append(observer)

    def _notify_severe_weather(self, vehicle: Vehicle, driver: Driver, destination: str) -> None:
        for observer in self.observers:
            observer.on_severe_weather(vehicle, driver, destination)

    def process_dispatch(self, order: ShipmentOrder, vehicle: Vehicle, driver: Driver, lat: float, lon: float,
                         dest_name: str) -> bool:

        try:

            weather_data = self.api_client.fetch_weather(lat, lon)
            current = weather_data.get("current_weather", {})

            condition = WeatherCondition(
                temperature=current.get("temperature", 20.0),
                wind_speed=current.get("windspeed", 0.0),
                weather_code=current.get("weathercode", 0)
            )

        except Exception as e:

            logger.error(f"Weather API failed for order {order.id}. Moving to fallback. Error: {e}")
            order.requires_officer_review = True
            return False


        if condition.is_severe:
            logger.info(f"Severe weather at {dest_name}. Adjusting safety parameters.")


            effective_max_capacity = vehicle.max_weight_capacity * 0.80

            if order.total_weight > effective_max_capacity:
                logger.warning(
                    f"Order {order.id} weight ({order.total_weight}kg) exceeds weather-adjusted capacity ({effective_max_capacity}kg). Dispatch BLOCKED.")
                return False

            pricing_strategy = SevereWeatherPricing()
            order.total_cost = pricing_strategy.calculate_cost(order.total_cost)

            self._notify_severe_weather(vehicle, driver, dest_name)

        else:

            pricing_strategy = NormalWeatherPricing()
            order.total_



class WeatherShippingService:
    def __init__(self, api_client=None, capacity_strategy=None, pricing_strategy=None):
        self.api_client = api_client or WeatherApiClient()
        self.capacity_strategy = capacity_strategy or WeatherAdjustedCapacityStrategy()
        self.pricing_strategy = pricing_strategy or ExtremeWeatherPricingStrategy()
        self._observers = []

    def attach_observer(self, observer):
        self._observers.append(observer)

    def notify_observers(self, event_type: str, data: dict):
        for obs in self._observers:
            obs.update(event_type, data)

    def evaluate_shipment(self, shipment, vehicle, latitude, longitude):
        weather_data = self._fetch_weather_safe(latitude, longitude)
        windspeed = weather_data.get("windspeed", 0.0)

        effective_capacity = self.capacity_strategy.calculate_effective_capacity(vehicle, weather_data)
        final_cost = self.pricing_strategy.calculate_final_cost(shipment.total_cost, weather_data)

        if windspeed > 35.0:
            self.notify_observers("HIGH_WIND_WARNING", {"vehicle": vehicle, "windspeed": windspeed})

        is_weight_safe = shipment.total_weight <= effective_capacity

        if not is_weight_safe:
            self.notify_observers("DISPATCH_BLOCKED", {"order_id": shipment.order_id, "vehicle": vehicle})

        return {
            "order_id": shipment.order_id,
            "final_cost": final_cost,
            "effective_capacity": effective_capacity,
            "is_weight_safe": is_weight_safe
        }