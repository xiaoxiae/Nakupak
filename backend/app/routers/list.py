from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from ..database import get_db
from ..models import Household, Item, ShoppingListItem, Recipe, RecipeItem, SessionItem
from ..schemas import (
    ShoppingListItemCreate, ShoppingListItemUpdate, ShoppingListItemResponse,
    AddItemsRequest, BulkIdsRequest, PoolItemResponse, ItemResponse
)
from ..auth import get_current_household
from ..websocket import broadcast_update

router = APIRouter(prefix="/api", tags=["list"])


@router.get("/list", response_model=list[ShoppingListItemResponse])
def get_shopping_list(
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    return db.query(ShoppingListItem).filter(
        ShoppingListItem.household_id == household.id
    ).all()


@router.post("/list/add", response_model=list[ShoppingListItemResponse])
def add_items_to_list(
    request: AddItemsRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    added_items = []
    for item_data in request.items:
        existing = db.query(ShoppingListItem).filter(
            ShoppingListItem.item_id == item_data.item_id,
            ShoppingListItem.household_id == household.id
        ).first()

        if existing:
            existing.quantity += item_data.quantity
            db.commit()
            db.refresh(existing)
            added_items.append(existing)
        else:
            new_item = ShoppingListItem(
                item_id=item_data.item_id,
                quantity=item_data.quantity,
                household_id=household.id
            )
            db.add(new_item)
            db.commit()
            db.refresh(new_item)
            added_items.append(new_item)

    background_tasks.add_task(broadcast_update, household.id, "list_updated", {})
    return added_items


@router.put("/list/{list_item_id}", response_model=ShoppingListItemResponse)
def update_list_item(
    list_item_id: int,
    update: ShoppingListItemUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    item = db.query(ShoppingListItem).filter(
        ShoppingListItem.id == list_item_id,
        ShoppingListItem.household_id == household.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="List item not found")

    item.quantity = update.quantity
    db.commit()
    db.refresh(item)
    background_tasks.add_task(broadcast_update, household.id, "list_updated", {})
    return item


@router.delete("/list/{list_item_id}")
def remove_from_list(
    list_item_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    item = db.query(ShoppingListItem).filter(
        ShoppingListItem.id == list_item_id,
        ShoppingListItem.household_id == household.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="List item not found")

    db.delete(item)
    db.commit()
    background_tasks.add_task(broadcast_update, household.id, "list_updated", {})
    return {"ok": True}


@router.post("/list/remove")
def bulk_remove_from_list(
    request: BulkIdsRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    deleted = db.query(ShoppingListItem).filter(
        ShoppingListItem.id.in_(request.ids),
        ShoppingListItem.household_id == household.id
    ).delete(synchronize_session=False)
    db.commit()
    background_tasks.add_task(broadcast_update, household.id, "list_updated", {})
    return {"ok": True, "deleted": deleted}


@router.delete("/list")
def clear_list(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    deleted = db.query(ShoppingListItem).filter(
        ShoppingListItem.household_id == household.id
    ).delete(synchronize_session=False)
    db.commit()
    background_tasks.add_task(broadcast_update, household.id, "list_updated", {})
    return {"ok": True, "deleted": deleted}


@router.post("/list/add-recipe/{recipe_id}", response_model=list[ShoppingListItemResponse])
def add_recipe_to_list(
    recipe_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    recipe = db.query(Recipe).filter(
        Recipe.id == recipe_id,
        Recipe.household_id == household.id
    ).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    added_items = []
    for recipe_item in recipe.recipe_items:
        if not recipe_item.item:
            continue
        existing = db.query(ShoppingListItem).filter(
            ShoppingListItem.item_id == recipe_item.item_id,
            ShoppingListItem.household_id == household.id
        ).first()

        if existing:
            existing.quantity += recipe_item.quantity
            existing.from_recipe_id = recipe_id
            db.commit()
            db.refresh(existing)
            added_items.append(existing)
        else:
            new_item = ShoppingListItem(
                item_id=recipe_item.item_id,
                quantity=recipe_item.quantity,
                household_id=household.id,
                from_recipe_id=recipe_id
            )
            db.add(new_item)
            db.commit()
            db.refresh(new_item)
            added_items.append(new_item)

    background_tasks.add_task(broadcast_update, household.id, "list_updated", {})
    return added_items


@router.get("/pool", response_model=list[PoolItemResponse])
def get_pool(
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)

    items = db.query(Item).filter(Item.household_id == household.id).all()
    pool_items = []

    for item in items:
        frequency = db.query(SessionItem).filter(
            SessionItem.item_id == item.id,
            SessionItem.checked == True
        ).count()

        last_session_item = db.query(SessionItem).filter(
            SessionItem.item_id == item.id,
            SessionItem.checked_at != None
        ).order_by(SessionItem.checked_at.desc()).first()

        last_added = last_session_item.checked_at if last_session_item else None

        recency_score = 0.0
        if last_added and last_added > thirty_days_ago:
            days_ago = (now - last_added).days
            recency_score = max(0, (30 - days_ago) / 30)

        frequency_score = min(frequency / 10, 1.0)
        score = (recency_score * 0.4) + (frequency_score * 0.6)

        if frequency > 0 or last_added:
            pool_items.append(PoolItemResponse(
                item=ItemResponse.model_validate(item),
                score=score,
                frequency=frequency,
                last_added=last_added
            ))

    pool_items.sort(key=lambda x: x.score, reverse=True)
    return pool_items[:50]
