import pytest
from unittest.mock import AsyncMock
from pydantic import BaseModel, ValidationError
from fastapi import WebSocketDisconnect
from app.core.utils.websocket_helpers import ValidatedWebSocket, handle_websocket_exception

class MockSchema(BaseModel):
    id: int
    name: str

@pytest.mark.asyncio
async def test_receive_validated_success():
    mock_ws = AsyncMock()
    mock_ws.receive_json.return_value = {"id": 1, "name": "House"}
    
    wrapper = ValidatedWebSocket(mock_ws, MockSchema)

    result = await wrapper.receive_validated()

    assert isinstance(result, MockSchema)
    assert result.id == 1
    mock_ws.receive_json.assert_called_once()

@pytest.mark.asyncio
async def test_receive_validated_validation_error():
    mock_ws = AsyncMock()
    mock_ws.receive_json.return_value = {"id": 1 }
    
    wrapper = ValidatedWebSocket(mock_ws, MockSchema)

    with pytest.raises(ValidationError):
        await wrapper.receive_validated()

def test_handle_websocket_exception_disconnect(capsys):
    mock_ws = "User123"
    exc = WebSocketDisconnect(code=1000)

    handle_websocket_exception(mock_ws, exc)

    captured = capsys.readouterr()
    assert "User User123 disconnected" in captured.out