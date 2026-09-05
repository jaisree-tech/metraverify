"""
Run this once after the backend is set up, to create a default ADMIN login.

Usage:
    python seed_admin.py

Default login created:
    email:    admin@metraverify.com
    password: Admin@123
"""
from app.database import SessionLocal, engine
from app import models, auth

models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

existing = db.query(models.User).filter(models.User.email == "admin@metraverify.com").first()
if existing:
    print("Admin user already exists.")
else:
    admin = models.User(
        name="System Admin",
        email="admin@metraverify.com",
        phone="0000000000",
        password_hash=auth.hash_password("Admin@123"),
        role=models.RoleEnum.ADMIN,
        address="HQ",
    )
    db.add(admin)
    db.commit()
    print("Admin user created:")
    print("  email:    admin@metraverify.com")
    print("  password: Admin@123")

db.close()
