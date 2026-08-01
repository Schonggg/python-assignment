import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CUSTOMER_FILE = os.path.join(DATA_DIR, "customers.txt")
STAFF_FILE = os.path.join(DATA_DIR, "staff.txt")
SERVICE_FILE = os.path.join(DATA_DIR, "service.txt")
BOOKING_FILE = os.path.join(DATA_DIR, "bookings.txt")
MAINTENANCE_FILE = os.path.join(DATA_DIR, "maintenance.txt")
PAYMENT_FILE = os.path.join(DATA_DIR, "payments.txt")


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


def write_lines(path, lines):
    ensure_file(path)
    with open(path, "w", encoding="utf-8") as handle:
        if lines:
            handle.write("\n".join(lines) + "\n")


def the_code(path, prefix):
    ensure_file(path)
    with open(path, "r", encoding="utf-8") as handle:
        next_number = len(handle.readlines()) + 1
    return f"{prefix}{next_number:03d}"


def primary_key(path):
    if path == CUSTOMER_FILE:
        return the_code(path, "C")
    if path == BOOKING_FILE:
        return the_code(path, "B")
    if path == STAFF_FILE:
        return the_code(path, "ST")
    if path == SERVICE_FILE:
        return the_code(path, "SV")
    if path == MAINTENANCE_FILE:
        return the_code(path, "M")
    if path == PAYMENT_FILE:
        return the_code(path, "P")
    return the_code(path, "")


def customer_code():
    return primary_key(CUSTOMER_FILE)