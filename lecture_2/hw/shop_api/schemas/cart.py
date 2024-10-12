from pydantic import BaseModel


class CartItem(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool


class Cart(BaseModel):
    id: int
    items: list[CartItem] = []
    price: float = 0.0
    quantity: int = 0
