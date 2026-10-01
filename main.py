from models import Driver, Vehicle, Parcel, StandardParcel, ExpressParcel, ShipmentOrder


def main():
    print("=== בדיקת מערכת LogiTrack ===")

    print("\n--- 1. יצירת נהגים ---")
    driver1 = Driver(driver_id="D001", name="Yair")
    driver2 = Driver.from_dict({"driver_id": "D002", "name": "Liem", "is_available": True})
    print(driver1)
    print(driver2)

    print("\n--- 2. יצירת רכבים ובדיקת וולידציה ---")
    vehicle1 = Vehicle(license_plate="123-45-678", max_weight_capacity=100.0)
    print(vehicle1)

    print("מנסים ליצור רכב עם משקל שלילי:")
    try:
        vehicle2 = Vehicle(license_plate="000-00-000", max_weight_capacity=-50)
    except ValueError as e:
        print(f"שגיאה נתפסה בהצלחה: {e}")

    print("\n--- 3. יצירת חבילות ---")
    parcel1 = Parcel.create_from_dict({"id": "P101", "weight": 10.0, "destination": "Tel Aviv", "type": "standard"})
    parcel2 = Parcel.create_from_dict({"id": "P102", "weight": 5.0, "destination": "Haifa", "type": "express"})
    parcel3 = ExpressParcel(parcel_id="P103", weight=12.0, destination="Jerusalem")

    print(parcel1)
    print(parcel2)

    print("\n--- 4. יצירת הזמנת משלוח וחישובים ---")
    order = ShipmentOrder(order_id="ORD-999")

    order.add_parcel(parcel1)
    order.add_parcel(parcel2)
    order.add_parcel(parcel3)

    print(f"כמות חבילות בהזמנה: {len(order)}")
    print(f'משקל כולל: {order.total_weight} ק"ג')
    print(f'עלות כוללת: {order.total_cost} ש"ח')

    print("\n--- 5. יציאה למשלוח (שינוי מצב כולל) ---")
    vehicle1.assign_driver(driver1)
    print(f"הנהג {driver1.name} שובץ לרכב {vehicle1.license_plate}.")

    print("משגרים את ההזמנה...")
    order.dispatch(vehicle1)

    print(order)

    print("סטטוס החבילות עודכן אוטומטית:")
    for p in order.parcels:
        print(f" - חבילה {p.parcel_id}: {p.status}")


if __name__ == "__main__":
    main()