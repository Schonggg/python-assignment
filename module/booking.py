from utils import (
    BOOKING_FILE,
    SERVICE_FILE,
    read_lines,
    write_lines,
    primary_key,
    validate_date
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
        if len(parts != 8):
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

    #step 3: validate the booking date
    if not validate_date(booking_date):
        print("Invalid date.")
        print("Please use YYYY_MM_DD format.")
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


# FIND BOOKING

def find_booking(booking_id):
    #find a booking usin its booking id
    #return a dict if found or None if the booking doesnt exist
    bookings = get_bookings()

    for booking in bookings():

        if booking["Booking_ID"] == booking_id:
            return booking

    return None


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

    #change the booking status
    for record in bookings:

        if record["Booking_ID"] == booking_id:
            record["Status"] = "Cancelled"
            break

    #save the updated booking records
    save_bookings(bookings)

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

    #check whether the new date is valid
    if not validate_date(new_date):
        print("Invalid date.")
        print("Please use YYYY-MM-DD format.")
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
