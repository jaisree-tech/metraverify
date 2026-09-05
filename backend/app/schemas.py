import datetime as dt
from typing import Optional
from pydantic import BaseModel, EmailStr

from .models import RoleEnum, ApplicationStatus, ResultEnum


# ---------- Auth / Users ----------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    address: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str]
    role: RoleEnum
    address: Optional[str]

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Instruments ----------
class InstrumentCreate(BaseModel):
    instrument_type: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    capacity: Optional[str] = None
    location: Optional[str] = None
    year_of_manufacture: Optional[int] = None


class InstrumentOut(InstrumentCreate):
    id: int
    registration_id: str
    owner_id: int
    created_at: dt.datetime

    class Config:
        from_attributes = True


# ---------- Applications ----------
class ApplicationCreate(BaseModel):
    instrument_id: int
    application_type: str = "New Verification"
    preferred_date: Optional[dt.datetime] = None


class ApplicationOut(BaseModel):
    id: int
    application_number: str
    instrument_id: int
    application_type: str
    status: ApplicationStatus
    preferred_date: Optional[dt.datetime]
    assigned_officer_id: Optional[int]
    submitted_date: dt.datetime

    class Config:
        from_attributes = True


class AssignOfficer(BaseModel):
    officer_id: int


# ---------- Verification ----------
class VerificationSubmit(BaseModel):
    expected_value: float
    observed_value: float
    tolerance: float
    remarks: Optional[str] = None


class VerificationOut(BaseModel):
    id: int
    application_id: int
    officer_id: Optional[int]
    verification_date: Optional[dt.datetime]
    expected_value: Optional[float]
    observed_value: Optional[float]
    tolerance: Optional[float]
    result: Optional[ResultEnum]
    remarks: Optional[str]

    class Config:
        from_attributes = True


# ---------- Certificates ----------
class CertificateOut(BaseModel):
    id: int
    certificate_number: str
    qr_token: str
    issue_date: dt.datetime
    expiry_date: dt.datetime
    status: str

    class Config:
        from_attributes = True


class PublicCertificateOut(BaseModel):
    certificate_number: str
    instrument_type: str
    status: str
    issue_date: dt.datetime
    expiry_date: dt.datetime
