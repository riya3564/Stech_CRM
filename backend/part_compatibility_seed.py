from app import app
from extensions import db

from models.repair_code import RepairCode
from models.diagnosis_code import DiagnosisCode
from models.part import Part
from models.part_compatibility import PartCompatibility


# ---------------------------------------------------------
# Keyword-based part selection
# ---------------------------------------------------------

PART_KEYWORDS = {
    "TV": [
        ("power", "PWR-SMPS"),
        ("smps", "PWR-SMPS"),
        ("main board", "MB-TV"),
        ("motherboard", "MB-TV"),
        ("backlight", "BL-TV"),
        ("display", "PANEL-TV"),
        ("panel", "PANEL-TV"),
        ("t-con", "TCON-TV"),
        ("speaker", "SPK-TV"),
        ("audio", "SPK-TV"),
        ("remote", "REM-TV"),
        ("wifi", "WIFI-TV"),
        ("wi-fi", "WIFI-TV"),
        ("bluetooth", "BT-TV"),
        ("antenna", "ANT-TV"),
        ("ir receiver", "IR-TV"),
        ("keypad", "KEY-TV"),
        ("lvds", "LVDS-TV"),
    ],

    "AC": [
        ("compressor", "COMP-AC"),
        ("condenser", "COND-AC"),
        ("evaporator", "EVAP-AC"),
        ("fan", "FAN-AC"),
        ("motor", "FAN-AC"),
        ("pcb", "PCB-AC"),
        ("power", "SMPS-AC"),
        ("capacitor", "CAP-AC"),
        ("sensor", "SENS-AC"),
        ("temperature", "SENS-AC"),
        ("remote", "REM-AC"),
        ("valve", "VALVE-AC"),
        ("drain", "DRAIN-AC"),
        ("switch", "SW-AC"),
    ],

    "REF": [
        ("compressor", "COMP-REF"),
        ("condenser", "COND-REF"),
        ("evaporator", "EVAP-REF"),
        ("fan", "FAN-REF"),
        ("motor", "FAN-REF"),
        ("pcb", "PCB-REF"),
        ("sensor", "SENS-REF"),
        ("temperature", "SENS-REF"),
        ("thermostat", "THERM-REF"),
        ("relay", "RELAY-REF"),
        ("capacitor", "CAP-REF"),
        ("valve", "VALVE-REF"),
        ("door", "DOOR-REF"),
        ("gasket", "GASKET-REF"),
    ],

    "WM": [
        ("motor", "MOTOR-WM"),
        ("pcb", "PCB-WM"),
        ("pump", "PUMP-WM"),
        ("drain", "PUMP-WM"),
        ("valve", "VALVE-WM"),
        ("water", "SENS-WM"),
        ("sensor", "SENS-WM"),
        ("door", "DOOR-WM"),
        ("belt", "BELT-WM"),
        ("drum", "DRUM-WM"),
        ("capacitor", "CAP-WM"),
        ("panel", "PANEL-WM"),
        ("hose", "HOSE-WM"),
    ],

    "MW": [
        ("magnetron", "MAG-MW"),
        ("transformer", "HV-MW"),
        ("high voltage", "HV-MW"),
        ("capacitor", "CAP-MW"),
        ("diode", "DIODE-MW"),
        ("pcb", "PCB-MW"),
        ("turntable", "MOTOR-MW"),
        ("motor", "MOTOR-MW"),
        ("fan", "FAN-MW"),
        ("door", "DOOR-MW"),
        ("interlock", "SW-MW"),
        ("switch", "SW-MW"),
        ("lamp", "LAMP-MW"),
        ("fuse", "FUSE-MW"),
    ],

    "GEY": [
        ("heater", "HEAT-GEY"),
        ("heating", "HEAT-GEY"),
        ("thermostat", "THERM-GEY"),
        ("pcb", "PCB-GEY"),
        ("sensor", "SENS-GEY"),
        ("temperature", "SENS-GEY"),
        ("valve", "VALVE-GEY"),
        ("tank", "TANK-GEY"),
        ("anode", "ANODE-GEY"),
        ("capacitor", "CAP-GEY"),
        ("fuse", "FUSE-GEY"),
        ("indicator", "IND-GEY"),
    ],

    "LAP": [
        ("motherboard", "MB-LAP"),
        ("main board", "MB-LAP"),
        ("battery", "BAT-LAP"),
        ("charging", "CHG-LAP"),
        ("charging port", "CHG-LAP"),
        ("adapter", "ADP-LAP"),
        ("power", "ADP-LAP"),
        ("ram", "RAM-LAP"),
        ("memory", "RAM-LAP"),
        ("ssd", "SSD-LAP"),
        ("storage", "SSD-LAP"),
        ("fan", "FAN-LAP"),
        ("keyboard", "KB-LAP"),
        ("display", "LCD-LAP"),
        ("screen", "LCD-LAP"),
        ("camera", "CAM-LAP"),
        ("speaker", "SPK-LAP"),
        ("wifi", "WIFI-LAP"),
        ("wi-fi", "WIFI-LAP"),
    ],

    "MOB": [
        ("battery", "BAT-MOB"),
        ("display", "LCD-MOB"),
        ("screen", "LCD-MOB"),
        ("main board", "MB-MOB"),
        ("motherboard", "MB-MOB"),
        ("charging", "CHG-MOB"),
        ("charging port", "CHG-MOB"),
        ("camera", "CAM-MOB"),
        ("speaker", "SPK-MOB"),
        ("microphone", "MIC-MOB"),
        ("mic", "MIC-MOB"),
        ("vibration", "VIB-MOB"),
        ("wifi", "WIFI-MOB"),
        ("wi-fi", "WIFI-MOB"),
        ("bluetooth", "WIFI-MOB"),
        ("antenna", "ANT-MOB"),
        ("flex", "FLEX-MOB"),
    ],
}


def find_part(category_code, text):
    """
    Find the most appropriate part using the
    repair + diagnosis text.
    """

    text = text.lower()

    rules = PART_KEYWORDS.get(
        category_code,
        []
    )

    for keyword, part_code in rules:

        if keyword in text:

            part = Part.query.filter_by(
                part_code=part_code
            ).first()

            if part:
                return part

    return None


with app.app_context():

    repairs = (
        RepairCode.query
        .order_by(RepairCode.id.asc())
        .all()
    )

    print("=" * 70)
    print("PART COMPATIBILITY SEED")
    print("=" * 70)

    print(
        f"Repairs in database : {len(repairs)}"
    )

    if not repairs:
        print("ERROR: No repair records found.")
        raise SystemExit(1)

    created = 0
    skipped = 0
    unmapped = []
    invalid_mappings = []

    # ---------------------------------------------------------
    # Process every repair
    # ---------------------------------------------------------

    for repair in repairs:

        diagnosis = repair.diagnosis

        if not diagnosis:
            unmapped.append({
                "repair_id": repair.id,
                "reason": "Diagnosis not found"
            })
            continue

        category = diagnosis.category

        if not category:
            unmapped.append({
                "repair_id": repair.id,
                "reason": "Category not found"
            })
            continue

        category_code = category.category_code

        searchable_text = " ".join([
            repair.repair_name or "",
            repair.description or "",
            diagnosis.diagnosis_name or "",
            diagnosis.description or "",
            repair.fault.fault_name
            if repair.fault
            else ""
        ])

        part = find_part(
            category_code,
            searchable_text
        )

        # -----------------------------------------------------
        # Fallback: category-compatible part
        # -----------------------------------------------------

        if not part:

            part = (
                Part.query
                .filter_by(
                    category_id=category.id,
                    status="Active"
                )
                .order_by(Part.id.asc())
                .first()
            )

        if not part:

            unmapped.append({
                "repair_id": repair.id,
                "repair_code": repair.repair_code,
                "category": category_code,
                "reason": "No compatible part found"
            })
            continue

        # -----------------------------------------------------
        # Validate category
        # -----------------------------------------------------

        if part.category_id != category.id:

            invalid_mappings.append({
                "repair_id": repair.id,
                "repair_code": repair.repair_code,
                "part_id": part.id,
                "part_code": part.part_code,
                "reason": "Category mismatch"
            })

            continue

        # -----------------------------------------------------
        # Duplicate check
        # -----------------------------------------------------

        existing = PartCompatibility.query.filter_by(
            diagnosis_id=diagnosis.id,
            repair_id=repair.id,
            part_id=part.id
        ).first()

        if existing:
            skipped += 1
            continue

        # -----------------------------------------------------
        # Create compatibility
        # -----------------------------------------------------

        compatibility = PartCompatibility(
            product_model_id=diagnosis.product_model_id,
            diagnosis_id=diagnosis.id,
            repair_id=repair.id,
            part_id=part.id,
            priority=1,
            is_active=True,
            notes=(
                "Primary compatible part mapped "
                "from Repair Master."
            )
        )

        db.session.add(compatibility)
        created += 1

    db.session.commit()

    # ---------------------------------------------------------
    # FINAL VALIDATION
    # ---------------------------------------------------------

    compatibility_records = (
        PartCompatibility.query
        .all()
    )

    repair_ids = {
        repair.id
        for repair in repairs
    }

    mapped_repair_ids = {
        record.repair_id
        for record in compatibility_records
    }

    missing_repairs = (
        repair_ids - mapped_repair_ids
    )

    extra_repairs = (
        mapped_repair_ids - repair_ids
    )

    # ---------------------------------------------------------
    # Validate every compatibility record
    # ---------------------------------------------------------

    for record in compatibility_records:

        repair = db.session.get(
            RepairCode,
            record.repair_id
        )

        diagnosis = db.session.get(
            DiagnosisCode,
            record.diagnosis_id
        )

        part = db.session.get(
            Part,
            record.part_id
        )

        if not repair:
            invalid_mappings.append({
                "record_id": record.id,
                "reason": "Invalid repair reference"
            })
            continue

        if not diagnosis:
            invalid_mappings.append({
                "record_id": record.id,
                "reason": "Invalid diagnosis reference"
            })
            continue

        if not part:
            invalid_mappings.append({
                "record_id": record.id,
                "reason": "Invalid part reference"
            })
            continue

        if repair.diagnosis_id != diagnosis.id:
            invalid_mappings.append({
                "record_id": record.id,
                "reason": "Repair-Diagnosis mismatch"
            })

        if repair.fault_id != diagnosis.fault_id:
            invalid_mappings.append({
                "record_id": record.id,
                "reason": "Repair-Fault mismatch"
            })

        if part.category_id != diagnosis.category_id:
            invalid_mappings.append({
                "record_id": record.id,
                "reason": "Part-Category mismatch"
            })

        if (
            record.product_model_id
            != diagnosis.product_model_id
        ):
            invalid_mappings.append({
                "record_id": record.id,
                "reason": "Product Model mismatch"
            })

    # ---------------------------------------------------------
    # Result
    # ---------------------------------------------------------

    print()
    print("=" * 70)
    print("PART COMPATIBILITY RESULT")
    print("=" * 70)

    print(
        f"Repairs processed    : {len(repairs)}"
    )

    print(
        f"Mappings created     : {created}"
    )

    print(
        f"Mappings skipped     : {skipped}"
    )

    print(
        f"Compatibility records: "
        f"{len(compatibility_records)}"
    )

    print(
        f"Unmapped repairs     : "
        f"{len(unmapped)}"
    )

    print(
        f"Missing repairs      : "
        f"{len(missing_repairs)}"
    )

    print(
        f"Extra repairs        : "
        f"{len(extra_repairs)}"
    )

    print(
        f"Invalid mappings     : "
        f"{len(invalid_mappings)}"
    )

    print()
    print("=" * 70)
    print("FINAL COVERAGE CHECK")
    print("=" * 70)

    covered = len(
        repair_ids & mapped_repair_ids
    )

    print(
        f"Repairs covered : "
        f"{covered} / {len(repairs)}"
    )

    print(
        f"Mappings       : "
        f"{len(compatibility_records)}"
    )

    if (
        covered == len(repairs)
        and not missing_repairs
        and not extra_repairs
        and not unmapped
        and not invalid_mappings
    ):
        print("Coverage       : PASS")
        print("Status         : SUCCESS")

    else:
        print("Coverage       : FAIL")
        print("Status         : CHECK REQUIRED")

        if unmapped:
            print()
            print("UNMAPPED REPAIRS:")
            for item in unmapped[:20]:
                print(item)

        if missing_repairs:
            print()
            print(
                "MISSING REPAIR IDs:",
                sorted(missing_repairs)
            )

        if invalid_mappings:
            print()
            print("INVALID MAPPINGS:")
            for item in invalid_mappings[:20]:
                print(item)

        raise SystemExit(1)

    print("=" * 70)