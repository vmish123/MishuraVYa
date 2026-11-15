from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/items", tags=["items"])
fake_db = {
    1: {"name": "Foo", "price": 50.2},
    2: {"name": "Hat", "price": 1000, "is_offer": True},

}


class Item(BaseModel):
    name: str = Field(..., title="Название", example="Телефон")
    price: float = Field(..., gt=0, title="Цена", example=199.99)
    is_offer: bool | None = Field(None, title="Акционный товар")


def is_name_taken(name: str, exclude_id: int | None = None):
    for existing_id, existing_item in fake_db.items():
        if existing_id != exclude_id and (
                existing_item["name"].lower() == name.lower()
        ):
            return True
    return False


@router.get("/{item_id}")
def read_item(
        item_id: int = Path(..., title="ID товара", ge=1),
        q: str | None = Query(None, title="Поисковый запрос", max_length=50)
):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id, "item": fake_db[item_id], "q": q}


@router.post("/", response_model=Item)
def create_item(item: Item):
    if is_name_taken(item.name):
        raise HTTPException(
            status_code=400,
            detail="Item with this name already exists",
        )
    new_id = max(fake_db.keys(), default=0) + 1
    fake_db[new_id] = item.model_dump()
    return item


@router.put("/{item_id}")
def update_item(
        item: Item,
        item_id: int = Path(..., title="ID товара", ge=1),
):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")

    if is_name_taken(item.name, exclude_id=item_id):
        raise HTTPException(
            status_code=400,
            detail="Item with this name already exists",
        )

    fake_db[item_id] = item.model_dump()
    return {"item_id": item_id, "item": fake_db[item_id]}
