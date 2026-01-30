from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Household, ShoppingSession, SessionItem, ShoppingListItem
from ..schemas import ShoppingSessionResponse, SessionItemResponse
from ..auth import get_current_household

router = APIRouter(prefix="/api", tags=["sessions"])


@router.post("/session/start", response_model=ShoppingSessionResponse)
def start_session(
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    active = db.query(ShoppingSession).filter(
        ShoppingSession.household_id == household.id,
        ShoppingSession.completed_at == None,
    ).first()
    if active:
        return active

    session = ShoppingSession(household_id=household.id)
    db.add(session)
    db.flush()

    list_items = db.query(ShoppingListItem).filter(
        ShoppingListItem.household_id == household.id
    ).all()
    for li in list_items:
        si = SessionItem(
            session_id=session.id,
            item_id=li.item_id,
            item_name=li.item.name,
            quantity=li.quantity,
            unit=li.unit,
        )
        db.add(si)

    db.commit()
    db.refresh(session)
    return session


@router.get("/session/active")
def get_active_session(
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    active = db.query(ShoppingSession).filter(
        ShoppingSession.household_id == household.id,
        ShoppingSession.completed_at == None,
    ).first()
    if active is None:
        return JSONResponse(content=None)
    return ShoppingSessionResponse.model_validate(active).model_dump(mode="json")


@router.put("/session/check/{session_item_id}")
def toggle_session_check(
    session_item_id: int,
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    si = db.query(SessionItem).join(ShoppingSession).filter(
        SessionItem.id == session_item_id,
        ShoppingSession.household_id == household.id,
    ).first()
    if not si:
        raise HTTPException(status_code=404, detail="Session item not found")

    if si.checked:
        si.checked = False
        si.checked_at = None
    else:
        si.checked = True
        si.checked_at = datetime.utcnow()

    db.commit()
    db.refresh(si)
    return {"checked": si.checked, "checked_at": si.checked_at.isoformat() if si.checked_at else None}


@router.post("/session/complete", response_model=ShoppingSessionResponse)
def complete_session(
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    active = db.query(ShoppingSession).filter(
        ShoppingSession.household_id == household.id,
        ShoppingSession.completed_at == None,
    ).first()
    if not active:
        raise HTTPException(status_code=404, detail="No active session")

    active.completed_at = datetime.utcnow()

    checked_item_ids = [
        si.item_id for si in active.session_items
        if si.checked and si.item_id is not None
    ]
    if checked_item_ids:
        db.query(ShoppingListItem).filter(
            ShoppingListItem.item_id.in_(checked_item_ids),
            ShoppingListItem.household_id == household.id,
        ).delete(synchronize_session=False)

    db.commit()
    db.refresh(active)
    return active


@router.delete("/session/active")
def abort_session(
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    active = db.query(ShoppingSession).filter(
        ShoppingSession.household_id == household.id,
        ShoppingSession.completed_at == None,
    ).first()
    if not active:
        raise HTTPException(status_code=404, detail="No active session")

    db.query(SessionItem).filter(SessionItem.session_id == active.id).delete()
    db.delete(active)
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
