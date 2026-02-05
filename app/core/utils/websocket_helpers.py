from fastapi import WebSocketDisconnect
from pydantic import ValidationError

class ValidatedWebSocket:
    def __init__(self, websocket, schema):
        self.ws = websocket
        self.schema = schema
    
    async def receive_validated(self):
        data = await self.ws.receive_json()
        return self.schema(**data)
    
    async def close(self, code=1000, reason=None):
        await self.ws.close(code=code, reason=reason)

def handle_websocket_exception(ws, e):
    print(e)

    if isinstance(e, ValidationError):
        print(f"Validation failed: {e}")

    if isinstance(e, WebSocketDisconnect):
        print(f"User {ws} disconnected")