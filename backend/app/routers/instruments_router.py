import datetime as dt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/instruments", tags=["Instruments"])


def _generate_registration_id(db: Session) -> str:
    year = dt.datetime.utcnow().year
    count = db.query(models.Instrument).count() + 1
    return f"INS-TN-{year}-{count:06d}"


@router.post("/", response_model=schemas.InstrumentOut)
def add_instrument(
    payload: schemas.InstrumentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    instrument = models.Instrument(
        registration_id=_generate_registration_id(db),
        owner_id=current_user.id,
        **payload.dict(),
    )
    db.add(instrument)
    db.commit()
    db.refresh(instrument)
    return instrument


@router.get("/", response_model=list[schemas.InstrumentOut])
def list_my_instruments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if current_user.role == models.RoleEnum.ADMIN:
        return db.query(models.Instrument).all()
    return (
        db.query(models.Instrument)
        .filter(models.Instrument.owner_id == current_user.id)
        .all()
    )


@router.get("/{instrument_id}", response_model=schemas.InstrumentOut)
def get_instrument(
    instrument_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    instrument = db.query(models.Instrument).filter(models.Instrument.id == instrument_id).first()
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")
    if instrument.owner_id != current_user.id and current_user.role not in (
        models.RoleEnum.ADMIN,
        models.RoleEnum.LMO,
    ):
        raise HTTPException(status_code=403, detail="Not allowed")
    return instrument
