from collections import deque
import heapq
from models import Parcel, StandardParcel, ExpressParcel  # [cite: 2]

def process_incoming_batch(batch_data):
    first_urgent, second_urgent, *regular_parcels = batch_data
    processing_list = list(regular_parcels)
    return first_urgent, second_urgent, processing_list

def manage_destinations(parcels):
    destinations = set()
    for p in parcels:
        destinations.add(p.destination)

    if "Tel Aviv" in destinations:
        print("We have deliveries to Tel Aviv today.")
    destinations.discard("Unknown")
    return destinations

def create_dictionaries(parcels):
    parcel_by_id = {}
    for p in parcels:
        if p.parcel_id in parcel_by_id:
            print(f"Warning: Parcel {p.parcel_id} already exists. Overwrite denied.")
        else:
            parcel_by_id[p.parcel_id] = p
    status_counts = {}
    for p in parcels:
        status_counts[p.status] = status_counts.get(p.status, 0) + 1
    for status, count in status_counts.items():
        print(f"Status '{status}': {count} parcels")
    return parcel_by_id, status_counts

def fifo_queue_process(parcels):
    queue = deque()
    for p in parcels[:4]:
        queue.append(p)
    processed = []
    while queue:
        try:
            current_parcel = queue.popleft()
            processed.append(current_parcel)
        except IndexError:
            break
    return processed

def priority_queue_process(parcels):
    pq = []
    counter = 0
    for p in parcels[:3]:
        priority = 1 if isinstance(p, ExpressParcel) else 2
        heapq.heappush(pq, (priority, counter, p))
        counter += 1
    if pq:
        highest_priority_item = heapq.heappop(pq)
        return highest_priority_item[2]
    return None

def comprehensions_examples(parcels):
    heavy_parcels = [p for p in parcels if p.weight > 10.0]
    unique_statuses = {p.status for p in parcels}
    id_to_weight = {p.parcel_id: p.weight for p in parcels}
    return heavy_parcels, unique_statuses, id_to_weight

def sorting_examples(parcels):
    def get_weight(p):
        return p.weight
    sorted_by_weight = sorted(parcels, key=get_weight)
    sorted_by_destination = sorted(parcels, key=lambda p: p.destination)
    sorted_by_status_and_weight = sorted(parcels, key=lambda p: (p.status, p.weight))
    return sorted_by_weight, sorted_by_destination, sorted_by_status_and_weight