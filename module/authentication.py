import os
import sys
import time
import random
from datetime import date, datetime, timedelta
from utils import (
    ensure_file, 
    read_lines, 
    write_lines, 
    primary_key, 
    read_lines, 
    color, 
    progress_bar, 
    validate_date, 
    clear_screen, 
    RED, 
    GREEN
)



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
BOOKING_FILE = os.path.join(DATA_DIR, "bookings.txt")
CUSTOMER_FILE = os.path.join(DATA_DIR, "customers.txt")
EQUIPMENT_FILE = os.path.join(DATA_DIR, "equipment.txt")
MAINTENANCE_FILE = os.path.join(DATA_DIR, "maintenance.txt")
PAYMENT_FILE = os.path.join(DATA_DIR, "payments.txt")
SCHEDULE_FILE = os.path.join(DATA_DIR, "schedules.txt")
SERVICE_FILE = os.path.join(DATA_DIR, "service.txt")
LOG_FILE = os.path.join(DATA_DIR, "logs.txt")
USER_FILE = os.path.join(DATA_DIR, "users.txt")


def load_users():
    
    users = []
    for line in read_lines(USER_FILE):
        parts = [part.strip() for part in line.split("|")]
        if parts[0].lower() in {"user_id", "customer_id"}:
            continue

        if len(parts) < 5:
            continue

        user_id = parts[0]
        username = parts[1]
        password = parts[2]
        role = parts[3].lower()
        
        users.append({
            "username": username,
            "password": password,
            "role": role,
            })
    return users



def username_exists(username):
    for account in load_users():
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
            print(color("FUCK YOU NIGGA", RED, bold=True))
            continue

        if username.lower() == "admin" or username.lower() == "officer1" or username.lower() == "accountant1" or username.lower() == "tech_boon":
            print(color("Admin is reserved. Please choose another username.", RED))
            continue

        if username_exists(username):
            print(color("Username already exists. Please choose another one.", RED))
            continue

        return username


def register_all(username):
    while True:
        password1 = input("\nCreate password: ").strip()
        password2 = input("Confirm password: ").strip()

        if password1 != password2:
            print(color("Password doesn't match! Please try again.", RED))
            continue

        if len(password1) < 6:
            print(color("Password must contain at least 6 characters. Please try again.", RED))
            continue

        full_name = input("\nPlease enter full name: ").strip()

        while True:
            phone = input("\nPlease enter phone number: ").strip().replace(" ", "")

            if not phone.isdigit():
                print(color("Phone number must contain only number. Please try again.", RED))
                continue

            if phone.startswith("011") or phone.startswith("015"):
                if len(phone) != 11:
                    print(color("Phone number must be 11 character. Please try again.", RED))
                    continue
            else:
                if len(phone) != 10:
                    print(color("Phone number must be 10 character. Please try again.", RED))
                    continue
            break
        email = input("\nPlesae enter email: ").strip()

        code_user = primary_key(USER_FILE)
        line_user = f"\n{code_user}|{username}|{password2}|Customer|{date.today()}\n"

        code_customer = primary_key(CUSTOMER_FILE)
        line_customer = f"\n{code_customer}|{code_user}|{full_name}|{phone}|{email}|1|Bronze\n"

        write_lines(USER_FILE, line_user)
        write_lines(CUSTOMER_FILE, line_customer)

        clear_screen()
        print("Registering...")
        items = 8
        for i in range(items + 1):
            progress_bar(i, items, prefix='Registering User', suffix='Done', length=30)
            time.sleep(random.uniform(0.01, 0.1))

        return True


def login(username, password):
    users = load_users()

    if not users:
        print("No customer records found. Please register first.")
        return None

    while True:
        username = input("Please enter username (or 'q' to cancel): ").strip()
        if username.lower() in {"q", "quit", "exit"}:
            return None

        password = input("Please enter password: ").strip()

        matched_user = None
        for user in users:
            if user["username"] == username and user["password"] == password:
                matched_user = user
                break

        if matched_user:
            for i in range(101):
                time.sleep(random.uniform(0.01, 0.1))
                progress_bar(i, 100, prefix='Verifying:', suffix='Complete', length=50)
            user_role = matched_user["role"]
            user_name = matched_user["username"]
            print(color(f"Login successful. Welcome, {user_name}! [{user_role}]", GREEN, bold=True))

            return matched_user

        print(color("Error: Invalid username or password.", RED))
        return None
    

if __name__ == "__main__":
    clear_screen()
    new_username = register_username()
    if new_username:
        register_all(new_username)
