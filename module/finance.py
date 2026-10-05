import os

from .utils import(
    PAYMENT_FILE,
    BOOKING_FILE,
    SERVICE_FILE,
    read_lines,
    write_lines,
    primary_key,
    validate_date,
    draw_box
)

def get_payment():

    
    payments = []
    lines = read_lines(PAYMENT_FILE)
    for line in lines[1:]:
        parts = [part.strip() for part in line.split("|")]
        if parts[0].lower() in {"payment_id"}:
            continue

        if len(parts) != 10:
            continue

        payment_id = parts[0]
        booking_id = parts[1]
        base_amount = float(parts[2])
        discount_amount = float(parts[3])
        penalty_fee = float(parts[4])
        tax_amount = float(parts[5])
        total_amount = float(parts[6])
        payment_status = parts[7]
        payment_method = parts[8]
        payment_date = parts[9]
        
        payments.append({
            "payment_id": payment_id,
            "booking_id": booking_id,
            "base_amount": base_amount,
            "discount_amount": discount_amount,
            "penalty_fee": penalty_fee,
            "tax_amount": tax_amount,
            "total_amount": total_amount,
            "payment_status": payment_status,
            "payment_method": payment_method,
            "payment_date": payment_date
            })
        
    return payments

def booking_service_id():

    booking_services = {}
    lines = read_lines(BOOKING_FILE)
    for line in lines[1:]:
        parts = [part.strip() for part in line.split("|")]
        if len(parts) != 8 or parts[0].lower() == "booking_id":
            continue

        booking_services[parts[0]] = parts[2]

    return booking_services


def service_name():

    names = {}
    lines = read_lines(SERVICE_FILE)
    for line in lines[1:]:
        parts = [part.strip() for part in line.split("|")]
        if len(parts) != 5 or parts[0].lower() == "service_id":
            continue

        names[parts[0]] = parts[1]

    return names


def service_name_from_booking(booking_id, booking_services, all_service_names):
    service_id = booking_services.get(booking_id)

    if service_id is None:
        return "Unknown Service"

    return all_service_names.get(service_id, service_id)




def income_summary():

    booking_services = booking_service_id()
    service_names = service_name()

    service_summary = {}
    total_paid_transactions = 0
    total_income = 0

    for payment in get_payment():

        status = payment["payment_status"]

        if not status.strip().lower() == "paid":
            continue

        amount = payment["total_amount"]

        total_paid_transactions += 1
        total_income += amount

        service = service_name_from_booking(
            payment["booking_id"], booking_services, service_names
        )

        if service not in service_summary:
            service_summary[service] = {"count": 0, "income": 0.0}

        service_summary[service]["count"] += 1
        service_summary[service]["income"] += amount

    summary_rows = [
        f"{service:<25}"
        f"-{details['count']}- RM{details['income']:.2f}"
        for service, details in service_summary.items()
    ]
    summary_rows.extend(
        [
            f"Total Paid Transaction : {total_paid_transactions}",
            f"Total Income : RM{total_income:.2f}",
        ]
    )
    print(draw_box(summary_rows, title="INCOME SUMMARY"))

    return {
        "total_paid_transactions": total_paid_transactions,
        "total_income": total_income,
        "per_service": service_summary,
    }



def monthly_financial_summary(month=None):

    if month is None:
        month = input("Enter Month (YYYY-MM): ")

    paid_count = 0
    unpaid_count = 0
    income = 0
    outstanding = 0


    for payment in get_payment():

        if payment["payment_date"][:7] != month:
            continue

        amount = payment["total_amount"]

        status = payment["payment_status"]

        if status.strip().lower():
            paid_count += 1
            income += amount

        else:
            unpaid_count += 1
            outstanding += amount

    print(draw_box(
        [
            f"Month: {month}",
            f"Total Paid Transactions: {paid_count}"
            f"Total Outstanding Transactions: {unpaid_count}",
            f"Total Income: RM{income:.2f}"
            f"Outstanding Amount: RM{outstanding:.2f}"
        ], "MONTHLY FINANCIAL SUMMARY"
    ))



def outstanding_payment_list():

    booking_services = booking_service_id()
    service_names = service_name()

    outstanding = []
    total_unpaid_transactions = 0
    total_unpaid_amount = 0.0
    summary_rows = []

    for payment in get_payment():
        if payment["payment_status"].strip().lower() == "paid":
            continue

        service = service_name_from_booking(
            payment["booking_id"], booking_services, service_names
        )
        record = {
            "payment_id": payment["payment_id"],
            "booking_id": payment["booking_id"],
            "service": service,
            "total_amount": payment["total_amount"],
            "payment_status": payment["payment_status"],
            "payment_date": payment["payment_date"],
        }
        outstanding.append(record)
        total_unpaid_transactions += 1
        total_unpaid_amount += record["total_amount"]

        summary_rows.extend(
            [
                f"Payment ID : {record['payment_id']}",
                f"Booking ID : {record['booking_id']}",
                f"Service : {record['service']}",
                f"Amount : RM{record['total_amount']:.2f}",
                f"Status : {record['payment_status']}",
                f"Date : {record['payment_date']}",
                "-" * 35,
            ]
        )

    if not outstanding:
        summary_rows.append("No Outstanding Payments.")

    summary_rows.extend(
        [
            f"Total Outstanding Transactions : {total_unpaid_transactions}",
            f"Total Outstanding Amount : RM{total_unpaid_amount:.2f}",
        ]
    )
    print(draw_box(summary_rows, title="OUTSTANDING PAYMENT LIST"))

    totals = {
        "total_unpaid_transactions": total_unpaid_transactions,
        "total_unpaid_amount": total_unpaid_amount,
    }
    return outstanding, totals

    
from datetime import datetime   

def generate_payment_id():

    file = open(r"C:\Users\kirel\OneDrive\Documents\Python\payments.txt","r")
    lines = file.readlines()
    file.close()

    if len(lines) == 0:
        return "P001"
    
    last_line = lines[-1]
    last_payment_id = last_line.split("|")[0]

    number = int(last_payment_id.replace("P", ""))
    number += 1
    return f"P{number:03d}"


def record_payment():

    booking_id_search = input("Enter Booking ID: ")
    if bool(booking_id_search):
        print("Booking ID entered")
#ID start with B001,B002,n+

    file = open(
        r"C:\Users\kirel\OneDrive\Documents\Python\bookings.txt",
        "r")
#better write the destination of file in full path to avoid errors

    

    for line in file:
        booking_id, customer, service, amount = line.strip().split("|")
    #status only show in payments.txt 

        if booking_id == booking_id_search:

            
            print("| Booking Found |")
            print("Customer:", customer)
            print("Service:", service)
            print("Amount: RM", amount)


            status = input("Enter Status (Paid/Unpaid): ")
            while status.lower() not in ["paid", "unpaid"]:
                print("Invalid status. Please enter 'Paid' or 'Unpaid'.")
                status = input("Enter Status (Paid/Unpaid): ")
            payment_id = generate_payment_id()
            payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            payment_file = open( r"C:\Users\kirel\OneDrive\Documents\Python\payments.txt",
            "a")

            payment_file.write(
            payment_id + "|" +
            customer + " | " +
            service + " | " +
            "RM" + amount + " | " +
            status.upper() + " | " +
            booking_id + " | " +
            payment_date + "\n"
            )

            payment_file.close()

            print("--Payment Recorded Successfully--")
            break
    else:
        print("--Booking Not Found--")
    file.close()

while True:

    record_payment()

    print("\n1. Make another payment record\n2. Exit")
    again = input("Make your choice: ")
    if again == "1":
        continue
    
    else:
        break

record_payment()