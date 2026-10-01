from typing import Any

try:
    from .models import Driver, ShipmentOrder, Vehicle
except (ImportError, ValueError):
    from models import Driver, ShipmentOrder, Vehicle


def generate_fleet_utilization_report(
    vehicles: list[Vehicle], shipments: list[ShipmentOrder]
) -> dict[str, Any]:
    total_vehicles = len(vehicles)
    if total_vehicles == 0:
        return {"status": "No vehicles available"}

    in_maintenance = sum(1 for v in vehicles if v.mechanical_status == "In Maintenance")
    active_vehicles = total_vehicles - in_maintenance
    total_capacity = sum(v.max_weight_capacity for v in vehicles if v.mechanical_status == "OK")
    utilized_weight = sum(
        s.total_weight for s in shipments if s.assigned_vehicle and s.assigned_vehicle.mechanical_status == "OK"
    )
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
        "current_utilized_weight_kg": round(utilized_weight, 2),
        "utilization_percentage": round(utilization_rate, 2),
        "strategic_recommendation": recommendation,
    }


def detect_operational_anomalies(
    shipments: list[ShipmentOrder],
    valid_vehicles: list[Vehicle],
    valid_drivers: list[Driver],
) -> list[str]:
    anomalies = []
    valid_vehicle_plates = {v.license_plate for v in valid_vehicles}
    valid_driver_ids = {d.driver_id for d in valid_drivers}

    for shipment in shipments:
        vehicle = shipment.assigned_vehicle
        if vehicle:
            if vehicle.license_plate not in valid_vehicle_plates:
                anomalies.append(
                    f"Integrity Anomaly: Shipment {shipment.order_id} references unknown vehicle license plate '{vehicle.license_plate}'."
                )
            driver = vehicle.assigned_driver
            if driver and driver.driver_id not in valid_driver_ids:
                anomalies.append(
                    f"Integrity Anomaly: Vehicle {vehicle.license_plate} is driven by unregistered driver ID '{driver.driver_id}'."
                )
            if shipment.total_weight > vehicle.max_weight_capacity:
                anomalies.append(
                    f"Capacity Anomaly: Shipment {shipment.order_id} total weight ({shipment.total_weight:.2f}kg) exceeds vehicle capacity ({vehicle.max_weight_capacity:.2f}kg)."
                )
            if vehicle.mechanical_status != "OK":
                anomalies.append(
                    f"Maintenance Anomaly: Shipment {shipment.order_id} assigned to disabled vehicle {vehicle.license_plate} (Status: {vehicle.mechanical_status})."
                )

    return anomalies
