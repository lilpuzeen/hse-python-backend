from fastapi import FastAPI
from .routers import cart, item, chat
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Shop API")
Instrumentator().instrument(app).expose(app)

app.include_router(cart.router, prefix="/cart", tags=["Cart"])
app.include_router(item.router, prefix="/item", tags=["Item"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
