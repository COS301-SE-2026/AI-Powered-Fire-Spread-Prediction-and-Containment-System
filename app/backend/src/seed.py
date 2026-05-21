import uuid
from datetime import datetime, timezone

from db import engine, SessionLocal, Base
from models import User, RoleRequestDB
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

def seed():
    print("Creating tables if they don't exist...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("\nWiping old data...")
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

