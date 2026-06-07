import requests

BASE_URL = "http://127.0.0.1:8000"


def create_event():
    name = input("Event name: ")
    seats = input("Total seats: ")
    date = input("Event date (e.g. 2027-01-01T10:00:00Z): ")

    reg = requests.post(f"{BASE_URL}/events/", json={
        "name": name,
        "total_seats": int(seats),
        "event_date": date
    })

    data = reg.json()
    if reg.status_code == 201:
        print(f"✅ Event created — ID: {data['id']}")
    else:
        print(f"❌ {data['detail']}")


def list_events():
    reg = requests.get(f"{BASE_URL}/events/", params={"sort_by_date": True})
    events = reg.json()

    if not events:
        print("No events found")
        return

    for e in events:
        print(f"[{e['id']}] {e['name']} | {e['event_date']} | Seats available: {e['available_seats']}")


def register_user():
    user_name=input("Your name: ")
    event_id=input("Event ID: ")

    reg=requests.post(f"{BASE_URL}/registrations/", json={
        "user_name": user_name,
        "event_id": int(event_id)
    })

    data = reg.json()
    if reg.status_code == 201:
        print(f"✅ Registered — Registration ID: {data['id']}")
    else:
        print(f"❌ {data['detail']}")


def cancel_registration():
    user_name=input("Your name: ")

    reg=requests.get(f"{BASE_URL}/registrations/user/{user_name}")
    registrations=reg.json()

    if not registrations:
        print("No active registrations found")
        return

    for reg in registrations:
        print(f"[{reg['id']}] Event ID: {reg['event_id']} | Registered at: {reg['registered_at']}")

    reg_id = input("Enter Registration ID to cancel: ")

    reg = requests.delete(f"{BASE_URL}/registrations/{reg_id}")
    data = reg.json()
    if reg.status_code == 200:
        print(f"✅ Registration {reg_id} cancelled")
    else:
        print(f"❌ {data['detail']}")


def main():
    print("== Event Registration System ==")

    while True:
        print("\n1. Create event")
        print("2. List events")
        print("3. Register for event")
        print("4. Cancel registration")
        print("5. Exit")

        choice = input("\nChoose: ")

        if choice == "1":
            create_event()
        elif choice == "2":
            list_events()
        elif choice == "3":
            register_user()
        elif choice == "4":
            cancel_registration()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid option")


if __name__ == "__main__":
    main()