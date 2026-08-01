import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CUSTOMER_FILE = os.path.join(DATA_DIR, "customers.txt")
STAFF_FILE = os.path.join(DATA_DIR, "staff.txt")
SERVICE_FILE = os.path.join(DATA_DIR, "service.txt")


def ensure_file(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8"):
            pass
    return path


def read_lines(path):
    ensure_file(path)
    with open(path, "r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def load_customers():
    customers = []
    for line in read_lines(CUSTOMER_FILE):
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 2:
            continue

        username = parts[0]
        password = parts[1]
        if len(parts) >= 3 and parts[2]:
            role = parts[2].lower()
        else:
            role = "admin" if username.lower() == "admin" else "customer"

        customers.append({
            "username": username,
            "password": password,
            "role": role,
        })
    return customers


def load_staff():
    staff_members = []
    for line in read_lines(STAFF_FILE):
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 2:
            continue

        username = parts[0]
        password = parts[1]
        if len(parts) >= 3 and parts[2]:
            role = parts[2].lower()
        else:
            role = "staff"

        staff_members.append({
            "username": username,
            "password": password,
            "role": role,
        })
    return staff_members


def username_exists(username):
    for account in load_customers() + load_staff():
        if account["username"].lower() == username.lower():
            return True
    return False


def show_services():
    services = read_lines(SERVICE_FILE)
    if not services:
        print("No services available.")
        return

    print("\nAvailable Services:")
    for service in services:
        print(service)



def customer_menu(username):
    while True:
        print("\n===== Customer =====")
        print(f"Welcome, {username}")
        print("1. View Services")
        print("0. Logout")

        choice = input("Choose an option: ").strip()
        if choice == "1":
            show_services()
        elif choice == "0":
            print("Logging out...")
            break
        else:
            print("Invalid choice, try again.")


def register_username():
    ensure_file(CUSTOMER_FILE)
    forbidden = {"nigga", "n1gga", "nlgga", "n!gga"}

    while True:
        username = input("Please enter username (or 'q' to cancel): ").strip()
        if username.lower() in {"q", "quit", "exit"}:
            return None

        if not username:
            print("Username cannot be empty.")
            continue

        if username.lower() in forbidden:
            print("\nFUCK YOU NIGGA.")
            continue

        if username.lower() == "admin":
            print("Admin is reserved. Please choose another username.")
            continue

        if username_exists(username):
            print("Username already exists. Please choose another one.")
            continue

        return username


def register_password(line, username):
    ensure_file(CUSTOMER_FILE)

    while True:
        password1 = input("\nCreate password: ")
        password2 = input("Confirm password: ")

        if password1 != password2:
            print("\nPassword doesn't match! Please try again.")
            continue

        if len(password1) < 6:
            print("\nPassword must contain at least 6 characters. Please try again.")
            continue

        with open(CUSTOMER_FILE, "a", encoding="utf-8") as handle:
            handle.write(f"C{line + 1:03d}, {username}, {password1}, customer\n")
            

        print("\nAccount successfully created!")
        return True


def login():
    customers = load_customers()
    staff_members = load_staff()

    if not customers and not staff_members:
        print("No customer records found. Please register first.")

    while True:
        username = input("Please enter username (or 'q' to cancel): ").strip()
        if username.lower() in {"q", "quit", "exit"}:
            return None

        password = input("Please enter password: ").strip()

        for staff_member in staff_members:
            if staff_member["username"] == username and staff_member["password"] == password:
                print(f"\nLogin successful. Welcome, {username}!")
                return staff_member

        for customer in customers:
            if customer["username"] == username and customer["password"] == password:
                print(f"\nLogin successful. Welcome, {username}!")
                return customer

        print("Invalid username or password. Please try again.")









if __name__ == "__main__":
    try:
        from module.utils import customer_code
    except ImportError:
        from utils import customer_code

    new_username = register_username()
    if new_username:
        line = customer_code()
        register_password(line, new_username)
