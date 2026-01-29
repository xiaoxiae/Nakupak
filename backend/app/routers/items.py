from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Household, Category, Item, ShoppingListItem, RecipeItem, SessionItem
from ..schemas import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    ItemCreate, ItemUpdate, ItemResponse, MergeItemsRequest,
    BulkIdsRequest, BulkSetCategoryRequest
)
from ..auth import get_current_household
from ..utils import strip_emoji

router = APIRouter(prefix="/api", tags=["items"])


@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    return sorted(
        db.query(Category).filter(Category.household_id == household.id).all(),
        key=lambda c: strip_emoji(c.name)
    )


@router.post("/categories", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    db_category = Category(**category.model_dump(), household_id=household.id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    db_category = db.query(Category).filter(
        Category.id == category_id,
        Category.household_id == household.id
    ).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = category.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)

    db.commit()
    db.refresh(db_category)
    return db_category


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    db_category = db.query(Category).filter(
        Category.id == category_id,
        Category.household_id == household.id
    ).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(db_category)
    db.commit()
    return {"ok": True}


@router.get("/items", response_model=list[ItemResponse])
def list_items(
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    return sorted(
        db.query(Item).filter(Item.household_id == household.id).all(),
        key=lambda i: strip_emoji(i.name)
    )


@router.post("/items", response_model=ItemResponse)
def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    db_item = Item(**item.model_dump(), household_id=household.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/items/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: int,
    item: ItemUpdate,
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    db_item = db.query(Item).filter(
        Item.id == item_id,
        Item.household_id == household.id
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = item.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    db_item = db.query(Item).filter(
        Item.id == item_id,
        Item.household_id == household.id
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(db_item)
    db.commit()
    return {"ok": True}


@router.post("/items/set-category")
def bulk_set_category(
    request: BulkSetCategoryRequest,
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    if request.category_id is not None:
        category = db.query(Category).filter(
            Category.id == request.category_id,
            Category.household_id == household.id
        ).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    updated = db.query(Item).filter(
        Item.id.in_(request.item_ids),
        Item.household_id == household.id
    ).update({"category_id": request.category_id}, synchronize_session=False)
    db.commit()
    return {"ok": True, "updated": updated}


@router.post("/items/delete")
def bulk_delete_items(
    request: BulkIdsRequest,
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    deleted = db.query(Item).filter(
        Item.id.in_(request.ids),
        Item.household_id == household.id
    ).delete(synchronize_session=False)
    db.commit()
    return {"ok": True, "deleted": deleted}


@router.post("/items/{target_id}/merge", response_model=ItemResponse)
def merge_items(
    target_id: int,
    request: MergeItemsRequest,
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    target_item = db.query(Item).filter(
        Item.id == target_id,
        Item.household_id == household.id
    ).first()
    if not target_item:
        raise HTTPException(status_code=404, detail="Target item not found")

    source_ids = [sid for sid in request.source_ids if sid != target_id]
    if not source_ids:
        return target_item

    db.query(ShoppingListItem).filter(ShoppingListItem.item_id.in_(source_ids)).update(
        {"item_id": target_id}, synchronize_session=False
    )
    db.query(RecipeItem).filter(RecipeItem.item_id.in_(source_ids)).update(
        {"item_id": target_id}, synchronize_session=False
    )
    db.query(SessionItem).filter(SessionItem.item_id.in_(source_ids)).update(
        {"item_id": target_id}, synchronize_session=False
    )

    db.query(Item).filter(Item.id.in_(source_ids)).delete(synchronize_session=False)

    db.commit()
    db.refresh(target_item)
    return target_item
