from ..utils import (
    BOOKING_FILE,
    SERVICE_FILE,
    SCHEDULE_FILE,
    CUSTOMER_FILE,
    read_lines,
    write_lines,
    primary_key,
    validate_date,
    draw_box,
    divider,
    success,
    warning,
    error,
    info
)


# SERVICE FUNCTIONS

def get_services():
    # read service records from service.txt
    # return them as a list of service dictionaries
    services = []

    lines = read_lines(SERVICE_FILE)

    # skip the first line because it contains the column headers
    for line in lines[1:]:

        parts = line.split("|")

        #to make sure the record has 5 fields
        if len(parts) != 5:
            continue

        service = {
            "Service_ID": parts[0],
            "Service_Name": parts[1],
            "Price": float(parts[2]),
            "Duration_Mins": int(parts[3]),
            "Status": parts[4]
        }

        services.append(service)

    return services


def find_service(service_id):
    #find a service usin its Service ID
    #return a dict if found, or None if not found
    services = get_services()

    for service in services:

        if service["Service_ID"] == service_id:
            return service

    return None


def display_services():
    #display all active services for the user to choose form
    services = get_services()

    found = False
    rows = []

    for service in services:

        #only display services that are currently active
        if service["Status"] == "Active":

            found = True

            rows.append(
                f'{service["Service_ID"]} | '
                f'{service["Service_Name"]} | '
                f'RM{service["Price"]:.2f} | '
                f'{service["Duration_Mins"]} mins'
            )

    if not found:
        print(warning("No active services available."))
    else:
        print(draw_box(rows, title="AVAILABLE SERVICES"))


# BOOKING FILE FUNCTIONS

def get_bookings():
    #read all booking records from bookings.txt
    #return them as a list of booking dictionaries
    bookings = []

    lines = read_lines(BOOKING_FILE)

    #skip the header line
    for line in lines[1:]:

        parts = line.split("|")

        #a booking record should contain 8 fields
        if len(parts) != 8:
            continue

        booking = {
           "Booking_ID": parts[0],
            "Customer_ID": parts[1],
            "Service_ID": parts[2],
            "Schedule_ID": parts[3],
            "Booking_Date": parts[4],
            "Status": parts[5],
            "Attendance_Status": parts[6],
            "Reschedule_Count": int(parts[7]) 
        }

        bookings.append(booking)

    return bookings


def save_bookings(bookings):
    #rewrite booking.txt with the updated booking records.
    #this function needed when a booking is cancled or reschedualed cause the existing line must be updated

    #keep the ori header
    lines = [
        "Booking_ID|Customer_ID|Service_ID|Schedule_ID|"
        "Booking_Date|Status|Attendance_Status|Reschedule_Count"
    ]

    #convert each bookin dictionnary back into txt format
    for booking in bookings:

        line = (
            f'{booking["Booking_ID"]}|'
            f'{booking["Customer_ID"]}|'
            f'{booking["Service_ID"]}|'
            f'{booking["Schedule_ID"]}|'
            f'{booking["Booking_Date"]}|'
            f'{booking["Status"]}|'
            f'{booking["Attendance_Status"]}|'
            f'{booking["Reschedule_Count"]}'
        )

        lines.append(line)

    #rewrite the whole file
    with open(BOOKING_FILE, "w", encoding="utf-8") as file:

        for line in lines:
            file.write(line + "\n")

# CREATE BOOKING

def creating_booking(customer_id, service_id, schedule_id, booking_date):
    """
    Create a new booking.

    The function checks:
    1. Whether the service exists.
    2. Whether the service is active.
    3. Whether the booking date is valid.
    4. Whether the same schedule is already booked.

    Note:
        Schedule availability is only checked against bookings.txt
        for now. Full schedule checking can be added later.
    """

    #step 1: check the service
    service = find_service(service_id)

    if service is None:
        print(error("Invalid Service ID."))
        return False

    #step 2: check whether the service is active
    if service["Status"] != "Active":
        print(warning("This service is currently unavailable."))
        return False

    if not validate_date(booking_date):
        print(error("Invalid date."))
        print(info("Please use YYYY-MM-DD format."))
        return False

    #check whether the schedule exist
    new_schedule = None
    schedules = read_lines(SCHEDULE_FILE)

    for line in schedules[1:]:
        parts = line.split("|")

        if len(parts) < 5:
            continue

        if parts[0] == schedule_id:
            new_schedule = {
                "Schedule_ID": parts[0],
                "Date": parts[1],
                "Time_Slot": parts[2],
                "Team_Assigned": parts[3],
                "Is_Booked": parts[4]
            }
            break

    #schedule does not exist
    if new_schedule is None:
        print(error("The schedule does not exist."))
        return False

    #schedule date must match booking date
    if new_schedule["Date"] != booking_date:
        print(warning("The selected schedule is not available on this date."))
        return False

    #schedule must be available
    if new_schedule["Is_Booked"].lower() == "yes":
        print(warning("The new schedule is already booked."))
        return False

    #step 4: check whether the schedule is already booked
    bookings =  get_bookings()

    for booking in bookings:

        if(
            booking["Schedule_ID"] == schedule_id
            and booking["Status"] == "Confirmed"
        ):
            print(warning("This schedule is already booked."))
            return False

    #step 5: generate a new booking id
    booking_id = primary_key(BOOKING_FILE)

    #step 6: create the booking record
    new_booking = (
        f"{booking_id}|"
        f"{customer_id}|"
        f"{service_id}|"
        f"{schedule_id}|"
        f"{booking_date}|"
        f"Confirmed|"
        f"Not Yet|"
        f"0"
    )

    #add new booking to booking.txt
    write_lines(BOOKING_FILE, new_booking)

    #update the schedule status to booked
    update_schedule_status(schedule_id, "Yes")

    #step 7: display confirmation
    print(draw_box(
        [            
            f"Booking ID : {booking_id}",
            f"Customer ID: {customer_id}",
            f"Service    : {service['Service_Name']}",
            f"Price      : RM{service['Price']:.2f}",
            f"Duration   : {service['Duration_Mins']} mins",
            f"Schedule ID: {schedule_id}",
            f"Date       : {booking_date}",
            "Status     : Confirmed",
        ],
        title="BOOKING CREATED",
    ))

    return True


# UPDATE SCHEDULE STATUS

def update_schedule_status(schedule_id, status):
    #update the Is_Booked status of a schedule.
    #the status should be "Yes" when the schedule is booked 
    #and "No" when the schedule becomes available

    lines = read_lines(SCHEDULE_FILE)

    if len(lines) == 0:
        return False

    updated_lines = []

    #keep the header
    updated_lines.append(lines[0])

    found = False

    #process schedule records
    for line in lines[1:]:
        parts = line.split("|")

        if len(parts) < 5:
            continue

        if parts[0] == schedule_id:
            parts[4] = status
            found = True

        updated_lines.append("|".join(parts))

    if not found:
        return False

    #rewrite the schedule file
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        for line in updated_lines:
            f.write(line + "\n")

    return True


# FIND BOOKING

def find_booking(booking_id):
    #find a booking usin its booking id
    #return a dict if found or None if the booking doesnt exist
    bookings = get_bookings()

    for booking in bookings:

        if booking["Booking_ID"] == booking_id:
            return booking

    return None


#CALCULATE PENALTY
def calculate_penalty(attendance_status):
    #calcualte penalty fee based on attandence status.
    #rules: 
    #- on time RM0 
    #- late RM15
    #- not yet RM0

    if attendance_status == "Late":
        return 15.00

    return 0.00


#CALCULATE LOYALTY POINTS
def calculate_loyalty_points(price, attendance_status):
    #to calculate loyalty points bsed on service price n attendance status
    #Rules:
    #- Base points: 10
    #- Price below RM50: +2
    #- Price RM50 to RM99.99: +5
    #- Price RM100 or above: +10
    #- Late: -2
    points = 10

    if price < 50:
        points += 2
    elif price < 100:
        points += 5
    else:
        points += 10

    if attendance_status == "Late":
        points -= 2

    return points


#CALCULATE LOYALTY TIER
def calculate_loyalty_tier(total_points):
    #calculate loyalty tier based on total loyalty points.
    #Rules:
    #- 0 to 49 points: Bronze
    #- 50 to 99 points: Silver
    #- 100 points or above: Gold

    if total_points < 50:
        return "Bronze"
    elif total_points < 100:
        return "Silver"
    else:
        return "Gold"


#UPDATE ATTENDANCE
def update_attendance(booking_id, attendance_status):
    #update the sttendance status of a booking
    #valid satuses:
    #- On Time
    #- Late
    bookings = get_bookings()

    #find the booking
    booking = find_booking(booking_id)

    if booking is None:
        print(error("Booking not found."))
        return False

    #only confirmed bookings can ve attendance updated
    if booking["Status"] != "Confirmed":
        print(warning("Only confirmed bookings can have their attendance updated."))
        return False

    #validate attendance status
    if attendance_status not in ["On Time", "Late"]:
        print(error("Invalid attendance status."))
        print(info("Please enter On Time or Late."))
        return False

    #update attendance status
    for record in bookings:
        if record["Booking_ID"] == booking_id:
            record["Attendance_Status"] = attendance_status
            break

    #save the updated boking reocrds
    save_bookings(bookings)

    #calculate the penalty
    penalty = calculate_penalty(attendance_status)

    print(f"Attendance for {booking_id} updated to {attendance_status}.")
    print(error(f"Penalty Fee: RM{penalty:.2f}"))

    return True


# COMPLETE BOOKING

def complete_booking(booking_id):
    bookings = get_bookings()

    booking = find_booking(booking_id)

    if booking is None:
        print(error("Booking not found"))
        return False

    if booking["Status"] != "Confirmed":
        print(warning("Only confirmed bookings can be completed."))
        return False

    for record in bookings:
        if record["Booking_ID"] == booking_id:
            record["Status"] = "Completed"
            break

    save_bookings(bookings)

    #update customer loyalty points and tier
    update_customer_loyalty(booking["Customer_ID"])

    # +5 bumped value for each equipment once booking marked as completed
    from .maintenance_pkg import get_equipments_for_service, increment_equipment_wear

    service_id = booking["Service_ID"]
    bumped = []

    for equipment_id in get_equipments_for_service(service_id):
        if increment_equipment_wear(equipment_id, 5):
            bumped.append(equipment_id)

    print(success(f"Booking {booking_id} has been marked as Completed."))

    if bumped:
        print(info(
            "Equipment wear increased for: " + ", ".join(bumped)
        ))

    return True



# CANCEL BOOKING

def cancel_booking(booking_id):
    #cancel an existing booking
    #the booking will not be deleted
    #only change its status to "Cancelled"
    #so that the bookin history is preserved
    bookings = get_bookings()

    #find the booking
    booking = find_booking(booking_id)

    if booking is None:
        print(error("Booking not found."))
        return False

    #a completed booking cannot be cancalled
    if booking["Status"] == "Completed":
        print(warning("Completed bookings cannot be cancelled."))
        return False
    
    #rmb current schedule
    old_schedule_id = booking["Schedule_ID"]

    #change the booking status
    for record in bookings:

        if record["Booking_ID"] == booking_id:
            record["Status"] = "Cancelled"
            break

    #save the updated booking records
    save_bookings(bookings)

    #release the schedule
    update_schedule_status(old_schedule_id, "No")

    print(success(f"Booking {booking_id} has been cancelled successfully."))

    return True


# RESCHEDULE BOOKING

def reschedule_booking(booking_id, new_schedule_id, new_date):
    #reschedule existing bookin
    #the function used to change the schedule_id and the booking date
    #also increace Reschedule_Count by 1
    bookings = get_bookings()

    #find the booking
    booking = find_booking(booking_id)

    if booking is None:
        print(error("Booking not found."))
        return False

    #completed bookings cannot be rescheduled
    if booking["Status"] == "Completed":
        print(warning("Completed bookings cannot be rescheduled."))
        return False

    #cancelled bookings cannot be rescheduled
    if booking["Status"] == "Cancelled":
        print(warning("Cancelled bookings cannot be rescheduled."))
        return False

    #check whether the new schedule is the same as the current schedule
    if booking["Schedule_ID"] == new_schedule_id:
        print(warning("The new schedule must be different from the current schedule."))
        return False 

    #check whether the new date is valid
    if not validate_date(new_date):
        print(error("Invalid date."))
        print(info("Please use YYYY-MM-DD format."))
        return False

    #fine the new schedule
    new_schedule = None
    schedules = read_lines(SCHEDULE_FILE)

    for line in schedules[1:]:
        parts = line.split("|")
        if len(parts) < 5:
            continue

        if parts[0] == new_schedule_id:

            new_schedule = {
                "Schedule_ID": parts[0],
                "Date": parts[1],
                "Time_Slot": parts[2],
                "Team_Assigned": parts[3],
                "Is_Booked": parts[4]
            }

            break

    #new schedule does not exist
    if new_schedule is None:
        print(error("The new schedule does not exist."))
        return False

    #the new schedule date must match the selected date
    if new_schedule["Date"] != new_date:
        print(warning("The selected schedule is not available on this date."))
        return False

    #new schedule must be available
    if new_schedule["Is_Booked"].lower() == "yes":
        print(warning("The new schedule is not available."))
        return False

    #check whther another booking alr use the new schedule
    for record in bookings:

        if (
            record["Schedule_ID"] == new_schedule_id
            and record["Booking_ID"] != booking_id
            and record["Status"] == "Confirmed"
        ):
            print(warning("The new schedule is already booked."))
            return False

    #to rmb the old schedule
    old_schedule_id = booking["Schedule_ID"]

    #update the booking
    for record in bookings:

        if record["Booking_ID"] == booking_id:

            record["Schedule_ID"] = new_schedule_id
            record["Booking_Date"] = new_date

            #increase the reschedule count
            record["Reschedule_Count"] += 1

            break

    #save the updated records
    save_bookings(bookings)

    #release the old schedule
    update_schedule_status(old_schedule_id, "No")

    #book the new schedule
    update_schedule_status(new_schedule_id, "Yes")

    print(success(f"Booking {booking_id} has been rescheduled successfully."))

    return True


# VIEW CUSTOMER BOOKING RECORDS

def view_customer_records(customer_id):
    #display all bookings belong to a customer
    #can be used by the loyalty system to calculate points 
    #based on the customer completed services
    bookings = get_bookings()

    found = False

    print(draw_box([f"Customer ID: {customer_id}"], title="CUSTOMER BOOKING RECORDS"))
    
    for booking in bookings:

        if booking["Customer_ID"] == customer_id:

            found = True

            service =  find_service(booking["Service_ID"])

            if service:
                service_name = service["Service_Name"]
            else:
                service_name = "Unknown Service"

            print(draw_box(
                [
                    f"Booking ID       : {booking['Booking_ID']}",
                    f"Service ID       : {booking['Service_ID']}",
                    f"Service Name     : {service_name}",
                    f"Schedule ID      : {booking['Schedule_ID']}",
                    f"Booking Date     : {booking['Booking_Date']}",
                    f"Status           : {booking['Status']}",
                    f"Attendance       : {booking['Attendance_Status']}",
                    f"Reschedule Count : {booking['Reschedule_Count']}",
                ]
            ))

    if not found:
        print(warning("No booking records found."))

    return found


# VIEW AVAILABLE SCHEDULES

def view_available_schedules():
    #display all available schedules
    #only schedules with Is_Booked = "No" are displayed
    #Is_Booked in schedules.txt is "No"
    #there is no Confirmed booking usnig the same Schedule_ID
    
    schedules = read_lines(SCHEDULE_FILE)
    bookings = get_bookings()

    print(divider())
    print(info("AVAILABLE SCHEDULES"))
    print(divider())

    found = False

    #skip the header
    for line in schedules[1:]:
        if not line.strip():
            continue

        parts = line.split("|")

        if len(parts) < 5:
            continue

        schedule_id = parts[0]
        schedule_date = parts[1]
        time_slot = parts[2]
        team_assigned = parts[3]
        is_booked = parts[4]

        #check whteher this schedule is ady used
        already_booked = False

        for booking in bookings:
            if(booking["Schedule_ID"] == schedule_id
               and booking["Status"] == "Confirmed"):
                already_booked = True
                break

        #only show available one
        if is_booked.lower() == "no" and not already_booked:

            found = True

            print(draw_box(
                [
                    f"Schedule ID : {schedule_id}",
                    f"Date        : {schedule_date}",
                    f"Time        : {time_slot}",
                    f"Team        : {team_assigned}",
                    f"Status      : Available",
                ]
            ))

    if not found:
        print(warning("No available schedules."))


# SCHEDULE AVAILABILITY HELPERS


def get_schedules():
    schedules = []

    lines = read_lines(SCHEDULE_FILE)

    for line in lines[1:]:
        if not line.strip():
            continue

        parts = line.split("|")

        if len(parts) != 5:
            continue

        schedule = {
            "Schedule_ID": parts[0],
            "Date": parts[1],
            "Time_Slot": parts[2],
            "Team_Assigned": parts[3],
            "Is_Booked": parts[4]
        }

        schedules.append(schedule)
    return schedules

def get_time_slots():
    slots = []

    for schedule in get_schedules():
        slot = schedule["Time_Slot"]

        if slot not in slots:
            slots.append(slot)

    return slots

def is_schedule_available(schedule):
    if schedule is None:
        return False

    if schedule["Is_Booked"].lower() == "yes":
        return False

    for booking in get_bookings():
        if(booking["Schedule_ID"] == schedule["Schedule_ID"]
                and booking["Status"] == "Confirmed"):
            return False

    return True


def find_schedule_for(date, time_slot):
    for schedule in get_schedules():
        if schedule["Date"] == date and schedule["Time_Slot"] == time_slot:
            return schedule
    return None

def find_next_available_schedule(user_date, user_time_slot):
    available = [s for s in get_schedules() if is_schedule_available(s)]
    if not available:
        return None

    #sort by date then time slot to find nearest available slot
    available.sort(key=lambda s: (s["Date"], s["Time_Slot"]))

    user_want = (user_date, user_time_slot)

    for schedule in available:
        if (schedule["Date"], schedule["Time_Slot"]) >= user_want:
            return schedule

    return available[0]



#VIEW LOYALTY POINTS
def view_loyalty_points(customer_id):
    #calculate n display loyalty points for a customer
    # only completed bookings are counted
    #points are based on service price n attendance status
    bookings = get_bookings()

    total_points = 0
    found = False

    print(draw_box([f"Customer ID: {customer_id}"], title="LOYALTY POINTS"))

    for booking in bookings:
        if booking["Customer_ID"] != customer_id:
            continue

        if booking["Status"] != "Completed":
            continue

        found = True

        service = find_service(booking["Service_ID"])

        if service is None:
            print(warning(f"Booking {booking['Booking_ID']}: Service not found."))
            continue

        service_name = service["Service_Name"]
        price = float(service["Price"])
        attendance_status = booking["Attendance_Status"]

        points = calculate_loyalty_points(
            price,
            attendance_status
        )

        total_points += points

        print(draw_box(
            [
                f"Booking ID : {booking['Booking_ID']}",
                f"Service    : {service_name}",
                f"Price      : RM{price:.2f}",
                f"Attendance : {attendance_status}",
                f"Points     : {points}",
            ]
        ))

    if not found:
        print(error("No completed bookings found."))

    tier = calculate_loyalty_tier(total_points)

    print(draw_box(
        [
            f"Total Loyalty Points: {total_points}",
            f"Loyalty Tier        : {tier}",  
        ]
    ))

    return total_points


#UPDATE CUSTOMER LOYALTY
def update_customer_loyalty(customer_id):
    #recalculate n update  customer loyalty points n tier
    bookings = get_bookings()
    total_points = 0

    for booking in bookings:
        if booking["Customer_ID"] != customer_id:
            continue

        if booking["Status"] != "Completed":
            continue

        service = find_service(booking["Service_ID"])

        if service is None:
            continue

        price = float(service["Price"])

        points = calculate_loyalty_points(
            price,
            booking["Attendance_Status"]
        )

        total_points += points

    tier = calculate_loyalty_tier(total_points)

    lines = read_lines(CUSTOMER_FILE)

    if not lines:
        return False

    updated_lines = [lines[0]]

    for line in lines[1:]:
        if not line.strip():
            continue

        parts = line.split("|")

        if len(parts) < 8:
            continue

        if parts[0] == customer_id:
            parts[6] = str(total_points)
            parts[7] = tier

        updated_lines.append("|".join(parts))

    with open(CUSTOMER_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(updated_lines) + "\n")

    return True

