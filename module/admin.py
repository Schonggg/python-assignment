import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_FILE = os.path.join(BASE_DIR, "service.txt")
CUSTOMER_FILE = os.path.join(BASE_DIR, "customer.txt")
BOOKING_FILE = os.path.join(BASE_DIR, "booking.txt")
FINANCE_FILE = os.path.join(BASE_DIR, "finance.txt")
PAYMENT_FILE = os.path.join(BASE_DIR, "payment.txt")


def ensure_file(path):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("")
    return path


def read_lines(path):
    ensure_file(path)
    with open(path, "r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def write_lines(path, lines):
    ensure_file(path)
    with open(path, "w", encoding="utf-8") as handle:
        if lines:
            handle.write("\n".join(lines) + "\n")


def load_services():
    services = []
    for line in read_lines(SERVICE_FILE):
        parts = [part.strip() for part in line.split("|")]
        if len(parts) >= 5:
            services.append({
                "code": parts[0],
                "name": parts[1],
                "price": parts[2],
                "duration": parts[3],
                "description": parts[4],
            })
    return services


def save_services(services):
    lines = []
    for service in services:
        lines.append("|".join([
            str(service["code"]),
            service["name"],
            service["price"],
            service["duration"],
            service["description"],
        ]))
    write_lines(SERVICE_FILE, lines)


def show_services():
    services = load_services()
    if not services:
        print("No services available.")
        return

    print("\nCurrent Services:")
    for service in services:
        print(f"[{service['code']}] {service['name']} | Price: {service['price']} | Duration: {service['duration']} | Description: {service['description']}")


def get_next_code(prefix, records, key_name="code"):
    numbers = []
    for record in records:
        code = record.get(key_name, "")
        if code.startswith(prefix):
            try:
                numbers.append(int(code[len(prefix):]))
            except ValueError:
                continue
    if not numbers:
        return f"{prefix}001"
    return f"{prefix}{max(numbers) + 1:03d}"


def add_service():
    print("\nAdd Service")
    name = input("Service name: ").strip()
    if not name:
        print("Service name is required.")
        return

    while True:
        price = input("Price: ").strip()
        try:
            float(price)
            break
        except ValueError:
            print("Please enter a valid number for price.")

    duration = input("Duration: ").strip()
    description = input("Description: ").strip()

    services = load_services()
    new_code = get_next_code("S", services)
    services.append({
        "code": new_code,
        "name": name,
        "price": price,
        "duration": duration,
        "description": description,
    })
    save_services(services)
    print("Service added successfully.")


def update_service():
    services = load_services()
    if not services:
        print("No services available to update.")
        return

    show_services()
    code = input("\nEnter service code to update (0 to cancel): ").strip()
    if code == "0":
        return

    service = None
    for item in services:
        if item["code"] == code:
            service = item
            break

    if service is None:
        print("Service code not found.")
        return

    print("\nLeave the field empty to keep the current value.")
    new_name = input(f"New service name [{service['name']}]: ").strip()
    new_price = input(f"New price [{service['price']}]: ").strip()
    new_duration = input(f"New duration [{service['duration']}]: ").strip()
    new_description = input(f"New description [{service['description']}]: ").strip()

    if new_name:
        service["name"] = new_name
    if new_price:
        service["price"] = new_price
    if new_duration:
        service["duration"] = new_duration
    if new_description:
        service["description"] = new_description

    save_services(services)
    print("Service updated successfully.")


def remove_service():
    services = load_services()
    if not services:
        print("No services available to remove.")
        return

    show_services()
    code = input("\nEnter service code to delete (0 to cancel): ").strip()
    if code == "0":
        return

    new_services = [service for service in services if service["code"] != code]
    if len(new_services) == len(services):
        print("Service code not found.")
        return

    save_services(new_services)
    print("Service removed successfully.")


def view_all_customers():
    print("\nAll Customers")
    customers = read_lines(CUSTOMER_FILE)
    if not customers:
        print("No customer records found.")
        return
    for customer in customers:
        print(customer)


def view_all_bookings():
    print("\nAll Bookings")
    bookings = read_lines(BOOKING_FILE)
    if not bookings:
        print("No booking records found.")
        return
    for booking in bookings:
        print(booking)


def view_all_payments():
    print("\nAll Payments")
    payment_path = FINANCE_FILE if os.path.exists(FINANCE_FILE) else PAYMENT_FILE
    payments = read_lines(payment_path)
    if not payments:
        print("No payment records found.")
        return
    for payment in payments:
        print(payment)


def generate_report():
    print("\nGenerate Report")
    services = load_services()
    bookings = read_lines(BOOKING_FILE)
    payment_path = FINANCE_FILE if os.path.exists(FINANCE_FILE) else PAYMENT_FILE
    payments = read_lines(payment_path)

    revenue = 0.0
    for payment in payments:
        parts = [part.strip() for part in payment.split("|")]
        for part in reversed(parts):
            try:
                revenue += float(part)
                break
            except ValueError:
                continue

    available_slots = max(0, (len(services) * 5) - len(bookings))

    print(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total bookings: {len(bookings)}")
    print(f"Revenue: {revenue:.2f}")
    print(f"Available slots: {available_slots}")


def show_menu():
    print("\n===== Administrator =====")
    print("1. Add Service")
    print("2. Update Service")
    print("3. Remove Service")
    print("4. View All Customers")
    print("5. View All Bookings")
    print("6. View All Payments")
    print("7. Generate Report")
    print("0. Back")


def main():
    ensure_file(SERVICE_FILE)
    ensure_file(CUSTOMER_FILE)
    ensure_file(BOOKING_FILE)
    ensure_file(FINANCE_FILE)
    ensure_file(PAYMENT_FILE)

    while True:
        show_menu()
        choice = input("\nEnter your choice: ").strip()

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
            print("Exiting administrator menu...")
            break
        else:
            print("Invalid choice. Please try again.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
