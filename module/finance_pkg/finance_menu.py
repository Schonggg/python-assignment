from ..utils import (
    render_menu,
    draw_box,
    divider,
    success,
    error,
    info,
    pause,
)
from module.finance_pkg.finance import (
    income_summary,
    monthly_financial_summary,
    outstanding_payment_list,
    record_payment
)


#sentinel returned by prompt_or_cancel when the accountant chooses to quit
_CANCEL = object()


def prompt_or_cancel(label):
    #read one field for Record Payment; typing q/quit/exit cancels the whole entry
    value = input(label).strip()

    if value.lower() in ("q", "quit", "exit"):
        return _CANCEL

    return value


def record_payment_flow():
    print(info("Type 'q' at any prompt to cancel."))

    prompts = (
        ("Enter Booking ID: ", "booking_id"),
        ("Enter Base Amount: ", "base_amount"),
        ("Enter Discount Amount: ", "discount_amount"),
        ("Enter Penalty Fee: ", "penalty_fee"),
        ("Enter Tax Amount: ", "tax_amount"),
        ("Enter Total Amount: ", "total_amount"),
        ("Enter Payment Status (Paid/Pending): ", "payment_status"),
        ("Enter Payment Method: ", "payment_method"),
        ("Enter Payment Date (YYYY-MM-DD): ", "payment_date"),
    )
    values = {}

    for prompt, field in prompts:
        value = prompt_or_cancel(prompt)
        if value is _CANCEL:
            print(info("Record payment cancelled."))
            return
        values[field] = value

    if record_payment(
        values["booking_id"],
        values["base_amount"],
        values["discount_amount"],
        values["penalty_fee"],
        values["tax_amount"],
        values["total_amount"],
        values["payment_status"],
        values["payment_method"],
        values["payment_date"],
    ):
        print(success("Payment recorded successfully."))
    else:
        print(error("Failed to record payment."))


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
            income_summary()

        elif choice == "2":
            month = prompt_or_cancel("Enter Month (YYYY-MM, q to cancel): ")
            if month is _CANCEL:
                print(info("Monthly financial summary cancelled."))
            else:
                print(divider())
                monthly_financial_summary(month)

        elif choice == "3":
            print(divider())
            outstanding_payment_list()

        elif choice == "4":
            record_payment_flow()

        elif choice == "0":
            print(info("Logging out..."))
            break
        else:
            print(error("Invalid choice, try again."))

        pause()
