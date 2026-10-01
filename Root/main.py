from models import Driver, Vehicle, Parcel, StandardParcel, ExpressParcel, ShipmentOrder
from iterators import ParcelCollection, filter_active_vehicles, build_available_fleet_pipeline
from context_managers import FleetDispatchSession


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




    print("--- 1. Iterators ---")
    collection = ParcelCollection([
        StandardParcel("P1", 2.0, "Tel Aviv"),
        StandardParcel("P2", 3.0, "Haifa"),
        StandardParcel("P3", 1.5, "Jerusalem")
    ])

    iter1 = iter(collection)
    iter2 = iter(collection)

    print(f"איטרטור 1 מתקדם: {next(iter1).parcel_id}")
    print(f"איטרטור 2 מתקדם עצמאית: {next(iter2).parcel_id}")
    print(f"איטרטור 1 מתקדם שוב: {next(iter1).parcel_id}")


    print("\n--- 2. Generator ---")
    vehicles = [
        Vehicle("11-111", 100, "OK"),
        Vehicle("22-222", 150, "In Maintenance"),
        Vehicle("33-333", 200, "OK"),
        Vehicle("44-444", 120, "OK")
    ]


    active_gen = filter_active_vehicles(vehicles)


    first = next(active_gen)
    print(f"קריאה ראשונה עם next: {first.license_plate}")


    print("ממשיכים לעבור עם for מהמיקום שנעצרנו (ידלג על הרכב הראשון שהוצאנו):")
    for v in active_gen:
        print(f"  נשלף ב-for: {v.license_plate}")


    print("מנסים לעבור עליו שוב (לא יודפס כלום כי הוא התרוקן):")
    for v in active_gen:
        print("  (השורה הזו לא תודפס לעולם)")


    print("\n--- 3. Lazy Pipeline ---")
    vehicles[0].assign_driver(Driver("D1", "Moshe"))

    pipeline = build_available_fleet_pipeline(vehicles)


    print(f"תוצאה 1: {next(pipeline)}")
    print(f"תוצאה 2: {next(pipeline)}")
    print("-> עצרנו! שאר הנתונים לא עובדו בזיכרון.")

    print("\n--- 4. Context Manager ---")


    v1 = Vehicle("99-999-99", 120.0, "OK")
    d1 = Driver("D2", "Sara")

    print(f"לפני הבלוק - האם הנהגת פנויה? {d1.is_available}")

    try:

        with FleetDispatchSession(v1, d1) as assigned_vehicle:
            print(f"בתוך הבלוק - הנהגת {assigned_vehicle.assigned_driver.name} שויכה בהצלחה.")
            print(f"האם הנהגת פנויה כרגע? {d1.is_available}")


            print("מדמים שגיאה קריטית (למשל: משקל חורג בזמן העמסה)...")
            raise ValueError("משקל חורג! מבטל את הנסיעה.")

    except ValueError as e:

        print(f"השגיאה נתפסה בחוץ: {e}")

    print("\nאחרי היציאה מהבלוק (הוכחת Rollback):")

    print(f"מי הנהג של הרכב עכשיו? {v1.assigned_driver}")
    print(f"האם הנהגת חזרה להיות פנויה? {d1.is_available}")

if __name__ == "__main__":
    main()