from ..authentication import load_users
from module.booking_pkg.booking import (
    display_services,
    creating_booking,
    cancel_booking,
    reschedule_booking,
    view_customer_records,
    view_available_schedules,
    view_loyalty_points,
    find_booking,
    find_schedule_for,
    is_schedule_available,
    find_next_available_schedule,
    get_time_slots
)
from ..utils import (
    read_lines, 
    CUSTOMER_FILE, 
    pause, 
    warning, 
    error, 
    success, 
    info, 
    render_menu, 
    draw_box, 
    clear_screen,
    validate_date

)

def get_customer_id(username):
    """
    Find the Customer_ID that belongs to the logged-in username.
    """
    users = load_users()

    user_id = None

    for user in users:
        if user["username"].lower() == username.lower():
            user_id = user["user_id"]
            break

    if user_id is None:
        return None

    lines = read_lines(CUSTOMER_FILE)

    for line in lines[1:]:
        parts = line.split("|")

        if len(parts) < 2:
            continue

        customer_id = parts[0]
        customer_user_id = parts[1]

        if customer_user_id == user_id:
            return customer_id

    return None



def customer_menu(username):
    customer_id = get_customer_id(username)

    while True:
        print(render_menu(
            "CUSTOMER_MENU",
            [
                ("1", "View Services"),
                ("2", "Create Booking"),
                ("3", "Cancel Booking"),
                ("4", "Reschedule Booking"),
                ("5", "View Booking Records"),
                ("6", "View Available Schedules"),
                ("7", "View Loyalty Points"),
                ("0", "Logout")
            ]
        ))

        choice = input("Choose an option: ").strip()
        
        if choice == "1":
            clear_screen()
            display_services()
            pause()
            clear_screen()

        elif choice == "2":

            if not customer_id:
                print(error("Customer record not found."))
                pause()
                continue

            #display all services
            clear_screen()
            display_services()

            service_id = input("Enter Service ID: ").strip()

            #display available schedules
            booking_date = input("Enter Date (YYYY-MM-DD): ").strip()

            if not validate_date(booking_date):
                print(error("Invalid date."))
                print(info("Please use YYYY-MM-DD format."))
                pause()
                continue

            time_slots = get_time_slots()

            if time_slots:
                print(draw_box(time_slots, title="Available Time Slots"))
            else:
                print(warning("No time slots."))
                pause()
                continue

            time_slot = input("Enter Time Slot (e.g. 8:00-10:00): ").strip()


            schedule = find_schedule_for(booking_date, time_slot)

            if schedule is not None and is_schedule_available(schedule):
                
                creating_booking(
                    customer_id,
                    service_id,
                    schedule["Schedule_ID"],
                    schedule["Date"]
                )
                pause()
                continue

            if schedule is None:
                print(warning(
                    f"No schedule exist for {booking_date} at {time_slot}."

                ))

            else:
                print(warning(
                    f"The schedule for {booking_date} at {time_slot} is not available."
                ))

            suggestion = find_next_available_schedule(booking_date, time_slot)

            if suggestion is None:
                print(warning("Recently no available schedule."))
                pause()
                continue

            print(info("Nearest next available schedule: "))
            print(draw_box(
                [
                    f"Schedule ID : {suggestion['Schedule_ID']}",
                    f"Date        : {suggestion['Date']}",
                    f"Time        : {suggestion['Time_Slot']}",
                    f"Team        : {suggestion['Team_Assigned']}",
                ],
                title="SUGGESTED SLOT",
            ))

            answer = input("Book this schedule instead? (y/n): ").strip().lower()

            if answer == "y" or answer == "yes":
                creating_booking(
                    customer_id,
                    service_id,
                    suggestion["Schedule_ID"],
                    suggestion["Date"],
                )

            else:
                print(info("Booking cancelled."))

            pause()



        elif choice == "3":

            if not customer_id:
                print(error("Customer record not found."))
                continue

            booking_id = input("Enter Booking ID: ").strip()

            #check whether the booking belongs to the loggedin customer
            booking = find_booking(booking_id)

            if booking is None:
                print(error("Booking not found."))
                continue

            if booking["Customer_ID"] != customer_id:
                print(warning("You can only cancel your own booking."))
                pause()
                continue
            
            cancel_booking(booking_id)
            pause()

        elif choice == "4":

            if not customer_id:
                print(error("Customer record not found."))
                pause()
                continue

            clear_screen()
            view_customer_records(customer_id)

            booking_id = input("Enter Booking ID: ").strip()

            #check whether the booking belongs to the loggedin customer
            booking = find_booking(booking_id)

            if booking is None:
                print(error("Booking not found."))
                continue

            if booking["Customer_ID"] != customer_id:
                print(warning("You can only reschedule your own booking."))
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

        elif choice == "5":

            if not customer_id:
                print(error("Customer record not found."))
                pause()
                continue

            clear_screen()
            view_customer_records(customer_id)
            pause()

        elif choice == "6":
            clear_screen()
            view_available_schedules()
            pause()

        elif choice == "7":
            if not customer_id:
                print(error("Customer record not found."))
                pause()
                continue

            clear_screen()    
            view_loyalty_points(customer_id)
            pause()

        elif choice == "0":
            print("Logging out...")
            clear_screen()
            break

        else:
            print(error("Invalid choice, try again."))
            pause()
     