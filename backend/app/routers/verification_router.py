import datetime as dt
import os
import qrcode

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/verification", tags=["Verification"])

QR_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "static", "qr")
os.makedirs(QR_DIR, exist_ok=True)


def _generate_certificate_number(db: Session) -> str:
    year = dt.datetime.utcnow().year
    count = db.query(models.Certificate).count() + 1
    return f"CERT-TN-{year}-{4000 + count}"


@router.post("/{application_id}/submit", response_model=schemas.VerificationOut)
def submit_verification(
    application_id: int,
    payload: schemas.VerificationSubmit,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_role("LMO", "ADMIN")),
):
    application = db.query(models.Application).filter(models.Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    deviation = abs(payload.observed_value - payload.expected_value)
    result = models.ResultEnum.PASS_ if deviation <= payload.tolerance else models.ResultEnum.FAIL

    verification = models.Verification(
        application_id=application.id,
        officer_id=current_user.id,
        verification_date=dt.datetime.utcnow(),
        expected_value=payload.expected_value,
        observed_value=payload.observed_value,
        tolerance=payload.tolerance,
        result=result,
        remarks=payload.remarks,
    )
    db.add(verification)

    application.status = (
        models.ApplicationStatus.APPROVED
        if result == models.ResultEnum.PASS_
        else models.ApplicationStatus.REJECTED
    )
    db.commit()
    db.refresh(verification)

    if result == models.ResultEnum.PASS_:
        _issue_certificate(db, verification)

    return verification


def _issue_certificate(db: Session, verification: models.Verification):
    cert_number = _generate_certificate_number(db)
    issue_date = dt.datetime.utcnow()
    expiry_date = issue_date + dt.timedelta(days=365)

    certificate = models.Certificate(
        verification_id=verification.id,
        certificate_number=cert_number,
        issue_date=issue_date,
        expiry_date=expiry_date,
        status="VALID",
    )
    db.add(certificate)
    db.commit()
    db.refresh(certificate)

    verification.application.status = models.ApplicationStatus.CERTIFICATE_ISSUED
    db.commit()

    # Generate QR code pointing to the public verification page
    verify_url = f"http://localhost:5173/verify/{certificate.qr_token}"
    img = qrcode.make(verify_url)
    img.save(os.path.join(QR_DIR, f"{certificate.qr_token}.png"))

    return certificate
