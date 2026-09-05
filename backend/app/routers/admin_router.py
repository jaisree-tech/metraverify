from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=list[schemas.UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_role("ADMIN")),
):
    return db.query(models.User).all()


@router.post("/users/{user_id}/make-officer", response_model=schemas.UserOut)
def make_officer(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_role("ADMIN")),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.role = models.RoleEnum.LMO
        db.commit()
        db.refresh(user)
    return user
