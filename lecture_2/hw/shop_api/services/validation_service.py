import typing as tp

from ..schemas.item import Item
from ..schemas.cart import Cart
from . import cart_service


def validate_item_filters(
    items: list[Item],
    show_deleted: bool,
    min_price: tp.Optional[float],
    max_price: tp.Optional[float],
) -> list[Item]:
    filtered_items = []
    for item in items:
        if not show_deleted and item.deleted:
            continue
        if min_price is not None and item.price < min_price:
            continue
        if max_price is not None and item.price > max_price:
            continue
        filtered_items.append(item)
    return filtered_items


def validate_cart_filters(
    carts: list[Cart],
    min_price: tp.Optional[float],
    max_price: tp.Optional[float],
    min_quantity: tp.Optional[int],
    max_quantity: tp.Optional[int],
) -> list[Cart]:
    filtered_carts: list[Cart] = []
    for cart in carts:
        cart = cart_service.prepare_cart_for_retrieval(cart)
        items_quantity = sum([item.quantity for item in cart.items])
        if min_price is not None and cart.price < min_price:
            continue
        if max_price is not None and cart.price > max_price:
            continue
        if min_quantity is not None and items_quantity < min_quantity:
            continue
        if max_quantity is not None and items_quantity > max_quantity:
            continue
        filtered_carts.append(cart)
    return filtered_carts
