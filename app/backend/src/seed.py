import uuid
from datetime import datetime, timedelta, timezone

from auth import hash_password
from db import Base, SessionLocal, engine
from enums.report_status import ReportStatus
from enums.role_request_status import RequestStatus
from enums.user_role import UserRole
from models.reported_fires import FireReports
from models.role_request import RoleRequest

# from models import User, RoleRequestDB, FireReportModel, ReportStatus
from models.users import User

password = "Password123!"

# 20 Users: 3 Admins, 5 Firefighters, 12 Users
SEED_USERS = [
    {
        "id": "usr_01",
        "email": "sipho.n@fireaway.co.za",
        "password": password,
        "name": "Sipho",
        "surname": "Ndlovu",
        "id_number": "8505125800081",
        "license_number": None,
        "role": "admin",
    },
    {
        "id": "usr_02",
        "email": "lerato.b@fireaway.co.za",
        "password": password,
        "name": "Lerato",
        "surname": "Botha",
        "id_number": "9008234800082",
        "license_number": None,
        "role": "admin",
    },
    {
        "id": "usr_03",
        "email": "johan.v@fireaway.co.za",
        "password": password,
        "name": "Johan",
        "surname": "van der Merwe",
        "id_number": "8201145000083",
        "license_number": None,
        "role": "admin",
    },
    {
        "id": "usr_04",
        "email": "thandiwe.k@fireaway.co.za",
        "password": password,
        "name": "Thandiwe",
        "surname": "Khumalo",
        "id_number": "9302284800084",
        "license_number": "FF-1001",
        "role": "firefighter",
    },
    {
        "id": "usr_05",
        "email": "pieter.m@fireaway.co.za",
        "password": password,
        "name": "Pieter",
        "surname": "Mokoena",
        "id_number": "9507115000085",
        "license_number": "FF-1002",
        "role": "firefighter",
    },
    {
        "id": "usr_06",
        "email": "fatima.p@fireaway.co.za",
        "password": password,
        "name": "Fatima",
        "surname": "Patel",
        "id_number": "9804054800086",
        "license_number": "FF-1003",
        "role": "firefighter",
    },
    {
        "id": "usr_07",
        "email": "siyabonga.z@fireaway.co.za",
        "password": password,
        "name": "Siyabonga",
        "surname": "Zulu",
        "id_number": "9109155000087",
        "license_number": "FF-1004",
        "role": "firefighter",
    },
    {
        "id": "usr_08",
        "email": "kagiso.m@fireaway.co.za",
        "password": password,
        "name": "Kagiso",
        "surname": "Mahlangu",
        "id_number": "9412125000088",
        "license_number": "FF-1005",
        "role": "firefighter",
    },
    {
        "id": "usr_09",
        "email": "amahle.d@fireaway.co.za",
        "password": password,
        "name": "Amahle",
        "surname": "Dlamini",
        "id_number": "0103144800089",
        "license_number": None,
        "role": "user",
    },
    {
        "id": "usr_10",
        "email": "heinrich.k@fireaway.co.za",
        "password": password,
        "name": "Heinrich",
        "surname": "Kruger",
        "id_number": "0005185000080",
        "license_number": None,
        "role": "user",
    },
    {
        "id": "usr_11",
        "email": "zanele.m@fireaway.co.za",
        "password": password,
        "name": "Zanele",
        "surname": "Mbatha",
        "id_number": "9906214800081",
        "license_number": None,
        "role": "user",
    },
    {
        "id": "usr_12",
        "email": "ruan.v@fireaway.co.za",
        "password": password,
        "name": "Ruan",
        "surname": "Venter",
        "id_number": "0208255000082",
        "license_number": None,
        "role": "user",
    },
    {
        "id": "usr_13",
        "email": "naledi.m@fireaway.co.za",
        "password": password,
        "name": "Naledi",
        "surname": "Moeng",
        "id_number": "9701304800083",
        "license_number": None,
        "role": "user",
    },
    {
        "id": "usr_14",
        "email": "willem.c@fireaway.co.za",
        "password": password,
        "name": "Willem",
        "surname": "Coetzee",
        "id_number": "9604125000084",
        "license_number": None,
        "role": "user",
    },
    {
        "id": "usr_15",
        "email": "kgotso.b@fireaway.co.za",
        "password": password,
        "name": "Kgotsofalang",
        "surname": "Baloyi",
        "id_number": "0309115000085",
        "license_number": None,
        "role": "user",
    },
    {
        "id": "usr_16",
        "email": "bianca.n@fireaway.co.za",
        "password": password,
        "name": "Bianca",
        "surname": "Naidoo",
        "id_number": "0107194800086",
        "license_number": None,
        "role": "user",
    },
    {
        "id": "usr_17",
        "email": "lungile.n@fireaway.co.za",
        "password": password,
        "name": "Lungile",
        "surname": "Ngcobo",
        "id_number": "9811224800087",
        "license_number": None,
        "role": "user",
    },
    {
        "id": "usr_18",
        "email": "deon.s@fireaway.co.za",
        "password": password,
        "name": "Deon",
        "surname": "Steyn",
        "id_number": "9510085000088",
        "license_number": None,
        "role": "user",
    },
    {
        "id": "usr_19",
        "email": "anika.s@fireaway.co.za",
        "password": password,
        "name": "Anika",
        "surname": "Smit",
        "id_number": "0402144800089",
        "license_number": None,
        "role": "user",
    },
    {
        "id": "usr_20",
        "email": "tshepo.m@fireaway.co.za",
        "password": password,
        "name": "Tshepo",
        "surname": "Moroka",
        "id_number": "0008165000080",
        "license_number": None,
        "role": "user",
    },
]

# 18 Role Requests
SEED_ROLE_REQUESTS = [
    {
        "request_id": "req_01",
        "user_id": "usr_01",
        "requested_role": UserRole.admin,
        "current_role": UserRole.user,
        "status": RequestStatus.approved,
        "reviewed_by": "usr_02",
    },
    {
        "request_id": "req_02",
        "user_id": "usr_02",
        "requested_role": UserRole.admin,
        "current_role": UserRole.user,
        "status": RequestStatus.approved,
        "reviewed_by": "usr_01",
    },
    {
        "request_id": "req_03",
        "user_id": "usr_03",
        "requested_role": UserRole.admin,
        "current_role": UserRole.user,
        "status": RequestStatus.approved,
        "reviewed_by": "usr_01",
    },
    {
        "request_id": "req_04",
        "user_id": "usr_09",
        "requested_role": UserRole.admin,
        "current_role": UserRole.user,
        "status": RequestStatus.pending,
        "reviewed_by": None,
    },
    {
        "request_id": "req_05",
        "user_id": "usr_12",
        "requested_role": UserRole.admin,
        "current_role": UserRole.user,
        "status": RequestStatus.pending,
        "reviewed_by": None,
    },
    {
        "request_id": "req_06",
        "user_id": "usr_15",
        "requested_role": UserRole.admin,
        "current_role": UserRole.user,
        "status": RequestStatus.pending,
        "reviewed_by": None,
    },
    {
        "request_id": "req_07",
        "user_id": "usr_17",
        "requested_role": UserRole.admin,
        "current_role": UserRole.user,
        "status": RequestStatus.pending,
        "reviewed_by": None,
    },
    {
        "request_id": "req_08",
        "user_id": "usr_20",
        "requested_role": UserRole.admin,
        "current_role": UserRole.user,
        "status": RequestStatus.pending,
        "reviewed_by": None,
    },
    {
        "request_id": "req_09",
        "user_id": "usr_10",
        "requested_role": UserRole.admin,
        "current_role": UserRole.user,
        "status": RequestStatus.rejected,
        "reviewed_by": "usr_01",
    },
    {
        "request_id": "req_10",
        "user_id": "usr_14",
        "requested_role": UserRole.admin,
        "current_role": UserRole.user,
        "status": RequestStatus.rejected,
        "reviewed_by": "usr_02",
    },
    {
        "request_id": "req_11",
        "user_id": "usr_18",
        "requested_role": UserRole.admin,
        "current_role": UserRole.user,
        "status": RequestStatus.rejected,
        "reviewed_by": "usr_03",
    },
    {
        "request_id": "req_12",
        "user_id": "usr_11",
        "requested_role": UserRole.admin,
        "current_role": UserRole.admin,
        "status": RequestStatus.revoked,
        "reviewed_by": "usr_01",
    },
    {
        "request_id": "req_13",
        "user_id": "usr_16",
        "requested_role": UserRole.admin,
        "current_role": UserRole.admin,
        "status": RequestStatus.revoked,
        "reviewed_by": "usr_02",
    },
    {
        "request_id": "req_14",
        "user_id": "usr_04",
        "requested_role": UserRole.firefighter,
        "current_role": UserRole.user,
        "status": RequestStatus.pending,
        "reviewed_by": None,
    },
    {
        "request_id": "req_15",
        "user_id": "usr_07",
        "requested_role": UserRole.firefighter,
        "current_role": UserRole.user,
        "status": RequestStatus.pending,
        "reviewed_by": None,
    },
    {
        "request_id": "req_16",
        "user_id": "usr_05",
        "requested_role": UserRole.firefighter,
        "current_role": UserRole.user,
        "status": RequestStatus.rejected,
        "reviewed_by": "usr_01",
    },
    {
        "request_id": "req_17",
        "user_id": "usr_08",
        "requested_role": UserRole.firefighter,
        "current_role": UserRole.user,
        "status": RequestStatus.rejected,
        "reviewed_by": "usr_03",
    },
    {
        "request_id": "req_18",
        "user_id": "usr_06",
        "requested_role": UserRole.firefighter,
        "current_role": UserRole.firefighter,
        "status": RequestStatus.revoked,
        "reviewed_by": "usr_02",
    },
]

DEFAULT_IMG = "https://placehold.co/600x400/png?text=Fire+Report"
DEFAULT_IP = "192.168.1.10"

# 18 Fire Reports around Pretoria
SEED_FIRE_REPORTS = [
    {
        "id": str(uuid.uuid4()),
        "reference_number": "FR-2026-001",
        "user_id": "usr_01",
        "location_text": "LC de Villiers Sports Grounds, Hatfield",
        "description": "Brush fire starting near the northern fence along the road.",
        "location_geom": "SRID=4326;POINT(28.2435 -25.7480)",
        "boundary_radius": 0.5,
        "image_url": DEFAULT_IMG,
        "reporter_ip": DEFAULT_IP,
        "status": ReportStatus.verified,
        "status_index": 2,
    },
    {
        "id": str(uuid.uuid4()),
        "reference_number": "FR-2026-002",
        "user_id": None,
        "location_text": "Groenkloof Nature Reserve",
        "description": "Heavy smoke visible from the main hiking trail.",
        "location_geom": "SRID=4326;POINT(28.2000 -25.7800)",
        "boundary_radius": 2.0,
        "image_url": DEFAULT_IMG,
        "reporter_ip": DEFAULT_IP,
        "status": ReportStatus.pending,
        "status_index": 1,
    },
    {
        "id": str(uuid.uuid4()),
        "reference_number": "FR-2026-003",
        "user_id": "usr_09",
        "location_text": "Struben Dam Bird Sanctuary",
        "description": "Small contained fire, looks like an abandoned braai.",
        "location_geom": "SRID=4326;POINT(28.2933 -25.7681)",
        "boundary_radius": 0.1,
        "image_url": DEFAULT_IMG,
        "reporter_ip": DEFAULT_IP,
        "status": ReportStatus.received,
        "status_index": 0,
    },
    {
        "id": str(uuid.uuid4()),
        "reference_number": "FR-2026-004",
        "user_id": "usr_10",
        "location_text": "Rietvlei Nature Reserve",
        "description": "Large veld fire spreading quickly towards the eastern border.",
        "location_geom": "SRID=4326;POINT(28.2800 -25.8800)",
        "boundary_radius": 3.5,
        "image_url": DEFAULT_IMG,
        "reporter_ip": DEFAULT_IP,
        "status": ReportStatus.verified,
        "status_index": 2,
    },
    {
        "id": str(uuid.uuid4()),
        "reference_number": "FR-2026-005",
        "user_id": None,
        "location_text": "Moreleta Kloof Nature Reserve",
        "description": "Smell of smoke and ash falling, but can't see the flames.",
        "location_geom": "SRID=4326;POINT(28.2890 -25.8180)",
        "boundary_radius": 1.0,
        "image_url": DEFAULT_IMG,
        "reporter_ip": DEFAULT_IP,
        "status": ReportStatus.received,
        "status_index": 0,
    },
    {
        "id": str(uuid.uuid4()),
        "reference_number": "FR-2026-006",
        "user_id": "usr_11",
        "location_text": "Faerie Glen Nature Reserve",
        "description": "Fire on the ridge, moving up the hill.",
        "location_geom": "SRID=4326;POINT(28.2930 -25.7760)",
        "boundary_radius": 1.5,
        "image_url": DEFAULT_IMG,
        "reporter_ip": DEFAULT_IP,
        "status": ReportStatus.verified,
        "status_index": 2,
    },
    {
        "id": str(uuid.uuid4()),
        "reference_number": "FR-2026-007",
        "user_id": "usr_12",
        "location_text": "Wonderboom Nature Reserve",
        "description": "Smoke coming from the northern slope of the Magaliesberg.",
        "location_geom": "SRID=4326;POINT(28.1900 -25.6800)",
        "boundary_radius": 2.5,
        "image_url": DEFAULT_IMG,
        "reporter_ip": DEFAULT_IP,
        "status": ReportStatus.pending,
        "status_index": 1,
    },
    {
        "id": str(uuid.uuid4()),
        "reference_number": "FR-2026-008",
        "user_id": "usr_13",
        "location_text": "Pretoria National Botanical Garden",
        "description": "Fire near the eastern boundary wall.",
        "location_geom": "SRID=4326;POINT(28.2700 -25.7300)",
        "boundary_radius": 0.3,
        "image_url": DEFAULT_IMG,
        "reporter_ip": DEFAULT_IP,
        "status": ReportStatus.verified,
        "status_index": 2,
    },
    {
        "id": str(uuid.uuid4()),
        "reference_number": "FR-2026-009",
        "user_id": None,
        "location_text": "Roodeplaat Dam Nature Reserve",
        "description": "Veld fire near the southern picnic site.",
        "location_geom": "SRID=4326;POINT(28.3600 -25.6300)",
        "boundary_radius": 4.0,
        "image_url": DEFAULT_IMG,
        "reporter_ip": DEFAULT_IP,
        "status": ReportStatus.verified,
        "status_index": 2,
    },
    {
        "id": str(uuid.uuid4()),
        "reference_number": "FR-2026-010",
        "user_id": "usr_14",
        "location_text": "Fountains Valley Recreation Resort",
        "description": "Thick smoke near the train tracks.",
        "location_geom": "SRID=4326;POINT(28.1960 -25.7820)",
        "boundary_radius": 0.8,
        "image_url": DEFAULT_IMG,
        "reporter_ip": DEFAULT_IP,
        "status": ReportStatus.received,
        "status_index": 0,
    },
    {
        "id": str(uuid.uuid4()),
        "reference_number": "FR-2026-011",
        "user_id": "usr_15",
        "location_text": "Vacant lot, Erasmuskloof",
        "description": "Grass fire near the highway offramp.",
        "location_geom": "SRID=4326;POINT(28.2600 -25.8100)",
        "boundary_radius": 0.2,
        "image_url": DEFAULT_IMG,
        "reporter_ip": DEFAULT_IP,
        "status": ReportStatus.verified,
        "status_index": 2,
    },
    {
        "id": str(uuid.uuid4()),
        "reference_number": "FR-2026-012",
        "user_id": None,
        "location_text": "Centurion field near N1",
        "description": "Large grass fire causing poor visibility on the N1.",
        "location_geom": "SRID=4326;POINT(28.1800 -25.8500)",
        "boundary_radius": 1.2,
        "image_url": DEFAULT_IMG,
        "reporter_ip": DEFAULT_IP,
        "status": ReportStatus.pending,
        "status_index": 1,
    },
    {
        "id": str(uuid.uuid4()),
        "reference_number": "FR-2026-013",
        "user_id": "usr_16",
        "location_text": "Pretoria West Industrial Area",
        "description": "Chemical smoke rising from an industrial yard.",
        "location_geom": "SRID=4326;POINT(28.1500 -25.7500)",
        "boundary_radius": 0.5,
        "image_url": DEFAULT_IMG,
        "reporter_ip": DEFAULT_IP,
        "status": ReportStatus.verified,
        "status_index": 2,
    },
    {
        "id": str(uuid.uuid4()),
        "reference_number": "FR-2026-014",
        "user_id": "usr_17",
        "location_text": "Atterbury Road grass verge",
        "description": "Small fire on the side of the road, looks like someone threw a cigarette.",
        "location_geom": "SRID=4326;POINT(28.3100 -25.7900)",
        "boundary_radius": 0.1,
        "image_url": DEFAULT_IMG,
        "reporter_ip": DEFAULT_IP,
        "status": ReportStatus.received,
        "status_index": 0,
    },
    {
        "id": str(uuid.uuid4()),
        "reference_number": "FR-2026-015",
        "user_id": "usr_18",
        "location_text": "Silver Lakes boundary",
        "description": "Fire in the open field approaching the estate wall.",
        "location_geom": "SRID=4326;POINT(28.3500 -25.7600)",
        "boundary_radius": 1.8,
        "image_url": DEFAULT_IMG,
        "reporter_ip": DEFAULT_IP,
        "status": ReportStatus.verified,
        "status_index": 2,
    },
    {
        "id": str(uuid.uuid4()),
        "reference_number": "FR-2026-016",
        "user_id": "usr_19",
        "location_text": "Menlyn Maine construction site brush",
        "description": "Debris fire getting out of control due to wind.",
        "location_geom": "SRID=4326;POINT(28.2800 -25.7800)",
        "boundary_radius": 0.4,
        "image_url": DEFAULT_IMG,
        "reporter_ip": DEFAULT_IP,
        "status": ReportStatus.pending,
        "status_index": 1,
    },
    {
        "id": str(uuid.uuid4()),
        "reference_number": "FR-2026-017",
        "user_id": None,
        "location_text": "Lynnwood Road crossing",
        "description": "Rubbish burning under the bridge, spreading to dry grass.",
        "location_geom": "SRID=4326;POINT(28.2500 -25.7600)",
        "boundary_radius": 0.2,
        "image_url": DEFAULT_IMG,
        "reporter_ip": DEFAULT_IP,
        "status": ReportStatus.received,
        "status_index": 0,
    },
    {
        "id": str(uuid.uuid4()),
        "reference_number": "FR-2026-018",
        "user_id": "usr_20",
        "location_text": "Voortrekker Monument hillside",
        "description": "Flames visible on the southern slope from the highway.",
        "location_geom": "SRID=4326;POINT(28.1700 -25.7700)",
        "boundary_radius": 3.0,
        "image_url": DEFAULT_IMG,
        "reporter_ip": DEFAULT_IP,
        "status": ReportStatus.verified,
        "status_index": 2,
    },
]


def seed_users(db):
    inserted = {}
    for data in SEED_USERS:
        existing = db.query(User).filter(User.id == data["id"]).first()
        if existing:
            print(f" SKIP {data['email']} (already exists)")
            inserted[data["email"]] = existing
            continue

        user = User(
            id=data["id"],
            name=data["name"],
            surname=data["surname"],
            email=data["email"],
            id_number=data["id_number"],
            license_number=data["license_number"],
            hashed_password=hash_password(data["password"]),
            role=data["role"],
            is_active=True,
            is_2fa_enabled=False,
            totp_secret=None,
        )
        db.add(user)
        inserted[data["email"]] = user
        print(f" ADD {data['email']} ({data['role']})")

    db.flush()
    return inserted


def seed_role_requests(db):
    for data in SEED_ROLE_REQUESTS:
        existing = (
            db.query(RoleRequest)
            .filter(RoleRequest.request_id == data["request_id"])
            .first()
        )

        if existing:
            print(f"  SKIP  role request {data['request_id']} (already exists)")
            continue

        role_request = RoleRequest(
            request_id=data["request_id"],
            user_id=data["user_id"],
            requested_role=data["requested_role"],
            current_role=data["current_role"],
            status=data["status"],
            reviewed_by=data["reviewed_by"],
            reviewed_at=datetime.now(timezone.utc) if data["reviewed_by"] else None,
        )
        db.add(role_request)
        print(f"  ADD   role request -> {data['requested_role']} for {data['user_id']}")


def seed_fire_reports(db):
    for data in SEED_FIRE_REPORTS:
        existing = (
            db.query(FireReports)
            .filter(FireReports.reference_number == data["reference_number"])
            .first()
        )

        if existing:
            print(f"  SKIP  fire report {data['reference_number']} (already exists)")
            continue

        report = FireReports(
            id=data["id"],
            reference_number=data["reference_number"],
            user_id=data["user_id"],
            reporter_ip=data.get("reporter_ip"),
            location_text=data["location_text"],
            description=data["description"],
            image_url=data["image_url"],
            location_geom=data["location_geom"],
            boundary_radius=data["boundary_radius"],
            status=data["status"],
            status_index=data["status_index"],
        )
        db.add(report)
        print(
            f"  ADD   fire report -> {data['reference_number']} at {data['location_text']}"
        )


def seed():
    print("Creating tables if they don't exist...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("\nSeeding users...")
        seed_users(db)

        print("\nSeeding role requests...")
        seed_role_requests(db)

        print("\nSeeding fire reports...")
        seed_fire_reports(db)

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