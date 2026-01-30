from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Household, Recipe, RecipeItem
from ..schemas import RecipeCreate, RecipeUpdate, RecipeResponse, RecipeItemBase
from ..auth import get_current_household
from ..utils import strip_emoji

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


@router.get("", response_model=list[RecipeResponse])
def list_recipes(
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    return sorted(
        db.query(Recipe).filter(Recipe.household_id == household.id).all(),
        key=lambda p: strip_emoji(p.name)
    )


@router.post("", response_model=RecipeResponse)
def create_recipe(
    recipe: RecipeCreate,
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    db_recipe = Recipe(name=recipe.name, color=recipe.color, household_id=household.id)
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)

    for item in recipe.items:
        recipe_item = RecipeItem(
            recipe_id=db_recipe.id,
            item_id=item.item_id,
            quantity=item.quantity,
            unit=item.unit,
        )
        db.add(recipe_item)

    db.commit()
    db.refresh(db_recipe)
    return db_recipe


@router.put("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(
    recipe_id: int,
    recipe: RecipeUpdate,
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    db_recipe = db.query(Recipe).filter(
        Recipe.id == recipe_id,
        Recipe.household_id == household.id
    ).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    if recipe.name is not None:
        db_recipe.name = recipe.name
    if recipe.color is not None:
        db_recipe.color = recipe.color

    if recipe.items is not None:
        db.query(RecipeItem).filter(RecipeItem.recipe_id == recipe_id).delete()
        for item in recipe.items:
            recipe_item = RecipeItem(
                recipe_id=recipe_id,
                item_id=item.item_id,
                quantity=item.quantity,
                unit=item.unit,
            )
            db.add(recipe_item)

    db.commit()
    db.refresh(db_recipe)
    return db_recipe


@router.delete("/{recipe_id}")
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    db_recipe = db.query(Recipe).filter(
        Recipe.id == recipe_id,
        Recipe.household_id == household.id
    ).first()
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    db.delete(db_recipe)
    db.commit()
    return {"ok": True}
