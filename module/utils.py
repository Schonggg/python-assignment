import os
import sys


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

BLACK ='\u001b[30m'
RED ='\u001b[31m'
GREEN = '\u001b[32m' 
YELLOW = '\u001b[33m'
BLUE = '\u001b[34m'
MAGENTA = '\u001b[35m'
CYAN = '\u001b[36m'
WHITE = '\u001b[37m'


BG_BLACK = '\u001b[40m'
BG_RED = '\u001b[41m' 
BG_GREEN = '\u001b[42m' 
BG_YELLOW = '\u001b[43m' 
BG_BLUE = '\u001b[44m' 
BG_MAGENTA = '\u001b[45m' 
BG_CYAN = '\u001b[46m' 
BG_WHITE = '\u001b[47m' 

RESET ='\u001b[0m'


def enable_ansi_colors():
    if os.name != 'nt':
        return

    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        if handle:
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        pass


enable_ansi_colors()


def progress_bar(iteration, total, prefix='', suffix='', length=30, fill='\u2588'):
    if total <= 0:
        total = 1

    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    line = f'\r{prefix} |{bar}| {percent}% {suffix}'
    if iteration >= total:
        line = f"{GREEN}{line}{RESET}"

    sys.stdout.write(line)
    sys.stdout.flush()

# Example usage
#for i in range(101):
#    time.sleep(random.uniform(0.00000001, 0.001))
#    progress_bar(i, 100, prefix='Verifying:', suffix='Complete', length=50)
#print(f"\nLogin successful. Welcome, {username}!")