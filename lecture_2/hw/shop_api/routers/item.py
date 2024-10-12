import typing as tp

from fastapi import APIRouter, HTTPException, status, Response, Query
from fastapi.responses import JSONResponse

from ..schemas.item import Item, ItemCreate, ItemUpdate
from ..services.validation_service import validate_item_filters

items_db = {}

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate):
    item_id = len(items_db) + 1
    items_db[item_id] = (new_item := Item(id=item_id, name=item.name, price=item.price))
    return JSONResponse(
        content={"id": item_id, "name": new_item.name, "price": new_item.price},
        status_code=status.HTTP_201_CREATED,
        headers={"Location": f"/item/{item_id}"},
    )


@router.get("/{id}", status_code=status.HTTP_200_OK)
def get_item(id: int):
    if id not in items_db or items_db[id].deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    item = items_db[id]
    return {"id": item.id, "name": item.name, "price": item.price}


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
    return [item for item in validated_items[start:end]]


@router.put("/{id}")
def update_item(id: int, item: ItemCreate):
    if id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    new_item = Item(id=id, name=item.name, price=item.price)
    items_db[id] = new_item
    return {"id": new_item.id, "name": new_item.name, "price": new_item.price}


@router.patch("/{id}")
def patch_item(id: int, body: tp.Dict[str, tp.Any]) -> dict:
    item = items_db.get(id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.deleted:
        raise HTTPException(status_code=304, detail="Item is deleted")
    allowed_fields = {"name", "price"}
    invalid_fields = set(body) - allowed_fields
    if invalid_fields:
        raise HTTPException(status_code=422, detail=f"Invalid fields in request body: {', '.join(invalid_fields)}")
    updated_fields = {key: value for key, value in body.items() if key in allowed_fields}
    for key, value in updated_fields.items():
        setattr(item, key, value)
    return {"id": item.id, "name": item.name, "price": item.price}


@router.delete("/{id}")
def delete_item(id: int):
    item = items_db.get(id)
    if item is None or item.deleted:
        return {"detail": "Already deleted"}
    item.deleted = True
    return {"detail": "Item deleted"}
