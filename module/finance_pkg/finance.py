import os
from module.maintenance_pkg.maintenance import get_maintenance_records

from ..utils import(
    PAYMENT_FILE,
    BOOKING_FILE,
    SERVICE_FILE,
    read_lines,
    write_lines,
    primary_key,
    validate_date,
    draw_box,
    error,
    warning,
    success,
    info
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
    income = 0.0
    outstanding = 0.0
    maintenance_expenses = sum(
        record["cost"]
        for record in get_maintenance_records()
        if record["maintenance_date"][:7] == month
    )


    for payment in get_payment():

        if payment["payment_date"][:7] != month:
            continue

        amount = payment["total_amount"]

        status = payment["payment_status"]

        if status.strip().lower() == "paid":
            paid_count += 1
            income += amount

        else:
            unpaid_count += 1
            outstanding += amount

    print(draw_box(
        [
            f"Month: {month}",
            f"Paid Transactions       : {paid_count}",
            f"Outstanding Transactions: {unpaid_count}",
            f"Paid Income             : RM{income:.2f}",
            f"Outstanding Amount      : RM{outstanding:.2f}",
            f"Equipment Maintenance   : RM{maintenance_expenses:.2f}",
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


def record_payment(booking_id, base_amount, discount_amount, penalty_fee,
                   tax_amount, total_amount, payment_status, payment_method,
                   payment_date):

    booking_services = booking_service_id()

    if booking_id not in booking_services:
        print(warning("Booking not found."))
        return False

    try:
        base_value = float(base_amount)
        discount_value = float(discount_amount)
        penalty_value = float(penalty_fee)
        tax_value = float(tax_amount)
        total_value = float(total_amount)

    except (ValueError, TypeError):
        print(error("Invalid amount. Please enter numbers."))
        return False


    if not validate_date(payment_date):
        print(warning("Invalid date."))
        print(info("Please use YYYY-MM-DD format."))
        return False

    payment_id = primary_key(PAYMENT_FILE)

    new_record = (
        f"{payment_id}|"
        f"{booking_id}|"
        f"{base_value:.2f}|"
        f"{discount_value:.2f}|"
        f"{penalty_value:.2f}|"
        f"{tax_value:.2f}|"
        f"{total_value:.2f}|"
        f"{payment_status}|"
        f"{payment_method}|"
        f"{payment_date}"
    )

    write_lines(PAYMENT_FILE, new_record)

    print(draw_box(
        [
            f"Payment ID : {payment_id}",
            f"Booking ID : {booking_id}",
            f"Total      : RM{total_value:.2f}",
            f"Status     : {payment_status}",
            f"Method     : {payment_method}",
            f"Date       : {payment_date}"
        ], "PAYMENT RECORDED"
    ))

    return True