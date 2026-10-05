from datetime import date, datetime

from .utils import (
    read_lines,
    write_lines,
    primary_key,
    validate_date,
    EQUIPMENT_FILE,
    MAINTENANCE_FILE,
    SERVICE_EQUIPMENT_FILE
)

Max_Durability = 100

Status_Need_Service = "Need Service"
Status_Operational = "Operational"

Durabiltiy_Per_Use = 5


def _parse_equipment_parts(parts):

    if len(parts) not in (5, 6):
        return None

    equipment_id = parts[0]
    equipment_name = parts[1]
    category = parts[2]
    status = parts[3]
    last_service_date = parts[4]

    stored_wear = 0
    if len(parts) == 6:
        try:
            stored_wear = int(parts[5])
        except (ValueError, TypeError):
            stored_wear = 0

    # clamp into the valid 0..MAX_WEAR range
    stored_wear = max(0, min(Max_Durability, stored_wear))

    return (
        equipment_id,
        equipment_name,
        category,
        status,
        last_service_date,
        stored_wear,
    )


def day_last_service(last_service_date):
    try:
        last_service = datetime.strptime(last_service_date, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None

    return max(0, (date.today() - last_service).days)

def effective_durability(equipment):

    stored_dura = equipment.get("durability", 100)
    days = day_last_service(equipment.get("last_service_date"))

    if days is None:
        return min(Max_Durability, stored_dura)

    return min(Max_Durability, stored_dura - days)


def _write_equipment(update_fn):

    lines = read_lines(EQUIPMENT_FILE)

    if len(lines) == 0:
        return False

    updated_lines = [
        "Equipment_ID|Equipment_Name|Category|Status|Last_Service_Date|Wear"
    ]
    found = False

    for line in lines[1:]:
        parts = [part.strip() for part in line.split("|")]

        if parts and parts[0].lower() == "equipment_id":
            continue

        parsed = _parse_equipment_parts(parts)
        if parsed is None:
            continue

        (equipment_id, equipment_name, category,
         status, last_service_date, stored_wear) = parsed

        change = update_fn(parsed)
        if change is not None:
            status, last_service_date, stored_wear = change
            found = True

        updated_lines.append(
            f"{equipment_id}|{equipment_name}|{category}|"
            f"{status}|{last_service_date}|{stored_wear}"
        )

    with open(EQUIPMENT_FILE, "w", encoding="utf-8") as f:
        for line in updated_lines:
            f.write(line + "\n")

    return found


def get_equipments():
    
    equipment = []
    lines = read_lines(EQUIPMENT_FILE)
    for line in lines[1:]:
        parts = [part.strip() for part in line.split("|")]
        if parts[0].lower() in {"equipment_id"}:
            continue

        if len(parts) == 6:
            continue

        equipment_id = parts[0]
        equipment_name = parts[1]
        category = parts[2]
        status = parts[3].lower()
        last_service_date = parts[4]
        durability = parts[5]
        
        equipment.append({
            "equipment_id": equipment_id,
            "equipment_name": equipment_name,
            "category": category,
            "status": status,
            "last_service_date": last_service_date,
            "durability": durability
            })
    return equipment

def find_equipment(equipment_id):

    for equipment in get_equipments():
        if equipment["equipment_id"] == equipment_id:
            return equipment

    return None


def get_equipment_needing_service():
    # equipment needs service when either:
    #   - (today - last_service_date) >= 60 days, OR
    #   - its effective/current wear has reached MAX_WEAR (100).
    # return the list of equipment dicts that are due for service
    needing_service = []

    for equipment in get_equipments():
        due = False

        days = day_last_service(equipment["last_service_date"])
        if days is not None and days >= 60:
            due = True

        if equipment["current_wear"] >= Max_Durability:
            due = True

        if due:
            needing_service.append(equipment)

    return needing_service


def equipment_status_change(equipment_id, new_status):
    # rewrite equipment.txt, updating the Status of the matching equipment row
    # while preserving (and normalizing to 6 fields) all other data.
    # return True on success, False if the equipment_id is not found.
    def update(parsed):
        (eq_id, _name, _cat, _status, last_service_date, stored_wear) = parsed
        if eq_id == equipment_id:
            return (new_status, last_service_date, stored_wear)
        return None

    return _write_equipment(update)





def durability_decrease(equipment_id, value = Durabiltiy_Per_Use):
    def update(parsed):
        (eq_id, _name, _cat, status, last_service_date, stored_wear) = parsed
        if eq_id != equipment_id:
            return None

        new_wear = max(0, min(Max_Durability, stored_wear + value))

        if new_wear >= Max_Durability:
            status = Status_Need_Service

        return (status, last_service_date, new_wear)

    return _write_equipment(update)


def recompute_equipment_status():
    # for each equipment whose current/effective wear >= MAX_WEAR, set its
    # Status to 'Need Service' and persist. gives the menu an explicit recompute
    # path so time-based decay can flip Status without a usage event.
    # return the list of equipment_ids that were flipped to 'Need Service'.
    flipped = []

    for equipment in get_equipments():
        if equipment["current_wear"] >= Max_Durability:
            flipped.append(equipment["equipment_id"])

    for equipment_id in flipped:
        equipment_status_change(equipment_id, Status_Need_Service)

    return flipped


def get_equipment_for_service(service_id):
    # load the service<->equipment mapping (data/service_equipment.txt) and
    # return the list of Equipment_IDs mapped to the given service_id.
    # tolerant of a missing file (returns []).
    mapped = []

    lines = read_lines(SERVICE_EQUIPMENT_FILE)

    # skip the header line
    for line in lines[1:]:
        parts = [part.strip() for part in line.split("|")]

        if len(parts) < 2:
            continue

        if parts[0].lower() == "service_id":
            continue

        if parts[0] == service_id:
            mapped.append(parts[1])

    return mapped


def _ensure_trailing_newline(path):
    # some data files are stored without a trailing newline. write_lines()
    # appends in "a" mode, so without this guard a new record would be glued
    # onto the previous line and corrupt it. ensure the file ends with "\n".
    import os

    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return

    with open(path, "rb") as handle:
        handle.seek(-1, os.SEEK_END)
        last_byte = handle.read(1)

    if last_byte != b"\n":
        with open(path, "a", encoding="utf-8") as handle:
            handle.write("\n")


def record_maintenance(equipment_id, maintenance_date, cost,
                       staff_user_id, description):
    # record a maintenance job against an equipment item.
    # validate the equipment exists, the date is valid, and the cost parses.
    # append the new record to maintenance.txt, then mark the equipment as
    # Operational with its Last_Service_Date set to the maintenance date.
    # return True on success, False otherwise.

    # step 1: check the equipment exists
    if find_equipment(equipment_id) is None:
        print("Invalid Equipment ID.")
        return False

    # step 2: validate the maintenance date
    if not validate_date(maintenance_date):
        print("Invalid date.")
        print("Please use YYYY-MM-DD format.")
        return False

    # step 3: validate the cost
    try:
        cost_value = float(cost)
    except (ValueError, TypeError):
        print("Invalid cost. Please enter a number.")
        return False

    # step 4: generate the new Maint_ID
    maint_id = primary_key(MAINTENANCE_FILE)

    # step 5: append the maintenance record
    new_record = (
        f"{maint_id}|"
        f"{equipment_id}|"
        f"{maintenance_date}|"
        f"{cost_value:.2f}|"
        f"{staff_user_id}|"
        f"{description}"
    )
    _ensure_trailing_newline(MAINTENANCE_FILE)
    write_lines(MAINTENANCE_FILE, new_record)

    # step 6: update the equipment status to reflect completed maintenance.
    # a completed maintenance makes it Operational, sets Last_Service_Date and
    # resets Wear back to 0.
    def _reset_after_maintenance(parsed):
        (eq_id, _name, _cat, _status, _last, _wear) = parsed
        if eq_id == equipment_id:
            return (Status_Operational, maintenance_date, 0)
        return None

    _write_equipment(_reset_after_maintenance)

    # step 7: display confirmation
    print(f"\n{'=' * 10} MAINTENANCE RECORDED {'=' * 10}")
    print(f"Maint ID    : {maint_id}")
    print(f"Equipment ID: {equipment_id}")
    print(f"Date        : {maintenance_date}")
    print(f"Cost        : RM{cost_value:.2f}")
    print(f"Staff       : {staff_user_id}")
    print(f"Description : {description}")

    return True


def get_maintenance_records():
    # read all maintenance records from maintenance.txt
    # return them as a list of maintenance dictionaries
    records = []
    lines = read_lines(MAINTENANCE_FILE)

    # skip the header line
    for line in lines[1:]:
        parts = [part.strip() for part in line.split("|")]

        # a maintenance record should contain 6 fields
        if len(parts) != 6:
            continue

        try:
            cost = float(parts[3])
        except (ValueError, TypeError):
            cost = 0.0

        records.append({
            "maint_id": parts[0],
            "equipment_id": parts[1],
            "maintenance_date": parts[2],
            "cost": cost,
            "staff_user_id": parts[4],
            "description": parts[5]
        })

    return records


def maintenance_summary():
    # aggregate maintenance records: total count, total cost, and a
    # per-equipment breakdown (count and total cost per equipment_id).
    # return the aggregated data so the menu layer can print it.
    records = get_maintenance_records()

    total_records = len(records)
    total_cost = 0.0
    per_equipment = {}

    for record in records:
        total_cost += record["cost"]

        equipment_id = record["equipment_id"]

        if equipment_id not in per_equipment:
            per_equipment[equipment_id] = {"count": 0, "cost": 0.0}

        per_equipment[equipment_id]["count"] += 1
        per_equipment[equipment_id]["cost"] += record["cost"]

    return {
        "total_records": total_records,
        "total_cost": total_cost,
        "per_equipment": per_equipment
    }
