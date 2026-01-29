from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Household
from ..schemas import HouseholdJoin, HouseholdResponse, Token
from ..auth import (
    create_access_token,
    generate_household_token,
    get_current_household,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/create", response_model=Token)
def create_household(db: Session = Depends(get_db)):
    token = generate_household_token()
    household = Household(token=token)
    db.add(household)
    db.commit()
    db.refresh(household)
    access_token = create_access_token(data={"sub": str(household.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/join", response_model=Token)
def join_household(data: HouseholdJoin, db: Session = Depends(get_db)):
    household = db.query(Household).filter(Household.token == data.token.upper().strip()).first()
    if not household:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Household not found"
        )
    access_token = create_access_token(data={"sub": str(household.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=HouseholdResponse)
def get_me(current_household: Annotated[Household, Depends(get_current_household)]):
    return current_household
