# Logistics and Delivery System - Project Proposal

## Project Name and Description
**LogiTrack**: A simple Python backend system to manage parcels, calculate delivery costs, and handle shipping queues.

## Business Need
Courier companies need a way to organize packages, calculate shipping costs based on weight and type, and process urgent orders first without making manual errors.

## Main Users
1. **Warehouse Worker**: Adds new packages, updates package status, and creates delivery batches.
2. **System Administrator**: Views all shipments, filters delayed packages, and checks total costs.

## Core Process
1. A new parcel is added to the system with weight, destination, and shipping type.
2. The system checks if the data is valid (for example, weight must be positive).
3. The parcel is put into a delivery list or a priority queue.
4. The system updates the parcel status from "Pending" to "In Transit" and finally "Delivered".

## Information Flow
* **Inputs**: Parcel ID, weight, destination address, recipient name, priority level.
* **Process**: Validating input data, sorting by priority, and calculating total shipment costs.
* **Outputs**: Summary of shipments, total delivery cost, list of parcels ready for dispatch.

## Expected Business Value
Saves time for warehouse staff, prevents wrong inputs, and helps deliver urgent packages faster.

## Entities and Relationships
* `Parcel` (Base class): Holds general package info (ID, weight, status).
  * `StandardParcel` (Child class): Standard shipping with normal cost calculation.
  * `ExpressParcel` (Child class): Fast shipping with extra fee calculation.
* `ShipmentOrder` (Composition): Holds a list of `Parcel` objects and calculates total weight and total price.

## Use Cases
1. **Adding and Sorting Parcels**: Adding multiple packages and sorting them so urgent packages are handled first.
2. **Batch Processing**: Reading parcel data from a file, creating parcel objects, and getting a total cost summary.

## Future Expansion Idea
Connecting the system to a real map API (like Google Maps API) to calculate real driving distance and delivery routes.

---

## Project Structure & Implementation

```text
LogicsticProj/
├── data/
│   └── sample_data.jsonl        # Synthetic dataset of parcel records
├── logitrack/
│   ├── __init__.py              # Package entry point
│   ├── models.py                # OOP hierarchy: Parcel, StandardParcel, ExpressParcel, ShipmentOrder
│   ├── repository.py            # JSONL reading/writing and parsing logic
│   ├── processing.py            # FIFO queue (deque), Priority queue (heapq), comprehensions, sorting
│   ├── iterators.py             # ParcelCollection, ParcelIterator, and lazy generator pipeline
│   └── context_managers.py      # ParcelProcessingLock for transactional state management
├── tests/
│   └── test_logitrack.py        # Comprehensive unittest test suite
├── main.py                      # End-to-end system demonstration
└── README.md                    # Project specification and documentation
```

## How to Run

### 1. Run the Demonstration
Execute the main script to see all modules in action:
```bash
python3 main.py
```

### 2. Run the Unit Tests
Execute the test suite with `unittest`:
```bash
python3 -m unittest discover -s tests
```