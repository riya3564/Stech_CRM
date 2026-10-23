from app import app
from extensions import db

from models.fault_code import FaultCode
from models.diagnosis_code import DiagnosisCode


def build_diagnosis_code(fault_code):
    """
    Example:
    FLT-TV-001-01 -> DIA-TV-001-01
    """

    if not fault_code.startswith("FLT-"):
        raise ValueError(
            f"Invalid fault code format: {fault_code}"
        )

    return fault_code.replace("FLT-", "DIA-", 1)


def build_diagnosis_name(fault_name):
    """
    Converts the fault into a structured
    technical diagnosis statement.
    """

    replacements = {
        " Failure": " Fault Confirmed",
        " Fault": " Fault Confirmed",
        " Failure.": " Fault Confirmed.",
    }

    diagnosis_name = fault_name.strip()

    for old, new in replacements.items():
        if diagnosis_name.endswith(old):
            diagnosis_name = (
                diagnosis_name[:-len(old)] + new
            )
            break

    return diagnosis_name


def build_description(fault):
    return (
        f"Technical diagnosis for {fault.fault_code}: "
        f"{fault.fault_name}. "
        f"Diagnosis is linked to the corresponding "
        f"product category, product type and service fault."
    )


def seed_diagnoses():

    with app.app_context():

        faults = db.session.scalars(
            db.select(FaultCode)
            .order_by(FaultCode.id)
        ).all()

        if not faults:
            raise RuntimeError(
                "No FaultCode records found. "
                "Run fault_codes_seed.py first."
            )

        print()
        print("=" * 70)
        print("DIAGNOSIS MASTER SEED")
        print("=" * 70)
        print(f"Faults found in database : {len(faults)}")
        print("=" * 70)

        created = 0
        skipped = 0

        # ---------------------------------------------------------
        # CREATE ONE DIAGNOSIS FOR EVERY FAULT
        # ---------------------------------------------------------

        for fault in faults:

            diagnosis_code = build_diagnosis_code(
                fault.fault_code
            )

            existing = db.session.scalar(
                db.select(DiagnosisCode).where(
                    DiagnosisCode.diagnosis_code
                    == diagnosis_code
                )
            )

            if existing:
                skipped += 1
                continue

            diagnosis = DiagnosisCode(
                diagnosis_code=diagnosis_code,

                diagnosis_name=build_diagnosis_name(
                    fault.fault_name
                ),

                description=build_description(
                    fault
                ),

                category_id=fault.category_id,

                product_type_id=fault.product_type_id,

                product_model_id=fault.product_model_id,

                fault_id=fault.id,

                status="Active",
            )

            db.session.add(diagnosis)
            created += 1

        db.session.commit()

        # ---------------------------------------------------------
        # DATABASE COUNTS
        # ---------------------------------------------------------

        total_faults = db.session.scalar(
            db.select(
                db.func.count(FaultCode.id)
            )
        )

        total_diagnoses = db.session.scalar(
            db.select(
                db.func.count(DiagnosisCode.id)
            )
        )

        # ---------------------------------------------------------
        # FIND FAULTS WITHOUT DIAGNOSIS
        # ---------------------------------------------------------

        unmapped_faults = db.session.scalars(
            db.select(FaultCode)
            .outerjoin(
                DiagnosisCode,
                DiagnosisCode.fault_id
                == FaultCode.id
            )
            .where(
                DiagnosisCode.id.is_(None)
            )
        ).all()

        # ---------------------------------------------------------
        # FIND INVALID DIAGNOSIS REFERENCES
        # ---------------------------------------------------------

        invalid_diagnoses = db.session.scalars(
            db.select(DiagnosisCode)
            .outerjoin(
                FaultCode,
                DiagnosisCode.fault_id
                == FaultCode.id
            )
            .where(
                FaultCode.id.is_(None)
            )
        ).all()

        # ---------------------------------------------------------
        # FINAL REPORT
        # ---------------------------------------------------------

        print()
        print("=" * 70)
        print("DIAGNOSIS MASTER SEED RESULT")
        print("=" * 70)

        print(
            f"Faults in database       : {total_faults}"
        )

        print(
            f"Diagnoses created       : {created}"
        )

        print(
            f"Diagnoses skipped       : {skipped}"
        )

        print(
            f"Diagnoses in database   : {total_diagnoses}"
        )

        print(
            f"Unmapped faults         : {len(unmapped_faults)}"
        )

        print(
            f"Invalid diagnosis refs  : {len(invalid_diagnoses)}"
        )

        print("=" * 70)

        # ---------------------------------------------------------
        # COVERAGE VALIDATION
        # ---------------------------------------------------------

        if unmapped_faults:

            print()
            print("MISSING DIAGNOSIS MAPPINGS:")

            for fault in unmapped_faults:
                print(
                    f"{fault.id} | "
                    f"{fault.fault_code} | "
                    f"{fault.fault_name}"
                )

            raise RuntimeError(
                "DIAGNOSIS COVERAGE FAILED."
            )

        if invalid_diagnoses:

            raise RuntimeError(
                "INVALID DIAGNOSIS -> FAULT REFERENCES FOUND."
            )

        if total_faults != total_diagnoses:

            raise RuntimeError(
                "FAULT AND DIAGNOSIS COUNTS DO NOT MATCH."
            )

        print()
        print("=" * 70)
        print("FINAL COVERAGE CHECK")
        print("=" * 70)
        print(
            f"Faults covered : {total_faults} / {total_faults}"
        )
        print(
            f"Diagnosis count: {total_diagnoses}"
        )
        print("Coverage       : PASS")
        print("Status         : SUCCESS")
        print("=" * 70)


if __name__ == "__main__":
    seed_diagnoses()