from datetime import date

from .utils import (
    read_lines,
    EQUIPMENT_FILE
)

def get_equipments():
    
    equipment = []
    lines = read_lines(EQUIPMENT_FILE)
    for line in lines[1:]:
        parts = [part.strip() for part in line.split("|")]
        if parts[0].lower() in {"equipment_id"}:
            continue

        if len(parts) == 5:
            continue

        equipment_id = parts[0]
        equipment_name = parts[1]
        category = parts[2]
        status = parts[3].lower()
        last_service_date = parts[4]
        
        equipment.append({
            "equipment_id": equipment_id,
            "equipment_name": equipment_name,
            "category": category,
            "status": status,
            "last_service_date": last_service_date
            })
    return equipment



def equipment_status_change():
# Change the status if today - last_service_date >= 60days
# Each maintenance cost 1 day
# Update status after maintenance done
    equipments = get_equipments()

    for status in equipments:

        if status["status"] == status:
            return status

    return None


def record_maintenance():
# start maintenance

def get_maintenance_records():


def maintenance_summary():
