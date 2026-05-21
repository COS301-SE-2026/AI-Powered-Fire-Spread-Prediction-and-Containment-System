import uuid
from datetime import datetime, timezone

from db import engine, SessionLocal, Base
from models import User, RoleRequestDB, FireReportModel, FireReport, FireReportCreate
from auth import hash_password

# 20 Users: 3 Admins, 5 Firefighters, 12 Users
SEED_USERS = [
    {"id": "usr_01", "email": "sipho.n@fireaway.co.za", "password": "Password123!", "name": "Sipho", "surname": "Ndlovu", "id_number": "8505125800081", "license_number": None, "role": "admin"},
    {"id": "usr_02", "email": "lerato.b@fireaway.co.za", "password": "Password123!", "name": "Lerato", "surname": "Botha", "id_number": "9008234800082", "license_number": None, "role": "admin"},
    {"id": "usr_03", "email": "johan.v@fireaway.co.za", "password": "Password123!", "name": "Johan", "surname": "van der Merwe", "id_number": "8201145000083", "license_number": None, "role": "admin"},
    {"id": "usr_04", "email": "thandiwe.k@fireaway.co.za", "password": "Password123!", "name": "Thandiwe", "surname": "Khumalo", "id_number": "9302284800084", "license_number": "FF-1001", "role": "firefighter"},
    {"id": "usr_05", "email": "pieter.m@fireaway.co.za", "password": "Password123!", "name": "Pieter", "surname": "Mokoena", "id_number": "9507115000085", "license_number": "FF-1002", "role": "firefighter"},
    {"id": "usr_06", "email": "fatima.p@fireaway.co.za", "password": "Password123!", "name": "Fatima", "surname": "Patel", "id_number": "9804054800086", "license_number": "FF-1003", "role": "firefighter"},
    {"id": "usr_07", "email": "siyabonga.z@fireaway.co.za", "password": "Password123!", "name": "Siyabonga", "surname": "Zulu", "id_number": "9109155000087", "license_number": "FF-1004", "role": "firefighter"},
    {"id": "usr_08", "email": "kagiso.m@fireaway.co.za", "password": "Password123!", "name": "Kagiso", "surname": "Mahlangu", "id_number": "9412125000088", "license_number": "FF-1005", "role": "firefighter"},
    {"id": "usr_09", "email": "amahle.d@fireaway.co.za", "password": "Password123!", "name": "Amahle", "surname": "Dlamini", "id_number": "0103144800089", "license_number": None, "role": "user"},
    {"id": "usr_10", "email": "heinrich.k@fireaway.co.za", "password": "Password123!", "name": "Heinrich", "surname": "Kruger", "id_number": "0005185000080", "license_number": None, "role": "user"},
    {"id": "usr_11", "email": "zanele.m@fireaway.co.za", "password": "Password123!", "name": "Zanele", "surname": "Mbatha", "id_number": "9906214800081", "license_number": None, "role": "user"},
    {"id": "usr_12", "email": "ruan.v@fireaway.co.za", "password": "Password123!", "name": "Ruan", "surname": "Venter", "id_number": "0208255000082", "license_number": None, "role": "user"},
    {"id": "usr_13", "email": "naledi.m@fireaway.co.za", "password": "Password123!", "name": "Naledi", "surname": "Moeng", "id_number": "9701304800083", "license_number": None, "role": "user"},
    {"id": "usr_14", "email": "willem.c@fireaway.co.za", "password": "Password123!", "name": "Willem", "surname": "Coetzee", "id_number": "9604125000084", "license_number": None, "role": "user"},
    {"id": "usr_15", "email": "kgotso.b@fireaway.co.za", "password": "Password123!", "name": "Kgotsofalang", "surname": "Baloyi", "id_number": "0309115000085", "license_number": None, "role": "user"},
    {"id": "usr_16", "email": "bianca.n@fireaway.co.za", "password": "Password123!", "name": "Bianca", "surname": "Naidoo", "id_number": "0107194800086", "license_number": None, "role": "user"},
    {"id": "usr_17", "email": "lungile.n@fireaway.co.za", "password": "Password123!", "name": "Lungile", "surname": "Ngcobo", "id_number": "9811224800087", "license_number": None, "role": "user"},
    {"id": "usr_18", "email": "deon.s@fireaway.co.za", "password": "Password123!", "name": "Deon", "surname": "Steyn", "id_number": "9510085000088", "license_number": None, "role": "user"},
    {"id": "usr_19", "email": "anika.s@fireaway.co.za", "password": "Password123!", "name": "Anika", "surname": "Smit", "id_number": "0402144800089", "license_number": None, "role": "user"},
    {"id": "usr_20", "email": "tshepo.m@fireaway.co.za", "password": "Password123!", "name": "Tshepo", "surname": "Moroka", "id_number": "0008165000080", "license_number": None, "role": "user"},
]

# 18 Role Requests
SEED_ROLE_REQUESTS = [
    {"request_id": "req_01", "user_email": "sipho.n@fireaway.co.za", "role": "admin", "firefighter_license_id": None, "status": "approved"},
    {"request_id": "req_02", "user_email": "lerato.b@fireaway.co.za", "role": "admin", "firefighter_license_id": None, "status": "approved"},
    {"request_id": "req_03", "user_email": "johan.v@fireaway.co.za", "role": "admin", "firefighter_license_id": None, "status": "approved"},
    {"request_id": "req_04", "user_email": "amahle.d@fireaway.co.za", "role": "admin", "firefighter_license_id": None, "status": "pending"},
    {"request_id": "req_05", "user_email": "ruan.v@fireaway.co.za", "role": "admin", "firefighter_license_id": None, "status": "pending"},
    {"request_id": "req_06", "user_email": "kgotso.b@fireaway.co.za", "role": "admin", "firefighter_license_id": None, "status": "pending"},
    {"request_id": "req_07", "user_email": "lungile.n@fireaway.co.za", "role": "admin", "firefighter_license_id": None, "status": "pending"},
    {"request_id": "req_08", "user_email": "tshepo.m@fireaway.co.za", "role": "admin", "firefighter_license_id": None, "status": "pending"},
    {"request_id": "req_09", "user_email": "heinrich.k@fireaway.co.za", "role": "admin", "firefighter_license_id": None, "status": "rejected"},
    {"request_id": "req_10", "user_email": "willem.c@fireaway.co.za", "role": "admin", "firefighter_license_id": None, "status": "rejected"},
    {"request_id": "req_11", "user_email": "deon.s@fireaway.co.za", "role": "admin", "firefighter_license_id": None, "status": "rejected"},
    {"request_id": "req_12", "user_email": "zanele.m@fireaway.co.za", "role": "admin", "firefighter_license_id": None, "status": "revoked"},
    {"request_id": "req_13", "user_email": "bianca.n@fireaway.co.za", "role": "admin", "firefighter_license_id": None, "status": "revoked"},
    {"request_id": "req_14", "user_email": "thandiwe.k@fireaway.co.za", "role": "admin", "firefighter_license_id": "FF-1001", "status": "pending"},
    {"request_id": "req_15", "user_email": "siyabonga.z@fireaway.co.za", "role": "admin", "firefighter_license_id": "FF-1004", "status": "pending"},
    {"request_id": "req_16", "user_email": "pieter.m@fireaway.co.za", "role": "admin", "firefighter_license_id": "FF-1002", "status": "rejected"},
    {"request_id": "req_17", "user_email": "kagiso.m@fireaway.co.za", "role": "admin", "firefighter_license_id": "FF-1005", "status": "rejected"},
    {"request_id": "req_18", "user_email": "fatima.p@fireaway.co.za", "role": "admin", "firefighter_license_id": "FF-1003", "status": "revoked"},
]

# 18 Fire Reports around Pretoria
SEED_FIRE_REPORTS = [
    {"reference_number": "FR-2026-001", "user_email": "sipho.n@fireaway.co.za", "location_text": "LC de Villiers Sports Grounds, Hatfield", "description": "Brush fire starting near the northern fence along the road.", "location_geom": "SRID=4326;POINT(28.2435 -25.7480)", "boundary_radius_km": 0.5, "status": ReportStatus.verified, "status_index": 2},
    {"reference_number": "FR-2026-002", "user_email": None, "location_text": "Groenkloof Nature Reserve", "description": "Heavy smoke visible from the main hiking trail.", "location_geom": "SRID=4326;POINT(28.2000 -25.7800)", "boundary_radius_km": 2.0, "status": ReportStatus.pending, "status_index": 1},
    {"reference_number": "FR-2026-003", "user_email": "amahle.d@fireaway.co.za", "location_text": "Struben Dam Bird Sanctuary", "description": "Small contained fire, looks like an abandoned braai.", "location_geom": "SRID=4326;POINT(28.2933 -25.7681)", "boundary_radius_km": 0.1, "status": ReportStatus.received, "status_index": 0},
    {"reference_number": "FR-2026-004", "user_email": "heinrich.k@fireaway.co.za", "location_text": "Rietvlei Nature Reserve", "description": "Large veld fire spreading quickly towards the eastern border.", "location_geom": "SRID=4326;POINT(28.2800 -25.8800)", "boundary_radius_km": 3.5, "status": ReportStatus.notified, "status_index": 3},
    {"reference_number": "FR-2026-005", "user_email": None, "location_text": "Moreleta Kloof Nature Reserve", "description": "Smell of smoke and ash falling, but can't see the flames.", "location_geom": "SRID=4326;POINT(28.2890 -25.8180)", "boundary_radius_km": 1.0, "status": ReportStatus.received, "status_index": 0},
    {"reference_number": "FR-2026-006", "user_email": "zanele.m@fireaway.co.za", "location_text": "Faerie Glen Nature Reserve", "description": "Fire on the ridge, moving up the hill.", "location_geom": "SRID=4326;POINT(28.2930 -25.7760)", "boundary_radius_km": 1.5, "status": ReportStatus.verified, "status_index": 2},
    {"reference_number": "FR-2026-007", "user_email": "ruan.v@fireaway.co.za", "location_text": "Wonderboom Nature Reserve", "description": "Smoke coming from the northern slope of the Magaliesberg.", "location_geom": "SRID=4326;POINT(28.1900 -25.6800)", "boundary_radius_km": 2.5, "status": ReportStatus.pending, "status_index": 1},
    {"reference_number": "FR-2026-008", "user_email": "naledi.m@fireaway.co.za", "location_text": "Pretoria National Botanical Garden", "description": "Fire near the eastern boundary wall.", "location_geom": "SRID=4326;POINT(28.2700 -25.7300)", "boundary_radius_km": 0.3, "status": ReportStatus.notified, "status_index": 3},
    {"reference_number": "FR-2026-009", "user_email": None, "location_text": "Roodeplaat Dam Nature Reserve", "description": "Veld fire near the southern picnic site.", "location_geom": "SRID=4326;POINT(28.3600 -25.6300)", "boundary_radius_km": 4.0, "status": ReportStatus.verified, "status_index": 2},
    {"reference_number": "FR-2026-010", "user_email": "willem.c@fireaway.co.za", "location_text": "Fountains Valley Recreation Resort", "description": "Thick smoke near the train tracks.", "location_geom": "SRID=4326;POINT(28.1960 -25.7820)", "boundary_radius_km": 0.8, "status": ReportStatus.received, "status_index": 0},
    {"reference_number": "FR-2026-011", "user_email": "kgotso.b@fireaway.co.za", "location_text": "Vacant lot, Erasmuskloof", "description": "Grass fire near the highway offramp.", "location_geom": "SRID=4326;POINT(28.2600 -25.8100)", "boundary_radius_km": 0.2, "status": ReportStatus.verified, "status_index": 2},
    {"reference_number": "FR-2026-012", "user_email": None, "location_text": "Centurion field near N1", "description": "Large grass fire causing poor visibility on the N1.", "location_geom": "SRID=4326;POINT(28.1800 -25.8500)", "boundary_radius_km": 1.2, "status": ReportStatus.pending, "status_index": 1},
    {"reference_number": "FR-2026-013", "user_email": "bianca.n@fireaway.co.za", "location_text": "Pretoria West Industrial Area", "description": "Chemical smoke rising from an industrial yard.", "location_geom": "SRID=4326;POINT(28.1500 -25.7500)", "boundary_radius_km": 0.5, "status": ReportStatus.notified, "status_index": 3},
    {"reference_number": "FR-2026-014", "user_email": "lungile.n@fireaway.co.za", "location_text": "Atterbury Road grass verge", "description": "Small fire on the side of the road, looks like someone threw a cigarette.", "location_geom": "SRID=4326;POINT(28.3100 -25.7900)", "boundary_radius_km": 0.1, "status": ReportStatus.received, "status_index": 0},
    {"reference_number": "FR-2026-015", "user_email": "deon.s@fireaway.co.za", "location_text": "Silver Lakes boundary", "description": "Fire in the open field approaching the estate wall.", "location_geom": "SRID=4326;POINT(28.3500 -25.7600)", "boundary_radius_km": 1.8, "status": ReportStatus.verified, "status_index": 2},
    {"reference_number": "FR-2026-016", "user_email": "anika.s@fireaway.co.za", "location_text": "Menlyn Maine construction site brush", "description": "Debris fire getting out of control due to wind.", "location_geom": "SRID=4326;POINT(28.2800 -25.7800)", "boundary_radius_km": 0.4, "status": ReportStatus.pending, "status_index": 1},
    {"reference_number": "FR-2026-017", "user_email": None, "location_text": "Lynnwood Road crossing", "description": "Rubbish burning under the bridge, spreading to dry grass.", "location_geom": "SRID=4326;POINT(28.2500 -25.7600)", "boundary_radius_km": 0.2, "status": ReportStatus.received, "status_index": 0},
    {"reference_number": "FR-2026-018", "user_email": "tshepo.m@fireaway.co.za", "location_text": "Voortrekker Monument hillside", "description": "Flames visible on the southern slope from the highway.", "location_geom": "SRID=4326;POINT(28.1700 -25.7700)", "boundary_radius_km": 3.0, "status": ReportStatus.verified, "status_index": 2}
]

def seed_users(db) -> dict:
    inserted = {}
    for data in SEED_USERS:
        existing = db.query(User).filter(User.email == data["email"]).first()
        if existing:
            print(f" SKIP {data['email']} (already exists)")
            inserted[data["email"]] = existing
            continue

        user = User(
            id=data["id"],
            email=data["email"],
            hashed_password=hash_password(data["password"]),
            name=data["name"],
            surname=data["surname"],
            id_number=data["id_number"],
            license_number=data.get("license_number"),
            role=data["role"],
            is_2fa_enabled=False,
        )
        db.add(user)
        inserted[data["email"]] = user
        print(f" ADD {data['email']} ({data['role']})")
    
    db.flush()
    return inserted

def seed_role_requests(db, users_by_email: dict):
    for data in SEED_ROLE_REQUESTS:
        user = users_by_email.get(data["user_email"])
        if not user:
            print(f"  SKIP  role request for {data['user_email']} (user not found)")
            continue

        existing = (
            db.query(RoleRequestDB)
            .filter(
                RoleRequestDB.user_id == user.id,
                RoleRequestDB.role == data["role"],
            )
            .first()
        )
        if existing:
            print(f"  SKIP  role request {data['role']} for {data['user_email']} (already exists)")
            continue

        role_request = RoleRequestDB(
            request_id=data["request_id"],
            user_id=user.id,
            user_full_name=f"{user.name} {user.surname}",
            email=user.email,
            role=data["role"],
            status=data["status"],
            firefighter_license_id=data.get("firefighter_license_id"),
            created_at=datetime.now(timezone.utc),
        )
        db.add(role_request)
        print(f"  ADD   role request → {data['role']} for {data['user_email']}")

def seed_fire_reports(db, users_by_email: dict):
    for data in SEED_FIRE_REPORTS:
        user_id = None
        if data["user_email"]:
            user = users_by_email.get(data["user_email"])
            if user:
                user_id = user.id

        existing = db.query(FireReportModel).filter(FireReportModel.reference_number == data["reference_number"]).first()
        if existing:
            print(f"  SKIP  fire report {data['reference_number']} (already exists)")
            continue

        report = FireReportModel(
            reference_number=data["reference_number"],
            user_id=user_id,
            location_text=data["location_text"],
            description=data["description"],
            location_geom=data["location_geom"],
            boundary_radius_km=data["boundary_radius_km"],
            status=data["status"],
            status_index=data["status_index"]
        )
        db.add(report)
        print(f"  ADD   fire report → {data['reference_number']} at {data['location_text']}")

def seed():
    print("Creating tables if they don't exist...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("\nWiping old data...")
        db.query(FireReportModel).delete()
        db.query(RoleRequestDB).delete()
        db.query(User).delete()

        db.commit()
        print("Old data wiped successfully.")

        print("\nSeeding users...")
        users_by_email = seed_users(db)

        print("\nSeeding role requests...")
        seed_role_requests(db, users_by_email)

        db.commit()
        print("\nSeed complete!")

    except Exception as exc:
        db.rollback()
        print(f"\nSeed failed, rolled back: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()

