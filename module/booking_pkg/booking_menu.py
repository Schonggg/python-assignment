from ..authentication import (
    register_username,
    register_all
)



from module.booking_pkg.booking import (
    display_services,
    view_available_schedules,
    creating_booking,
    cancel_booking,
    reschedule_booking,
    view_customer_records,
    find_booking,
    get_bookings,
    find_schedule_for,
    is_schedule_available,
    find_next_available_schedule,
    get_time_slots,
)



from ..utils import(
    render_menu,
    draw_box,
    divider,
    success,
    warning,
    error,
    info,
    pause,
    validate_date
)

def display_bookings():

    bookings = get_bookings()

    if not bookings:
        print(warning("No booking records found."))
        return

    print(draw_box(["All Bookings"], title = "BOOKING RECORDS"))

    for booking in bookings:
        print(draw_box(
            [
                f"Booking ID       : {booking['Booking_ID']}",
                f"Customer ID      : {booking['Customer_ID']}",
                f"Service ID       : {booking['Service_ID']}",
                f"Schedule ID      : {booking['Schedule_ID']}",
                f"Booking Date     : {booking['Booking_Date']}",
                f"Status           : {booking['Status']}",
                f"Attendance       : {booking['Attendance_Status']}",
                f"Reschedule Count : {booking['Reschedule_Count']}"
            ]

        ))

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
            
            
            schedule = find_schedule_for(booking_date, time_slots)
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
                    f"No schedule exists for {booking_date} at {time_slots}."
                ))
            else:
                print(warning(
                    f"The schedule for {booking_date} at {time_slots} is not available."
                ))

            suggestion = find_next_available_schedule(booking_date, time_slots)

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
            customer_id = input("Enter Customer ID (blank = all bookings): ").strip()

            if customer_id:
                view_customer_records(customer_id)

            else:
                display_bookings()

            booking_id = input("Enter Booking ID: ").strip()

            booking = find_booking(booking_id)

            if booking is None:
                print(error("Booking not found."))
                pause()
                continue

            cancel_booking(booking_id)
            pause()

        elif choice == "4":
            customer_id = input("Enter Customer ID (blank = all bookings): ").strip()

            if customer_id:
                view_customer_records(customer_id)

            else:
                display_bookings()

            booking_id = input("Enter Booking ID: ").strip()

            booking = find_booking(booking_id)

            if booking is None:
                print(error("Booking not found."))
                pause()
                continue

            view_available_schedules()

            new_schedule_id = input("Enter New Schedule ID: ").strip()
            new_date = input("Enter New Date (YYYY-MM-DD): ").strip()

            reschedule_booking(
                booking_id,
                new_schedule_id,
                new_date
            )

            pause()


        elif choice == "0":
            print(info("Logging out..."))
            break

        else:
            print(error("Invalid choice, try again."))
            pause()