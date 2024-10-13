from fastapi import APIRouter, HTTPException, status, Query, Response
from ..schemas.cart import Cart, CartItem
from ..services.cart_service import prepare_cart_for_retrieval
from ..services.validation_service import validate_cart_filters
from .item import items_db

carts_db = {}
cart_id_counter = 0

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_cart(response: Response):
    global cart_id_counter
    new_cart = Cart(id=cart_id_counter)
    carts_db[cart_id_counter] = new_cart
    response.headers["location"] = f"/cart/{new_cart.id}"
    cart_id_counter += 1
    return {"id": new_cart.id}


@router.get("/{id}", response_model=Cart)
def get_cart(id: int):
    cart = carts_db.get(id)
    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")
    return prepare_cart_for_retrieval(cart=cart)


@router.get("/")
def list_carts(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: float = Query(None, ge=0.0),
    max_price: float = Query(None, ge=0.0),
    min_quantity: int = Query(None, ge=0),
    max_quantity: int = Query(None, ge=0),
):
    validated_carts = validate_cart_filters(
        carts=list(carts_db.values()),
        min_price=min_price,
        max_price=max_price,
        min_quantity=min_quantity,
        max_quantity=max_quantity,
    )
    return validated_carts[offset : offset + limit]


@router.post("/{cart_id}/add/{item_id}", response_model=Cart)
def add_item_to_cart(cart_id: int, item_id: int):
    cart = carts_db.get(cart_id)
    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")

    item = items_db.get(item_id)
    if item is None or item.deleted:
        raise HTTPException(status_code=404, detail="Item not found")

    cart_item = next((ci for ci in cart.items if ci.id == item_id), None)
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(
            id=item_id,
            name=item.name,
            quantity=1,
            available=not item.deleted,
        )
        cart.items.append(cart_item)

    return cart
