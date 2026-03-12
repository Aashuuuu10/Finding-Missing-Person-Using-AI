import sqlite3
from datetime import datetime
from sqlmodel import create_engine, Session, select

from pages.helper.data_models import RegisteredCases, PublicSubmissions, CaseActivity


sqlite_url = "sqlite:///sqlite_database.db"
engine = create_engine(sqlite_url)


def create_db():
    try:
        RegisteredCases.__table__.create(engine)
    except:
        pass
    try:
        PublicSubmissions.__table__.create(engine)
    except:
        pass
    try:
        CaseActivity.__table__.create(engine)
    except:
        pass
    # Migrate: add new columns if they don't exist
    _migrate_columns()


def _migrate_columns():
    """Add new columns to existing tables if missing (safe migration)."""
    conn = sqlite3.connect("sqlite_database.db")
    cursor = conn.cursor()
    migrations = [
        ("registeredcases", "photo_count", "INTEGER DEFAULT 1"),
        ("registeredcases", "match_score", "REAL DEFAULT 0.0"),
    ]
    for table, col, col_type in migrations:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
        except sqlite3.OperationalError:
            pass  # column already exists
    conn.commit()
    conn.close()


def register_new_case(case_details: RegisteredCases):
    with Session(engine) as session:
        session.add(case_details)
        session.commit()


def fetch_registered_cases(submitted_by: str, status: str):
    if status == "All":
        status = ["F", "NF"]
    elif status == "Found":
        status = ["F"]
    elif status == "Not Found":
        status = ["NF"]

    with Session(engine) as session:
        result = session.exec(
            select(
                RegisteredCases.id,
                RegisteredCases.name,
                RegisteredCases.age,
                RegisteredCases.status,
                RegisteredCases.last_seen,
                RegisteredCases.matched_with,
            )
            .where(RegisteredCases.submitted_by == submitted_by)
            .where(RegisteredCases.status.in_(status))
        ).all()
        return result


def fetch_public_cases(train_data: bool, status: str):
    if train_data:
        with Session(engine) as session:
            result = session.exec(
                select(
                    PublicSubmissions.id,
                    PublicSubmissions.face_mesh,
                ).where(PublicSubmissions.status == status)
            ).all()
            return result

    with Session(engine) as session:
        result = session.exec(
            select(
                PublicSubmissions.id,
                PublicSubmissions.status,
                PublicSubmissions.location,
                PublicSubmissions.mobile,
                PublicSubmissions.birth_marks,
                PublicSubmissions.submitted_on,
                PublicSubmissions.submitted_by,
            )
        ).all()
        return result


def get_not_confirmed_registered_cases(submitted_by: str):
    with Session(engine) as session:
        result = session.query(RegisteredCases).all()
        return result


def get_training_data(submitted_by: str):
    with Session(engine) as session:
        result = session.exec(
            select(RegisteredCases.id, RegisteredCases.face_mesh)
            .where(RegisteredCases.submitted_by == submitted_by)
            .where(RegisteredCases.status == "NF")
        ).all()
        return result


def new_public_case(public_case_details: PublicSubmissions):
    with Session(engine) as session:
        session.add(public_case_details)
        session.commit()


def get_public_case_detail(case_id: str):
    with Session(engine) as session:
        result = session.exec(
            select(
                PublicSubmissions.location,
                PublicSubmissions.submitted_by,
                PublicSubmissions.mobile,
                PublicSubmissions.birth_marks,
            ).where(PublicSubmissions.id == case_id)
        ).all()
        return result


def get_registered_case_detail(case_id: str):
    print(case_id)
    with Session(engine) as session:
        result = session.exec(
            select(
                RegisteredCases.name,
                RegisteredCases.complainant_mobile,
                RegisteredCases.age,
                RegisteredCases.last_seen,
                RegisteredCases.birth_marks,
            ).where(RegisteredCases.id == case_id)
        ).all()
        print(result)
        return result


def list_public_cases():
    with Session(engine) as session:
        result = session.exec(select(PublicSubmissions)).all()
        return result


def update_found_status(register_case_id: str, public_case_id: str):
    with Session(engine) as session:
        registered_case_details = session.exec(
            select(RegisteredCases).where(RegisteredCases.id == str(register_case_id))
        ).one()
        registered_case_details.status = "F"
        registered_case_details.matched_with = str(public_case_id)

        public_case_details = session.exec(
            select(PublicSubmissions).where(PublicSubmissions.id == str(public_case_id))
        ).one()
        public_case_details.status = "F"

        session.add(registered_case_details)
        session.add(public_case_details)
        session.commit()


def update_found_status_with_score(register_case_id: str, public_case_id: str, score: float):
    """Update found status and also store similarity score."""
    with Session(engine) as session:
        registered_case_details = session.exec(
            select(RegisteredCases).where(RegisteredCases.id == str(register_case_id))
        ).one()
        registered_case_details.status = "F"
        registered_case_details.matched_with = str(public_case_id)
        registered_case_details.match_score = score

        public_case_details = session.exec(
            select(PublicSubmissions).where(PublicSubmissions.id == str(public_case_id))
        ).one()
        public_case_details.status = "F"

        session.add(registered_case_details)
        session.add(public_case_details)
        session.commit()


def update_photo_count(case_id: str, count: int):
    """Update photo count for a registered case."""
    with Session(engine) as session:
        case = session.exec(
            select(RegisteredCases).where(RegisteredCases.id == str(case_id))
        ).one()
        case.photo_count = count
        session.add(case)
        session.commit()


# ─── Activity Log ───

def log_activity(case_id: str, case_type: str, action: str, description: str = "", actor: str = ""):
    """Log an activity event for a case."""
    create_db()  # ensure CaseActivity table exists
    with Session(engine) as session:
        activity = CaseActivity(
            case_id=case_id,
            case_type=case_type,
            action=action,
            description=description,
            actor=actor,
        )
        session.add(activity)
        session.commit()


def get_case_activities(case_id: str):
    """Fetch all activities for a case, ordered by timestamp desc."""
    create_db()
    with Session(engine) as session:
        result = session.exec(
            select(CaseActivity)
            .where(CaseActivity.case_id == case_id)
            .order_by(CaseActivity.timestamp.desc())
        ).all()
        return result


def get_all_activities(limit: int = 50):
    """Fetch recent activities across all cases."""
    create_db()
    with Session(engine) as session:
        result = session.exec(
            select(CaseActivity)
            .order_by(CaseActivity.timestamp.desc())
            .limit(limit)
        ).all()
        return result


# ─── Analytics Queries ───

def get_cases_over_time(submitted_by: str):
    """Return list of (submitted_on, status) for date-based charts."""
    with Session(engine) as session:
        result = session.exec(
            select(RegisteredCases.submitted_on, RegisteredCases.status)
            .where(RegisteredCases.submitted_by == submitted_by)
            .order_by(RegisteredCases.submitted_on)
        ).all()
        return result


def get_cases_by_area(submitted_by: str):
    """Return list of (last_seen,) for area grouping."""
    with Session(engine) as session:
        result = session.exec(
            select(RegisteredCases.last_seen)
            .where(RegisteredCases.submitted_by == submitted_by)
        ).all()
        return result


def get_age_distribution(submitted_by: str):
    """Return list of (age,) for age distribution chart."""
    with Session(engine) as session:
        result = session.exec(
            select(RegisteredCases.age)
            .where(RegisteredCases.submitted_by == submitted_by)
        ).all()
        return result


def get_match_score_for_case(case_id: str):
    """Return the match_score for a registered case."""
    with Session(engine) as session:
        result = session.exec(
            select(RegisteredCases.match_score)
            .where(RegisteredCases.id == str(case_id))
        ).first()
        return result


def get_registered_cases_count(submitted_by: str, status: str):
    create_db()

    with Session(engine) as session:
        result = session.exec(
            select(RegisteredCases)
            .where(RegisteredCases.submitted_by == submitted_by)
            .where(RegisteredCases.status == status)
        ).all()
        return result


if __name__ == "__main__":
    r = fetch_public_cases("NF")
    print(r)
