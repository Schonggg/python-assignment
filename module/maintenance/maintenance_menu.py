from ..maintenance import (
    load_equipment,
    display_equipments,

)


def maintenance_menu():
    while True:
        print("\n===== Maintenance Staff =====")
        print("1. View All Equipment")
        print("2. View Equipment Needing Service")
        print("3. Update Equipment Status")
        print("4. Record Maintenance")
        print("5. View Maintenance History")
        print("6. Generate Maintenance Summary")
        print("0. Logout")

        choice = input("Choose an option: ").strip()
        if choice == "1":
            display_equipments()

        elif choice == "2":
            customer_id = load_users(username)

            if not customer_id:
                print("Customer record not found.")
                continue

            display_services()

            service_id = input("Enter Service ID: ").strip()
            schedule_id = input("Enter Schedule ID: ").strip()
            booking_date = input(
                "Enter Booking Date (YYYY-MM-DD): "
            ).strip()

            creating_booking(
                customer_id,
                service_id,
                schedule_id,
                booking_date
            )

        elif choice == "3":
            booking_id = input("Enter Booking ID: ").strip()
            cancel_booking(booking_id)

        elif choice == "4":
            booking_id = input("Enter Booking ID: ").strip()
            new_schedule_id = input("Enter New Schedule ID: ").strip()
            new_date = input("Enter New Date (YYYY-MM-DD): ").strip()

            reschedule_booking(
                booking_id,
                new_schedule_id,
                new_date
            )

        elif choice == "5":
            customer_id = load_users(username)

            if not customer_id:
                print("Customer record not found.")
                continue

            view_customer_bookings(customer_id)

        elif choice == "0":
            print("Logging out...")
            break
        else:
            print("Invalid choice, try again.")
