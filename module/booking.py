from .utils import (
    BOOKING_FILE,
    SERVICE_FILE,
    SCHEDULE_FILE,
    read_lines,
    write_lines,
    primary_key,
    validate_date
)

print("BOOKING.PY VALIDATE_DATE:", validate_date)

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

    print(f"\n{'=' * 10} AVAILABLE SERVICES {'=' * 10}")

    found = False

    for service in services:

        #only display services that are currently active
        if service["Status"] == "Active":

            found = True

            print(
                f'{service["Service_ID"]} | '
                f'{service["Service_Name"]} | '
                f'RM{service["Price"]:.2f} | '
                f'{service["Duration_Mins"]} mins'
            )

    if not found:
        print("No active services available.")


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
        print("Invalid Service ID.")
        return False

    #step 2: check whether the service is active
    if service["Status"] != "Active":
        print("This service is currently unavailable.")
        return False

    if not validate_date(booking_date):
        print("Invalid date.")
        print("Please use YYYY-MM-DD format.")
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
        print("The schedule does not exist.")
        return False

    #schedule date must match booking date
    if new_schedule["Date"] != booking_date:
        print("The selected schedule is not available on this date.")
        return False

    #schedule must be available
    if new_schedule["Is_Booked"].lower() == "yes":
        print("The new schedule is already booked.")
        return False

    #step 4: check whether the schedule is already booked
    bookings =  get_bookings()

    for booking in bookings:

        if(
            booking["Schedule_ID"] == schedule_id
            and booking["Status"] == "Confirmed"
        ):
            print("This schedule is already booked.")
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
    print(f"\n{'=' * 10} BOOKING CREATED {'=' * 10}")
    print(f"Booking ID : {booking_id}")
    print(f"Customer ID: {customer_id}")
    print(f"Service    : {service['Service_Name']}")
    print(f"Price      : RM{service['Price']:.2f}")
    print(f"Duration   : {service['Duration_Mins']} mins")
    print(f"Schedule ID: {schedule_id}")
    print(f"Date       : {booking_date}")
    print("Status     : Confirmed")

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
        print("Booking not found.")
        return False

    #only confirmed bookings can ve attendance updated
    if booking["Status"] != "Confirmed":
        print("Only confirmed bookings can have their attendance updated.")
        return False

    #validate attendance status
    if attendance_status not in ["On Time", "Late"]:
        print("Invalid attendance status.")
        print("Please enter On Time or Late.")
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
    print(f"Penalty Fee: RM{penalty:.2f}")

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
        print("Booking not found.")
        return False

    #a completed booking cannot be cancalled
    if booking["Status"] == "Completed":
        print("Completed bookings cannot be cancelled.")
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

    print(f"Booking {booking_id} has been cancelled successfully.")

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
        print("Booking not found.")
        return False

    #completed bookings cannot be rescheduled
    if booking["Status"] == "Completed":
        print("Completed bookings cannot be rescheduled.")
        return False

    #cancelled bookings cannot be rescheduled
    if booking["Status"] == "Cancelled":
        print("Cancelled bookings cannot be rescheduled.")
        return False

    #check whether the new schedule is the same as the current schedule
    if booking["Schedule_ID"] == new_schedule_id:
        print("The new schedule must be different from the current schedule.")
        return False 

    #check whether the new date is valid
    if not validate_date(new_date):
        print("Invalid date.")
        print("Please use YYYY-MM-DD format.")
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
        print("The new schedule does not exist.")
        return False

    #the new schedule date must match the selected date
    if new_schedule["Date"] != new_date:
        print("The selected schedule is not available on this date.")
        return False

    #new schedule must be available
    if new_schedule["Is_Booked"].lower() == "yes":
        print("The new schedule is not available.")
        return False

    #check whther another booking alr use the new schedule
    for record in bookings:

        if (
            record["Schedule_ID"] == new_schedule_id
            and record["Booking_ID"] != booking_id
            and record["Status"] == "Confirmed"
        ):
            print("The new schedule is already booked.")
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

    print(f"Booking {booking_id} has been rescheduled successfully.")

    return True


# VIEW CUSTOMER BOOKING HISTORY

def view_customer_bookings(customer_id):
    #display all bookings belong to a specific customer
    #can be used by the loyalty system to calculate points 
    #based on the customer completed services
    bookings = get_bookings()

    found = False

    print(f"\n{'=' * 10} CUSTOMER BOOKING HISTORY {'=' * 10}")

    for booking in bookings:

        if booking["Customer_ID"] == customer_id:

            found = True

            service =  find_service(booking["Service_ID"])

            if service:
                service_name = service["Service_Name"]

            else:
                service_name = "Unknown Service"

            print(
                f"\nBooking ID : {booking['Booking_ID']}"
                f"\nService    : {service_name}"
                f"\nDate       : {booking['Booking_Date']}"
                f"\nStatus     : {booking['Status']}"
                f"\nAttendance : {booking['Attendance_Status']}"
                f"\nReschedule : {booking['Reschedule_Count']}"
            )

    if not found:
        print("No booking history found.")


# VIEW AVAILABLE SCHEDULES

def view_available_schedules():
    #display all available schedules
    #only schedules with Is_Booked = "No" are displayed
    #Is_Booked in schedules.txt is "No"
    #there is no Confirmed booking usnig the same Schedule_ID
    
    schedules = read_lines(SCHEDULE_FILE)
    bookings = get_bookings()

    print(f"\n{'=' * 10} AVAILABLE SCHEDULES {'=' * 10}")

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

            print(f"\nSchedule ID : {schedule_id}")
            print(f"Date        : {schedule_date}")
            print(f"Time        : {time_slot}")
            print(f"Team        : {team_assigned}")
            print(f"Status      : Available")

    if not found:
        print("\nNo available schedules.")

