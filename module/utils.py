# customer_code generation
# booking_id generation
# read the data inside the file
# write the data into the file

import os
from module.authentication import ensure_file

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CUSTOMER_FILE = os.path.join(DATA_DIR, "customers.txt")
BOOKING_FILE = os.path.join(DATA_DIR, "booking.txt")

def customer_code():
    ensure_file(CUSTOMER_FILE)
    with open(CUSTOMER_FILE, "r", encoding="utf-8") as line_count:
        return len(line_count.readlines())


def booking_id():
    ensure_file(BOOKING_FILE)

    while True:
        with open(BOOKING_FILE, "r", encoding = "utf-8") as booking_count:
            booking_id = len(booking_count.readlines())


