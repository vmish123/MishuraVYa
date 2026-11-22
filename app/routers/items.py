import logging
from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field

# Создание логгера модуля и роутера
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/items", tags=["items"])

fake_db = {
    1: {"name": "Foo", "price": 50.2},
    2: {"name": "Hat", "price": 1000, "is_offer": True},
}


# Определение модели данных товара с метаданными полей
class Item(BaseModel):
    name: str = Field(..., title="Название", example="Телефон")
    price: float = Field(..., gt=0, title="Цена", example=199.99)
    is_offer: bool | None = Field(None, title="Акционный товар")


# Проверка уникальности имени товара среди записей в fake_db
def is_name_taken(name: str, exclude_id: int | None = None):
    for existing_id, existing_item in fake_db.items():
        if existing_id != exclude_id and (
                existing_item["name"].lower() == name.lower()
        ):
            return True

    return False


# Получение товара по ID с проверкой его наличия
@router.get("/{item_id}")
def read_item(
        item_id: int = Path(..., title="ID товара", ge=1),
        q: str | None = Query(None, title="Поисковый запрос", max_length=50)
):
    if item_id not in fake_db:
        logger.warning("Товар с item_id=%s не найден", item_id)
        raise HTTPException(status_code=404, detail="Item not found")

    logger.info("Получен товар item_id=%s (q=%s)", item_id, q)
    return {"item_id": item_id, "item": fake_db[item_id], "q": q}


# Создание нового товара с проверкой уникальности имени
@router.post("/", response_model=Item)
def create_item(item: Item):
    if is_name_taken(item.name):
        logger.warning("Не удалось создать товар с name: %s. Товар уже существует.", item.name)
        raise HTTPException(
            status_code=400,
            detail="Item with this name already exists",
        )

    # Генерация нового ID и сохранение товара в базу
    new_id = max(fake_db.keys(), default=0) + 1
    fake_db[new_id] = item.model_dump()

    logger.info("Создан новый товар item_id=%s (%s)", new_id, item.name)
    return item


# Обновление данных товара по ID с проверкой уникальности имени
@router.put("/{item_id}")
def update_item(
        item: Item,
        item_id: int = Path(..., title="ID товара", ge=1),
):
    if item_id not in fake_db:
        logger.warning("Не удалось обновить несуществующий товар item_id=%s", item_id)
        raise HTTPException(status_code=404, detail="Item not found")

    if is_name_taken(item.name, exclude_id=item_id):
        logger.warning("Не удалось обновить товар %s с name: %s. Имя уже занято.", item_id, item.name)
        raise HTTPException(
            status_code=400,
            detail="Item with this name already exists",
        )

    # Обновление записи товара в базе
    fake_db[item_id] = item.model_dump()

    logger.info("Товар item_id=%s обновлён (%s)", item_id, item.name)
    return {"item_id": item_id, "item": fake_db[item_id]}
