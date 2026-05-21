import uuid
from datetime import datetime, timezone

from db import engine, SessionLocal, Base
from models import User, RoleRequestDB
from auth import hash_password

SEED_USERS = [
    {
        "id": f"usr_{uuid.uuid4().hex[:8]}",
        "email": "admin@fireaway.co.za",
        "password": "Admin1234!",
        "name": "Admin",
        "surname": "User",
        "id_number": "0000000000000",
        "license_number": None,
        "role": "Admin",
    },
    {
        "id": f"usr_{uuid.uuid4().hex[:8]}",
        "email": "dispatcher@fireaway.co.za",
        "password": "Dispatch1234!",
        "name": "Sarah",
        "surname": "Nkosi",
        "id_number": "9001015800085",
        "license_number": None,
        "role": "Dispatcher",
    },
    {
        "id": f"usr_{uuid.uuid4().hex[:8]}",
        "email": "driver@fireaway.co.za",
        "password": "Driver1234!",
        "name": "Thabo",
        "surname": "Dlamini",
        "id_number": "8805125900083",
        "license_number": "GP-2024-00123",
        "role": "User",
    },
]

SEED_ROLE_REQUESTS = [
    {
        "user_email": "driver@fireaway.co.za",
        "role": "Dispatcher",
        "firefighter_license_id": "GP-2024-00123",
        "status": "pending",
    },
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
            hash_password=data["hash_password"],
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

