import os
import re
import sys
from contextlib import redirect_stdout
from datetime import date, datetime, timedelta
from io import StringIO

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
SERVICE_EQUIPMENT_FILE = os.path.join(DATA_DIR, "service_equipment.txt")

TIME_SLOTS = [
    "08:00-10:00",
    "10:00-12:00",
    "14:00-16:00",
    "16:00-18:00",
    "18:00-20:00",
]

TEAMS = ["Team Alpha", "Team Beta"]

_startup_messages = {}
_startup_messages_displayed = set()


def show_startup_messages(role):
    role = role.lower()
    if role in _startup_messages_displayed:
        return

    _startup_messages_displayed.add(role)
    for message in _startup_messages.get(role, []):
        print(message)


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


def write_lines(path, line):
    ensure_file(path)
    with open(path, "rb+") as handle:
        handle.seek(0, os.SEEK_END)
        end_position = handle.tell()
        if end_position:
            handle.seek(-1, os.SEEK_END)
            if handle.read(1) != b"\n":
                handle.seek(0, os.SEEK_END)
                handle.write(b"\n")
        handle.seek(0, os.SEEK_END)
        handle.write((line.strip() + "\n").encode("utf-8"))


def the_code(path, prefix):
    lines = read_lines(path)
    if len(lines) <= 1:
        return f"{prefix}001"

    last_line = lines[-1]

    try:
        last_id = last_line.split("|")[0].strip()

        numeric_part = last_id.replace(prefix, "")
        next_number = int(numeric_part) + 1

    except (ValueError, IndexError):
        next_number = len(lines)

    return f"{prefix}{next_number:03d}"


def primary_key(path):

    prefix_map = {
        BOOKING_FILE: "BK",
        CUSTOMER_FILE: "CUST",
        EQUIPMENT_FILE: "EQ",
        MAINTENANCE_FILE: "MNT",
        PAYMENT_FILE: "PAY",
        SCHEDULE_FILE: "SCH",
        SERVICE_FILE: "SV",
        LOG_FILE: "LOG",
        USER_FILE: "USR"        
    }
    prefix = prefix_map.get(path, "")
    return the_code(path, prefix)

RESET      ='\u001b[0m'
BOLD       ='\u001b[1m'
UNDERLINE  ='\u001b[4m'

BLACK      ='\u001b[30m'
RED        ='\u001b[31m'
GREEN      = '\u001b[32m' 
YELLOW     = '\u001b[33m'
BLUE       = '\u001b[34m'
MAGENTA    = '\u001b[35m'
CYAN       = '\u001b[36m'
WHITE      = '\u001b[37m'

#For background
BG_BLACK   = '\u001b[40m'
BG_RED     = '\u001b[41m' 
BG_GREEN   = '\u001b[42m' 
BG_YELLOW  = '\u001b[43m' 
BG_BLUE    = '\u001b[44m' 
BG_MAGENTA = '\u001b[45m' 
BG_CYAN    = '\u001b[46m' 
BG_WHITE   = '\u001b[47m' 

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

def del_ansi_len(text):
    return ANSI_RE.sub("", text)

def true_len(text):
    return len(del_ansi_len(text))

def draw_box(lines, title = None, color_code = WHITE, padding = 1):
    #崇拜我吧
    if isinstance(lines, str):
        content = lines.split("\n")

    else:
        content = list(lines)
    if not content:
        content = [""]

    width = max(true_len(line) for line in content)
    title_len = true_len(title) if title else 0
    inner_len = max(width, title_len) + padding * 2

    
    def border(text):
        return color_v2(text, color_code)
    top    = border("╔" + "═" * inner_len + "╗")
    mid    = border("║" ) 
    bottom = border("╚" + "═" * inner_len + "╝")

    tt = [top]

    if title is not None:
        total_space = inner_len - title_len
        left = total_space // 2
        right = total_space - left
        tt.append(mid + " " * left + title + " " * right + mid)
        tt.append(border("╠" + "═" * inner_len + "╣"))

    for line in content:
        gap = inner_len - true_len(line) - padding
        if gap < 0:
            gap = 0
        row = mid + " " * padding + line + " " * gap + mid
        tt.append(row)
    tt.append(bottom)
    return "\n".join(tt)


def color(text, color_code, bold=False):
    style = f"{BOLD}{color_code}" if bold else color_code
    return f"{style}{text}{RESET}\n"

def color_v2(text, *color_code):
    color = "".join(color_code)
    return f"{color}{text}{RESET}"


def progress_bar(iteration, total, prefix='', suffix='', length=30, fill='\u2588'):
    total = max(1, total)
    iteration = min(iteration, total)

    percent_num = 100 * (iteration / float(total))
    filled_length = int(length * iteration // total)

    current_color = GREEN if iteration >= total else ""

    bar = fill * filled_length + '-' * (length - filled_length)
    colored_bar = f"{current_color}{bar}{RESET}"

    line = f'\r{BOLD}{prefix}{RESET} |{colored_bar}| {percent_num:.1f}% {suffix}'
    sys.stdout.write(line)
    sys.stdout.flush()

    if iteration >= total:
        sys.stdout.write('\n')
        sys.stdout.flush()

#Example usage:
#
#custoemer = read_lines("customers.txt")
#customer_count = len(customers)

#print(f"Start printing {customer_count}customer's loyalty tier...")

#for index, customer in enumerate(customers, start=1):
#   update_customer_loyalty(customer)
#   time.sleep(0.05)


#   customer_name = customer.get('Full_Name', 'Unknown')
#   progress_bar(
#        iteration=index,
#        total=total_tasks,
#        prefix='Updating Customers: ',
#        suffix=f'({index}/{total_tasks}) Processing {customer_name}',
#        length = 30
#    )

def pause():
    input("\nPress Enter to continue...")


def success(msg):
    return color_v2(f"{msg}", GREEN, BOLD)

def warning(msg):
    return color_v2(f"{msg}", YELLOW, BOLD)

def error(msg):
    return color_v2(f"{msg}", RED, BOLD)

def info(msg):
    return color_v2(f"{msg}", CYAN)

def render_menu(title, items, color_code=WHITE):
    code_width = max((len(str(code)) for code, _ in items), default=1)

    rows = []
    for code, label in items:
        key_str = str(code).rjust(code_width)
        cover = color_v2(f"[{key_str}]", BOLD, color_code)
        row = f"{cover}  {label}"
        rows.append(row)

    framed_title = color_v2(title, BOLD, color_code)
    return draw_box(rows, title=framed_title, color_code=color_code, padding=2)

def divider(width=None, color_code=WHITE):
    if width == None:
        width = 50
    return color_v2("━" * width, color_code)


def validate_date(date_str):
    if len(date_str) != 10:
        return False

    if date_str[4] != "-" or date_str[7] != "-":
        return False

    parts = date_str.split("-")

    if len(parts) != 3:
        return False

    try:
        year = int(parts[0])
        month = int(parts[1])
        date = int(parts[2])

        if year < 2026 or year > 2045:
            return False

        if month < 1 or month >12:
            return False

        datetime(year, month, date)

        return True

    except ValueError:
        return False 
    

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def _ensure_trailing_newline(path):
    # some data files are stored without a trailing newline. write_lines()
    # appends in "a" mode, so without this guard a new record would be glued
    # onto the previous line and corrupt it. ensure the file ends with "\n".
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return

    with open(path, "rb") as handle:
        handle.seek(-1, os.SEEK_END)
        last_byte = handle.read(1)

    if last_byte != b"\n":
        with open(path, "a", encoding="utf-8") as handle:
            handle.write("\n")

def get_schedules():
    schedules = []

    lines = read_lines(SCHEDULE_FILE)

    for line in lines[1:]:
        if not line.strip():
            continue

        parts = line.split("|")

        if len(parts) != 5:
            continue

        schedule = {
            "Schedule_ID": parts[0],
            "Date": parts[1],
            "Time_Slot": parts[2],
            "Team_Assigned": parts[3],
            "Is_Booked": parts[4]
        }

        schedules.append(schedule)
    return schedules

def schedule_date_exists(date_str):
    #return True when schedules.txt already has at least one roster row for
    #the given date. used to make generation idempotent (one roster per day).
    for schedule in get_schedules():
        if schedule["Date"] == date_str:
            return True

    return False


def modify_schedule_list(schedule_id, date_str=None, time_slot=None, team=None):
    changes = {}

    if date_str is not None:
        if not validate_date(date_str):
            print(error("Invalid date."))
            print(info("Please use a valid date in YYYY-MM-DD format."))
            return False
        changes["Date"] = date_str

    if time_slot is not None:
        if time_slot not in TIME_SLOTS:
            print(error("Invalid time slot."))
            return False
        changes["Time_Slot"] = time_slot

    if team is not None:
        if team not in TEAMS:
            print(error("Invalid team."))
            return False
        changes["Team_Assigned"] = team

    if not changes:
        print(error("Enter at least one schedule value to modify."))
        return False

    lines = read_lines(SCHEDULE_FILE)
    for index, line in enumerate(lines[1:], start=1):
        parts = line.split("|")
        if len(parts) != 5 or parts[0] != schedule_id:
            continue

        if parts[4].lower() == "yes":
            print(warning("Booked schedules cannot be modified."))
            return False

        updated = parts.copy()
        fields = {
            "Date": 1,
            "Time_Slot": 2,
            "Team_Assigned": 3,
        }
        for field, value in changes.items():
            updated[fields[field]] = value

        for other_line in lines[1:]:
            other = other_line.split("|")
            if (
                len(other) == 5
                and other[0] != schedule_id
                and other[1:4] == updated[1:4]
            ):
                print(error("Another schedule already has this date, time, and team."))
                return False

        lines[index] = "|".join(updated)
        with open(SCHEDULE_FILE, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
        return True

    print(error(f"Schedule {schedule_id} was not found."))
    return False


def generate_schedule_for_date(date_str):
    #generate the daily duty roster for a single date and append it to
    #schedules.txt. each team (TEAMS) gets one row per time slot (TIME_SLOTS),
    #so a full day is len(TEAMS) * len(TIME_SLOTS) rows (2 * 5 = 10 rows).
    #
    #idempotent: if a roster already exists for this date, nothing is written.
    #returns the number of rows created (0 when the date already existed or the
    #date is invalid).
    if not validate_date(date_str):
        print(error("Invalid date."))
        print(info("Please use YYYY-MM-DD format."))
        return 0

    #de-dup by date so we never append a second roster for the same day
    if schedule_date_exists(date_str):
        return 0

    #avoid gluing the first new row onto the last existing line
    _ensure_trailing_newline(SCHEDULE_FILE)

    created = 0

    #write one team-row per time slot, pairing each slot with both teams so the
    #same (date, time_slot) ends up with one row per team.
    for time_slot in TIME_SLOTS:
        for team in TEAMS:
            #generate the next ID AFTER the previous write so IDs stay
            #sequential and unique even when writing many rows in a row.
            schedule_id = primary_key(SCHEDULE_FILE)

            new_schedule = (
                f"{schedule_id}|"
                f"{date_str}|"
                f"{time_slot}|"
                f"{team}|"
                f"No"
            )

            write_lines(SCHEDULE_FILE, new_schedule)
            created += 1

    return created


def generate_schedules(start_date, days):
    #generate daily duty rosters for a run of consecutive days starting at
    #start_date (inclusive). days must be a positive integer. returns the total
    #number of rows created across all days (dates that already existed add 0).
    if not validate_date(start_date):
        print(error("Invalid start date."))
        print(info("Please use YYYY-MM-DD format."))
        return 0

    try:
        days = int(days)
    except (TypeError, ValueError):
        print(error("Days must be a whole number."))
        return 0

    if days < 1:
        print(error("Days must be at least 1."))
        return 0

    #walk forward one calendar day at a time. we only use the standard library;
    #datetime handles month/year rollover correctly.
    current = datetime.strptime(start_date, "%Y-%m-%d")
    total_created = 0

    for _ in range(days):
        date_str = current.strftime("%Y-%m-%d")
        total_created += generate_schedule_for_date(date_str)
        current += timedelta(days=1)

    return total_created









def generate_weekly_schedule():
    start_date = date.today()
    print(draw_box(
        [f"{len(TEAMS)} teams on duty: " + ", ".join(TEAMS)]
        + [f"Slot: {slot}" for slot in TIME_SLOTS],
        title="WEEKLY SCHEDULE",
    ))

    created = generate_schedules(start_date.strftime("%Y-%m-%d"), 7)

    if created > 0:
        print(success(
            f"Generated {created} schedule rows for the week starting "
            f"{start_date.strftime('%Y-%m-%d')}."
        ))


def process_due_bookings():
    global _startup_messages, _startup_messages_displayed

    from random import choice, random

    from module.booking_pkg.booking import (
        complete_booking,
        calculate_penalty,
        find_service,
        get_bookings,
        update_attendance,
    )
    from module.finance_pkg.finance import get_payment, record_payment

    _startup_messages = {
        "admin": [],
        "officer": [],
        "accountant": [],
        "maintenance": [],
    }
    _startup_messages_displayed = set()

    schedule_output = StringIO()
    with redirect_stdout(schedule_output):
        generate_weekly_schedule()
    weekly_schedule = schedule_output.getvalue().strip()
    if weekly_schedule:
        _startup_messages["officer"].append(weekly_schedule)
        _startup_messages["admin"].append(weekly_schedule)

    schedule_dates = {}
    for line in read_lines(SCHEDULE_FILE)[1:]:
        parts = [part.strip() for part in line.split("|")]
        if len(parts) == 5:
            schedule_dates[parts[0]] = date.fromisoformat(parts[1])

    payment_booking_ids = {
        payment["booking_id"] for payment in get_payment()
    }
    today = date.today()
    completed_count = 0
    payment_count = 0
    startup_warnings = []

    for booking in get_bookings():
        if booking["Status"] != "Confirmed":
            continue

        service_date = schedule_dates.get(booking["Schedule_ID"])
        if service_date is None:
            startup_warnings.append(warning(
                f"Booking {booking['Booking_ID']} has no valid schedule date."
            ))
            continue
        if service_date > today:
            continue

        has_payment = booking["Booking_ID"] in payment_booking_ids
        service = find_service(booking["Service_ID"]) if not has_payment else None
        if not has_payment and service is None:
            startup_warnings.append(warning(
                f"Booking {booking['Booking_ID']} has no matching service; "
                "it was not completed."
            ))
            continue

        attendance_status = "Late" if random() < 0.3 else "On Time"
        attendance_output = StringIO()
        with redirect_stdout(attendance_output):
            attendance_updated = update_attendance(
                booking["Booking_ID"], attendance_status
            )
        attendance_message = attendance_output.getvalue().strip()
        if attendance_message:
            for role in ("officer", "admin", "accountant"):
                _startup_messages[role].append(attendance_message)
        if not attendance_updated:
            continue

        if not has_payment:
            base_amount = service["Price"]
            discount_amount = 0.0
            penalty_fee = calculate_penalty(attendance_status)
            tax_amount = round(
                (base_amount - discount_amount + penalty_fee) * 0.06,
                2,
            )
            total_amount = round(
                base_amount - discount_amount + penalty_fee + tax_amount,
                2,
            )

            payment_output = StringIO()
            with redirect_stdout(payment_output):
                payment_recorded = record_payment(
                    booking["Booking_ID"],
                    base_amount,
                    discount_amount,
                    penalty_fee,
                    tax_amount,
                    total_amount,
                    "Paid",
                    choice(["Cash", "E-wallet"]),
                    today.isoformat(),
                )
            payment_message = payment_output.getvalue().strip()
            if payment_message:
                _startup_messages["accountant"].append(payment_message)
                _startup_messages["admin"].append(payment_message)
            if not payment_recorded:
                continue

            payment_booking_ids.add(booking["Booking_ID"])
            payment_count += 1

        completion_output = StringIO()
        with redirect_stdout(completion_output):
            booking_completed = complete_booking(booking["Booking_ID"])
        completion_message = completion_output.getvalue().strip()
        equipment_marker = "Equipment durability decreased for:"
        if equipment_marker in completion_message:
            booking_message, equipment_message = completion_message.split(
                equipment_marker, 1
            )
            booking_message = booking_message.strip()
            equipment_message = equipment_marker + equipment_message
            if booking_message:
                _startup_messages["officer"].append(booking_message)
                _startup_messages["admin"].append(booking_message)
            _startup_messages["maintenance"].append(equipment_message.strip())
            _startup_messages["admin"].append(equipment_message.strip())
        elif completion_message:
            _startup_messages["officer"].append(completion_message)
            _startup_messages["admin"].append(completion_message)

        if booking_completed:
            completed_count += 1

    _startup_messages["admin"].extend(startup_warnings)
    _startup_messages["admin"].append(info(
        f"Startup processing finished: {completed_count} booking(s) "
        f"completed and {payment_count} new payment(s) recorded."
    ))





if __name__ == "__main__":
    print(draw_box(["Line one", "A longer second line here"], title = "NAME"))
