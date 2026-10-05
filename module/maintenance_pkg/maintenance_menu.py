from module.maintenance_pkg.maintenance import (
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
)


def display_equipments(equipments):
    if not equipments:
        print(draw_box(["No equipment records found."], title="EQUIPMENT"))
        return

    print(divider())
    print(info("EQUIPMENT"))
    print(divider())

    for equipment in equipments:
        current_wear = equipment.get("current_wear", equipment.get("wear", 0))
        wear_line = f"Wear              : {current_wear}/100"
        if current_wear >= 100:
            wear_line += "  (NEEDS SERVICE)"

        print(draw_box(
            [
                f"Equipment ID      : {equipment['equipment_id']}",
                f"Name              : {equipment['equipment_name']}",
                f"Category          : {equipment['category']}",
                f"Status            : {equipment['status']}",
                f"Last Service Date : {equipment['last_service_date']}",
                wear_line,
            ],
        ))


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


def maintenance_menu():
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

        elif choice == "2":
            # recompute first so time-decayed items flip to Need Service
            recompute_equipment_status()
            display_equipments(get_equipment_needing_service())

        elif choice == "3":
            equipment_id = input("Enter Equipment ID: ").strip()
            new_status = input("Enter New Status: ").strip()

            if equipment_status_change(equipment_id, new_status):
                print(success(f"Equipment {equipment_id} status updated to {new_status}."))
            else:
                print(error("Equipment not found."))

        elif choice == "4":
            equipment_id = input("Enter Equipment ID: ").strip()
            maintenance_date = input(
                "Enter Maintenance Date (YYYY-MM-DD): "
            ).strip()
            cost = input("Enter Cost: ").strip()
            staff_user_id = input("Enter Staff User ID: ").strip()
            description = input("Enter Description: ").strip()

            record_maintenance(
                equipment_id,
                maintenance_date,
                cost,
                staff_user_id,
                description
            )

        elif choice == "5":
            display_maintenance_records(get_maintenance_records())

        elif choice == "6":
            display_summary(maintenance_summary())

        elif choice == "7":
            booking_id = input("Enter Booking ID to mark as Completed: ").strip()
            booking_pkg.complete_booking(booking_id)

        elif choice == "0":
            print(info("Logging out..."))
            break
        else:
            print(error("Invalid choice, try again."))
