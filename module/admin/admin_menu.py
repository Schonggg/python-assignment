from pathlib import Path

from module.utils import (
    SERVICE_FILE,
    draw_box,
    error,
    info,
    primary_key,
    render_menu,
    success,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
_CANCEL = object()


def _prompt_or_cancel(prompt):
    value = input(prompt).strip()
    if value.lower() in {"q", "quit", "exit"}:
        return _CANCEL
    return value


def _report_cancelled():
    print(info("Operation cancelled."))


def _service_file_parts(lines):
    has_header = bool(
        lines and lines[0].split("|", 1)[0].strip().lower() == "service_id"
    )
    header = lines[0] if has_header else None
    records = lines[1:] if has_header else lines[:]
    delimiter = "|" if any("|" in line for line in records) else ","
    return header, records, delimiter


def _service_menu_items(records, delimiter):
    items = []
    for index, record in enumerate(records, 1):
        parts = [part.strip() for part in record.split(delimiter)]
        if delimiter == "|" and len(parts) >= 5:
            label = (
                f"{parts[0]} | {parts[1]} | RM{parts[2]} | "
                f"{parts[3]} min | {parts[4]}"
            )
        elif delimiter == "|" and len(parts) >= 3:
            label = f"{parts[0]} | {parts[1]} | RM{parts[2]}"
        else:
            label = record
        items.append((str(index), label))
    items.append(("q", "Cancel"))
    return items


def read_lines(file_name):
    file_path = DATA_DIR / file_name
    try:
        with file_path.open("r", encoding="utf-8") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        return []


def write_lines(file_name, lines):
    file_path = DATA_DIR / file_name
    with file_path.open("w", encoding="utf-8") as file:
        for line in lines:
            file.write(line + "\n")


def _print_table(title, headers, rows, right_align=()):
    normalized_rows = [
        [str(value).strip() for value in row[:len(headers)]]
        + [""] * max(0, len(headers) - len(row))
        for row in rows
    ]
    widths = [
        max(
            len(headers[index]),
            *(len(row[index]) for row in normalized_rows),
        )
        for index in range(len(headers))
    ]

    def format_row(row):
        cells = []
        for index, value in enumerate(row):
            aligned = value.rjust(widths[index]) if index in right_align else value.ljust(widths[index])
            cells.append(aligned)
        return " | ".join(cells)

    table_lines = [
        format_row(headers),
        "-+-".join("-" * width for width in widths),
    ]
    table_lines.extend(format_row(row) for row in normalized_rows)
    print(draw_box(table_lines, title=title))


def show_admin_menu():
    print(render_menu(
        "ADMINISTRATOR",
        [
            ("1", "Add Service"),
            ("2", "Update Service"),
            ("3", "Remove Service"),
            ("4", "View All Customers"),
            ("5", "View All Bookings"),
            ("6", "View All Payments"),
            ("7", "Generate Report"),
            ("8", "Modify Schedule"),
            ("0", "Back"),
        ],
    ))


def add_service():
    name = _prompt_or_cancel("Enter service name (q to cancel): ")
    if name is _CANCEL:
        _report_cancelled()
        return
    if not name:
        print("Service name cannot be empty.")
        return

    price_input = _prompt_or_cancel("Enter service price (q to cancel): ")
    if price_input is _CANCEL:
        _report_cancelled()
        return
    try:
        price = float(price_input)
    except ValueError:
        print("Price must be a number.")
        return

    duration_input = _prompt_or_cancel(
        "Enter service duration in minutes (q to cancel): "
    )
    if duration_input is _CANCEL:
        _report_cancelled()
        return
    try:
        duration = int(duration_input)
        if duration <= 0:
            raise ValueError
    except ValueError:
        print("Duration must be a positive whole number of minutes.")
        return

    services = read_lines("service.txt")
    if not services or services[0].split("|", 1)[0].strip().lower() != "service_id":
        services.insert(
            0,
            "Service_ID|Service_Name|Price|Duration_Mins|Status",
        )
    service_id = primary_key(str(SERVICE_FILE))
    services.append(
        f"{service_id}|{name}|{price:.2f}|{duration}|Active"
    )
    write_lines("service.txt", services)
    print(success(f"Service {service_id} added successfully."))


def update_service():
    services = read_lines("service.txt")
    header, records, delimiter = _service_file_parts(services)
    if not records:
        print("No services available.")
        return

    print(render_menu(
        "SELECT SERVICE TO UPDATE",
        _service_menu_items(records, delimiter),
    ))

    selection = _prompt_or_cancel("Choose a service number, or q to cancel: ")
    if selection is _CANCEL:
        _report_cancelled()
        return

    try:
        choice = int(selection) - 1
        if not 0 <= choice < len(records):
            print("Invalid selection.")
            return
    except ValueError:
        print("Please enter a valid number.")
        return

    parts = [part.strip() for part in records[choice].split(delimiter)]
    name_index, price_index = (1, 2) if delimiter == "|" and len(parts) >= 3 else (0, 1)
    old_name = parts[name_index] if len(parts) > name_index else ""
    old_price = parts[price_index] if len(parts) > price_index else ""

    new_name = _prompt_or_cancel(
        f"Enter new service name [{old_name}] (q to cancel): "
    )
    if new_name is _CANCEL:
        _report_cancelled()
        return
    new_name = new_name or old_name

    new_price = _prompt_or_cancel(
        f"Enter new price [{old_price}] (q to cancel): "
    )
    if new_price is _CANCEL:
        _report_cancelled()
        return
    new_price = new_price or old_price

    try:
        float(new_price)
    except ValueError:
        print("Price must be a number.")
        return

    while len(parts) <= max(name_index, price_index):
        parts.append("")
    parts[name_index] = new_name
    parts[price_index] = new_price
    records[choice] = delimiter.join(parts)
    updated_lines = ([header] if header is not None else []) + records
    write_lines("service.txt", updated_lines)
    print("Service updated successfully.")


def remove_service():
    services = read_lines("service.txt")
    header, records, delimiter = _service_file_parts(services)
    if not records:
        print("No services available.")
        return

    print(render_menu(
        "SELECT SERVICE TO REMOVE",
        _service_menu_items(records, delimiter),
    ))

    selection = _prompt_or_cancel("Choose a service number, or q to cancel: ")
    if selection is _CANCEL:
        _report_cancelled()
        return

    try:
        choice = int(selection) - 1
        if not 0 <= choice < len(records):
            print("Invalid selection.")
            return
    except ValueError:
        print("Please enter a valid number.")
        return

    removed = records.pop(choice)
    updated_lines = ([header] if header is not None else []) + records
    write_lines("service.txt", updated_lines)
    print(f"Removed service: {removed}")


def view_all_customers():
    customers = read_lines("customers.txt")
    if not customers or len(customers) == 1:
        print(draw_box(["No customer records found."], title="ALL CUSTOMERS"))
        return

    headers = [part.strip() for part in customers[0].split("|")]
    rows = [[part.strip() for part in line.split("|")] for line in customers[1:]]
    _print_table("ALL CUSTOMERS", headers, rows)


def view_all_bookings():
    bookings = read_lines("bookings.txt")
    if not bookings or len(bookings) == 1:
        print(draw_box(["No booking records found."], title="ALL BOOKINGS"))
        return

    headers = [part.strip() for part in bookings[0].split("|")]
    rows = [[part.strip() for part in line.split("|")] for line in bookings[1:]]
    _print_table("ALL BOOKINGS", headers, rows)


def view_all_payments():
    payments = read_lines("payments.txt")
    if not payments or len(payments) == 1:
        print(draw_box(["No payment records found."], title="ALL PAYMENTS"))
        return

    headers = [part.strip() for part in payments[0].split("|")]
    rows = [[part.strip() for part in line.split("|")] for line in payments[1:]]
    _print_table("ALL PAYMENTS", headers, rows)


def generate_report():
    customers = read_lines("customers.txt")
    bookings = read_lines("bookings.txt")
    payments = read_lines("payments.txt")
    services = read_lines("service.txt")

    customer_rows = [
        line for line in customers
        if not line.split("|", 1)[0].strip().lower() == "customer_id"
    ]
    booking_rows = [
        [part.strip() for part in line.split("|")]
        for line in bookings
        if not line.split("|", 1)[0].strip().lower() == "booking_id"
    ]
    payment_rows = [
        [part.strip() for part in line.split("|")]
        for line in payments
        if not line.split("|", 1)[0].strip().lower() == "payment_id"
    ]
    service_rows = [
        [part.strip() for part in line.split("|")]
        for line in services
        if not line.split("|", 1)[0].strip().lower() == "service_id"
    ]

    booking_statuses = {}
    for booking in booking_rows:
        if len(booking) >= 6:
            status = booking[5].title()
            booking_statuses[status] = booking_statuses.get(status, 0) + 1

    payment_statuses = {}
    paid_total = 0.0
    for payment in payment_rows:
        if len(payment) < 8:
            continue

        status = payment[7].title()
        payment_statuses[status] = payment_statuses.get(status, 0) + 1
        if status.lower() == "paid":
            try:
                paid_total += float(payment[6])
            except ValueError:
                continue

    summary = [
        ("Customers", len(customer_rows)),
        ("Bookings", len(booking_rows)),
        ("  Completed", booking_statuses.get("Completed", 0)),
        ("  Confirmed", booking_statuses.get("Confirmed", 0)),
        ("  Cancelled", booking_statuses.get("Cancelled", 0)),
        ("Payments", len(payment_rows)),
        ("  Paid", payment_statuses.get("Paid", 0)),
        ("  Pending", payment_statuses.get("Pending", 0)),
        ("Paid revenue", f"RM{paid_total:.2f}"),
        ("Services", len(service_rows)),
    ]

    _print_table("ADMIN REPORT", ["Metric", "Count / Amount"], summary, (1,))

    service_headers = ["Service ID", "Service Name", "Price", "Duration", "Status"]
    service_rows_for_table = []
    for service in service_rows:
        if len(service) < 5:
            continue
        service_id, name, price, duration, status = service[:5]
        service_rows_for_table.append(
            [service_id, name, f"RM{price}", f"{duration} min", status]
        )

    _print_table("SERVICE OVERVIEW", service_headers, service_rows_for_table)


def edit_schedule():
    from module.utils import TIME_SLOTS, get_schedules, modify_schedule_list

    schedules = [
        schedule
        for schedule in get_schedules()
        if schedule["Is_Booked"].lower() != "yes"
    ]
    if not schedules:
        print("No unbooked schedules are available to modify.")
        return

    schedule_items = [
        (
            str(index),
            f"{schedule['Schedule_ID']} | {schedule['Date']} | "
            f"{schedule['Time_Slot']} | {schedule['Team_Assigned']}",
        )
        for index, schedule in enumerate(schedules, 1)
    ]
    schedule_items.append(("q", "Cancel"))
    print(render_menu("SELECT SCHEDULE TO MODIFY", schedule_items))

    selection = _prompt_or_cancel(
        "Choose a schedule number, or q to cancel: "
    )
    if selection is _CANCEL:
        _report_cancelled()
        return

    try:
        schedule_index = int(selection) - 1
        if not 0 <= schedule_index < len(schedules):
            print(error("Invalid selection."))
            return
    except ValueError:
        print(error("Please choose a schedule number or q to cancel."))
        return

    schedule_id = schedules[schedule_index]["Schedule_ID"]

    date_str = _prompt_or_cancel(
        "New date (YYYY-MM-DD, blank to keep current, q to cancel): "
    )
    if date_str is _CANCEL:
        _report_cancelled()
        return

    time_slot = _prompt_or_cancel(
        f"New time slot ({', '.join(TIME_SLOTS)}), "
        "blank to keep current, q to cancel: "
    )
    if time_slot is _CANCEL:
        _report_cancelled()
        return

    team = _prompt_or_cancel(
        "New team (Team Alpha/Team Beta, blank to keep current, q to cancel): "
    )
    if team is _CANCEL:
        _report_cancelled()
        return

    if modify_schedule_list(
        schedule_id,
        date_str=date_str or None,
        time_slot=time_slot or None,
        team=team or None,
    ):
        print(f"Schedule {schedule_id} updated successfully.")


def admin_menu():
    while True:
        show_admin_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_service()
        elif choice == "2":
            update_service()
        elif choice == "3":
            remove_service()
        elif choice == "4":
            view_all_customers()
        elif choice == "5":
            view_all_bookings()
        elif choice == "6":
            view_all_payments()
        elif choice == "7":
            generate_report()
        elif choice == "8":
            edit_schedule()
        elif choice == "0":
            print(info("Returning to main menu..."))
            break
        else:
            print(error("Invalid choice, try again."))

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    admin_menu()
