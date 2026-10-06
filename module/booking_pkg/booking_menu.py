from module.authentication import (
    register_username,
    register_all
)



from module.booking_pkg.booking import (
    display_services,
    creating_booking,
    cancel_booking,
    reschedule_booking,
    find_booking,
    get_bookings,
    find_schedule_for,
    is_schedule_available,
    find_next_available_schedule,
    get_time_slots,
    get_schedules,
)
from module.utils import CUSTOMER_FILE, read_lines


from module.utils import(
    render_menu,
    draw_box,
    warning,
    error,
    info,
    pause,
    validate_date
)


def _display_table(title, headers, rows, empty_message):
    if not rows:
        print(draw_box([empty_message], title=title))
        return

    widths = [
        max(len(headers[index]), *(len(row[index]) for row in rows))
        for index in range(len(headers))
    ]
    table_lines = [
        " | ".join(header.ljust(widths[index]) for index, header in enumerate(headers)),
        "-+-".join("-" * width for width in widths),
    ]
    table_lines.extend(
        " | ".join(value.ljust(widths[index]) for index, value in enumerate(row))
        for row in rows
    )
    print(draw_box(table_lines, title=title))


def display_customers():
    customers = []
    lines = read_lines(CUSTOMER_FILE)
    for line in lines[1:]:
        parts = [part.strip() for part in line.split("|")]
        if len(parts) < 5 or parts[0].casefold() == "customer_id":
            continue
        customers.append([parts[0], parts[2], parts[3], parts[4]])

    _display_table(
        "CUSTOMER LIST",
        ["Customer ID", "Name", "Phone", "Email"],
        customers,
        "No customer records found.",
    )


def display_bookings(customer_id=None, confirmed_only=False):
    bookings = get_bookings()
    if customer_id:
        bookings = [
            booking for booking in bookings
            if booking["Customer_ID"] == customer_id
        ]
    if confirmed_only:
        bookings = [
            booking for booking in bookings
            if booking["Status"].strip().casefold() == "confirmed"
        ]

    rows = [
        [
            booking["Booking_ID"],
            booking["Customer_ID"],
            booking["Service_ID"],
            booking["Schedule_ID"],
            booking["Booking_Date"],
            booking["Status"],
        ]
        for booking in bookings
    ]
    _display_table(
        "CONFIRMED BOOKINGS" if confirmed_only else "BOOKING RECORDS",
        ["Booking ID", "Customer ID", "Service ID", "Schedule ID", "Date", "Status"],
        rows,
        "No confirmed bookings found." if confirmed_only else "No booking records found.",
    )

def booking_menu():
    while True:
        print(draw_box(["Welcome, Officer"], title = "BOOKING OFFICER"))
        print(render_menu(
            "BOOKING OFFICER",
            [
                ("1", "Register New Customer"),
                ("2", "Create Booking"),
                ("3", "Cancel Booking"),
                ("4", "Reschedule Booking"),
                ("5", "View Current Bookings / Customer Service History"),
                ("0", "Logout")
            ]
        ))

        choice = input("Choose an option: ").strip()

        if choice == "1":
            new_username = register_username()

            if new_username:
                register_all(new_username)
            else:
                print(info("Registration cancelled."))

            pause()

        elif choice == "2":
            display_customers()
            customer_id = input("Enter Customer_ID: ").strip()

            if not customer_id:
                print(error("Customer ID cannot be empty."))
                pause()
                continue

            display_services()

            service_id = input("Enter Service ID: ").strip()


            booking_date = input("Enter Date (YYYY-MM-DD): ").strip()
            if not validate_date(booking_date):
                print(error("Invalid date."))
                print(info("Please try again with YYYY-MM-DD."))


            time_slots = get_time_slots()
            if time_slots:
                print(draw_box(time_slots, title = "AVAILABLE TIME SLOTS"))
            else:
                print(warning("No time slots yet."))
                pause()
                continue
            time_slot = input("Enter Time Slot (e.g. 08:00-10:00): ").strip()
            
            
            schedule = find_schedule_for(booking_date, time_slot)
            if schedule is not None and is_schedule_available(schedule):
                creating_booking(
                    customer_id,
                    service_id,
                    schedule["Schedule_ID"],
                    schedule["Date"],
                )
                pause()
                continue

            if schedule is None:
                print(warning(
                    f"No available schedule exists for {booking_date} at {time_slot}."
                ))
            else:
                print(warning(
                    f"The schedule for {booking_date} at {time_slot} is not available."
                ))

            suggestion = find_next_available_schedule(booking_date, time_slot)

            if suggestion is None:
                print(warning("There's no available schedule."))
                pause()
                continue

            print(info("Nearest available schedule:"))
            print(draw_box(
                [
                    f"Schedule ID : {suggestion['Schedule_ID']}",
                    f"Date        : {suggestion['Date']}",
                    f"Time        : {suggestion['Time_Slot']}",
                    f"Team        : {suggestion['Team_Assigned']}",
                ],
                title="SUGGESTED SLOT",
            ))

            answer = input("Book this schedule instrad? (y/n): ").strip()

            if answer == "y" or answer == "yes":
                creating_booking(
                    customer_id,
                    service_id,
                    suggestion["Schedule_ID"],
                    suggestion["Date"]
                )
            else:
                print(info("Booking cancelled."))

            pause()

        elif choice == "3":
            display_customers()
            customer_id = input("Enter Customer ID (blank = all customers): ").strip()
            display_bookings(customer_id or None, confirmed_only=True)

            booking_id = input("Enter Booking ID: ").strip()

            booking = find_booking(booking_id)

            if booking is None:
                print(error("Booking not found."))
                pause()
                continue

            cancel_booking(booking_id)
            pause()

        elif choice == "4":
            display_customers()
            customer_id = input("Enter Customer ID (blank = all customers): ").strip()
            display_bookings(customer_id or None, confirmed_only=True)

            booking_id = input("Enter Booking ID: ").strip()

            booking = find_booking(booking_id)

            if booking is None:
                print(error("Booking not found."))
                pause()
                continue

            new_date = input("Enter New Date (YYYY-MM-DD): ").strip()
            if not validate_date(new_date):
                print(error("Invalid date. Please use YYYY-MM-DD format."))
                pause()
                continue

            available_time_slots = []
            for schedule in get_schedules():
                if (
                    schedule["Date"] == new_date
                    and is_schedule_available(schedule)
                    and schedule["Time_Slot"] not in available_time_slots
                ):
                    available_time_slots.append(schedule["Time_Slot"])

            if not available_time_slots:
                print(warning(f"No available time slots for {new_date}."))
                pause()
                continue

            print(draw_box(available_time_slots, title="AVAILABLE TIME SLOTS"))
            new_time_slot = input(
                "Enter New Time Slot (e.g. 08:00-10:00): "
            ).strip()
            new_schedule = find_schedule_for(new_date, new_time_slot)

            if new_schedule is None:
                print(warning(
                    f"No available schedule for {new_date} at {new_time_slot}."
                ))
                pause()
                continue

            reschedule_booking(
                booking_id,
                new_schedule["Schedule_ID"],
                new_schedule["Date"],
            )

            pause()

        elif choice == "5":
            display_customers()
            customer_id = input("Enter Customer ID (blank = all bookings): ").strip()
            display_bookings(customer_id or None)
            pause()

        elif choice == "0":
            print(info("Logging out..."))
            break

        else:
            print(error("Invalid choice, try again."))
            pause()