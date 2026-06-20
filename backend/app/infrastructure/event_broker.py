from dataclasses import dataclass, field

from fastapi import WebSocket


@dataclass(slots=True)
class EventBroker:
    connections: list[WebSocket] = field(default_factory=list)

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, event: dict[str, object]) -> None:
        disconnected: list[WebSocket] = []
        for websocket in tuple(self.connections):
            try:
                await websocket.send_json(event)
            except RuntimeError:
                disconnected.append(websocket)
        for websocket in disconnected:
            self.disconnect(websocket)
