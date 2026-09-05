from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, auth
from ..database import get_db

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if current_user.role == models.RoleEnum.USER:
        instrument_ids = [
            i.id
            for i in db.query(models.Instrument).filter(
                models.Instrument.owner_id == current_user.id
            )
        ]
        total_instruments = len(instrument_ids)
        apps = db.query(models.Application).filter(
            models.Application.instrument_id.in_(instrument_ids or [0])
        )
        return {
            "total_instruments": total_instruments,
            "total_applications": apps.count(),
            "certificates_issued": apps.filter(
                models.Application.status == models.ApplicationStatus.CERTIFICATE_ISSUED
            ).count(),
        }

    if current_user.role == models.RoleEnum.LMO:
        apps = db.query(models.Application).filter(
            models.Application.assigned_officer_id == current_user.id
        )
        return {
            "assigned": apps.count(),
            "pending": apps.filter(
                models.Application.status.in_(
                    [models.ApplicationStatus.SCHEDULED, models.ApplicationStatus.UNDER_REVIEW]
                )
            ).count(),
            "completed": apps.filter(
                models.Application.status.in_(
                    [models.ApplicationStatus.APPROVED, models.ApplicationStatus.CERTIFICATE_ISSUED]
                )
            ).count(),
        }

    # ADMIN
    total_applications = db.query(models.Application).count()
    return {
        "total_registered_instruments": db.query(models.Instrument).count(),
        "total_applications": total_applications,
        "pending_applications": db.query(models.Application)
        .filter(
            models.Application.status.in_(
                [models.ApplicationStatus.SUBMITTED, models.ApplicationStatus.UNDER_REVIEW]
            )
        )
        .count(),
        "verified": db.query(models.Application)
        .filter(models.Application.status == models.ApplicationStatus.CERTIFICATE_ISSUED)
        .count(),
        "rejected": db.query(models.Application)
        .filter(models.Application.status == models.ApplicationStatus.REJECTED)
        .count(),
        "certificates_expiring_soon": db.query(models.Certificate)
        .filter(models.Certificate.status == "VALID")
        .count(),
    }


@router.get("/risk-score/{instrument_id}")
def risk_score(
    instrument_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Simple rule-based risk score, per the SIH problem statement suggestion."""
    verifications = (
        db.query(models.Verification)
        .join(models.Application)
        .filter(models.Application.instrument_id == instrument_id)
        .all()
    )

    score = 0
    failures = sum(1 for v in verifications if v.result == models.ResultEnum.FAIL)
    if failures > 2:
        score += 30

    instrument = db.query(models.Instrument).filter(models.Instrument.id == instrument_id).first()
    if instrument and instrument.year_of_manufacture:
        import datetime as dt

        age = dt.datetime.utcnow().year - instrument.year_of_manufacture
        if age > 10:
            score += 20

    high_deviation = any(
        v.expected_value and v.observed_value and v.tolerance
        and abs(v.observed_value - v.expected_value) > (2 * v.tolerance)
        for v in verifications
    )
    if high_deviation:
        score += 30

    level = "HIGH RISK" if score >= 60 else "MEDIUM RISK" if score >= 30 else "LOW RISK"
    return {"instrument_id": instrument_id, "risk_score": score, "risk_level": level}
