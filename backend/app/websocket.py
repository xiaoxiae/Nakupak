from fastapi import WebSocket, WebSocketDisconnect
import json


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, household_id: int):
        await websocket.accept()
        if household_id not in self.active_connections:
            self.active_connections[household_id] = []
        self.active_connections[household_id].append(websocket)

    def disconnect(self, websocket: WebSocket, household_id: int):
        if household_id in self.active_connections:
            self.active_connections[household_id] = [
                ws for ws in self.active_connections[household_id] if ws != websocket
            ]
            if not self.active_connections[household_id]:
                del self.active_connections[household_id]

    async def broadcast(self, household_id: int, message: dict):
        for connection in self.active_connections.get(household_id, []):
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


async def broadcast_update(household_id: int, update_type: str, data: dict):
    await manager.broadcast(household_id, {"type": update_type, "data": data})
