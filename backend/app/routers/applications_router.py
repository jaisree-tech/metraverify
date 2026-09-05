import datetime as dt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/applications", tags=["Applications"])


def _generate_application_number(db: Session) -> str:
    count = db.query(models.Application).count() + 1
    return f"APP-{10000 + count}"


@router.post("/", response_model=schemas.ApplicationOut)
def submit_application(
    payload: schemas.ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    instrument = (
        db.query(models.Instrument)
        .filter(models.Instrument.id == payload.instrument_id)
        .first()
    )
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")
    if instrument.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your instrument")

    application = models.Application(
        application_number=_generate_application_number(db),
        instrument_id=payload.instrument_id,
        application_type=payload.application_type,
        preferred_date=payload.preferred_date,
        status=models.ApplicationStatus.SUBMITTED,
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/", response_model=list[schemas.ApplicationOut])
def list_applications(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    q = db.query(models.Application)
    if current_user.role == models.RoleEnum.USER:
        q = q.join(models.Instrument).filter(models.Instrument.owner_id == current_user.id)
    elif current_user.role == models.RoleEnum.LMO:
        q = q.filter(models.Application.assigned_officer_id == current_user.id)
    # ADMIN sees everything
    return q.all()


@router.post("/{application_id}/assign", response_model=schemas.ApplicationOut)
def assign_officer(
    application_id: int,
    payload: schemas.AssignOfficer,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_role("ADMIN")),
):
    application = db.query(models.Application).filter(models.Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    officer = db.query(models.User).filter(
        models.User.id == payload.officer_id, models.User.role == models.RoleEnum.LMO
    ).first()
    if not officer:
        raise HTTPException(status_code=404, detail="Officer not found")

    application.assigned_officer_id = officer.id
    application.status = models.ApplicationStatus.SCHEDULED
    db.commit()
    db.refresh(application)
    return application


@router.get("/{application_id}", response_model=schemas.ApplicationOut)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    application = db.query(models.Application).filter(models.Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application
