from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    household_id: int | None = None


class HouseholdJoin(BaseModel):
    token: str


class HouseholdResponse(BaseModel):
    token: str
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str
    sort_order: int = 0
    color: str = "#6b7280"


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = None
    sort_order: int | None = None
    color: str | None = None


class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True


class ItemBase(BaseModel):
    name: str
    category_id: int | None = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: str | None = None
    category_id: int | None = None


class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    category: CategoryResponse | None = None

    class Config:
        from_attributes = True


class ShoppingListItemBase(BaseModel):
    item_id: int
    quantity: float = 1
    unit: str = "x"


class ShoppingListItemCreate(BaseModel):
    item_id: int
    quantity: float = 1
    unit: str = "x"


class ShoppingListItemUpdate(BaseModel):
    quantity: float
    unit: str | None = None


class ShoppingListItemResponse(BaseModel):
    id: int
    item_id: int
    quantity: float
    unit: str = "x"
    checked: bool = False
    added_at: datetime
    from_recipe_id: int | None
    item: ItemResponse

    class Config:
        from_attributes = True


class RecipeItemBase(BaseModel):
    item_id: int
    quantity: float = 1
    unit: str = "x"


class RecipeBase(BaseModel):
    name: str
    color: str = "#3b82f6"


class RecipeCreate(RecipeBase):
    items: list[RecipeItemBase] = []


class RecipeUpdate(BaseModel):
    name: str | None = None
    color: str | None = None
    items: list[RecipeItemBase] | None = None


class RecipeItemResponse(BaseModel):
    item_id: int
    quantity: float
    unit: str = "x"
    item: ItemResponse

    class Config:
        from_attributes = True


class RecipeResponse(RecipeBase):
    id: int
    created_at: datetime
    recipe_items: list[RecipeItemResponse] = []

    class Config:
        from_attributes = True


class SessionItemBase(BaseModel):
    item_id: int | None = None
    item_name: str
    quantity: float = 1
    unit: str = "x"


class SessionItemResponse(SessionItemBase):
    id: int
    item: ItemResponse | None = None

    class Config:
        from_attributes = True


class ShoppingSessionResponse(BaseModel):
    id: int
    started_at: datetime
    completed_at: datetime | None
    session_items: list[SessionItemResponse] = []

    class Config:
        from_attributes = True


class PoolItemResponse(BaseModel):
    item: ItemResponse
    score: float
    frequency: int
    last_added: datetime | None

    class Config:
        from_attributes = True


class AddItemsRequest(BaseModel):
    items: list[ShoppingListItemCreate]


class MergeItemsRequest(BaseModel):
    source_ids: list[int]


class BulkIdsRequest(BaseModel):
    ids: list[int]


class BulkSetCategoryRequest(BaseModel):
    item_ids: list[int]
    category_id: int | None = None


class WSMessage(BaseModel):
    type: str
    data: dict
