from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import get_db
from ..models import Household, ShoppingListItem, ShoppingSession, SessionItem
from ..schemas import ShoppingSessionResponse
from ..auth import get_current_household

router = APIRouter(prefix="/api", tags=["sessions"])


def get_active_session(db: Session, household_id: int) -> ShoppingSession | None:
    return db.query(ShoppingSession).filter(
        ShoppingSession.completed_at == None,
        ShoppingSession.household_id == household_id
    ).first()


@router.post("/session/start", response_model=ShoppingSessionResponse)
def start_session(
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    active = get_active_session(db, household.id)
    if active:
        return active

    session = ShoppingSession(household_id=household.id)
    db.add(session)
    db.commit()
    db.refresh(session)

    list_items = db.query(ShoppingListItem).filter(
        ShoppingListItem.household_id == household.id
    ).all()
    for list_item in list_items:
        session_item = SessionItem(
            session_id=session.id,
            item_id=list_item.item_id,
            item_name=list_item.item.name,
            quantity=list_item.quantity
        )
        db.add(session_item)

    db.commit()
    db.refresh(session)
    return session


@router.get("/session/active", response_model=ShoppingSessionResponse | None)
def get_active(
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    return get_active_session(db, household.id)


@router.put("/session/check/{session_item_id}")
def toggle_check(
    session_item_id: int,
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    item = db.query(SessionItem).join(ShoppingSession).filter(
        SessionItem.id == session_item_id,
        ShoppingSession.household_id == household.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Session item not found")

    item.checked = not item.checked
    item.checked_at = datetime.utcnow() if item.checked else None
    db.commit()
    db.refresh(item)
    return {"checked": item.checked, "checked_at": item.checked_at}


@router.post("/session/complete", response_model=ShoppingSessionResponse)
def complete_session(
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    session = get_active_session(db, household.id)
    if not session:
        raise HTTPException(status_code=404, detail="No active session")

    session.completed_at = datetime.utcnow()

    # Get all checked item IDs from the session
    checked_item_ids = {
        si.item_id for si in session.session_items if si.checked
    }

    # Only delete shopping list items that were checked off
    if checked_item_ids:
        db.query(ShoppingListItem).filter(
            ShoppingListItem.item_id.in_(checked_item_ids),
            ShoppingListItem.household_id == household.id
        ).delete(synchronize_session=False)

    db.commit()
    db.refresh(session)
    return session


@router.delete("/session/active")
def abort_session(
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    """Abort the active session - all items return to shopping list."""
    session = get_active_session(db, household.id)
    if not session:
        raise HTTPException(status_code=404, detail="No active session")

    # Delete all session items first
    db.query(SessionItem).filter(SessionItem.session_id == session.id).delete()

    # Delete the session
    db.delete(session)
    db.commit()

    return {"ok": True}


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
