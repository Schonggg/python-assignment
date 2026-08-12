import os
import sys
import time

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
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(line.strip() + "\n")


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

def color(text, color_code, bold=False):
    style = f"{BOLD}{color_code}" if bold else color_code
    return f"{style}{text}{RESET}\n"

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


def validate_date(date_str):
    if len(date_str) != 10:
        return False

    if date_str[4] != "-" or date_str[6] != "-":
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

        if date < 1 or date > 31:
            return False

        return True

    except ValueError:
        return False 


if __name__ == "__main__":
    # 测试颜色包装函数
    print(color("【成功】 预约已创建！", GREEN, bold=True))
    print(color("【警告】 客户迟到 15 分钟！", YELLOW))
    print(color("【错误】 付款失败，余额不足！", RED, bold=True))
    print()

    # 测试进度条
    print("正在模拟生成财务报表...")
    items = 50
    for i in range(items + 1):
        progress_bar(i, items, prefix='Generating Report', suffix='Done', length=30)
        time.sleep(0.03)  # 模拟耗时操作

    print(color("报表生成完毕，已保存至 data/payments.txt！", GREEN, bold=True))