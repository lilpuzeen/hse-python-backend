from fastapi import WebSocket
import uuid


class Manager:
    def __init__(self):
        self.rooms: dict[str, list[WebSocket]] = {}
        self.users: dict[WebSocket, str] = {}

    async def connect(self, ws: WebSocket, room: str):
        await ws.accept()
        nick = str(uuid.uuid4())[:8]
        self.users[ws] = nick
        if room not in self.rooms:
            self.rooms[room] = []
        self.rooms[room].append(ws)

    def disconnect(self, ws: WebSocket, room: str):
        self.rooms[room].remove(ws)
        del self.users[ws]
        if not self.rooms[room]:
            del self.rooms[room]

    async def send(self, msg: str, room: str, sender: WebSocket):
        for ws in self.rooms.get(room, []):
            if ws != sender:
                await ws.send_text(msg)


manager = Manager()
