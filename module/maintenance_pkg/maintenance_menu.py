from module.maintenance_pkg.maintenance import (
    Status_Need_Service,
    Status_Operational,
    get_equipments,
    get_equipment_needing_service,
    equipment_status_change,
    record_maintenance,
    get_maintenance_records,
    maintenance_summary,
    recompute_equipment_status,
)
from module.booking_pkg import booking
from ..utils import (
    render_menu,
    draw_box,
    divider,
    success,
    warning,
    error,
    info,
    pause,
    clear_screen,
)


def _finish_display():
    pause()
    clear_screen()


def display_equipments(equipments):
    if not equipments:
        print(draw_box(["No equipment records found."], title="EQUIPMENT"))
        return

    headers = [
        "Equipment ID",
        "Name",
        "Category",
        "Status",
        "Last Service Date",
        "Durability",
    ]
    rows = []
    for equipment in equipments:
        rows.append(
            [
                equipment["equipment_id"],
                equipment["equipment_name"],
                equipment["category"],
                equipment["status"].title(),
                equipment["last_service_date"],
                f"{equipment['current_durability']}/100",
            ]
        )

    widths = [
        max(len(headers[index]), *(len(row[index]) for row in rows))
        for index in range(len(headers))
    ]
    table_lines = [
        " | ".join(header.ljust(widths[index]) for index, header in enumerate(headers)),
        "-+-".join("-" * width for width in widths),
    ]
    table_lines.extend(
        " | ".join(value.ljust(widths[index]) for index, value in enumerate(row))
        for row in rows
    )
    print(draw_box(table_lines, title="ALL EQUIPMENT"))


def display_bookings(bookings):
    if not bookings:
        print(draw_box(["No booking records found."], title="BOOKING LIST"))
        return

    headers = [
        "Booking ID",
        "Customer ID",
        "Service ID",
        "Schedule ID",
        "Booking Date",
        "Status",
    ]
    rows = [
        [
            booking_record["Booking_ID"],
            booking_record["Customer_ID"],
            booking_record["Service_ID"],
            booking_record["Schedule_ID"],
            booking_record["Booking_Date"],
            booking_record["Status"],
        ]
        for booking_record in bookings
    ]
    widths = [
        max(len(headers[index]), *(len(row[index]) for row in rows))
        for index in range(len(headers))
    ]
    table_lines = [
        " | ".join(header.ljust(widths[index]) for index, header in enumerate(headers)),
        "-+-".join("-" * width for width in widths),
    ]
    table_lines.extend(
        " | ".join(value.ljust(widths[index]) for index, value in enumerate(row))
        for row in rows
    )
    print(draw_box(table_lines, title="BOOKING LIST"))


def display_maintenance_records(records):
    if not records:
        print(draw_box(["No maintenance records found."], title="MAINTENANCE HISTORY"))
        return

    print(divider())
    print(info("MAINTENANCE HISTORY"))
    print(divider())

    for record in records:
        print(draw_box(
            [
                f"Maint ID    : {record['maint_id']}",
                f"Equipment ID: {record['equipment_id']}",
                f"Date        : {record['maintenance_date']}",
                f"Cost        : RM{record['cost']:.2f}",
                f"Staff       : {record['staff_user_id']}",
                f"Description : {record['description']}",
            ],
        ))


def display_summary(summary):
    lines = [
        f"Total Records : {summary['total_records']}",
        f"Total Cost    : RM{summary['total_cost']:.2f}",
    ]
    print(draw_box(lines, title="MAINTENANCE SUMMARY"))

    print(info("Per Equipment:"))

    if not summary["per_equipment"]:
        print(warning("No maintenance recorded yet."))
        return

    for equipment_id, data in summary["per_equipment"].items():
        print(
            f"  {equipment_id} : {data['count']} job(s), "
            f"RM{data['cost']:.2f}"
        )


def maintenance_menu(current_user_id):
    while True:
        print(render_menu(
            "MAINTENANCE STAFF",
            [
                ("1", "View All Equipment"),
                ("2", "View Equipment Needing Service"),
                ("3", "Update Equipment Status"),
                ("4", "Record Maintenance"),
                ("5", "View Maintenance History"),
                ("6", "Generate Maintenance Summary"),
                ("7", "Mark Booking Completed"),
                ("0", "Logout"),
            ],
        ))

        choice = input("Choose an option: ").strip()

        if choice == "1":
            display_equipments(get_equipments())
            _finish_display()

        elif choice == "2":
            recompute_equipment_status()
            display_equipments(get_equipment_needing_service())
            _finish_display()

        elif choice == "3":
            display_equipments(get_equipments())
            equipment_id = input("Enter Equipment ID: ").strip()
            new_status = input(
                "Enter New Status (Need Service/Operational): "
            ).strip().casefold()
            allowed_statuses = {
                Status_Need_Service.casefold(): Status_Need_Service,
                Status_Operational.casefold(): Status_Operational,
            }
            new_status = allowed_statuses.get(new_status, new_status)

            if equipment_status_change(equipment_id, new_status):
                print(success(f"Equipment {equipment_id} status updated to {new_status}."))
            else:
                print(error("Equipment not found."))

        elif choice == "4":
            display_equipments(get_equipments())
            equipment_id = input("Enter Equipment ID: ").strip()
            maintenance_date = input(
                "Enter Maintenance Date (YYYY-MM-DD): "
            ).strip()
            try:
                cost = float(input("Enter Cost: ").strip())
            except ValueError:
                print(error("Cost must be a number."))
                continue
            description = input("Enter Description: ").strip()

            record_maintenance(
                equipment_id,
                maintenance_date,
                cost,
                current_user_id,
                description
            )

        elif choice == "5":
            display_maintenance_records(get_maintenance_records())
            _finish_display()

        elif choice == "6":
            display_summary(maintenance_summary())
            _finish_display()

        elif choice == "7":
            display_bookings(booking.get_bookings())
            booking_id = input("Enter Booking ID to mark as Completed: ").strip()
            booking.complete_booking(booking_id)
            pause()

        elif choice == "0":
            print(info("Logging out..."))
            break
        else:
            print(error("Invalid choice, try again."))
