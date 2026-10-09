from datetime import date, datetime

from ..utils import (
    read_lines,
    write_lines,
    primary_key,
    draw_box,
    validate_date,
    error,
    warning,
    info,
    EQUIPMENT_FILE,
    MAINTENANCE_FILE,
    SERVICE_EQUIPMENT_FILE
)

Max_Durability = 100

Status_Need_Service = "Need Service"
Status_Operational = "Operational"

Durability_Per_Use = 5


def parse_equipment_parts(parts):

    if len(parts) not in (5, 6):
        return None

    equipment_id = parts[0]
    equipment_name = parts[1]
    category = parts[2]
    status = parts[3].strip()
    if status.casefold() == "in repair":
        status = Status_Need_Service
    elif status.casefold() == Status_Need_Service.casefold():
        status = Status_Need_Service
    elif status.casefold() == Status_Operational.casefold():
        status = Status_Operational
    last_service_date = parts[4]

    stored_durability = Max_Durability
    if len(parts) == 6:
        try:
            stored_durability = int(parts[5])
        except (ValueError, TypeError):
            stored_durability = Max_Durability

    stored_durability = max(0, min(Max_Durability, stored_durability))

    return (
        equipment_id,
        equipment_name,
        category,
        status,
        last_service_date,
        stored_durability,
    )


def day_last_service(last_service_date):
    try:
        last_service = datetime.strptime(last_service_date, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None

    return max(0, (date.today() - last_service).days)

def effective_durability(equipment):
    stored_durability = equipment.get("durability", 100)
    days = day_last_service(equipment.get("last_service_date"))

    if days is None:
        return max(0, min(Max_Durability, stored_durability))

    return max(0, min(Max_Durability, stored_durability - days))


def write_equipment(update_fn):

    lines = read_lines(EQUIPMENT_FILE)

    if len(lines) == 0:
        return False

    updated_lines = [
        "Equipment_ID|Equipment_Name|Category|Status|Last_Service_Date|Durability"
    ]
    found = False

    for line in lines[1:]:
        parts = [part.strip() for part in line.split("|")]

        if parts and parts[0].lower() == "equipment_id":
            continue

        parsed = parse_equipment_parts(parts)
        if parsed is None:
            continue

        (equipment_id, equipment_name, category,
         status, last_service_date, stored_durability) = parsed

        change = update_fn(parsed)
        if change is not None:
            status, last_service_date, stored_durability = change
            found = True

        updated_lines.append(
            f"{equipment_id}|{equipment_name}|{category}|"
            f"{status}|{last_service_date}|{stored_durability}"
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

        parsed = parse_equipment_parts(parts)
        if parsed is None:
            continue

        (equipment_id, equipment_name, category,
         status, last_service_date, stored_durability) = parsed

        record = {
            "equipment_id": equipment_id,
            "equipment_name": equipment_name,
            "category": category,
            "status": status.lower(),
            "last_service_date": last_service_date,
            "durability": stored_durability,
        }
        record["current_durability"] = effective_durability(record)

        equipment.append(record)
    return equipment

def find_equipment(equipment_id):

    for equipment in get_equipments():
        if equipment["equipment_id"] == equipment_id:
            return equipment

    return None


def get_equipment_needing_service():

    needing_service = []

    for equipment in get_equipments():
        if equipment["current_durability"] <= 0:
            needing_service.append(equipment)

    return needing_service


def equipment_status_change(equipment_id, new_status):

    if new_status not in (Status_Need_Service, Status_Operational):
        print(error("Status must be Need Service or Operational."))
        return False

    def update(parsed):
        (eq_id, _name, _cat, _status, last_service_date, stored_durability) = parsed
        if eq_id == equipment_id:
            return (new_status, last_service_date, stored_durability)
        return None

    return write_equipment(update)





def durability_decrease(equipment_id, value=Durability_Per_Use):
    def update(parsed):
        (eq_id, _name, _cat, status, last_service_date, stored_durability) = parsed
        if eq_id != equipment_id:
            return None

        new_durability = max(
            0,
            min(Max_Durability, stored_durability - value),
        )

        if new_durability <= 0:
            status = Status_Need_Service

        return (status, last_service_date, new_durability)

    return write_equipment(update)


def recompute_equipment_status():

    flipped = []

    for equipment in get_equipments():
        target_status = (
            Status_Need_Service
            if equipment["current_durability"] <= 0
            else Status_Operational
        )
        if equipment["status"] != target_status.lower():
            flipped.append(equipment["equipment_id"])
            equipment_status_change(equipment["equipment_id"], target_status)

    return flipped


def get_equipment_for_service(service_id):

    mapped = []

    lines = read_lines(SERVICE_EQUIPMENT_FILE)

    for line in lines[1:]:
        parts = [part.strip() for part in line.split("|")]

        if len(parts) < 2:
            continue

        if parts[0].lower() == "service_id":
            continue

        if parts[0] == service_id:
            mapped.append(parts[1])

    return mapped


def record_maintenance(equipment_id, maintenance_date, cost,
                       staff_user_id, description):

    if find_equipment(equipment_id) is None:
        print(warning("Invalid Equipment ID."))
        return False

    if not validate_date(maintenance_date):
        print(warning("Invalid date."))
        print(info("Please use YYYY-MM-DD format."))
        return False

    try:
        cost_value = float(cost)
    except (ValueError, TypeError):
        print("Invalid cost. Please enter a number.")
        return False

    maint_id = primary_key(MAINTENANCE_FILE)

    new_record = (
        f"{maint_id}|"
        f"{equipment_id}|"
        f"{maintenance_date}|"
        f"{cost_value:.2f}|"
        f"{staff_user_id}|"
        f"{description}"
    )
    write_lines(MAINTENANCE_FILE, new_record)

    def _reset_after_maintenance(parsed):
        (eq_id, _name, _cat, _status, _last, _durability) = parsed
        if eq_id == equipment_id:
            return (Status_Operational, maintenance_date, Max_Durability)
        return None

    write_equipment(_reset_after_maintenance)

    print(draw_box(
        [
            f"Maint ID    : {maint_id}",
            f"Equipment ID: {equipment_id}",
            f"Date        : {maintenance_date}",
            f"Cost        : RM{cost_value:.2f}",
            f"Staff       : {staff_user_id}",
            f"Description : {description}"       
        ], "MAINTENANCE RECORDED"
    ))

    return True


def get_maintenance_records():
    records = []
    lines = read_lines(MAINTENANCE_FILE)

    for line in lines[1:]:
        parts = [part.strip() for part in line.split("|")]


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
