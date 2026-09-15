from ..authentication import get_customer_id
from ..booking import (
    display_services,
    creating_booking,
    cancel_booking,
    reschedule_booking,
    view_customer_bookings
)


def customer_menu(username):
    while True:
        print("\n===== Customer =====")
        print(f"Welcome, {username}")
        print("1. View Services")
        print("2. Create Booking")
        print("3. Cancel Booking")
        print("4. Reschedule Booking")
        print("5. View Booking History")
        print("0. Logout")

        choice = input("Choose an option: ").strip()
        if choice == "1":
            display_services()

        elif choice == "2":
            customer_id = get_customer_id(username)

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
            customer_id = get_customer_id(username)

            if not customer_id:
                print("Customer record not found.")
                continue

            view_customer_bookings(customer_id)

        elif choice == "0":
            print("Logging out...")
            break
        else:
            print("Invalid choice, try again.")
