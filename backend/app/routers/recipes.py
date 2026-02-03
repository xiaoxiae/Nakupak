import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Household, Recipe, RecipeItem
from ..schemas import RecipeCreate, RecipeUpdate, RecipeResponse, RecipeItemBase
from ..auth import get_current_household
from ..utils import sort_key

router = APIRouter(prefix="/api/recipes", tags=["recipes"])

_uploads_dir = Path(__file__).resolve().parent.parent.parent.parent / "data" / "uploads"


@router.post("/upload-image")
async def upload_image(
    file: UploadFile,
    household: Household = Depends(get_current_household),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    ext = Path(file.filename or "img").suffix or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    dest = _uploads_dir / filename
    content = await file.read()
    dest.write_bytes(content)
    return {"image_url": f"/api/uploads/{filename}"}


@router.get("", response_model=list[RecipeResponse])
def list_recipes(
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    return sorted(
        db.query(Recipe).filter(Recipe.household_id == household.id).all(),
        key=lambda p: sort_key(p.name)
    )


@router.post("", response_model=RecipeResponse)
def create_recipe(
    recipe: RecipeCreate,
    db: Session = Depends(get_db),
    household: Household = Depends(get_current_household)
):
    db_recipe = Recipe(name=recipe.name, description=recipe.description, image_url=recipe.image_url, household_id=household.id)
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
    if recipe.description is not None:
        db_recipe.description = recipe.description
    if recipe.image_url is not None:
        db_recipe.image_url = recipe.image_url or None

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
