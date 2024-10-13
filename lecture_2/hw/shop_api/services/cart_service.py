from ..routers.item import items_db
from ..schemas.cart import Cart


def prepare_cart_for_retrieval(cart: Cart) -> Cart:
    price = 0
    for cart_item in cart.items:
        item = items_db.get(cart_item.id)
        if item:
            cart_item.available = True
            cart_item.name = item.name
            price += item.price * cart_item.quantity
        else:
            cart_item.available = False

    cart.price = price

    return cart
