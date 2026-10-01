"""Main Demonstration Script for LogiTrack Logistics Management System.

This script executes the complete end-to-end operational scenario.
Per project requirements, NO business classes are defined here;
all components are imported from the logitrack package.
"""

from pathlib import Path

from logitrack import (
    DeliveryWaitlistQueue,
    Driver,
    ExpressParcel,
    FleetDispatchSession,
    ParcelCollection,
    ParcelRepository,
    PriorityDispatchQueue,
    ShipmentManagerDict,
    ShipmentOrder,
    StandardParcel,
    Vehicle,
    VehicleRepository,
    build_available_fleet_pipeline,
    build_urgent_parcels_pipeline,
    filter_active_vehicles,
    generate_fleet_utilization_report,
    manage_destinations,
    process_incoming_batch,
    run_comprehensions,
    sort_parcels_collection,
    validate_fleet_data_relationships,
)


def print_header(title: str) -> None:
    print(f"\n{'=' * 25} {title} {'=' * 25}")


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    parcels_file = base_dir / "data" / "sample_data.jsonl"
    vehicles_file = base_dir / "data" / "vehicles_data.jsonl"

    print_header("LogiTrack Logistics System - Full Demonstration")

    # -------------------------------------------------------------------------
    # 1. DATA REPOSITORY: Lazy Loading & Find by ID
    # -------------------------------------------------------------------------
    print_header("1. Data Repository & Lazy Loading (repository.py)")
    repo = ParcelRepository(parcels_file)
    print(f"Loading parcels from: {parcels_file.relative_to(base_dir)}")

    all_parcels = repo.get_all()
    print(f"Successfully loaded {len(all_parcels)} parcels into memory.")

    print("\n[Query: find_by_id]")
    target_id = "P102"
    found = repo.find_by_id(target_id)
    print(f" - Searching for '{target_id}': Found -> {found}")

    missing_id = "P999"
    not_found = repo.find_by_id(missing_id)
    print(f" - Searching for '{missing_id}': Result -> {not_found}")

    # -------------------------------------------------------------------------
    # 2. BUSINESS MODELS: Inheritance, Polymorphism & Validation
    # -------------------------------------------------------------------------
    print_header("2. Business Models, Polymorphism & Validation (models.py)")
    driver1 = Driver(driver_id="D101", name="Yair")
    driver2 = Driver(driver_id="D102", name="Liem")
    print(f"Created drivers:\n  {driver1}\n  {driver2}")

    vehicle1 = Vehicle(license_plate="11-222-33", max_weight_capacity=150.0, mechanical_status="OK")
    vehicle2 = Vehicle(license_plate="44-555-66", max_weight_capacity=80.0, mechanical_status="In Maintenance")
    print(f"\nCreated vehicles:\n  {vehicle1}\n  {vehicle2}")

    print("\n[Validation Check: Creating Vehicle with invalid capacity]")
    try:
        Vehicle(license_plate="99-999-99", max_weight_capacity=-10.0)
    except ValueError as e:
        print(f"  [Handled correctly] Caught expected error: {e}")

    print("\n[Polymorphism Check: Cost calculation per parcel type]")
    sp = StandardParcel(parcel_id="SP-1", weight=10.0, destination="Tel Aviv")
    ep = ExpressParcel(parcel_id="EP-1", weight=10.0, destination="Tel Aviv")
    print(f"  StandardParcel (10kg): {sp.calculate_cost()} ILS (rate: 15/kg)")
    print(f"  ExpressParcel  (10kg): {ep.calculate_cost()} ILS (rate: 15/kg + 50 surcharge)")

    # -------------------------------------------------------------------------
    # 3. ITERABLES, ITERATORS, GENERATORS & LAZY PIPELINES
    # -------------------------------------------------------------------------
    print_header("3. Iterators, Generators & Lazy Pipeline (iterators.py)")
    sample_subset = all_parcels[:3]
    collection = ParcelCollection(sample_subset)
    print(f"Iterating over custom ParcelCollection (length={len(collection)}):")
    for idx, p in enumerate(collection, start=1):
        print(f"  [{idx}] {p}")

    print("\n[Generator: filter_active_vehicles]")
    v_repo = VehicleRepository(vehicles_file)
    fleet = list(v_repo.load_vehicles())
    active_vehicles = list(filter_active_vehicles(fleet))
    print(f"  Active vehicles in operational status: {len(active_vehicles)} of {len(fleet)}")
    for v in active_vehicles:
        print(f"   - {v.license_plate} (Capacity: {v.max_weight_capacity}kg)")

    print("\n[Lazy Pipeline: build_available_fleet_pipeline]")
    pipeline = build_available_fleet_pipeline(fleet)
    print("  Consuming pipeline stages lazily (on-demand):")
    for item in pipeline:
        print(f"   - Pipeline yield: Plate={item['license_plate']}, Available Cap={item['available_capacity_kg']}kg")

    # -------------------------------------------------------------------------
    # 4. PROCESSING: Collections, Comprehensions & Sorting
    # -------------------------------------------------------------------------
    print_header("4. Collections Processing, Comprehensions & Sorting (processing.py)")

    print("[Tuple Unpacking: process_incoming_batch]")
    urgent_1, urgent_2, regulars = process_incoming_batch(all_parcels[:6])
    print(f"  First urgent:  {urgent_1.parcel_id} ({urgent_1.destination})")
    print(f"  Second urgent: {urgent_2.parcel_id} ({urgent_2.destination})")
    print(f"  Regular batch: {[p.parcel_id for p in regulars]}")

    print("\n[Set Operations: Destinations Management]")
    dest_info = manage_destinations(all_parcels)
    print(f"  Unique destinations count: {len(dest_info['destinations'])}")
    print(f"  Has delivery to Tel Aviv: {dest_info['has_tel_aviv']}")
    print(f"  Intersection with restricted zones: {dest_info['intersection']}")

    print("\n[Comprehensions: List, Set, Dict]")
    heavy, statuses, id_weights = run_comprehensions(all_parcels)
    print(f"  Heavy parcels count (>3kg): {len(heavy)}")
    print(f"  Unique parcel statuses: {statuses}")
    print(f"  Sample id->weight mapping (first 3): {dict(list(id_weights.items())[:3])}")

    print("\n[Sorting: Custom Key, Lambda & Multi-key]")
    by_weight, by_dest, by_status_weight = sort_parcels_collection(all_parcels[:5])
    print(f"  Sorted by weight: {[p.weight for p in by_weight]}")
    print(f"  Sorted by destination: {[p.destination for p in by_dest]}")
    print(f"  Sorted by status & weight: {[(p.status, p.weight) for p in by_status_weight]}")

    print("\n[Priority Queue (heapq) vs FIFO Queue (deque)]")
    pq = PriorityDispatchQueue()
    pq.add_parcel_with_priority(all_parcels[0], priority_level=2)  # Standard
    pq.add_parcel_with_priority(all_parcels[1], priority_level=1)  # Express
    pq.add_parcel_with_priority(all_parcels[3], priority_level=1)  # Express
    print(f"  Popped highest priority parcel: {pq.pop_next_urgent_parcel()}")

    fifo = DeliveryWaitlistQueue()
    fifo.add_parcel(all_parcels[0])
    fifo.add_parcel(all_parcels[1])
    print(f"  Popped FIFO parcel: {fifo.process_next_parcel()}")

    # -------------------------------------------------------------------------
    # 5. CUSTOM CONTEXT MANAGER: Transactional Driver Assignment & Rollback
    # -------------------------------------------------------------------------
    print_header("5. Context Manager & Transaction Rollback (context_managers.py)")
    test_vehicle = Vehicle(license_plate="99-888-77", max_weight_capacity=200.0, mechanical_status="OK")
    test_driver = Driver(driver_id="D999", name="Eitan", is_available=True)

    print("Initial state:")
    print(f"  Vehicle driver: {test_vehicle.assigned_driver}, Driver available: {test_driver.is_available}")

    print("\n[Test 1: Successful Context Session]")
    with FleetDispatchSession(test_vehicle, test_driver) as v:
        print(f"  Inside session -> Vehicle driver: {v.assigned_driver.name}, Driver available: {test_driver.is_available}")

    print(f"After session commit -> Vehicle driver: {test_vehicle.assigned_driver.name}, Driver available: {test_driver.is_available}")

    print("\n[Test 2: Failed Session with Automatic Rollback]")
    test_vehicle.release_driver()
    try:
        with FleetDispatchSession(test_vehicle, test_driver):
            print(f"  Inside session -> Driver assigned: {test_vehicle.assigned_driver.name}")
            print("  Simulating unexpected operational failure...")
            raise RuntimeError("Database connection lost during loading.")
    except RuntimeError as err:
        print(f"  [Handled] Caught exception: {err}")

    print("After rollback:")
    print(f"  Vehicle driver: {test_vehicle.assigned_driver} (restored)")
    print(f"  Driver available: {test_driver.is_available} (restored)")

    # -------------------------------------------------------------------------
    # 6. BUSINESS ACTIONS: Shipment Dispatch & Management Report
    # -------------------------------------------------------------------------
    print_header("6. Business Actions & Fleet Utilization Report")
    order = ShipmentOrder(order_id="ORD-2026-001")
    for p in all_parcels[:4]:
        order.add_parcel(p)

    print(f"Created Shipment Order: {order}")
    print(f"Total Weight: {order.total_weight:.2f} kg | Total Cost: {order.total_cost:.2f} ILS")

    dispatch_vehicle = active_vehicles[0]
    dispatch_driver = Driver(driver_id="D500", name="Dan", is_available=True)
    dispatch_vehicle.assign_driver(dispatch_driver)

    print(f"\nDispatching {order.order_id} onto Vehicle {dispatch_vehicle.license_plate}...")
    order.dispatch(dispatch_vehicle)
    print(f"Order status updated: {order}")
    print(f"Parcels dispatched: {[f'{p.parcel_id}: {p.status}' for p in order.parcels]}")

    print("\n[Strategic Decision Support: Fleet Utilization Report]")
    report = generate_fleet_utilization_report(fleet, [order])
    for key, value in report.items():
        print(f"  {key}: {value}")

    print_header("LogiTrack Demonstration Completed Successfully!")


if __name__ == "__main__":
    main()
