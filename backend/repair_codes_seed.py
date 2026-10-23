from app import app
from extensions import db
from models.diagnosis_code import DiagnosisCode
from models.repair_code import RepairCode


def build_repair_name(diagnosis):
    """
    Generate a practical repair action from the diagnosis/fault name.
    The repair remains linked to the exact existing diagnosis and fault.
    """

    text = (
        f"{diagnosis.diagnosis_name} "
        f"{diagnosis.fault.fault_name if diagnosis.fault else ''}"
    ).lower()

    if "panel" in text or "display" in text:
        return "Display Panel / Display Assembly Replacement"

    if "backlight" in text:
        return "Backlight Circuit / LED Strip Repair or Replacement"

    if "power" in text or "smps" in text or "power supply" in text:
        return "Power Supply / SMPS Repair or Replacement"

    if "main board" in text or "motherboard" in text:
        return "Main Board Repair or Replacement"

    if "t-con" in text or "timing controller" in text:
        return "T-Con Board Repair or Replacement"

    if "speaker" in text or "audio" in text:
        return "Speaker / Audio Circuit Repair or Replacement"

    if "remote" in text:
        return "Remote Control Replacement or Repair"

    if "wifi" in text or "wi-fi" in text:
        return "Wi-Fi Module / Network Circuit Repair or Replacement"

    if "bluetooth" in text:
        return "Bluetooth Module / Circuit Repair or Replacement"

    if "antenna" in text:
        return "Antenna Circuit Repair or Replacement"

    if "compressor" in text:
        return "Compressor Repair or Replacement"

    if "condenser" in text:
        return "Condenser System Repair or Replacement"

    if "evaporator" in text:
        return "Evaporator System Repair or Replacement"

    if "fan" in text:
        return "Fan Motor / Fan Assembly Repair or Replacement"

    if "motor" in text:
        return "Motor Repair or Replacement"

    if "pump" in text:
        return "Pump Repair or Replacement"

    if "drain" in text:
        return "Drain System Repair or Replacement"

    if "sensor" in text:
        return "Sensor Repair or Replacement"

    if "thermostat" in text:
        return "Thermostat Repair or Replacement"

    if "heater" in text or "heating" in text:
        return "Heating Element / Heater Repair or Replacement"

    if "capacitor" in text:
        return "Capacitor Replacement"

    if "relay" in text:
        return "Relay Repair or Replacement"

    if "wiring" in text or "wire" in text:
        return "Wiring Harness / Connection Repair"

    if "switch" in text:
        return "Switch Repair or Replacement"

    if "valve" in text:
        return "Valve Repair or Replacement"

    if "door" in text:
        return "Door Assembly / Door Mechanism Repair or Replacement"

    if "keyboard" in text:
        return "Keyboard Replacement"

    if "battery" in text:
        return "Battery Replacement"

    if "charging" in text or "charger" in text:
        return "Charging Circuit / Charging Port Repair"

    if "camera" in text:
        return "Camera Module Replacement"

    if "microphone" in text:
        return "Microphone Module Repair or Replacement"

    if "storage" in text or "hard disk" in text or "ssd" in text:
        return "Storage Device Repair or Replacement"

    if "ram" in text or "memory" in text:
        return "RAM / Memory Module Replacement"

    if "motherboard" in text:
        return "Motherboard Repair or Replacement"

    if "software" in text or "firmware" in text:
        return "Software / Firmware Reinstallation or Update"

    if "network" in text or "connectivity" in text:
        return "Network / Connectivity Circuit Repair"

    if "leak" in text:
        return "Leakage Inspection and System Repair"

    if "gas" in text or "refrigerant" in text:
        return "Refrigerant / Gas System Service and Repair"

    if "water" in text:
        return "Water Supply / Drainage System Repair"

    if "cooling" in text:
        return "Cooling System Repair or Component Replacement"

    if "heating" in text:
        return "Heating System Repair or Component Replacement"

    if "noise" in text or "vibration" in text:
        return "Mechanical Assembly Inspection and Repair"

    if "error" in text or "software" in text:
        return "System Reset / Software or Firmware Service"

    return "Component Inspection, Repair or Replacement"


with app.app_context():

    diagnoses = (
        DiagnosisCode.query
        .order_by(DiagnosisCode.id.asc())
        .all()
    )

    diagnosis_count = len(diagnoses)

    print("=" * 70)
    print("REPAIR MASTER COVERAGE VALIDATION")
    print("=" * 70)

    print(f"Diagnoses in database : {diagnosis_count}")

    if diagnosis_count == 0:
        print("ERROR: No diagnoses found.")
        raise SystemExit(1)

    # ---------------------------------------------------------
    # Validate that every diagnosis has a valid fault reference
    # ---------------------------------------------------------

    invalid_faults = []

    for diagnosis in diagnoses:
        if diagnosis.fault is None:
            invalid_faults.append(diagnosis.id)

    print(f"Invalid fault references : {len(invalid_faults)}")

    if invalid_faults:
        print("ERROR: Some diagnoses have invalid fault references.")
        print("Diagnosis IDs:", invalid_faults)
        raise SystemExit(1)

    # ---------------------------------------------------------
    # Create exactly one repair for every diagnosis
    # ---------------------------------------------------------

    created = 0
    skipped = 0

    for diagnosis in diagnoses:

        existing = RepairCode.query.filter_by(
            diagnosis_id=diagnosis.id
        ).first()

        if existing:
            skipped += 1
            continue

        category = diagnosis.category
        category_code = category.category_code if category else "GEN"

        repair_code = (
            f"REP-{category_code}-"
            f"{diagnosis.id:04d}"
        )

        repair_name = build_repair_name(diagnosis)

        repair = RepairCode(
            repair_code=repair_code,
            repair_name=repair_name,
            description=(
                f"Repair action for diagnosis "
                f"{diagnosis.diagnosis_code}: "
                f"{diagnosis.diagnosis_name}"
            ),
            category_id=diagnosis.category_id,
            product_type_id=diagnosis.product_type_id,
            product_model_id=diagnosis.product_model_id,
            fault_id=diagnosis.fault_id,
            diagnosis_id=diagnosis.id,
            status="Active"
        )

        db.session.add(repair)
        created += 1

    db.session.commit()

    # ---------------------------------------------------------
    # FINAL COVERAGE VALIDATION
    # ---------------------------------------------------------

    repairs = RepairCode.query.all()

    diagnosis_ids = {
        diagnosis.id
        for diagnosis in diagnoses
    }

    repair_diagnosis_ids = {
        repair.diagnosis_id
        for repair in repairs
    }

    missing_diagnoses = diagnosis_ids - repair_diagnosis_ids
    extra_diagnoses = repair_diagnosis_ids - diagnosis_ids

    invalid_repair_refs = []

    for repair in repairs:

        diagnosis = DiagnosisCode.query.get(
            repair.diagnosis_id
        )

        if diagnosis is None:
            invalid_repair_refs.append(repair.id)
            continue

        if repair.fault_id != diagnosis.fault_id:
            invalid_repair_refs.append(repair.id)
            continue

        if repair.category_id != diagnosis.category_id:
            invalid_repair_refs.append(repair.id)
            continue

        if repair.product_type_id != diagnosis.product_type_id:
            invalid_repair_refs.append(repair.id)
            continue

        if repair.product_model_id != diagnosis.product_model_id:
            invalid_repair_refs.append(repair.id)
            continue

    # ---------------------------------------------------------
    # RESULT
    # ---------------------------------------------------------

    print()
    print("=" * 70)
    print("REPAIR MASTER SEED RESULT")
    print("=" * 70)

    print(f"Diagnoses in database : {diagnosis_count}")
    print(f"Repairs created       : {created}")
    print(f"Repairs skipped       : {skipped}")
    print(f"Repairs in database   : {len(repairs)}")
    print(f"Missing diagnoses     : {len(missing_diagnoses)}")
    print(f"Extra diagnoses       : {len(extra_diagnoses)}")
    print(f"Invalid repair refs   : {len(invalid_repair_refs)}")

    print()
    print("=" * 70)
    print("FINAL COVERAGE CHECK")
    print("=" * 70)

    print(
        f"Diagnoses covered : "
        f"{len(diagnosis_ids & repair_diagnosis_ids)} / "
        f"{diagnosis_count}"
    )

    print(f"Repair count      : {len(repairs)}")

    if (
        len(repairs) == diagnosis_count
        and not missing_diagnoses
        and not extra_diagnoses
        and not invalid_repair_refs
    ):
        print("Coverage          : PASS")
        print("Status             : SUCCESS")
    else:
        print("Coverage          : FAIL")
        print("Status             : CHECK REQUIRED")

        if missing_diagnoses:
            print(
                "Missing diagnosis IDs:",
                sorted(missing_diagnoses)
            )

        if extra_diagnoses:
            print(
                "Extra diagnosis IDs:",
                sorted(extra_diagnoses)
            )

        if invalid_repair_refs:
            print(
                "Invalid repair IDs:",
                sorted(invalid_repair_refs)
            )

        raise SystemExit(1)

    print("=" * 70)