import enum
import uuid
import datetime as dt

from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Enum, Text, Float, Boolean
)
from sqlalchemy.orm import relationship

from .database import Base


class RoleEnum(str, enum.Enum):
    USER = "USER"
    LMO = "LMO"
    ADMIN = "ADMIN"


class ApplicationStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    SCHEDULED = "SCHEDULED"
    VERIFICATION_IN_PROGRESS = "VERIFICATION_IN_PROGRESS"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CERTIFICATE_ISSUED = "CERTIFICATE_ISSUED"


class ResultEnum(str, enum.Enum):
    PASS_ = "PASS"
    FAIL = "FAIL"
    REQUIRES_CORRECTION = "REQUIRES_CORRECTION"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    phone = Column(String(20))
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.USER, nullable=False)
    address = Column(String(255))
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    instruments = relationship("Instrument", back_populates="owner")


class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(String(50), unique=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    instrument_type = Column(String(100), nullable=False)
    manufacturer = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100))
    capacity = Column(String(50))
    location = Column(String(150))
    year_of_manufacture = Column(Integer)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    owner = relationship("User", back_populates="instruments")
    applications = relationship("Application", back_populates="instrument")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    application_number = Column(String(50), unique=True, index=True)
    instrument_id = Column(Integer, ForeignKey("instruments.id"))
    application_type = Column(String(50), default="New Verification")
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.SUBMITTED)
    preferred_date = Column(DateTime, nullable=True)
    assigned_officer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    submitted_date = Column(DateTime, default=dt.datetime.utcnow)

    instrument = relationship("Instrument", back_populates="applications")
    verification = relationship("Verification", back_populates="application", uselist=False)


class Verification(Base):
    __tablename__ = "verifications"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), unique=True)
    officer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verification_date = Column(DateTime, nullable=True)
    expected_value = Column(Float, nullable=True)
    observed_value = Column(Float, nullable=True)
    tolerance = Column(Float, nullable=True)
    result = Column(Enum(ResultEnum), nullable=True)
    remarks = Column(Text, nullable=True)

    application = relationship("Application", back_populates="verification")
    certificate = relationship("Certificate", back_populates="verification", uselist=False)


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    verification_id = Column(Integer, ForeignKey("verifications.id"), unique=True)
    certificate_number = Column(String(50), unique=True, index=True)
    qr_token = Column(String(64), unique=True, index=True, default=lambda: uuid.uuid4().hex)
    issue_date = Column(DateTime, default=dt.datetime.utcnow)
    expiry_date = Column(DateTime)
    status = Column(String(20), default="VALID")

    verification = relationship("Verification", back_populates="certificate")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String(255))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
