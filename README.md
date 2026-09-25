**Logistics and Delivery System - Project Proposal**

***Project Name and Description***

LogiTrack: A Python backend system to manage parcels, prioritize shipments, and manage a fleet of delivery vehicles.

**Business Need**

Courier companies need a way to organize packages, calculate shipping costs, process urgent orders first, and efficiently manage their fleet of delivery vehicles. This system prevents manual routing errors, avoids delays of express packages, and maximizes vehicle capacity utilization while tracking mechanical maintenance.

**Main Users**

Warehouse Worker: Receives new packages, updates their status, and creates delivery batches.

Fleet Manager: Manages the vehicle fleet, tracks their mechanical status, and assigns drivers to shifts/vehicles.

System Administrator: Views all shipments and generates reports on delays, costs, and fleet utilization.

**Core Process**

A new parcel is added to the system (weight, destination, priority level) and verified.

The parcel is placed into either a standard waitlist or a priority queue.

The Fleet Manager assigns available drivers to mechanically sound vehicles.

The system dispatches shipments by pulling the most urgent parcels and loading them onto available vehicles (up to their maximum weight capacity).

The parcel status updates from "Pending" to "In Transit" and finally "Delivered".

**Information Flow**

Inputs: Parcel details (ID, weight, destination, priority), Vehicle details (capacity, mechanical status), and Driver details.

Process: Validating input data, sorting parcels by priority, assigning drivers to vehicles, and matching shipment total weights to vehicle capacities.

Outputs: Summary of ready-to-dispatch shipments, list of out-of-service vehicles, and fleet utilization reports.

**Expected Business Value**

Saves time for warehouse staff, delivers urgent packages faster, ensures deliveries only happen with mechanically safe vehicles, and provides clear data for strategic management decisions regarding fleet expansion.

**Entities and Relationships**

**Main System (Parcels):**

Parcel (Base class): Holds general package info (ID, weight, status).

StandardParcel (Child class): Standard shipping with normal cost calculation.

ExpressParcel (Child class): Fast shipping with extra fee calculation.

ShipmentOrder (Composition): Holds a list of Parcel objects and calculates total weight and total price.

**Sub-System (Fleet Management):**

Vehicle: Holds data such as license plate, max weight capacity, and mechanical status.

Driver: Holds driver information and availability status.

Relationships & New Business Actions:

A ShipmentOrder is assigned to a Vehicle (driven by a Driver), ensuring the shipment's total weight does not exceed the vehicle's max capacity.

**Business Actions:**

Assigning a driver to a vehicle.

Updating a vehicle's mechanical status (e.g., marking as "In Maintenance").

Allocating a ShipmentOrder to a specific Vehicle.

**Supported Business Decision / Report:**

Fleet Utilization Report: The system calculates the ratio of active vs. in-maintenance vehicles and the weight capacity utilization of the active ones. This data supports a critical management decision: whether the company needs to lease/buy more vehicles due to capacity limits, or if they just need to optimize their current routing.

**Use Cases**

Handling Peak Shipment Loads (Warehouse Worker): A warehouse worker receives dozens of morning packages, marking several as 'Express'. Business Goal: The system automatically prioritizes these express packages for the next immediate delivery batch. This ensures the company meets its guaranteed Service Level Agreements (SLA) for fast shipping and maintains high customer satisfaction.

Daily Fleet Dispatch (Fleet Manager): The fleet manager reviews the list of vehicles, marks one as "In Maintenance" due to a needed oil change, and assigns drivers to the remaining functional fleet. Business Goal: Ensure deliveries are only dispatched on safe, functional vehicles with sufficient weight capacity. This minimizes on-road breakdowns, prevents delivery delays, and maximizes daily driver efficiency.

**Future Expansion Idea**

Connecting the system to a real map API (like Google Maps API) to calculate real driving distances, optimize delivery routes for the assigned vehicles, and provide customers with live ETAs.
