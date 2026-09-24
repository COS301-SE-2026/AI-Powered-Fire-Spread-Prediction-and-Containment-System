import uuid
import sys
from datetime import date, datetime, timedelta, timezone
import os

from app.backend.src.dependencies.auth import hash_password
from app.backend.db import Base, SessionLocal, engine
from app.backend.src.enums.report_status import ReportStatus
from app.backend.src.enums.resource import (
    ResourceStatus,
    ResourceType,
    capacity_unit_for,
)
from app.backend.src.enums.role_request_status import RequestStatus
from app.backend.src.enums.user_role import UserRole
from app.backend.src.models.reported_fires import FireReports
from app.backend.src.models.role_request import RoleRequest
from app.backend.src.models.containment_lines import ContainmentLines
from app.backend.src.models.water_resource import WaterResource

# from models import User, RoleRequestDB, FireReportModel, ReportStatus
from app.backend.src.models.users import User

DEFAULT_PASSWORD = os.getenv("SEED_DEFAULT_PASSWORD")
ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD")

if not DEFAULT_PASSWORD:
    raise ValueError("Missing env variables for passwords")


def get_raw_password(role: str) -> str:
    if role == "admin" and ADMIN_PASSWORD:
        return ADMIN_PASSWORD
    return DEFAULT_PASSWORD


# 20 Users: 3 Admins, 5 Firefighters, 12 Users
SEED_USERS = [
    {
        "id": "usr_01",
        "email": "sipho.n@fireaway.co.za",
        "name": "Sipho",
        "surname": "Ndlovu",
        "id_number": "8505125800081",
        "role": "admin",
    },
    {
        "id": "usr_02",
        "email": "lerato.b@fireaway.co.za",
        "name": "Lerato",
        "surname": "Botha",
        "id_number": "9008234800082",
        "role": "admin",
    },
    {
        "id": "usr_03",
        "email": "johan.v@fireaway.co.za",
        "name": "Johan",
        "surname": "van der Merwe",
        "id_number": "8201145000083",
        "role": "admin",
    },
    {
        "id": "usr_04",
        "email": "thandiwe.k@fireaway.co.za",
        "name": "Thandiwe",
        "surname": "Khumalo",
        "id_number": "9302284800084",
        "role": "firefighter",
    },
    {
        "id": "usr_05",
        "email": "pieter.m@fireaway.co.za",
        "name": "Pieter",
        "surname": "Mokoena",
        "id_number": "9507115000085",
        "role": "firefighter",
    },
    {
        "id": "usr_06",
        "email": "fatima.p@fireaway.co.za",
        "name": "Fatima",
        "surname": "Patel",
        "id_number": "9804054800086",
        "role": "firefighter",
    },
    {
        "id": "usr_07",
        "email": "siyabonga.z@fireaway.co.za",
        "name": "Siyabonga",
        "surname": "Zulu",
        "id_number": "9109155000087",
        "role": "firefighter",
    },
    {
        "id": "usr_08",
        "email": "kagiso.m@fireaway.co.za",
        "name": "Kagiso",
        "surname": "Mahlangu",
        "id_number": "9412125000088",
        "role": "firefighter",
    },
    {
        "id": "usr_09",
        "email": "amahle.d@fireaway.co.za",
        "name": "Amahle",
        "surname": "Dlamini",
        "id_number": "0103144800089",
        "role": "user",
    },
    {
        "id": "usr_10",
        "email": "heinrich.k@fireaway.co.za",
        "name": "Heinrich",
        "surname": "Kruger",
        "id_number": "0005185000080",
        "role": "user",
    },
    {
        "id": "usr_11",
        "email": "zanele.m@fireaway.co.za",
        "name": "Zanele",
        "surname": "Mbatha",
        "id_number": "9906214800081",
        "role": "user",
    },
    {
        "id": "usr_12",
        "email": "ruan.v@fireaway.co.za",
        "name": "Ruan",
        "surname": "Venter",
        "id_number": "0208255000082",
        "role": "user",
    },
    {
        "id": "usr_13",
        "email": "naledi.m@fireaway.co.za",
        "name": "Naledi",
        "surname": "Moeng",
        "id_number": "9701304800083",
        "role": "user",
    },
    {
        "id": "usr_14",
        "email": "willem.c@fireaway.co.za",
        "name": "Willem",
        "surname": "Coetzee",
        "id_number": "9604125000084",
        "role": "user",
    },
    {
        "id": "usr_15",
        "email": "kgotso.b@fireaway.co.za",
        "name": "Kgotsofalang",
        "surname": "Baloyi",
        "id_number": "0309115000085",
        "role": "user",
    },
    {
        "id": "usr_16",
        "email": "bianca.n@fireaway.co.za",
        "name": "Bianca",
        "surname": "Naidoo",
        "id_number": "0107194800086",
        "role": "user",
    },
    {
        "id": "usr_17",
        "email": "lungile.n@fireaway.co.za",
        "name": "Lungile",
        "surname": "Ngcobo",
        "id_number": "9811224800087",
        "role": "user",
    },
    {
        "id": "usr_18",
        "email": "deon.s@fireaway.co.za",
        "name": "Deon",
        "surname": "Steyn",
        "id_number": "9510085000088",
        "role": "user",
    },
    {
        "id": "usr_19",
        "email": "anika.s@fireaway.co.za",
        "name": "Anika",
        "surname": "Smit",
        "id_number": "0402144800089",
        "role": "user",
    },
    {
        "id": "usr_20",
        "email": "tshepo.m@fireaway.co.za",
        "name": "Tshepo",
        "surname": "Moroka",
        "id_number": "0008165000080",
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
    {
        "name": "LC de Villiers Sports Grounds",
        "lat": -25.7480,
        "lng": 28.2435,
        "desc": "Brush fire near northern fence.",
        "radius": 0.5,
    },
    {
        "name": "Silkaatsnek Nature Reserve, Hartbeespoort",
        "lat": -25.6900,
        "lng": 27.9100,
        "desc": "Mountain ridge fire climbing towards towers.",
        "radius": 2.0,
    },
    {
        "name": "Oak Avenue Farmlands, Cullinan",
        "lat": -25.6700,
        "lng": 28.5300,
        "desc": "Grassland fire burning through dry crop residues.",
        "radius": 0.1,
    },
    {
        "name": "Rietvlei Nature Reserve, Irene",
        "lat": -25.8800,
        "lng": 28.2800,
        "desc": "Large veld fire spreading toward eastern border.",
        "radius": 3.5,
    },
    {
        "name": "Dinokeng Game Reserve North",
        "lat": -25.3800,
        "lng": 28.3800,
        "desc": "Bushveld blaze near reserve perimeter.",
        "radius": 1.0,
    },
    {
        "name": "Buffelspoort Valley, Magaliesberg",
        "lat": -25.7500,
        "lng": 27.4800,
        "desc": "Wildfire burning across steep mountain slopes.",
        "radius": 1.5,
    },
    {
        "name": "Crocodile River Banks, Brits",
        "lat": -25.6200,
        "lng": 27.7700,
        "desc": "Dense reed fire near citrus orchards.",
        "radius": 2.5,
    },
    {
        "name": "Pretoria National Botanical Garden",
        "lat": -25.7300,
        "lng": 28.2700,
        "desc": "Fire near eastern boundary wall.",
        "radius": 0.3,
    },
    {
        "name": "Roodeplaat Dam Nature Reserve",
        "lat": -25.6300,
        "lng": 28.3600,
        "desc": "Veld fire near southern picnic site.",
        "radius": 4.0,
    },
    {
        "name": "Main Road Verge, Kyalami",
        "lat": -25.9800,
        "lng": 28.0700,
        "desc": "Thick smoke near electrical sub-station.",
        "radius": 0.8,
    },
    {
        "name": "Kromdraai Slopes, Cradle of Humankind",
        "lat": -25.9700,
        "lng": 27.7600,
        "desc": "Grass fire burning along rocky slopes.",
        "radius": 0.2,
    },
    {
        "name": "Roodekrans Ridge, Krugersdorp",
        "lat": -26.0800,
        "lng": 27.8400,
        "desc": "Large grass fire causing smoke drift.",
        "radius": 1.2,
    },
    {
        "name": "Pretoria West Industrial Area",
        "lat": -25.7500,
        "lng": 28.1500,
        "desc": "Chemical smoke rising from industrial yard.",
        "radius": 0.5,
    },
    {
        "name": "Atterbury Road Verge, Pretoria East",
        "lat": -25.7900,
        "lng": 28.3100,
        "desc": "Roadside spot fire spreading into dry brush.",
        "radius": 0.1,
    },
    {
        "name": "Silver Lakes Boundary",
        "lat": -25.7600,
        "lng": 28.3500,
        "desc": "Fire in open field approaching estate wall.",
        "radius": 1.8,
    },
    {
        "name": "R21 Corridor, Serengeti North",
        "lat": -26.0200,
        "lng": 28.2700,
        "desc": "Grass fire blowing smoke across highway.",
        "radius": 0.4,
    },
    {
        "name": "M17 Open Veld, Mabopane",
        "lat": -25.5200,
        "lng": 28.0500,
        "desc": "Uncontrolled rubbish and tall grass burn.",
        "radius": 0.2,
    },
    {
        "name": "Suikerbosrand Nature Reserve, Heidelberg",
        "lat": -26.5100,
        "lng": 28.2500,
        "desc": "Massive mountain veld fire consuming open land.",
        "radius": 3.0,
    },
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
    ReportStatus.rejected: 2,
}

SEED_WATER_RESOURCES = [
    {
        "id": "res_01",
        "user_id": "usr_10",
        "resource": ResourceType.water_tank,
        "capacity": 10000,
        "status": ResourceStatus.available,
        "from_days": -30,
        "until_days": None,
        "location": "Kruger Farm, Old Warmbaths Road, Pretoria North",
        "lat": -25.6512,
        "lng": 28.1530,
        "name": "Heinrich Kruger",
        "contact": "082 555 0142",
    },
    {
        "id": "res_02",
        "user_id": "usr_12",
        "resource": ResourceType.borehole,
        "capacity": 20000,
        "status": ResourceStatus.available,
        "from_days": -14,
        "until_days": 180,
        "location": "Plot 14, Hartbeespoort",
        "lat": -25.7420,
        "lng": 27.8900,
        "name": "Ruan Venter",
        "contact": "083 555 7788",
    },
    {
        "id": "res_03",
        "user_id": "usr_14",
        "resource": ResourceType.trailer,
        "capacity": 5000,
        "status": ResourceStatus.available,
        "from_days": -7,
        "until_days": None,
        "location": "Oak Avenue Farmlands, Cullinan",
        "lat": -25.6790,
        "lng": 28.5150,
        "name": "Willem Coetzee",
        "contact": "071 555 9036",
    },
    {
        "id": "res_04",
        "user_id": "usr_09",
        "resource": ResourceType.water_tank,
        "capacity": 5000,
        "status": ResourceStatus.available,
        "from_days": -2,
        "until_days": 60,
        "location": "Main Road, Kyalami",
        "lat": -25.9850,
        "lng": 28.0600,
        "name": "Amahle Dlamini",
        "contact": "076 555 5520",
    },
    {
        "id": "res_05",
        "user_id": "usr_16",
        "resource": ResourceType.dam,
        "capacity": 120000,
        "status": ResourceStatus.available,
        "from_days": -90,
        "until_days": None,
        "location": "Farm dam near Roodeplaat Dam Nature Reserve",
        "lat": -25.6200,
        "lng": 28.3450,
        "name": "Bianca Naidoo",
        "contact": "060 555 4419",
    },
    {
        "id": "res_06",
        "user_id": "usr_18",
        "resource": ResourceType.dam,
        "capacity": 80000,
        "status": ResourceStatus.available,
        "from_days": -45,
        "until_days": 365,
        "location": "Farm dam, Suikerbosrand area, Heidelberg",
        "lat": -26.5000,
        "lng": 28.2300,
        "name": "Deon Steyn",
        "contact": "072 555 1187",
    },
    {
        "id": "res_07",
        "user_id": "usr_19",
        "resource": ResourceType.crew,
        "capacity": 6,
        "status": ResourceStatus.available,
        "from_days": -5,
        "until_days": 30,
        "location": "Roodekrans, Krugersdorp",
        "lat": -26.0900,
        "lng": 27.7900,
        "name": "Anika Smit",
        "contact": "084 555 3351",
    },
    {
        "id": "res_08",
        "user_id": "usr_05",
        "resource": ResourceType.crew,
        "capacity": 12,
        "status": ResourceStatus.dispatched,
        "from_days": -60,
        "until_days": None,
        "location": "Buffelspoort Valley, Magaliesberg",
        "lat": -25.7600,
        "lng": 27.5000,
        "name": "Magaliesberg Volunteer Fire Brigade",
        "contact": "079 555 2264",
    },
    {
        "id": "res_09",
        "user_id": "usr_08",
        "resource": ResourceType.aircraft,
        "capacity": 1500,
        "status": ResourceStatus.dispatched,
        "from_days": -20,
        "until_days": 90,
        "location": "Wonderboom Airport, Pretoria",
        "lat": -25.6540,
        "lng": 28.2240,
        "name": "Highveld Aerial Firefighting",
        "contact": "061 555 7045",
    },
    {
        "id": "res_10",
        "user_id": "usr_11",
        "resource": ResourceType.other,
        "other_resource": "Portable diesel pump with 200 m of hose",
        "other_capacity": "pumps",
        "capacity": 3,
        "status": ResourceStatus.available,
        "from_days": -10,
        "until_days": None,
        "location": "Crocodile River Banks, Brits",
        "lat": -25.6300,
        "lng": 27.7800,
        "name": "Zanele Mbatha",
        "contact": "073 555 6612",
    },
    {
        "id": "res_11",
        "user_id": "usr_13",
        "resource": ResourceType.other,
        "other_resource": "Tractor with sprayer tank",
        "other_capacity": "L sprayer tank",
        "capacity": 3000,
        "status": ResourceStatus.unavailable,
        "from_days": -25,
        "until_days": 15,
        "location": "M17 Open Veld, Mabopane",
        "lat": -25.5100,
        "lng": 28.0600,
        "name": "Naledi Moeng",
        "contact": "082 555 9958",
    },
    {
        "id": "res_12",
        "user_id": "usr_15",
        "resource": ResourceType.borehole,
        "capacity": 8000,
        "status": ResourceStatus.available,
        "from_days": -60,
        "until_days": 90,
        "location": "Dinokeng Game Reserve North",
        "lat": -25.3900,
        "lng": 28.3700,
        "name": "Kgotsofalang Baloyi",
        "contact": "078 555 2130",
    },
    {
        "id": "res_13",
        "user_id": "usr_17",
        "resource": ResourceType.trailer,
        "capacity": 2000,
        "status": ResourceStatus.available,
        "from_days": 3,
        "until_days": 30,
        "location": "Rietvlei Nature Reserve, Irene",
        "lat": -25.8850,
        "lng": 28.2700,
        "name": "Lungile Ngcobo",
        "contact": "081 555 4403",
    },
    {
        "id": "res_14",
        "user_id": "usr_20",
        "resource": ResourceType.water_tank,
        "capacity": 15000,
        "status": ResourceStatus.available,
        "from_days": -100,
        "until_days": None,
        "location": "Atterbury Road, Pretoria East",
        "lat": -25.7850,
        "lng": 28.3200,
        "name": "Tshepo Moroka",
        "contact": "066 555 8759",
    },
    {
        "id": "res_15",
        "user_id": "usr_07",
        "resource": ResourceType.crew,
        "capacity": 8,
        "status": ResourceStatus.available,
        "from_days": -1,
        "until_days": 120,
        "location": "Heidelberg, Southern Gauteng",
        "lat": -26.5040,
        "lng": 28.3560,
        "name": "Southern Gauteng Rapid Response Crew",
        "contact": "074 555 1096",
    },
    # usr_04 (firefighter)
    {
        "id": "res_16",
        "user_id": "usr_04",
        "resource": ResourceType.trailer,
        "capacity": 8000,
        "status": ResourceStatus.available,
        "from_days": -12,
        "until_days": None,
        "location": "Pretoria West Industrial Area",
        "lat": -25.7520,
        "lng": 28.1480,
        "name": "Thandiwe Khumalo",
        "contact": "062 555 3307",
    },
    {
        "id": "res_17",
        "user_id": "usr_04",
        "resource": ResourceType.other,
        "other_resource": "Class A foam concentrate stock",
        "other_capacity": "L of foam concentrate",
        "capacity": 400,
        "status": ResourceStatus.available,
        "from_days": -6,
        "until_days": 75,
        "location": "Kromdraai Slopes, Cradle of Humankind",
        "lat": -25.9700,
        "lng": 27.7600,
        "name": "Thandiwe Khumalo",
        "contact": "064 555 8812",
    },
    # usr_01 (admin)
    {
        "id": "res_18",
        "user_id": "usr_01",
        "resource": ResourceType.dam,
        "capacity": 60000,
        "status": ResourceStatus.available,
        "from_days": -75,
        "until_days": None,
        "location": "Farm dam, Cullinan",
        "lat": -25.6600,
        "lng": 28.5000,
        "name": "Sipho Ndlovu",
        "contact": "063 555 4128",
    },
    {
        "id": "res_19",
        "user_id": "usr_01",
        "resource": ResourceType.crew,
        "capacity": 5,
        "status": ResourceStatus.available,
        "from_days": -3,
        "until_days": 45,
        "location": "Kyalami, Johannesburg",
        "lat": -25.9780,
        "lng": 28.0750,
        "name": "Sipho Ndlovu",
        "contact": "065 555 7719",
    },
    # usr_20 (regular user, second and third resources)
    {
        "id": "res_20",
        "user_id": "usr_20",
        "resource": ResourceType.borehole,
        "capacity": 12000,
        "status": ResourceStatus.available,
        "from_days": -20,
        "until_days": 120,
        "location": "Silver Lakes, Pretoria East",
        "lat": -25.7620,
        "lng": 28.3520,
        "name": "Tshepo Moroka",
        "contact": "067 555 2246",
    },
    {
        "id": "res_21",
        "user_id": "usr_20",
        "resource": ResourceType.trailer,
        "capacity": 3000,
        "status": ResourceStatus.dispatched,
        "from_days": -8,
        "until_days": 10,
        "location": "Atterbury Road, Pretoria East",
        "lat": -25.7830,
        "lng": 28.3150,
        "name": "Tshepo Moroka",
        "contact": "068 555 9401",
    },
]


def seed_users(db):
    inserted = {}
    for data in SEED_USERS:
        raw_pass = get_raw_password(data["role"])
        new_hash = hash_password(raw_pass)

        existing = db.query(User).filter(User.id == data["id"]).first()
        if existing:
            existing.hashed_password = new_hash
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
            hashed_password=new_hash,
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
            db.query(FireReports).filter(FireReports.reference_number == ref).first()
        )

        if existing:
            print(f"  SKIP  fire report {ref} (already exists)")
            continue

        status = STATUS_CYCLES[(index - 1) % len(STATUS_CYCLES)]
        status_idx = STATUS_LEVEL_MAP[status]
        assigned_user = user_ids[(index - 1) % len(user_ids)]

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
        print(f"  ADD   fire report -> {ref} at {loc['name']}")
        
def seed_water_resources(db):
    today = date.today()
    
    for data in SEED_WATER_RESOURCES:
        existing = (
            db.query(WaterResource).filter(WaterResource.id == data["id"]).first()
        )
        
        if existing:
            print(f" SKIP water resource {data['id']} (already exists)")
            continue
        
        until_days = data["until_days"]
        resource = WaterResource(
            id=data["id"],
            user_id=data["user_id"],
            resource_type=data["resource"],
            other_resource=data.get("other_resource"),
            capacity=data["capacity"],
            capacity_unit=capacity_unit_for(data["resource"]),
            other_capacity_unit=data.get("other_capacity"),
            status=data["status"],
            available_from=today + timedelta(days=data["from_days"]),
            available_until=(today + timedelta(days=until_days) if until_days is not None else None),
            location_text=data["location"],
            location_geom=f"SRID=4326;POINT({data['lng']} {data['lat']})",
            name=data["name"],
            contact=data["contact"],
        )
        db.add(resource)
        print(f" ADD water resource -> {data['name']} ({data['resource'].value})")
    
    


def wipe_all_data(db):
    print(" Wiping database for a reseed")

    db.query(WaterResource).delete()
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
        
        print("\nSeeding water resources...")
        seed_water_resources(db)

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
