import os
import time
import random
from module.utils import CUSTOMER_FILE, ensure_file, primary_key, read_lines, RED, GREEN, MAGENTA, RESET, progress_bar


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CUSTOMER_FILE = os.path.join(DATA_DIR, "customers.txt")
STAFF_FILE = os.path.join(DATA_DIR, "staff.txt")
SERVICE_FILE = os.path.join(DATA_DIR, "service.txt")
BOOKING_FILE = os.path.join(DATA_DIR, "booking.txt")
MAINTENANCE_FILE = os.path.join(DATA_DIR, "maintenance.txt")
PAYMENT_FILE = os.path.join(DATA_DIR, "payment.txt")



def load_customers():
    customers = []
    for line in read_lines(CUSTOMER_FILE):
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 4:
            continue

        code = parts[0]
        username = parts[1]
        password = parts[2]
        role = parts[3].lower() if parts[3] else "customer"

        customers.append({
            "code": code,
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
            print(f"{RED}FUCK YOU NIGGA.\n {RESET}")
            continue

        if username.lower() == "admin":
            print("Admin is reserved. Please choose another username.")
            continue

        if username_exists(username):
            print("Username already exists. Please choose another one.")
            continue

        return username


def register_password(username):
    ensure_file(CUSTOMER_FILE)
    while True:
        password1 = input("\nCreate password: ")
        password2 = input("Confirm password: ")

        if password1 != password2:
            print(f"\nPassword doesn't match! Please try again.")
            continue

        if len(password1) < 6:
            print("\nPassword must contain at least 6 characters. Please try again.")
            continue

        code = primary_key(CUSTOMER_FILE)

        with open(CUSTOMER_FILE, "a", encoding="utf-8") as handle:
            handle.write(f"{code}, {username}, {password1}, customer\n")
            

        print("\nAccount successfully created!")
        return True


def login():
    customers = load_customers()
    staff_members = load_staff()

    if not customers and not staff_members:
        print("No customer records found. Please register first.")
        return None

    while True:
        username = input("Please enter username (or 'q' to cancel): ").strip()
        if username.lower() in {"q", "quit", "exit"}:
            return None

        password = input("Please enter password: ").strip()

        for staff_member in staff_members:
            if staff_member["username"] == username and staff_member["password"] == password:
                for i in range(101):
                    time.sleep(random.uniform(0.001, 0.1))
                    progress_bar(i, 100, prefix='Verifying:', suffix='Complete', length=50)
                print(f"\nLogin successful. Welcome, {MAGENTA}{username}{RESET}!")
                return staff_member

        for customer in customers:
            if customer["username"] == username and customer["password"] == password:
                for i in range(101):
                    time.sleep(random.uniform(0.00000001, 0.001))
                    progress_bar(i, 100, prefix='Verifying:', suffix='Complete', length=50)
                print(f"\nLogin successful. Welcome, {MAGENTA}{username}{RESET}!")
                return customer

        print("Invalid username or password. Please try again.")









if __name__ == "__main__":
    new_username = register_username()
    if new_username:
        register_password(new_username)
