from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Household, ShoppingSession, SessionItem
from ..schemas import ShoppingSessionResponse
from ..auth import get_current_household

router = APIRouter(prefix="/api", tags=["sessions"])


@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    session = db.query(ShoppingSession).filter(
        ShoppingSession.id == session_id,
        ShoppingSession.household_id == household.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db.query(SessionItem).filter(SessionItem.session_id == session.id).delete()
    db.delete(session)
    db.commit()
    return {"ok": True}


@router.get("/sessions", response_model=list[ShoppingSessionResponse])
def list_sessions(
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    return db.query(ShoppingSession).filter(
        ShoppingSession.completed_at != None,
        ShoppingSession.household_id == household.id
    ).order_by(ShoppingSession.completed_at.desc()).all()
