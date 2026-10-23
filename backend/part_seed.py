from app import app
from extensions import db
from models.part import Part
from models.product_category import ProductCategory
from models.product_type import ProductType


PART_TEMPLATES = {
    "TV": [
        ("PWR-SMPS", "SMPS / Power Supply Board"),
        ("PWR-MAIN", "Main Power Board"),
        ("MB-TV", "TV Main Board"),
        ("TCON-TV", "T-Con Board"),
        ("BL-TV", "LED Backlight Strip"),
        ("DRV-BL-TV", "Backlight Driver Board"),
        ("PANEL-TV", "Display Panel Assembly"),
        ("SPK-TV", "TV Speaker Assembly"),
        ("IR-TV", "IR Receiver Module"),
        ("WIFI-TV", "Wi-Fi Module"),
        ("BT-TV", "Bluetooth Module"),
        ("REM-TV", "Remote Control"),
        ("KEY-TV", "Keypad / Control Switch Board"),
        ("LVDS-TV", "LVDS Cable"),
        ("ANT-TV", "TV Antenna Module"),
    ],

    "AC": [
        ("COMP-AC", "AC Compressor"),
        ("COND-AC", "Condenser Coil"),
        ("EVAP-AC", "Evaporator Coil"),
        ("FAN-AC", "Indoor / Outdoor Fan Motor"),
        ("PCB-AC", "AC Control PCB"),
        ("SMPS-AC", "AC Power Supply Board"),
        ("CAP-AC", "AC Capacitor"),
        ("SENS-AC", "Temperature Sensor"),
        ("REM-AC", "AC Remote Control"),
        ("VALVE-AC", "Expansion Valve"),
        ("DRAIN-AC", "Drain Pump / Drain Assembly"),
        ("SW-AC", "AC Control Switch"),
    ],

    "REF": [
        ("COMP-REF", "Refrigerator Compressor"),
        ("COND-REF", "Condenser Coil"),
        ("EVAP-REF", "Evaporator Coil"),
        ("FAN-REF", "Refrigerator Fan Motor"),
        ("PCB-REF", "Refrigerator Control PCB"),
        ("SENS-REF", "Temperature Sensor"),
        ("THERM-REF", "Thermostat"),
        ("RELAY-REF", "Compressor Relay"),
        ("CAP-REF", "Compressor Capacitor"),
        ("VALVE-REF", "Water / Gas Valve Assembly"),
        ("DOOR-REF", "Door Assembly"),
        ("GASKET-REF", "Door Gasket"),
    ],

    "WM": [
        ("MOTOR-WM", "Washing Machine Motor"),
        ("PCB-WM", "Washing Machine Control PCB"),
        ("PUMP-WM", "Drain Pump"),
        ("VALVE-WM", "Water Inlet Valve"),
        ("SENS-WM", "Water Level Sensor"),
        ("DOOR-WM", "Door Lock Assembly"),
        ("BELT-WM", "Drive Belt"),
        ("DRUM-WM", "Drum Assembly"),
        ("CAP-WM", "Motor Capacitor"),
        ("PANEL-WM", "Control Panel"),
        ("HOSE-WM", "Drain / Inlet Hose"),
    ],

    "MW": [
        ("MAG-MW", "Magnetron"),
        ("HV-MW", "High Voltage Transformer"),
        ("CAP-MW", "High Voltage Capacitor"),
        ("DIODE-MW", "High Voltage Diode"),
        ("PCB-MW", "Microwave Control PCB"),
        ("MOTOR-MW", "Turntable Motor"),
        ("FAN-MW", "Cooling Fan Motor"),
        ("DOOR-MW", "Door Assembly"),
        ("SW-MW", "Door Interlock Switch"),
        ("LAMP-MW", "Microwave Lamp"),
        ("FUSE-MW", "Microwave Fuse"),
    ],

    "GEY": [
        ("HEAT-GEY", "Heating Element"),
        ("THERM-GEY", "Thermostat"),
        ("PCB-GEY", "Geyser Control PCB"),
        ("SENS-GEY", "Temperature Sensor"),
        ("VALVE-GEY", "Water Inlet Valve"),
        ("TANK-GEY", "Storage Tank Assembly"),
        ("ANODE-GEY", "Anode Rod"),
        ("CAP-GEY", "Capacitor"),
        ("FUSE-GEY", "Thermal Fuse"),
        ("IND-GEY", "Geyser Indicator"),
    ],

    "LAP": [
        ("MB-LAP", "Laptop Motherboard"),
        ("BAT-LAP", "Laptop Battery"),
        ("CHG-LAP", "Laptop Charging Port"),
        ("ADP-LAP", "Laptop Power Adapter"),
        ("RAM-LAP", "Laptop RAM Module"),
        ("SSD-LAP", "SSD Storage Drive"),
        ("FAN-LAP", "Laptop Cooling Fan"),
        ("KB-LAP", "Laptop Keyboard"),
        ("LCD-LAP", "Laptop Display Assembly"),
        ("CAM-LAP", "Laptop Camera Module"),
        ("SPK-LAP", "Laptop Speaker"),
        ("WIFI-LAP", "Laptop Wi-Fi Module"),
    ],

    "MOB": [
        ("BAT-MOB", "Mobile Battery"),
        ("LCD-MOB", "Mobile Display Assembly"),
        ("MB-MOB", "Mobile Main Board"),
        ("CHG-MOB", "Charging Port"),
        ("CAM-MOB", "Camera Module"),
        ("SPK-MOB", "Speaker Module"),
        ("MIC-MOB", "Microphone Module"),
        ("VIB-MOB", "Vibration Motor"),
        ("WIFI-MOB", "Wi-Fi Module"),
        ("BT-MOB", "Bluetooth Module"),
        ("ANT-MOB", "Mobile Antenna"),
        ("FLEX-MOB", "Flex Cable Assembly"),
    ],
}


with app.app_context():

    categories = {
        category.category_code: category
        for category in ProductCategory.query.all()
    }

    product_types = ProductType.query.all()

    print("=" * 70)
    print("PART MASTER SEED")
    print("=" * 70)

    created = 0
    skipped = 0
    invalid_categories = []

    for category_code, templates in PART_TEMPLATES.items():

        category = categories.get(category_code)

        if not category:
            invalid_categories.append(category_code)
            continue

        category_types = [
            product_type
            for product_type in product_types
            if product_type.category_id == category.id
        ]

        for part_suffix, part_name in templates:

            # Create a category-level master part.
            part_code = part_suffix

            existing = Part.query.filter_by(
                part_code=part_code
            ).first()

            if existing:
                skipped += 1
                continue

            part = Part(
                part_code=part_code,
                part_name=part_name,
                description=(
                    f"{part_name} spare part for "
                    f"{category.category_name} products."
                ),
                brand_id=None,
                category_id=category.id,
                product_type_id=None,
                status="Active"
            )

            db.session.add(part)
            created += 1

    db.session.commit()

    parts = Part.query.all()

    category_ids = {
        category.id
        for category in categories.values()
    }

    invalid_parts = []

    for part in parts:

        if part.category_id not in category_ids:
            invalid_parts.append(part.id)

        if part.product_type_id is not None:
            product_type = db.session.get(
                ProductType,
                part.product_type_id
            )

            if not product_type:
                invalid_parts.append(part.id)

            elif product_type.category_id != part.category_id:
                invalid_parts.append(part.id)

    print()
    print("=" * 70)
    print("PART MASTER RESULT")
    print("=" * 70)

    print(f"Categories expected : {len(PART_TEMPLATES)}")
    print(f"Parts created       : {created}")
    print(f"Parts skipped       : {skipped}")
    print(f"Parts in database   : {len(parts)}")
    print(f"Invalid part refs   : {len(invalid_parts)}")

    print()
    print("=" * 70)
    print("CATEGORY COVERAGE")
    print("=" * 70)

    for category_code, templates in PART_TEMPLATES.items():

        category = categories.get(category_code)

        if not category:
            print(
                f"{category_code:<8} : MISSING CATEGORY"
            )
            continue

        count = Part.query.filter_by(
            category_id=category.id
        ).count()

        print(
            f"{category_code:<8} : "
            f"{count:>3} parts"
        )

    print()
    print("=" * 70)
    print("FINAL VALIDATION")
    print("=" * 70)

    if invalid_categories:
        print(
            "Missing categories:",
            invalid_categories
        )

    if invalid_parts:
        print(
            "Invalid part IDs:",
            sorted(set(invalid_parts))
        )

    if invalid_categories or invalid_parts:
        print("Coverage : FAIL")
        raise SystemExit(1)

    print("Coverage : PASS")
    print("Status   : SUCCESS")
    print("=" * 70)