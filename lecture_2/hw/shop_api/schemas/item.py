import typing as tp

from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    price: float


class ItemUpdate(BaseModel):
    name: tp.Optional[str] = None
    price: tp.Optional[float] = None


class Item(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = False
