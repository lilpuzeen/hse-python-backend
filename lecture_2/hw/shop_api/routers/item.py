import typing as tp

from fastapi import APIRouter, HTTPException, status, Response, Query
from ..schemas.item import Item, ItemCreate, ItemUpdate
from ..services.validation_service import validate_item_filters

items_db = {}
item_id_counter = 0

router = APIRouter()


@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, response: Response):
    global item_id_counter
    item_id_counter += 1
    item_id = item_id_counter
    items_db[item_id] = (new_item := Item(id=item_id, name=item.name, price=item.price))
    response.headers["location"] = f"item/{item_id}"
    return new_item.model_dump()


@router.get("/{id}", response_model=Item)
def get_item(id: int):
    if id not in items_db or items_db[id].deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    return items_db[id].model_dump


@router.get("/")
def list_items(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: tp.Optional[float] = Query(None, ge=0.0),
    max_price: tp.Optional[float] = Query(None, ge=0.0),
    show_deleted: bool = Query(False),
):
    validated_items = validate_item_filters(
        items=list(items_db.values()),
        show_deleted=show_deleted,
        min_price=min_price,
        max_price=max_price,
    )
    start, end = offset, offset + limit
    return [item.model_dump() for item in validated_items[start:end]]


@router.put("/{id}")
def update_item(id: int, new_item: ItemCreate):
    item = items_db.get(id)
    if not item or item.deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    item.name = new_item.name
    item.price = new_item.price
    return item


@router.patch("/{id}")
def partial_update_item(id: int, item_update: ItemUpdate):
    item = items_db.get(id)
    if item.deleted:
        raise HTTPException(status_code=304, detail="Cannot update this field")
    if "deleted" in item_update:
        raise HTTPException(status_code=422, detail="Cannot update this field")
    if "name" in item_update:
        item.name = item_update.name
    if "price" in item_update:
        item.price = item_update.price
    return item


@router.delete("/{id}")
def delete_item(id: int):
    item = items_db.get(id)
    if item is None or item.deleted:
        return {"detail": "Already deleted"}
    item.deleted = True
    return {"detail": "Item deleted"}
