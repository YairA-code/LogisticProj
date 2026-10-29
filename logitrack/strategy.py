from abc import ABC, abstractmethod
from typing import Any, Dict
try:
    from .models import Vehicle
except (ImportError, ValueError):
    from models import Vehicle

class PricingStrategy(ABC):
    @abstractmethod
    def calculate_final_cost(self, base_cost: float, weather_data: Dict[str, Any]) -> float:
        pass

class StandardPricingStrategy(PricingStrategy):
    def calculate_final_cost(self, base_cost: float, weather_data: Dict[str, Any]) -> float:
        return base_cost

class ExtremeWeatherPricingStrategy(PricingStrategy):
    def calculate_final_cost(self, base_cost: float, weather_data: Dict[str, Any]) -> float:
        windspeed = weather_data.get("windspeed", 0.0)
        surcharge = 50.0 if windspeed > 35.0 else 0.0
        return base_cost + surcharge


class FleetCapacityStrategy(ABC):
    @abstractmethod
    def calculate_effective_capacity(self, vehicle: Vehicle, weather_data: Dict[str, Any]) -> float:
        pass

class WeatherAdjustedCapacityStrategy(FleetCapacityStrategy):
    def calculate_effective_capacity(self, vehicle: Vehicle, weather_data: Dict[str, Any]) -> float:
        windspeed = weather_data.get("windspeed", 0.0)
        if windspeed > 35.0:
            return vehicle.max_weight_capacity * 0.8
        return float(vehicle.max_weight_capacity)