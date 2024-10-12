from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..services.manager import manager

router = APIRouter()


@router.websocket("/{room}")
async def chat(ws: WebSocket, room: str):
    await manager.connect(ws, room)
    nick = manager.users[ws]
    try:
        while True:
            text = await ws.receive_text()
            msg = f"{nick} :: {text}"
            await manager.send(msg, room, ws)
    except WebSocketDisconnect:
        manager.disconnect(ws, room)
