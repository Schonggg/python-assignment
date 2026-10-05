from ..utils import (
    render_menu,
    draw_box,
    divider,
    success,
    error,
    info,
)
from module.finance_pkg import finance


#sentinel returned by prompt_or_cancel when the accountant chooses to quit
_CANCEL = object()


def prompt_or_cancel(label):
    #read one field for Record Payment; typing q/quit/exit cancels the whole entry
    value = input(label).strip()

    if value.lower() in ("q", "quit", "exit"):
        return _CANCEL

    return value


def finance_menu():
    while True:
        print(render_menu(
            "FINANCE",
            [
                ("1", "Income Summary"),
                ("2", "Monthly Financial Summary"),
                ("3", "Outstanding Payment List"),
                ("4", "Record Payment"),
                ("0", "Logout"),
            ],
        ))

        choice = input("Choose an option: ").strip()

        if choice == "1":
            print(divider())
            finance_pkg.income_summary()

        elif choice == "2":
            month = input("Enter Month (YYYY-MM): ").strip()
            print(divider())
            finance_pkg.monthly_financial_summary(month)

        elif choice == "3":
            print(divider())
            finance_pkg.outstanding_payment_list()

        elif choice == "4":
            #type q (or quit/exit) at any prompt to cancel the whole entry
            print(info("Type 'q' at any prompt to cancel."))

            booking_id = prompt_or_cancel("Enter Booking ID: ")
            if booking_id is _CANCEL:
                print(info("Record payment cancelled."))
                continue

            base_amount = prompt_or_cancel("Enter Base Amount: ")
            if base_amount is _CANCEL:
                print(info("Record payment cancelled."))
                continue

            discount_amount = prompt_or_cancel("Enter Discount Amount: ")
            if discount_amount is _CANCEL:
                print(info("Record payment cancelled."))
                continue

            penalty_fee = prompt_or_cancel("Enter Penalty Fee: ")
            if penalty_fee is _CANCEL:
                print(info("Record payment cancelled."))
                continue

            tax_amount = prompt_or_cancel("Enter Tax Amount: ")
            if tax_amount is _CANCEL:
                print(info("Record payment cancelled."))
                continue

            total_amount = prompt_or_cancel("Enter Total Amount: ")
            if total_amount is _CANCEL:
                print(info("Record payment cancelled."))
                continue

            payment_status = prompt_or_cancel("Enter Payment Status (Paid/Pending): ")
            if payment_status is _CANCEL:
                print(info("Record payment cancelled."))
                continue

            payment_method = prompt_or_cancel("Enter Payment Method: ")
            if payment_method is _CANCEL:
                print(info("Record payment cancelled."))
                continue

            payment_date = prompt_or_cancel("Enter Payment Date (YYYY-MM-DD): ")
            if payment_date is _CANCEL:
                print(info("Record payment cancelled."))
                continue

            if finance_pkg.record_payment(
                booking_id,
                base_amount,
                discount_amount,
                penalty_fee,
                tax_amount,
                total_amount,
                payment_status,
                payment_method,
                payment_date,
            ):
                print(success("Payment recorded successfully."))
            else:
                print(error("Failed to record payment."))

        elif choice == "0":
            print(info("Logging out..."))
            break
        else:
            print(error("Invalid choice, try again."))
