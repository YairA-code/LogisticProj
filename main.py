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
    detect_operational_anomalies,
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

    print_header("3. Iterators, Generators & Lazy Pipeline (iterators.py)")
    sample_subset = all_parcels[:3]
    collection = ParcelCollection(sample_subset)
    print(f"ParcelCollection created with {len(collection)} parcels.")

    print("\n[Two Independent Iterators on Same Collection]")
    it1 = iter(collection)
    it2 = iter(collection)
    print(f"  Iterator 1 (step 1): {next(it1)}")
    print(f"  Iterator 2 (step 1): {next(it2)}")
    print(f"  Iterator 1 (step 2): {next(it1)}")
    print(f"  Iterator 2 (step 2 - independent): {next(it2)}")

    print("\n[Generator with yield: filter_active_vehicles]")
    v_repo = VehicleRepository(vehicles_file)
    fleet = list(v_repo.load_vehicles())
    gen = filter_active_vehicles(fleet)
    print("  Created generator object without processing all data yet.")
    first_active = next(gen)
    print(f"  Single call via next(): {first_active.license_plate} (resumed state)")
    print("  Continuing iteration via for loop:")
    for v in gen:
        print(f"   - {v.license_plate} (Capacity: {v.max_weight_capacity}kg)")
    print("  Verifying generator exhaustion:")
    exhausted_items = list(gen)
    print(f"  Items left in exhausted generator: {len(exhausted_items)} (requires creating a new generator)")

    print("\n[Lazy Pipeline: build_available_fleet_pipeline]")
    pipeline = build_available_fleet_pipeline(fleet)
    print("  Consuming ONLY first 2 results and stopping (per rubric):")
    res1 = next(pipeline)
    print(f"  [1] Plate={res1['license_plate']}, Capacity={res1['available_capacity_kg']}kg")
    res2 = next(pipeline)
    print(f"  [2] Plate={res2['license_plate']}, Capacity={res2['available_capacity_kg']}kg")
    print("  Pipeline execution halted: subsequent items were never evaluated.")

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
    pq.add_parcel_with_priority(all_parcels[0], priority_level=2)
    pq.add_parcel_with_priority(all_parcels[1], priority_level=1)
    pq.add_parcel_with_priority(all_parcels[3], priority_level=1)
    print(f"  Popped highest priority parcel: {pq.pop_next_urgent_parcel()}")

    fifo = DeliveryWaitlistQueue()
    fifo.add_parcel(all_parcels[0])
    fifo.add_parcel(all_parcels[1])
    print(f"  Popped FIFO parcel: {fifo.process_next_parcel()}")

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

    print_header("6. Fleet Subsystem Actions, Anomaly Detection & Strategic Report")

    print("[Subsystem Business Actions: Fleet Management]")
    test_sub_vehicle = Vehicle(license_plate="33-444-55", max_weight_capacity=100.0, mechanical_status="OK")
    test_sub_driver = Driver(driver_id="D777", name="Ronen", is_available=True)
    test_sub_vehicle.assign_driver(test_sub_driver)
    print(f"  Assigned driver: {test_sub_vehicle.assigned_driver.name}, Driver available: {test_sub_driver.is_available}")

    test_sub_vehicle.send_to_maintenance()
    print(f"  Sent to maintenance: Status={test_sub_vehicle.mechanical_status}, Driver released: {test_sub_vehicle.assigned_driver is None}, Driver available: {test_sub_driver.is_available}")

    test_sub_vehicle.mark_as_repaired()
    print(f"  Vehicle repaired: Status={test_sub_vehicle.mechanical_status}")

    print("\n[Business Process: Shipment Dispatch & State Transitions]")
    order = ShipmentOrder(order_id="ORD-2026-001")
    for p in all_parcels[:4]:
        order.add_parcel(p)

    print(f"  Created Shipment Order: {order}")
    print(f"  Total Weight: {order.total_weight:.2f} kg | Total Cost: {order.total_cost:.2f} ILS")

    dispatch_vehicle = next(filter_active_vehicles(fleet))
    dispatch_driver = Driver(driver_id="D500", name="Dan", is_available=True)
    dispatch_vehicle.assign_driver(dispatch_driver)

    print(f"\nDispatching {order.order_id} onto Vehicle {dispatch_vehicle.license_plate}...")
    order.dispatch(dispatch_vehicle)
    print(f"  Order status updated: {order}")
    print(f"  Parcels dispatched: {[f'{p.parcel_id}: {p.status}' for p in order.parcels]}")

    print("\n[Data Relationships & Anomaly Detection Check]")
    valid_anomalies = detect_operational_anomalies([order], fleet, [dispatch_driver, driver1, driver2, test_sub_driver])
    print(f"  Anomalies in verified fleet operation: {len(valid_anomalies)} (Clean)")

    anomalous_vehicle = Vehicle(license_plate="UNKNOWN-99", max_weight_capacity=5.0, mechanical_status="In Maintenance")
    anomalous_driver = Driver(driver_id="UNREGISTERED-D", name="Ghost", is_available=True)
    anomalous_vehicle.assigned_driver = anomalous_driver
    anomalous_order = ShipmentOrder(order_id="ORD-ANOMALY-999")
    anomalous_order.parcels = all_parcels[:3]
    anomalous_order.assigned_vehicle = anomalous_vehicle

    detected = detect_operational_anomalies([anomalous_order], fleet, [driver1, driver2])
    print(f"  Simulated anomaly test detected {len(detected)} integrity violations:")
    for a in detected:
        print(f"   - {a}")

    print("\n[Strategic Decision Support: Fleet Utilization Report (reports.py)]")
    report = generate_fleet_utilization_report(fleet, [order])
    for key, value in report.items():
        print(f"  {key}: {value}")

    print_header("LogiTrack Demonstration Completed Successfully!")


if __name__ == "__main__":
    main()
