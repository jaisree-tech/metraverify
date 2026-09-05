from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/certificates", tags=["Certificates"])


@router.get("/", response_model=list[schemas.CertificateOut])
def my_certificates(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    q = (
        db.query(models.Certificate)
        .join(models.Verification)
        .join(models.Application)
        .join(models.Instrument)
    )
    if current_user.role == models.RoleEnum.USER:
        q = q.filter(models.Instrument.owner_id == current_user.id)
    return q.all()


@router.get("/verify/{qr_token}", response_model=schemas.PublicCertificateOut)
def verify_certificate(qr_token: str, db: Session = Depends(get_db)):
    """Public endpoint - no login required. Scanned via QR code."""
    certificate = (
        db.query(models.Certificate)
        .filter(models.Certificate.qr_token == qr_token)
        .first()
    )
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found or invalid")

    instrument = certificate.verification.application.instrument
    return schemas.PublicCertificateOut(
        certificate_number=certificate.certificate_number,
        instrument_type=instrument.instrument_type,
        status=certificate.status,
        issue_date=certificate.issue_date,
        expiry_date=certificate.expiry_date,
    )
