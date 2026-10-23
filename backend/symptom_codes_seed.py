from app import app
from extensions import db
from models.product_category import ProductCategory
from models.product_type import ProductType
from models.symptom_code import SymptomCode


# ============================================================
# COMPREHENSIVE SYMPTOM MASTER
# 8 PRODUCT CATEGORIES
# Total records intended: 173
# ============================================================

SYMPTOMS = [

    # ========================================================
    # TELEVISION - 27
    # ========================================================
    ("TV", "LED-TV", "SYM-TV-001", "TV Not Powering ON"),
    ("TV", "LED-TV", "SYM-TV-002", "TV Power Light Not Working"),
    ("TV", "LED-TV", "SYM-TV-003", "TV Screen Blank"),
    ("TV", "LED-TV", "SYM-TV-004", "TV No Display"),
    ("TV", "LED-TV", "SYM-TV-005", "TV No Picture"),
    ("TV", "LED-TV", "SYM-TV-006", "TV No Sound"),
    ("TV", "LED-TV", "SYM-TV-007", "TV Sound Distorted"),
    ("TV", "LED-TV", "SYM-TV-008", "TV Screen Flickering"),
    ("TV", "LED-TV", "SYM-TV-009", "TV Screen Lines Appearing"),
    ("TV", "LED-TV", "SYM-TV-010", "TV Half Screen Display"),
    ("TV", "LED-TV", "SYM-TV-011", "TV Screen Dark"),
    ("TV", "LED-TV", "SYM-TV-012", "TV Backlight Not Working"),
    ("TV", "LED-TV", "SYM-TV-013", "TV Picture Too Dark"),
    ("TV", "LED-TV", "SYM-TV-014", "TV Picture Too Bright"),
    ("TV", "LED-TV", "SYM-TV-015", "TV HDMI Not Working"),
    ("TV", "LED-TV", "SYM-TV-016", "TV USB Port Not Working"),
    ("TV", "LED-TV", "SYM-TV-017", "TV WiFi Not Connecting"),
    ("TV", "LED-TV", "SYM-TV-018", "TV Bluetooth Not Working"),
    ("TV", "LED-TV", "SYM-TV-019", "TV Remote Not Working"),
    ("TV", "LED-TV", "SYM-TV-020", "TV Buttons Not Working"),
    ("TV", "LED-TV", "SYM-TV-021", "TV Auto Restarting"),
    ("TV", "LED-TV", "SYM-TV-022", "TV Hanging or Freezing"),
    ("TV", "LED-TV", "SYM-TV-023", "TV Apps Not Opening"),
    ("TV", "LED-TV", "SYM-TV-024", "TV Network Disconnected"),
    ("TV", "LED-TV", "SYM-TV-025", "TV Overheating"),
    ("TV", "LED-TV", "SYM-TV-026", "TV Panel Damaged"),
    ("TV", "LED-TV", "SYM-TV-027", "TV Burning Smell"),

    # ========================================================
    # AIR CONDITIONER - 22
    # ========================================================
    ("AC", "SPLIT-AC", "SYM-AC-001", "AC Not Powering ON"),
    ("AC", "SPLIT-AC", "SYM-AC-002", "AC Not Cooling"),
    ("AC", "SPLIT-AC", "SYM-AC-003", "AC Low Cooling"),
    ("AC", "SPLIT-AC", "SYM-AC-004", "AC Not Heating"),
    ("AC", "SPLIT-AC", "SYM-AC-005", "AC Water Leakage"),
    ("AC", "SPLIT-AC", "SYM-AC-006", "AC Indoor Unit Water Leakage"),
    ("AC", "SPLIT-AC", "SYM-AC-007", "AC Outdoor Unit Not Working"),
    ("AC", "SPLIT-AC", "SYM-AC-008", "AC Compressor Not Starting"),
    ("AC", "SPLIT-AC", "SYM-AC-009", "AC Compressor Noise"),
    ("AC", "SPLIT-AC", "SYM-AC-010", "AC Fan Not Working"),
    ("AC", "SPLIT-AC", "SYM-AC-011", "AC Blower Not Working"),
    ("AC", "SPLIT-AC", "SYM-AC-012", "AC Remote Not Working"),
    ("AC", "SPLIT-AC", "SYM-AC-013", "AC Display Not Working"),
    ("AC", "SPLIT-AC", "SYM-AC-014", "AC Error Code Displayed"),
    ("AC", "SPLIT-AC", "SYM-AC-015", "AC Bad Smell"),
    ("AC", "SPLIT-AC", "SYM-AC-016", "AC Abnormal Noise"),
    ("AC", "SPLIT-AC", "SYM-AC-017", "AC Ice Formation"),
    ("AC", "SPLIT-AC", "SYM-AC-018", "AC Excessive Power Consumption"),
    ("AC", "SPLIT-AC", "SYM-AC-019", "AC Auto Restarting"),
    ("AC", "SPLIT-AC", "SYM-AC-020", "AC Sensor Not Working"),
    ("AC", "SPLIT-AC", "SYM-AC-021", "AC PCB Not Working"),
    ("AC", "SPLIT-AC", "SYM-AC-022", "AC Gas Leakage Suspected"),

    # ========================================================
    # REFRIGERATOR - 20
    # ========================================================
    ("REF", "SINGLE-DOOR-REF", "SYM-REF-001", "Refrigerator Not Powering ON"),
    ("REF", "SINGLE-DOOR-REF", "SYM-REF-002", "Refrigerator Not Cooling"),
    ("REF", "SINGLE-DOOR-REF", "SYM-REF-003", "Refrigerator Low Cooling"),
    ("REF", "SINGLE-DOOR-REF", "SYM-REF-004", "Refrigerator Excessive Cooling"),
    ("REF", "SINGLE-DOOR-REF", "SYM-REF-005", "Freezer Not Cooling"),
    ("REF", "SINGLE-DOOR-REF", "SYM-REF-006", "Ice Formation Excessive"),
    ("REF", "SINGLE-DOOR-REF", "SYM-REF-007", "Water Leakage"),
    ("REF", "SINGLE-DOOR-REF", "SYM-REF-008", "Compressor Not Working"),
    ("REF", "SINGLE-DOOR-REF", "SYM-REF-009", "Compressor Noise"),
    ("REF", "SINGLE-DOOR-REF", "SYM-REF-010", "Fan Not Working"),
    ("REF", "SINGLE-DOOR-REF", "SYM-REF-011", "Refrigerator Light Not Working"),
    ("REF", "SINGLE-DOOR-REF", "SYM-REF-012", "Door Not Closing Properly"),
    ("REF", "SINGLE-DOOR-REF", "SYM-REF-013", "Door Seal Damaged"),
    ("REF", "SINGLE-DOOR-REF", "SYM-REF-014", "Bad Smell"),
    ("REF", "SINGLE-DOOR-REF", "SYM-REF-015", "Display Not Working"),
    ("REF", "SINGLE-DOOR-REF", "SYM-REF-016", "Error Code Displayed"),
    ("REF", "SINGLE-DOOR-REF", "SYM-REF-017", "Temperature Not Maintaining"),
    ("REF", "SINGLE-DOOR-REF", "SYM-REF-018", "Excessive Power Consumption"),
    ("REF", "SINGLE-DOOR-REF", "SYM-REF-019", "Auto Restarting"),
    ("REF", "SINGLE-DOOR-REF", "SYM-REF-020", "Abnormal Vibration"),

    # ========================================================
    # WASHING MACHINE - 20
    # ========================================================
    ("WM", "TOPLOAD-WM", "SYM-WM-001", "Washing Machine Not Powering ON"),
    ("WM", "TOPLOAD-WM", "SYM-WM-002", "Washing Machine Not Starting"),
    ("WM", "TOPLOAD-WM", "SYM-WM-003", "Washing Machine Not Filling Water"),
    ("WM", "TOPLOAD-WM", "SYM-WM-004", "Washing Machine Water Not Draining"),
    ("WM", "TOPLOAD-WM", "SYM-WM-005", "Washing Machine Drum Not Rotating"),
    ("WM", "TOPLOAD-WM", "SYM-WM-006", "Washing Machine Excessive Vibration"),
    ("WM", "TOPLOAD-WM", "SYM-WM-007", "Washing Machine Excessive Noise"),
    ("WM", "TOPLOAD-WM", "SYM-WM-008", "Washing Machine Water Leakage"),
    ("WM", "TOPLOAD-WM", "SYM-WM-009", "Washing Machine Door Not Locking"),
    ("WM", "TOPLOAD-WM", "SYM-WM-010", "Washing Machine Door Not Opening"),
    ("WM", "TOPLOAD-WM", "SYM-WM-011", "Washing Machine Spin Not Working"),
    ("WM", "TOPLOAD-WM", "SYM-WM-012", "Washing Machine Wash Cycle Not Working"),
    ("WM", "TOPLOAD-WM", "SYM-WM-013", "Washing Machine Display Not Working"),
    ("WM", "TOPLOAD-WM", "SYM-WM-014", "Washing Machine Error Code Displayed"),
    ("WM", "TOPLOAD-WM", "SYM-WM-015", "Washing Machine Detergent Not Dispensing"),
    ("WM", "TOPLOAD-WM", "SYM-WM-016", "Washing Machine Clothes Not Clean"),
    ("WM", "TOPLOAD-WM", "SYM-WM-017", "Washing Machine Spin Cycle Too Slow"),
    ("WM", "TOPLOAD-WM", "SYM-WM-018", "Washing Machine Motor Noise"),
    ("WM", "TOPLOAD-WM", "SYM-WM-019", "Washing Machine Auto Restarting"),
    ("WM", "TOPLOAD-WM", "SYM-WM-020", "Washing Machine Bad Smell"),

    # ========================================================
    # MICROWAVE - 15
    # ========================================================
    ("MW", "SOLO-MW", "SYM-MW-001", "Microwave Not Powering ON"),
    ("MW", "SOLO-MW", "SYM-MW-002", "Microwave Not Heating"),
    ("MW", "SOLO-MW", "SYM-MW-003", "Microwave Low Heating"),
    ("MW", "SOLO-MW", "SYM-MW-004", "Microwave Turntable Not Rotating"),
    ("MW", "SOLO-MW", "SYM-MW-005", "Microwave Display Not Working"),
    ("MW", "SOLO-MW", "SYM-MW-006", "Microwave Buttons Not Working"),
    ("MW", "SOLO-MW", "SYM-MW-007", "Microwave Door Not Closing"),
    ("MW", "SOLO-MW", "SYM-MW-008", "Microwave Door Not Opening"),
    ("MW", "SOLO-MW", "SYM-MW-009", "Microwave Sparking"),
    ("MW", "SOLO-MW", "SYM-MW-010", "Microwave Abnormal Noise"),
    ("MW", "SOLO-MW", "SYM-MW-011", "Microwave Burning Smell"),
    ("MW", "SOLO-MW", "SYM-MW-012", "Microwave Light Not Working"),
    ("MW", "SOLO-MW", "SYM-MW-013", "Microwave Fan Not Working"),
    ("MW", "SOLO-MW", "SYM-MW-014", "Microwave Auto Restarting"),
    ("MW", "SOLO-MW", "SYM-MW-015", "Microwave Error Code Displayed"),

    # ========================================================
    # GEYSER - 15
    # ========================================================
    ("GEY", "STORAGE-GEY", "SYM-GEY-001", "Geyser Not Powering ON"),
    ("GEY", "STORAGE-GEY", "SYM-GEY-002", "Geyser Not Heating Water"),
    ("GEY", "STORAGE-GEY", "SYM-GEY-003", "Geyser Low Heating"),
    ("GEY", "STORAGE-GEY", "SYM-GEY-004", "Geyser Water Overheating"),
    ("GEY", "STORAGE-GEY", "SYM-GEY-005", "Geyser Water Leakage"),
    ("GEY", "STORAGE-GEY", "SYM-GEY-006", "Geyser Tank Leakage"),
    ("GEY", "STORAGE-GEY", "SYM-GEY-007", "Geyser Heating Indicator Not Working"),
    ("GEY", "STORAGE-GEY", "SYM-GEY-008", "Geyser Thermostat Not Working"),
    ("GEY", "STORAGE-GEY", "SYM-GEY-009", "Geyser Heating Element Not Working"),
    ("GEY", "STORAGE-GEY", "SYM-GEY-010", "Geyser Abnormal Noise"),
    ("GEY", "STORAGE-GEY", "SYM-GEY-011", "Geyser Burning Smell"),
    ("GEY", "STORAGE-GEY", "SYM-GEY-012", "Geyser Display Not Working"),
    ("GEY", "STORAGE-GEY", "SYM-GEY-013", "Geyser Error Code Displayed"),
    ("GEY", "STORAGE-GEY", "SYM-GEY-014", "Geyser Excessive Power Consumption"),
    ("GEY", "STORAGE-GEY", "SYM-GEY-015", "Geyser Safety Cutoff Not Working"),

    # ========================================================
    # LAPTOP - 24
    # ========================================================
    ("LAP", "LAPTOP", "SYM-LAP-001", "Laptop Not Powering ON"),
    ("LAP", "LAPTOP", "SYM-LAP-002", "Laptop Not Charging"),
    ("LAP", "LAPTOP", "SYM-LAP-003", "Laptop Battery Draining Quickly"),
    ("LAP", "LAPTOP", "SYM-LAP-004", "Laptop Battery Not Detected"),
    ("LAP", "LAPTOP", "SYM-LAP-005", "Laptop Screen Blank"),
    ("LAP", "LAPTOP", "SYM-LAP-006", "Laptop Display Flickering"),
    ("LAP", "LAPTOP", "SYM-LAP-007", "Laptop Keyboard Not Working"),
    ("LAP", "LAPTOP", "SYM-LAP-008", "Laptop Touchpad Not Working"),
    ("LAP", "LAPTOP", "SYM-LAP-009", "Laptop WiFi Not Working"),
    ("LAP", "LAPTOP", "SYM-LAP-010", "Laptop Bluetooth Not Working"),
    ("LAP", "LAPTOP", "SYM-LAP-011", "Laptop USB Port Not Working"),
    ("LAP", "LAPTOP", "SYM-LAP-012", "Laptop HDMI Port Not Working"),
    ("LAP", "LAPTOP", "SYM-LAP-013", "Laptop Camera Not Working"),
    ("LAP", "LAPTOP", "SYM-LAP-014", "Laptop Microphone Not Working"),
    ("LAP", "LAPTOP", "SYM-LAP-015", "Laptop Speaker Not Working"),
    ("LAP", "LAPTOP", "SYM-LAP-016", "Laptop Overheating"),
    ("LAP", "LAPTOP", "SYM-LAP-017", "Laptop Fan Noise"),
    ("LAP", "LAPTOP", "SYM-LAP-018", "Laptop Slow Performance"),
    ("LAP", "LAPTOP", "SYM-LAP-019", "Laptop Hanging or Freezing"),
    ("LAP", "LAPTOP", "SYM-LAP-020", "Laptop Auto Restarting"),
    ("LAP", "LAPTOP", "SYM-LAP-021", "Laptop Operating System Error"),
    ("LAP", "LAPTOP", "SYM-LAP-022", "Laptop Keyboard Key Damaged"),
    ("LAP", "LAPTOP", "SYM-LAP-023", "Laptop Body Damaged"),
    ("LAP", "LAPTOP", "SYM-LAP-024", "Laptop Liquid Damage"),

    # ========================================================
    # MOBILE - 30
    # ========================================================
    ("MOB", "SMARTPHONE", "SYM-MOB-001", "Mobile Not Powering ON"),
    ("MOB", "SMARTPHONE", "SYM-MOB-002", "Mobile Not Charging"),
    ("MOB", "SMARTPHONE", "SYM-MOB-003", "Mobile Battery Draining Quickly"),
    ("MOB", "SMARTPHONE", "SYM-MOB-004", "Mobile Battery Swollen"),
    ("MOB", "SMARTPHONE", "SYM-MOB-005", "Mobile Screen Blank"),
    ("MOB", "SMARTPHONE", "SYM-MOB-006", "Mobile Screen Flickering"),
    ("MOB", "SMARTPHONE", "SYM-MOB-007", "Mobile Touch Not Working"),
    ("MOB", "SMARTPHONE", "SYM-MOB-008", "Mobile Display Damaged"),
    ("MOB", "SMARTPHONE", "SYM-MOB-009", "Mobile Camera Not Working"),
    ("MOB", "SMARTPHONE", "SYM-MOB-010", "Mobile Front Camera Not Working"),
    ("MOB", "SMARTPHONE", "SYM-MOB-011", "Mobile Rear Camera Not Working"),
    ("MOB", "SMARTPHONE", "SYM-MOB-012", "Mobile Speaker Not Working"),
    ("MOB", "SMARTPHONE", "SYM-MOB-013", "Mobile Microphone Not Working"),
    ("MOB", "SMARTPHONE", "SYM-MOB-014", "Mobile Earphone Not Working"),
    ("MOB", "SMARTPHONE", "SYM-MOB-015", "Mobile SIM Not Detected"),
    ("MOB", "SMARTPHONE", "SYM-MOB-016", "Mobile Network Not Working"),
    ("MOB", "SMARTPHONE", "SYM-MOB-017", "Mobile WiFi Not Working"),
    ("MOB", "SMARTPHONE", "SYM-MOB-018", "Mobile Bluetooth Not Working"),
    ("MOB", "SMARTPHONE", "SYM-MOB-019", "Mobile GPS Not Working"),
    ("MOB", "SMARTPHONE", "SYM-MOB-020", "Mobile Fingerprint Not Working"),
    ("MOB", "SMARTPHONE", "SYM-MOB-021", "Mobile Face Unlock Not Working"),
    ("MOB", "SMARTPHONE", "SYM-MOB-022", "Mobile Overheating"),
    ("MOB", "SMARTPHONE", "SYM-MOB-023", "Mobile Auto Restarting"),
    ("MOB", "SMARTPHONE", "SYM-MOB-024", "Mobile Hanging or Freezing"),
    ("MOB", "SMARTPHONE", "SYM-MOB-025", "Mobile Apps Crashing"),
    ("MOB", "SMARTPHONE", "SYM-MOB-026", "Mobile USB Port Not Working"),
    ("MOB", "SMARTPHONE", "SYM-MOB-027", "Mobile Vibration Not Working"),
    ("MOB", "SMARTPHONE", "SYM-MOB-028", "Mobile Power Button Not Working"),
    ("MOB", "SMARTPHONE", "SYM-MOB-029", "Mobile Volume Button Not Working"),
    ("MOB", "SMARTPHONE", "SYM-MOB-030", "Mobile Physical Damage"),
]


# ============================================================
# SEED FUNCTION
# ============================================================

def seed_symptoms():
    created = 0
    skipped = 0

    with app.app_context():

        for category_code, type_code, symptom_code, symptom_name in SYMPTOMS:

            # ------------------------------------------------
            # Find Product Category
            # ------------------------------------------------
            category = db.session.scalar(
                db.select(ProductCategory).where(
                    ProductCategory.category_code == category_code
                )
            )

            if not category:
                print(
                    f"SKIPPED CATEGORY: {category_code} | "
                    f"{symptom_code} | {symptom_name}"
                )
                skipped += 1
                continue

            # ------------------------------------------------
            # Find Product Type
            # ------------------------------------------------
            product_type = db.session.scalar(
                db.select(ProductType).where(
                    ProductType.type_code == type_code
                )
            )

            if not product_type:
                print(
                    f"SKIPPED PRODUCT TYPE: {type_code} | "
                    f"{symptom_code} | {symptom_name}"
                )
                skipped += 1
                continue

            # ------------------------------------------------
            # Prevent Duplicate Symptom Codes
            # ------------------------------------------------
            existing = db.session.scalar(
                db.select(SymptomCode).where(
                    SymptomCode.symptom_code == symptom_code
                )
            )

            if existing:
                skipped += 1
                continue

            # ------------------------------------------------
            # Create Symptom
            # ------------------------------------------------
            symptom = SymptomCode(
                symptom_code=symptom_code,
                symptom_name=symptom_name,
                description=f"Customer-reported symptom: {symptom_name}",
                category_id=category.id,
                product_type_id=product_type.id,
                product_model_id=None,
                status="Active",
            )

            db.session.add(symptom)
            created += 1

        # ----------------------------------------------------
        # Commit
        # ----------------------------------------------------
        db.session.commit()

    print()
    print("=" * 55)
    print("SYMPTOM MASTER SEED COMPLETED")
    print("=" * 55)
    print(f"Created : {created}")
    print(f"Skipped : {skipped}")
    print(f"Total   : {len(SYMPTOMS)}")
    print("=" * 55)


if __name__ == "__main__":
    seed_symptoms()