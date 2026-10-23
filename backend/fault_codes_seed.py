from app import app
from extensions import db
from models.symptom_code import SymptomCode
from models.fault_code import FaultCode


# ============================================================
# FAULT MASTER
#
# Every existing Symptom Code must receive fault mappings.
#
# 173 Symptoms
# Minimum 2 Faults per Symptom
# Target minimum Fault records = 346
#
# IMPORTANT:
# Faults are linked to the actual SymptomCode database record.
# No category/type/model is guessed here.
# ============================================================


FAULT_MAP = {

    # ========================================================
    # TELEVISION
    # ========================================================

    "SYM-TV-001": [
        "AC Input / Power Supply Failure",
        "SMPS or Main Board Power Circuit Failure",
    ],
    "SYM-TV-002": [
        "Standby LED Circuit Failure",
        "Main Board Standby Power Failure",
    ],
    "SYM-TV-003": [
        "Backlight System Failure",
        "Main Board Video Output Failure",
    ],
    "SYM-TV-004": [
        "T-Con / Display Signal Failure",
        "Panel Drive Circuit Failure",
    ],
    "SYM-TV-005": [
        "Video Processing Circuit Failure",
        "T-Con or Panel Signal Failure",
    ],
    "SYM-TV-006": [
        "Audio Amplifier Failure",
        "Speaker Circuit Failure",
    ],
    "SYM-TV-007": [
        "Audio Amplifier Distortion",
        "Speaker / Audio Processing Failure",
    ],
    "SYM-TV-008": [
        "LED Backlight Driver Instability",
        "Panel Signal Processing Failure",
    ],
    "SYM-TV-009": [
        "T-Con Signal Circuit Failure",
        "Panel Driver / COF Connection Failure",
    ],
    "SYM-TV-010": [
        "Panel Drive Circuit Failure",
        "T-Con Channel Failure",
    ],
    "SYM-TV-011": [
        "LED Backlight Failure",
        "Backlight Driver Circuit Failure",
    ],
    "SYM-TV-012": [
        "LED Backlight Strip Failure",
        "Backlight Driver Failure",
    ],
    "SYM-TV-013": [
        "Backlight LED Degradation",
        "Panel Power / Backlight Driver Failure",
    ],
    "SYM-TV-014": [
        "Backlight Driver Regulation Failure",
        "Picture Processing / Panel Control Failure",
    ],
    "SYM-TV-015": [
        "HDMI Port Hardware Failure",
        "HDMI Signal Processing Circuit Failure",
    ],
    "SYM-TV-016": [
        "USB Port Hardware Failure",
        "Main Board USB Controller Failure",
    ],
    "SYM-TV-017": [
        "Wi-Fi Module Failure",
        "Wireless Antenna / Network Circuit Failure",
    ],
    "SYM-TV-018": [
        "Bluetooth Module Failure",
        "Wireless Communication Circuit Failure",
    ],
    "SYM-TV-019": [
        "Remote Receiver Failure",
        "Remote Control Communication Failure",
    ],
    "SYM-TV-020": [
        "Keypad / Button Circuit Failure",
        "Main Board Input Circuit Failure",
    ],
    "SYM-TV-021": [
        "Power Supply Instability",
        "Main Board Software / Power Management Failure",
    ],
    "SYM-TV-022": [
        "Main Board Processing Failure",
        "System Memory / Software Failure",
    ],
    "SYM-TV-023": [
        "Smart TV Software Failure",
        "Network / Application Service Failure",
    ],
    "SYM-TV-024": [
        "Network Module Failure",
        "Wi-Fi Configuration / Communication Failure",
    ],
    "SYM-TV-025": [
        "Cooling / Ventilation Failure",
        "Power Supply or Main Board Overheating",
    ],
    "SYM-TV-026": [
        "LCD / LED Panel Physical Failure",
        "Panel Driver / COF Damage",
    ],
    "SYM-TV-027": [
        "Power Supply Component Overheating",
        "PCB / Electrical Component Failure",
    ],


    # ========================================================
    # AIR CONDITIONER
    # ========================================================

    "SYM-AC-001": [
        "AC Power Supply Failure",
        "Indoor PCB Power Circuit Failure",
    ],
    "SYM-AC-002": [
        "Refrigerant Charge Deficiency",
        "Compressor / Refrigeration Circuit Failure",
    ],
    "SYM-AC-003": [
        "Low Refrigerant Condition",
        "Evaporator / Condenser Heat Transfer Failure",
    ],
    "SYM-AC-004": [
        "Reversing Valve Failure",
        "Heating Control Circuit Failure",
    ],
    "SYM-AC-005": [
        "Condensate Drain Blockage",
        "Drain Pan / Drain Pipe Leakage",
    ],
    "SYM-AC-006": [
        "Indoor Drain Pipe Blockage",
        "Condensate Drain Pan Overflow",
    ],
    "SYM-AC-007": [
        "Outdoor PCB Failure",
        "Outdoor Fan / Compressor Circuit Failure",
    ],
    "SYM-AC-008": [
        "Compressor Start Circuit Failure",
        "Compressor Motor / Capacitor Failure",
    ],
    "SYM-AC-009": [
        "Compressor Mechanical Wear",
        "Compressor Mount / Vibration Failure",
    ],
    "SYM-AC-010": [
        "Outdoor Fan Motor Failure",
        "Fan Capacitor / Motor Control Failure",
    ],
    "SYM-AC-011": [
        "Indoor Blower Motor Failure",
        "Blower Motor Capacitor / Control Failure",
    ],
    "SYM-AC-012": [
        "Remote Control Failure",
        "Indoor Receiver Circuit Failure",
    ],
    "SYM-AC-013": [
        "Indoor Display Board Failure",
        "Main PCB Display Communication Failure",
    ],
    "SYM-AC-014": [
        "Sensor / Protection Fault",
        "Indoor or Outdoor PCB Fault",
    ],
    "SYM-AC-015": [
        "Evaporator / Drain Contamination",
        "Indoor Coil / Air Filter Contamination",
    ],
    "SYM-AC-016": [
        "Fan Motor Bearing Wear",
        "Compressor / Blower Mechanical Noise",
    ],
    "SYM-AC-017": [
        "Low Refrigerant / Low Pressure Condition",
        "Restricted Airflow / Evaporator Freeze",
    ],
    "SYM-AC-018": [
        "Compressor Efficiency Failure",
        "Refrigeration System / Electrical Load Fault",
    ],
    "SYM-AC-019": [
        "Power Supply Instability",
        "PCB / Control Software Failure",
    ],
    "SYM-AC-020": [
        "Temperature Sensor Failure",
        "Sensor Wiring / Control Circuit Failure",
    ],
    "SYM-AC-021": [
        "Indoor PCB Component Failure",
        "PCB Power Supply Circuit Failure",
    ],
    "SYM-AC-022": [
        "Refrigerant Circuit Leakage",
        "Pipe Joint / Flare Connection Leakage",
    ],


    # ========================================================
    # REFRIGERATOR
    # ========================================================

    "SYM-REF-001": [
        "AC Power Supply Failure",
        "Control PCB Power Circuit Failure",
    ],
    "SYM-REF-002": [
        "Compressor Failure",
        "Refrigeration System / Refrigerant Failure",
    ],
    "SYM-REF-003": [
        "Low Refrigerant Condition",
        "Compressor Cooling Efficiency Failure",
    ],
    "SYM-REF-004": [
        "Thermostat / Temperature Control Failure",
        "Temperature Sensor Control Failure",
    ],
    "SYM-REF-005": [
        "Evaporator Cooling Failure",
        "Refrigerant Circulation Failure",
    ],
    "SYM-REF-006": [
        "Defrost System Failure",
        "Evaporator Airflow Restriction",
    ],
    "SYM-REF-007": [
        "Drain Pipe Blockage",
        "Drain Tray / Water Outlet Leakage",
    ],
    "SYM-REF-008": [
        "Compressor Motor Failure",
        "Compressor Start Relay / Capacitor Failure",
    ],
    "SYM-REF-009": [
        "Compressor Mechanical Wear",
        "Compressor Mount / Vibration Failure",
    ],
    "SYM-REF-010": [
        "Evaporator Fan Motor Failure",
        "Fan Motor Control Circuit Failure",
    ],
    "SYM-REF-011": [
        "Door Lamp / LED Failure",
        "Door Switch Failure",
    ],
    "SYM-REF-012": [
        "Door Hinge Alignment Failure",
        "Door Gasket / Seal Deformation",
    ],
    "SYM-REF-013": [
        "Door Gasket Damage",
        "Door Seal Magnetic Failure",
    ],
    "SYM-REF-014": [
        "Drain / Interior Contamination",
        "Food / Moisture Related Odor Source",
    ],
    "SYM-REF-015": [
        "Display Board Failure",
        "Main PCB Display Communication Failure",
    ],
    "SYM-REF-016": [
        "Temperature / System Sensor Fault",
        "Control PCB Fault",
    ],
    "SYM-REF-017": [
        "Temperature Sensor Failure",
        "Thermostat / Control System Failure",
    ],
    "SYM-REF-018": [
        "Compressor Overload / Inefficiency",
        "Electrical Control Component Failure",
    ],
    "SYM-REF-019": [
        "Power Supply Instability",
        "Control PCB Reset / Software Failure",
    ],
    "SYM-REF-020": [
        "Compressor Mount Vibration",
        "Fan Motor / Mechanical Component Wear",
    ],


    # ========================================================
    # WASHING MACHINE
    # ========================================================

    "SYM-WM-001": [
        "AC Input / Power Supply Failure",
        "Main PCB Power Circuit Failure",
    ],
    "SYM-WM-002": [
        "Door / Lid Lock Interlock Failure",
        "Main PCB Start Control Failure",
    ],
    "SYM-WM-003": [
        "Water Inlet Valve Failure",
        "Water Supply / Inlet Filter Restriction",
    ],
    "SYM-WM-004": [
        "Drain Pump Failure",
        "Drain Hose / Filter Blockage",
    ],
    "SYM-WM-005": [
        "Drive Motor Failure",
        "Drive Belt / Coupling Failure",
    ],
    "SYM-WM-006": [
        "Tub Suspension / Shock Absorber Failure",
        "Unbalanced Drum / Mechanical Alignment Fault",
    ],
    "SYM-WM-007": [
        "Drum Bearing Wear",
        "Motor / Drive Assembly Mechanical Fault",
    ],
    "SYM-WM-008": [
        "Drain / Inlet Hose Leakage",
        "Tub Seal / Water Seal Failure",
    ],
    "SYM-WM-009": [
        "Door Lock Assembly Failure",
        "Door Interlock Sensor Failure",
    ],
    "SYM-WM-010": [
        "Door Lock Mechanism Jam",
        "Door Interlock Solenoid Failure",
    ],
    "SYM-WM-011": [
        "Motor / Drive Control Failure",
        "Drive Belt / Coupling Failure",
    ],
    "SYM-WM-012": [
        "Main PCB Program Control Failure",
        "Motor / Water Valve Control Failure",
    ],
    "SYM-WM-013": [
        "Display Module Failure",
        "Main PCB Display Communication Failure",
    ],
    "SYM-WM-014": [
        "Sensor / Actuator Fault",
        "Main PCB Control Fault",
    ],
    "SYM-WM-015": [
        "Detergent Dispenser Blockage",
        "Water Inlet Distribution Failure",
    ],
    "SYM-WM-016": [
        "Wash Motor Performance Failure",
        "Water / Detergent Circulation Failure",
    ],
    "SYM-WM-017": [
        "Motor Speed Control Failure",
        "Drive Belt / Mechanical Transmission Failure",
    ],
    "SYM-WM-018": [
        "Motor Bearing / Rotor Wear",
        "Motor Mount / Drive Assembly Failure",
    ],
    "SYM-WM-019": [
        "Main PCB Power Instability",
        "Motor / Control Circuit Protection Fault",
    ],
    "SYM-WM-020": [
        "Tub / Drain Contamination",
        "Detergent / Moisture Residue Accumulation",
    ],


    # ========================================================
    # MICROWAVE
    # ========================================================

    "SYM-MW-001": [
        "AC Power Supply Failure",
        "Main PCB / Fuse Protection Failure",
    ],
    "SYM-MW-002": [
        "Magnetron Failure",
        "High Voltage Diode / Capacitor Circuit Failure",
    ],
    "SYM-MW-003": [
        "Magnetron Reduced Output",
        "High Voltage Power Circuit Failure",
    ],
    "SYM-MW-004": [
        "Turntable Motor Failure",
        "Turntable Drive Coupling Failure",
    ],
    "SYM-MW-005": [
        "Display Module Failure",
        "Main PCB Display Circuit Failure",
    ],
    "SYM-MW-006": [
        "Keypad Membrane Failure",
        "Control PCB Input Circuit Failure",
    ],
    "SYM-MW-007": [
        "Door Latch Mechanism Failure",
        "Door Interlock Switch Failure",
    ],
    "SYM-MW-008": [
        "Door Latch Mechanism Jam",
        "Door Hinge / Interlock Assembly Failure",
    ],
    "SYM-MW-009": [
        "Waveguide / Cavity Damage",
        "High Voltage / Magnetron Arcing",
    ],
    "SYM-MW-010": [
        "Cooling Fan Motor Failure",
        "Turntable / Magnetron Mechanical Noise",
    ],
    "SYM-MW-011": [
        "Electrical Component Overheating",
        "Magnetron / High Voltage Circuit Failure",
    ],
    "SYM-MW-012": [
        "Cavity Lamp Failure",
        "Lamp Control Circuit Failure",
    ],
    "SYM-MW-013": [
        "Cooling Fan Motor Failure",
        "Fan Control Circuit Failure",
    ],
    "SYM-MW-014": [
        "Control PCB Power Instability",
        "Door / Power Protection Circuit Fault",
    ],
    "SYM-MW-015": [
        "Sensor / Protection Circuit Fault",
        "Main Control PCB Fault",
    ],


    # ========================================================
    # GEYSER
    # ========================================================

    "SYM-GEY-001": [
        "AC Power Supply Failure",
        "Geyser PCB / Electrical Control Failure",
    ],
    "SYM-GEY-002": [
        "Heating Element Failure",
        "Thermostat / Heating Control Failure",
    ],
    "SYM-GEY-003": [
        "Heating Element Scaling / Degradation",
        "Low Heating Power / Thermostat Fault",
    ],
    "SYM-GEY-004": [
        "Thermostat Control Failure",
        "Temperature Sensor / Cutoff Failure",
    ],
    "SYM-GEY-005": [
        "Water Inlet / Outlet Joint Leakage",
        "Tank / Internal Seal Leakage",
    ],
    "SYM-GEY-006": [
        "Inner Tank Corrosion / Leakage",
        "Tank Seal / Flange Leakage",
    ],
    "SYM-GEY-007": [
        "Indicator Lamp / LED Failure",
        "Control PCB Indicator Circuit Failure",
    ],
    "SYM-GEY-008": [
        "Thermostat Sensor Failure",
        "Temperature Control Circuit Failure",
    ],
    "SYM-GEY-009": [
        "Heating Element Open Circuit",
        "Heating Element Scaling / Burnout",
    ],
    "SYM-GEY-010": [
        "Heating Element / Tank Scale Noise",
        "Internal Mechanical / Pressure Noise",
    ],
    "SYM-GEY-011": [
        "Heating Element Electrical Failure",
        "Internal Wiring / Component Overheating",
    ],
    "SYM-GEY-012": [
        "Display Module Failure",
        "Control PCB Display Circuit Failure",
    ],
    "SYM-GEY-013": [
        "Temperature / Safety Sensor Fault",
        "Control PCB Fault",
    ],
    "SYM-GEY-014": [
        "Heating Element Inefficiency",
        "Thermostat / Power Control Failure",
    ],
    "SYM-GEY-015": [
        "Thermal Cut-Off Failure",
        "Safety Thermostat / Protection Circuit Failure",
    ],


    # ========================================================
    # LAPTOP
    # ========================================================

    "SYM-LAP-001": [
        "DC Power Input Failure",
        "Motherboard Power Circuit Failure",
    ],
    "SYM-LAP-002": [
        "DC Jack / Charging Port Failure",
        "Charging IC / Adapter Circuit Failure",
    ],
    "SYM-LAP-003": [
        "Battery Cell Degradation",
        "Battery Management Circuit Failure",
    ],
    "SYM-LAP-004": [
        "Battery Communication Failure",
        "Battery Connector / Detection Circuit Failure",
    ],
    "SYM-LAP-005": [
        "LCD / Display Panel Failure",
        "Display Cable / Graphics Circuit Failure",
    ],
    "SYM-LAP-006": [
        "LCD Panel Signal Failure",
        "Display Cable / Graphics Circuit Failure",
    ],
    "SYM-LAP-007": [
        "Keyboard Matrix Failure",
        "Keyboard Connector / Controller Failure",
    ],
    "SYM-LAP-008": [
        "Touchpad Hardware Failure",
        "Touchpad Controller / Connector Failure",
    ],
    "SYM-LAP-009": [
        "Wi-Fi Module Failure",
        "Wireless Antenna / Driver Communication Failure",
    ],
    "SYM-LAP-010": [
        "Bluetooth Module Failure",
        "Wireless Driver / Controller Failure",
    ],
    "SYM-LAP-011": [
        "USB Port Hardware Failure",
        "USB Controller / Power Circuit Failure",
    ],
    "SYM-LAP-012": [
        "HDMI Port Hardware Failure",
        "Display Output / Graphics Circuit Failure",
    ],
    "SYM-LAP-013": [
        "Camera Module Failure",
        "Camera Connector / Controller Failure",
    ],
    "SYM-LAP-014": [
        "Microphone Module Failure",
        "Audio Codec / Microphone Circuit Failure",
    ],
    "SYM-LAP-015": [
        "Speaker Module Failure",
        "Audio Amplifier / Codec Failure",
    ],
    "SYM-LAP-016": [
        "Cooling Fan Failure",
        "Thermal Paste / Heat Sink Performance Failure",
    ],
    "SYM-LAP-017": [
        "Cooling Fan Bearing Wear",
        "Fan Motor / Fan Control Failure",
    ],
    "SYM-LAP-018": [
        "CPU / Thermal Throttling",
        "Storage / Memory Performance Failure",
    ],
    "SYM-LAP-019": [
        "RAM / Memory Failure",
        "Operating System / Storage Failure",
    ],
    "SYM-LAP-020": [
        "Power Management Failure",
        "Motherboard / Operating System Failure",
    ],
    "SYM-LAP-021": [
        "Operating System Corruption",
        "Storage Drive / Boot System Failure",
    ],
    "SYM-LAP-022": [
        "Keyboard Key Switch Failure",
        "Keycap / Keyboard Mechanism Damage",
    ],
    "SYM-LAP-023": [
        "Chassis / Housing Physical Damage",
        "Hinge / Structural Assembly Failure",
    ],
    "SYM-LAP-024": [
        "Liquid-Induced Board Damage",
        "Keyboard / Connector Liquid Damage",
    ],


    # ========================================================
    # MOBILE
    # ========================================================

    "SYM-MOB-001": [
        "Battery / Power Circuit Failure",
        "Motherboard Power Management Failure",
    ],
    "SYM-MOB-002": [
        "Charging Port Failure",
        "Charging IC / Battery Charging Circuit Failure",
    ],
    "SYM-MOB-003": [
        "Battery Cell Degradation",
        "Power Management IC / Background Power Fault",
    ],
    "SYM-MOB-004": [
        "Battery Cell Swelling / Internal Failure",
        "Battery Charging / Thermal Management Failure",
    ],
    "SYM-MOB-005": [
        "Display Panel Failure",
        "Display Connector / Power Circuit Failure",
    ],
    "SYM-MOB-006": [
        "Display Panel Signal Failure",
        "Display Connector / Graphics Circuit Failure",
    ],
    "SYM-MOB-007": [
        "Touch Digitizer Failure",
        "Touch Controller / Display Assembly Failure",
    ],
    "SYM-MOB-008": [
        "Display Panel Physical Failure",
        "Display Assembly / Connector Damage",
    ],
    "SYM-MOB-009": [
        "Camera Module Failure",
        "Camera Connector / Camera IC Failure",
    ],
    "SYM-MOB-010": [
        "Front Camera Module Failure",
        "Front Camera Connector / Control Circuit Failure",
    ],
    "SYM-MOB-011": [
        "Rear Camera Module Failure",
        "Rear Camera Connector / Camera IC Failure",
    ],
    "SYM-MOB-012": [
        "Speaker Module Failure",
        "Audio Amplifier / Audio Codec Failure",
    ],
    "SYM-MOB-013": [
        "Microphone Module Failure",
        "Audio Codec / Microphone Circuit Failure",
    ],
    "SYM-MOB-014": [
        "Earpiece Speaker Failure",
        "Audio Amplifier / Connector Failure",
    ],
    "SYM-MOB-015": [
        "SIM Reader Hardware Failure",
        "SIM Detection / Baseband Circuit Failure",
    ],
    "SYM-MOB-016": [
        "Baseband / RF Circuit Failure",
        "SIM / Network Antenna Circuit Failure",
    ],
    "SYM-MOB-017": [
        "Wi-Fi Module Failure",
        "Wi-Fi Antenna / RF Circuit Failure",
    ],
    "SYM-MOB-018": [
        "Bluetooth Module / RF Failure",
        "Wireless Controller / Antenna Failure",
    ],
    "SYM-MOB-019": [
        "GPS Receiver Failure",
        "GNSS Antenna / RF Circuit Failure",
    ],
    "SYM-MOB-020": [
        "Fingerprint Sensor Failure",
        "Fingerprint Sensor Connector / Controller Failure",
    ],
    "SYM-MOB-021": [
        "Face Recognition Camera Failure",
        "Biometric Sensor / Software Control Failure",
    ],
    "SYM-MOB-022": [
        "Thermal Management Failure",
        "Battery / Processor Overheating",
    ],
    "SYM-MOB-023": [
        "Power Management Failure",
        "Motherboard / Software Stability Failure",
    ],
    "SYM-MOB-024": [
        "RAM / Storage Performance Failure",
        "Operating System / Application System Failure",
    ],
    "SYM-MOB-025": [
        "Application / Operating System Failure",
        "Storage / Memory Resource Failure",
    ],
    "SYM-MOB-026": [
        "USB / Charging Port Hardware Failure",
        "Charging / USB Controller Failure",
    ],
    "SYM-MOB-027": [
        "Vibration Motor Failure",
        "Vibration Driver Circuit Failure",
    ],
    "SYM-MOB-028": [
        "Power Button Switch Failure",
        "Power Key Flex / Control Circuit Failure",
    ],
    "SYM-MOB-029": [
        "Volume Button Switch Failure",
        "Volume Key Flex / Control Circuit Failure",
    ],
    "SYM-MOB-030": [
        "Housing / Chassis Physical Damage",
        "Internal Component / Connector Damage",
    ],
}


# ============================================================
# VALIDATE COVERAGE BEFORE INSERT
# ============================================================

def validate_fault_map():
    expected = set(
        db.session.scalars(
            db.select(SymptomCode.symptom_code)
            .order_by(SymptomCode.symptom_code)
        ).all()
    )

    mapped = set(FAULT_MAP.keys())

    missing = expected - mapped
    extra = mapped - expected

    print()
    print("=" * 65)
    print("FAULT COVERAGE VALIDATION")
    print("=" * 65)
    print(f"Symptoms in database : {len(expected)}")
    print(f"Symptoms in mapping  : {len(mapped)}")
    print(f"Missing mappings     : {len(missing)}")
    print(f"Extra mappings       : {len(extra)}")
    print("=" * 65)

    if missing:
        print("\nMISSING SYMPTOM MAPPINGS:")
        for code in sorted(missing):
            print(" -", code)

    if extra:
        print("\nEXTRA / UNKNOWN MAPPINGS:")
        for code in sorted(extra):
            print(" -", code)

    if missing or extra:
        raise RuntimeError(
            "FAULT COVERAGE CHECK FAILED. "
            "No fault records were inserted."
        )

    # Every symptom must have at least 2 faults.
    insufficient = {
        code: faults
        for code, faults in FAULT_MAP.items()
        if len(faults) < 2
    }

    if insufficient:
        print("\nINSUFFICIENT FAULT MAPPINGS:")
        for code, faults in insufficient.items():
            print(code, "=>", len(faults))

        raise RuntimeError(
            "Some symptoms have fewer than 2 fault mappings."
        )

    total_fault_definitions = sum(
        len(faults)
        for faults in FAULT_MAP.values()
    )

    print(f"Fault definitions    : {total_fault_definitions}")
    print("Coverage status      : PASS")
    print("=" * 65)


# ============================================================
# SEED FAULTS
# ============================================================

def seed_faults():

    with app.app_context():

        # ----------------------------------------------------
        # First validate everything.
        # Nothing is inserted if validation fails.
        # ----------------------------------------------------
        validate_fault_map()

        created = 0
        skipped = 0

        # ----------------------------------------------------
        # Create fault records
        # ----------------------------------------------------
        for symptom_code, fault_names in FAULT_MAP.items():

            symptom = db.session.scalar(
                db.select(SymptomCode).where(
                    SymptomCode.symptom_code == symptom_code
                )
            )

            if not symptom:
                raise RuntimeError(
                    f"Symptom not found in database: {symptom_code}"
                )

            for fault_index, fault_name in enumerate(
                fault_names,
                start=1
            ):

                # Stable unique fault code
                fault_code = (
                    f"FLT-{symptom_code.replace('SYM-', '')}"
                    f"-{fault_index:02d}"
                )

                existing = db.session.scalar(
                    db.select(FaultCode).where(
                        FaultCode.fault_code == fault_code
                    )
                )

                if existing:
                    skipped += 1
                    continue

                fault = FaultCode(
                    fault_code=fault_code,
                    fault_name=fault_name,
                    description=(
                        f"Possible technical fault associated "
                        f"with symptom {symptom.symptom_code}: "
                        f"{symptom.symptom_name}"
                    ),
                    category_id=symptom.category_id,
                    product_type_id=symptom.product_type_id,
                    product_model_id=symptom.product_model_id,
                    symptom_id=symptom.id,
                    status="Active",
                )

                db.session.add(fault)
                created += 1

        db.session.commit()

        # ----------------------------------------------------
        # Final database verification
        # ----------------------------------------------------
        total_faults = db.session.scalar(
            db.select(db.func.count(FaultCode.id))
        )

        print()
        print("=" * 65)
        print("FAULT MASTER SEED COMPLETED")
        print("=" * 65)
        print(f"Symptoms covered    : {len(FAULT_MAP)}")
        print(f"Fault definitions   : {sum(len(v) for v in FAULT_MAP.values())}")
        print(f"Created             : {created}")
        print(f"Skipped             : {skipped}")
        print(f"Faults in database  : {total_faults}")
        print("=" * 65)


if __name__ == "__main__":
    seed_faults()