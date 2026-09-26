from collections import deque
import heapq
from models import Parcel, StandardParcel, ExpressParcel, ShipmentOrder, Vehicle, Driver


def process_incoming_batch(batch_data: list[Parcel]) -> tuple[Parcel, Parcel, list[Parcel]]:
    if len(batch_data) < 2:
        raise ValueError("Batch must contain at least 2 parcels.")
    first_urgent, second_urgent, *regular_parcels = batch_data
    return (first_urgent, second_urgent, regular_parcels)

def manage_destinations(parcels: list[Parcel], restricted_destinations: list[str]) -> dict:
    destinations = {p.destination for p in parcels}
    restricted_set = set(restricted_destinations)
    destinations.add("Jerusalem")
    destinations.discard("Unknown_Destination")
    has_tel_aviv = "Tel Aviv" in destinations
    union_result = destinations.union(restricted_set)
    intersection_result = destinations.intersection(restricted_set)
    return {
        "destinations": destinations,
        "has_tel_aviv": has_tel_aviv,
        "union": union_result,
        "intersection": intersection_result
    }

class ShipmentManagerDict:
    def __init__(self, parcels: list[Parcel]):
        self.parcel_by_id: dict[str, Parcel] = {}
        self.status_counts: dict[str, int] = {}
        for p in parcels:
            if p.parcel_id in self.parcel_by_id:
                raise ValueError(f"Parcel ID '{p.parcel_id}' already exists in the system!")
            self.parcel_by_id[p.parcel_id] = p
            self.status_counts[p.status] = self.status_counts.get(p.status, 0) + 1

    def print_catalog_summary(self) -> list[str]:
        summary = []
        for parcel_id, parcel_obj in self.parcel_by_id.items():
            summary.append(
                f"Parcel ID: {parcel_id}, Destination: {parcel_obj.destination}, Status: {parcel_obj.status}")
        return summary

class DeliveryWaitlistQueue:
    def __init__(self):
        self.queue = deque()

    def add_parcel(self, parcel: Parcel):
        self.queue.append(parcel)

    def process_next_parcel(self):
        if not self.queue:
            return None
        try:
            return self.queue.popleft()
        except IndexError:
            return None

class PriorityDispatchQueue:
    def __init__(self):
        self.heap = []
        self.counter = 0

    def add_parcel_with_priority(self, parcel: Parcel, priority_level: int):
        self.counter += 1
        heapq.heappush(self.heap, (priority_level, self.counter, parcel))

    def pop_next_urgent_parcel(self) -> Parcel | None:
        if not self.heap:
            return None
        priority, _, parcel = heapq.heappop(self.heap)
        return parcel

def run_comprehensions(parcels: list[Parcel]):
    heavy_parcels = [p for p in parcels if p.weight > 10.0]
    unique_statuses = {p.status for p in parcels}
    id_to_weight = {p.parcel_id: p.weight for p in parcels}
    return heavy_parcels, unique_statuses, id_to_weight

def sort_parcels_collection(parcels: list[Parcel]):
    def get_parcel_weight(p: Parcel) -> float:
        return p.weight
    sorted_by_weight = sorted(parcels, key=get_parcel_weight)
    sorted_by_destination = sorted(parcels, key=lambda p: p.destination)
    sorted_by_status_and_weight = sorted(parcels, key=lambda p: (p.status, -p.weight))
    return sorted_by_weight, sorted_by_destination, sorted_by_status_and_weight

def validate_fleet_data_relationships(shipments: list[ShipmentOrder], valid_vehicles: list[Vehicle], valid_drivers: list[Driver]) -> list[str]:
    anomalies = []
    valid_vehicle_plates = {v.license_plate for v in valid_vehicles}
    valid_driver_ids = {d.driver_id for d in valid_drivers}
    for shipment in shipments:
        vehicle = shipment.assigned_vehicle
        if vehicle:
            if vehicle.license_plate not in valid_vehicle_plates:
                anomalies.append(f"Anomaly: Shipment {shipment.order_id} assigned to unknown vehicle {vehicle.license_plate}.")
            driver = vehicle.assigned_driver
            if driver and driver.driver_id not in valid_driver_ids:
                anomalies.append(f"Anomaly: Vehicle {vehicle.license_plate} is driven by unknown driver {driver.driver_id}.")
            if shipment.total_weight > vehicle.max_weight_capacity:
                anomalies.append(f"Anomaly: Shipment {shipment.order_id} weight ({shipment.total_weight}kg) exceeds capacity of vehicle {vehicle.license_plate} ({vehicle.max_weight_capacity}kg).")
    return anomalies

def generate_fleet_utilization_report(vehicles: list[Vehicle], shipments: list[ShipmentOrder]) -> dict:
    total_vehicles = len(vehicles)
    if total_vehicles == 0:
        return {"status": "No vehicles available"}
    in_maintenance = sum(1 for v in vehicles if v.mechanical_status == "In Maintenance")
    active_vehicles = total_vehicles - in_maintenance
    total_capacity = sum(v.max_weight_capacity for v in vehicles if v.mechanical_status == "OK")
    utilized_weight = sum(s.total_weight for s in shipments if s.assigned_vehicle and s.assigned_vehicle.mechanical_status == "OK")
    utilization_rate = (utilized_weight / total_capacity * 100) if total_capacity > 0 else 0
    recommendation = "Fleet utilization is balanced and optimal."
    if utilization_rate > 85:
        recommendation = "Warning: High fleet utilization (>85%). Consider expanding the fleet or leasing additional vehicles."
    elif in_maintenance / total_vehicles > 0.3:
        recommendation = "Warning: High maintenance rate (>30%). Review vehicle health and mechanic availability."
    return {
        "total_vehicles": total_vehicles,
        "active_vehicles": active_vehicles,
        "in_maintenance": in_maintenance,
        "total_active_capacity_kg": total_capacity,
        "current_utilized_weight_kg": utilized_weight,
        "utilization_percentage": round(utilization_rate, 2),
        "strategic_recommendation": recommendation
    }