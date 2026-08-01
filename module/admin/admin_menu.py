from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


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


def show_admin_menu():
    print("\n===== Administrator =====")
    print("1. Add Service")
    print("2. Update Service")
    print("3. Remove Service")
    print("4. View All Customers")
    print("5. View All Bookings")
    print("6. View All Payments")
    print("7. Generate Report")
    print("0. Back")


def add_service():
    name = input("Enter service name: ").strip()
    if not name:
        print("Service name cannot be empty.")
        return

    price = input("Enter service price: ").strip()
    if not price.replace(".", "", 1).isdigit():
        print("Price must be a number.")
        return

    services = read_lines("service.txt")
    services.append(f"{name},{price}")
    write_lines("service.txt", services)
    print("Service added successfully.")


def update_service():
    services = read_lines("service.txt")
    if not services:
        print("No services available.")
        return

    print("Current services:")
    for index, service in enumerate(services, 1):
        print(f"{index}. {service}")

    try:
        choice = int(input("Select service number to update: "))
        if not 1 <= choice <= len(services):
            print("Invalid selection.")
            return
    except ValueError:
        print("Please enter a valid number.")
        return

    parts = services[choice - 1].split(",", 1)
    old_name = parts[0].strip()
    old_price = parts[1].strip() if len(parts) > 1 else ""

    new_name = input(f"Enter new service name [{old_name}]: ").strip() or old_name
    new_price = input(f"Enter new price [{old_price}]: ").strip() or old_price

    services[choice - 1] = f"{new_name},{new_price}"
    write_lines("service.txt", services)
    print("Service updated successfully.")


def remove_service():
    services = read_lines("service.txt")
    if not services:
        print("No services available.")
        return

    print("Current services:")
    for index, service in enumerate(services, 1):
        print(f"{index}. {service}")

    try:
        choice = int(input("Select service number to remove: "))
        if not 1 <= choice <= len(services):
            print("Invalid selection.")
            return
    except ValueError:
        print("Please enter a valid number.")
        return

    removed = services.pop(choice - 1)
    write_lines("service.txt", services)
    print(f"Removed service: {removed}")


def view_all_customers():
    customers = read_lines("customers.txt")
    if not customers:
        print("No customers found.")
        return

    print("\nAll Customers:")
    for customer in customers:
        print("-", customer)


def view_all_bookings():
    bookings = read_lines("bookings.txt")
    if not bookings:
        print("No bookings found.")
        return

    print("\nAll Bookings:")
    for booking in bookings:
        print("-", booking)


def view_all_payments():
    payments = read_lines("payments.txt")
    if not payments:
        print("No payments found.")
        return

    print("\nAll Payments:")
    for payment in payments:
        print("-", payment)


def generate_report():
    customers = read_lines("customers.txt")
    bookings = read_lines("bookings.txt")
    payments = read_lines("payments.txt")
    services = read_lines("service.txt")

    print("\n===== Admin Report =====")
    print(f"Total Customers: {len(customers)}")
    print(f"Total Bookings: {len(bookings)}")
    print(f"Total Payments: {len(payments)}")
    print(f"Total Services: {len(services)}")

    if services:
        print("Services:")
        for service in services:
            print("-", service)


def admin_menu():
    while True:
        clear_screen()
        show_admin_menu()
        choice = input("Enter your choice: ").strip()

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
        elif choice == "0":
            print("Returning to main menu...")
            break
        else:
            print("Invalid choice. Please try again.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    admin_menu()
