import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

SERVICE_FILE = os.path.join(DATA_DIR, "service.txt")
CUSTOMER_FILE = os.path.join(DATA_DIR, "customers.txt")
BOOKING_FILE = os.path.join(DATA_DIR, "bookings.txt")
FINANCE_FILE = os.path.join(DATA_DIR, "finance.txt")
PAYMENT_FILE = os.path.join(DATA_DIR, "payments.txt")
MAINTENANCE_FILE = os.path.join(DATA_DIR, "maintenance.txt")
STAFF_FILE = os.path.join(DATA_DIR, "staff.txt")
SYSTEM_LOGS_FILE = os.path.join(DATA_DIR, "system_logs.txt")

ROOT_SERVICE_FILE = os.path.join(BASE_DIR, "service.txt")
ROOT_CUSTOMER_FILE = os.path.join(BASE_DIR, "customer.txt")
ROOT_BOOKING_FILE = os.path.join(BASE_DIR, "booking.txt")
ROOT_PAYMENT_FILE = os.path.join(BASE_DIR, "payment.txt")


def open_file(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as file:
            file.write("")
    return path


def migrate_legacy_file(path, legacy_paths=()):
    open_file(path)
    if os.path.getsize(path) > 0:
        return path

    for legacy_path in legacy_paths:
        if os.path.exists(legacy_path) and os.path.getsize(legacy_path) > 0:
            with open(legacy_path, "r", encoding="utf-8") as legacy_file:
                legacy_content = legacy_file.read()
            with open(path, "w", encoding="utf-8") as target_file:
                target_file.write(legacy_content)
            break

    return path


def legacy_paths_for(path):
    if path == SERVICE_FILE:
        return (ROOT_SERVICE_FILE,)
    if path == CUSTOMER_FILE:
        return (ROOT_CUSTOMER_FILE,)
    if path == BOOKING_FILE:
        return (ROOT_BOOKING_FILE,)
    if path == PAYMENT_FILE:
        return (ROOT_PAYMENT_FILE,)
    return ()

def read_lines(path):
    migrate_legacy_file(path, legacy_paths_for(path))
    with open(path, "r", encoding="utf-8") as file:
        result = []
        for line in file: 
            if line.strip(): 
                result.append(line.strip()) 
        return result 

def write_lines(path, lines): 
    open_file(path)
    with open(path, "w", encoding="utf-8") as file:
        if lines:
            file.write("\n".join(lines) + "\n")
        else:
            file.write("") # 如果列表为空，清空文件

def generate_next_service_code():
    lines = read_lines(SERVICE_FILE)
    if not lines:
        return "S001"
    
    last_line = lines[-1]
    last_code = last_line.split("|")[0].strip()
    try:
        number = int(last_code.replace("S", ""))
        return f"S{number + 1:03d}"
    except ValueError:
        # 万一前面数据格式不对，退回按行数生成
        return f"S{len(lines) + 1:03d}"

def admin_menu():
    print("\n===== Administrator =====")
    print("1. Add Service")
    print("2. Update Service")
    print("3. Remove Service")
    print("4. View All Services")
    print("5. View All Customers")
    print("6. View All Bookings")
    print("7. View All Payments")
    print("8. Generate Report")
    print("0. Back")

def add_service():
    print("\nAdd Service")

    # 1. service name
    while True:
        name = input("Service: ").strip()
        if name != "":
            break
        print("Please enter again the service name")

    # 2. service price
    while True:
        price = input("Cost(RM): ").strip()
        if price != "" and price.isdigit():
            break 
        print("Please enter the correct price(RM)")

    # 3. service time
    while True:
        time = input("Time(min): ").strip()
        if time != "" and time.isdigit():
            break  
        print("Please enter the correct time(min)")

    # 4. service detail
    while True:
        description = input("Description: ").strip()
        if description != "":
            break 
        print("Please enter again the service description (at least \"no\")")

    # 5. 动态获取下一个新编号
    new_code = generate_next_service_code()
    
    # 格式化储存：保持纯干净的字符串数据（用 | 隔开）
    new_line = f"{new_code}|{name}|{price}|{time}|{description}"
    
    lines = read_lines(SERVICE_FILE)
    lines.append(new_line)
    write_lines(SERVICE_FILE, lines)
    
    print(f"\nService [{new_code}] added successfully")

def update_service():
    print("\nUpdate Service")

    lines = read_lines(SERVICE_FILE)
    if not lines:
        print("No services available to update.")
        return

    print("\n--- Current Services ---")
    for line in lines:
        print(line)
    print("------------------------\n")
    
    update_code = input("Please enter the service code that need to update (press 0 to cancel): ").strip().upper()
    if update_code == "0":
        return

    found = False
    for line in lines:
        code = line.split("|")[0].strip() 
        if code == update_code:
            found = True
            break

    if not found:
        print(f"Service code [{update_code}] not found.")
        return

    while True:
        new_name = input("New Service: ").strip()
        if new_name != "":
            break
        print("Please enter again the service name")      

    while True:
        new_price = input("New Cost: ").strip()
        if new_price != "" and new_price.isdigit():
            break 
        print("Please enter the correct price(RM)")

    while True:
        new_time = input("New Time: ").strip()
        if new_time != "" and new_time.isdigit():
            break  
        print("Please enter the correct time(min)")

    while True:
        new_description = input("New Description: ").strip()
        if new_description != "":
            break 
        print("Please enter again the service description (at least \"no\")")

    updated_lines = []
    for line in lines:
        code = line.split("|")[0].strip()
        if code == update_code: 
            new_line = f"{update_code}|{new_name}|{new_price}|{new_time}|{new_description}"
            updated_lines.append(new_line)
        else:                     
            updated_lines.append(line)

    write_lines(SERVICE_FILE, updated_lines)
    print(f"\nService [{update_code}] updated successfully")

def remove_service():
    print("\nRemove Service")

    lines = read_lines(SERVICE_FILE)
    if not lines:
        print("No services available to remove.")
        return

    print("\n--- Current Services ---")
    for line in lines:
        print(line)
    print("------------------------\n")

    while True:
        delete_code = input("Please enter the service code that need to remove (press 0 to cancel): ").strip().upper()
        if delete_code == "0":
            return
        elif delete_code != "":
            break
        else:
            print("Service code cannot be empty. Please try again.")

    found = False
    for line in lines:
        code = line.split("|")[0].strip() 
        if code == delete_code:
            found = True
            break

    if not found:
        print(f"Service code [{delete_code}] not found.")
        return

    new_service_lines = []
    for line in lines:
        code = line.split("|")[0].strip()
        if code == delete_code:
            continue  
        else:
            new_service_lines.append(line)

    write_lines(SERVICE_FILE, new_service_lines)
    print(f"\nService [{delete_code}] removed successfully")  # 这里修复了原来的 updated 提示错误

def view_all_services():
    print("\nView All Services")
    services = read_lines(SERVICE_FILE)
    if not services:
        print("No services records found")
        return
    for service in services:
        print(service)

def view_all_customers():
    print("\nView All Customers")
    customers = read_lines(CUSTOMER_FILE)
    if not customers:
        print("No customer records found")
        return
    for customer in customers: 
        print(customer)

def view_all_bookings():
    print("\nView All Booking")
    bookings = read_lines(BOOKING_FILE)
    if not bookings:
        print("No booking records found")
        return
    for booking in bookings:
        print(booking)
    
def view_all_payments():
    print("\nView All Payment")
    payments = read_lines(PAYMENT_FILE)
    if not payments:
        print("No payment records found")
        return
    for payment in payments:
        print(payment)

def generate_report():
    services = read_lines(SERVICE_FILE)
    bookings = read_lines(BOOKING_FILE)
    finances = read_lines(FINANCE_FILE)

    total_booking = len(bookings)
    revenue = finances 
    available_slots = max(0, (len(services) * 5) - len(bookings))

    print("\nGenerate Report")
    print("------------------")
    print(f"Total bookings\t:{total_booking}")
    print(f"Revenue\t\t:{revenue}")
    print(f"Available slots\t:{available_slots}")

def start_menu():
    for path in [SERVICE_FILE, CUSTOMER_FILE, BOOKING_FILE, FINANCE_FILE, PAYMENT_FILE, MAINTENANCE_FILE, STAFF_FILE, SYSTEM_LOGS_FILE]:
        open_file(path)

    while True:
        admin_menu()
        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            add_service()
        elif choice == "2":
            update_service()
        elif choice == "3":
            remove_service()
        elif choice == "4":
            view_all_services()
        elif choice == "5":
            view_all_customers()
        elif choice == "6":
            view_all_bookings()
        elif choice == "7":
            view_all_payments()
        elif choice == "8":
            generate_report()
        elif choice == "0":
            print("Exiting administrator menu...")
            break
        else:
            print("Invalid choice. Please try again.")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    start_menu()