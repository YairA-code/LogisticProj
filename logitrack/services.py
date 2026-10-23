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

