import uuid
import sys
from datetime import datetime, timedelta, timezone

from dependencies.auth import hash_password
from db import Base, SessionLocal, engine
from enums.report_status import ReportStatus
from enums.role_request_status import RequestStatus
from enums.user_role import UserRole
from models.reported_fires import FireReports
from models.role_request import RoleRequest
from models.containment_lines import ContainmentLines

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

# 18 spread out realistic locations across Guateng and North West for fires
REGIONAL_LOCATIONS = [
    {"name": "LC de Villiers Sports Grounds", "lat": -25.7480, "lng": 28.2435, "desc": "Brush fire near northern fence.", "radius": 0.5},
    {"name": "Silkaatsnek Nature Reserve, Hartbeespoort", "lat": -25.6900, "lng": 27.9100, "desc": "Mountain ridge fire climbing towards towers.", "radius": 2.0},
    {"name": "Oak Avenue Farmlands, Cullinan", "lat": -25.6700, "lng": 28.5300, "desc": "Grassland fire burning through dry crop residues.", "radius": 0.1},
    {"name": "Rietvlei Nature Reserve, Irene", "lat": -25.8800, "lng": 28.2800, "desc": "Large veld fire spreading toward eastern border.", "radius": 3.5},
    {"name": "Dinokeng Game Reserve North", "lat": -25.3800, "lng": 28.3800, "desc": "Bushveld blaze near reserve perimeter.", "radius": 1.0},
    {"name": "Buffelspoort Valley, Magaliesberg", "lat": -25.7500, "lng": 27.4800, "desc": "Wildfire burning across steep mountain slopes.", "radius": 1.5},
    {"name": "Crocodile River Banks, Brits", "lat": -25.6200, "lng": 27.7700, "desc": "Dense reed fire near citrus orchards.", "radius": 2.5},
    {"name": "Pretoria National Botanical Garden", "lat": -25.7300, "lng": 28.2700, "desc": "Fire near eastern boundary wall.", "radius": 0.3},
    {"name": "Roodeplaat Dam Nature Reserve", "lat": -25.6300, "lng": 28.3600, "desc": "Veld fire near southern picnic site.", "radius": 4.0},
    {"name": "Main Road Verge, Kyalami", "lat": -25.9800, "lng": 28.0700, "desc": "Thick smoke near electrical sub-station.", "radius": 0.8},
    {"name": "Kromdraai Slopes, Cradle of Humankind", "lat": -25.9700, "lng": 27.7600, "desc": "Grass fire burning along rocky slopes.", "radius": 0.2},
    {"name": "Roodekrans Ridge, Krugersdorp", "lat": -26.0800, "lng": 27.8400, "desc": "Large grass fire causing smoke drift.", "radius": 1.2},
    {"name": "Pretoria West Industrial Area", "lat": -25.7500, "lng": 28.1500, "desc": "Chemical smoke rising from industrial yard.", "radius": 0.5},
    {"name": "Atterbury Road Verge, Pretoria East", "lat": -25.7900, "lng": 28.3100, "desc": "Roadside spot fire spreading into dry brush.", "radius": 0.1},
    {"name": "Silver Lakes Boundary", "lat": -25.7600, "lng": 28.3500, "desc": "Fire in open field approaching estate wall.", "radius": 1.8},
    {"name": "R21 Corridor, Serengeti North", "lat": -26.0200, "lng": 28.2700, "desc": "Grass fire blowing smoke across highway.", "radius": 0.4},
    {"name": "M17 Open Veld, Mabopane", "lat": -25.5200, "lng": 28.0500, "desc": "Uncontrolled rubbish and tall grass burn.", "radius": 0.2},
    {"name": "Suikerbosrand Nature Reserve, Heidelberg", "lat": -26.5100, "lng": 28.2500, "desc": "Massive mountain veld fire consuming open land.", "radius": 3.0},
]

STATUS_CYCLES = [
    ReportStatus.received,
    ReportStatus.pending,
    ReportStatus.verified,
    ReportStatus.rejected,
]

STATUS_LEVEL_MAP = {
    ReportStatus.received: 0,
    ReportStatus.pending: 1,
    ReportStatus.verified: 2,
    ReportStatus.rejected: 2
}


def seed_users(db):
    inserted = {}
    for data in SEED_USERS:
        existing = db.query(User).filter(User.id == data["id"]).first()
        if existing:
            if existing.role != data["role"]:
                existing.role = data["role"]
                print(f" UPDATE {data['email']} role -> {data['role']}")
            else:
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
    user_ids = [f"usr_{i:02d}" for i in range(1, 21)] + [None, None, None]

    for index, loc in enumerate(REGIONAL_LOCATIONS, start=1):
        ref = f"FR-2026-{index:03d}"

        existing = (
            db.query(FireReports)
            .filter(FireReports.reference_number == ref)
            .first()
        )

        if existing:
            print(f"  SKIP  fire report {ref} (already exists)")
            continue

        status = STATUS_CYCLES[(index - 1) % len(STATUS_CYCLES)]
        status_idx = STATUS_LEVEL_MAP[status]
        assigned_user = user_ids[(index-1) % len(user_ids)]

        report = FireReports(
            id=str(uuid.uuid4()),
            reference_number=ref,
            user_id=assigned_user,
            reporter_ip=DEFAULT_IP,
            location_text=loc["name"],
            description=loc["desc"],
            image_url=DEFAULT_IMG,
            location_geom=f"SRID=4326;POINT({loc['lng']} {loc['lat']})",
            boundary_radius=loc["radius"],
            status=status,
            status_index=status_idx,
        )
        db.add(report)
        print(
            f"  ADD   fire report -> {ref} at {loc['name']}"
        )

def wipe_all_data(db):
    print(" Wiping database for a reseed")

    db.query(ContainmentLines).delete()
    db.query(FireReports).delete()
    db.query(RoleRequest).delete()
    db.query(User).delete()
    db.flush()
    print("All databases cleared")

def seed(reseed: bool = False):
    print("Creating tables if they don't exist...")

    db = SessionLocal()
    try:
        if reseed:
            wipe_all_data(db)
        
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
    is_reseed = "--reseed" in sys.argv
    seed(reseed=is_reseed)
